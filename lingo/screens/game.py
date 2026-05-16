from __future__ import annotations

import random
import time
from collections import Counter

from textual.app import ComposeResult
from textual.containers import Center, Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Static

from lingo.scores import calculate_score
from lingo.screens.name_prompt import NamePromptScreen
from lingo.screens.splash import LOGO
from lingo.words import ANSWERS, is_valid_word

WORD_LEN = 5
MAX_GUESSES = 6

# Cell color classes mapped to letter state.
HIT = "hit"        # green: correct letter + position
PRESENT = "present"  # yellow: in word, wrong position
MISS = "miss"      # grey: not in word
EMPTY = "empty"
PENDING = "pending"  # current row, typed but unsubmitted


def score_guess(guess: str, answer: str) -> list[str]:
    """Return per-letter state for guess against answer.

    Handles duplicate letters correctly (two-pass: hits first, then presents).
    """
    states = [MISS] * WORD_LEN
    remaining = Counter()
    for i, (g, a) in enumerate(zip(guess, answer)):
        if g == a:
            states[i] = HIT
        else:
            remaining[a] += 1
    for i, g in enumerate(guess):
        if states[i] == HIT:
            continue
        if remaining[g] > 0:
            states[i] = PRESENT
            remaining[g] -= 1
    return states


class Cell(Static):
    DEFAULT_CSS = ""

    def __init__(self, *, letter: str = " ", state: str = EMPTY) -> None:
        super().__init__(self._format(letter), classes=f"cell {state}")
        self._letter = letter
        self._state = state

    @staticmethod
    def _format(letter: str) -> str:
        return f" {letter.upper() if letter.strip() else ' '} "

    def set_cell(self, letter: str, state: str) -> None:
        if letter != self._letter:
            self._letter = letter
            self.update(self._format(letter))
        if state != self._state:
            self.remove_class(self._state)
            self.add_class(state)
            self._state = state


class GameScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Menu")]

    status: reactive[str] = reactive("")

    def __init__(self) -> None:
        super().__init__()
        self.answer = random.choice(ANSWERS)
        self.guesses: list[str] = []
        self.current: str = ""
        self.finished: bool = False
        self.cells: list[list[Cell]] = []
        self.key_states: dict[str, str] = {}
        self.start_time: float = 0.0
        self.elapsed: float = 0.0
        self.naming: bool = False
        self.won: bool = False
        self._anim_step: int = 0
        self._anim_timer = None

    def compose(self) -> ComposeResult:
        with Center():
            yield Static(LOGO, id="logo-small")
        with Center():
            with Horizontal(id="play-area"):
                yield Vertical(id="grid")
                with Vertical(id="keyboard-pane"):
                    yield Static(self._render_keyboard(), id="keyboard")
        with Center():
            yield Static("", id="status")
        with Center():
            yield Static(
                "type letters · enter to submit · esc for menu", id="hint"
            )

    def on_mount(self) -> None:
        grid = self.query_one("#grid", Vertical)
        for _ in range(MAX_GUESSES):
            row = Horizontal(classes="row")
            grid.mount(row)
            row_cells: list[Cell] = []
            for _ in range(WORD_LEN):
                cell = Cell()
                row.mount(cell)
                row_cells.append(cell)
            self.cells.append(row_cells)
        self.start_time = time.monotonic()

    # ---- input handling ----

    def on_key(self, event) -> None:
        if self.naming:
            # name input owns its keys
            return
        if self.finished:
            # any key after a loss returns to menu (win flow handles its own input)
            if not self.won and event.key in ("enter", "space", "escape"):
                event.stop()
                self.app.pop_screen()
            return
        key = event.key
        if key == "enter":
            event.stop()
            self._submit()
        elif key == "backspace":
            event.stop()
            self._backspace()
        elif len(key) == 1 and key.isalpha():
            event.stop()
            self.type_letter(key.lower())

    def type_letter(self, ch: str) -> None:
        if len(self.current) >= WORD_LEN:
            return
        self.current += ch
        row = len(self.guesses)
        self.cells[row][len(self.current) - 1].set_cell(ch, PENDING)
        self._set_status("")

    def _backspace(self) -> None:
        if self.finished or not self.current:
            return
        row = len(self.guesses)
        self.cells[row][len(self.current) - 1].set_cell(" ", EMPTY)
        self.current = self.current[:-1]

    def _submit(self) -> None:
        if self.finished:
            return
        if len(self.current) != WORD_LEN:
            self._set_status("need 5 letters", error=True)
            return
        if not is_valid_word(self.current):
            self._set_status(f"'{self.current.upper()}' is not a word", error=True)
            return
        row = len(self.guesses)
        states = score_guess(self.current, self.answer)
        for i, (ch, st) in enumerate(zip(self.current, states)):
            self.cells[row][i].set_cell(ch, st)
        self._update_key_states(self.current, states)
        self.query_one("#keyboard", Static).update(self._render_keyboard())
        self.guesses.append(self.current)

        if self.current == self.answer:
            self.finished = True
            self.won = True
            self.elapsed = time.monotonic() - self.start_time
            self.current = ""
            self._celebrate()
            return
        if len(self.guesses) >= MAX_GUESSES:
            self.finished = True
            self._set_status(
                f"out of guesses — answer was '{self.answer.upper()}'. enter/esc for menu",
                error=True,
            )
        else:
            self._set_status("")
        self.current = ""

    # ---- win flow ----

    _ANIM_COLORS = ("#ffd166", "#06d6a0", "#118ab2", "#ef476f", "#ffd166", "#06d6a0", "#118ab2", "#ef476f")

    def _celebrate(self) -> None:
        score = calculate_score(len(self.guesses), self.elapsed)
        self.win_score = score
        mins, secs = divmod(int(self.elapsed), 60)
        self.query_one("#status", Static).update(
            f"[b green]NAILED IT![/]  score [b]{score}[/]  ·  {len(self.guesses)}/6  ·  {mins}:{secs:02d}"
        )
        logo = self.query_one("#logo-small", Static)
        logo.add_class("winner")
        self._anim_step = 0
        self._anim_timer = self.set_interval(0.2, self._anim_tick)
        self.set_timer(1.8, self._show_name_prompt)

    def _anim_tick(self) -> None:
        logo = self.query_one("#logo-small", Static)
        logo.styles.color = self._ANIM_COLORS[self._anim_step % len(self._ANIM_COLORS)]
        self._anim_step += 1
        if self._anim_step >= len(self._ANIM_COLORS) and self._anim_timer is not None:
            self._anim_timer.stop()
            self._anim_timer = None

    def _show_name_prompt(self) -> None:
        self.naming = True
        self.app.push_screen(
            NamePromptScreen(
                score=self.win_score,
                attempts=len(self.guesses),
                seconds=self.elapsed,
                word=self.answer,
            )
        )

    # ---- presentation ----

    def _set_status(self, msg: str, *, error: bool = False, win: bool = False) -> None:
        widget = self.query_one("#status", Static)
        if win:
            widget.update(f"[b green]{msg}[/]")
        elif error:
            widget.update(f"[b red]{msg}[/]")
        else:
            widget.update(msg)

    def _update_key_states(self, guess: str, states: list[str]) -> None:
        rank = {MISS: 0, PRESENT: 1, HIT: 2}
        for ch, st in zip(guess, states):
            prev = self.key_states.get(ch)
            if prev is None or rank[st] > rank[prev]:
                self.key_states[ch] = st

    def _render_keyboard(self) -> str:
        rows = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]
        out_lines: list[str] = []
        for r in rows:
            parts: list[str] = []
            for ch in r:
                st = self.key_states.get(ch)
                label = f" {ch.upper()} "
                if st == HIT:
                    parts.append(f"[black on #6aaa64]{label}[/]")
                elif st == PRESENT:
                    parts.append(f"[black on #c9b458]{label}[/]")
                elif st == MISS:
                    parts.append(f"[#1a1a1a on #b0b0b0]{label}[/]")
                else:
                    parts.append(f"[#e0e0e0 on #3a3a3c]{label}[/]")
            out_lines.append(" ".join(parts))
        # indent middle and bottom rows slightly for a keyboard-y shape
        return "\n".join(
            [
                out_lines[0],
                "  " + out_lines[1],
                "      " + out_lines[2],
            ]
        )
