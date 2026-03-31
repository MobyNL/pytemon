---
name: event-trigger-debugger
description: Diagnoses and fixes broken story events, one-time triggers, and NPC interactions in robot-pokemon. Use when a story event doesn't fire, fires twice, or a story flag is not being set or checked correctly.
---

# event-trigger-debugger

Debugs story events, one-time triggers, and flag-gated NPC interactions that are misfiring or not firing at all.

## Associated Agent
`game-logic.agent.md`

## Instructions

### 1. Diagnose the Problem

Ask / check:
- **Does the event fire at all?** → Is the entry point being reached?
- **Does it fire multiple times?** → Is the flag guard missing or checking the wrong key?
- **Does the flag get set?** → Is `story_flags["key"] = True` actually executed?
- **Is the flag checked correctly?** → `.get("key")` vs `["key"]` — use `.get()` to avoid `KeyError`

### 2. Common Bug Patterns

**Bug: event fires every time (flag not persisted)**
```python
# ❌ Flag check is correct but set is inside an else — never actually runs
if not flags.get("received_moon_stone"):
    output.write("You found a Moon Stone!")   # no Rich markup, and...
    # forgot: flags["received_moon_stone"] = True   ← missing!
```
```python
# ✅ Set the flag BEFORE the reward display; use texts/en/ for the message
# texts/en/exploration.py:
# MOON_STONE_FOUND: list[str] = [
#     "[bold yellow]★  You found a MOON STONE![/bold yellow]",
# ]
from pytemon.texts.en import exploration as T
from pytemon.ui.formatters import write_lines

if not flags.get("received_moon_stone"):
    flags["received_moon_stone"] = True          # set first
    bag["Moon Stone"] = bag.get("Moon Stone", 0) + 1
    write_lines(output, T.MOON_STONE_FOUND)
```

**Bug: event never fires (wrong trigger location)**
```python
# ❌ Event checks location name with wrong capitalisation
if location_name == "mt. moon":    # LOCATIONS key is "Mt. Moon"
```
```python
# ✅ Case-insensitive compare, or use canonical name from LOCATIONS
if location_name.lower() == "mt. moon":
```

**Bug: flag checked but GameState not saved → lost on reload**
```python
# Verify save/load includes story_flags
# game_state.py save_game() must serialise game_data["story_flags"]
# game_state.py load_game() must restore it
```

**Bug: building handler called twice on one visit**
```python
# ❌ BuildingMixin calls enter_building() in both button press AND process_command
# ✅ Trace on_button_pressed and process_command — ensure only one path leads to the handler
```

### 3. Debug Checklist
- [ ] Add a temporary `output.write(f"[dim]DEBUG flags: {flags}[/dim]")` to see current state
- [ ] Confirm the flag key string is spelled identically at set and check sites (grep for it)
- [ ] Confirm the function containing the trigger is actually called (add a `logger.debug` or output line)
- [ ] Confirm `game_data["story_flags"]` is saved and restored in `save_game()` / `load_game()`
- [ ] Remove debug output before committing

### 4. Output
- Root cause identified
- Fixed code snippet
- Confirmation the flag is correctly guarded (set once, checked consistently)

## Examples

**Input:** "The Bike Shop gives the bicycle every time the player enters."

**Investigation:** The function lacks a flag guard.

**Fix:**
```python
# texts/en/buildings.py:
# BIKE_SHOP_REPEAT: list[str] = ["[italic]\"Enjoying that Bicycle?\"[/italic]"]
# BIKE_SHOP_FIRST_VISIT: list[str] = [
#     "[italic]\"Here, take this BICYCLE on the house!\"[/italic]",
#     "",
#     "[bold cyan]You received a BICYCLE![/bold cyan]",
# ]
from pytemon.texts.en import buildings as T
from pytemon.ui.formatters import write_lines

def enter_bike_shop(game_state, output):
    flags = game_state.game_data["story_flags"]
    if flags.get("received_bicycle"):
        write_lines(output, T.BIKE_SHOP_REPEAT)
        return
    flags["received_bicycle"] = True          # guard set FIRST
    game_state.game_data["bag"]["Bicycle"] = 1
    write_lines(output, T.BIKE_SHOP_FIRST_VISIT)
```

## Dependencies
- `pytemon/exploration.py` — arrival events
- `pytemon/buildings.py` — building handlers
- `pytemon/game_state.py` — `story_flags` storage and save/load
- `pytemon/ui/building_mixin.py` — building entry routing

## Error Handling
- **KeyError on `story_flags["key"]`**: always use `.get("key")` or `.get("key", False)`
- **Flag resets on game load**: verify `save_game()` includes `story_flags` in the serialised dict
