---
name: panel-designer
description: Creates new UI panels for the robot-pokemon Textual TUI. Use when adding a new overlay, dialog, or display section — generates the widget definition in compose(), the show/hide methods in PanelMixin, and the TCSS style block.
---

# panel-designer

Automates creating new UI panels for the Pokémon terminal game using Textual and Rich. Ensures panels are consistent with the mixin architecture and existing style conventions.

## Associated Agent
`tui-specialist.agent.md`

## Instructions

### 1. Input
Gather from the user or task description:
- **Panel name** — e.g. `nickname`, `fossil-revival`, `bill-pc`
- **Purpose** — what it displays or collects (e.g. "ask player for a Pokemon nickname")
- **Widgets needed** — Input, Button(s), Static labels, RichLog, etc.
- **Trigger** — which command or event opens it

### 2. Validation
- Check `terminal.py` `compose()` for an existing ID clash (e.g. `#nickname-panel` already defined)
- Check `ui/panel_mixin.py` for an existing `show_<name>_panel` method
- Widget IDs must be unique across the whole compose tree

### 3. Execution

**Step 1** — Add the widget block inside `compose()` in `terminal.py`:
```python
with Vertical(id="nickname-panel", classes="overlay hidden"):
    yield Static("What will you name this Pokémon?", id="nickname-label")
    yield Input(placeholder="Enter nickname...", id="nickname-input")
    yield Button("Confirm", id="confirm-nickname")
    yield Button("Skip", id="skip-nickname")
```

**Step 2** — Add show/hide methods to `ui/panel_mixin.py`:
```python
def show_nickname_panel(self) -> None:
    self.query_one("#nickname-panel").display = True
    self.query_one("#nickname-input", Input).focus()

def hide_nickname_panel(self) -> None:
    self.query_one("#nickname-panel").display = False
```

**Step 3** — Add TCSS in `terminal.tcss`:
```css
#nickname-panel {
    layer: overlay;
    border: double $accent;
    padding: 1 2;
    width: 50;
    height: auto;
    align: center middle;
}
```

**Step 4** — Wire into `pending_command` if the panel collects input (see state-machine-designer skill).

**Step 5** — Route button presses in `on_button_pressed()` in `terminal.py`:
```python
elif button_id == "confirm-nickname":
    self.handle_pending_command(str(self.query_one("#nickname-input", Input).value), output)
elif button_id == "skip-nickname":
    self.hide_nickname_panel()
    self.pending_command = None
```

### 4. Output
- Confirm which files were modified
- Show a preview of the new panel in the compose tree
- Suggest the `pending_command` token to use if input is needed

## Examples

**Input:** "Create a panel to confirm healing at the Pokemon Center."

**Output additions:**
```python
# terminal.py compose()
with Vertical(id="heal-confirm-panel", classes="overlay hidden"):
    yield Static("Heal your Pokémon? (₽0)", id="heal-confirm-label")
    yield Button("Yes", id="confirm-heal")
    yield Button("No", id="cancel-heal")

# ui/panel_mixin.py
def show_heal_confirm_panel(self) -> None:
    self.query_one("#heal-confirm-panel").display = True

def hide_heal_confirm_panel(self) -> None:
    self.query_one("#heal-confirm-panel").display = False
```

## Dependencies
- `PokemonLibrary/terminal.py` — compose tree
- `PokemonLibrary/terminal.tcss` — styles
- `PokemonLibrary/ui/panel_mixin.py` — show/hide methods
- `PokemonLibrary/ui/game_flow_mixin.py` — if using `pending_command`

## Error Handling
- **ID clash**: rename with a more specific prefix (e.g. `#center-heal-panel` instead of `#heal-panel`)
- **Panel not visible after show**: check that the parent container is not itself hidden; check `display` vs `visible` vs CSS `hidden` class
- **Input not focusable**: ensure panel `display = True` is set before calling `.focus()`
