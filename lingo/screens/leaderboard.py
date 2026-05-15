from textual.app import ComposeResult
from textual.containers import Center, Middle
from textual.screen import Screen
from textual.widgets import Static

from lingo.scores import load_scores
from lingo.screens.splash import LOGO


class LeaderboardScreen(Screen):
    BINDINGS = [("escape", "app.pop_screen", "Menu")]

    def compose(self) -> ComposeResult:
        with Middle():
            with Center():
                yield Static(LOGO, id="logo-small")
            with Center():
                yield Static("LEADERBOARD", id="title")
            with Center():
                yield Static(self._render_table(), id="leaderboard-table")
            with Center():
                yield Static("esc to return", id="hint")

    def _render_table(self) -> str:
        scores = load_scores()
        if not scores:
            return "[dim]no scores yet — go play a game[/]"
        lines = [
            "[b] #   NAME          SCORE   GUESSES  TIME   WORD[/]",
            "[dim]" + "─" * 50 + "[/]",
        ]
        for i, s in enumerate(scores, 1):
            mins, secs = divmod(s["seconds"], 60)
            time_str = f"{mins}:{secs:02d}"
            lines.append(
                f" {i:>2}   {s['name']:<12}  {s['score']:>5}   {s['attempts']:>2}/6    "
                f"{time_str:<5}  {s['word'].upper()}"
            )
        return "\n".join(lines)
