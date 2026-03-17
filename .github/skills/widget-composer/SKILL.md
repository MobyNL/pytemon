---
name: widget-composer
description: Builds complex Textual widget trees for the robot-pokemon TUI. Use when designing the layout of a new screen section, composing nested containers, or refactoring an existing layout that is hard to maintain.
---

# widget-composer

Designs and implements Textual widget compositions — nested containers, scrollable areas, grids, and multi-column layouts — that integrate cleanly with the existing compose tree in `terminal.py`.

## Associated Agent
`tui-specialist.agent.md`

## Instructions

### 1. Input
- **Section name** — what area of the screen is being designed
- **Contents** — what widgets go inside (log, input, buttons, labels, tables)
- **Layout type** — vertical, horizontal, grid, or scrollable
- **Sizing** — fixed, `1fr`, auto, percentage

### 2. Validation
- Scan `terminal.py` `compose()` for the insertion point (before `yield Footer()`, inside a container, etc.)
- All widget IDs must be globally unique in the compose tree
- Use `Vertical`, `Horizontal`, `ScrollableContainer` from `textual.containers`
- Use `Grid` from `textual.widgets` for tabular layouts

### 3. Execution

**Main layout skeleton:**
```python
def compose(self) -> ComposeResult:
    yield Header()
    with Horizontal(id="main-body"):
        with Vertical(id="left-pane"):
            yield RichLog(id="output", markup=True, wrap=True)
            yield Input(id="command-input", placeholder="Enter command...")
        with Vertical(id="right-pane", classes="hidden"):
            yield Static(id="status-display")
            yield RichLog(id="battle-log", markup=True)
    yield Footer()
    # Overlay panels (hidden by default)
    with Vertical(id="modal-panel", classes="overlay hidden"):
        yield Static(id="modal-title")
        yield Button("OK", id="modal-ok")
```

**Scrollable item list:**
```python
with ScrollableContainer(id="item-list"):
    for item_name in items:
        yield Button(item_name, id=f"item-{item_name.lower().replace(' ', '-')}")
```

**Two-column battle layout:**
```python
with Horizontal(id="battle-hud"):
    with Vertical(id="player-side"):
        yield Static(id="player-name")
        yield Static(id="player-hp-bar")
    with Vertical(id="enemy-side"):
        yield Static(id="enemy-name")
        yield Static(id="enemy-hp-bar")
```

### 4. Output
- Full `compose()` snippet with the new section inserted in the correct position
- List of new widget IDs to register in PanelMixin or TCSS

## Examples

**Input:** "Add a 4-button move selection grid for battle."

**Output:**
```python
with Grid(id="move-grid", classes="hidden"):
    yield Button("---", id="move-btn-0", classes="move-btn")
    yield Button("---", id="move-btn-1", classes="move-btn")
    yield Button("---", id="move-btn-2", classes="move-btn")
    yield Button("---", id="move-btn-3", classes="move-btn")
```
```css
/* terminal.tcss */
#move-grid { grid-size: 2 2; height: 6; }
.move-btn  { width: 1fr; }
```

## Dependencies
- `PokemonLibrary/terminal.py` — compose tree lives here
- `PokemonLibrary/terminal.tcss` — layout sizing and positioning
- `textual.containers` — `Vertical`, `Horizontal`, `ScrollableContainer`
- `textual.widgets` — `Grid`, `Static`, `Input`, `Button`, `RichLog`

## Error Handling
- **Layout overflow**: add `overflow: hidden auto` in TCSS or use `ScrollableContainer`
- **Widget not found by `query_one`**: double-check the ID string matches compose exactly
- **Grid not sizing correctly**: set explicit `grid-size: <cols> <rows>` in TCSS
