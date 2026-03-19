"""
Exploration and movement handlers for Pokemon Terminal.

This module handles location navigation, area exploration, and related displays.
"""

import random
from typing import TYPE_CHECKING

from textual.widgets import RichLog

from . import stats as _stats
from .data import get_trainers_by_location
from .locations import get_location
from .ui.formatters import format_list, get_travel_description

if TYPE_CHECKING:
    from .game_state import GameState


def move_to_location(
    game_state: "GameState", destination: str, output: RichLog, show_arrival_callback
) -> None:
    """
    Move to a new location.

    Args:
        game_state: The game state object
        destination: Name of the destination location
        output: The RichLog widget to write to
        show_arrival_callback: Callback to show location arrival
    """
    if not game_state.current_location:
        output.write("[red]❌ Error: No current location set[/red]")
        return

    current = game_state.current_location

    # Find the destination in available exits (case-insensitive)
    destination_lower = destination.lower()
    matching_exit = None

    for exit_name in current.exits.keys():
        if exit_name.lower() == destination_lower or destination_lower in exit_name.lower():
            matching_exit = exit_name
            break

    if not matching_exit:
        output.write("")
        output.write(f"[red]❌ You can't go to '{destination}' from {current.name}[/red]")
        output.write("[dim]Type 'Look Around' to see available exits[/dim]")
        output.write("")
        return

    # Check if the exit is blocked
    exit_data = current.exits[matching_exit]

    # Special check: Unblock Route 24 from Cerulean City once player has Cascade Badge
    if matching_exit == "Route 24" and current.name == "Cerulean City":
        badges = game_state.game_data.get("badges", [])
        if "cascade_badge" in badges:
            exit_data = {**exit_data, "blocked": False}

    # Special check: Unblock Route 21 from Pallet Town once player has used Surf
    if matching_exit == "Route 21" and current.name == "Pallet Town":
        surf_unlocked = game_state.game_data.get("surf_unlocked", [])
        if "Route 21" in surf_unlocked or game_state.cheat_mode:
            exit_data = {**exit_data, "blocked": False}

    # Special check: Unblock Route 19 from Fuchsia City once player has used Surf
    if matching_exit == "Route 19" and current.name == "Fuchsia City":
        surf_unlocked = game_state.game_data.get("surf_unlocked", [])
        if "Route 19" in surf_unlocked or game_state.cheat_mode:
            exit_data = {**exit_data, "blocked": False}

    # Special check: Unblock Route 20 from Route 19 once player has used Surf
    if matching_exit == "Route 20" and current.name == "Route 19":
        surf_unlocked = game_state.game_data.get("surf_unlocked", [])
        if "Route 20" in surf_unlocked or game_state.cheat_mode:
            exit_data = {**exit_data, "blocked": False}

    # Special check: Unblock Route 21 from Cinnabar Island once player has used Surf
    if matching_exit == "Route 21" and current.name == "Cinnabar Island":
        surf_unlocked = game_state.game_data.get("surf_unlocked", [])
        if "Route 21" in surf_unlocked or game_state.cheat_mode:
            exit_data = {**exit_data, "blocked": False}
        else:
            exit_data = {
                **exit_data,
                "blocked": True,
                "reason": "Route 21 is open water. You need a Pokemon that knows Surf.",
            }

    # Gate A: Saffron City gates (from Route 7 or Route 8) — requires marsh_badge or silph_co_cleared
    if matching_exit == "Saffron City":
        badges = game_state.game_data.get("badges", [])
        story_flags = game_state.game_data.get("story_flags", {})
        if "marsh_badge" not in badges and not story_flags.get("silph_co_cleared", False):
            exit_data = {
                **exit_data,
                "blocked": True,
                "reason": (
                    "The gates to Saffron City are sealed. "
                    "The Silph Co. employees won't let anyone through "
                    "until the situation is resolved."
                ),
            }

    # Gate B: Victory Road — requires all 8 badges (including Earth Badge from Giovanni)
    if matching_exit == "Victory Road":
        badges = game_state.game_data.get("badges", [])
        if "earth_badge" not in badges:
            exit_data = {
                **exit_data,
                "blocked": True,
                "reason": "The gate to Victory Road is locked. You need all 8 Badges to pass.",
            }

    if exit_data.get("blocked", False) and not game_state.cheat_mode:
        reason = exit_data.get("reason", "This path is blocked")
        output.write("")
        output.write(f"[yellow]⚠ {reason}[/yellow]")
        output.write("")
        return

    # Check min_explores requirement for forward exits.
    # Skip entirely when heading back to where the player came from.
    previous_location = game_state.game_data.get("previous_location")
    is_backtracking = previous_location and matching_exit == previous_location
    required = current.get_exit_min_explores(matching_exit)
    done = game_state.get_route_progress(current.name)
    if required > 0 and done < required and not game_state.cheat_mode and not is_backtracking:
        remaining = required - done
        output.write("")
        output.write(f"[yellow]⚠ You haven't fully explored {current.name} yet![/yellow]")
        output.write(
            f"[dim]Explore the area {remaining} more time(s) before heading to {matching_exit}.[/dim]"
        )
        output.write(
            f"[dim]Progress: {done}/{required} — use 'Explore' to continue searching[/dim]"
        )
        output.write("")
        return

    # Special check: Block Route 1 from Pallet Town if no Pokemon
    pokemon = game_state.game_data.get("pokemon", [])
    if (
        matching_exit == "Route 1"
        and current.name == "Pallet Town"
        and not pokemon
        and not game_state.cheat_mode
    ):
        output.write("")
        output.write("[bold red]Professor Oak:[/bold red] [cyan]Wait! Don't go out there![/cyan]")
        output.write("")
        output.write("[cyan]   It's dangerous to go alone without a Pokemon![/cyan]")
        output.write("[cyan]   Come to my lab and I'll give you your first Pokemon![/cyan]")
        output.write("")
        return

    # Move to the new location
    new_location = get_location(matching_exit)
    if not new_location:
        output.write(f"[red]❌ Error: Location '{matching_exit}' not found[/red]")
        return

    game_state.game_data["previous_location"] = current.name
    game_state.current_location = new_location
    game_state.game_data["location"] = new_location.name
    # Reset explore counter for the destination — requirements apply fresh every visit
    game_state.game_data.setdefault("route_progress", {})[new_location.name] = 0

    # Autosave silently on every location change
    autosave_path = game_state.autosave_on_location_change()

    # Display arrival message
    output.write("")
    output.write(f"[bold cyan]➜ Traveling to {new_location.name}...[/bold cyan]")
    if autosave_path:
        output.write(f"[dim]  💾 Autosaved to {autosave_path.name}[/dim]")
    output.write("")

    # Show the location details
    show_arrival_callback(output)


