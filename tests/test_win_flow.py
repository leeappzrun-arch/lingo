"""Drive the game to a win and assert the name prompt appears.

Run with the project venv:
    .venv/bin/python tests/test_win_flow.py
"""

from __future__ import annotations

import asyncio
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from textual.widgets import Input  # noqa: E402

from lingo.app import LingoApp  # noqa: E402
from lingo.screens.game import GameScreen  # noqa: E402


ANSWER = "apple"


async def run() -> int:
    # force a known answer
    random.choice = lambda _seq: ANSWER  # type: ignore[assignment]

    app = LingoApp()
    # mimic a typical terminal size so we catch layout overflow
    async with app.run_test(size=(100, 30)) as pilot:
        # splash → menu
        await pilot.press("space")
        await pilot.pause(0.1)

        # menu: "New Game" is first item, enter selects it
        await pilot.press("enter")
        await pilot.pause(0.1)

        # we should now be on the game screen
        screen = app.screen
        if not isinstance(screen, GameScreen):
            print(f"FAIL: expected GameScreen, got {type(screen).__name__}")
            return 1
        if screen.answer != ANSWER:
            print(f"FAIL: answer not forced — got {screen.answer!r}")
            return 1

        # type the answer + submit
        for ch in ANSWER:
            await pilot.press(ch)
        await pilot.press("enter")

        # animation runs ~1.6s, name prompt scheduled at 1.8s — wait past that
        await pilot.pause(2.5)

        if not screen.won:
            print("FAIL: screen.won is False after submitting the answer")
            return 1
        if not screen.naming:
            print("FAIL: screen.naming is False — _show_name_prompt didn't run")
            return 1

        from lingo.screens.name_prompt import NamePromptScreen

        modal = app.screen
        if not isinstance(modal, NamePromptScreen):
            print(
                f"FAIL: top screen is {type(modal).__name__}, expected NamePromptScreen"
            )
            return 1

        inputs = list(modal.query(Input))
        if len(inputs) != 1 or inputs[0].id != "name-input":
            print(f"FAIL: expected one #name-input on modal, got {[i.id for i in inputs]}")
            return 1
        prompt = inputs[0]
        r = prompt.region
        screen_size = app.size
        print(f"INFO: screen={screen_size}, name-input region={r}")
        if r.y < 0 or r.bottom > screen_size.height:
            print(
                f"FAIL: name-input off-screen — y={r.y}, bottom={r.bottom}, "
                f"screen height={screen_size.height}"
            )
            return 1
        if app.focused is not prompt:
            focused = app.focused.id if app.focused else None
            print(f"FAIL: focus is on #{focused}, not #name-input")
            return 1

        print("PASS: name-prompt modal mounted, on-screen, and focused")
        return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(run()))
