---
name: css-styler
description: Styles Textual widgets in terminal.tcss for the robot-pokemon TUI. Use when a panel looks wrong, needs colour/border/layout adjustments, or when adding new TCSS rules for new widgets.
---

# css-styler

Applies and fixes TCSS (Textual CSS) styles in `terminal.tcss`. Ensures visual consistency across all panels, overlays, and widgets.

## Associated Agent
`tui-specialist.agent.md`

## Instructions

### 1. Input
- **Widget ID or class** being styled (e.g. `#nickname-panel`, `.overlay`)
- **Desired appearance** — border style, colours, dimensions, alignment
- **Problem description** if fixing existing styles (e.g. "panel overflows the screen")

### 2. Validation
- Open `terminal.tcss` and check if a rule for the target ID/class already exists
- Check `terminal.py` `compose()` to confirm the widget ID/class is actually applied
- Textual uses `$primary`, `$accent`, `$surface`, `$panel`, `$warning`, `$error`, `$success` CSS variables — prefer these over hardcoded colours

### 3. Execution

**Common patterns:**

```css
/* Full-screen overlay */
#my-panel {
    layer: overlay;
    width: 100%;
    height: 100%;
    background: $surface 80%;
    align: center middle;
}

/* Centred dialog box */
#my-dialog {
    layer: overlay;
    width: 60;
    height: auto;
    border: double $accent;
    padding: 1 2;
    align: center middle;
}

/* Scrollable log area */
#output {
    height: 1fr;
    border: solid $primary;
    scrollbar-gutter: stable;
}

/* HP bar colours */
.hp-high  { color: $success; }
.hp-mid   { color: $warning; }
.hp-low   { color: $error; }
```

**Show/hide pattern** — use `display` property, not `visibility`:
```css
.hidden { display: none; }
```
```python
# In PanelMixin — toggle display directly, not the class
self.query_one("#my-panel").display = True
```

### 4. Output
- Show the new/modified TCSS block
- Note any widget property that must be set in Python to complement the CSS (e.g. `display = True`)

## Examples

**Input:** "The battle panel overlaps the main log and is too wide."

**Fix:**
```css
#battle-panel {
    layer: overlay;
    width: 70%;
    max-width: 80;
    height: auto;
    border: heavy $warning;
    padding: 1 2;
    align: center middle;
    offset: 15% 10%;
}
```

## Dependencies
- `pytemon/terminal.tcss` — all styles live here
- `pytemon/terminal.py` — widget IDs and classes defined in `compose()`
- Textual CSS reference: https://textual.textualize.io/guide/CSS/

## Error Handling
- **Style not applying**: confirm the widget ID in `compose()` matches exactly (case-sensitive)
- **Layer overlap issues**: ensure overlays use `layer: overlay` and the app defines `LAYERS = ["default", "overlay"]`
- **Height: auto not working**: some Textual containers require explicit height; try `height: 1fr` or a fixed value