def prompt_for_location(
    game_state: "GameState", output: RichLog, set_pending_command_callback, show_panel_callback=None
) -> None:
    """Show available locations and wait for user to choose."""
    if not game_state.current_location:
        output.write("[red]❌ Error: No current location set[/red]")
        return

    current = game_state.current_location
    available_exits = current.get_available_exits()

    if not available_exits:
        output.write("")
        output.write("[yellow]⚠ There are no available paths from here[/yellow]")
        output.write("")
        return

    output.write("")
    output.write("[bold cyan]🗺️  Where would you like to go?[/bold cyan]")
    output.write("")
    output.write("[bold green]Available destinations:[/bold green]")

    for exit_name in available_exits:
        exit_data = current.exits[exit_name]
        direction = exit_data.get("direction", "")
        dest_location = get_location(exit_name)

        if direction:
            output.write(f"  ➜ [green]{exit_name}[/green] ({direction})")
        else:
            output.write(f"  ➜ [green]{exit_name}[/green]")

        if dest_location:
            output.write(f"     [dim]{dest_location.description}[/dim]")

    output.write("")

    # Use panel callback if provided, otherwise show text-based prompt
    if show_panel_callback:
        output.write("[yellow]Select a destination from the menu above[/yellow]")
        output.write("")
        show_panel_callback(available_exits)
    else:
        output.write("[yellow]Type the name of the location you want to visit:[/yellow]")
        output.write("[dim](or type 'cancel' to go back)[/dim]")
        output.write("")

    set_pending_command_callback("move_to")


def prompt_for_building(
    game_state: "GameState", output: RichLog, set_pending_command_callback, show_panel_callback=None
) -> None:
    """Show available buildings and wait for user to choose."""
    if not game_state.current_location:
        output.write("[red]❌ Error: No current location set[/red]")
        return

    current = game_state.current_location

    if not current.buildings:
        output.write("")
        output.write("[yellow]⚠ There are no buildings here to enter[/yellow]")
        output.write("[dim]You can only enter buildings in towns and cities[/dim]")
        output.write("")
        return

    output.write("")
    output.write("[bold cyan]🏛️  Which building would you like to enter?[/bold cyan]")
    output.write("")
    output.write("[bold green]Available buildings:[/bold green]")

    for building in current.buildings:
        output.write(f"  🏛️  [green]{building}[/green]")

    if current.blocked_buildings:
        output.write("")
        output.write("[dim]Blocked buildings:[/dim]")
        for building, reason in current.blocked_buildings.items():
            output.write(f"  [dim]🔒 {building} - {reason}[/dim]")

    output.write("")

    # Use panel callback if provided, otherwise show text-based prompt
    if show_panel_callback:
        output.write("[yellow]Select a building from the menu above[/yellow]")
        output.write("")
        show_panel_callback(current.buildings)
    else:
        output.write("[yellow]Type the name of the building you want to enter:[/yellow]")
        output.write("[dim](or type 'cancel' to go back)[/dim]")
        output.write("")

    set_pending_command_callback("enter_building")


