# Pokemon Terminal Game - GitHub Copilot Agent

You are an expert Python and Robot Framework developer helping build an interactive Pokemon game using Textual TUI.

## Project Overview

This is a Robot Framework library that provides an interactive terminal-based Pokemon game. It combines:

- **Robot Framework** - Test automation framework used as the game launcher
- **robotframework-pythonlibcore** - For clean library structure with DynamicCore
- **Textual** - Modern Python TUI framework for full-screen terminal interfaces
- **Rich** - For beautiful text formatting and styling

## Technical Stack

### Core Technologies

- **Python 3.8+** - Main programming language
- **Robot Framework 7.0+** - Keyword-driven test automation framework
- **robotframework-pythonlibcore 4.4+** - Base class for creating RF libraries
- **Textual 0.73+** - Terminal User Interface framework
- **Rich 13.7+** - Terminal text formatting

### Project Structure

```
robot-pokemon/
├── .github/
│   └── copilot-instructions.md    # This file
├── PokemonLibrary/
│   ├── __init__.py                # Package initialization
│   ├── library.py                 # Main RF library (DynamicCore)
│   ├── terminal.py                # Textual App — event handlers, compose, command router
│   ├── terminal.tcss              # Textual CSS styles
│   ├── game_state.py              # GameState dataclass + BattleState
│   ├── exploration.py             # look_around, explore_area, encounter triggers
│   ├── buildings.py               # Pokemon Center, Pokemart, houses, Oak's Lab logic
│   ├── locations.py               # Location registry and navigation rules
│   ├── pokedex.py                 # Pokedex display and entry lookup
│   ├── cheat_commands.py          # Dev cheat codes and secret phrases
│   ├── gym_system.py              # Gym leaders and badge logic
│   ├── evolution.py               # Evolution conditions and force_evolve
│   ├── pc_system.py               # Bill's PC storage system
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── panel_mixin.py         # Mixin: all panel show/hide methods
│   │   ├── game_flow_mixin.py     # Mixin: menu, save/load, quit, pending-command dispatch
│   │   ├── building_mixin.py      # Mixin: building entry, shop, exploration delegates
│   │   ├── battle_mixin.py        # Mixin: full battle system + evolution prompting
│   │   ├── displays.py            # show_party, show_bag, show_help, show_status, etc.
│   │   ├── formatters.py          # format_hp_bar and other display helpers
│   │   ├── menus.py               # Menu text builders (show_main_menu text, etc.)
│   │   └── text_animation.py      # Typewriter animation helpers
│   ├── battle/
│   │   ├── battle_ui.py           # Battle display: HP bars, move lists, result text
│   │   └── battle_actions.py      # Battle logic: damage calc, catch math, flee odds
│   ├── engine/
│   │   └── battle_engine.py       # Core battle simulation engine
│   └── data/
│       ├── pokemon_data.py        # POKEMON dict — all species stats
│       ├── move_data.py           # MOVES dict — all move definitions
│       ├── type_chart.py          # Type effectiveness table
│       └── trainer_data.py        # Trainer rosters by location
├── saves/                         # Player save files (JSON)
├── test.robot                     # Robot Framework test/launcher
├── run_terminal.py                # Direct Python launcher
├── run_robot.sh                   # Helper script for running tests
├── pyproject.toml                 # Poetry dependencies
└── README.md
```

## Architecture

### Mixin-Based Terminal Design

`PokemonTerminal` is assembled from four focused Python mixins plus the Textual `App` base:

```python
class PokemonTerminal(PanelMixin, GameFlowMixin, BuildingMixin, BattleMixin, App):
    ...
```

Each mixin owns a logical slice of behaviour. All methods share `self` (which is always a `PokemonTerminal` at runtime), so any mixin method can call `self.query_one(...)`, `self.game_state`, `self.pending_command`, etc.

