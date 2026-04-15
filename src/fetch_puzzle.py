from __future__ import annotations

import json
from pathlib import Path

import requests

DAILY_PUZZLE_URL = "https://lichess.org/api/puzzle/daily"
LOCAL_FALLBACK_PUZZLE = {
    "game": {
        "id": "MwZcnjIz",
        "perf": {"key": "classical", "name": "Classical"},
        "rated": True,
        "players": [
            {"name": "antigua1956", "id": "antigua1956", "color": "white", "rating": 1747},
            {"name": "Shalaza", "id": "shalaza", "color": "black", "rating": 1735},
        ],
        "pgn": "e4 e5 f4 Nf6 fxe5 Nxe4 Nf3 d5 exd6 Nxd6 Nc3 Bg4 Be2 Be7 O-O O-O Ne5 Bxe2 Qxe2 Bf6 d3 Re8 Bf4 Nd7 d4 c5 dxc5",
        "clock": "15+15",
    },
    "puzzle": {
        "id": "N5nr0",
        "rating": 1804,
        "plays": 89042,
        "solution": ["f6e5", "f4e5", "e8e5"],
        "themes": ["middlegame", "advantage", "short"],
        "fen": "r2qr1k1/pp1n1ppp/3n1b2/2P1N3/5B2/2N5/PPP1Q1PP/R4RK1 b - - 0 1",
        "lastMove": "d4c5",
        "initialPly": 26,
    },
}


class PuzzleFetchError(RuntimeError):
    pass


def fetch_daily_puzzle(timeout_seconds: int = 30) -> dict:
    try:
        response = requests.get(
            DAILY_PUZZLE_URL,
            timeout=timeout_seconds,
            headers={"Accept": "application/json"},
        )
    except requests.RequestException:
        return LOCAL_FALLBACK_PUZZLE

    if response.status_code != 200:
        raise PuzzleFetchError(
            f"Daily puzzle fetch failed with status code {response.status_code}"
        )
    return response.json()


def save_raw_puzzle(raw_payload: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(raw_payload, indent=2, sort_keys=True) + "\n")
