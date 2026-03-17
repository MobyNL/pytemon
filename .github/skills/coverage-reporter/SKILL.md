---
name: coverage-reporter
description: Generates and interprets pytest coverage reports for robot-pokemon. Use when you need to know the current coverage state, identify which files are below the 80% threshold, or produce a coverage summary before a PR.
---

# coverage-reporter

Runs coverage measurements, reads reports, and produces a human-friendly summary of what's covered and what isn't.

## Associated Agent
`ci-quality.agent.md`

## Instructions

### 1. Quick Coverage Check

```bash
# Full report (matches CI exactly)
poetry run pytest tests/ -q --cov=PokemonLibrary --cov-report=term-missing 2>&1

# Files below 80% only
poetry run pytest tests/ -q --cov=PokemonLibrary --cov-report=term-missing 2>&1 \
  | awk 'NR==1 || /^PokemonLibrary/' \
  | awk '$4+0 < 80 && $4 ~ /%/'
```

### 2. Excluded Files (configured in `pyproject.toml`)

These are intentionally excluded and will not appear in the report:
- `PokemonLibrary/terminal.py`
- `PokemonLibrary/library.py`
- `PokemonLibrary/ui/text_animation.py`

Do not add tests targeting these files for coverage purposes.

### 3. Interpreting the Report

```
Name                                      Stmts   Miss  Cover   Missing
------------------------------------------------------------------------
PokemonLibrary/buildings.py                  87     14    84%   45-52, 88
PokemonLibrary/exploration.py               120     38    68%   34, 67-89
PokemonLibrary/items.py                      65      8    88%   78-85
------------------------------------------------------------------------
TOTAL                                       850    102    88%
```

| Column | Meaning |
|---|---|
| Stmts | Total executable statements in file |
| Miss | Statements not executed by any test |
| Cover | % of statements executed |
| Missing | Line numbers not covered |

### 4. Coverage Configuration (`pyproject.toml`)

```toml
[tool.coverage.run]
source = ["PokemonLibrary"]
omit = [
    "PokemonLibrary/terminal.py",
    "PokemonLibrary/library.py",
    "PokemonLibrary/ui/text_animation.py",
]

[tool.coverage.report]
fail_under = 80
show_missing = true
```

### 5. Output

Produce a table like:

```
File                          Current%  Target%  Gap  Priority
------------------------------------------------------------
exploration.py                   68%      80%    12%  HIGH
buildings.py                     84%      80%     -    OK
items.py                         88%      80%     -    OK
TOTAL                            82%      80%     -    OK
```

Then list the MISS lines per below-target file and map them to branch types (see test-coverage-analyzer skill for branch mapping).

## Examples

**Command to get just the TOTAL line:**
```bash
poetry run pytest tests/ -q --cov=PokemonLibrary --cov-report=term-missing 2>&1 | grep TOTAL
```

**Expected output when CI will pass:**
```
TOTAL    850    95    89%
```

## Dependencies
- `pytest-cov` — coverage plugin
- `pyproject.toml` — `[tool.coverage]` configuration
- `tests/` — test suite

## Error Handling
- **Coverage below 80% despite new tests**: confirm new test file is named `test_*.py` and is in `tests/`
- **TOTAL drops unexpectedly**: a new source file was added; check `git diff --name-only` and add tests for it
- **Missing lines don't match code**: coverage can be stale — always run fresh with `--cov` rather than reading a cached `.coverage` file