| Mixin | File | Responsibility |
|---|---|---|
| `PanelMixin` | `ui/panel_mixin.py` | Every `show_*_panel` / `hide_*` method — pure widget manipulation, no game logic |
| `GameFlowMixin` | `ui/game_flow_mixin.py` | Main menu, save/load, quit flow, `handle_pending_command` dispatcher |
| `BuildingMixin` | `ui/building_mixin.py` | Building entry, Pokemart shop loop, exploration delegates, name/starter selection |
| `BattleMixin` | `ui/battle_mixin.py` | Wild/trainer/gym encounters, move execution, flee, catch, switch, victory, evolution |

**What stays in `terminal.py`:**
- `compose()` — full Textual widget tree
- `on_mount()` — startup
- `on_button_pressed()` — routes button clicks to the right mixin method
- `on_input_submitted()` — routes typed commands to `process_command` or `handle_pending_command`
- `process_command()` — in-game command dispatcher (movement, party, bag, pokedex, settings, …)
- Thin display delegates (`show_party`, `show_bag`, `show_pokedex`, …) that call `ui/displays.py`
- `action_quit`, `action_help`, `launch_terminal()`

### State Management

All mutable game state lives in `GameState` (`game_state.py`). The terminal holds a single instance at `self.game_state`. Key fields:

- `game_state.in_menu` / `in_game` — determines whether typed input goes to menu or game
- `game_state.battle_state` — `BattleState` instance while a battle is active, `None` otherwise
- `self.pending_command` — string token naming the current multi-step interaction (e.g. `"move_to"`, `"battle"`, `"save_name"`)
- `self.pending_command_data` — `dict` of extra context for the pending flow

### `pending_command` State Machine

Multi-step interactions (location pick, save name, heal confirmation, …) work by:

1. Setting `self.pending_command = "<token>"` and optionally populating `self.pending_command_data`
2. Showing the relevant panel or prompting via the output log
3. The next `on_input_submitted` or button press calls `self.handle_pending_command(value, output)`
4. `handle_pending_command` (in `GameFlowMixin`) dispatches on the token and clears state when done

**Never** clear `self.pending_command` from inside an event handler — call `handle_pending_command` and let it manage state.

## Coding Standards

### Python Code Style

1. **Follow PEP 8** - Standard Python style guide
2. **Type hints** - Use type annotations for function parameters and returns
3. **Docstrings** - Use Google-style docstrings for all classes and methods
4. **F-strings** - Prefer f-strings over .format() or % formatting
5. **Pathlib** - Use pathlib.Path instead of os.path

Example:

```python
from pathlib import Path
from typing import Optional

def load_pokemon_data(data_file: Path) -> Optional[dict]:
    """
    Load Pokemon data from a JSON file.

    Args:
        data_file: Path to the Pokemon data file

    Returns:
        Dictionary containing Pokemon data, or None if file not found
    """
    if not data_file.exists():
        return None
    return json.loads(data_file.read_text())
```

### Robot Framework Library Standards

1. **Use robotframework-pythonlibcore** - Inherit from DynamicCore
2. **@keyword decorator** - Explicitly decorate all RF keywords
3. **ROBOT_LIBRARY_SCOPE** - Set to 'SUITE' for state persistence
4. **Comprehensive docstrings** - Include Robot Framework examples

Example:

```python
from robotlibcore import DynamicCore
from robot.api.deco import keyword
from robot.api import logger

class PokemonLibrary(DynamicCore):
    """Pokemon Robot Framework Library"""

    ROBOT_LIBRARY_SCOPE = 'SUITE'
    ROBOT_LIBRARY_VERSION = '0.1.0'

    def __init__(self):
        DynamicCore.__init__(self, [])
        logger.info("PokemonLibrary initialized")

    @keyword("Start Interactive Terminal")
    def start_interactive_terminal(self):
        """
        Start the interactive Pokemon terminal.

        Example:
        | Start Interactive Terminal |
        """
        # Implementation
```

