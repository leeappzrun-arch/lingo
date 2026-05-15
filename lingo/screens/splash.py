from textual.app import ComposeResult
from textual.containers import Center, Middle
from textual.screen import Screen
from textual.widgets import Static

LOGO = r"""
 ██╗     ██╗███╗   ██╗ ██████╗  ██████╗
 ██║     ██║████╗  ██║██╔════╝ ██╔═══██╗
 ██║     ██║██╔██╗ ██║██║  ███╗██║   ██║
 ██║     ██║██║╚██╗██║██║   ██║██║   ██║
 ███████╗██║██║ ╚████║╚██████╔╝╚██████╔╝
 ╚══════╝╚═╝╚═╝  ╚═══╝ ╚═════╝  ╚═════╝
"""


class SplashScreen(Screen):
    """ASCII logo + tagline. Any key (or 1.5s timer) advances to the menu."""

    def compose(self) -> ComposeResult:
        with Middle():
            with Center():
                yield Static(LOGO, id="logo")
            with Center():
                yield Static("a wordle-style word game", id="tagline")
            with Center():
                yield Static("press any key to continue", id="hint")

    def advance(self) -> None:
        if self.app.screen is self:
            self.app.switch_screen("menu")

    def on_key(self, event) -> None:
        event.stop()
        self.advance()
