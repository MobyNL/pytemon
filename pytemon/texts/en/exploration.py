"""
Text constants for pytemon/exploration.py.
"""

ERROR_NO_CURRENT_LOCATION: list[str] = [
    "[red]❌ Error: No current location set[/red]",
]

# ── move_to_location ──────────────────────────────────────────────────────────

# Dynamic: use write_lines_fmt(output, CANT_GO_THERE, destination=..., location=...)
CANT_GO_THERE: list[str] = [
    "",
    "[red]❌ You can't go to '{destination}' from {location}[/red]",
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

# Dynamic: use write_lines_fmt(output, NOT_ENOUGH_EXPLORES,
#          location=..., remaining=..., destination=..., done=..., required=...)
NOT_ENOUGH_EXPLORES: list[str] = [
    "",
    "[yellow]⚠ You haven't fully explored {location} yet![/yellow]",
    "[dim]Explore the area {remaining} more time(s) before heading to {destination}.[/dim]",
    "[dim]Progress: {done}/{required} — use 'Explore' to continue searching[/dim]",
    "",
]

EXIT_BLOCKED_REASON: list[str] = [
    "",
    "[yellow]⚠ {reason}[/yellow]",
    "",
]

LOCATION_NOT_FOUND: list[str] = [
    "[red]❌ Error: Location '{location_name}' not found[/red]",
]

TRAVELING_TO: list[str] = [
    "",
    "[bold cyan]➜ Traveling to {location_name}...[/bold cyan]",
]

AUTOSAVED_TO: list[str] = [
    "[dim]  💾 Autosaved to {autosave_name}[/dim]",
]

TRAVELING_TO_FOOTER: list[str] = [
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

SELECT_DESTINATION_ENTRY_WITH_DIRECTION: list[str] = [
    "  ➜ [green]{exit_name}[/green] ({direction})",
]

SELECT_DESTINATION_ENTRY: list[str] = [
    "  ➜ [green]{exit_name}[/green]",
]

SELECT_DESTINATION_DESCRIPTION: list[str] = [
    "     [dim]{description}[/dim]",
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

SELECT_DESTINATION_LIST_FOOTER: list[str] = [
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

SELECT_BUILDING_ENTRY: list[str] = [
    "  🏛️  [green]{building}[/green]",
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

SELECT_BUILDING_LIST_FOOTER: list[str] = [
    "",
]

BLOCKED_BUILDINGS_HEADER: list[str] = [
    "",
    "[dim]Blocked buildings:[/dim]",
]

BLOCKED_BUILDINGS_FOOTER: list[str] = [
    "",
]

BLOCKED_BUILDING_ENTRY: list[str] = [
    "  [dim]🔒 {building} - {reason}[/dim]",
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

ARRIVAL_HEADER: list[str] = [
    "[bold green]══════════════════════════════════════════════════[/bold green]",
    "[bold cyan]📍 {location_name_upper}[/bold cyan]",
    "[bold green]══════════════════════════════════════════════════[/bold green]",
    "",
]

ARRIVAL_LOAD_TEXT: list[str] = [
    "[bold]You find yourself in {location_name}.[/bold]",
]

ARRIVAL_TEXT: list[str] = [
    "[bold]You have arrived in {location_name}.[/bold]",
]

ARRIVAL_DESCRIPTION: list[str] = [
    "[dim]{description}[/dim]",
    "",
]

ARRIVAL_ACTIVITIES_ONE: list[str] = [
    "Here you can {activity1}.",
    "",
]

ARRIVAL_ACTIVITIES_TWO: list[str] = [
    "Here you can {activity1} or {activity2}.",
    "",
]

ARRIVAL_ACTIVITIES_MANY: list[str] = [
    "Here you can {activity_text}.",
    "",
]

ARRIVAL_PATHS_HEADER: list[str] = [
    "[bold yellow]From {location_name} you can travel to:[/bold yellow]",
]

ARRIVAL_PATH_WITH_DIRECTION: list[str] = [
    "  • [cyan]{exit_name}[/cyan] ({direction}) - {description}{back_tag}",
]

ARRIVAL_PATH_WITH_DESCRIPTION: list[str] = [
    "  • [cyan]{exit_name}[/cyan] - {description}{back_tag}",
]

ARRIVAL_PATH_BASIC: list[str] = [
    "  • [cyan]{exit_name}[/cyan]{back_tag}",
]

ARRIVAL_PATHS_FOOTER: list[str] = [
    "",
]

ARRIVAL_BLOCKED_BUILDINGS_HEADER: list[str] = [
    "[dim]Note:[/dim]",
]

ARRIVAL_BLOCKED_BUILDINGS_FOOTER: list[str] = [
    "",
]

ARRIVAL_EXPLORE_FOOTER: list[str] = [
    "",
]

# ── look_around ───────────────────────────────────────────────────────────────

LOOK_AROUND_EXPLORE_HINT: list[str] = [
    "[yellow]💡 This area can be explored[/yellow]",
]

LOOK_AROUND_WILD_HINT: list[str] = [
    "[dim]   Wild Pokemon may appear when exploring[/dim]",
]

LOOK_AROUND_TRAINERS_HINT: list[str] = [
    "[dim]   {trainer_count} trainer(s) may challenge you[/dim]",
]

LOOK_AROUND_HEADER: list[str] = [
    "",
    "[bold cyan]👀 Looking around {location_name}...[/bold cyan]",
    "",
]

LOOK_AROUND_BUILDINGS_HEADER: list[str] = [
    "[bold yellow]Buildings:[/bold yellow]",
]

LOOK_AROUND_BUILDING_ENTRY: list[str] = [
    "  🏛️  {building}",
]

LOOK_AROUND_BUILDINGS_FOOTER: list[str] = [
    "",
]

LOOK_AROUND_BLOCKED_BUILDINGS_HEADER: list[str] = [
    "[dim]Blocked Buildings:[/dim]",
]

LOOK_AROUND_BLOCKED_BUILDINGS_FOOTER: list[str] = [
    "",
]

LOOK_AROUND_AVAILABLE_PATHS_HEADER: list[str] = [
    "[bold green]Available Paths:[/bold green]",
]

LOOK_AROUND_FORWARD_BACKTRACK: list[str] = [
    "  [dim]→ {exit_name}: [cyan]↩ back (no explores needed)[/cyan][/dim]",
]

LOOK_AROUND_FORWARD_UNLOCKED: list[str] = [
    "  [dim]→ {exit_name}: [{bar}] ✓ Unlocked[/dim]",
]

LOOK_AROUND_FORWARD_PROGRESS: list[str] = [
    "  [dim]→ {exit_name}: [{bar}] {progress}/{required}[/dim]",
]

LOOK_AROUND_PATH_BACK: list[str] = [
    "  ➜ {exit_name}{direction_str} [cyan]↩ back[/cyan]",
]

LOOK_AROUND_PATH: list[str] = [
    "  ➜ {exit_name}{direction_str}",
]

LOOK_AROUND_BLOCKED_PATH_ENTRY: list[str] = [
    "  [dim]🔒 {exit_name} - {reason}[/dim]",
]

LOOK_AROUND_HINT_LINE: list[str] = [
    "{hint}",
]

LOOK_AROUND_AVAILABLE_PATHS_FOOTER: list[str] = [
    "",
]

LOOK_AROUND_BLOCKED_PATHS_HEADER: list[str] = [
    "[dim]Blocked Paths:[/dim]",
]

LOOK_AROUND_BLOCKED_PATHS_FOOTER: list[str] = [
    "",
]

LOOK_AROUND_EXPLORE_FOOTER: list[str] = [
    "",
]

EXPLORE_NOTHING_HERE: list[str] = [
    "",
    "[yellow]⚠ There's nothing to explore in {location_name}[/yellow]",
    "[dim]You can only explore routes and forests[/dim]",
    "",
]

EXPLORE_START: list[str] = [
    "",
    "[bold cyan]🔍 Exploring {location_name}...[/bold cyan]",
    "",
]

DARK_TUNNEL_WARNING: list[str] = [
    "[dim]🌑 The tunnel is pitch black — encounters are far more frequent![/dim]",
    "[dim]   Use Flash to illuminate the cave and reduce wild encounter rate.[/dim]",
    "",
]

EXPLORE_NO_POKEMON: list[str] = [
    "[yellow]⚠ You can't explore without Pokemon![/yellow]",
    "[dim]Get a starter from Professor Oak's Lab first[/dim]",
    "",
]

EXPLORE_NOTHING_FOUND: list[str] = [
    "[dim]You search the area but find nothing...[/dim]",
    "",
]

REPEL_SUPPRESSED_ENCOUNTER: list[str] = [
    "[dim]🪢 The Repel keeps wild Pokemon away...[/dim]",
]

REPEL_REMAINING: list[str] = [
    "[dim]   ({remaining} explore(s) of Repel remaining)[/dim]",
]

REPEL_WORE_OFF: list[str] = [
    "[dim]   The Repel wore off![/dim]",
]

REPEL_FOOTER: list[str] = [
    "",
]

POKEMON_TOWER_GHOST_BLOCKS: list[str] = [
    "",
    "[bold magenta]👻 A wandering spirit materialises before you![/bold magenta]",
    "[magenta]   Your Pokeballs pass right through it — you can't fight it![/magenta]",
    "[magenta]   You back away slowly to a lower floor...[/magenta]",
    "",
    "[yellow]⚠ Tip:[/yellow] [dim]You need the Silph Scope to battle Ghost-type Pokemon here.[/dim]",
    "[dim]   The Silph Scope is held by Team Rocket — defeat them in Celadon City.[/dim]",
    "",
]

EXPLORE_NO_ENCOUNTER_CYCLING: list[str] = [
    "[cyan]🚲 You zip through the area on your Bicycle![/cyan]",
]

EXPLORE_NO_ENCOUNTER_WALKING: list[str] = [
    "[dim]You search the tall grass but nothing jumps out...[/dim]",
]

EXPLORE_NO_ENCOUNTER_FOOTER: list[str] = [
    "",
]

ITEM_FOUND_FLAVOUR: list[str] = [
    "[dim]   {flavour} Added to your bag.[/dim]",
]

ITEM_FOUND_HEADER: list[str] = [
    "{emoji} [bold green]You found {item_name}![/bold green]",
]

ITEM_FOUND_MORE_NEARBY: list[str] = [
    "[dim]   (You sense {remaining} more hidden item{s_suffix} nearby...)[/dim]",
]

ITEM_FOUND_FOOTER: list[str] = [
    "",
]

MT_MOON_FOUND_MOON_STONE: list[str] = [
    "",
    "[bold magenta]✨ You spot something glinting in the cave wall![/bold magenta]",
    "[magenta]   It's a [bold]Moon Stone[/bold]! You carefully pry it loose.[/magenta]",
    "[bold green]✓ Found a Moon Stone![/bold green]",
    "[dim]   (Causes certain Pokemon to evolve when used)[/dim]",
    "",
]

MT_MOON_FOUND_FOSSIL: list[str] = [
    "",
    "[bold yellow]🦴 You find a fossil embedded in the cave wall![/bold yellow]",
    "[yellow]   With great care you extract a [bold]{fossil}[/bold]![/yellow]",
    "[bold green]✓ Found a {fossil}![/bold green]",
    "[dim]   (A scientist might be able to revive the Pokemon inside)[/dim]",
    "",
]

POKEMON_TOWER_GHOST_EVENT_HEADER: list[str] = [
    "",
    "[bold magenta]👻 A shadowy figure blocks the stairs...[/bold magenta]",
]

POKEMON_TOWER_GHOST_EVENT_WITH_SCOPE: list[str] = [
    "[magenta]   Through the Silph Scope you see clearly:[/magenta]",
    "[magenta]   It's the ghost of a [bold]MAROWAK[/bold]![/magenta]",
    "[magenta]   The vengeful spirit of a mother protecting her child...[/magenta]",
    "[magenta]   You feel the Silph Scope resonate and the ghost fades.[/magenta]",
    "",
    "[dim]   (With the Silph Scope you can now identify and battle ghost Pokemon)[/dim]",
]

POKEMON_TOWER_GHOST_EVENT_NO_SCOPE: list[str] = [
    "[magenta]   The ghost cannot be identified — your Pokeballs pass right through![/magenta]",
    "[magenta]   You retreat to a lower floor, shaken.[/magenta]",
    "",
    "[yellow]⚠ Tip:[/yellow] [dim]You need the Silph Scope to battle the ghost Pokemon here.[/dim]",
    "[dim]   The Silph Scope is said to be held by Team Rocket...[/dim]",
]

POKEMON_TOWER_GHOST_EVENT_FOOTER: list[str] = [
    "",
]

POKEMON_TOWER_RESCUE_MR_FUJI: list[str] = [
    "",
    "[bold cyan]🏠 You reach the top of Pokemon Tower...[/bold cyan]",
    "[cyan]   Team Rocket Grunts scatter as you approach![/cyan]",
    "",
    "[bold]Mr. Fuji:[/bold] [cyan]Oh my... a young trainer, here to rescue me![/cyan]",
    "[cyan]   Those dreadful Team Rocket villains imprisoned me![/cyan]",
    "[cyan]   Please — take this Poke Flute as thanks.[/cyan]",
    "[cyan]   It will wake the sleeping Pokemon that block your path.[/cyan]",
    "",
    "[bold yellow]★ Received Poke Flute! ★[/bold yellow]",
    "[dim]   The Poke Flute wakes sleeping Snorlax blocking certain routes.[/dim]",
    "",
]

ROCKET_HIDEOUT_FOUND_LIFT_KEY: list[str] = [
    "",
    "[bold yellow]🗝️  A small key glints under a fallen crate...[/bold yellow]",
    "[yellow]   The tag reads: [bold]LIFT KEY — B4F[/bold].[/yellow]",
    "[bold green]✓ Found the Lift Key![/bold green]",
    "[dim]   Use this key to reach the lower floors and confront the Rocket Boss.[/dim]",
    "",
]

ROCKET_HIDEOUT_GIOVANNI_REWARD: list[str] = [
    "",
    "[bold red]🚀 You reach the deepest level of the Hideout...[/bold red]",
    "[red]   Giovanni stares at you with cold contempt.[/red]",
    "",
    "[bold]Giovanni:[/bold] [red]So... you've made it this far.[/red]",
    "[red]   I am Giovanni — the Boss of Team Rocket.[/red]",
    "[red]   You have some skill. But skill alone does not impress me.[/red]",
    "[red]   ...You win. Take the Silph Scope.[/red]",
    "[red]   It is useless to us if we cannot hold this base.[/red]",
    "[red]   Team Rocket will retreat... for now.[/red]",
    "",
    "[bold yellow]★ Received Silph Scope! ★[/bold yellow]",
    "[dim]   The Silph Scope lets you identify ghost Pokemon in Pokemon Tower.[/dim]",
    "",
]