### Textual TUI Best Practices

1. **CSS Styling** - Use Textual's CSS for widget styling
2. **Reactive Properties** - Use reactive variables for dynamic updates
3. **Widget Composition** - Break UI into small, reusable widgets
4. **Message Handling** - Use Textual's message system for events
5. **Bindings** - Define keyboard shortcuts for better UX

Example:

```python
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, RichLog
from textual.binding import Binding
from textual.reactive import reactive

class PokemonTerminal(App):
    """Pokemon terminal application."""

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        ("q", "quit", "Quit"),
        ("h", "help", "Help"),
    ]

    CSS = """
    RichLog {
        border: solid $primary;
        height: 1fr;
    }
    """

    command_count = reactive(0)

    def compose(self) -> ComposeResult:
        yield Header()
        yield RichLog(id="output")
        yield Input(placeholder="Command...")
        yield Footer()
```

## Domain Knowledge

### Pokemon Game Concepts

When implementing Pokemon features, follow these conventions:

1. **Pokemon Data Structure**

   ```python
   {
       "name": "Pikachu",
       "number": 25,
       "types": ["Electric"],
       "level": 5,
       "hp": 35,
       "moves": ["Thunder Shock", "Growl"]
   }
   ```

2. **Game States**
   - INITIAL - No game loaded
   - EXPLORING - Walking around
   - IN_BATTLE - Fighting wild Pokemon
   - IN_MENU - Viewing menus

3. **Locations**
   - Pallet Town (starting location)
   - Routes (1-25)
   - Cities (Viridian, Pewter, Cerulean, etc.)

### Robot Framework Keywords

Keywords should be:

- **Action-oriented** - "Start New Game", "Choose Starter", "Walk To Route"
- **Clear and descriptive** - Self-documenting
- **Properly scoped** - Use SUITE scope for stateful libraries

Example Robot Framework test:

```robot
*** Settings ***
Library    PokemonLibrary

*** Test Cases ***
Play Pokemon Game
    Start Interactive Terminal
    # Terminal runs interactively
```

## Implementation Guidelines

### Where to Add New Code

Before writing anything, pick the right file:

| What you're adding | Where it goes |
|---|---|
| New in-game typed command | `terminal.py` → `process_command()` |
| New UI panel (show/hide) | `ui/panel_mixin.py` |
| New save/load/quit flow | `ui/game_flow_mixin.py` |
| New building or shop | `ui/building_mixin.py` |
| New battle mechanic | `ui/battle_mixin.py` |
| New display (party, bag, …) | `ui/displays.py` + thin delegate in `terminal.py` |
| New Pokemon/move data | `data/pokemon_data.py` or `data/move_data.py` |
| New location | `locations.py` |
| New gym leader | `gym_system.py` + `data/trainer_data.py` |
| New pending-command flow | Set `self.pending_command` token, handle in `GameFlowMixin.handle_pending_command` |

### Adding New Terminal Commands

When adding a simple in-game command:

1. Add an `elif` branch in `process_command()` in `terminal.py`
2. Call out to a module function or mixin method — **do not inline complex logic**
3. Provide rich formatted output
4. Always end complex output blocks with `output.write("")` for spacing

Example (simple, self-contained):

```python
elif cmd in ("run", "run away"):
    output.write("")
    output.write("[yellow]🏃 You ran away safely![/yellow]")
    output.write("")
```

Example (delegates to a module):

```python
elif cmd.startswith("fish"):
    from . import fishing
    fishing.start_fishing(self.game_state, output)
```

### Adding a New Multi-Step Flow

For interactions that need multiple inputs (e.g. a "nickname your Pokemon" flow):

1. Create a `show_nickname_panel()` method in `PanelMixin` that makes the panel visible
2. Set `self.pending_command = "nickname"` and `self.pending_command_data['target'] = pokemon`
3. Add a handler branch in `GameFlowMixin.handle_pending_command`:

