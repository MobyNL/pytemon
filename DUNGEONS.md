# How Dungeons Work in pytemon

This document describes the current dungeon/area system — how locations are defined,
how exploration works, how trainers and wild encounters are triggered, and what the path
forward looks like for multi-floor dungeons.

---

## 1. Location Types

Every in-game area is a `Location` object (defined in `pytemon/locations.py`).
There are four types:

| Constant | Value | Description |
|---|---|---|
| `TYPE_TOWN` | `"town"` | Cities and towns — no exploration, only buildings and exits |
| `TYPE_ROUTE` | `"route"` | Outdoor routes with tall grass — explorable |
| `TYPE_FOREST` | `"forest"` | Forest areas — explorable, higher encounter rate |
| `TYPE_DUNGEON` | `"dungeon"` | Caves, buildings, towers — explorable, same rules as routes |

Only `TYPE_ROUTE`, `TYPE_FOREST`, and `TYPE_DUNGEON` locations can be **explored** (`can_explore()` returns `True`).

---

## 2. The Location Dataclass

```python
Location(
    name="Rock Tunnel",
    location_type=TYPE_DUNGEON,
    description="A pitch-black labyrinth...",
    exits={
        "Route 10": {"direction": "north", "blocked": False, "min_explores": 10},
        "Lavender Town": {"direction": "south", "blocked": False, "min_explores": 10},
    },
    wild_pokemon=["ZUBAT", "GEODUDE", "MACHOP", "ONIX", "GRAVELER"],
    wild_level_range=(15, 23),
    trainers=5,
    trainer_encounter_rate=0.30,
    wild_encounter_rate=0.65,
)
```

### Key fields

| Field | Purpose |
|---|---|
| `exits` | Dict of destination → `{direction, blocked, reason, min_explores}` |
| `wild_pokemon` | List of species keys (must match names in `POKEMON` dict) |
| `wild_level_range` | `(min, max)` — wild Pokemon level is randomly picked in this range |
| `trainers` | Total trainer count (used for display — actual trainer objects live in `trainer_data.py`) |
| `trainer_encounter_rate` | Probability (0–1) of a trainer battle triggering when undefeated trainers exist |
| `wild_encounter_rate` | Probability (0–1) of a wild encounter triggering after the trainer check passes |
| `blocked_buildings` | Dict of building → reason string, shown as locked icons |

---

## 3. Exits and Gating

Every exit is an entry in `exits`:

```python
"Route 13": {
    "direction": "south",
    "blocked": True,
    "reason": "A sleeping Snorlax blocks the path...",
}
"Fuchsia City": {
    "direction": "west",
    "blocked": False,
    "min_explores": 5,   # player must explore ≥5 times before this exit appears
}
```

- `blocked: True` → exit is locked; `reason` is shown to the player
- `min_explores` → exit only becomes available once the player has explored the area N times
- Badge checks and story flag checks are applied in `exploration.py` at movement time

---

## 4. The Explore Loop (`exploration.py`)

When the player types `explore` (or presses the Explore button):

```
explore_area(game_state, output, trigger_wild_cb, trigger_trainer_cb)
```

### Decision tree (per explore call)

```
1. Is there an undefeated trainer here?
   └─ Yes (trainer_encounter_rate roll succeeds)
       → trigger_trainer_callback → battle begins
   └─ No (or roll fails)
       → check for item pickup (_try_find_item)
       → roll wild_encounter_rate
           └─ Wild encounter → trigger_wild_callback → battle begins
           └─ No encounter → flavour text ("You search but find nothing...")
2. Increment route_progress[location_name] by 1 (or 2 if cycling)
3. Record explore in stats
```

### Trainer encounter logic

Trainers are matched by location: `get_trainers_for_location(location_name)` returns all
`Trainer` objects from `trainer_data.py` that have `location == current_location.name`.
Defeated trainer IDs are stored in `game_state.game_data["defeated_trainers"]`.
Only undefeated trainers are eligible for encounter.

**Gym trainers** are a separate concept — they are stored in `GYM_TRAINERS` in
`gym_system.py` and only appear when the player enters the Gym building, not during
general exploration.

---

## 5. Route Progress and Exit Unlocking

`game_state.get_route_progress(name)` returns how many times the player has explored a location.

When the player tries to move to a destination with `min_explores: N`, the engine checks:

```python
if progress >= required OR destination == previous_location:
    allow movement
else:
    show progress bar and block
```

The progress bar displayed in `look_around` shows something like:
```
→ Fuchsia City: [█████░░░░░] 5/10
```

---

## 6. Item Pickups (`_try_find_item`)

Ground items are defined in `_GROUND_ITEMS` (a dict in `exploration.py`).
Each location has a list of items that can be found in order.
A small random roll triggers a pickup on each explore.
Items are one-time: a `found_items` counter per location tracks how many have been picked up.

---

## 7. Current Dungeon Areas

