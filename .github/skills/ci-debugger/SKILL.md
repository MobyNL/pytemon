---
name: ci-debugger
description: Diagnoses and fixes failures in the robot-pokemon CI pipeline — pytest errors, import errors, fixture problems, and unexpected test interactions. Use when pytest exits non-zero or tests that previously passed start failing.
---

# ci-debugger

Diagnoses broken CI runs: import errors, unexpected test failures, fixture problems, and environment issues.

## Associated Agent
`test-writer.agent.md`

## Instructions

### 1. Read the Failure Output

```bash
# Reproduce CI failure locally
poetry run pytest tests/ --tb=short -v 2>&1 | head -80

# Short traceback for all failures
poetry run pytest tests/ --tb=short 2>&1 | grep -A 10 "FAILED\|ERROR"

# Single failing test
poetry run pytest tests/test_buildings.py::TestBikeShop::test_gives_bicycle -v --tb=long
```

### 2. Classify the Failure

| Symptom | Likely cause | Fix |
|---|---|---|
| `ImportError` / `ModuleNotFoundError` | New file not in package, circular import, missing `__init__.py` | Add `__init__.py` or fix import order |
| `AttributeError: 'NoneType'` | Fixture returns `None`, or method not setting up state | Check fixture, add `start_new_game()` call |
| `KeyError` in game_data | `start_new_game()` not called on `gs` fixture | Use `gs` fixture from conftest, not bare `GameState()` |
| `AssertionError` with no message | Logic changed, test expectation stale | Update test to match new behaviour or fix the logic |
| `TypeError: X() takes N args` | Function signature changed | Update call sites — use `list_code_usages` to find all |
| Collection error / syntax error | Ruff lint introduced a change that broke syntax | Run `ruff check tests/` to surface it |

### 3. Common Fixes

**Import error from new file:**
```python
# Ensure PokemonLibrary/new_module.py has no circular imports
# Check: does import of new_module trigger an import of terminal.py? (banned — circular)
```

**Fixture state issue:**
```python
# ❌ Using raw GameState without start_new_game
def test_something():
    gs = GameState()
    # gs.game_data is empty / None

# ✅ Use the conftest fixture or call start_new_game
@pytest.fixture
def gs():
    state = GameState()
    state.start_new_game()
    return state
```

**Stale assertion after refactor:**
```python
# Old: function returned a bool
assert can_move_to(gs, "Route 1") is True

# New: function returns (bool, message)
can, _ = can_move_to(gs, "Route 1")
assert can is True
```

### 4. Isolation Strategy

If many tests fail after a single change:
1. `git diff --stat` — identify changed files
2. Run only tests for the changed module: `pytest tests/test_buildings.py -v`
3. Fix that module's tests first before looking at others
4. Confirm the fix doesn't break previously-passing tests: run the full suite

### 5. Output
- Root cause identified
- Fix applied
- Confirmation: `pytest tests/ -q` exits 0

## Examples

**Input:** "After adding `enter_fossil_lab()` to buildings.py, 12 tests fail with ImportError."

**Investigation:** `buildings.py` now imports from `terminal.py` (circular).

**Fix:** Move the shared helper to `game_state.py` or `items.py` — never import from `terminal.py` in library modules.

## Dependencies
- `pytest` with `--tb=short` / `--tb=long`
- `PokemonLibrary/` — source under test
- `tests/conftest.py` — shared fixtures

## Error Handling
- **Flaky test (passes sometimes)**: look for state shared between tests; each test must use fresh fixtures
- **CI passes locally but fails remotely**: check Python version (`pyproject.toml` targets 3.8+); avoid 3.9+ syntax
