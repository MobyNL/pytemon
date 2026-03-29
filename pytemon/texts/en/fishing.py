"""
Text constants for pytemon/fishing.py.
"""

# ── start_fishing ─────────────────────────────────────────────────────────────

FISHING_NO_POKEMON: list[str] = [
    "",
    "[yellow]⚠ You can't fish without Pokemon![/yellow]",
    "[dim]Get a starter from Professor Oak first.[/dim]",
    "",
]

FISHING_WRONG_LOCATION: list[str] = [
    "",
    "[yellow]⚠ You can't fish here![/yellow]",
    "[dim]Fish near water routes, lakes, or coastal areas.[/dim]",
    "",
]

FISHING_NO_ROD: list[str] = [
    "",
    "[yellow]⚠ You don't have a fishing rod![/yellow]",
    "[dim]Obtain a fishing rod to catch water Pokemon.[/dim]",
    "[dim]  • Old Rod — basic, found early in the game[/dim]",
    "[dim]  • Good Rod — better variety[/dim]",
    "[dim]  • Super Rod — rare catches[/dim]",
    "",
]

# Dynamic: "[red]❌ You don't have a {rod_name}![/red]"
FISHING_WRONG_ROD: list[str] = [
    "",
    # dynamic line
    "[dim]Buy fishing rods from the Fishing Guru.[/dim]",
    "",
]

# Dynamic: "[bold cyan]🎣 You cast your {rod_name} into the water...[/bold cyan]"
FISHING_CAST_POST: list[str] = [
    "",
]

FISHING_NOTHING: list[str] = [
    "[dim]...Nothing. The water is still.[/dim]",
    "[dim]  Try again![/dim]",
    "",
]

# Dynamic: "[bold yellow]A wild {species} appeared! (Lv.{level})[/bold yellow]"
