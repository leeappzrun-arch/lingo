from textual.app import ComposeResult
from textual.containers import Center, Middle, Vertical
from textual.screen import Screen
from textual.widgets import Static

HELP_TEXT = """\
[b]How to play Lingo[/b]

Guess the hidden 5-letter word in [b]6 tries[/b].

After each guess, each letter is colored:
  [black on green] G [/]  correct letter, correct spot
  [black on yellow] Y [/]  letter is in the word, wrong spot
  [white on grey23] . [/]  letter is not in the word

[b]Controls[/b]
  A–Z       type a letter
  ENTER     submit guess
  BACKSPACE delete last letter
  ESC       return to menu
"""


class HelpScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Back")]

    def compose(self) -> ComposeResult:
        with Middle():
            with Center():
                yield Vertical(Static(HELP_TEXT, id="help-text"), id="help-box")
            with Center():
                yield Static("esc to return", id="hint")