```python
elif self.pending_command == "nickname":
    pokemon = self.pending_command_data.get('target')
    pokemon['nickname'] = command.strip()
    self.pending_command = None
    self.pending_command_data = {}
    output.write(f"[green]✓ Nicknamed {pokemon['name']} '{pokemon['nickname']}'![/green]")
```

4. Wire up any buttons to call `self.handle_pending_command(value, output)`

### Adding New RF Keywords

When adding Robot Framework keywords:

1. Use the `@keyword` decorator
2. Provide detailed docstrings with examples
3. Log important actions
4. Handle exceptions appropriately

Example:

```python
@keyword("Choose Starter Pokemon")
def choose_starter_pokemon(self, pokemon_name: str):
    """
    Choose your starter Pokemon.

    Arguments:
    - ``pokemon_name``: Name of starter (Bulbasaur, Charmander, Squirtle)

    Example:
    | Choose Starter Pokemon | Charmander |
    """
    logger.info(f"Choosing starter: {pokemon_name}")
    # Implementation
```

### Error Handling

Always provide helpful error messages:

```python
if pokemon_name not in ["Bulbasaur", "Charmander", "Squirtle"]:
    raise ValueError(
        f"Invalid starter: {pokemon_name}. "
        f"Must be Bulbasaur, Charmander, or Squirtle"
    )
```

### ⚠️ CRITICAL: Rich Text Object Handling

**ALWAYS check and convert Rich `Text` objects to strings** when extracting values from Textual widgets!

Common issue: Button labels, widget labels, and other text properties in Textual return `Text` objects (from Rich library), NOT plain strings.

```python
# ❌ WRONG - Will cause AttributeError when calling .lower(), .strip(), etc.
location_name = button.label
destination_lower = location_name.lower()  # ERROR: 'Text' object has no attribute 'lower'

# ✅ CORRECT - Always convert to string first
location_name = str(button.label)
destination_lower = location_name.lower()  # Works!
```

**When to convert:**
- Button labels: `str(button.label)`
- Static text: `str(static.renderable)`
- Any widget property that returns formatted text
- Before passing values to functions expecting strings
- Before string operations (`.lower()`, `.strip()`, `.split()`, etc.)

**Practice:** Whenever you access `.label` or text properties from Textual widgets, wrap in `str()` if you need to:
- Pass to another function
- Perform string operations
- Compare with strings
- Store as game state

```python
# Good patterns
location = str(button.label)
building = str(event.button.label)
choice = str(widget.renderable)

# Then safe to use
if location.lower() in available_locations:
    move_to(location)
```

## Rich Text Formatting

Use Rich markup for beautiful terminal output:

```python
# Colors
output.write("[red]Error message[/red]")
output.write("[green]Success message[/green]")
output.write("[yellow]Warning message[/yellow]")
output.write("[cyan]Info message[/cyan]")

# Styles
output.write("[bold]Bold text[/bold]")
output.write("[italic]Italic text[/italic]")
output.write("[dim]Dimmed text[/dim]")

# Combinations
output.write("[bold green]✓ Success![/bold green]")
output.write("[bold red]✗ Failed![/bold red]")

# Emojis for better UX
output.write("🎮 Game started")
output.write("⚔️ Battle initiated")
output.write("👾 Wild Pokemon appeared")
output.write("🏆 Victory!")
```

## Testing, Coverage & Code Quality

### CI Pipeline

The CI runs on every push and PR (`.github/workflows/ci.yml`). All steps except mypy and the source lint are **hard failures** — they must pass:

| Step | Command | Hard fail? |
|---|---|---|
| Format check | `ruff format --check PokemonLibrary/ tests/` | ✅ Yes |
| Lint tests | `ruff check tests/` | ✅ Yes |
| Lint source | `ruff check PokemonLibrary/` | ⚠️ Informational only |
| Type check | `mypy PokemonLibrary/` | ⚠️ Informational only |
| Unit tests + coverage | `pytest tests/ --tb=short -v --cov=PokemonLibrary --cov-report=term-missing` | ✅ Yes |

