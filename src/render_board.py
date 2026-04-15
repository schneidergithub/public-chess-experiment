from __future__ import annotations

from io import BytesIO
from pathlib import Path

import cairosvg
import chess
import chess.svg
from PIL import Image, ImageDraw, ImageFont

from src.puzzle_model import PuzzleModel


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def _render_board_image(board: chess.Board, board_size: int, show_coordinates: bool) -> Image.Image:
    svg_data = chess.svg.board(board=board, size=board_size, coordinates=show_coordinates)
    png_bytes = cairosvg.svg2png(bytestring=svg_data.encode("utf-8"))
    return Image.open(BytesIO(png_bytes)).convert("RGBA")


def _draw_centered_text(draw: ImageDraw.ImageDraw, text: str, y: int, font: ImageFont.ImageFont, fill: str, canvas_width: int) -> None:
    text_box = draw.textbbox((0, 0), text, font=font)
    text_width = text_box[2] - text_box[0]
    draw.text(((canvas_width - text_width) // 2, y), text, font=font, fill=fill)


def _save_scene(
    *,
    board: chess.Board,
    title: str,
    subtitle: str,
    frame_count: int,
    frame_index: int,
    frames_dir: Path,
    video_width: int,
    video_height: int,
    board_size: int,
    show_coordinates: bool,
    header_height: int,
    background_color: str,
    text_color: str,
    title_font: ImageFont.ImageFont,
    subtitle_font: ImageFont.ImageFont,
) -> int:
    board_image = _render_board_image(board, board_size, show_coordinates)
    x = (video_width - board_size) // 2
    y = header_height + max(0, (video_height - header_height - board_size) // 2)

    for _ in range(frame_count):
        frame = Image.new("RGB", (video_width, video_height), background_color)
        frame.paste(board_image, (x, y), board_image)
        draw = ImageDraw.Draw(frame)
        _draw_centered_text(draw, title, 48, title_font, text_color, video_width)
        _draw_centered_text(draw, subtitle, 132, subtitle_font, text_color, video_width)
        frame.save(frames_dir / f"frame_{frame_index:05d}.png")
        frame_index += 1

    return frame_index


def render_frames(puzzle: PuzzleModel, frames_dir: Path, config: dict) -> list[Path]:
    frames_dir.mkdir(parents=True, exist_ok=True)
    video = config["video"]
    render = config["render"]
    fps = int(video["fps"])
    video_width = int(video["width"])
    video_height = int(video["height"])
    header_height = int(render.get("header_height", 220))
    safe_board_size = min(
        int(render["board_size"]),
        video_width - 80,
        max(100, video_height - header_height - 40),
    )

    title_font = _load_font(int(render.get("title_font_size", 64)))
    subtitle_font = _load_font(int(render.get("subtitle_font_size", 42)))

    board = chess.Board(puzzle.fen)
    frame_index = 0

    frame_index = _save_scene(
        board=board,
        title=f"Lichess Daily Puzzle: {puzzle.puzzle_id}",
        subtitle=f"Rating {puzzle.rating or 'N/A'} · {puzzle.side_to_move} to move",
        frame_count=max(1, int(fps * float(render.get("intro_seconds", 1.0)))),
        frame_index=frame_index,
        frames_dir=frames_dir,
        video_width=video_width,
        video_height=video_height,
        board_size=safe_board_size,
        show_coordinates=bool(render.get("show_coordinates", True)),
        header_height=header_height,
        background_color=str(render.get("background_color", "#101010")),
        text_color=str(render.get("text_color", "#f2f2f2")),
        title_font=title_font,
        subtitle_font=subtitle_font,
    )

    frame_index = _save_scene(
        board=board,
        title="Find the best move",
        subtitle="Pause and calculate",
        frame_count=max(1, int(fps * float(render.get("think_seconds", 1.0)))),
        frame_index=frame_index,
        frames_dir=frames_dir,
        video_width=video_width,
        video_height=video_height,
        board_size=safe_board_size,
        show_coordinates=bool(render.get("show_coordinates", True)),
        header_height=header_height,
        background_color=str(render.get("background_color", "#101010")),
        text_color=str(render.get("text_color", "#f2f2f2")),
        title_font=title_font,
        subtitle_font=subtitle_font,
    )

    if puzzle.solution:
        first_move = chess.Move.from_uci(puzzle.solution[0])
        if first_move not in board.legal_moves:
            raise ValueError(f"Illegal first puzzle move for provided FEN: {puzzle.solution[0]}")
        board.push(first_move)
        frame_index = _save_scene(
            board=board,
            title=f"Solution: {puzzle.solution[0]}",
            subtitle="Best move played",
            frame_count=max(1, int(fps * float(render.get("solution_seconds", 1.0)))),
            frame_index=frame_index,
            frames_dir=frames_dir,
            video_width=video_width,
            video_height=video_height,
            board_size=safe_board_size,
            show_coordinates=bool(render.get("show_coordinates", True)),
            header_height=header_height,
            background_color=str(render.get("background_color", "#101010")),
            text_color=str(render.get("text_color", "#f2f2f2")),
            title_font=title_font,
            subtitle_font=subtitle_font,
        )

    _save_scene(
        board=board,
        title="Puzzle complete",
        subtitle=f"Themes: {', '.join(puzzle.themes) if puzzle.themes else 'N/A'}",
        frame_count=max(1, int(fps * float(render.get("outro_seconds", 1.0)))),
        frame_index=frame_index,
        frames_dir=frames_dir,
        video_width=video_width,
        video_height=video_height,
        board_size=safe_board_size,
        show_coordinates=bool(render.get("show_coordinates", True)),
        header_height=header_height,
        background_color=str(render.get("background_color", "#101010")),
        text_color=str(render.get("text_color", "#f2f2f2")),
        title_font=title_font,
        subtitle_font=subtitle_font,
    )

    return sorted(frames_dir.glob("frame_*.png"))
