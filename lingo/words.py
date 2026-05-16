"""Word lists for Lingo.

ANSWERS is the pool the game picks the secret from (curated common 5-letter
words). VALID_WORDS is the full set of 5-letter words accepted as guesses —
ANSWERS plus a much larger list of less common real words.

Both lists are loaded from text files bundled in lingo/data/.
"""

from __future__ import annotations

from importlib.resources import files


def _load(name: str) -> tuple[str, ...]:
    text = files(__package__).joinpath("data", name).read_text(encoding="utf-8")
    return tuple(
        line.strip().lower()
        for line in text.splitlines()
        if len(line.strip()) == 5 and line.strip().isalpha()
    )


ANSWERS: tuple[str, ...] = _load("answers.txt")
_ALLOWED: tuple[str, ...] = _load("allowed.txt")

VALID_WORDS: frozenset[str] = frozenset(ANSWERS) | frozenset(_ALLOWED)


def is_valid_word(word: str) -> bool:
    return word.lower() in VALID_WORDS
