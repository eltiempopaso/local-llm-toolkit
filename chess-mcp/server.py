from typing import Any, Literal

import cairosvg
import chess
import chess.svg
from fen_tools import FenTools
from mcp.server.fastmcp import FastMCP, Image
from mcp.server.transport_security import TransportSecuritySettings

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
        "The score fields indicate their perspective."
    ),
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=["chess-mcp:8000"],
    ),
)


@mcp.tool()
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
def pgn_to_position(pgn: str) -> dict[str, Any]:
    """Convert a PGN game to its final FEN, moves, headers, and parsing warnings."""
    return FenTools.pgn_to_position(pgn)


@mcp.tool()
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
    mcp.run(transport="streamable-http")
