---
name: cross-module-integrator
description: Wires together changes across multiple robot-pokemon layers after specialist agents have implemented them. Use when a feature has been built in data/logic/TUI layers separately and needs to be connected end-to-end.
---

# cross-module-integrator

Connects independently-implemented feature layers into a working end-to-end feature — verifying imports, call sites, and data flows across modules.

## Associated Agent
`feature-orchestrator.agent.md`

## Instructions

### 1. Integration Checklist

After specialist agents complete their layers, verify each connection point:

#### Data → Logic
- [ ] New `Location` entries are imported and accessible via `get_location(name)`
- [ ] New `Trainer` entries are accessible via `get_trainer(id)` and `get_trainers_by_location(loc)`
- [ ] New Pokemon species are in `POKEMON` and referenced correctly in wild tables
- [ ] `content-validator` skill passes with zero errors

#### Logic → TUI
- [ ] New building handler in `buildings.py` is wired in `BuildingMixin.enter_building()` keyed by building name
- [ ] New story flags set in `exploration.py` or `buildings.py` are checked in `exploration.py` exit gates
- [ ] New `pending_command` tokens are handled in `GameFlowMixin.handle_pending_command`
- [ ] `process_command()` in `terminal.py` routes to new commands or locations

#### TUI → Battle
- [ ] New trainer encounter triggers `start_trainer_battle(trainer_id, output)` in `BattleMixin`
- [ ] Gym challenge button wired through `BattleMixin.start_gym_battle`
- [ ] Post-battle flag (e.g. `trainer_beaten`) is set in the battle victory handler

### 2. Common Missing Connections

**Building not triggering:**
```python
# ui/building_mixin.py — enter_building() must have the name keyed
BUILDING_HANDLERS = {
    "pokemon center": self._enter_pokemon_center,
    "pokemart": self._enter_pokemart,
    "bill's house": lambda: enter_bills_house(self.game_state, output),  # ← missing?
}
```

**New command not routable:**
```python
# terminal.py process_command() — add elif branch
elif cmd.startswith("fish"):
    from PokemonLibrary import fishing
    fishing.start_fishing(self.game_state, output)
```

**Story flag set but exit not gated:**
```python
# exploration.py can_move_to() — gate must check the flag
if destination == "Route 24" and "cascade" not in badges:
    if not game_state.cheat_mode:
        return False, "You need the Cascade Badge."
```

### 3. End-to-End Smoke Test (Manual)

Run the game and test the complete user path:
```bash
poetry run python run_terminal.py
```
1. Start a new game → choose starter
2. Walk to the first new location
3. Trigger the new building / NPC
4. Confirm flags are set (`story_flags` visible in debug or save file)
5. Attempt the badge-gated exit before and after earning the badge
6. Trigger a battle with the new trainer
7. Win → confirm prize money and badge (if gym leader)

### 4. Output
- A checklist with each connection verified ✅ or fixed 🔧
- Any remaining gaps requiring specialist agent follow-up

## Dependencies
- All feature layers already implemented
- `PokemonLibrary/ui/building_mixin.py` — building routing
- `PokemonLibrary/terminal.py` — command routing
- `PokemonLibrary/ui/game_flow_mixin.py` — pending_command handler
- `PokemonLibrary/exploration.py` — movement gates

## Error Handling
- **Import error at integration**: a circular import was likely introduced — check that `terminal.py` is not imported from any `PokemonLibrary/` module
- **Feature worked in isolation but not end-to-end**: trace the call path from `process_command` or `on_button_pressed` through to the affected module; one link in the chain is missing
