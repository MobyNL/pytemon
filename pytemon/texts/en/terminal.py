"""
Text constants for pytemon/terminal.py.
"""

SAVE_NEW_FILE_PROMPT: list[str] = [
    "",
    "[yellow]Enter a name for your new save file:[/yellow]",
    "[dim]Or press Enter to use a timestamp[/dim]",
    "",
]

LOAD_SELECT_SAVE_REQUIRED: list[str] = [
    "",
    "[red]❌ Please click a save file in the list first![/red]",
    "",
]

LOCATION_SELECT_REQUIRED: list[str] = [
    "",
    "[red]❌ Please select a destination first![/red]",
    "",
]

BUILDING_SELECT_REQUIRED: list[str] = [
    "",
    "[red]❌ Please select a building first![/red]",
    "",
]

POKEDEX_CLOSED: list[str] = [
    "",
    "[dim]Pokedex closed.[/dim]",
    "",
]

MOM_HEAL_DECLINED: list[str] = [
    "",
    "[bold]Mom:[/bold] [magenta]Okay! Come back anytime you need to rest![/magenta]",
    "",
    "[dim]You leave the house[/dim]",
    "",
]

LEAVE_POKEMON_CENTER: list[str] = [
    "",
    "[dim]You leave the Pokemon Center. Come back if your Pokemon need healing![/dim]",
    "",
]

PC_LOG_OUT: list[str] = [
    "",
    "[dim]You log out of the PC.[/dim]",
    "",
]

SHOP_THANK_YOU_LEAVE: list[str] = [
    "",
    "[bold]Clerk:[/bold] [yellow]Thank you! Come again![/yellow]",
    "[dim]You leave the Pokemart.[/dim]",
    "",
]

QUIT_CANCELLED: list[str] = [
    "",
    "[green]✓ Cancelled[/green]",
    "[dim]Continuing game...[/dim]",
    "",
]

GYM_LEAVE: list[str] = [
    "",
    "[dim]You leave the Gym. Come back when you're ready![/dim]",
    "",
]

EVOLUTION_STOPPED: list[str] = [
    "",
    "[cyan]{pokemon_name} did not evolve.[/cyan]",
    "",
]

USAGE_SHOW_POKEDEX_PAGE: list[str] = [
    "",
    "[yellow]⚠ Usage: Show Pokedex Page <number>[/yellow]",
    "[dim]Example: 'Show Pokedex Page 3'[/dim]",
    "",
]

USAGE_INSPECT: list[str] = [
    "",
    "[yellow]⚠ Usage: Inspect <name|number>[/yellow]",
    "[dim]Example: 'Inspect Pikachu' or 'Inspect 25'[/dim]",
    "",
]

AUTOSAVE_ENABLED: list[str] = [
    "",
    "[green]✓ Autosave enabled[/green]",
    "[dim]Game will autosave every {frequency} commands[/dim]",
    "",
]

AUTOSAVE_DISABLED: list[str] = [
    "",
    "[yellow]⚠ Autosave disabled[/yellow]",
    "[dim]Remember to save manually![/dim]",
    "",
]

AUTOSAVE_FREQUENCY_SET: list[str] = [
    "",
    "[green]✓ Autosave frequency set to {frequency} commands[/green]",
    "",
]

AUTOSAVE_FREQUENCY_RANGE_ERROR: list[str] = [
    "",
    "[red]❌ Autosave frequency must be between 5 and 100[/red]",
    "",
]

PC_CENTER_REQUIRED: list[str] = [
    "",
    "[yellow]⚠ Bill's PC is only accessible at a Pokemon Center.[/yellow]",
    "[dim]Enter the Pokemon Center to access the PC.[/dim]",
    "",
]

NO_BICYCLE: list[str] = [
    "",
    "[yellow]⚠ You don't have a Bicycle![/yellow]",
    "[dim]Visit the Bike Shop in Cerulean City to get one[/dim]",
    "",
]

BICYCLE_LOCATION_RESTRICTED: list[str] = [
    "",
    "[yellow]⚠ You can only ride your Bicycle in routes, forests, and caves![/yellow]",
    "[dim]Get to an explorable area first, then hop on your bike[/dim]",
    "",
]

BICYCLE_OFF: list[str] = [
    "",
    "[cyan]🚶 You hop off your Bicycle[/cyan]",
    "[dim]Back to walking pace[/dim]",
    "",
]

BICYCLE_ON: list[str] = [
    "",
    "[bold cyan]🚲 You hop on your Bicycle![/bold cyan]",
    "[cyan]   You zoom along the route at high speed![/cyan]",
    "[dim]Wild encounter rate reduced while cycling[/dim]",
    "",
]

NOT_INSIDE_BUILDING: list[str] = [
    "",
    "[yellow]⚠ You're not inside a building.[/yellow]",
    "[dim]Walk into a building first with 'Enter <building>'[/dim]",
    "[dim]To close the game use 'Stop' or 'Stop Playing'[/dim]",
    "",
]

USAGE_USE_ITEM: list[str] = [
    "",
    "[yellow]⚠ Usage:  use <item>  or  use <item> on <pokemon>[/yellow]",
    "[dim]Example: use potion  /  use fire stone on eevee[/dim]",
    "",
]

POKEDEX_FIRST_PAGE_ALREADY: list[str] = [
    "",
    "[yellow]⚠ Already on first page[/yellow]",
    "",
]

POKEDEX_PAGE_MINIMUM: list[str] = [
    "",
    "[yellow]⚠ Page number must be at least 1[/yellow]",
    "",
]
