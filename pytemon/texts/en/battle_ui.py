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

# ── battle introductions ─────────────────────────────────────────────────────

WILD_BATTLE_START: list[str] = [
    "",
    "[bold red]═══════════════════════════════════════════[/bold red]",
    "[bold red]⚔️  A wild {wild_name} appeared! (Lv. {wild_level})  ⚔️[/bold red]",
    "[bold red]═══════════════════════════════════════════[/bold red]",
    "",
    "[bold]Go! {player_name}![/bold]",
    "",
]

SAFARI_BATTLE_START: list[str] = [
    "",
    "[bold green]═══════════════════════════════════════════[/bold green]",
    "[bold green]🦁  A wild {wild_name} appeared! (Lv. {wild_level})  🦁[/bold green]",
    "[bold green]═══════════════════════════════════════════[/bold green]",
    "",
    "[dim]You're in the Safari Zone — you can't battle here![/dim]",
    "[dim]Use Bait, Rock, or throw a Safari Ball![/dim]",
    "",
]

TRAINER_BATTLE_SENT_OUT: list[str] = [
    "[dim]{trainer_name} sent out {pokemon_name}![/dim]",
]

TRAINER_BATTLE_TEAM_SIZE: list[str] = [
    "[dim]They have {num_pokemon} Pokemon total[/dim]",
]

TRAINER_BATTLE_GO: list[str] = [
    "",
    "[bold]Go! {player_name}![/bold]",
    "",
]

# ── option menus ─────────────────────────────────────────────────────────────

BATTLE_WHAT_TO_DO: list[str] = [
    "[bold yellow]What will you do?[/bold yellow]",
]

BATTLE_OPTIONS_CORE: list[str] = [
    "  [cyan]Fight[/cyan]  |  [cyan]Switch[/cyan]  |  [cyan]Item[/cyan]",
]

BATTLE_OPTIONS_TRAINER_HINT: list[str] = [
    "[dim]  (Can't flee or catch in trainer battles)[/dim]",
]

BATTLE_OPTIONS_CATCH_AVAILABLE: list[str] = [
    "  [green]Catch[/green] ({pokeballs} Pokeballs)  |  [yellow]Flee[/yellow]",
]

BATTLE_OPTIONS_CATCH_NONE: list[str] = [
    "  [dim]Catch (No Pokeballs)[/dim]  |  [yellow]Flee[/yellow]",
]

SAFARI_STATUS_LINE: list[str] = [
    "  {status_text}",
]

SAFARI_OPTIONS_WITH_BALLS: list[str] = [
    "  [green]Safari Ball[/green] ({safari_balls})  |  [cyan]Bait[/cyan]  |  [cyan]Rock[/cyan]  |  [yellow]Run[/yellow]",
]

SAFARI_OPTIONS_NO_BALLS: list[str] = [
    "  [dim]No Safari Balls![/dim]  |  [cyan]Bait[/cyan]  |  [cyan]Rock[/cyan]  |  [yellow]Run[/yellow]",
]

MENU_TRAILING_BLANK: list[str] = [
    "",
]

# ── move/switch/help/bag panels ──────────────────────────────────────────────

MOVE_SELECTION_HEADER: list[str] = [
    "",
    "[bold yellow]Select a move:[/bold yellow]",
    "",
]

MOVE_SELECTION_PROMPT: list[str] = [
    "",
    "[dim]Type the move name or 'Back' to go back[/dim]",
    "",
]

SWITCH_MENU_HEADER: list[str] = [
    "",
    "[bold cyan]Choose a Pokemon to switch in:[/bold cyan]",
    "",
]

SWITCH_MENU_PROMPT: list[str] = [
    "",
    "[yellow]Type the number or name of the Pokemon, or 'Back':[/yellow]",
    "",
]

BATTLE_HELP_BLOCK: list[str] = [
    "",
    "[bold cyan]⚔️  BATTLE HELP ⚔️[/bold cyan]",
    "",
    "[bold yellow]Commands:[/bold yellow]",
    "  [cyan]Fight[/cyan]   - Choose a move to attack",
    "  [cyan]Switch[/cyan]  - Switch to another Pokemon",
    "  [cyan]Item[/cyan]    - Use an item (Potion, Pokeball, etc.)",
    "  [cyan]Catch[/cyan]   - Try to catch the wild Pokemon (needs Pokeball)",
    "  [cyan]Flee[/cyan]    - Try to escape from battle",
    "",
    "[bold yellow]Items you can use in battle:[/bold yellow]",
    "  [green]Potion[/green]        - Restores 20 HP",
    "  [green]Super Potion[/green]  - Restores 50 HP",
    "  [green]Antidote[/green]      - Cures poison",
    "  [green]Paralyze Heal[/green] - Cures paralysis",
    "  [green]Awakening[/green]     - Wakes sleeping Pokemon",
    "",
    "[dim]Trainer battles: Can't catch or flee[/dim]",
    "",
]

BATTLE_BAG_HEADER: list[str] = [
    "",
    "[bold cyan]🎒 Battle Bag[/bold cyan]",
]

BATTLE_BAG_NO_ITEMS: list[str] = [
    "  [dim]Your bag has no usable items![/dim]",
    "",
    "[dim]Buy items at the Pokemart. Type 'fight' or 'run'[/dim]",
]

BATTLE_BAG_CANCEL_HINT: list[str] = [
    "",
    "[dim]Or type 'fight'/'run' to cancel[/dim]",
]

BATTLE_BAG_FOOTER: list[str] = [
    "",
]
