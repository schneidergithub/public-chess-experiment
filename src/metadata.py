from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from src.puzzle_model import PuzzleModel


def write_metadata(
    metadata_path: Path,
    puzzle: PuzzleModel,
    frame_count: int,
    video_path: Path,
    config: dict,
) -> None:
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "date": metadata_path.parent.name,
        "generated_at": datetime.now(UTC).isoformat(),
        "puzzle_id": puzzle.puzzle_id,
        "rating": puzzle.rating,
        "themes": puzzle.themes,
        "side_to_move": puzzle.side_to_move,
        "perf": puzzle.perf,
        "frame_count": frame_count,
        "video_path": str(video_path),
        "video": config["video"],
        "render": config["render"],
    }
    metadata_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
