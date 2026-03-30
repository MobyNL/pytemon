---
name: pokemon-data-entry
description: Adds new Pokemon species entries to the robot-pokemon data layer. Use when adding a new species, filling in missing base stats, updating learnsets, or wiring evolution chains.
---

# pokemon-data-entry

Adds well-formed entries to `POKEMON` in `data/pokemon_data.py`, ensuring stats, learnsets, and evolution chains are correct and complete.

## Associated Agent
`game-content.agent.md`

## Instructions

### 1. Input
- **Species name** (uppercase, e.g. `CLEFAIRY`)
- **Pokedex number**
- **Types** (1 or 2)
- **Base stats**: hp, attack, defense, special, speed
- **Base moves** (moves known at level 1)
- **Learnset** (level → move name dict)
- **Evolution info** (method, condition, target species)
- **Catch rate** (0–255; rarer = lower)
- **Flavour description**

### 2. Validation
- All move names in `base_moves` and `learnset` must exist in `MOVES` (`data/move_data.py`)
- Evolution `"into"` species must also exist in `POKEMON` (add both pre- and post-evolution together)
- Types must be valid type strings from `TYPE_CHART` (`data/type_chart.py`)
- Pokedex number must be unique

### 3. Execution

```python
# data/pokemon_data.py — add to POKEMON dict
"CLEFAIRY": {
    "number": 35,
    "name": "CLEFAIRY",
    "types": ["Normal"],
    "base_stats": {
        "hp": 70, "attack": 45, "defense": 48,
        "special": 60, "speed": 35
    },
    "base_moves": ["POUND", "GROWL"],
    "learnset": {
        13: "SING",
        18: "DOUBLESLAP",
        24: "MINIMIZE",
        31: "METRONOME",
        39: "DEFENSE CURL",
        48: "LIGHT SCREEN",
        58: "DOUBLE-EDGE",
    },
    "evolution": {
        "method": "item",
        "item": "Moon Stone",
        "into": "CLEFABLE",
    },
    "catch_rate": 150,
    "base_exp": 68,
    "description": "Its magical and cute appearance has many admirers.",
},
```

**For trade evolutions:**
```python
"evolution": {"method": "trade", "into": "ALAKAZAM"}
```

**For Pokemon with no evolution:**
```python
"evolution": None
```

### 4. Output
- The complete dict entry ready to paste into `POKEMON`
- A checklist confirming moves, types, and evolution target all exist

## Examples

**Input:** "Add Eevee (133) with branching stone evolutions to Vaporeon, Jolteon, Flareon."

**Output snippet:**
```python
"EEVEE": {
    "number": 133,
    "name": "EEVEE",
    "types": ["Normal"],
    "base_stats": {"hp": 55, "attack": 55, "defense": 50, "special": 45, "speed": 55},
    "base_moves": ["TACKLE", "TAIL WHIP"],
    "learnset": {29: "SAND ATTACK", 36: "GROWL", 42: "QUICK ATTACK", 54: "FOCUS ENERGY"},
    "evolution": {
        "method": "item",
        "item": "Water Stone",   # handled per-branch in evolution.py get_stone_evolution()
        "into": "VAPOREON",
    },
    "catch_rate": 45,
    "base_exp": 92,
    "description": "An unstable genetic makeup that suddenly mutates due to the environment.",
},
```

## Dependencies
- `pytemon/data/pokemon_data.py` — `POKEMON` dict
- `pytemon/data/move_data.py` — `MOVES` dict (validate move names)
- `pytemon/data/type_chart.py` — valid type strings
- `pytemon/evolution.py` — `check_evolution`, `get_stone_evolution`

## Error Handling
- **Move not in MOVES**: add the move to `move_data.py` first, or choose an existing move
- **Evolution target missing**: add both species in the same commit
- **Duplicate Pokedex number**: check existing entries before assigning