def show_location_arrival(game_state: "GameState", output: RichLog, is_load: bool = False) -> None:
    """Display location arrival information with available actions."""
    if not game_state.current_location:
        output.write("[red]❌ Error: No current location set[/red]")
        return

    location = game_state.current_location

    # Header
    output.write("[bold green]" + "═" * 50 + "[/bold green]")
    output.write(f"[bold cyan]📍 {location.name.upper()}[/bold cyan]")
    output.write("[bold green]" + "═" * 50 + "[/bold green]")
    output.write("")

    # Arrival text
    if is_load:
        output.write(f"[bold]You find yourself in {location.name}.[/bold]")
    else:
        output.write(f"[bold]You have arrived in {location.name}.[/bold]")

    output.write(f"[dim]{location.description}[/dim]")
    output.write("")

    # First-visit rich narrative for key Phase 4 locations
    story_flags = game_state.game_data.setdefault("story_flags", {})
    _visited_key = f"visited_{location.name.lower().replace(' ', '_')}"
    if not story_flags.get(_visited_key):
        story_flags[_visited_key] = True
        if location.name == "Saffron City":
            output.write("[bold cyan]🏙️  Saffron City[/bold cyan]")
            output.write(
                "[dim]The largest city in Kanto. Silph Co.'s tower looms over the skyline...[/dim]"
            )
            output.write("[red]Team Rocket has seized Silph Co.! The city is in a panic.[/red]")
            output.write("")
        elif location.name == "Cinnabar Island":
            output.write("[bold red]🌋  Cinnabar Island[/bold red]")
            output.write(
                "[dim]The smell of sulphur hangs in the sea air."
                " An ancient volcano looms behind the research complex.[/dim]"
            )
            output.write(
                "[dim]Burnt ruins of the Pokemon Mansion are visible just south of the lab.[/dim]"
            )
            output.write("")
        elif location.name == "Victory Road":
            output.write("[bold yellow]⛰️  Victory Road[/bold yellow]")
            output.write(
                "[dim]This treacherous cave connects Viridian City to the Pokemon League.[/dim]"
            )
            output.write("[bold]Only the strongest trainers dare to enter...[/bold]")
            output.write("")
        elif location.name == "Pokemon League":
            output.write("[bold yellow]🏆  The Pokémon League — Indigo Plateau[/bold yellow]")
            badges_count = len(game_state.game_data.get("badges", []))
            output.write(f"   [dim]You have {badges_count} of 8 badges.[/dim]")
            if story_flags.get("defeated_champion"):
                output.write("   [bold gold1]★ You are the Pokémon Champion! ★[/bold gold1]")
            elif story_flags.get("defeated_lance"):
                output.write("   [cyan]The Champion awaits...[/cyan]")
            elif story_flags.get("defeated_agatha"):
                output.write("   [cyan]Lance, the Dragon Master, waits ahead.[/cyan]")
            elif story_flags.get("defeated_bruno"):
                output.write("   [cyan]Agatha of the Ghost Elite Four awaits.[/cyan]")
            elif story_flags.get("defeated_lorelei"):
                output.write("   [cyan]Bruno, master of Fighting types, is next.[/cyan]")
            else:
                output.write("   [cyan]Lorelei awaits you in the first chamber.[/cyan]")
            output.write("")

    # Build the activities description
    activities = []

    # Add buildings
    if location.buildings:
        building_list = format_list(location.buildings, "the")
        activities.append(f"visit {building_list}")

    # Add exploration option
    if location.can_explore():
        activities.append("explore the area")

    # Add movement as final option
    if activities:
        activities.append("continue your journey")

    # Show activities if any
    if activities:
        if len(activities) == 1:
            output.write(f"Here you can {activities[0]}.")
        elif len(activities) == 2:
            output.write(f"Here you can {activities[0]} or {activities[1]}.")
        else:
            activity_text = ", ".join(activities[:-1]) + f", or {activities[-1]}"
            output.write(f"Here you can {activity_text}.")
        output.write("")

    # Show available paths
    available_exits = location.get_available_exits()
    if available_exits:
        previous_location = game_state.game_data.get("previous_location")
        output.write(f"[bold yellow]From {location.name} you can travel to:[/bold yellow]")
        for exit_name in available_exits:
            exit_data = location.exits[exit_name]
            direction = exit_data.get("direction", "")
            back_tag = " [cyan]↩ back[/cyan]" if exit_name == previous_location else ""

            # Get destination description
            dest_location = get_location(exit_name)
            if dest_location:
                description = get_travel_description(exit_name, dest_location)
                if direction:
                    output.write(
                        f"  • [cyan]{exit_name}[/cyan] ({direction}) - {description}{back_tag}"
                    )
                else:
                    output.write(f"  • [cyan]{exit_name}[/cyan] - {description}{back_tag}")
            else:
                output.write(f"  • [cyan]{exit_name}[/cyan]{back_tag}")
        output.write("")

    # Show blocked buildings if any
    if location.blocked_buildings:
        output.write("[dim]Note:[/dim]")
        for building, reason in location.blocked_buildings.items():
            output.write(f"  [dim]🔒 {building} - {reason}[/dim]")
        output.write("")

    # Show exploration hint
    if location.can_explore():
        output.write(
            "[yellow]💡 Tip:[/yellow] Use the [cyan]'Explore'[/cyan] command to search this area"
        )
        if location.wild_pokemon:
            output.write("[dim]   for wild Pokemon encounters[/dim]")
        forward_exits = [
            (n, d["min_explores"])
            for n, d in location.exits.items()
            if d.get("min_explores", 0) > 0
        ]
        if forward_exits and any(
            game_state.get_route_progress(location.name) < req for _, req in forward_exits
        ):
            output.write("[dim]   Explore this area to unlock forward paths.[/dim]")
        output.write("")

    output.write("[dim]Type 'Help' to see all available commands[/dim]")
    output.write("")


