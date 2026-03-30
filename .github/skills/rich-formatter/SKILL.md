---
name: rich-formatter
description: Writes Rich markup strings and Rich Table/Panel objects for the robot-pokemon TUI output. Use when formatting terminal output, building HP bars, status tables, Pokedex entries, or any coloured/styled text written to a RichLog.
---

# rich-formatter

Produces well-formatted Rich markup for game output. Ensures consistent colour conventions, table layouts, and styled text across the game.

## Associated Agent
`tui-specialist.agent.md`

## Instructions

### 1. Input
- **What to display** — item name, Pokemon stat block, HP bar, menu list, etc.
- **Target widget** — `RichLog` ID (usually `#output` or `#battle-log`)
- **Data available** — the Python dict/object that holds the values

### 2. Colour Conventions (always follow these)

| Colour | Use for |
|---|---|
| `[green]` / `[bold green]` | Success, heal, gain, caught |
| `[red]` / `[bold red]` | Damage, faint, error |
| `[yellow]` / `[bold yellow]` | Items, warnings, money, level-up |
| `[cyan]` | Info, location descriptions, prompts |
| `[magenta]` | Pokemon names, special events |
| `[dim]` | Already seen / inactive hints |
| `[bold]` | Section headers, Pokemon names in battle |
| `[italic]` | Flavour text, NPC dialogue |

### 3. Common Patterns

> **Rule:** Any sequence of 2+ related static lines belongs in `texts/en/<module>.py` and is
> emitted via `write_lines(output, T.CONSTANT)`. Placeholder-based dynamic lines should use
> `write_lines_fmt(...)` or `write_dynamic_lines(...)` with `texts/en/` constants.

**HP bar:**
```python
# ui/formatters.py
def format_hp_bar(current: int, max_hp: int, width: int = 20) -> str:
    ratio = current / max_hp if max_hp > 0 else 0
    filled = int(ratio * width)
    bar = "█" * filled + "░" * (width - filled)
    colour = "green" if ratio > 0.5 else ("yellow" if ratio > 0.25 else "red")
    return f"[{colour}]{bar}[/{colour}] {current}/{max_hp}"
```

**Pokemon status line:**
```python
# texts/en/displays.py:
# PARTY_STATUS_LINE: list[str] = [
#     "[bold magenta]{name}[/bold magenta]  Lv.[cyan]{level}[/cyan]  HP: {hp_bar}",
# ]
from pytemon.texts.en import displays as T
from pytemon.ui.formatters import write_lines_fmt
write_lines_fmt(
    output,
    T.PARTY_STATUS_LINE,
    name=pkmn["name"],
    level=pkmn["level"],
    hp_bar=format_hp_bar(pkmn["hp"], pkmn["max_hp"]),
)
```

**Rich Table (party view):**
```python
from rich.table import Table
table = Table(title="Your Party", border_style="cyan")
table.add_column("Name", style="magenta bold")
table.add_column("Level", justify="right")
table.add_column("HP", justify="right")
table.add_column("Status")
for p in party:
    status = f"[red]{p.get('status', '')}[/red]" if p.get("status") else "[green]OK[/green]"
    table.add_row(p["name"], str(p["level"]), f"{p['hp']}/{p['max_hp']}", status)
output.write(table)
```

**Rich Panel (location header):**
```python
from rich.panel import Panel
output.write(Panel(f"[bold]{location.name}[/bold]\n[italic]{location.description}[/italic]",
                   border_style="cyan", expand=False))
```

**Money / reward:**
```python
from pytemon.texts.en import battle_ui as T
from pytemon.ui.formatters import write_lines_fmt
write_lines_fmt(output, T.PRIZE_MONEY_WON, prize_money=prize_money)
```

**Section separator:**
```python
from pytemon.texts.en import displays as T
from pytemon.ui.formatters import write_lines
write_lines(output, T.SECTION_SEPARATOR)
```

### 4. Output
- Working Rich markup strings or `Table`/`Panel` objects
- Static multi-line blocks added to the correct `texts/en/<module>.py` constant and called via `write_lines()`
- Placement of dynamic single-line helpers in `ui/displays.py` or the relevant mixin

## Examples

**Input:** "Format the Pokedex entry for a caught Pokemon."

**Output:**
```python
output.write(Panel(
    f"[bold magenta]#{pkmn['number']:03d}  {pkmn['name']}[/bold magenta]\n"
    f"[cyan]Type:[/cyan] {' / '.join(pkmn['types'])}\n"
    f"[italic]{pkmn.get('description', 'No data.')}[/italic]",
    title="[bold]Pokédex[/bold]", border_style="yellow"
))
```

## Dependencies
- `rich.table.Table`, `rich.panel.Panel`, `rich.text.Text`
- `pytemon/ui/formatters.py` — `format_hp_bar`, `write_lines`, `write_lines_fmt`, `write_dynamic_lines`
- `pytemon/texts/en/<module>.py` — all static/semi-static text constants
- `pytemon/ui/displays.py` — display functions that call formatters

## Error Handling
- **RichLog not accepting Table objects**: ensure `RichLog(markup=True)` in compose
- **Markup tag mismatch**: every `[tag]` must have a matching `[/tag]`; use `[/]` to close all
- **EN DASH in strings** (`–`): replace with plain hyphen (`-`) to avoid ruff RUF003 in comments
