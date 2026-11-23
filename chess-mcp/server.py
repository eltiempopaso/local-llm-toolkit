import logging
from functools import wraps
from pathlib import Path
from time import perf_counter
from typing import Any, Callable, Literal, ParamSpec, TypeVar

import cairosvg
import chess
import chess.svg
from fen_tools import FenTools
from mcp.server.fastmcp import FastMCP, Image
from mcp.server.transport_security import TransportSecuritySettings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

P = ParamSpec("P")
R = TypeVar("R")

ANALYZE_POSITION_SKILL_PATH = (
    Path(__file__).parent / "skills" / "analyze_position.md"
)
SKILLS = {
    "analyze_position": (
        ANALYZE_POSITION_SKILL_PATH,
        "Workflow for validating a chess position, selecting Stockfish "
        "analysis, and interpreting its evaluation.",
    ),
}


def trace_handler(function: Callable[P, R]) -> Callable[P, R]:
    """Log MCP handler starts, completions, durations, and failures."""
    @wraps(function)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        started_at = perf_counter()
        handler_name = function.__name__
        logger.info("MCP handler %s started", handler_name)
        try:
            result = function(*args, **kwargs)
        except Exception:
            logger.exception(
                "MCP handler %s failed after %.3f seconds",
                handler_name,
                perf_counter() - started_at,
            )
            raise

        logger.info(
            "MCP handler %s completed in %.3f seconds",
            handler_name,
            perf_counter() - started_at,
        )
        return result

    return wrapper


mcp = FastMCP(
    "Chess MCP",
    instructions=(
        "Chess tools for FEN, PGN, and Stockfish. Use pgn_to_position to get the "
        "final FEN of a PGN game; play_moves to apply moves; inspect_position to "
        "check position status, material, and moves; stockfish_analyze for engine "
        "evaluations or recommendations; and render_board_image to create a board "
        "image. Whenever the user asks for a Stockfish evaluation, advantage, best "
        "move, or analysis, always call stockfish_analyze: use analysis_mode="
        "'evaluation' for the score, 'best_move' for a move recommendation, and "
        "'variations' to compare lines. Never invent evaluations. You need a FEN "
        "or moves that identify the position; ask for them if they are missing. "
        "The score fields indicate their perspective. Available skill: "
        "'analyze_position' provides the workflow for validating a position, "
        "choosing an analysis mode, and interpreting scores. When a user asks "
        "for specialized workflows, call list_skills to discover available "
        "skills. For position analysis, evaluation, or best move, call "
        "get_skill(name='analyze_position'), follow that methodology, then use "
        "the chess tools."
    ),
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=["chess-mcp:8000"],
    ),
)


@mcp.tool()
@trace_handler
def list_skills() -> list[dict[str, str]]:
    """List available skills with their names and descriptions.

    Call this to discover which specialized chess workflows are available,
    then use get_skill to load the relevant skill.
    """
    return [
        {"name": name, "description": description}
        for name, (_, description) in sorted(SKILLS.items())
    ]


@mcp.tool()
@trace_handler
def get_skill(name: str) -> str:
    """Load the Markdown content of an available skill by name.

    Call list_skills first to discover valid skill names.
    """
    skill = SKILLS.get(name)
    if skill is None:
        raise ValueError(
            f"Unknown skill '{name}'. Available skills: "
            f"{', '.join(sorted(SKILLS))}"
        )

    skill_path, _ = skill
    logger.info("Loading skill %s", name)
    return skill_path.read_text(encoding="utf-8")


@mcp.tool()
@trace_handler
def render_board_image(
    fen: str,
    orientation: Literal["white", "black"] = "white",
    size: int = 480,
) -> Image:
    """Render a chess position FEN as a PNG board.

    Args:
        fen: Complete FEN string for the position.
        orientation: Which side appears at the bottom of the board.
        size: Image width and height in pixels, from 200 to 1200.
    """
    if not 200 <= size <= 1200:
        raise ValueError("size must be between 200 and 1200 pixels")

    try:
        board = chess.Board(fen)
    except ValueError as exc:
        raise ValueError(f"Invalid FEN: {exc}") from exc
    if not board.is_valid():
        raise ValueError(
            f"FEN contains an invalid chess position (status {board.status()})"
        )

    svg = chess.svg.board(
        board,
        size=size,
        coordinates=True,
        orientation=chess.WHITE if orientation == "white" else chess.BLACK,
    )
    return Image(data=cairosvg.svg2png(bytestring=svg.encode("utf-8")), format="png")


@mcp.tool()
@trace_handler
def pgn_to_position(pgn: str) -> dict[str, Any]:
    """Convert a PGN game to its final FEN, moves, headers, and parsing warnings."""
    return FenTools.pgn_to_position(pgn)


@mcp.tool()
@trace_handler
def play_moves(
    fen: str,
    moves: list[str],
    notation: Literal["SAN", "UCI"] = "SAN",
) -> dict[str, Any]:
    """Apply a sequence of chess moves and return the resulting FEN.

    Use SAN by default (for example ["Nf3", "d5"]); set notation="UCI" for
    coordinate moves (for example ["g1f3", "d7d5"]). The result includes both
    notations for every played move.
    """
    return FenTools.play_moves(fen, moves, notation)


@mcp.tool()
@trace_handler
def inspect_position(
    fen: str,
    detail: Literal["summary", "legal_moves", "board", "all"] = "summary",
) -> dict[str, Any]:
    """Inspect one FEN: validity, turn, check/game result, material and move count.

    Use detail="summary" for the compact position report, "legal_moves" to also
    list every legal move in SAN and UCI, "board" to add an ASCII board, or "all"
    to include both. The move list also marks captures and promotions.
    """
    return FenTools.inspect_position(fen, detail)


@mcp.tool()
@trace_handler
def stockfish_analyze(
    fen: str,
    analysis_mode: Literal["evaluation", "best_move", "variations"] = "evaluation",
    depth: int = 12,
    multipv: int = 3,
    time_limit: float = 2.0,
) -> dict[str, Any]:
    """Ask Stockfish for an evaluation, best move, or candidate variations.

    This is the single Stockfish tool. Call it for questions about evaluation,
    score, advantage, who is better, best move, or engine analysis.
    For position analysis, first load and follow the "analyze_position" skill
    with get_skill.

    Args:
        fen: Complete FEN string for the position.
        analysis_mode: "evaluation" for score only; "best_move" for the top move
            and its principal variation; "variations" to compare candidate lines.
        depth: Maximum search depth from 1 to 30.
        multipv: Number of candidate lines in variations mode, from 1 to 5.
        time_limit: Maximum search time in seconds, from 0.1 to 10.

    Scores are returned in centipawns or mate moves, from White's and the
    side-to-move perspectives. Search stops when either limit is reached.
    """
    return FenTools.stockfish_analyze(fen, analysis_mode, depth, multipv, time_limit)


if __name__ == "__main__":
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = 8000
    logger.info(
        "Starting Chess MCP server on %s:%s",
        mcp.settings.host,
        mcp.settings.port,
    )
    mcp.run(transport="streamable-http")
