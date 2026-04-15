from __future__ import annotations

import subprocess
from pathlib import Path
from shutil import which

import imageio_ffmpeg


def build_video(frames_dir: Path, output_path: Path, config: dict) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    video = config["video"]
    ffmpeg_config = config.get("ffmpeg", {})
    requested_binary = str(ffmpeg_config.get("binary", "ffmpeg"))
    timeout_seconds = int(ffmpeg_config.get("timeout_seconds", 300))
    ffmpeg_binary = requested_binary if which(requested_binary) else imageio_ffmpeg.get_ffmpeg_exe()

    command = [
        str(ffmpeg_binary),
        "-y",
        "-framerate",
        str(video["fps"]),
        "-i",
        str(frames_dir / "frame_%05d.png"),
        "-c:v",
        str(video.get("codec", "libx264")),
        "-pix_fmt",
        str(video.get("pixel_format", "yuv420p")),
        "-an",
        str(output_path),
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"FFmpeg timed out after {timeout_seconds}s") from exc
    if result.returncode != 0:
        raise RuntimeError(
            f"FFmpeg failed ({result.returncode}): {result.stderr.strip() or result.stdout.strip()}"
        )
