# Lingo

A terminal word game in the spirit of Wordle. Guess the 5-letter word in 6 tries.

```
 ██╗     ██╗███╗   ██╗ ██████╗  ██████╗
 ██║     ██║████╗  ██║██╔════╝ ██╔═══██╗
 ██║     ██║██╔██╗ ██║██║  ███╗██║   ██║
 ██║     ██║██║╚██╗██║██║   ██║██║   ██║
 ███████╗██║██║ ╚████║╚██████╔╝╚██████╔╝
 ╚══════╝╚═╝╚═╝  ╚═══╝ ╚═════╝  ╚═════╝
```

## Run

With [uv](https://docs.astral.sh/uv/) (recommended):

```sh
uv run python -m lingo
```

Or with a plain venv:

```sh
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m lingo
```

## How to play

- Type letters `A`–`Z` to fill the current row.
- `ENTER` submits the guess.
- `BACKSPACE` deletes the last letter.
- After each guess, letters are colored:
  - **green** — correct letter, correct spot
  - **yellow** — letter is in the word, wrong spot
  - **grey** — letter is not in the word
- `ESC` returns to the main menu.
- `q` quits from the menu, `Ctrl+C` quits from anywhere.

## Layout

```
lingo/
  lingo/
    __main__.py        # `python -m lingo`
    app.py             # Textual App + screen registration
    words.py           # word list
    screens/
      splash.py        # ASCII logo splash
      menu.py          # main menu
      game.py          # the game itself
      help.py          # how-to-play
    styles.tcss        # Textual CSS
  pyproject.toml
```
