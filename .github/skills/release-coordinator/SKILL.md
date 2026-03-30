---
name: release-coordinator
description: Runs the full robot-pokemon CI quality gate before a feature is considered done. Use as the final step in any feature implementation to confirm ruff format, ruff lint, pytest coverage, and Robot Framework smoke test all pass.
---

# release-coordinator

Executes every CI quality gate in sequence and confirms the feature is ready to commit.

## Associated Agent
`feature-orchestrator.agent.md`

## Instructions

### 1. Full CI Gate (run in this exact order)

```bash
# 1. Format check (hard fail)
poetry run ruff format --check pytemon/ tests/

# 2. Lint tests (hard fail)
poetry run ruff check tests/

# 3. Lint source (informational — fix if possible)
poetry run ruff check pytemon/

# 4. Type check (informational)
poetry run mypy pytemon/

# 5. Unit tests + coverage (hard fail — must be ≥80%)
poetry run pytest tests/ --tb=short -v --cov=pytemon --cov-report=term-missing

# 6. Robot Framework smoke test (game launches without crash)
poetry run robot test.robot
```

### 2. Auto-Fix Workflow (if steps 1-3 fail)

```bash
poetry run ruff format pytemon/ tests/
poetry run ruff check tests/ --fix
poetry run ruff check pytemon/ --fix

# Re-run checks to confirm clean
poetry run ruff format --check pytemon/ tests/
poetry run ruff check tests/
```

### 3. Hard-Fail Criteria (must pass before done)

| Check | Pass condition |
|---|---|
| `ruff format --check` | 0 files would be reformatted |
| `ruff check tests/` | 0 errors |
| `pytest` exit code | 0 |
| Coverage TOTAL | ≥ 80% |

### 4. Informational-Only (fix if easy, don't block)

| Check | Notes |
|---|---|
| `ruff check pytemon/` | Fix obvious violations; N999 and RUF012 are whitelisted |
| `mypy pytemon/` | Fix type errors where possible; `Any` annotations are acceptable |

### 5. Coverage Shortfall Response

If coverage drops below 80%:
1. Run `--cov-report=term-missing` to find MISS lines
2. Use `test-case-generator` skill to write targeted tests
3. Re-run coverage to confirm ≥80%

### 6. Success Report Format

After all gates pass, produce:

```
✅ ruff format --check  — clean
✅ ruff check tests/    — 0 errors
⚠️  ruff check source   — 2 informational (N809 — acceptable)
⚠️  mypy                — 3 notes (Any types — acceptable)
✅ pytest               — 247 passed, 0 failed
✅ coverage             — TOTAL 84%
✅ robot test.robot      — 1 test passed
```

### 7. Reporting a Blocker

If a hard-fail gate cannot be fixed without scope change, surface it immediately:
```
🚫 BLOCKER: pytest — 3 tests failing in test_buildings.py
   Root cause: enter_bike_shop() raises KeyError on "bag" — start_new_game() not called in fixture
   Action needed: fix fixture in conftest.py (mock-data-creator skill) before release
```

## Dependencies
- `ruff`, `mypy`, `pytest`, `pytest-cov` — installed via poetry
- `test.robot` — Robot Framework smoke test
- `pyproject.toml` — ruff and coverage configuration

## Error Handling
- **Robot Framework test fails**: run `poetry run robot --loglevel DEBUG test.robot` for full output
- **Coverage at exactly 80%**: this passes; do not add low-value tests just to bump a decimal
- **Mypy fails on a new file**: add `# type: ignore` only if the error is in Textual integration code; otherwise fix the type
