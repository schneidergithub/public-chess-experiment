from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path


class StateManager:
    def __init__(self, run_dir: Path) -> None:
        self.run_dir = run_dir
        self.state_dir = run_dir / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def reset(self) -> None:
        if self.state_dir.exists():
            shutil.rmtree(self.state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def is_complete(self) -> bool:
        return (self.state_dir / "run.complete").exists()

    def mark_step_done(self, step: str) -> None:
        (self.state_dir / f"{step}.done").write_text(datetime.now(UTC).isoformat() + "\n")

    def mark_error(self, step: str, error_message: str) -> None:
        payload = {
            "step": step,
            "error_message": error_message,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        (self.state_dir / f"{step}.error.json").write_text(json.dumps(payload, indent=2) + "\n")

    def mark_complete(self) -> None:
        (self.state_dir / "run.complete").write_text(datetime.now(UTC).isoformat() + "\n")
