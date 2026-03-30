---
name: code-style-enforcer
description: Reviews and corrects Python code style in robot-pokemon source and tests. Use when adding new code to ensure it follows PEP 8, uses type hints, has correct docstrings, and matches the project's formatting conventions before running ruff.
---

# code-style-enforcer

Reviews new Python code for style compliance before linting: PEP 8, type hints, docstring format, naming conventions, and import ordering.

## Associated Agent
`ci-quality.agent.md`

## Instructions

### 1. Formatting Rules

- **Line length**: 100 characters max (enforced by `ruff format`)
- **Quotes**: double quotes `"..."` — never single quotes for strings
- **Indent**: 4 spaces — never tabs
- **Blank lines**: 2 blank lines between top-level definitions; 1 between methods

### 2. Type Hints

All function parameters and return types must be annotated:

```python
# ✅ Correct
def enter_bike_shop(game_state: "GameState", output: Any) -> None:

# ✅ Optional parameter
def get_location(name: str) -> Optional["Location"]:

# ❌ Missing annotations
def enter_bike_shop(game_state, output):
```

Use `from __future__ import annotations` or string literals (`"GameState"`) for forward references to avoid circular imports.

Keep `typing` imports for Python 3.8 compatibility — do **not** `pyupgrade` them away:
```python
from typing import Any, Dict, List, Optional  # keep for 3.8 compat
```

### 3. Docstrings (Google style)

```python
def move_to_location(
    game_state: "GameState",
    destination: str,
    output: Any,
    show_arrival_callback: Any,
) -> None:
    """Move the player to a new location.

    Args:
        game_state: Current game state instance.
        destination: Name of the destination location.
        output: RichLog-compatible output writer.
        show_arrival_callback: Called after moving to update the UI.
    """
```

### 4. Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Module | lowercase_underscore | `battle_engine.py` |
| Class | PascalCase | `GameState`, `BattleState` |
| Function / method | lowercase_underscore | `heal_all_pokemon` |
| Constant | UPPER_UNDERSCORE | `SHOP_CATALOG_BASIC` |
| Private method | `_prefix` | `_do_quit_action` |

**Ruff N999 exception**: `pytemon/` package dir is intentionally PascalCase — don't rename it.

### 5. Import Order (isort enforced by ruff)

```python
# 1. Standard library
import json
import os
from pathlib import Path
from typing import Any, Optional

# 2. Third-party
from rich.table import Table
from textual.app import App

# 3. Local
from pytemon.game_state import GameState
from pytemon.data import get_pokemon
```

### 6. Output
- A copy of the code with style fixes applied
- A checklist of what was changed and why

## Dependencies
- `ruff` — formatter and linter (`ruff format`, `ruff check`)
- `pyproject.toml` — ruff configuration

## Error Handling
- **Circular import from type hint**: use `from __future__ import annotations` or string literal
- **Long line that can't be shortened**: wrap function call arguments — ruff format handles this automatically
- **Conflicting sort order**: run `ruff check --fix` to let isort resolve import ordering
