---
name: content-validator
description: Validates the integrity of the robot-pokemon data layer. Use before committing new game content to confirm bidirectional connections, valid species/move references, unique Pokedex numbers, and consistent gym badge chains.
---

# content-validator

Runs a systematic integrity check across the data layer to catch missing references, broken connections, and inconsistent data before tests or CI catch them the hard way.

## Associated Agent
`game-content.agent.md`

## Instructions

### 1. What to Validate

Run these checks after any game-content change:

#### Locations
- [ ] Every name in `connected_to` exists as a key in `LOCATIONS`
- [ ] Connections are bidirectional: if A connects to B, B connects to A
- [ ] Every location with `gym_leader` has an entry in `GYMS`
- [ ] Wild species in `wild_pokemon` lists exist in `POKEMON`

#### Pokemon
- [ ] `evolution["into"]` species exists in `POKEMON`
- [ ] All move names in `base_moves` and `learnset` exist in `MOVES`
- [ ] Types are valid strings present in `TYPE_CHART`
- [ ] Pokedex numbers are unique

#### Trainers / Gyms
- [ ] Gym `leader_id` matches a `Trainer.id` in `TRAINERS`
- [ ] Gym `min_badges` actually corresponds to a badge that is obtainable before this gym
- [ ] All `TrainerPokemon.species` exist in `POKEMON`
- [ ] Non-zero `badge_reward` and `badge_id` only on trainers with `trainer_class="Gym Leader"`

### 2. Quick Validation Script

Run this in a Python shell to surface broken references:

```python
from pytemon.locations import LOCATIONS
from pytemon.data.pokemon_data import POKEMON
from pytemon.data.move_data import MOVES
from pytemon.data.type_chart import TYPE_CHART
from pytemon.gym_system import GYMS
from pytemon.data.trainer_data import TRAINERS

errors = []

# Bidirectional connections
for name, loc in LOCATIONS.items():
    for neighbour in loc.connected_to:
        if neighbour not in LOCATIONS:
            errors.append(f"MISSING LOCATION: {name} -> {neighbour}")
        elif name not in LOCATIONS[neighbour].connected_to:
            errors.append(f"ONE-WAY: {name} -> {neighbour} (not reciprocated)")

# Wild species
for name, loc in LOCATIONS.items():
    for entry in loc.wild_pokemon:
        if entry["species"] not in POKEMON:
            errors.append(f"MISSING SPECIES: {entry['species']} in {name} wild table")

# Pokemon moves and evolutions
for species, data in POKEMON.items():
    for move in data.get("base_moves", []):
        if move not in MOVES:
            errors.append(f"MISSING MOVE: {move} in {species} base_moves")
    evo = data.get("evolution")
    if evo and evo.get("into") and evo["into"] not in POKEMON:
        errors.append(f"MISSING EVO TARGET: {evo['into']} for {species}")

for err in errors:
    print("ERROR:", err)
print(f"Validation complete. {len(errors)} error(s) found.")
```

### 3. Fixing Common Issues
- **One-way connection**: add the missing name to the other location's `connected_to`
- **Missing move**: add to `MOVES` in `move_data.py` or change to an existing move name
- **Missing evolution target**: add the evolved form to `POKEMON`
- **Gym leader ID mismatch**: align the `leader_id` in `GYMS` with the `id` field on the `Trainer`

### 4. Output
- List of all validation errors (empty = clean)
- Confirmation that connections, species, and moves are all internally consistent

## Examples

**Running locally:**
```bash
poetry run python -c "
from pytemon.locations import LOCATIONS
for n, l in LOCATIONS.items():
    for nb in l.connected_to:
        if nb not in LOCATIONS:
            print(f'MISSING: {n} -> {nb}')
        elif n not in LOCATIONS[nb].connected_to:
            print(f'ONE-WAY: {n} -> {nb}')
print('done')
"
```

## Dependencies
- `pytemon/locations.py`
- `pytemon/data/pokemon_data.py`
- `pytemon/data/move_data.py`
- `pytemon/data/type_chart.py`
- `pytemon/gym_system.py`
- `pytemon/data/trainer_data.py`

## Error Handling
- **Import error when running script**: check for a syntax error in the file you just edited
- **Circular connection**: A→B and B→A is correct and expected — this is not a bug
- **Location added but tests fail**: run `content-validator` first; a broken reference will cascade into test failures
