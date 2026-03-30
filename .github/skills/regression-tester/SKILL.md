---
name: regression-tester
description: Verifies that existing robot-pokemon tests still pass after a change, identifies tests broken by refactoring, and ensures no previously-passing test suite turns red. Use before committing any refactor or cross-module change.
---

# regression-tester

Runs the full test suite, identifies newly broken tests, and confirms no regression has been introduced by a change.

## Associated Agent
`test-writer.agent.md`

## Instructions

### 1. Pre-Commit Regression Check

```bash
# Run the full suite quickly
poetry run pytest tests/ -q 2>&1 | tail -5

# Run with failure detail only
poetry run pytest tests/ --tb=short -q 2>&1 | grep -E "FAILED|ERROR|passed|failed"

# Compare against a baseline (before your change)
git stash
poetry run pytest tests/ -q 2>&1 | tail -3  # baseline
git stash pop
poetry run pytest tests/ -q 2>&1 | tail -3  # after change
```

### 2. Scope Regression by Changed Files

```bash
# Find tests related to a changed file
git diff --name-only | sed 's|pytemon/||; s|\.py||; s|^|tests/test_|; s|$|.py|'

# Run only those tests
poetry run pytest tests/test_buildings.py tests/test_exploration.py -v
```

### 3. Classifying Regressions

| Type | Description | Action |
|---|---|---|
| **Expected break** | Test was testing old behaviour that intentionally changed | Update test expectation |
| **Accidental break** | Refactor broke a side effect or assumption | Fix the code, not the test |
| **Fixture break** | `conftest.py` change affects multiple tests | Restore conftest compatibility |
| **Import error** | Circular import introduced by change | Reorganise imports |

### 4. Updating Broken Tests After Intentional Change

```python
# Old behaviour: function returned bool
assert move_to_location(gs, "Route 1", output, cb) is True

# New behaviour: function returns None (side effect only)
move_to_location(gs, "Route 1", output, cb)
assert gs.current_location == "Route 1"   # check side effect instead
```

**Do NOT change test expectations just to make tests pass if the behaviour is wrong — fix the code.**

### 5. Isolation Run for Confirming a Fix

```bash
# After a fix, run the previously failing tests first
poetry run pytest tests/test_buildings.py::TestBikeShop -v

# Then confirm no collateral damage
poetry run pytest tests/ -q
```

### 6. Output
- List of tests that were passing before and are now failing (regression set)
- For each: classify as expected or accidental
- Confirmation: `pytest tests/ -q` exits 0 with same or more passed tests than before

## Examples

**Input:** "After refactoring `exploration.py` to return `(bool, message)` instead of `bool`, 8 tests fail."

**Investigation:**
- All 8 tests call `move_to_location` and check its return value as a bool
- This is an **expected break** — update assertions to check `gs.current_location` instead

**Fix pattern:**
```python
# Before:
assert move_to_location(gs, "Route 1", output, cb)

# After:
move_to_location(gs, "Route 1", output, cb)
assert gs.current_location == "Route 1"
```

## Dependencies
- `pytest` — test runner
- `git diff` — identify changed files
- `tests/` — full test suite

## Error Handling
- **Too many failures to track**: run `pytest tests/ -q --tb=no` first to get a count; fix in waves by file
- **Intermittent failures**: add `--count=3` (pytest-repeat) to confirm flakiness before investigating
- **CI red but local green**: check Python version and platform differences; avoid f-strings with `=` (3.8 compat)
