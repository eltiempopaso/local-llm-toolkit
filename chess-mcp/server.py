import chess
import chess.svg
import cairosvg


from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from mcp.server.fastmcp import Image

mcp = FastMCP(
    "Chess MCP",
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=[
            "chess-mcp:8000",
        ],
    ),
)


@mcp.tool()
def fen2position(
    fen: str,
    orientation: str = "white",
    size: int = 480
) -> Image:
    """
    Draw a chess position from a FEN string.

    Args:
        fen: FEN representation of the chess position.
        orientation: Board orientation, white or black.
        size: Image width and height in pixels.

    Returns:
        PNG image containing the chessboard.
    """

    # Validate orientation
    if orientation not in ("white", "black"):
        raise ValueError("Orientation must be white or black")

    # Limit image dimensions
    if not 200 <= size <= 1200:
        raise ValueError("Size must be between 200 and 1200")

    # Parse FEN
    try:
        board = chess.Board(fen)
    except ValueError as exc:
        raise ValueError(f"Invalid FEN: {exc}") from exc

    # Validate chess position
    if not board.is_valid():
        raise ValueError("FEN contains an invalid chess position")

    # Generate SVG
    svg = chess.svg.board(
        board,
        size=size,
        coordinates=True,
        orientation=(
            chess.WHITE if orientation == "white"
            else chess.BLACK
        )
    )

    # Convert SVG to PNG
    png = cairosvg.svg2png(
        bytestring=svg.encode("utf-8")
    )

    return Image(
        data=png,
        format="png"
    )


if __name__ == "__main__":
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = 8000

    mcp.run(transport="streamable-http")
