---
name: animation-creator
description: Adds typewriter text animations and timed reveal sequences to the robot-pokemon TUI. Use when adding dialogue reveal, battle intro text, or any text that should appear character-by-character or line-by-line.
---

# animation-creator

Implements typewriter and reveal animations using `ui/text_animation.py`. Keeps animations consistent, cancellable, and non-blocking.

## Associated Agent
`tui-specialist.agent.md`

## Instructions

### 1. Input
- **Text to animate** — the string or list of lines to reveal
- **Speed** — characters-per-second or delay-per-line (default: fast for battle, slow for story)
- **Context** — which panel/output widget receives the text
- **Cancellable?** — should pressing a key skip to the end

### 2. Validation
- Check `ui/text_animation.py` for existing animation helpers before writing new ones
- Never use `time.sleep()` in Textual — animations must use `asyncio.sleep()` or `self.set_timer()`
- Animation coroutines must be called with `self.call_later()` or `asyncio.create_task()` from within Textual event handlers

### 3. Execution

**Typewriter on a RichLog:**
```python
# ui/text_animation.py helper (add if not present)
async def typewriter(output: RichLog, text: str, delay: float = 0.03) -> None:
    """Reveal text character by character."""
    buf = ""
    for ch in text:
        buf += ch
        output.clear()
        output.write(buf)
        await asyncio.sleep(delay)

# Call from a Textual async method:
async def show_intro_text(self) -> None:
    output = self.query_one("#output", RichLog)
    await typewriter(output, "[bold yellow]A wild PIDGEY appeared![/bold yellow]")
```

**Line-by-line reveal:**
```python
async def reveal_lines(output: RichLog, lines: list[str], delay: float = 0.4) -> None:
    """Print lines one at a time with a pause between each."""
    for line in lines:
        output.write(line)
        await asyncio.sleep(delay)
```

**Skip-to-end pattern:**
```python
self._animating = True

async def animate(self) -> None:
    for ch in long_text:
        if not self._animating:
            output.write(long_text)  # dump remainder
            break
        # ... append ch ...
        await asyncio.sleep(0.02)
    self._animating = False

def on_key(self, event: Key) -> None:
    if event.key in ("enter", "space") and self._animating:
        self._animating = False  # triggers skip
```

### 4. Output
- Add helper functions to `ui/text_animation.py`
- Show the call site in the mixin or terminal method

## Examples

**Input:** "Animate the 'You received [item]!' message after a story event."

**Output:**
```python
# texts/en/buildings.py
BICYCLE_RECEIVED: list[str] = [
    "",
    "[bold cyan]★  The researcher hands you something...[/bold cyan]",
    "[bold yellow]You received a BICYCLE![/bold yellow]",
    "",
]

# In BuildingMixin or buildings.py callback:
from pytemon.texts.en import buildings as T
await reveal_lines(output, T.BICYCLE_RECEIVED, delay=0.5)
```

## Dependencies
- `pytemon/ui/text_animation.py` — animation helpers (excluded from coverage)
- `asyncio` — required for non-blocking delays
- Textual's async event system (`async def on_*`, `self.call_later()`)

## Error Handling
- **Frozen UI**: ensure all delays use `await asyncio.sleep()`, never `time.sleep()`
- **Animation not cancelling**: set a cancellation flag (`self._animating = False`) before awaiting
- **Text appears all at once**: confirm the coroutine is `await`ed, not just called