### Running Tests Locally

```bash
# Full test suite with coverage (matches CI exactly)
poetry run pytest tests/ --tb=short -v --cov=PokemonLibrary --cov-report=term-missing

# Quick run (no coverage)
poetry run pytest tests/ -q

# Single file
poetry run pytest tests/test_battle_engine.py -v

# Single test
poetry run pytest tests/test_battle_engine.py::TestAttemptCatch::test_master_ball_always_catches -v
```

### Ruff — Formatting & Linting

Config lives in `pyproject.toml` under `[tool.ruff]`. Key settings:

- **Line length**: 100 characters
- **Target**: Python 3.8+
- **Quote style**: double quotes
- **Indent**: spaces

**Enabled rule sets**: `E/W` (pycodestyle), `F` (pyflakes), `I` (isort), `B` (bugbear), `UP` (pyupgrade), `N` (pep8-naming), `C4` (comprehensions), `RUF` (ruff-specific)

**Ignored rules** (intentional):
- `E501` — line length enforced by formatter, not linter
- `UP006/UP007/UP035/UP045` — `typing` imports kept for Python 3.8 compat
- `RUF012` — mutable class attributes are normal in game code
- `N999` — `PokemonLibrary` uses PascalCase intentionally

```bash
# Check formatting
ruff format --check PokemonLibrary/ tests/

# Apply formatting
ruff format PokemonLibrary/ tests/

# Lint tests (must pass clean)
ruff check tests/

# Lint + auto-fix tests
ruff check tests/ --fix

# Lint source (informational)
ruff check PokemonLibrary/
```

### Common Lint Pitfalls to Avoid

When writing test code, these patterns cause CI failures:

```python
# ❌ F841 — unused variable (remove assignment, or prefix with _)
bs = setup_wild_battle(gs)          # if bs is never used after

# ✅ Fix: drop the assignment
setup_wild_battle(gs)

# ❌ RUF059 — unused unpacked variable
caught, shakes, messages = bs.attempt_catch("Pokeball")  # if messages unused

# ✅ Fix: use _ for unused slots
caught, shakes, _ = bs.attempt_catch("Pokeball")

# ❌ RUF003 — EN DASH in comments (common from copy-paste)
# GameState – find_pokemon

# ✅ Fix: use plain hyphen
# GameState - find_pokemon

# ❌ F401 — unused import
import json   # if never used in the file

# ❌ I001 — unsorted imports (isort ordering required)
import sys
import os     # 'os' should come before 'sys'
```

### Coverage

Coverage is collected automatically by `pytest --cov=PokemonLibrary`. Config is in `pyproject.toml` under `[tool.coverage]`.

