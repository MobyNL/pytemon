---
name: lint-fixer
description: Fixes ruff lint violations in robot-pokemon source and test code. Use when ruff check reports errors — covers every rule that causes CI failures with exact fix patterns for each.
---

# lint-fixer

Fixes every ruff lint violation that causes CI failures. Reference this skill before committing any code change.

## Associated Agent
`ci-quality.agent.md`

## Instructions

### 1. Run Lint

```bash
# Hard-fail checks (must be clean)
ruff check tests/
ruff format --check pytemon/ tests/

# Informational
ruff check pytemon/

# Auto-fix what ruff can fix automatically
ruff format pytemon/ tests/
ruff check tests/ --fix
ruff check pytemon/ --fix
```

### 2. Fix Patterns for Every Common Violation

**F841 — Local variable assigned but never used**
```python
# ❌ result = some_function()  ← result never read
# ✅ some_function()           ← drop the assignment
```

**RUF059 — Unused unpacked variable**
```python
# ❌ caught, shakes, messages = attempt_catch("Pokeball")  ← messages unused
# ✅ caught, shakes, _ = attempt_catch("Pokeball")
```

**RUF003 — EN DASH (`–`) in comment**
```python
# ❌ # GameState – find pokemon
# ✅ # GameState - find pokemon
```

**F401 — Unused import**
```python
# ❌ import json   ← never used in this file
# ✅ (remove the line entirely)
```

**I001 — Unsorted imports**
```python
# ❌ import sys; import os     (os must come before sys)
# ✅ import os; import sys
# Run: ruff check --fix to let isort handle this automatically
```

**B007 — Loop variable unused in loop body**
```python
# ❌ for i in range(5): do_thing()
# ✅ for _ in range(5): do_thing()
```

**E711 — Comparison to None**
```python
# ❌ if x == None:
# ✅ if x is None:
```

**E712 — Comparison to True/False**
```python
# ❌ if flag == True:
# ✅ if flag:
```

**W291/W293 — Trailing whitespace**
```python
# Run: ruff format — it removes trailing whitespace automatically
```

**B006 — Mutable default argument**
```python
# ❌ def foo(items=[]):
# ✅ def foo(items=None):
#        if items is None: items = []
```

### 3. Rules That Are Intentionally Ignored (do NOT fix)

- `E501` — line length (formatter handles)
- `RUF012` — mutable class variables (normal in game code)
- `N999` — PascalCase `PokemonLibrary` module name
- `UP006/UP007/UP035/UP045` — `typing` imports kept for Python 3.8 compat
- `B008` — function calls in default args

### 4. Output
- Fixed code with inline comments explaining each change
- Confirmation that `ruff check tests/` and `ruff format --check` pass

## Examples

**Input:** "ruff check tests/ reports: F841, RUF059, I001 in test_buildings.py"

**Fix:**
```python
# F841: drop unused variable
enter_bike_shop(gs, output)   # was: result = enter_bike_shop(...)

# RUF059: use _ for unused slot
caught, _ = attempt_catch(...)   # was: caught, msg = attempt_catch(...)

# I001: run `ruff check tests/test_buildings.py --fix` to sort imports automatically
```

## Dependencies
- `ruff` installed via `poetry` (`pyproject.toml`)
- `pyproject.toml` — `[tool.ruff]` configuration

## Error Handling
- **Auto-fix breaks logic**: review `git diff` after `--fix`; some fixes (like removing imports) may need manual verification
- **New rule fires after ruff upgrade**: check if it's in the intentionally-ignored list before fixing
