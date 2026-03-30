"""
Text constants for pytemon/dungeon.py.
"""

# ── Entry ─────────────────────────────────────────────────────────────────────

# Dynamic: write_lines_fmt(output, DUNGEON_ENTER_HEADER, dungeon_name=..., floor_name=...)
DUNGEON_ENTER_HEADER: list[str] = [
    "",
    "[bold cyan]🕳️  Entering {dungeon_name}[/bold cyan]",
    "[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]",
    "[cyan]  📍 {floor_name}[/cyan]",
]

# Dynamic: write_lines_fmt(output, DUNGEON_FLOOR_DESCRIPTION, description=...)
DUNGEON_FLOOR_DESCRIPTION: list[str] = [
    "[dim]  {description}[/dim]",
    "",
]

DUNGEON_ENTER_FOOTER: list[str] = [
    "[dim]  Type [bold]explore[/bold] to search the floor, "
    "[bold]go up[/bold] / [bold]go down[/bold] to change floors, "
    "or [bold]where[/bold] to see your position.[/dim]",
    "",
]

DUNGEON_CHECKPOINT_REACHED: list[str] = [
    "[bold green]  🚩 Checkpoint reached! If your party faints you'll restart here.[/bold green]",
]

# ── Navigation ────────────────────────────────────────────────────────────────

# Dynamic: write_lines_fmt(output, DUNGEON_FLOOR_ARRIVED, floor_name=...)
DUNGEON_FLOOR_ARRIVED: list[str] = [
    "",
    "[bold cyan]🗺️  {floor_name}[/bold cyan]",
    "[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]",
]

# Dynamic: write_lines_fmt(output, DUNGEON_EXIT_GATED_FLAG, label=...)
DUNGEON_EXIT_GATED_FLAG: list[str] = [
    "",
    "[yellow]⚠  {label} is blocked. Something is stopping you from proceeding.[/yellow]",
    "",
]

# Dynamic: write_lines_fmt(output, DUNGEON_EXIT_GATED_ITEM, label=..., item=...)
DUNGEON_EXIT_GATED_ITEM: list[str] = [
    "",
    "[yellow]⚠  {label} requires [bold]{item}[/bold] to pass.[/yellow]",
    "",
]

# Dynamic: write_lines_fmt(output, DUNGEON_EXIT_GATED_BADGE, label=..., badge=...)
DUNGEON_EXIT_GATED_BADGE: list[str] = [
    "",
    "[yellow]⚠  {label} requires the [bold]{badge}[/bold] to proceed.[/yellow]",
    "",
]

# Dynamic: write_lines_fmt(output, DUNGEON_FLOOR_NOT_FOUND, floor_id=...)
DUNGEON_FLOOR_NOT_FOUND: list[str] = [
    "[red]❌ Floor '{floor_id}' not found in this dungeon.[/red]",
]

# Dynamic: write_lines_fmt(output, DUNGEON_EXITED, dungeon_name=..., location=...)
DUNGEON_EXITED: list[str] = [
    "",
    "[bold green]🚪 You exit {dungeon_name}.[/bold green]",
    "[cyan]  You emerge near {location}.[/cyan]",
    "",
]

# Dynamic: write_lines_fmt(output, DUNGEON_EXIT_LOCATION_NOT_FOUND, location=...)
DUNGEON_EXIT_LOCATION_NOT_FOUND: list[str] = [
    "[red]❌ Exit destination '{location}' not found.[/red]",
]

# ── Exits display ─────────────────────────────────────────────────────────────

DUNGEON_EXITS_HEADER: list[str] = [
    "",
    "[bold]  Exits from this floor:[/bold]",
]

# Dynamic: write_lines_fmt(output, DUNGEON_EXIT_ENTRY, direction=..., label=...)
DUNGEON_EXIT_ENTRY: list[str] = [
    "    [cyan]→ {direction}[/cyan]  [dim]{label}[/dim]",
]

# Dynamic: write_lines_fmt(output, DUNGEON_EXIT_ENTRY_LEAVE, direction=..., label=..., location=...)
DUNGEON_EXIT_ENTRY_LEAVE: list[str] = [
    "    [green]→ {direction}[/green]  [dim]{label}[/dim]  [green](leaves dungeon → {location})[/green]",
]

DUNGEON_EXITS_FOOTER: list[str] = [
    "",
]

# ── Items ─────────────────────────────────────────────────────────────────────

# Dynamic: write_lines_fmt(output, DUNGEON_ITEM_PICKUP, item=...)
DUNGEON_ITEM_PICKUP: list[str] = [
    "",
    "[bold yellow]✨ You found: {item}![/bold yellow]",
    "[dim]   Added to your bag.[/dim]",
    "",
]

