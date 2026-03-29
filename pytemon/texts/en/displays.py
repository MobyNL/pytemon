"""
Text constants for pytemon/ui/displays.py.
"""

# ── activate_pikachu_mode ─────────────────────────────────────────────────────

PIKACHU_MODE_NOTHING: list[str] = [
    "",
    "[dim]...Nothing happened.[/dim]",
    "",
]

PIKACHU_MODE_ALREADY: list[str] = [
    "",
    "[yellow]You're already running late! Better hurry to the lab![/yellow]",
    "",
]

PIKACHU_MODE_ACTIVATED: list[str] = [
    "",
    "[bold yellow]═══════════════════════════════════════════[/bold yellow]",
    "[bold yellow]⏰ Oh no! You overslept! ⏰[/bold yellow]",
    "[bold yellow]═══════════════════════════════════════════[/bold yellow]",
    "",
    "[yellow]You rush downstairs and run to Professor Oak's Lab![/yellow]",
    "[yellow]By the time you arrive, the other trainers have already chosen their Pokemon![/yellow]",
    "",
    "[dim]A special encounter awaits you...[/dim]",
    "",
]

# ── show_party ────────────────────────────────────────────────────────────────

PARTY_HEADER: list[str] = [
    "",
    "[bold cyan]👥 Your Pokemon Party[/bold cyan]",
    "",
]

PARTY_EMPTY: list[str] = [
    "[dim]You don't have any Pokemon yet![/dim]",
    "",
]

# ── show_bag (delegates to items.py) — see texts/en/items.py ─────────────────

# ── show_help ─────────────────────────────────────────────────────────────────

HELP_HEADER: list[str] = [
    "",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "[bold cyan]           📋 HELP — COMMANDS 📋           [/bold cyan]",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "",
]

# ── show_status ───────────────────────────────────────────────────────────────

STATUS_HEADER: list[str] = [
    "",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "[bold cyan]           📊 TRAINER STATUS 📊            [/bold cyan]",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "",
]
