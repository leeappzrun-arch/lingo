from textual.app import App

from lingo.screens.game import GameScreen
from lingo.screens.help import HelpScreen
from lingo.screens.leaderboard import LeaderboardScreen
from lingo.screens.menu import MenuScreen
from lingo.screens.splash import SplashScreen


class LingoApp(App):
    CSS_PATH = "styles.tcss"
    TITLE = "Lingo"

    SCREENS = {
        "splash": SplashScreen,
        "menu": MenuScreen,
        "help": HelpScreen,
        "game": GameScreen,
        "leaderboard": LeaderboardScreen,
    }

    BINDINGS = [("ctrl+c", "quit", "Quit")]

    def on_mount(self) -> None:
        self.push_screen("splash")
