---
name: test-case-generator
description: Generates pytest test cases for new or modified robot-pokemon code. Use when a new feature, function, or module needs test coverage — produces correctly structured test classes with fixtures, assertions, and lint-clean code.
---

# test-case-generator

Generates complete, CI-passing pytest test files for new robot-pokemon features.

## Associated Agent
`test-writer.agent.md`

## Instructions

### 1. Input
- **File(s) to test** — e.g. `PokemonLibrary/buildings.py`
- **Functions/classes** — which functions need coverage
- **Current coverage** — run `pytest --cov-report=term-missing` and paste the MISS lines
- **Fixtures needed** — `gs` (GameState), `output` (MockRichLog), or custom

### 2. File Naming and Structure

```
PokemonLibrary/buildings.py  →  tests/test_buildings.py
PokemonLibrary/ui/battle_mixin.py  →  tests/test_battle_mixin.py
```

```python
# tests/test_buildings.py
import pytest
from PokemonLibrary.buildings import enter_bike_shop, heal_all_pokemon
from tests.conftest import MockRichLog   # or define inline if not in conftest


class TestBikeShop:
    def test_gives_bicycle_on_first_visit(self, gs, output):
        enter_bike_shop(gs, output)
        assert gs.game_data["bag"].get("Bicycle") == 1
        assert gs.game_data["story_flags"].get("received_bicycle") is True

    def test_no_duplicate_bicycle_on_repeat(self, gs, output):
        enter_bike_shop(gs, output)
        enter_bike_shop(gs, output)
        assert gs.game_data["bag"].get("Bicycle") == 1   # still 1, not 2

    def test_repeat_visit_message(self, gs, output):
        enter_bike_shop(gs, output)
        output.lines.clear()
        enter_bike_shop(gs, output)
        assert any("already" in str(l).lower() or "enjoying" in str(l).lower()
                   for l in output.lines)
```

### 3. Coverage-Guided Test Writing

From `--cov-report=term-missing` output:
```
buildings.py    72%   MISS 45-52, 88, 101-110
```
Map line numbers back to uncovered branches:
- Lines 45-52 → missing `else` branch of a condition → add a test hitting that branch
- Line 88 → error path → add a test with invalid input
- Lines 101-110 → repeat-visit block → add a "second call" test

### 4. Lint Rules to Follow in Test Code

```python
# ❌ F841 — unused variable
result = some_function()    # result never used after

# ✅
some_function()

# ❌ RUF059 — unused unpacked slot
caught, shakes, messages = attempt_catch(...)   # messages unused

# ✅
caught, shakes, _ = attempt_catch(...)

# ❌ I001 — unsorted imports
import pytest
import os      # os should come before pytest

# ✅
import os
import pytest
```

### 5. Output
- Complete test file or test class, ready to paste into `tests/`
- Coverage statement ("these tests should bring coverage from X% to Y%")

## Examples

**Input:** "Generate tests for `exploration.py` `move_to_location` — currently at 62% coverage."

**Output skeleton:**
```python
class TestMoveToLocation:
    def test_valid_move_succeeds(self, gs, output):
        # arrange: player at Pallet Town which connects to Route 1
        assert gs.current_location == "Pallet Town"
        move_to_location(gs, "Route 1", output, lambda: None)
        assert gs.current_location == "Route 1"

    def test_invalid_destination_shows_error(self, gs, output):
        move_to_location(gs, "Nowhere", output, lambda: None)
        assert any("can't" in str(l).lower() or "not" in str(l).lower() for l in output.lines)

    def test_blocked_exit_respects_badge_gate(self, gs, output):
        gs.current_location = "Cerulean City"
        move_to_location(gs, "Route 24", output, lambda: None)
        assert gs.current_location == "Cerulean City"   # didn't move
```

## Dependencies
- `tests/conftest.py` — `gs` and `output` fixtures, `MockRichLog`
- `pytest` — test runner
- `PokemonLibrary/` — modules under test

## Error Handling
- **Test imports fail**: check for a circular import or missing `__init__.py` in `tests/`
- **Fixture not found**: confirm fixtures are defined in `conftest.py` or the test file itself
- **Coverage not improving**: re-run with `--cov-report=term-missing` and check if new tests hit the MISS lines
