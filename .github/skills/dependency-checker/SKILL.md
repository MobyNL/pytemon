---
name: dependency-checker
description: Audits and updates robot-pokemon Python dependencies in pyproject.toml. Use when adding a new package, resolving version conflicts, checking if a library is available, or verifying the Poetry lock file is consistent.
---

# dependency-checker

Manages Python dependencies in `pyproject.toml` — checking availability, adding packages, and resolving conflicts.

## Associated Agent
`ci-quality.agent.md`

## Instructions

### 1. Current Dependency Stack

Core runtime dependencies (from `pyproject.toml`):
```toml
[tool.poetry.dependencies]
python = "^3.8"
robotframework = "^7.0"
robotframework-pythonlibcore = "^4.4"
textual = "^0.73"
rich = "^13.7"
```

Dev/test dependencies:
```toml
[tool.poetry.dev-dependencies]
pytest = "*"
pytest-cov = "*"
ruff = "*"
mypy = "*"
```

### 2. Checking if a Package Is Available

```bash
# Check what's installed
poetry run pip show <package-name>

# Check if importable in current env
poetry run python -c "import <package>; print(<package>.__version__)"
```

### 3. Adding a New Dependency

```bash
# Runtime dependency
poetry add <package>

# Dev-only dependency
poetry add --dev <package>

# With version constraint
poetry add "textual>=0.73,<1.0"
```

Then verify:
```bash
poetry lock --no-update   # update lock without upgrading everything
poetry install
poetry run pytest tests/ -q   # confirm nothing broke
```

### 4. Checking for Version Conflicts

```bash
# Show dependency tree
poetry show --tree

# Check for conflicts
poetry check
```

### 5. Python Version Compatibility

All code must run on **Python 3.8+** (the minimum declared in `pyproject.toml`). Avoid:
- `match`/`case` statements (3.10+)
- `X | Y` union type hints in function signatures (3.10+) — use `Optional[X]` or string literals
- `dict | dict` merging with `|` (3.9+) — use `{**a, **b}`
- f-string `=` debugging (`f"{x=}"`) (3.8 is fine, but `f"x={x}"` is more compatible)

```python
# ❌ 3.10+ only
def foo(x: int | str) -> None: ...

# ✅ 3.8 compatible
def foo(x: Union[int, str]) -> None: ...
# or
def foo(x: "int | str") -> None: ...   # string literal defers evaluation
```

### 6. Output
- Confirmation the requested package is available or instructions to add it
- Updated `pyproject.toml` snippet if adding a new dependency
- Confirmation that `poetry check` and `pytest tests/ -q` pass after the change

## Examples

**Input:** "Do we have `pytest-asyncio`? Integration tests might need it."

**Check:**
```bash
poetry run pip show pytest-asyncio
```
If missing:
```bash
poetry add --dev pytest-asyncio
```
Then confirm tests still pass.

## Dependencies
- `poetry` — package manager
- `pyproject.toml` — dependency declarations and tool config
- `poetry.lock` — pinned versions

## Error Handling
- **`poetry lock` fails**: run `poetry lock --no-update` first; if still failing, check for yanked versions
- **Import error after `poetry add`**: run `poetry install` to actually install into the venv
- **3.8 compat break**: run `mypy --python-version 3.8 pytemon/` to surface version-specific type errors
