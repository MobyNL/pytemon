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
# Dynamic lines — use write_dynamic_lines(output, WARP_SUCCESS, {"location": name})
#                 or   write_lines_fmt(output, WARP_SUCCESS, location=name)

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

# ── Generic dynamic status blocks ────────────────────────────────────────────

CHEAT_ITEM_RECEIVED: list[str] = [
    "",
    "[bold green]✓ Received {quantity}x {item_name}![/bold green]",
    "",
]

CHEAT_MONEY_RECEIVED: list[str] = [
    "",
    "[bold green]✓ Received ₽{amount}![/bold green]",
    "  [dim]Total money: ₽{total_money}[/dim]",
    "",
]

CHEAT_POKEMON_NOT_FOUND: list[str] = [
    "",
    "[red]❌ Pokemon not found: {pokemon_name}[/red]",
    "[dim]Use 'cheat list pokemon' to see all Pokemon[/dim]",
    "",
]

CHEAT_ALL_FAINTED_FOR_BATTLE: list[str] = [
    "",
    "[red]❌ All your Pokemon have fainted! You need at least one Pokemon to battle.[/red]",
    "",
]

CHEAT_TRAINER_NOT_FOUND: list[str] = [
    "",
    "[red]❌ Trainer not found: {trainer_id}[/red]",
    "[dim]Use 'cheat list trainers' to see all trainers[/dim]",
    "",
]

CHEAT_PARTY_FULL: list[str] = [
    "",
    "[red]❌ Party is full! Remove a Pokemon first.[/red]",
    "",
]

CHEAT_PARTY_ADD_SUCCESS: list[str] = [
    "",
    "[bold green]✓ Added {pokemon_name} (Lv.{level}) to party![/bold green]",
    "  [dim]Party size: {party_size}/6[/dim]",
    "",
]

CHEAT_PARTY_EMPTY: list[str] = [
    "",
    "[red]❌ Your party is empty![/red]",
    "",
]

CHEAT_PARTY_MEMBER_NOT_FOUND: list[str] = [
    "",
    "[red]❌ Pokemon not found in party: {identifier}[/red]",
    "[dim]Use 'party' to see your Pokemon[/dim]",
    "",
]

CHEAT_PARTY_CANNOT_REMOVE_LAST: list[str] = [
    "",
    "[red]❌ Can't remove your last Pokemon![/red]",
    "",
]

CHEAT_PARTY_REMOVE_SUCCESS: list[str] = [
    "",
    "[bold yellow]Removed {pokemon_name} (Lv.{pokemon_level}) from party[/bold yellow]",
    "  [dim]Party size: {party_size}/6[/dim]",
    "",
]

CHEAT_LEVEL_OUT_OF_RANGE: list[str] = [
    "",
    "[red]❌ Level must be between 1 and 100[/red]",
    "",
]

CHEAT_LEVEL_UP_SUCCESS: list[str] = [
    "",
    "[bold green]✓ {pokemon_name} leveled up![/bold green]",
    "  Level: {old_level} → {new_level}",
    "  [dim]HP: {max_hp} | Stats recalculated[/dim]",
    "",
]

CHEAT_EVOLUTION_DATA_NOT_FOUND: list[str] = [
    "",
    "[red]❌ Can't find evolution data for {pokemon_name}[/red]",
    "",
]

CHEAT_DOES_NOT_EVOLVE: list[str] = [
    "",
    "[yellow]⚠ {pokemon_name} doesn't evolve[/yellow]",
    "",
]

CHEAT_EVOLUTION_DATA_ERROR: list[str] = [
    "",
    "[red]❌ Evolution data error for {pokemon_name}[/red]",
    "",
]

CHEAT_EVOLVED_FORM_NOT_FOUND: list[str] = [
    "",
    "[red]❌ Evolved form not found in data: {evolved_form}[/red]",
    "",
]

CHEAT_POKEMON_NOT_FOUND_IN_PARTY: list[str] = [
    "",
    "[red]❌ Pokemon not found: {identifier}[/red]",
    "[dim]Use 'party' to see your Pokemon[/dim]",
    "",
]

CHEAT_ALREADY_FAINTED: list[str] = [
    "",
    "[yellow]⚠ {pokemon_name} is already fainted![/yellow]",
    "",
]

CHEAT_CANNOT_FAINT_LAST_HEALTHY: list[str] = [
    "",
    "[red]❌ Can't faint your last healthy Pokemon![/red]",
    "",
]

CHEAT_FAINTED_SUCCESS: list[str] = [
    "",
    "[bold yellow]🎮 [CHEAT MODE] {pokemon_name} fainted![/bold yellow]",
    "",
]

CHEAT_MOVE_NOT_FOUND: list[str] = [
    "",
    "[red]❌ Move not found: {move_name}[/red]",
    "[dim]Check the move name and try again[/dim]",
    "",
]
