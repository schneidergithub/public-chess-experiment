from __future__ import annotations

from dataclasses import dataclass

import chess


@dataclass(frozen=True)
class PuzzleModel:
    puzzle_id: str
    rating: int | None
    themes: list[str]
    solution: list[str]
    fen: str
    side_to_move: str
    perf: str | None


def _extract_fen(raw_payload: dict) -> str:
    puzzle = raw_payload.get("puzzle", {})
    game = raw_payload.get("game", {})

    for fen_value in (puzzle.get("fen"), raw_payload.get("fen"), game.get("fen")):
        if fen_value:
            return str(fen_value)

    raise ValueError("No FEN found in payload. Expected puzzle.fen, raw.fen, or game.fen")


def _extract_perf(raw_payload: dict) -> str | None:
    perf_value = raw_payload.get("game", {}).get("perf")
    if isinstance(perf_value, dict):
        return perf_value.get("name") or perf_value.get("key")
    if perf_value is None:
        return None
    return str(perf_value)


def normalize_puzzle(raw_payload: dict) -> PuzzleModel:
    puzzle = raw_payload.get("puzzle", {})
    fen = _extract_fen(raw_payload)
    board = chess.Board(fen)
    side_to_move = "white" if board.turn == chess.WHITE else "black"

    return PuzzleModel(
        puzzle_id=str(puzzle.get("id", "")),
        rating=puzzle.get("rating"),
        themes=[str(item) for item in puzzle.get("themes", [])],
        solution=[str(item) for item in puzzle.get("solution", [])],
        fen=fen,
        side_to_move=side_to_move,
        perf=_extract_perf(raw_payload),
    )
