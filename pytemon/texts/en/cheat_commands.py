"""
Text constants for pytemon/cheat_commands.py.
"""

# ── check_secret_phrase ──────────────────────────────────────────────────────

CHEAT_ACTIVATED: list[str] = [
    "",
    "[bold yellow]═══════════════════════════════════════════[/bold yellow]",
    "[bold yellow]    🎮 CHEAT MODE ACTIVATED 🎮[/bold yellow]",
    "[bold yellow]═══════════════════════════════════════════[/bold yellow]",
    "",
    "[cyan]Developer mode enabled![/cyan]",
    "",
    "[bold]Available cheat commands:[/bold]",
    "  [green]cheat battle <pokemon> <level>[/green]  - Battle a specific Pokemon",
    "  [green]cheat trainer <id>[/green]              - Battle a specific trainer",
    "  [green]cheat warp <location>[/green]           - Teleport to any location",
    "  [green]cheat add <pokemon> <level>[/green]     - Add Pokemon to party",
    "  [green]cheat remove <pokemon/slot>[/green]     - Remove Pokemon from party",
    "  [green]cheat level <pokemon/slot> <lvl>[/green] - Set Pokemon level",
    "  [green]cheat evolve <pokemon/slot>[/green]     - Force Pokemon evolution",
    "  [green]cheat win[/green]                       - Instantly win current battle",
    "  [green]cheat lose[/green]                      - Instantly lose current battle",
    "  [green]cheat faint <pokemon/slot>[/green]      - Make a party Pokemon faint",
    "  [green]cheat learn <pokemon/slot> <move>[/green] - Teach any move to a Pokemon",
    "  [green]cheat list pokemon[/green]              - List all Pokemon",
    "  [green]cheat list trainers[/green]             - List all trainers",
    "  [green]cheat list locations[/green]            - List all locations",
    "  [green]cheat give <item> <qty>[/green]         - Add items to inventory",
    "  [green]cheat money <amount>[/green]            - Add money",
    "",
    "[dim]Type 'I am not professor Oak' to disable cheat mode[/dim]",
    "",
]

CHEAT_ALREADY_ENABLED: list[str] = [
    "",
    "[yellow]⚠ Cheat mode is already enabled[/yellow]",
    "",
]

CHEAT_DEACTIVATED: list[str] = [
    "",
    "[bold yellow]🎮 CHEAT MODE DEACTIVATED 🎮[/bold yellow]",
    "",
]

CHEAT_ALREADY_DISABLED: list[str] = [
    "",
    "[yellow]⚠ Cheat mode is already disabled[/yellow]",
    "",
]

# ── show_cheat_help ──────────────────────────────────────────────────────────

CHEAT_HELP: list[str] = [
    "",
    "[bold yellow]🎮 Cheat Commands:[/bold yellow]",
    "",
    "  [green]cheat battle <pokemon> <level>[/green]  - Battle a specific Pokemon",
    "  [green]cheat trainer <id>[/green]              - Battle a specific trainer",
    "  [green]cheat win[/green]                       - Instantly win current battle",
    "  [green]cheat lose[/green]                      - Instantly lose current battle",
    "  [green]cheat faint <pokemon/slot>[/green]      - Make a party Pokemon faint",
    "  [green]cheat learn <pokemon/slot> <move>[/green] - Teach any move to a Pokemon",
    "  [green]cheat warp <location>[/green]           - Teleport to any location",
    "  [green]cheat add <pokemon> <level>[/green]     - Add Pokemon to party",
    "  [green]cheat remove <pokemon/slot>[/green]     - Remove Pokemon from party",
    "  [green]cheat level <pokemon/slot> <lvl>[/green] - Set Pokemon level",
    "  [green]cheat evolve <pokemon/slot>[/green]     - Force Pokemon evolution",
    "  [green]cheat list pokemon[/green]              - List all Pokemon",
    "  [green]cheat list trainers[/green]             - List all trainers",
    "  [green]cheat list locations[/green]            - List all locations",
    "  [green]cheat give <item> <qty>[/green]         - Add items to inventory",
    "  [green]cheat money <amount>[/green]            - Add money",
    "",
]

# ── list_pokemon ─────────────────────────────────────────────────────────────

LIST_POKEMON_HEADER: list[str] = [
    "",
    "[bold cyan]Available Pokemon:[/bold cyan]",
    "",
]

LIST_POKEMON_FOOTER: list[str] = [
    "",
    "[dim]Usage: cheat battle <pokemon_name> <level>[/dim]",
    "",
]

# ── list_trainers ─────────────────────────────────────────────────────────────

LIST_TRAINERS_HEADER: list[str] = [
    "",
    "[bold cyan]Available Trainers:[/bold cyan]",
    "",
]

LIST_TRAINERS_FOOTER: list[str] = [
    "[dim]Usage: cheat trainer <trainer_id>[/dim]",
    "",
]

# ── list_locations ────────────────────────────────────────────────────────────

LIST_LOCATIONS_HEADER: list[str] = [
    "",
    "[bold cyan]Available Locations:[/bold cyan]",
    "",
]

LIST_LOCATIONS_FOOTER: list[str] = [
    "",
    "[dim]Usage: cheat warp <location_name>[/dim]",
    "",
]

# ── warp_to_location ─────────────────────────────────────────────────────────
# Dynamic lines — use write_lines_fmt(output, WARP_SUCCESS, location=name)

WARP_NOT_FOUND: list[str] = [
    "",
    "[red]❌ Location not found: {location}[/red]",
    "[dim]Use 'cheat list locations' to see all locations[/dim]",
    "",
]

WARP_SUCCESS: list[str] = [
    "",
    "[bold yellow]✨ *WHOOSH* ✨[/bold yellow]",
    "",
    "[bold green]Warped to {location}![/bold green]",
    "",
]

# ── trigger_cheat_battle / trigger_cheat_trainer_battle ──────────────────────

CHEAT_BATTLE_SPAWN: list[str] = [
    "",
    "[bold yellow]🎮 [CHEAT MODE] Spawning battle...[/bold yellow]",
]

CHEAT_TRAINER_BATTLE_SPAWN: list[str] = [
    "",
    "[bold yellow]🎮 [CHEAT MODE] Spawning trainer battle...[/bold yellow]",
    "",
]