def look_around(game_state: "GameState", output: RichLog, auto: bool = False) -> None:
    """Look around the current location."""
    if not game_state.current_location:
        output.write("[red]❌ Error: No current location set[/red]")
        return

    location = game_state.current_location

    if not auto:
        output.write("")
        output.write(f"[bold cyan]👀 Looking around {location.name}...[/bold cyan]")
        output.write("")

    # Show buildings if it's a town
    if location.type == "town":
        if location.buildings:
            output.write("[bold yellow]Buildings:[/bold yellow]")
            for building in location.buildings:
                output.write(f"  🏛️  {building}")
            output.write("")

        if location.blocked_buildings:
            output.write("[dim]Blocked Buildings:[/dim]")
            for building, reason in location.blocked_buildings.items():
                output.write(f"  [dim]🔒 {building} - {reason}[/dim]")
            output.write("")

    # Show exploration hint for routes/forests
    if location.can_explore():
        output.write("[yellow]💡 This area can be explored[/yellow]")
        if location.wild_pokemon:
            output.write("[dim]   Wild Pokemon may appear when exploring[/dim]")
        if location.trainers > 0:
            output.write(f"[dim]   {location.trainers} trainer(s) may challenge you[/dim]")
        forward_exits = [
            (n, d["min_explores"])
            for n, d in location.exits.items()
            if d.get("min_explores", 0) > 0
        ]
        if forward_exits:
            previous_location = game_state.game_data.get("previous_location")
            progress = game_state.get_route_progress(location.name)
            for exit_name, req in forward_exits:
                if exit_name == previous_location:
                    output.write(
                        f"  [dim]→ {exit_name}: [cyan]↩ back (no explores needed)[/cyan][/dim]"
                    )
                elif progress >= req:
                    bar = "█" * req
                    output.write(f"  [dim]→ {exit_name}: [{bar}] ✓ Unlocked[/dim]")
                else:
                    bar = "█" * progress + "░" * (req - progress)
                    output.write(f"  [dim]→ {exit_name}: [{bar}] {progress}/{req}[/dim]")
        hint = get_explore_hint(game_state)
        if hint:
            output.write(hint)
        output.write("")

    # Show available exits
    available_exits = location.get_available_exits()
    if available_exits:
        previous_location = game_state.game_data.get("previous_location")
        output.write("[bold green]Available Paths:[/bold green]")
        for exit_name in available_exits:
            direction = location.exits[exit_name].get("direction", "")
            direction_str = f" ({direction})" if direction else ""
            if exit_name == previous_location:
                output.write(f"  ➜ {exit_name}{direction_str} [cyan]↩ back[/cyan]")
            else:
                output.write(f"  ➜ {exit_name}{direction_str}")
        output.write("")

    # Show blocked exits
    blocked_exits = location.get_blocked_exits()
    if blocked_exits:
        output.write("[dim]Blocked Paths:[/dim]")
        for exit_name, reason in blocked_exits.items():
            output.write(f"  [dim]🔒 {exit_name} - {reason}[/dim]")
        output.write("")


# ---------------------------------------------------------------------------
# Canonical ground items — based on Gen 1 (Red/Blue) item placements
# ---------------------------------------------------------------------------
# Each location maps to an ordered list of items that can be found there.
# Items are awarded one at a time as the player explores.  Once all items
# for a location are found they are gone for that save — finder is tracked
# in game_state.game_data["found_items"][location_name] as a simple count.
#
# Sources: Serebii.net/rb/items and Smogon Orange Islands hidden-items guide.

