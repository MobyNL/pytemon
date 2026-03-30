---
name: dialogue-writer
description: Writes NPC dialogue, trainer intro/defeat/victory text, and building story text for the robot-pokemon game. Use when adding a new NPC, trainer encounter, or building script that needs flavourful in-game text.
---

# dialogue-writer

Writes in-game text for NPCs, trainers, and story moments. Text must fit the Gen 1 Pokemon tone: energetic, brief, and memorable.

## Associated Agent
`game-content.agent.md`

## Instructions

### 1. Input
- **Character type**: trainer, NPC, gym leader, building attendant, item giver
- **Context**: location, situation (first meeting, defeat, victory, repeat visit)
- **Key info to convey**: badge requirement, item reward, lore hook, hint
- **Tone**: competitive (trainer), quirky (NPC), authoritative (gym leader), helpful (attendant)

### 2. Voice Guide

| Character class | Tone | Example opener |
|---|---|---|
| Youngster | Overconfident, rivalrous | "My [Pokemon] is in the top percent!" |
| Lass | Cheerful, fashion-conscious | "Oh! You have such cute Pokemon!" |
| Gym Leader | Serious, elemental themed | "I, Misty, accept your challenge!" |
| Professor / Researcher | Informative, encouraging | "Fascinating! You obtained a [item]." |
| Pokemon Center Nurse | Warm, professional | "Welcome! We heal Pokemon to full health." |
| Pokemart Clerk | Friendly, commercial | "We carry only the finest items!" |
| Rival | Smug, competitive | "Smell ya later! I'll always be one step ahead." |

### 3. Execution

**Trainer structure** (`trainer_data.py`):
```python
Trainer(
    id="lass_dana",
    name="Dana",
    trainer_class="Lass",
    location="Route 3",
    pokemon=[TrainerPokemon(species="JIGGLYPUFF", level=13)],
    prize_money=208,
    intro_text=[
        "La-la-la!",
        "I've been practicing all week!",
        "Battle me!",
    ],
    defeat_text=["You're really strong...", "Next time I'll win!"],
    victory_text=["La-la-la! See? I told you I'd win!"],
)
```

**Building NPC text** (`texts/en/buildings.py` + `buildings.py`):
```python
# texts/en/buildings.py
BIKE_SHOP_FIRST_VISIT: list[str] = [
    "[italic]\"We're running a promotion today...[/italic]",
    "[italic]\"Here, take this BICYCLE on the house!\"[/italic]",
    "",
    "[bold cyan]You received a BICYCLE![/bold cyan]",
]
BIKE_SHOP_REPEAT: list[str] = [
    "[italic]\"Take good care of that Bicycle!\"[/italic]",
]

# buildings.py
from .texts.en import buildings as T
from .ui.formatters import write_lines

def enter_bike_shop(game_state, output):
    if game_state.game_data["story_flags"].get("received_bicycle"):
        write_lines(output, T.BIKE_SHOP_REPEAT)
        return
    write_lines(output, T.BIKE_SHOP_FIRST_VISIT)
```

**Story event flavour (one-time) in `texts/en/buildings.py`:**
```python
MOON_STONE_FOUND: list[str] = [
    "[bold yellow]★  A glittering stone catches your eye...[/bold yellow]",
    "[italic]It's a Moon Stone! It pulses with mysterious energy.[/italic]",
    "[bold yellow]You picked up a MOON STONE![/bold yellow]",
]

### 4. Rules
- Keep `intro_text` to 2–3 short lines; each line maps to a string in the `list[str]` block in `texts/en/trainer_data.py` (or similar)
- All spoken NPC dialogue lives in `texts/en/<module>.py`; the source module only calls `write_lines(output, T.CONSTANT)`
- Never spoil gym puzzle or story ahead of time in random trainer text
- Item giver NPCs should acknowledge repeat visits with a short line (story flag check)
- Use Rich italic for spoken dialogue: `[italic]"..."[/italic]`

## Examples

**Input:** "Write dialogue for Misty — gym leader intro, defeat, and victory."

**Output:**
```python
intro_text=[
    "I'm Misty, the Cerulean City Gym Leader!",
    "My policy is an all-out offensive with water-type Pokemon!",
    "Shall we battle?",
],
defeat_text=[
    "...You're too much.",
    "Okay! You win. Take the Cascade Badge.",
],
victory_text=[
    "Hah! Was that the best you could do?",
    "My water Pokemon are invincible!",
],
```

## Dependencies
- `pytemon/data/trainer_data.py` — Trainer / TrainerPokemon dataclasses
- `pytemon/buildings.py` — building handler functions
- `pytemon/texts/en/buildings.py` (and other `texts/en/` modules) — **all dialog strings live here**
- `pytemon/ui/formatters.py` — `write_lines`, `write_lines_fmt`, `write_dynamic_lines`
- Rich markup for styled output

## Error Handling
- **Text too long**: split into multiple short lines in the `list[str]` constant; each element is one beat
- **Spoiler risk**: re-read the text from a new player's perspective before committing
- **Repeat-visit missing**: always add a `story_flags` check so NPCs acknowledge they've been seen before
- **Inline NPC lines in source modules**: move the strings to `texts/en/<module>.py` and call `write_lines(output, T.CONSTANT)`
