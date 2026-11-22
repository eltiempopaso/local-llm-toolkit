import io
import os
from typing import Any

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
    """FEN, move, position and Stockfish analysis helpers for MCP tools."""

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
    def _score_data(score: chess.engine.Score) -> dict[str, int | None]:
        if score.is_mate():
            return {"centipawns": None, "mate_in": score.mate()}
        return {"centipawns": score.score(), "mate_in": None}

    @staticmethod
    def _validate_analysis_limits(
        depth: int,
        multipv: int,
        time_limit: float,
    ) -> None:
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

    @staticmethod
    def _analyze(
        fen: str,
        depth: int,
        multipv: int,
        time_limit: float,
    ) -> dict[str, Any]:
        FenTools._validate_analysis_limits(depth, multipv, time_limit)
        board = FenTools._board(fen)
        if not board.is_valid():
            raise ValueError(
                f"Cannot analyze an invalid chess position (status {board.status()})"
            )

        with chess.engine.SimpleEngine.popen_uci(
            STOCKFISH_PATH,
            timeout=max(10.0, time_limit + 5.0),
        ) as engine:
            engine_lines = engine.analyse(
                board,
                chess.engine.Limit(depth=depth, time=time_limit),
                multipv=multipv,
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
                    "score_white": FenTools._score_data(score.pov(chess.WHITE)),
                    "score_side_to_move": FenTools._score_data(
                        score.pov(board.turn)
                    ),
                    "principal_variation_san": pv_san,
                    "principal_variation_uci": pv_uci,
                }
            )

        return {
            "fen": board.fen(),
            "turn": "white" if board.turn else "black",
            "depth_reached": max(
                (info.get("depth", 0) for info in engine_lines),
                default=0,
            ),
            "nodes": max((info.get("nodes", 0) for info in engine_lines), default=0),
            "time_seconds": max(
                (info.get("time", 0.0) for info in engine_lines),
                default=0.0,
            ),
            "lines": lines,
            "score_convention": (
                "Positive scores favor the named perspective; centipawns are "
                "1/100 of a pawn and mate_in is signed."
            ),
        }

    @staticmethod
    def pgn_to_fen(pgn: str) -> dict[str, Any]:
        """Return the final main-line position and move list from a PGN."""
        try:
            game = chess.pgn.read_game(io.StringIO(pgn))
            if game is None:
                raise ValueError("No valid PGN game was found.")
            board = game.board()
            moves_san = []
            for move in game.mainline_moves():
                moves_san.append(board.san(move))
                board.push(move)
            return FenTools._success(
                {
                    "fen": board.fen(),
                    "moves_san": moves_san,
                    "move_count": len(moves_san),
                    "headers": dict(game.headers),
                    "warnings": [str(error) for error in game.errors],
                }
            )
        except (ValueError, TypeError) as exc:
            return FenTools._failure(exc)

    @staticmethod
    def apply_san_moves(fen: str, moves: list[str]) -> dict[str, Any]:
        """Apply SAN moves sequentially and report the resulting FEN."""
        try:
            board = FenTools._board(fen)
            applied_moves = []
            for index, san in enumerate(moves):
                move = board.parse_san(san)
                normalized_san = board.san(move)
                board.push(move)
                applied_moves.append(
                    {"ply": index + 1, "san": normalized_san, "uci": move.uci()}
                )
            return FenTools._success(
                {"fen": board.fen(), "applied_moves": applied_moves}
            )
        except (ValueError, TypeError) as exc:
            return FenTools._failure(exc)

    @staticmethod
    def validate_fen(fen: str) -> dict[str, Any]:
        """Distinguish FEN parse errors from chess-position validity."""
        try:
            board = FenTools._board(fen)
            status = board.status()
            return FenTools._success(
                {
                    "valid": board.is_valid(),
                    "status_code": int(status),
                    "status_flags": [
                        flag.name.lower()
                        for flag in POSITION_STATUS_FLAGS
                        if status & flag
                    ],
                    "fen": board.fen(),
                }
            )
        except (ValueError, TypeError) as exc:
            return FenTools._failure(exc)

    @staticmethod
    def legal_moves(fen: str) -> dict[str, Any]:
        """List legal moves with SAN, UCI, and useful move attributes."""
        try:
            board = FenTools._board(fen)
            moves = []
            for move in board.legal_moves:
                moves.append(
                    {
                        "san": board.san(move),
                        "uci": move.uci(),
                        "from": chess.square_name(move.from_square),
                        "to": chess.square_name(move.to_square),
                        "is_capture": board.is_capture(move),
                        "promotion": (
                            chess.piece_name(move.promotion)
                            if move.promotion
                            else None
                        ),
                    }
                )
            return FenTools._success({"count": len(moves), "moves": moves})
        except (ValueError, TypeError) as exc:
            return FenTools._failure(exc)

    @staticmethod
    def san_to_uci(fen: str, san: str) -> dict[str, Any]:
        try:
            board = FenTools._board(fen)
            move = board.parse_san(san)
            return FenTools._success(
                {"san": board.san(move), "uci": move.uci()}
            )
        except (ValueError, TypeError) as exc:
            return FenTools._failure(exc)

    @staticmethod
    def uci_to_san(fen: str, uci: str) -> dict[str, Any]:
        try:
            board = FenTools._board(fen)
            move = chess.Move.from_uci(uci)
            if move not in board.legal_moves:
                raise ValueError(f"Illegal move in this position: {uci}")
            return FenTools._success(
                {"uci": move.uci(), "san": board.san(move)}
            )
        except (ValueError, TypeError) as exc:
            return FenTools._failure(exc)

    @staticmethod
    def position_summary(fen: str) -> dict[str, Any]:
        try:
            board = FenTools._board(fen)
            outcome = board.outcome(claim_draw=True)
            return FenTools._success(
                {
                    "fen": board.fen(),
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
                }
            )
        except (ValueError, TypeError) as exc:
            return FenTools._failure(exc)

    @staticmethod
    def is_checkmate(fen: str) -> dict[str, Any]:
        try:
            return FenTools._success(FenTools._board(fen).is_checkmate())
        except (ValueError, TypeError) as exc:
            return FenTools._failure(exc)

    @staticmethod
    def is_draw(fen: str) -> dict[str, Any]:
        try:
            board = FenTools._board(fen)
            outcome = board.outcome(claim_draw=True)
            return FenTools._success(
                bool(outcome and outcome.winner is None)
            )
        except (ValueError, TypeError) as exc:
            return FenTools._failure(exc)

    @staticmethod
    def board_ascii(fen: str) -> dict[str, Any]:
        try:
            return FenTools._success(str(FenTools._board(fen)))
        except (ValueError, TypeError) as exc:
            return FenTools._failure(exc)

    @staticmethod
    def material_balance(fen: str) -> dict[str, Any]:
        try:
            board = FenTools._board(fen)
            material = {
                color: sum(
                    len(board.pieces(piece_type, chess_color)) * value
                    for piece_type, value in PIECE_VALUES.items()
                )
                for color, chess_color in (
                    ("white", chess.WHITE),
                    ("black", chess.BLACK),
                )
            }
            return FenTools._success(
                {
                    "white": material["white"],
                    "black": material["black"],
                    "white_minus_black": material["white"] - material["black"],
                    "unit": "pawn_value",
                }
            )
        except (ValueError, TypeError) as exc:
            return FenTools._failure(exc)

    @staticmethod
    def available_captures(fen: str) -> dict[str, Any]:
        try:
            board = FenTools._board(fen)
            captures = [
                {"san": board.san(move), "uci": move.uci()}
                for move in board.legal_moves
                if board.is_capture(move)
            ]
            return FenTools._success({"count": len(captures), "captures": captures})
        except (ValueError, TypeError) as exc:
            return FenTools._failure(exc)

    @staticmethod
    def opponent_capture_threats(fen: str) -> dict[str, Any]:
        """List captures available after hypothetically giving the opponent the move."""
        try:
            board = FenTools._board(fen)
            opponent_board = board.copy(stack=False)
            opponent_board.turn = not board.turn
            captures = [
                {"san": opponent_board.san(move), "uci": move.uci()}
                for move in opponent_board.legal_moves
                if opponent_board.is_capture(move)
            ]
            return FenTools._success(
                {
                    "note": (
                        "Hypothetical opponent captures with the turn switched; "
                        "this is not a full tactical analysis."
                    ),
                    "count": len(captures),
                    "captures": captures,
                }
            )
        except (ValueError, TypeError) as exc:
            return FenTools._failure(exc)

    @staticmethod
    def analyze_position(
        fen: str,
        depth: int = 12,
        multipv: int = 3,
        time_limit: float = 2.0,
    ) -> dict[str, Any]:
        """Analyze a position with MultiPV; limits stop at depth or time, whichever comes first."""
        try:
            return FenTools._success(
                FenTools._analyze(fen, depth, multipv, time_limit)
            )
        except (ValueError, TypeError, OSError, chess.engine.EngineError) as exc:
            return FenTools._failure(exc)

    @staticmethod
    def best_move(
        fen: str,
        depth: int = 12,
        time_limit: float = 2.0,
    ) -> dict[str, Any]:
        """Return Stockfish's top move, score, and principal variation."""
        result = FenTools.analyze_position(
            fen,
            depth=depth,
            multipv=1,
            time_limit=time_limit,
        )
        if not result["success"]:
            return result
        analysis = result["data"]
        line = analysis["lines"][0] if analysis["lines"] else None
        return FenTools._success(
            {
                "fen": analysis["fen"],
                "turn": analysis["turn"],
                "depth_reached": analysis["depth_reached"],
                "nodes": analysis["nodes"],
                "time_seconds": analysis["time_seconds"],
                "best_line": line,
                "score_convention": analysis["score_convention"],
            }
        )

    @staticmethod
    def evaluate_position(
        fen: str,
        depth: int = 12,
        time_limit: float = 2.0,
    ) -> dict[str, Any]:
        """Return a Stockfish score from White's and the side-to-move perspectives."""
        result = FenTools.best_move(fen, depth=depth, time_limit=time_limit)
        if not result["success"]:
            return result
        data = result["data"]
        line = data["best_line"]
        return FenTools._success(
            {
                "fen": data["fen"],
                "turn": data["turn"],
                "depth_reached": data["depth_reached"],
                "score_white": line["score_white"] if line else None,
                "score_side_to_move": (
                    line["score_side_to_move"] if line else None
                ),
                "score_convention": data["score_convention"],
            }
        )
