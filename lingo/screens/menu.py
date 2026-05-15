from textual.app import ComposeResult
from textual.containers import Center, Middle, Vertical
from textual.screen import Screen
from textual.widgets import Label, ListItem, ListView, Static

from lingo.screens.splash import LOGO


class MenuScreen(Screen):
    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        with Middle():
            with Center():
                yield Static(LOGO, id="logo-small")
            with Center():
                yield Vertical(
                    ListView(
                        ListItem(Label("New Game"), id="new"),
                        ListItem(Label("Leaderboard"), id="leaderboard"),
                        ListItem(Label("How to Play"), id="help"),
                        ListItem(Label("Quit"), id="quit"),
                        id="menu",
                    ),
                    id="menu-box",
                )
            with Center():
                yield Static("↑/↓ to move · enter to select · q to quit", id="hint")

    def on_mount(self) -> None:
        self.query_one("#menu", ListView).focus()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        choice = event.item.id
        if choice == "new":
            self.app.push_screen("game")
        elif choice == "leaderboard":
            self.app.push_screen("leaderboard")
        elif choice == "help":
            self.app.push_screen("help")
        elif choice == "quit":
            self.app.exit()