| Location | Type | Wild Pokemon | Trainers | Special |
|---|---|---|---|---|
| Viridian Forest | forest | Caterpie, Metapod, Butterfree, Pikachu, Weedle | 3 | — |
| Mt. Moon | dungeon | Zubat, Clefairy, Geodude, Paras | 6 | Fossil items spawnable |
| Rock Tunnel | dungeon | Zubat, Geodude, Machop, Onix, Graveler | 5 | Flash mentioned in description |
| Diglett's Cave | dungeon | Diglett, Dugtrio | 0 | Shortcut Route 2 ↔ Route 11 |
| Pokemon Tower | dungeon | Gastly, Haunter, Cubone | 3 | enter_pokemon_tower() story flags |
| Team Rocket's Hideout | dungeon | Rattata, Ekans, Koffing, Drowzee | 10 | Giovanni boss fight |
| Safari Zone | dungeon | Scyther, Kangaskhan, Tauros, Chansey, Pinsir… | 0 | enter_safari_zone() entry flow |
| S.S. Anne | — | — | — | enter_ss_anne() building function, no Location entry |

---

## 8. Special Building Entry Functions

Some dungeon-like areas are implemented as **building entry functions** rather than standalone
`Location` objects. These live in `pytemon/buildings.py` and are dispatched from
`enter_building()` when a matching name is found in the current location's `buildings` list.

| Function | Building name | What it does |
|---|---|---|
| `enter_pokemon_tower()` | `"Pokemon Tower"` | Story flags, Channeler trainers, Mr. Fuji arc |
| `enter_ss_anne()` | `"S.S. Anne"` | Ticket check, trainer tour, captain + HM01 Cut |
| `enter_ss_anne_dock()` | `"S.S. Anne Dock"` | Pre-boarding dock NPC |
| `enter_game_corner()` | `"Game Corner"` | Slot machine flavour, Rocket hint |
| `enter_department_store()` | `"Celadon Department Store"` | Display-only item list |
| `enter_safari_zone()` | `"Safari Zone"` | ₽500 entry, 30 Safari Balls, move to Safari Zone location |
| `enter_mr_fujis_house()` | `"Mr. Fuji's House"` | Story flags, Poke Flute reward |

---

## 9. Story Flags in Dungeons

Story progress is tracked as booleans in `game_state.game_data["story_flags"]`.
Common dungeon flags:

| Flag | Set when |
|---|---|
| `ss_anne_departed` | SS Anne leaves Vermillion after player visits |
| `received_hm01_cut` | Captain awards HM01 Cut |
| `received_mt_moon_fossil` | Player picks up a fossil in Mt. Moon |
| `pokemon_tower_visited` | Player enters Pokemon Tower for the first time |
| `pokemon_tower_mr_fuji_rescued` | Mr. Fuji rescue arc complete |
| `pokemon_tower_ghost_appeared` | Ghost encounter triggered |
| `defeated_giovanni_hideout` | Giovanni defeated in Team Rocket's Hideout |

---

## 10. What's Not Yet Implemented (Future Work)

The following are planned but not yet built:

### Multi-floor dungeons
Currently every dungeon is a **single flat `Location`**. The plan is to give each dungeon
multiple named floors/rooms, each with their own wild Pokemon, trainers, and exits
(ladders, stairs, warps). This requires a `DungeonDefinition` data model and a
`current_floor` field in `GameState`.

---

## 11. Recently Implemented

### Mt. Moon registered as dungeon ✅
Mt. Moon was previously registered as `TYPE_FOREST`. It is now `TYPE_DUNGEON`, matching
its description as a cave system.

### Flash darkness penalty (Rock Tunnel) ✅
Without Flash active, Rock Tunnel's wild encounter rate is tripled (capped at 100%) and
all trainer names/descriptions are hidden (`"???"` / `"Trainer"`). Using `HM05 Flash`
(via the `use flash` field command) stores the lit state in
`game_state.game_data["flash_lit_locations"]` and resets when the player leaves the
location. The tip to use Flash is shown on every dark-tunnel explore.

### Silph Scope gating (Pokemon Tower) ✅
Without the Silph Scope, 70 % of wild encounters in Pokemon Tower resolve as a ghost
blocking message instead of a battle. The remaining 30 % still reach Cubone (a non-ghost
species) normally. With the Silph Scope all wild encounters proceed as usual.

### Safari Zone catch mechanics ✅
Wild encounters in the Safari Zone now start in Safari mode (`BattleState.is_safari = True`).
The normal battle options are replaced with:

| Command | Effect |
|---|---|
| `safari ball` | Throw a Safari Ball (same catch modifier as Ultra Ball); bait halves catch rate, rock raises it 1.5× |
| `bait` | 3-turn bait active: flee chance drops to 2 %, catch rate halved |
| `rock` | 2-turn rock active: flee chance rises to 35 %, catch rate ×1.5 |
| `run` | Flee safely with no penalty |

Safari Balls are now stored in the standard `game_data["items"]` dict (fixed the
previous bug where they were written to `game_data["bag"]`).

### Escape Rope dungeon restriction ✅
The Escape Rope now performs a BFS over the location graph to find the nearest reachable
town, so it works correctly from deep dungeons (e.g. Diglett's Cave) that have no direct
town exit. It still refuses to activate from inside a town.

