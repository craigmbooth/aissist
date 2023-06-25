from pathlib import Path

current_dir = Path(__file__).resolve().parent
with open(current_dir / "VERSION") as f:
    __version__ = f.read().strip()
