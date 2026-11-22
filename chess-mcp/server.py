from typing import Any

import cairosvg
import chess
import chess.svg
from fen_tools import FenTools
from mcp.server.fastmcp import FastMCP, Image
from mcp.server.transport_security import TransportSecuritySettings

mcp = FastMCP(
    "Chess MCP",
    instructions=(
        "Este servidor ofrece herramientas de ajedrez y análisis de posiciones con Stockfish. "
        "INSTRUCCIÓN IMPORTANTE: cuando el usuario pregunte por la evaluación, puntuación, "
        "valoración, ventaja, quién está mejor, análisis o mejor jugada de Stockfish, llama "
        "a una herramienta de Stockfish; no respondas de memoria ni inventes una evaluación. "
        "Usa stockfish_evaluation para una evaluación breve, best_move para la mejor jugada "
        "y analyze_position cuando pidan variantes o análisis de varias líneas. "
        "Las herramientas necesitan la posición: usa el FEN o las jugadas dados en la "
        "conversación; si no hay información suficiente para construir la posición, pide "
        "el FEN o la secuencia de jugadas. Explica las puntuaciones desde la perspectiva "
        "de blancas o del turno según los campos devueltos."
    ),
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=["chess-mcp:8000"],
    ),
)


@mcp.tool()
def render_board_image(
    fen: str,
    orientation: str = "white",
    size: int = 480,
) -> Image:
    """Render a valid FEN position as a PNG chessboard.

    Args:
        fen: Complete FEN string for the position.
        orientation: Place White or Black at the bottom.
        size: Image width and height in pixels, from 200 to 1200.
    """
    if orientation not in ("white", "black"):
        raise ValueError("orientation must be 'white' or 'black'")
    if not 200 <= size <= 1200:
        raise ValueError("size must be between 200 and 1200 pixels")

    try:
        board = chess.Board(fen)
    except ValueError as exc:
        raise ValueError(f"Invalid FEN: {exc}") from exc
    if not board.is_valid():
        raise ValueError(f"FEN contains an invalid chess position (status {board.status()})")

    svg = chess.svg.board(
        board,
        size=size,
        coordinates=True,
        orientation=chess.WHITE if orientation == "white" else chess.BLACK,
    )
    return Image(data=cairosvg.svg2png(bytestring=svg.encode("utf-8")), format="png")


@mcp.tool()
def pgn_to_fen(pgn: str) -> dict[str, Any]:
    """Convert a PGN game's main line to its final FEN and list the played moves."""
    return FenTools.pgn_to_fen(pgn)


@mcp.tool()
def apply_san_moves(fen: str, moves: list[str]) -> dict[str, Any]:
    """Apply SAN moves in order; returns the new FEN and each move in SAN and UCI."""
    return FenTools.apply_san_moves(fen, moves)


@mcp.tool()
def validate_fen(fen: str) -> dict[str, Any]:
    """Check FEN syntax and chess-position validity; reports status flags if invalid."""
    return FenTools.validate_fen(fen)


@mcp.tool()
def legal_moves(fen: str) -> dict[str, Any]:
    """List legal moves in SAN and UCI, including capture and promotion details."""
    return FenTools.legal_moves(fen)


@mcp.tool()
def san_to_uci(fen: str, san: str) -> dict[str, Any]:
    """Convert a legal SAN move to UCI for the supplied position."""
    return FenTools.san_to_uci(fen, san)


@mcp.tool()
def uci_to_san(fen: str, uci: str) -> dict[str, Any]:
    """Convert a legal UCI move to SAN for the supplied position."""
    return FenTools.uci_to_san(fen, uci)


@mcp.tool()
def position_summary(fen: str) -> dict[str, Any]:
    """Summarize whose turn it is, check/game status, legal moves, and move counters."""
    return FenTools.position_summary(fen)


@mcp.tool()
def is_checkmate(fen: str) -> dict[str, Any]:
    """Return whether the side to move is checkmated."""
    return FenTools.is_checkmate(fen)


@mcp.tool()
def is_draw(fen: str) -> dict[str, Any]:
    """Return whether the position is drawn, including claimable draws."""
    return FenTools.is_draw(fen)


@mcp.tool()
def board_ascii(fen: str) -> dict[str, Any]:
    """Show the board as a compact text diagram."""
    return FenTools.board_ascii(fen)


