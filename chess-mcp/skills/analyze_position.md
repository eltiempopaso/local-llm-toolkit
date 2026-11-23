# Analyze a Chess Position

Use this workflow whenever the user asks to analyze a chess position, evaluate
Stockfish's score, identify the better side, recommend a move, or compare
candidate lines.

## Establish the position

1. Use the FEN supplied by the user, or derive the position from the supplied
   PGN or move sequence with `pgn_to_position` or `play_moves`.
2. Do not assume the standard starting position unless the user says the game
   starts there.
3. If there is no FEN or enough move history to determine the position, ask the
   user for it instead of inventing one.
4. Call `inspect_position` to verify the FEN before engine analysis. If it is
   invalid, explain the returned status flags and request a corrected position.

## Choose the Stockfish analysis mode

Call `stockfish_analyze` for the engine result:

- Use `analysis_mode="evaluation"` for a score or "who is better?" question.
- Use `analysis_mode="best_move"` when the user asks what to play or for the
  engine's recommendation.
- Use `analysis_mode="variations"` to compare candidate moves or provide
  multiple principal variations. Choose `multipv` between 1 and 5 based on the
  requested number of lines.
- Keep the default search limits unless the user requests a deeper or faster
  analysis. `depth` is capped at 30 and `time_limit` at 10 seconds.

## Interpret and report the result

1. Report the achieved depth and the side to move.
2. A positive `score_white` favors White; a negative one favors Black.
   `score_side_to_move` is from the perspective of the player whose turn it is.
3. Centipawns are hundredths of a pawn: for example, `35` means approximately
   `+0.35` pawns for the indicated perspective. State the perspective explicitly.
4. If `mate_in` is not null, report the signed forced-mate distance instead of
   describing it as a centipawn score.
5. Present suggested moves in SAN and include the principal variation when
   useful. Do not claim that a short, limited search is a definitive result.
6. Only report values and moves returned by the tool. If the tool returns an
   error, relay the issue and do not fabricate an evaluation.
7. Always show a diagram with the analyzed position

## Example

For "What is Stockfish's evaluation of this position?", validate the supplied
FEN, call `stockfish_analyze` with `analysis_mode="evaluation"`, then explain the
score and its perspective. If the user also asks for the best move, use
`analysis_mode="best_move"` instead.