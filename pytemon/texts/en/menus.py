"""
Text constants for pytemon/ui/menus.py.
"""

# ── show_main_menu ────────────────────────────────────────────────────────────

MAIN_MENU: list[str] = [
    "",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "[bold cyan]        🎮 POKEMON TERMINAL GAME 🎮        [/bold cyan]",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "",
    "[bold green]MAIN MENU:[/bold green]",
    "",
    "  [cyan]Start New Game[/cyan] - Begin a new adventure",
    "  [cyan]Load Game[/cyan]      - Continue from a save",
    "  [cyan]Exit[/cyan]           - Quit the game",
    "",
    "[dim]Type a command to continue...[/dim]",
    "",
]

# ── start_new_game ────────────────────────────────────────────────────────────

NEW_GAME_STARTING: list[str] = [
    "",
    "[bold green]✓ Starting new game...[/bold green]",
    "",
]

NEW_GAME_WELCOME: list[str] = [
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "[bold green]🌟 Welcome to the Pokemon World! 🌟[/bold green]",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "",
]

# ── show_load_menu ────────────────────────────────────────────────────────────

LOAD_MENU_HEADER: list[str] = [
    "",
    "[bold cyan]📂 Load Game[/bold cyan]",
    "",
]

LOAD_MENU_NO_SAVES: list[str] = [
    "[yellow]⚠ No save files found![/yellow]",
    "",
    "[dim]Save files should be in: {saves_dir}[/dim]",
    "[dim]Type 'menu' to return to main menu[/dim]",
    "",
]

LOAD_MENU_FOOTER: list[str] = [
    "",
    "[dim]Type the save name to load, or 'menu' to go back[/dim]",
    "",
]

# ── load_selected_save ────────────────────────────────────────────────────────

GAME_LOADED_HEADER: list[str] = [
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "[bold green]🎮 Game Loaded! 🎮[/bold green]",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "",
]

LOAD_FAILED: list[str] = [
    "",
    "[red]❌ Failed to load save file[/red]",
    "",
]

# ── process_menu_command ──────────────────────────────────────────────────────

MENU_GOODBYE: list[str] = [
    "",
    "[cyan]👋 Thanks for playing! Goodbye, Trainer![/cyan]",
    "",
]
