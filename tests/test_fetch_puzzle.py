import requests

from src.fetch_puzzle import LOCAL_FALLBACK_PUZZLE, PuzzleFetchError, fetch_daily_puzzle


class _FakeResponse:
    def __init__(self, status_code: int, payload: dict) -> None:
        self.status_code = status_code
        self._payload = payload

    def json(self) -> dict:
        return self._payload


def test_fetch_daily_puzzle_uses_live_response(monkeypatch) -> None:
    monkeypatch.setattr(
        requests,
        "get",
        lambda *args, **kwargs: _FakeResponse(200, {"puzzle": {"id": "live"}}),
    )

    payload = fetch_daily_puzzle()

    assert payload["puzzle"]["id"] == "live"


def test_fetch_daily_puzzle_uses_fallback_on_request_error(monkeypatch) -> None:
    def _raise(*args, **kwargs):
        raise requests.RequestException("offline")

    monkeypatch.setattr(requests, "get", _raise)

    payload = fetch_daily_puzzle()

    assert payload["puzzle"]["id"] == LOCAL_FALLBACK_PUZZLE["puzzle"]["id"]


def test_fetch_daily_puzzle_raises_on_non_200(monkeypatch) -> None:
    monkeypatch.setattr(
        requests,
        "get",
        lambda *args, **kwargs: _FakeResponse(500, {"error": "boom"}),
    )

    try:
        fetch_daily_puzzle()
    except PuzzleFetchError as exc:
        assert "500" in str(exc)
    else:
        raise AssertionError("Expected PuzzleFetchError for non-200 responses")