_GROUND_ITEMS: dict[str, list[str]] = {
    # ── Early game ───────────────────────────────────────────────────────────
    "Route 1": ["Potion"],
    "Route 2 South": ["HP Up", "Potion"],
    "Route 2 North": ["Antidote", "Moon Stone"],
    "Viridian Forest": ["Pokeball", "Antidote", "Potion", "Awakening", "Pokeball"],
    "Route 22": ["Super Potion"],
    # ── Mt. Moon corridor ────────────────────────────────────────────────────
    "Route 3": ["Potion", "Super Potion"],
    "Mt. Moon": [
        "Escape Rope",
        "Potion",
        "Moon Stone",
        "Rare Candy",
        "HP Up",
        "Potion",
        "Moon Stone",
    ],
    "Route 4": ["Antidote", "Super Potion"],
    # ── Cerulean area ────────────────────────────────────────────────────────
    "Route 24": ["Super Potion", "Repel"],
    "Route 25": ["Super Potion"],
    "Route 9": ["Super Potion", "Repel"],
    "Route 10": ["Hyper Potion", "Super Repel"],
    # ── Vermillion area ──────────────────────────────────────────────────────
    "Route 6": ["Super Potion"],
    "Route 11": ["Super Potion", "Super Potion"],
    # ── Lavender Town area ───────────────────────────────────────────────────
    "Pokemon Tower": [
        "Escape Rope",
        "Awakening",
        "Revive",
        "Super Potion",
        "Awakening",
        "Rare Candy",
    ],
    # ── Celadon area ─────────────────────────────────────────────────────────
    "Route 8": ["Super Potion", "Full Heal"],
    "Team Rocket's Hideout": [
        "Full Restore",
        "Hyper Potion",
        "Revive",
        "Escape Rope",
        "Full Heal",
        "Max Potion",
        "Nugget",
    ],
    # ── Later routes ─────────────────────────────────────────────────────────
    "Route 12": ["Iron", "Super Potion"],
    "Route 13": ["Protein", "Full Heal"],
    "Route 14": ["Full Heal"],
    "Route 15": ["Super Repel", "Full Heal"],
    "Route 16": ["Rare Candy", "Repel"],
    "Route 17": ["Full Restore", "Super Repel"],
    "Route 18": ["Hyper Potion"],
    # ── Victory Road area ────────────────────────────────────────────────────
    "Route 21": ["Hyper Potion", "Super Potion"],
    "Route 22 North": ["Super Potion"],
    "Victory Road": ["Full Restore", "Full Heal", "Max Potion"],
    # ── Pokemon League ───────────────────────────────────────────────────────
    "Pokemon League": ["Full Restore", "Max Revive", "Elixir"],
}

# Item emojis for the found-item message
_ITEM_EMOJI: dict[str, str] = {
    "Potion": "💊",
    "Super Potion": "💊",
    "Hyper Potion": "💊",
    "Max Potion": "💊",
    "Full Restore": "✨",
    "Antidote": "🧪",
    "Paralyze Heal": "⚡",
    "Awakening": "☀️",
    "Burn Heal": "🧊",
    "Full Heal": "🌟",
    "Revive": "💫",
    "Rare Candy": "🍬",
    "Pokeball": "🔴",
    "Repel": "🪢",
    "Super Repel": "🪢",
    "Escape Rope": "🪢",
    "HP Up": "❤️",
    "Protein": "💪",
    "Iron": "🛡️",
    "Calcium": "🔹",
    "Carbos": "⚡",
    "Moon Stone": "🌙",
    "Great Ball": "🔵",
    "X Speed": "⚡",
    "X Attack": "⚔️",
    "Nugget": "💛",
}

# Probability that any given explore attempt finds the next ground item.
# ~5 %: rare enough to feel like a discovery, not a vending machine.
_ITEM_FIND_CHANCE = 0.05


def _try_find_item(game_state: "GameState", location_name: str, output: RichLog) -> bool:
    """
    Attempt to find the next ground item at *location_name*.

    Items are awarded in list order from ``_GROUND_ITEMS``.  Once the list is
    exhausted the function is a no-op for that location.  Progress is persisted
    in ``game_state.game_data["found_items"][location_name]``.

    Returns True if an item was actually given (caller skips encounter roll).
    """
    pool = _GROUND_ITEMS.get(location_name)
    if not pool:
        return False

    found_map: dict = game_state.game_data.setdefault("found_items", {})
    already = found_map.get(location_name, 0)

    if already >= len(pool):
        return False  # all items for this location collected

    if random.random() >= _ITEM_FIND_CHANCE:
        return False

    item_name = pool[already]
    found_map[location_name] = already + 1

    # Add to bag
    items = game_state.game_data.setdefault("items", {})
    items[item_name] = items.get(item_name, 0) + 1

    emoji = _ITEM_EMOJI.get(item_name, "✨")
    output.write(f"{emoji} [bold green]You found {item_name}![/bold green]")
    lower = location_name.lower()
    if "cave" in lower or "mountain" in lower or "mt." in lower or "tunnel" in lower:
        flavour = "It was tucked behind a rock."
    elif "forest" in lower:
        flavour = "It was buried under some leaves."
    elif "tower" in lower:
        flavour = "It was resting on a memorial shelf."
    elif "hideout" in lower or "rocket" in lower:
        flavour = "It was stashed in a Rocket crate."
    elif "anne" in lower or "s.s." in lower:
        flavour = "It was left on a cabin shelf."
    else:
        flavour = "It was hidden in the tall grass."
    output.write(f"[dim]   {flavour} Added to your bag.[/dim]")
    remaining = len(pool) - (already + 1)
    if remaining > 0:
        output.write(
            f"[dim]   (You sense {remaining} more hidden item{'s' if remaining > 1 else ''} nearby...)[/dim]"
        )
    output.write("")
    return True


