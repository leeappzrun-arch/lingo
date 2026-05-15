from textual.app import ComposeResult
from textual.containers import Center, Middle, Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Static

from lingo.scores import save_score


class NamePromptScreen(ModalScreen[str]):
    """Modal shown after a win: collect a name, persist the score, go to leaderboard."""

    BINDINGS = [("escape", "dismiss", "Cancel")]

    def __init__(
        self,
        *,
        score: int,
        attempts: int,
        seconds: float,
        word: str,
    ) -> None:
        super().__init__()
        self.score = score
        self.attempts = attempts
        self.seconds = seconds
        self.word = word

    def compose(self) -> ComposeResult:
        mins, secs = divmod(int(self.seconds), 60)
        with Middle():
            with Center():
                yield Vertical(
                    Static("[b green]NAILED IT![/]", id="win-title"),
                    Static(
                        f"score [b]{self.score}[/]  ·  {self.attempts}/6  ·  {mins}:{secs:02d}",
                        id="win-stats",
                    ),
                    Static("enter your name for the leaderboard:", id="win-hint"),
                    Input(placeholder="your name", id="name-input", max_length=12),
                    id="win-box",
                )

    def on_mount(self) -> None:
        self.query_one("#name-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        save_score(
            name=event.value,
            score=self.score,
            attempts=self.attempts,
            seconds=self.seconds,
            word=self.word,
        )
        self.app.switch_screen("leaderboard")