# Dynamic: write_lines_fmt(output, DUNGEON_ITEM_PICKUP_FOSSIL, fossil=...)
DUNGEON_ITEM_PICKUP_FOSSIL: list[str] = [
    "",
    "[bold yellow]🦴 You snatched a [bold]{fossil}[/bold] before the Team Rocket grunt could![/bold yellow]",
    "[dim]   It can be revived at the Cinnabar Island Pokemon Lab.[/dim]",
    "",
]

# ── Blackout ──────────────────────────────────────────────────────────────────

# Dynamic: write_lines_fmt(output, DUNGEON_BLACKOUT,
#          dungeon_name=..., floor_name=..., penalty=...)
DUNGEON_BLACKOUT: list[str] = [
    "",
    "[bold red]💀 Your whole party fainted![/bold red]",
    "[red]   You were carried back to safety in {dungeon_name}.[/red]",
    "[yellow]   Respawning at checkpoint: [bold]{floor_name}[/bold][/yellow]",
    "[yellow]   You lost ₽{penalty} in the confusion.[/yellow]",
    "",
]

# ── Where command ─────────────────────────────────────────────────────────────

# Dynamic: write_lines_fmt(output, WHERE_HEADER, dungeon_name=..., floor_name=...)
WHERE_HEADER: list[str] = [
    "",
    "[bold cyan]🗺️  Dungeon Status — {dungeon_name}[/bold cyan]",
    "[dim]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim]",
    "[bold]  Current floor:[/bold] [cyan]{floor_name}[/cyan]",
]

# Dynamic: write_lines_fmt(output, WHERE_DESCRIPTION, description=...)
WHERE_DESCRIPTION: list[str] = [
    "[dim]  {description}[/dim]",
    "",
]

# Dynamic: write_lines_fmt(output, WHERE_EXPLORED, explored_count=..., total_floors=...)
WHERE_EXPLORED: list[str] = [
    "[bold]  Floors explored:[/bold] [cyan]{explored_count}/{total_floors}[/cyan]",
]

# Dynamic: write_lines_fmt(output, WHERE_FLOOR_ENTRY, marker=..., floor_name=..., tag=...)
WHERE_FLOOR_ENTRY: list[str] = [
    "    {marker} {floor_name}{tag}",
]

# Dynamic: write_lines_fmt(output, WHERE_CHECKPOINT, floor_name=...)
WHERE_CHECKPOINT: list[str] = [
    "",
    "[bold green]  🚩 Checkpoint:[/bold green] [green]{floor_name}[/green]",
]

WHERE_FOOTER: list[str] = [
    "",
    "[dim]  Commands: [bold]go up[/bold] · [bold]go down[/bold] · [bold]go north/south/east/west[/bold] · [bold]explore[/bold][/dim]",
    "",
]

# ── Event hooks ───────────────────────────────────────────────────────────────

EVENT_MT_MOON_B1F: list[str] = [
    "",
    "[bold cyan]✨ You reach a moonlit underground chamber.[/bold cyan]",
    "[dim]   Clefairy dance in the soft light filtering through a crack in the ceiling.[/dim]",
    "[dim]   A Moon Stone glints near the wall — yours for the taking.[/dim]",
    "",
]

EVENT_MT_MOON_FOSSIL: list[str] = [
    "",
    "[bold red]⚠  A Team Rocket grunt is arguing with a scientist over two fossils![/bold red]",
    "[red]   'These belong to Team Rocket now!' he shouts.[/red]",
    "[cyan]   You step forward. The grunt turns. 'You again? Fine — BATTLE ME!'[/cyan]",
    "",
    "[dim]   Defeat the Rocket grunt and choose one fossil to keep.[/dim]",
    "",
]

EVENT_ROCK_TUNNEL_DARK: list[str] = [
    "",
    "[bold yellow]⚠  It's pitch black in here![/bold yellow]",
    "[yellow]   Without Flash the Zubat swarms are relentless.[/yellow]",
    "[dim]   Tip: use 'use flash' if you have HM05 Flash to light up the tunnel.[/dim]",
    "",
]

EVENT_VICTORY_ROAD_ARRIVAL: list[str] = [
    "",
    "[bold yellow]⛰️  Victory Road — the final gauntlet.[/bold yellow]",
    "[dim]   Only trainers with all 8 Gym Badges may set foot here.[/dim]",
    "[bold]   The Pokemon League is just ahead. Steel yourself.[/bold]",
    "",
]

EVENT_VICTORY_ROAD_RIVAL: list[str] = [
    "",
    "[bold magenta]Your Rival appears from the shadows![/bold magenta]",
    "[magenta]   '{rival}: I knew you'd make it this far.'[/magenta]",
    "[magenta]   'But only ONE of us is going to the Pokemon League.'[/magenta]",
    "[magenta]   'Let's settle this — here and now!'[/magenta]",
    "",
]
