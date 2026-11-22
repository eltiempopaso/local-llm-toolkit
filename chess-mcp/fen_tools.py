import io
import os
from typing import Any, Literal

import chess
import chess.engine
import chess.pgn

STOCKFISH_PATH = os.getenv("STOCKFISH_PATH", "stockfish")
PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
}
POSITION_STATUS_FLAGS = (
    chess.STATUS_NO_WHITE_KING,
    chess.STATUS_NO_BLACK_KING,
    chess.STATUS_TOO_MANY_KINGS,
    chess.STATUS_TOO_MANY_WHITE_PAWNS,
    chess.STATUS_TOO_MANY_BLACK_PAWNS,
    chess.STATUS_PAWNS_ON_BACKRANK,
    chess.STATUS_TOO_MANY_WHITE_PIECES,
    chess.STATUS_TOO_MANY_BLACK_PIECES,
    chess.STATUS_BAD_CASTLING_RIGHTS,
    chess.STATUS_INVALID_EP_SQUARE,
    chess.STATUS_OPPOSITE_CHECK,
    chess.STATUS_EMPTY,
    chess.STATUS_RACE_CHECK,
    chess.STATUS_RACE_OVER,
    chess.STATUS_RACE_MATERIAL,
    chess.STATUS_TOO_MANY_CHECKERS,
    chess.STATUS_IMPOSSIBLE_CHECK,
)


