# Python Examples

This directory contains Python examples demonstrating different ways to use the pytemon library.

## Running the Examples

From the `pytemon/` directory:

```bash
# Basic terminal launch
poetry run python examples/basic_launch.py

# Programmatic game state manipulation
poetry run python examples/programmatic_game.py

# Battle simulation
poetry run python examples/battle_simulation.py
```

## Examples Overview

### 1. `basic_launch.py` - Launch the Interactive Terminal

The simplest way to run the game from Python. This launches the full Textual TUI interface.

**Use case:** Embedding the game in a larger Python application, custom launchers.

```python
from pytemon.terminal import launch_terminal

launch_terminal()
```

### 2. `programmatic_game.py` - GameState Manipulation

Shows how to interact with the game state directly without the terminal UI. Demonstrates:

- Creating a new game
- Setting player data
- Creating and adding Pokemon to the party
- Managing the bag (items)
- Moving between locations
- Saving the game

**Use case:** Automation, headless testing, save file manipulation, building alternative UIs.

```python
from pytemon.game_state import GameState

gs = GameState()
gs.start_new_game()
gs.game_data["player"] = {"name": "Red", "money": 3000}
starter = gs.create_pokemon("Charmander", level=5)
gs.game_data["party"] = [starter]
```

### 3. `battle_simulation.py` - Battle Engine

Demonstrates using the battle engine programmatically without the UI. Shows:

- Creating a BattleState
- Executing moves
- Tracking damage and effectiveness
- Battle flow (turn-by-turn)
- Win/lose conditions

**Use case:** Battle simulations, AI training, battle testing, alternative battle interfaces.

```python
from pytemon.engine.battle_engine import BattleState

bs = BattleState(player_mon, opponent_mon, is_trainer_battle=False)
result = bs.execute_move("Thunder Shock", is_player_move=True)
```

## Building Your Own Application

These examples can be used as starting points for:

- **Web interfaces** - Use the GameState as a backend API
- **Discord bots** - Turn battle commands into bot interactions
- **AI experiments** - Train agents to play Pokemon
- **Testing** - Automated game testing without the UI
- **Save editors** - Manipulate save files programmatically
- **Custom UIs** - Build your own interface on top of the game engine

## API Reference

For more details on available classes and methods:

- `pytemon.game_state.GameState` - Central game state manager
- `pytemon.engine.battle_engine.BattleState` - Battle simulation engine
- `pytemon.terminal.PokemonTerminal` - Textual TUI application
- `pytemon.data.pokemon_data.POKEMON` - Pokemon species data
- `pytemon.data.move_data.MOVES` - Move data
- `pytemon.locations` - Location and navigation system
