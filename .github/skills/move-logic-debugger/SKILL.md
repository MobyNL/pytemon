---
name: move-logic-debugger
description: Diagnoses and fixes incorrect move damage calculations, status effect application, and PP tracking in robot-pokemon. Use when a move deals wrong damage, a status effect doesn't apply, or PP is not decremented correctly.
---

# move-logic-debugger

Diagnoses bugs in move execution: damage formula, type effectiveness, status effects, accuracy, and PP.

## Associated Agent
`battle-system.agent.md`

## Instructions

### 1. Damage Formula

```python
# battle/battle_actions.py — simplified Gen 1 formula
damage = ((2 * level / 5 + 2) * power * attack / defense) / 50 + 2
damage = int(damage * type_effectiveness * stab_bonus * random_factor)
```

- **STAB** (Same Type Attack Bonus): 1.5× if attacker's type matches move type
- **Type effectiveness**: from `TYPE_CHART` (`data/type_chart.py`) — 0, 0.5, 1, or 2
- **Random factor**: 0.85–1.00
- **Min damage**: always at least 1

### 2. Type Effectiveness Lookup

```python
from PokemonLibrary.data.type_chart import TYPE_CHART

effectiveness = TYPE_CHART.get(move_type, {}).get(defender_type, 1.0)
# Dual-type defender: multiply both
eff = TYPE_CHART.get(move_type, {}).get(type1, 1.0) * TYPE_CHART.get(move_type, {}).get(type2, 1.0)
```

### 3. Status Effect Application

Status effects are applied in `battle_engine.py` via `apply_status_effect(pokemon, effect)`:

```python
# effect values: "paralysis", "sleep", "poison", "bad_poison", "burn", "freeze"

# End-of-turn damage (burn and poison)
if pokemon.get("status") == "burn":
    damage = max(1, pokemon["max_hp"] // 8)
    pokemon["hp"] = max(0, pokemon["hp"] - damage)

if pokemon.get("status") == "poison":
    damage = max(1, pokemon["max_hp"] // 16)
    pokemon["hp"] = max(0, pokemon["hp"] - damage)
```

### 4. PP Tracking

```python
# Each move in party Pokemon's move list should track current PP
# Structure: {"name": "TACKLE", "pp": 35, "max_pp": 35}

# Decrement on use
move_entry["pp"] = max(0, move_entry["pp"] - 1)

# Check before allowing use
if move_entry["pp"] <= 0:
    output.write("[red]No PP left for this move![/red]")
    return
```

### 5. Debug Checklist

- [ ] Is the move in `MOVES`? Check with `get_move("MOVE NAME")`
- [ ] Is `power` set to a value > 0 for damaging moves? (Status moves have `power: 0`)
- [ ] Is type effectiveness looking up the right types? (defender's types, not attacker's)
- [ ] Is STAB applied with the move's type vs attacker's types?
- [ ] Is `apply_status_effect` checking `effect_chance` with a random roll?

### 6. Output
- Root cause of the damage/effect/PP bug
- Fixed code snippet in the relevant file (`battle_actions.py`, `battle_engine.py`)

## Examples

**Input:** "Thunderbolt is doing the same damage against Ground types as Electric types."

**Investigation:** Type effectiveness lookup using wrong defender.

**Fix:**
```python
# ❌ Looking up move type vs move type (wrong)
eff = TYPE_CHART.get(move["type"], {}).get(move["type"], 1.0)

# ✅ Looking up move type vs defender type
for def_type in defender["types"]:
    eff *= TYPE_CHART.get(move["type"], {}).get(def_type, 1.0)
```

## Dependencies
- `PokemonLibrary/battle/battle_actions.py` — damage calculation
- `PokemonLibrary/engine/battle_engine.py` — `BattleState`, status effects, turn resolution
- `PokemonLibrary/data/type_chart.py` — `TYPE_CHART`
- `PokemonLibrary/data/move_data.py` — `MOVES`

## Error Handling
- **Damage = 0**: check if `power` is 0 (status move) or if effectiveness chain results in 0 (Immunity)
- **Status never applies**: verify `effect_chance` > 0 and the random roll logic (`random.randint(1,100) <= effect_chance`)
- **PP never runs out**: confirm `pp` is tracked on the Pokemon's move dict, not on the global `MOVES` dict