def explore_area(
    game_state: "GameState", output: RichLog, trigger_wild_callback, trigger_trainer_callback
) -> None:
    """Explore the current area for wild Pokemon encounters and trainers."""
    if not game_state.current_location:
        output.write("[red]❌ Error: No current location set[/red]")
        return

    location = game_state.current_location

    if not location.can_explore():
        output.write("")
        output.write(f"[yellow]⚠ There's nothing to explore in {location.name}[/yellow]")
        output.write("[dim]You can only explore routes and forests[/dim]")
        output.write("")
        return

    output.write("")
    output.write(f"[bold cyan]🔍 Exploring {location.name}...[/bold cyan]")
    output.write("")

    # Check for undefeated trainers first (60% chance to encounter if available)
    trainers = get_trainers_by_location(location.name)
    defeated_ids = game_state.game_data.get("defeated_trainers", [])
    available_trainers = [t for t in trainers if t["id"] not in defeated_ids]

    pokemon_list = game_state.game_data.get("pokemon", [])
    if not pokemon_list:
        output.write("[yellow]⚠ You can't explore without Pokemon![/yellow]")
        output.write("[dim]Get a starter from Professor Oak's Lab first[/dim]")
        output.write("")
        return

    # Prioritize trainer encounters
    if available_trainers and random.random() < location.trainer_encounter_rate:
        # Encounter a random undefeated trainer
        trainer = random.choice(available_trainers)
        game_state.increment_route_progress(location.name)
        _stats.record_explore(game_state, location.name)
        trigger_trainer_callback(output, trainer)
        return

    # Otherwise check for wild Pokemon
    if not location.wild_pokemon:
        output.write("[dim]You search the area but find nothing...[/dim]")
        output.write("")
        return

    # Small chance to find a ground item before any encounter roll
    if _try_find_item(game_state, location.name, output):
        game_state.increment_route_progress(location.name)
        _stats.record_explore(game_state, location.name)
        return

    # Bicycle halves wild encounter rate and counts as 2 explores per trip
    cycling = game_state.game_data.get("cycling", False)
    explore_step = 2 if cycling else 1
    wild_encounter_rate = location.wild_encounter_rate
    if cycling:
        wild_encounter_rate = wild_encounter_rate * 0.5

    if random.random() < wild_encounter_rate:
        # Check repel — if active, halve chance and drain one step
        repel_steps = game_state.game_data.get("repel_steps", 0)
        if repel_steps > 0:
            game_state.game_data["repel_steps"] = repel_steps - 1
            remaining = repel_steps - 1
            if random.random() < 0.5:
                # Repel suppressed this encounter
                game_state.increment_route_progress(location.name, explore_step)
                _stats.record_explore(game_state, location.name)
                output.write("[dim]🪢 The Repel keeps wild Pokemon away...[/dim]")
                if remaining > 0:
                    output.write(f"[dim]   ({remaining} explore(s) of Repel remaining)[/dim]")
                else:
                    output.write("[dim]   The Repel wore off![/dim]")
                output.write("")
                return
        game_state.increment_route_progress(location.name, explore_step)
        _stats.record_explore(game_state, location.name)
        trigger_wild_callback(output)
    else:
        game_state.increment_route_progress(location.name, explore_step)
        _stats.record_explore(game_state, location.name)
        if cycling:
            output.write("[cyan]🚲 You zip through the area on your Bicycle![/cyan]")
        else:
            output.write("[dim]You search the tall grass but nothing jumps out...[/dim]")
        hint = get_explore_hint(game_state)
        if hint:
            output.write(hint)
        output.write("")
        # Mt. Moon one-time discoveries
        if location.name == "Mt. Moon":
            _story_flags = game_state.game_data.setdefault("story_flags", {})
            if not _story_flags.get("received_moon_stone") and random.random() < 0.40:
                _story_flags["received_moon_stone"] = True
                _items = game_state.game_data.setdefault("items", {})
                _items["Moon Stone"] = _items.get("Moon Stone", 0) + 1
                output.write("")
                output.write(
                    "[bold magenta]✨ You spot something glinting in the cave wall![/bold magenta]"
                )
                output.write(
                    "[magenta]   It's a [bold]Moon Stone[/bold]! You carefully pry it loose.[/magenta]"
                )
                output.write("[bold green]✓ Found a Moon Stone![/bold green]")
                output.write("[dim]   (Causes certain Pokemon to evolve when used)[/dim]")
                output.write("")
            if not _story_flags.get("received_mt_moon_fossil") and random.random() < 0.30:
                _story_flags["received_mt_moon_fossil"] = True
                _fossil = random.choice(["Dome Fossil", "Helix Fossil"])
                _items = game_state.game_data.setdefault("items", {})
                _items[_fossil] = _items.get(_fossil, 0) + 1
                output.write("")
                output.write(
                    "[bold yellow]🦴 You find a fossil embedded in the cave wall![/bold yellow]"
                )
                output.write(
                    f"[yellow]   With great care you extract a [bold]{_fossil}[/bold]![/yellow]"
                )
                output.write(f"[bold green]✓ Found a {_fossil}![/bold green]")
                output.write(
                    "[dim]   (A scientist might be able to revive the Pokemon inside)[/dim]"
                )
                output.write("")
        # ── Pokemon Tower: Ghost encounter & Mr. Fuji rescue ──────────────────
        elif location.name == "Pokemon Tower":
            _tower_flags = game_state.game_data.setdefault("story_flags", {})
            _bag = game_state.game_data.setdefault("items", {})
            has_silph_scope = bool(_bag.get("Silph Scope", 0))
            if not _tower_flags.get("ghost_encounter_shown") and random.random() < 0.40:
                _tower_flags["ghost_encounter_shown"] = True
                output.write("")
                output.write(
                    "[bold magenta]👻 A shadowy figure blocks the stairs...[/bold magenta]"
                )
                if has_silph_scope:
                    output.write("[magenta]   Through the Silph Scope you see clearly:[/magenta]")
                    output.write("[magenta]   It's the ghost of a [bold]MAROWAK[/bold]![/magenta]")
                    output.write(
                        "[magenta]   The vengeful spirit of a mother protecting her child...[/magenta]"
                    )
                    output.write(
                        "[magenta]   You feel the Silph Scope resonate and the ghost fades.[/magenta]"
                    )
                    output.write("")
                    output.write(
                        "[dim]   (With the Silph Scope you can now identify and battle ghost Pokemon)[/dim]"
                    )
                else:
                    output.write(
                        "[magenta]   The ghost cannot be identified — your Pokeballs pass right through![/magenta]"
                    )
                    output.write("[magenta]   You retreat to a lower floor, shaken.[/magenta]")
                    output.write("")
                    output.write(
                        "[yellow]⚠ Tip:[/yellow] [dim]You need the Silph Scope to battle the ghost Pokemon here.[/dim]"
                    )
                    output.write(
                        "[dim]   The Silph Scope is said to be held by Team Rocket...[/dim]"
                    )
                output.write("")
            if (
                not _tower_flags.get("rescued_mr_fuji")
                and has_silph_scope
                and game_state.get_route_progress(location.name) >= 8
                and random.random() < 0.35
            ):
                _tower_flags["rescued_mr_fuji"] = True
                _bag["Poke Flute"] = _bag.get("Poke Flute", 0) + 1
                output.write("")
                output.write("[bold cyan]🏠 You reach the top of Pokemon Tower...[/bold cyan]")
                output.write("[cyan]   Team Rocket Grunts scatter as you approach![/cyan]")
                output.write("")
                output.write(
                    "[bold]Mr. Fuji:[/bold] [cyan]Oh my... a young trainer, here to rescue me![/cyan]"
                )
                output.write("[cyan]   Those dreadful Team Rocket villains imprisoned me![/cyan]")
                output.write("[cyan]   Please — take this Poke Flute as thanks.[/cyan]")
                output.write(
                    "[cyan]   It will wake the sleeping Pokemon that block your path.[/cyan]"
                )
                output.write("")
                output.write("[bold yellow]★ Received Poke Flute! ★[/bold yellow]")
                output.write(
                    "[dim]   The Poke Flute wakes sleeping Snorlax blocking certain routes.[/dim]"
                )
                output.write("")
        # ── Team Rocket's Hideout: Lift Key & Silph Scope from Giovanni ───────
        elif location.name == "Team Rocket's Hideout":
            _rocket_flags = game_state.game_data.setdefault("story_flags", {})
            _bag = game_state.game_data.setdefault("items", {})
            if not _rocket_flags.get("found_lift_key") and random.random() < 0.25:
                _rocket_flags["found_lift_key"] = True
                _bag["Lift Key"] = _bag.get("Lift Key", 0) + 1
                output.write("")
                output.write(
                    "[bold yellow]🗝️  A small key glints under a fallen crate...[/bold yellow]"
                )
                output.write("[yellow]   The tag reads: [bold]LIFT KEY — B4F[/bold].[/yellow]")
                output.write("[bold green]✓ Found the Lift Key![/bold green]")
                output.write(
                    "[dim]   Use this key to reach the lower floors and confront the Rocket Boss.[/dim]"
                )
                output.write("")
            if (
                not _rocket_flags.get("defeated_giovanni_hideout")
                and _rocket_flags.get("found_lift_key")
                and game_state.get_route_progress(location.name) >= 10
                and random.random() < 0.30
            ):
                _rocket_flags["defeated_giovanni_hideout"] = True
                _bag["Silph Scope"] = _bag.get("Silph Scope", 0) + 1
                output.write("")
                output.write(
                    "[bold red]🚀 You reach the deepest level of the Hideout...[/bold red]"
                )
                output.write("[red]   Giovanni stares at you with cold contempt.[/red]")
                output.write("")
                output.write("[bold]Giovanni:[/bold] [red]So... you've made it this far.[/red]")
                output.write("[red]   I am Giovanni — the Boss of Team Rocket.[/red]")
                output.write(
                    "[red]   You have some skill. But skill alone does not impress me.[/red]"
                )
                output.write("[red]   ...You win. Take the Silph Scope.[/red]")
                output.write("[red]   It is useless to us if we cannot hold this base.[/red]")
                output.write("[red]   Team Rocket will retreat... for now.[/red]")
                output.write("")
                output.write("[bold yellow]★ Received Silph Scope! ★[/bold yellow]")
                output.write(
                    "[dim]   The Silph Scope lets you identify ghost Pokemon in Pokemon Tower.[/dim]"
                )
                output.write("")


