# pytemon

Python Pokemon game library with interactive terminal UI.

> **Disclaimer:** This is an unofficial fan project and is not affiliated with, endorsed by, or connected to Nintendo, Game Freak, or The Pokémon Company. Pokémon and all related names are trademarks of Nintendo / Creatures Inc. / GAME FREAK inc. This project is made for educational and entertainment purposes only, with love for the franchise.

## Overview

`pytemon` is a pure Python library that implements an interactive Pokemon game using the [Textual](https://textual.textualize.io/) TUI framework. It contains the full game engine — exploration, battles, items, gyms, evolution, and a rich terminal interface.

The [robotframework-pokemon](https://github.com/MobyNL/robotframework-pokemon) sibling project wraps this library as a Robot Framework keyword library.

## Setup

```bash
cd pytemon/
poetry install
```

## Run the game directly

```bash
poetry run python run_terminal.py
```

## Run unit tests

```bash
poetry run pytest tests/ --tb=short -v --cov=pytemon --cov-report=term-missing
```

## Project structure

```
pytemon/
├── pytemon/           # The Python package
│   ├── terminal.py    # Textual TUI app
│   ├── game_state.py  # Central game state
│   ├── exploration.py # Movement and encounters
│   ├── buildings.py   # Pokemon Center, Pokemart, etc.
│   ├── battle/        # Battle UI and actions
│   ├── data/          # Pokemon, move, trainer data
│   ├── engine/        # Core battle engine
│   └── ui/            # TUI mixin modules
├── tests/             # Pytest unit tests
├── run_terminal.py    # Direct launcher
└── pyproject.toml
```