class FenTools:
    """Chess position, move and Stockfish helpers used by the MCP server."""

    @staticmethod
    def _success(data: Any) -> dict[str, Any]:
        return {"success": True, "data": data, "error": None}

    @staticmethod
    def _failure(error: Exception | str) -> dict[str, Any]:
        return {"success": False, "data": None, "error": str(error)}

    @staticmethod
    def _board(fen: str) -> chess.Board:
        return chess.Board(fen)

    @staticmethod
    def _position_status(board: chess.Board) -> dict[str, Any]:
        status = board.status()
        return {
            "valid": board.is_valid(),
            "status_code": int(status),
            "status_flags": [
                flag.name.lower()
                for flag in POSITION_STATUS_FLAGS
                if status & flag
            ],
        }

    @staticmethod
    def _material_balance(board: chess.Board) -> dict[str, Any]:
        white = sum(
            len(board.pieces(piece_type, chess.WHITE)) * value
            for piece_type, value in PIECE_VALUES.items()
        )
        black = sum(
            len(board.pieces(piece_type, chess.BLACK)) * value
            for piece_type, value in PIECE_VALUES.items()
        )
        return {
            "white": white,
            "black": black,
            "white_minus_black": white - black,
            "unit": "pawn_value",
        }

    @staticmethod
    def _legal_moves(board: chess.Board) -> list[dict[str, Any]]:
        return [
            {
                "san": board.san(move),
                "uci": move.uci(),
                "from": chess.square_name(move.from_square),
                "to": chess.square_name(move.to_square),
                "is_capture": board.is_capture(move),
                "promotion": (
                    chess.piece_name(move.promotion) if move.promotion else None
                ),
            }
            for move in board.legal_moves
        ]

    @staticmethod
    def pgn_to_position(pgn: str) -> dict[str, Any]:
        """Convert a PGN main line to a final FEN and its moves."""
        try:
            game = chess.pgn.read_game(io.StringIO(pgn))
            if game is None:
                raise ValueError("No valid PGN game was found.")

            board = game.board()
            moves = []
            for move in game.mainline_moves():
                moves.append({"san": board.san(move), "uci": move.uci()})
                board.push(move)

            return FenTools._success(
                {
                    "fen": board.fen(),
                    "moves": moves,
                    "move_count": len(moves),
                    "headers": dict(game.headers),
                    "warnings": [str(error) for error in game.errors],
                }
            )
        except (ValueError, TypeError) as exc:
            return FenTools._failure(exc)

    @staticmethod
    def play_moves(
        fen: str,
        moves: list[str],
        notation: Literal["SAN", "UCI"] = "SAN",
    ) -> dict[str, Any]:
        """Apply SAN or UCI moves and return the resulting position."""
        try:
            if notation not in ("SAN", "UCI"):
                raise ValueError("notation must be 'SAN' or 'UCI'")
            board = FenTools._board(fen)
            applied_moves = []
            for index, move_text in enumerate(moves):
                if notation == "SAN":
                    move = board.parse_san(move_text)
                else:
                    move = chess.Move.from_uci(move_text)
                    if move not in board.legal_moves:
                        raise ValueError(f"Illegal UCI move in this position: {move_text}")

                applied_moves.append(
                    {
                        "ply": index + 1,
                        "san": board.san(move),
                        "uci": move.uci(),
                    }
                )
                board.push(move)

            return FenTools._success(
                {"fen": board.fen(), "applied_moves": applied_moves}
            )
        except (ValueError, TypeError) as exc:
            return FenTools._failure(exc)

    @staticmethod
    def inspect_position(
        fen: str,
        detail: Literal["summary", "legal_moves", "board", "all"] = "summary",
    ) -> dict[str, Any]:
        """Return position status; optionally include moves, board, or both."""
        try:
            if detail not in ("summary", "legal_moves", "board", "all"):
                raise ValueError(
                    "detail must be 'summary', 'legal_moves', 'board', or 'all'"
                )

            board = FenTools._board(fen)
            position_status = FenTools._position_status(board)
            data: dict[str, Any] = {
                "fen": board.fen(),
                **position_status,
            }
            if not position_status["valid"]:
                return FenTools._success(data)

            outcome = board.outcome(claim_draw=True)
            data.update(
                {
                    "turn": "white" if board.turn else "black",
                    "is_check": board.is_check(),
                    "is_checkmate": board.is_checkmate(),
                    "is_stalemate": board.is_stalemate(),
                    "is_insufficient_material": board.is_insufficient_material(),
                    "is_game_over": outcome is not None,
                    "result": outcome.result() if outcome else None,
                    "termination": (
                        outcome.termination.name.lower() if outcome else None
                    ),
                    "legal_moves_count": board.legal_moves.count(),
                    "halfmove_clock": board.halfmove_clock,
                    "fullmove_number": board.fullmove_number,
                    "material_balance": FenTools._material_balance(board),
                }
            )
            if detail in ("legal_moves", "all"):
                data["legal_moves"] = FenTools._legal_moves(board)
            if detail in ("board", "all"):
                data["board_ascii"] = str(board)
            return FenTools._success(data)
        except (ValueError, TypeError) as exc:
            return FenTools._failure(exc)

    @staticmethod
    def _score_data(score: chess.engine.Score) -> dict[str, int | None]:
        if score.is_mate():
            return {"centipawns": None, "mate_in": score.mate()}
        return {"centipawns": score.score(), "mate_in": None}

    @staticmethod
    def stockfish_analyze(
        fen: str,
        analysis_mode: Literal["evaluation", "best_move", "variations"] = "evaluation",
        depth: int = 12,
        multipv: int = 3,
        time_limit: float = 2.0,
    ) -> dict[str, Any]:
        """Evaluate, find the best move, or compare Stockfish candidate lines."""
        try:
            if analysis_mode not in ("evaluation", "best_move", "variations"):
                raise ValueError(
                    "analysis_mode must be 'evaluation', 'best_move', or 'variations'"
                )
            if type(depth) is not int or not 1 <= depth <= 30:
                raise ValueError("depth must be an integer between 1 and 30")
            if type(multipv) is not int or not 1 <= multipv <= 5:
                raise ValueError("multipv must be an integer between 1 and 5")
            if (
                isinstance(time_limit, bool)
                or not isinstance(time_limit, (int, float))
                or not 0.1 <= time_limit <= 10
            ):
                raise ValueError("time_limit must be between 0.1 and 10 seconds")

            board = FenTools._board(fen)
            if not board.is_valid():
                raise ValueError(
                    f"Cannot analyze an invalid chess position (status {board.status()})"
                )

            line_count = multipv if analysis_mode == "variations" else 1
            with chess.engine.SimpleEngine.popen_uci(
                STOCKFISH_PATH,
                timeout=max(10.0, time_limit + 5.0),
            ) as engine:
                engine_lines = engine.analyse(
                    board,
                    chess.engine.Limit(depth=depth, time=time_limit),
                    multipv=line_count,
                )

            lines = []
            for rank, info in enumerate(engine_lines, start=1):
                score = info["score"]
                principal_variation = info.get("pv", [])
                pv_board = board.copy()
                pv_san = []
                pv_uci = []
                for move in principal_variation:
                    pv_san.append(pv_board.san(move))
                    pv_uci.append(move.uci())
                    pv_board.push(move)

                first_move = principal_variation[0] if principal_variation else None
                lines.append(
                    {
                        "rank": rank,
                        "best_move": (
                            {
                                "san": board.san(first_move),
                                "uci": first_move.uci(),
                            }
                            if first_move is not None
                            else None
                        ),
                        "score_white": FenTools._score_data(
                            score.pov(chess.WHITE)
                        ),
                        "score_side_to_move": FenTools._score_data(
                            score.pov(board.turn)
                        ),
                        "principal_variation_san": pv_san,
                        "principal_variation_uci": pv_uci,
                    }
                )

            data: dict[str, Any] = {
                "fen": board.fen(),
                "turn": "white" if board.turn else "black",
                "analysis_mode": analysis_mode,
                "depth_reached": max(
                    (info.get("depth", 0) for info in engine_lines),
                    default=0,
                ),
                "nodes": max(
                    (info.get("nodes", 0) for info in engine_lines),
                    default=0,
                ),
                "time_seconds": max(
                    (info.get("time", 0.0) for info in engine_lines),
                    default=0.0,
                ),
                "score_convention": (
                    "Positive scores favor the named perspective; centipawns are "
                    "1/100 of a pawn and mate_in is signed."
                ),
            }

            if analysis_mode == "variations":
                data["lines"] = lines
            else:
                line = lines[0] if lines else None
                data["evaluation"] = (
                    {
                        "score_white": line["score_white"],
                        "score_side_to_move": line["score_side_to_move"],
                    }
                    if line
                    else None
                )
                if analysis_mode == "best_move":
                    data["best_move"] = line["best_move"] if line else None
                    data["principal_variation_san"] = (
                        line["principal_variation_san"] if line else []
                    )
                    data["principal_variation_uci"] = (
                        line["principal_variation_uci"] if line else []
                    )

            return FenTools._success(data)
        except (
            ValueError,
            TypeError,
            OSError,
            chess.engine.EngineError,
        ) as exc:
            return FenTools._failure(exc)