**Excluded from coverage** (TUI/launcher code that can't be unit-tested without a display):
- `PokemonLibrary/terminal.py`
- `PokemonLibrary/library.py`
- `PokemonLibrary/ui/text_animation.py`

**When adding new source files:** aim for high coverage. Every non-trivial function should have a corresponding test in `tests/`. Mirror the source structure — `PokemonLibrary/foo.py` → `tests/test_foo.py`.

### Test Conventions

Tests live in `tests/` and use `pytest`. Key patterns from the codebase:

```python
# Use conftest.py fixtures — don't recreate GameState from scratch
@pytest.fixture
def gs():
    state = GameState()
    state.start_new_game()
    return state

# Use a MockRichLog instead of real Textual widgets
class MockRichLog:
    def __init__(self):
        self.lines: list[str] = []
    def write(self, text: str) -> None:
        self.lines.append(text)
    @property
    def combined(self) -> str:
        return "\n".join(str(l) for l in self.lines)

# Use _ for unpacked return values you don't need
can, _ = can_challenge_gym(gs, "Pewter City")

# Don't assign return values you never read
setup_wild_battle(gs)       # not: bs = setup_wild_battle(gs)

# Import inside test methods for heavy/optional modules (keeps startup fast)
def test_something(self):
    from PokemonLibrary.engine import BattleState
    ...
```

### Running the Robot Framework Launcher

```bash
# Run the game via Robot Framework
poetry run robot test.robot

# Or with the helper script
./run_robot.sh test.robot

# Direct Python launcher (for debugging TUI)
poetry run python run_terminal.py
```

## Common Patterns

### GameState is the Single Source of Truth

All mutable game data lives in `self.game_state` (a `GameState` instance). Never store game data as instance attributes on `PokemonTerminal` or any mixin — put it in `GameState` instead.

```python
# ✅ Correct — read/write via game_state
self.game_state.game_data['player']['name'] = "Ash"
location = self.game_state.location

# ❌ Wrong — bypasses GameState
self.player_name = "Ash"
```

### Command Registry

```python
COMMANDS = {
    "help": "Show available commands",
    "status": "Show game status",
    "move": "Move to a location",
    # etc.
}
```

### Reactive Updates

```python
class PokemonTerminal(App):
    player_location = reactive("Pallet Town")

    def watch_player_location(self, new_location: str) -> None:
        """Called when location changes."""
        self.sub_title = f"Location: {new_location}"
```

## When Suggesting Code

### Always Consider:

1. **Textual best practices** - Use widgets, CSS, and reactive properties
2. **RF library conventions** - Use @keyword, proper docstrings
3. **Rich formatting** - Make terminal output beautiful
4. **Error handling** - Provide helpful error messages
5. **State management** - Track game state properly

### Prefer:

- Adding logic to the appropriate mixin rather than growing `terminal.py`
- Calling module-level functions from mixins (keeps mixins thin)
- Clear, descriptive names for `pending_command` tokens (e.g. `"heal_confirm"` not `"hc"`)
- Small, focused functions
- Type hints for clarity
- Comprehensive docstrings

### Avoid:

- Adding methods to `terminal.py` that belong in a mixin
- Inlining game logic into `on_button_pressed` — route to a mixin method instead
- Directly calling `self.exit()` outside of `GameFlowMixin._do_quit_action`
- Global mutable state (all state goes in `GameState`)
- Blocking operations in Textual (use async or `asyncio.sleep`)
- Hardcoded values (use constants in `data/` modules)
- Silent failures (always log/report errors)
- **🚨 CRITICAL: Using button.label or widget text without str() conversion** — This is the most common bug! Always use `str(button.label)` before calling `.lower()`, `.strip()`, or passing to functions. Button labels return Rich `Text` objects, not strings!
- Assuming widget properties return plain strings (they often return Rich Text objects)
- Importing `terminal` from any mixin or `ui/` module (circular import!)

## Quick Reference

### Import Statements

```python
# Robot Framework
from robotlibcore import DynamicCore
from robot.api.deco import keyword
from robot.api import logger

# Textual
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, RichLog, Static
from textual.containers import Container, Vertical, Horizontal
from textual.binding import Binding
from textual.reactive import reactive

# Rich (for formatting)
from rich.text import Text
from rich.panel import Panel
from rich.table import Table

# Standard library
from pathlib import Path
from typing import Optional, Dict, List, Any
import json
```

### Useful Textual Patterns

```python
# Query widgets
output = self.query_one("#output", RichLog)
input_field = self.query_one("#command-input", Input)

# Write to log
output.write("[green]Success![/green]")

# Focus widget
self.query_one(Input).focus()

# Exit app
self.exit()
```

## Remember

This is an **April Fools project** - a "test framework" that's actually a fun Pokemon game! The humor comes from QA engineers expecting to run tests but getting an interactive game instead. Keep the implementation professional and well-structured, but remember the playful nature of the project.

Happy coding! 🎮🐍
