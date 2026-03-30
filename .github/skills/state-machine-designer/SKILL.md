---
name: state-machine-designer
description: Designs and implements pending_command multi-step interaction flows in robot-pokemon. Use when adding any interaction that requires more than one player input — save names, move selection, nickname prompts, confirmation dialogs.
---

# state-machine-designer

Implements the `pending_command` state machine pattern used for all multi-step player interactions in the terminal.

## Associated Agent
`game-logic.agent.md`

## Instructions

### 1. Input
- **Flow name** — a short token string (e.g. `"nickname"`, `"move_to"`, `"heal_confirm"`)
- **Steps** — list of inputs the player must provide in sequence
- **Data carried** — extra context dict needed across steps (e.g. `{"target_pokemon": pkmn}`)
- **Completion action** — what happens when the flow finishes

### 2. How the State Machine Works

```
on_input_submitted(value)
    └── if self.pending_command → handle_pending_command(value, output)  [GameFlowMixin]
    └── else                   → process_command(value, output)          [terminal.py]

on_button_pressed(event)
    └── route to mixin method → mixin sets self.pending_command
                              → or calls self.handle_pending_command(str(btn.label), output)
```

### 3. Execution

**Step 1 — Start the flow** (from any mixin method or `process_command`):
```python
from pytemon.texts.en import buildings as T
from pytemon.ui.formatters import write_lines_fmt

def ask_for_nickname(self, pokemon: dict, output: Any) -> None:
    self.pending_command = "nickname"
    self.pending_command_data = {"target": pokemon}
    write_lines_fmt(output, T.NICKNAME_PROMPT, name=pokemon["name"])  # "Give {name} a nickname? (Enter to skip)"
```

**Step 2 — Handle the response** in `GameFlowMixin.handle_pending_command`:
```python
elif self.pending_command == "nickname":
    target = self.pending_command_data.get("target", {})
    nickname = command.strip()
    if nickname:
        target["nickname"] = nickname
        write_lines_fmt(output, T.NICKNAME_GIVEN, name=target["name"], nickname=nickname)  # "✓ Named {name} '{nickname}'!"
    else:
        write_lines_fmt(output, T.NICKNAME_SKIPPED, name=target["name"])  # "{name} kept its name."
    self.pending_command = None
    self.pending_command_data = {}
```

**Multi-step flow** (two sequential inputs):
```python
# Step 1: start
from pytemon.texts.en import pc_system as T
from pytemon.ui.formatters import write_lines
self.pending_command = "move_confirm_step1"
self.pending_command_data = {}
write_lines(output, T.MOVE_TO_PC_PROMPT)  # "Which Pokemon do you want to move to the PC? (1-6)"

# Step 2: receive index, ask confirmation
elif self.pending_command == "move_confirm_step1":
    idx = int(command.strip()) - 1
    self.pending_command = "move_confirm_step2"
    self.pending_command_data = {"index": idx}
    write_lines_fmt(output, T.MOVE_TO_PC_CONFIRM, name=party[idx]["name"])  # "Send {name} to the PC? (yes/no)"

# Step 3: confirm
elif self.pending_command == "move_confirm_step2":
    if command.strip().lower() in ("yes", "y"):
        do_transfer(...)
    self.pending_command = None
    self.pending_command_data = {}
```

### 4. Rules
- **Always** clear `self.pending_command = None` and `self.pending_command_data = {}` when a flow ends (success or cancel)
- **Never** clear `pending_command` inside `on_input_submitted` directly — always via `handle_pending_command`
- Token names must be unique — search `GameFlowMixin` before adding a new token
- Add a `"cancel"` / `"back"` branch for every flow that can be aborted

### 4. Output
- The start method (goes in the relevant mixin)
- The `elif` branch to add in `GameFlowMixin.handle_pending_command`
- Any panel calls needed (`self.show_*_panel()` / `self.hide_*_panel()`)

## Examples

**Input:** "Add a heal confirmation flow for the Pokemon Center."

**Token:** `"heal_confirm"`

**Start (BuildingMixin):**
```python
# texts/en/buildings.py:
# HEAL_CONFIRM_PROMPT: list[str] = [
#     "[cyan]Heal all your Pokémon? ([bold]yes[/bold]/no)[/cyan]",
# ]

from pytemon.texts.en import buildings as T
from pytemon.ui.formatters import write_lines
self.pending_command = "heal_confirm"
self.pending_command_data = {}
write_lines(output, T.HEAL_CONFIRM_PROMPT)
```

**Handler (GameFlowMixin):**
```python
from pytemon.buildings import heal_all_pokemon
from pytemon.texts.en import buildings as T
from pytemon.ui.formatters import write_lines

elif self.pending_command == "heal_confirm":
    if command.strip().lower() in ("yes", "y", ""):
        heal_all_pokemon(self.game_state, output)
    else:
        write_lines(output, T.HEAL_CONFIRM_DECLINED)   # "Come back when you need rest."
    self.pending_command = None
    self.pending_command_data = {}
```

## Dependencies
- `pytemon/ui/game_flow_mixin.py` — `handle_pending_command` dispatcher
- `pytemon/terminal.py` — `on_input_submitted`, `on_button_pressed`
- `pytemon/ui/panel_mixin.py` — panel show/hide calls

## Error Handling
- **Flow gets stuck**: ensure every code path in `handle_pending_command` clears `pending_command`; add a universal `"cancel"` escape
- **Wrong handler fires**: token names must be unique; grep for the token string before using it
