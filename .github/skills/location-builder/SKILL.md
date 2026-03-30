---
name: location-builder
description: Creates new Location entries for the robot-pokemon world map. Use when adding routes, cities, towns, or dungeons — handles the Location dataclass, bidirectional connections, wild Pokemon tables, and gym stubs.
---

# location-builder

Adds fully connected `Location` entries to `LOCATIONS` in `locations.py`, ensuring the world map stays internally consistent.

## Associated Agent
`game-content.agent.md`

## Instructions

### 1. Input
Per location:
- **Name** (exact string used everywhere, e.g. `"Route 3"`)
- **Type**: `"route"`, `"town"`, `"city"`, `"dungeon"`
- **Connects to** (list of adjacent location names)
- **Wild Pokemon** (list of `{species, min_level, max_level}` dicts) — empty for towns/cities
- **Description** (1–2 sentences shown on arrival)
- **Flags**: `has_pokemon_center`, `has_pokemart`, `gym_leader` (leader trainer ID or `None`)

### 2. Validation
- Every name in `connected_to` must already exist in `LOCATIONS` **or** be added in the same batch
- Add the new location's name to `connected_to` on each neighbour — connections are **bidirectional**
- Species in wild tables must exist in `POKEMON`
- A location with `gym_leader` must have a matching entry in `GYMS`

### 3. Execution

```python
# locations.py — add to LOCATIONS dict
"Route 3": Location(
    name="Route 3",
    location_type="route",
    connected_to=["Pewter City", "Mt. Moon"],
    wild_pokemon=[
        {"species": "PIDGEY",    "min_level": 10, "max_level": 14},
        {"species": "JIGGLYPUFF","min_level": 11, "max_level": 13},
        {"species": "MEOWTH",    "min_level": 10, "max_level": 14},
    ],
    description="A winding path east of Pewter City, alive with the sounds of wild Pokemon.",
    has_pokemon_center=False,
    has_pokemart=False,
    gym_leader=None,
),
```

**Then update each neighbour's `connected_to`:**
```python
# Pewter City entry — add "Route 3"
connected_to=["Route 2", "Route 3"],   # was: ["Route 2"]

# Mt. Moon entry — add "Route 3"
connected_to=["Route 3", "Route 4"],   # was: ["Route 4"]
```

**City with gym:**
```python
"Cerulean City": Location(
    name="Cerulean City",
    location_type="city",
    connected_to=["Route 4", "Route 24"],
    wild_pokemon=[],
    description="A beautiful city known for its water Pokemon gym.",
    has_pokemon_center=True,
    has_pokemart=True,
    gym_leader="misty",
),
```

### 4. Output
- All new `Location` entries
- Updated `connected_to` lists for affected neighbours
- Checklist: bidirectional connections confirmed, species validated

## Examples

**Input:** "Add Mt. Moon as a dungeon between Route 3 and Route 4 with Zubat, Clefairy, Geodude."

**Output:**
```python
"Mt. Moon": Location(
    name="Mt. Moon",
    location_type="dungeon",
    connected_to=["Route 3", "Route 4"],
    wild_pokemon=[
        {"species": "ZUBAT",   "min_level": 8,  "max_level": 12},
        {"species": "CLEFAIRY","min_level": 9,  "max_level": 11},
        {"species": "GEODUDE", "min_level": 8,  "max_level": 12},
    ],
    description="A vast cave riddled with Zubat and strange lunar stones.",
),
```

## Dependencies
- `pytemon/locations.py` — `LOCATIONS` dict and `Location` dataclass
- `pytemon/data/pokemon_data.py` — validate wild species
- `pytemon/gym_system.py` — if adding a city with a gym

## Error Handling
- **Missing neighbour**: if a connected location doesn't exist yet, add it in the same batch
- **One-way connection**: always update both sides of every connection
- **Wild species typo**: use uppercase species key (e.g. `"CLEFAIRY"`, not `"Clefairy"`)
