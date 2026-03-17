---
name: test-coverage-analyzer
description: Analyses pytest coverage reports for robot-pokemon and identifies which lines, branches, and files need more tests. Use when overall coverage drops below 80%, when a new file needs coverage, or before a PR to verify targets are met.
---

# test-coverage-analyzer

Reads coverage reports, maps uncovered lines to code branches, and produces a prioritised list of gaps to fill.

## Associated Agent
`test-writer.agent.md`

## Instructions

### 1. Run Coverage

```bash
# Full report with missing lines
poetry run pytest tests/ -q --cov=PokemonLibrary --cov-report=term-missing 2>&1 | tee coverage.txt

# Single file focus
poetry run pytest tests/ -q --cov=PokemonLibrary --cov-report=term-missing 2>&1 | grep "buildings\|exploration\|items"
```

### 2. Reading the Report

```
Name                                Stmts   Miss  Cover   Missing
-----------------------------------------------------------------
PokemonLibrary/buildings.py            87     14    84%   45-52, 88, 101-110
PokemonLibrary/exploration.py         120     38    68%   34, 67-89, 112-140
PokemonLibrary/items.py                65      8    88%   78-85
```

- **Cover < 80%** = must add tests (hard CI requirement)
- **Miss lines** = specific uncovered statements

### 3. Excluded Files (do NOT add to coverage target)

```
PokemonLibrary/terminal.py
PokemonLibrary/library.py
PokemonLibrary/ui/text_animation.py
```

### 4. Mapping Missing Lines to Branches

Open the file and read the MISS line numbers. Common patterns:

| MISS pattern | Likely cause | Test to add |
|---|---|---|
| Single line (88) | Error/edge branch | Test with invalid/boundary input |
| Contiguous block (45-52) | Else/elif branch | Test that takes the other path |
| End of function (101-110) | Repeat-visit or fallback | Second-call test, or `if not flag` path |
| Exception handler | Exception never raised | Test with malformed data |

### 5. Priority Order

1. Files below 80% (CI failure risk) — fix immediately
2. Files between 80-85% — opportunistic improvement
3. Files above 90% — only add tests when touching the file anyway

### 6. Output
Produce:
- A table of files with current % and needed % increase
- For each below-80% file: which missing lines map to which branches
- Test names to add (use test-case-generator skill to implement)

## Examples

**Run and analyse:**
```bash
poetry run pytest tests/ -q --cov=PokemonLibrary --cov-report=term-missing 2>&1 \
  | awk '/TOTAL/{p=0} p; /Name/{p=1}' \
  | awk '$4 < 80 {print $0}'
```

**Report any file under 80%:**
```
PokemonLibrary/exploration.py   120   38   68%   34, 67-89
→ Need ~15 more statements covered. Add tests for:
  - Line 34: early-return when destination == current location
  - Lines 67-89: blocked exit message path
  - Lines 112-140: cheat_mode bypass
```

## Dependencies
- `pytest` with `pytest-cov`
- `tests/` — existing test suite
- `PokemonLibrary/` — source under measurement

## Error Handling
- **Coverage not changing**: confirm the new test file is discovered (filename must start with `test_`)
- **TOTAL drops unexpectedly**: a new source file was added without tests — identify and cover it
- **Excluded files affecting total**: check `[tool.coverage.report] omit` in `pyproject.toml`
