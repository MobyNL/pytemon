"""
Text constants for pytemon/ui/game_flow_mixin.py.
"""

NEW_GAME_START: list[str] = [
    "",
    "[bold green]✓ Starting new game...[/bold green]",
    "",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "[bold green]🌟 Welcome to the Pokemon World! 🌟[/bold green]",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "",
    "Before we begin your adventure...",
    "",
]

ACTION_CANCELLED: list[str] = [
    "",
    "[dim]Cancelled.[/dim]",
    "",
]

EVOLUTION_DECLINED: list[str] = [
    "",
    "[cyan]{pokemon_name} did not evolve.[/cyan]",
    "",
]

LEAVING_GAME_PROMPT: list[str] = [
    "",
    "[bold yellow]⚠ Leaving the game?[/bold yellow]",
    "",
]

GOODBYE_SIMPLE: list[str] = [
    "[cyan]👋 Goodbye![/cyan]",
]

GOODBYE_TRAINER: list[str] = [
    "[cyan]👋 Goodbye, Trainer![/cyan]",
]

PROGRESS_NOT_SAVED_AND_GOODBYE: list[str] = [
    "",
    "[yellow]⚠ Progress not saved[/yellow]",
    "[cyan]👋 Goodbye, Trainer![/cyan]",
]

CONTINUING_GAME: list[str] = [
    "",
    "[green]✓ Continuing game...[/green]",
    "",
]

PROGRESS_NOT_SAVED: list[str] = [
    "",
    "[yellow]⚠ Progress not saved[/yellow]",
]

QUIT_CANCELLED: list[str] = [
    "",
    "[green]✓ Cancelled[/green]",
    "[dim]Continuing game...[/dim]",
    "",
]

INVALID_QUIT_CHOICE: list[str] = [
    "",
    "[red]❌ Invalid choice[/red]",
    "[dim]Please type: Yes, No, or Cancel[/dim]",
    "",
]

SAVE_BEFORE_QUIT_PROMPT: list[str] = [
    "",
    "[bold yellow]⚠ Would you like to save before you {dest_label}?[/bold yellow]",
    "",
    "  [green]Yes[/green] - Save first",
    "  [red]No[/red] - Continue without saving",
    "  [cyan]Cancel[/cyan] - Go back",
    "",
    "[dim]Click a button or type your choice:[/dim]",
    "",
]

CHOOSE_LEAD_WILD_USE_RUN: list[str] = [
    "",
    "[yellow]Choose your lead Pokemon to begin the battle.[/yellow]",
    "[dim]If you want to quit a wild battle, use [bold]run[/bold] once battle starts.[/dim]",
    "",
]

CHOOSE_LEAD_TRAINER_NO_CANCEL: list[str] = [
    "",
    "[red]You can't cancel lead selection in a trainer battle.[/red]",
    "[dim]Choose a Pokemon to continue.[/dim]",
    "",
]

CHOOSE_LEAD_ENTER_NUMBER: list[str] = [
    "[red]❌ Please enter a number to choose your Pokemon.[/red]",
]

CHOOSE_LEAD_RANGE: list[str] = [
    "[red]❌ Please enter a number between 1 and {max_slot}.[/red]",
]

CHOOSE_LEAD_GO: list[str] = [
    "",
    "[bold green]Go, {chosen_name}![/bold green]",
    "",
]

RETURNING_MAIN_MENU: list[str] = [
    "",
    "[dim]Returning to main menu...[/dim]",
    "",
]

UNKNOWN_CONFIRMATION_TYPE: list[str] = [
    "[red]❌ Unknown confirmation type: {confirmation_type}[/red]",
]
