from __future__ import annotations

import argparse
import json
from datetime import UTC, date, datetime
from pathlib import Path

from src.build_video import build_video
from src.fetch_puzzle import fetch_daily_puzzle, save_raw_puzzle
from src.metadata import write_metadata
from src.puzzle_model import normalize_puzzle
from src.render_board import render_frames
from src.state_manager import StateManager

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "app.json"


def _log_event(step: str, event: str, **fields: object) -> None:
    payload: dict[str, object] = {
        "timestamp": datetime.now(UTC).isoformat(),
        "step": step,
        "event": event,
    }
    payload.update(fields)
    print(json.dumps(payload, sort_keys=True))


def _load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text())


def smoke_test() -> int:
    _load_config()
    _log_event("smoke-test", "ok")
    return 0


def run_pipeline(skip_upload: bool, force: bool) -> int:
    config = _load_config()
    run_date = date.today().isoformat()
    artifacts_dir = PROJECT_ROOT / "artifacts" / run_date
    frames_dir = artifacts_dir / "frames"
    puzzle_path = artifacts_dir / "puzzle.json"
    metadata_path = artifacts_dir / "metadata.json"
    video_path = artifacts_dir / "video.mp4"

    artifacts_dir.mkdir(parents=True, exist_ok=True)
    state_manager = StateManager(artifacts_dir)

    if state_manager.is_complete() and not force:
        _log_event("run", "already_complete", date=run_date, artifact_path=str(artifacts_dir))
        return 0

    if force:
        state_manager.reset()
        _log_event("run", "force_reset", date=run_date, artifact_path=str(artifacts_dir))

    try:
        step = "fetch"
        _log_event(step, "start", date=run_date)
        raw_payload = fetch_daily_puzzle()
        save_raw_puzzle(raw_payload, puzzle_path)
        state_manager.mark_step_done(step)
        _log_event(step, "complete", artifact_path=str(puzzle_path))

        step = "normalize"
        _log_event(step, "start", date=run_date)
        puzzle = normalize_puzzle(raw_payload)
        state_manager.mark_step_done(step)
        _log_event(step, "complete", puzzle_id=puzzle.puzzle_id)

        step = "render"
        _log_event(step, "start", date=run_date, artifact_path=str(frames_dir))
        frames = render_frames(puzzle, frames_dir, config)
        state_manager.mark_step_done(step)
        _log_event(step, "complete", frame_count=len(frames), artifact_path=str(frames_dir))

        step = "video"
        _log_event(step, "start", date=run_date, artifact_path=str(video_path))
        build_video(frames_dir, video_path, config)
        state_manager.mark_step_done(step)
        _log_event(step, "complete", artifact_path=str(video_path))

        step = "metadata"
        _log_event(step, "start", date=run_date, artifact_path=str(metadata_path))
        write_metadata(metadata_path, puzzle, frame_count=len(frames), video_path=video_path, config=config)
        state_manager.mark_step_done(step)
        _log_event(step, "complete", artifact_path=str(metadata_path))

        if skip_upload:
            _log_event("upload", "skipped", reason="--skip-upload")

        state_manager.mark_complete()
        _log_event("run", "complete", date=run_date, artifact_path=str(artifacts_dir))
        return 0
    except Exception as exc:  # noqa: BLE001
        state_manager.mark_error(step, str(exc))
        _log_event(
            step,
            "error",
            error_message=str(exc),
            artifact_path=str(artifacts_dir / "state" / f"{step}.error.json"),
        )
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Milestone 1 local chess puzzle video pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("smoke-test", help="Validate runtime setup and config loading")
    run_parser = subparsers.add_parser("run", help="Generate local puzzle video artifacts")
    run_parser.add_argument("--skip-upload", action="store_true", help="Do not upload artifacts")
    run_parser.add_argument("--force", action="store_true", help="Force rerun from scratch")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "smoke-test":
        return smoke_test()
    if args.command == "run":
        return run_pipeline(skip_upload=bool(args.skip_upload), force=bool(args.force))
    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
