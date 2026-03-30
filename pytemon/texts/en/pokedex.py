"""
Text constants for pytemon/pokedex.py.
"""

# ── show_pokedex ──────────────────────────────────────────────────────────────

POKEDEX_HEADER: list[str] = [
    "",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "[bold cyan]            📖 POKEDEX 📖                 [/bold cyan]",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "",
]

POKEDEX_DIVIDER: list[str] = [
    "",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "",
]

POKEDEX_NO_MATCH: list[str] = [
    "[dim]No Pokemon match this filter.[/dim]",
]

# ── show_pokedex_entry ────────────────────────────────────────────────────────

POKEDEX_ENTRY_HEADER: list[str] = [
    "",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "[bold cyan]         📖 POKEDEX ENTRY 📖               [/bold cyan]",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "",
]

POKEDEX_ENTRY_NOT_SEEN: list[str] = [
    "[dim]No data available - Pokemon not yet encountered[/dim]",
    "",
]

# Dynamic: "[red]❌ Pokemon '{name}' not found in Pokedex data[/red]"
POKEDEX_NOT_FOUND_PRE: list[str] = [""]
POKEDEX_NOT_FOUND_POST: list[str] = [""]
