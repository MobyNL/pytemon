---
name: rule-enforcer
description: Implements and audits gameplay rules in robot-pokemon — badge-gated paths, one-time event guards, item use restrictions, and movement constraints. Use when adding a blocked exit, a story flag gate, or any conditional behaviour that depends on player progress.
---

# rule-enforcer

Adds and validates gameplay rules: badge gates, story flag checks, item restrictions, and one-time event guards.

## Associated Agent
`game-logic.agent.md`

## Instructions

### 1. Input
- **Rule to enforce** — e.g. "Route 24 requires Cascade Badge", "Moon Stone only gained once"
- **Triggering location or action** — where/when the rule applies
- **Condition** — badge ID, story flag key, item count, or party state
- **Failure message** — what the player sees when blocked

### 2. Badge-Gated Path

In `locations.py`, add a blocking condition to the exit:
```python
# In can_move_to() in locations.py or exploration.py
if destination == "Route 24":
    if "cascade" not in game_data.get("badges", []):
        return False, "[yellow]The path is blocked. Earn the Cascade Badge first.[/yellow]"
```

Or via `exit_data` on the Location:
```python
# locations.py
connected_to=["Cerulean City"],   # Route 24 exit
# exploration.py checks game_data["badges"] before allowing movement
```

### 3. Story Flag Guard (one-time event)

```python
# exploration.py — in show_arrival or explore_area callback
flags = game_state.game_data["story_flags"]
if location_name == "Mt. Moon" and not flags.get("received_moon_stone"):
    flags["received_moon_stone"] = True
    bag = game_state.game_data["bag"]
    bag["Moon Stone"] = bag.get("Moon Stone", 0) + 1
    output.write("[bold yellow]★  You found a MOON STONE![/bold yellow]")
# Second visit: flag is True, block skips, no duplicate item
```

### 4. Item Use Restriction

```python
# items.py
if item_name == "Thunder Stone":
    valid_species = {"PIKACHU", "EEVEE"}   # only these can use it
    if pokemon["species"] not in valid_species:
        output.write(f"[red]{pokemon['name']} can't use the Thunder Stone.[/red]")
        return
```

### 5. Checklist Before Adding a New Rule
- [ ] Story flag key is a meaningful snake_case string (e.g. `"rival_cerulean_beaten"`)
- [ ] Flag is set exactly once — guard with `if not flags.get("flag_name")`
- [ ] Player sees a helpful message explaining the block (not a silent no-op)
- [ ] Rule is bypassed by `game_state.cheat_mode` if it's a movement gate

### 6. Output
- The guard code snippet + flag key
- The failure message string (Rich formatted)
- Where to insert the code (file and function)

## Examples

**Input:** "Block Route 24 until player has Cascade Badge."

**Output:**
```python
# exploration.py — in move_to_location, after resolving destination
if destination.lower() == "route 24":
    if "cascade" not in game_state.game_data.get("badges", []):
        if not game_state.cheat_mode:
            output.write("[yellow]A trainer blocks the way: 'You need the Cascade Badge!'[/yellow]")
            return
```

## Dependencies
- `PokemonLibrary/exploration.py` — movement and arrival logic
- `PokemonLibrary/items.py` — item use restrictions
- `PokemonLibrary/game_state.py` — `game_data["story_flags"]`, `game_data["badges"]`, `cheat_mode`

## Error Handling
- **Flag never set**: trace back to where the preceding event (gym win, story beat) should set it
- **CheatMode bypass forgotten**: always wrap hard blocks with `if not game_state.cheat_mode`
- **Rule fires on repeat visits**: ensure the flag is set before the reward so the guard fires correctly next time
