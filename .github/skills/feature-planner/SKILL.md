---
name: feature-planner
description: Breaks a robot-pokemon feature request into a layered implementation plan across data, logic, TUI, tests, and CI. Use at the start of any new feature to produce a scoped work breakdown before delegating to specialist agents.
---

# feature-planner

Analyses a feature request and produces a complete, ordered implementation plan — identifying which layers are affected, what files to change, and in what order.

## Associated Agent
`feature-orchestrator.agent.md`

## Instructions

### 1. Input
- **Feature description** — what the player will experience (e.g. "Add Route 24, Bill's House, and NPC that gives S.S. Anne ticket")

### 2. Layer Analysis

Work top-down through the stack. For each layer, ask: "Does this feature require work here?"

```
Layer 1 — game-content:   Static data (Pokemon, moves, locations, trainers, gyms)
Layer 2 — game-logic:     Exploration, buildings, items, story flags
Layer 3 — tui-specialist: Terminal commands, panels, pending_command flows, button wiring
Layer 4 — battle-system:  Only if new battle mechanics are introduced
Layer 5 — test-writer:    Tests for every changed file
Layer 6 — ci-quality:     Ruff format + lint + pytest confirmation
```

### 3. Output Format

Produce a structured plan:

```
## Feature: Add Route 24 and Bill's House

### Layer 1 — game-content
Files: locations.py, trainer_data.py
Changes:
- Route 24: route type, connects Cerulean City <-> Nugget Bridge area
  wild_pokemon: Bellsprout lv15-20, Abra lv13-17
- Bill's House: city type stub, connects Route 24
- 5 Nugget Bridge trainers (lv14-17), prize Nugget at end
Blocked by: player must have Cascade Badge

### Layer 2 — game-logic
Files: exploration.py, buildings.py
Changes:
- exploration.py: gate Route 24 exit behind cascade badge flag
- buildings.py: enter_bills_house() — story dialogue + one-time SS Anne ticket reward
  flag: "received_ss_ticket"

### Layer 3 — tui-specialist
Files: terminal.py, ui/building_mixin.py
Changes:
- Add "bill's house" to enter_building() routing
- Wire "nugget bridge" text event via show_arrival callback

### Layer 4 — battle-system
Not required (no new battle mechanics).

### Layer 5 — test-writer
Files to test: locations.py, exploration.py, buildings.py
Tests needed:
- Route 24 exists with correct connections
- Connections bidirectional (Cerulean <-> Route 24)
- Badge gate blocks movement without Cascade Badge
- Badge gate passes with Cascade Badge
- Bill's House ticket: given once, not again on repeat visit
- Nugget Bridge trainers exist with correct levels

### Layer 6 — ci-quality
Run: ruff format --check, ruff check tests/, pytest -q
```

### 4. Dependency Order Rules

- Layer 1 must complete before Layer 2 (logic depends on data)
- Layer 2 must complete before Layer 3 (TUI wires logic layer functions)
- Layer 4 is independent — run in parallel with 2 or 3 if possible
- Layer 5 must run after all implementation layers
- Layer 6 always runs last

### 5. Output
- The full layered plan as above
- List of all files that will be modified
- Any risks or ambiguities to resolve before starting

## Dependencies
- All specialist agents: `game-content`, `game-logic`, `tui-specialist`, `battle-system`, `test-writer`, `ci-quality`

## Error Handling
- **Scope too large**: split into sub-features (e.g. "Route 24 data" as one feature, "Bill's House logic" as another)
- **Unclear requirement**: surface the ambiguity before building the plan rather than guessing