def get_explore_hint(game_state: "GameState") -> str:
    """
    Return a short contextual hint about exploration progress for the
    current route/forest location.  Empty string for towns.

    Args:
        game_state: The game state object

    Returns:
        A Rich-markup string describing progress, or "" for towns.
    """
    loc = game_state.current_location
    if not loc or not loc.can_explore():
        return ""

    done = game_state.get_route_progress(loc.name)
    prev = game_state.game_data.get("previous_location")

    # Collect forward exits (not where we came from, not blocked)
    forward_exits = [
        (name, data)
        for name, data in loc.exits.items()
        if not data.get("blocked", False) and name != prev
    ]

    if not forward_exits:
        return ""

    # Build per-destination status lines
    lines = []
    all_ready = True
    for dest_name, exit_data in forward_exits:
        required = exit_data.get("min_explores", 0)
        if required == 0:
            lines.append((dest_name, 0, 0, True))  # no gate
        elif done >= required:
            lines.append((dest_name, done, required, True))
        else:
            lines.append((dest_name, done, required, False))
            all_ready = False

    # Compose a human-readable hint
    if len(lines) == 1:
        dest_name, done, required, ready = lines[0]
        if required == 0:
            return f"[dim]The path to [cyan]{dest_name}[/cyan] is open — move ahead when you're ready.[/dim]"
        remaining = required - done
        bar_filled = int((done / required) * 8)
        bar = "█" * bar_filled + "░" * (8 - bar_filled)
        if ready:
            return (
                f"[dim][cyan]{dest_name}[/cyan] is within reach! "
                f"Move ahead or linger a while longer. [{bar}][/dim]"
            )
        elif remaining == 1:
            return (
                f"[dim]You can almost see [cyan]{dest_name}[/cyan] — "
                f"one last look around should do it. [{bar}][/dim]"
            )
        elif done < required / 2:
            return (
                f"[dim]There's plenty left to discover here before heading to "
                f"[cyan]{dest_name}[/cyan]. Keep exploring. [{bar}][/dim]"
            )
        else:
            return (
                f"[dim]You're getting the lay of the land — "
                f"a little more exploration and [cyan]{dest_name}[/cyan] will be within reach. [{bar}][/dim]"
            )
    else:
        # Multiple forward exits
        parts = []
        for dest_name, done, required, ready in lines:
            if required == 0 or ready:
                parts.append(f"[cyan]{dest_name}[/cyan] [green](open)[/green]")
            else:
                remaining = required - done
                if remaining == 1:
                    parts.append(f"[cyan]{dest_name}[/cyan] (almost there)")
                elif done < required / 2:
                    parts.append(f"[cyan]{dest_name}[/cyan] (more exploring needed)")
                else:
                    parts.append(f"[cyan]{dest_name}[/cyan] (getting close)")
        dest_list = " and ".join(parts)
        if all_ready:
            return f"[dim]The paths ahead are clear — {dest_list}. Move when ready.[/dim]"
        else:
            return f"[dim]Paths ahead: {dest_list}. Keep exploring to advance.[/dim]"
