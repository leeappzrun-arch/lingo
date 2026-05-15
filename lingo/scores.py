"""Leaderboard storage + score formula."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

MAX_GUESSES = 6
TOP_N = 10


def calculate_score(attempts: int, seconds: float) -> int:
    """Score = attempt bonus (1000 per saved guess) + time bonus (5/sec under 5min)."""
    attempt_bonus = (MAX_GUESSES - attempts + 1) * 1000
    time_bonus = max(0, int((300 - seconds) * 5))
    return attempt_bonus + time_bonus


def _scores_path() -> Path:
    base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    p = Path(base) / "lingo"
    p.mkdir(parents=True, exist_ok=True)
    return p / "scores.json"


def load_scores() -> list[dict]:
    path = _scores_path()
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_score(
    *, name: str, score: int, attempts: int, seconds: float, word: str
) -> list[dict]:
    scores = load_scores()
    scores.append(
        {
            "name": (name.strip() or "anon")[:12],
            "score": score,
            "attempts": attempts,
            "seconds": int(seconds),
            "word": word,
            "ts": datetime.utcnow().isoformat(timespec="seconds"),
        }
    )
    scores.sort(key=lambda s: s["score"], reverse=True)
    scores = scores[:TOP_N]
    _scores_path().write_text(json.dumps(scores, indent=2))
    return scores