@mcp.tool()
def material_balance(fen: str) -> dict[str, Any]:
    """Count material using pawn values (pawn=1, knight/bishop=3, rook=5, queen=9)."""
    return FenTools.material_balance(fen)


@mcp.tool()
def available_captures(fen: str) -> dict[str, Any]:
    """List legal captures for the side to move in SAN and UCI."""
    return FenTools.available_captures(fen)


@mcp.tool()
def opponent_capture_threats(fen: str) -> dict[str, Any]:
    """List hypothetical opponent captures after switching the turn; not engine analysis."""
    return FenTools.opponent_capture_threats(fen)


@mcp.tool()
def analyze_position(
    fen: str,
    depth: int = 12,
    multipv: int = 3,
    time_limit: float = 2.0,
) -> dict[str, Any]:
    """Analiza una posición de ajedrez con Stockfish y devuelve variantes principales.

    Usa esta herramienta si el usuario pide análisis de Stockfish, varias líneas,
    variantes candidatas, MultiPV o una comparación de jugadas. Para una valoración
    rápida sin varias variantes, usa stockfish_evaluation.

    Args:
        fen: FEN completo de la posición que se quiere analizar.
        depth: Profundidad máxima de búsqueda, de 1 a 30.
        multipv: Número de variantes candidatas, de 1 a 5.
        time_limit: Tiempo máximo en segundos, de 0.1 a 10.

    La búsqueda termina al alcanzar primero el límite de profundidad o de tiempo.
    Devuelve la evaluación en centipeones o mate, mejor jugada y variantes en SAN/UCI.
    """
    return FenTools.analyze_position(fen, depth, multipv, time_limit)


@mcp.tool()
def best_move(
    fen: str,
    depth: int = 12,
    time_limit: float = 2.0,
) -> dict[str, Any]:
    """Obtén con Stockfish la mejor jugada, su evaluación y la variante principal.

    Args:
        fen: FEN completo de la posición.
        depth: Profundidad máxima, de 1 a 30.
        time_limit: Tiempo máximo en segundos, de 0.1 a 10.

    Usa esta herramienta cuando el usuario pregunte qué jugar, cuál es la mejor
    jugada, best move, Stockfish move o recomendación del motor. Incluye la jugada
    en SAN y UCI, evaluación y línea principal.
    """
    return FenTools.best_move(fen, depth, time_limit)


@mcp.tool()
def evaluate_position(
    fen: str,
    depth: int = 12,
    time_limit: float = 2.0,
) -> dict[str, Any]:
    """Evalúa con Stockfish una posición de ajedrez (evaluación, puntuación o valoración).

    Usa esta herramienta cuando pregunten «¿cuál es la evaluación de Stockfish?»,
    «¿quién está mejor?», «what is the Stockfish evaluation?» o por la ventaja
    de una posición. Devuelve puntuación en centipeones o mate forzado, tanto
    desde la perspectiva de blancas como desde la perspectiva del turno.

    Args:
        fen: FEN completo de la posición que se quiere evaluar.
        depth: Profundidad máxima de búsqueda, de 1 a 30.
        time_limit: Tiempo máximo de búsqueda en segundos, de 0.1 a 10.
    """
    return FenTools.evaluate_position(fen, depth, time_limit)


@mcp.tool()
def stockfish_evaluation(
    fen: str,
    depth: int = 12,
    time_limit: float = 2.0,
) -> dict[str, Any]:
    """Evaluación / valoración / puntuación de Stockfish para una posición FEN.

    Herramienta directa para preguntas como «¿cuál es la evaluación de Stockfish?»,
    «evalúa esta posición», «¿quién está mejor?» o «what is Stockfish's evaluation?».
    Devuelve centipeones o mate forzado desde las perspectivas de blancas y del turno.
    Si el usuario pide también jugadas candidatas, usa analyze_position.

    Args:
        fen: FEN completo de la posición a evaluar.
        depth: Profundidad máxima, de 1 a 30.
        time_limit: Tiempo máximo en segundos, de 0.1 a 10.
    """
    return FenTools.evaluate_position(fen, depth, time_limit)


if __name__ == "__main__":
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = 8000
    mcp.run(transport="streamable-http")
