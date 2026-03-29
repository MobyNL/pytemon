"""
Text constants for pytemon/battle/battle_ui.py.

Note: most battle_ui text is already returned as list[str] from get_*_lines()
functions so the battle_ui module is already well-structured. These constants
cover purely static blocks (headers/footers) that are repeated verbatim.
"""

# ── Wild encounter borders ────────────────────────────────────────────────────
# (dynamic content like Pokemon name/level stays inline via get_battle_start_lines)

WILD_ENCOUNTER_BORDER: list[str] = [
    "",
    "[bold red]═══════════════════════════════════════════[/bold red]",
    # dynamic: f"[bold red]⚔️  A wild {name} appeared! (Lv. {level})  ⚔️[/bold red]"
    "[bold red]═══════════════════════════════════════════[/bold red]",
    "",
]

SAFARI_ENCOUNTER_BORDER: list[str] = [
    "",
    "[bold green]═══════════════════════════════════════════[/bold green]",
    # dynamic: f"[bold green]🦁  A wild {name} appeared! (Lv. {level})  🦁[/bold green]"
    "[bold green]═══════════════════════════════════════════[/bold green]",
    "",
    "[dim]You're in the Safari Zone — you can't battle here![/dim]",
    "[dim]Use Bait, Rock, or throw a Safari Ball![/dim]",
    "",
]

TRAINER_BATTLE_HEADER: list[str] = [
    "",
    "[bold yellow]═══════════════════════════════════════════[/bold yellow]",
    "[bold yellow]⚔️  TRAINER BATTLE!  ⚔️[/bold yellow]",
    "[bold yellow]═══════════════════════════════════════════[/bold yellow]",
    "",
]

GYM_BATTLE_HEADER: list[str] = [
    "",
    "[bold magenta]═══════════════════════════════════════════[/bold magenta]",
    "[bold magenta]⚔️  GYM LEADER BATTLE!  ⚔️[/bold magenta]",
    "[bold magenta]═══════════════════════════════════════════[/bold magenta]",
    "",
]

# ── show_battle_options ───────────────────────────────────────────────────────

BATTLE_OPTIONS_HEADER: list[str] = [
    "",
    "[bold]What will you do?[/bold]",
    "",
    "  [green]Fight[/green]    — Choose a move",
    "  [cyan]Bag[/cyan]      — Use an item",
    "  [yellow]Pokemon[/yellow]  — Switch Pokemon",
    "  [red]Run[/red]      — Escape from battle",
    "",
]

SAFARI_BATTLE_OPTIONS: list[str] = [
    "",
    "[bold]Safari Zone — what will you do?[/bold]",
    "",
    "  [green]Ball[/green]   — Throw a Safari Ball",
    "  [yellow]Bait[/yellow]   — Make the Pokemon less likely to flee",
    "  [cyan]Rock[/cyan]   — Make the Pokemon angrier (easier to catch, more likely to flee)",
    "  [red]Run[/red]    — Leave the Safari Zone",
    "",
]

# ── victory / defeat ──────────────────────────────────────────────────────────

BATTLE_VICTORY_HEADER: list[str] = [
    "",
    "[bold green]═══════════════════════════════════════════[/bold green]",
    "[bold green]🏆  VICTORY!  🏆[/bold green]",
    "[bold green]═══════════════════════════════════════════[/bold green]",
    "",
]

BATTLE_DEFEAT_HEADER: list[str] = [
    "",
    "[bold red]═══════════════════════════════════════════[/bold red]",
    "[bold red]💀  DEFEATED...  💀[/bold red]",
    "[bold red]═══════════════════════════════════════════[/bold red]",
    "",
]

TRAINER_VICTORY_HEADER: list[str] = [
    "",
    "[bold green]═══════════════════════════════════════════[/bold green]",
    "[bold green]🏆  TRAINER DEFEATED!  🏆[/bold green]",
    "[bold green]═══════════════════════════════════════════[/bold green]",
    "",
]

# ── catch result ──────────────────────────────────────────────────────────────

CATCH_SUCCESS: list[str] = [
    "",
    "[bold green]🎉 Gotcha! Pokemon was caught![/bold green]",
    "",
]

CATCH_FAILED: list[str] = [
    "",
    "[red]Oh no! The Pokemon broke free![/red]",
    "",
]

CATCH_FLED: list[str] = [
    "",
    "[yellow]The wild Pokemon fled![/yellow]",
    "",
]
