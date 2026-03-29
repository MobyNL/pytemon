"""
Text constants for pytemon/exploration.py.
"""

# ── move_to_location ──────────────────────────────────────────────────────────

# Dynamic: "[red]❌ You can't go to '{destination}' from {location}[/red]"
CANT_GO_THERE: list[str] = [
    "",
    # dynamic line here
    "[dim]Type 'Look Around' to see available exits[/dim]",
    "",
]

OAK_NO_POKEMON_WARNING: list[str] = [
    "",
    "[bold red]Professor Oak:[/bold red] [cyan]Wait! Don't go out there![/cyan]",
    "",
    "[cyan]   It's dangerous to go alone without a Pokemon![/cyan]",
    "[cyan]   Come to my lab and I'll give you your first Pokemon![/cyan]",
    "",
]

NOT_ENOUGH_EXPLORES: list[str] = [
    "",
    # dynamic: "[yellow]⚠ You haven't fully explored {location} yet![/yellow]"
    # dynamic: "[dim]Explore the area {remaining} more time(s) before heading to {destination}.[/dim]"
    # dynamic: "[dim]Progress: {done}/{required} — use 'Explore' to continue searching[/dim]"
    "",
]

# ── prompt_for_location ───────────────────────────────────────────────────────

NO_AVAILABLE_PATHS: list[str] = [
    "",
    "[yellow]⚠ There are no available paths from here[/yellow]",
    "",
]

SELECT_DESTINATION_HEADER: list[str] = [
    "",
    "[bold cyan]🗺️  Where would you like to go?[/bold cyan]",
    "",
    "[bold green]Available destinations:[/bold green]",
]

SELECT_DESTINATION_TEXT_PROMPT: list[str] = [
    "[yellow]Type the name of the location you want to visit:[/yellow]",
    "[dim](or type 'cancel' to go back)[/dim]",
    "",
]

SELECT_DESTINATION_PANEL_PROMPT: list[str] = [
    "[yellow]Select a destination from the menu above[/yellow]",
    "",
]

# ── prompt_for_building ───────────────────────────────────────────────────────

NO_BUILDINGS_HERE: list[str] = [
    "",
    "[yellow]⚠ There are no buildings here to enter[/yellow]",
    "[dim]You can only enter buildings in towns and cities[/dim]",
    "",
]

SELECT_BUILDING_HEADER: list[str] = [
    "",
    "[bold cyan]🏛️  Which building would you like to enter?[/bold cyan]",
    "",
    "[bold green]Available buildings:[/bold green]",
]

SELECT_BUILDING_TEXT_PROMPT: list[str] = [
    "[yellow]Type the name of the building you want to enter:[/yellow]",
    "[dim](or type 'cancel' to go back)[/dim]",
    "",
]

SELECT_BUILDING_PANEL_PROMPT: list[str] = [
    "[yellow]Select a building from the menu above[/yellow]",
    "",
]

# ── show_location_arrival ─────────────────────────────────────────────────────

ARRIVAL_FOOTER: list[str] = [
    "[dim]Type 'Help' to see all available commands[/dim]",
    "",
]

ARRIVAL_EXPLORE_TIP: list[str] = [
    "[yellow]💡 Tip:[/yellow] Use the [cyan]'Explore'[/cyan] command to search this area",
]

ARRIVAL_EXPLORE_WILD: list[str] = [
    "[dim]   for wild Pokemon encounters[/dim]",
]

ARRIVAL_EXPLORE_UNLOCK: list[str] = [
    "[dim]   Explore this area to unlock forward paths.[/dim]",
]

# ── look_around ───────────────────────────────────────────────────────────────

LOOK_AROUND_EXPLORE_HINT: list[str] = [
    "[yellow]💡 This area can be explored[/yellow]",
]

LOOK_AROUND_WILD_HINT: list[str] = [
    "[dim]   Wild Pokemon may appear when exploring[/dim]",
]
