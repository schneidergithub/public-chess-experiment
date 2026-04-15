# public-chess-experiment
automated chess video

## Milestone 1 local run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
python -m src.main smoke-test
python -m src.main run --skip-upload --force
```
