from src.puzzle_model import normalize_puzzle


def test_normalize_prefers_puzzle_fen_and_perf_object() -> None:
    payload = {
        "game": {"perf": {"key": "classical", "name": "Classical"}, "fen": "8/8/8/8/8/8/8/8 w - - 0 1"},
        "puzzle": {
            "id": "abc123",
            "rating": 1800,
            "themes": ["middlegame", "short"],
            "solution": ["e2e4"],
            "fen": "8/8/8/8/8/8/8/8 b - - 0 1",
        },
        "fen": "8/8/8/8/8/8/8/8 w - - 0 1",
    }

    model = normalize_puzzle(payload)

    assert model.puzzle_id == "abc123"
    assert model.fen == "8/8/8/8/8/8/8/8 b - - 0 1"
    assert model.side_to_move == "black"
    assert model.perf == "Classical"


def test_normalize_uses_raw_fen_and_perf_string() -> None:
    payload = {
        "game": {"perf": "rapid"},
        "puzzle": {"id": "raw-fen", "themes": [], "solution": []},
        "fen": "8/8/8/8/8/8/8/8 w - - 0 1",
    }

    model = normalize_puzzle(payload)

    assert model.puzzle_id == "raw-fen"
    assert model.fen == "8/8/8/8/8/8/8/8 w - - 0 1"
    assert model.side_to_move == "white"
    assert model.perf == "rapid"
