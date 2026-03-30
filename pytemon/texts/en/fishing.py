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

# Dynamic: use write_lines_fmt(output, FISHING_WRONG_ROD, rod_name=...)
FISHING_WRONG_ROD: list[str] = [
    "",
    "[red]❌ You don't have a {rod_name}![/red]",
    "[dim]Buy fishing rods from the Fishing Guru.[/dim]",
    "",
]

# Dynamic: use write_lines_fmt(output, FISHING_CAST, rod_name=...)
FISHING_CAST: list[str] = [
    "",
    "[bold cyan]🎣 You cast your {rod_name} into the water...[/bold cyan]",
    "",
]

FISHING_NOTHING: list[str] = [
    "[dim]...Nothing. The water is still.[/dim]",
    "[dim]  Try again![/dim]",
    "",
]

# Dynamic: "[bold yellow]A wild {species} appeared! (Lv.{level})[/bold yellow]"
