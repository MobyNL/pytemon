"""
Exploration and movement handlers for Pokemon Terminal.

This module handles location navigation, area exploration, and related displays.
"""

import random
from dataclasses import replace as _dataclass_replace
from typing import TYPE_CHECKING

from textual.widgets import RichLog

from . import stats as _stats
from .data import get_trainers_by_location
from .locations import get_location
from .texts.en import exploration as T  # noqa: N812
from .ui.formatters import format_list, get_travel_description, write_lines, write_lines_fmt

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
        write_lines(output, T.ERROR_NO_CURRENT_LOCATION)
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
        write_lines_fmt(
            output,
            T.CANT_GO_THERE,
            destination=destination,
            location=current.name,
        )
        return

    # Check if the exit is blocked
    exit_data = current.exits[matching_exit]

    # Safari Zone can only be entered via the building ("enter safari zone reception"),
    # not via "move to".
    if matching_exit == "Safari Zone":
        write_lines(output, T.SAFARI_ZONE_ENTER_BUILDING)
        return

    # Safari Zone can only be left via "exit safari zone", not via "move to".
    if current.name == "Safari Zone":
        write_lines(output, T.SAFARI_ZONE_EXIT_COMMAND)
        return

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

    # Gate C: Cerulean Cave — requires being Champion
    if matching_exit == "Cerulean Cave":
        story_flags = game_state.game_data.get("story_flags", {})
        if story_flags.get("is_champion"):
            exit_data = {**exit_data, "blocked": False}
        else:
            exit_data = {
                **exit_data,
                "blocked": True,
                "reason": (
                    "The cave is sealed with heavy barriers. "
                    'A guard says: "Only the Pokemon Champion may enter."'
                ),
            }

    # Gate D: Champion's Garden — requires being Champion
    if matching_exit == "Champion's Garden":
        story_flags = game_state.game_data.get("story_flags", {})
        if story_flags.get("is_champion"):
            exit_data = {**exit_data, "blocked": False}
        else:
            exit_data = {
                **exit_data,
                "blocked": True,
                "reason": exit_data.get("reason", "This hidden path is only visible to Champions."),
            }

    # Seafoam Islands and Power Plant require Surf
    if matching_exit in ("Seafoam Islands", "Power Plant"):
        surf_unlocked = game_state.game_data.get("surf_unlocked", [])
        if matching_exit not in surf_unlocked and not game_state.cheat_mode:
            exit_data = {
                **exit_data,
                "blocked": True,
                "reason": f"You need HM Surf to reach {matching_exit}.",
            }

    if exit_data.get("blocked", False) and not game_state.cheat_mode:
        reason = exit_data.get("reason", "This path is blocked")
        write_lines_fmt(output, T.EXIT_BLOCKED_REASON, reason=reason)
        return

    # Check min_explores requirement for forward exits.
    # Skip entirely when heading back to where the player came from.
    previous_location = game_state.game_data.get("previous_location")
    is_backtracking = previous_location and matching_exit == previous_location
    required = current.get_exit_min_explores(matching_exit)
    done = game_state.get_route_progress(current.name)
    if required > 0 and done < required and not game_state.cheat_mode and not is_backtracking:
        remaining = required - done
        write_lines_fmt(
            output,
            T.NOT_ENOUGH_EXPLORES,
            location=current.name,
            remaining=remaining,
            destination=matching_exit,
            done=done,
            required=required,
        )
        return

    # Special check: Block Route 1 from Pallet Town if no Pokemon
    pokemon = game_state.game_data.get("pokemon", [])
    if (
        matching_exit == "Route 1"
        and current.name == "Pallet Town"
        and not pokemon
        and not game_state.cheat_mode
    ):
        write_lines(output, T.OAK_NO_POKEMON_WARNING)
        return

    # Move to the new location
    new_location = get_location(matching_exit)
    if not new_location:
        write_lines_fmt(output, T.LOCATION_NOT_FOUND, location_name=matching_exit)
        return

    # Exit the current dungeon if applicable (before updating current_location)
    from .dungeon import exit_dungeon as _exit_dungeon, get_dungeon_for_location as _get_dungeon

    prev_dungeon = _get_dungeon(current.name)
    if prev_dungeon:
        _exit_dungeon(game_state)

    game_state.game_data["previous_location"] = current.name
    game_state.current_location = new_location
    game_state.game_data["location"] = new_location.name
    # Reset explore counter for the destination — requirements apply fresh every visit
    game_state.game_data.setdefault("route_progress", {})[new_location.name] = 0

    # Flash wears off when leaving a location
    flash_lit: list = game_state.game_data.get("flash_lit_locations", [])
    if current.name in flash_lit:
        flash_lit.remove(current.name)
        game_state.game_data["flash_lit_locations"] = flash_lit

    # Autosave silently on every location change
    autosave_path = game_state.autosave_on_location_change()

    # Display arrival message
    write_lines_fmt(output, T.TRAVELING_TO, location_name=new_location.name)
    if autosave_path:
        write_lines_fmt(output, T.AUTOSAVED_TO, autosave_name=autosave_path.name)
    write_lines(output, T.TRAVELING_TO_FOOTER)

    # If the new location is a dungeon, enter it automatically
    new_dungeon = _get_dungeon(new_location.name)
    if new_dungeon:
        from .dungeon import enter_dungeon as _enter_dungeon

        _enter_dungeon(game_state, new_dungeon, output)
    else:
        # Show the location details normally
        show_arrival_callback(output)


def prompt_for_location(
    game_state: "GameState", output: RichLog, set_pending_command_callback, show_panel_callback=None
) -> None:
    """Show available locations and wait for user to choose."""
    if not game_state.current_location:
        write_lines(output, T.ERROR_NO_CURRENT_LOCATION)
        return

    current = game_state.current_location
    available_exits = current.get_available_exits()

    if not available_exits:
        write_lines(output, T.NO_AVAILABLE_PATHS)
        return

    write_lines(output, T.SELECT_DESTINATION_HEADER)

    for exit_name in available_exits:
        exit_data = current.exits[exit_name]
        direction = exit_data.get("direction", "")
        dest_location = get_location(exit_name)

        if direction:
            write_lines_fmt(
                output,
                T.SELECT_DESTINATION_ENTRY_WITH_DIRECTION,
                exit_name=exit_name,
                direction=direction,
            )
        else:
            write_lines_fmt(output, T.SELECT_DESTINATION_ENTRY, exit_name=exit_name)

        if dest_location:
            write_lines_fmt(
                output,
                T.SELECT_DESTINATION_DESCRIPTION,
                description=dest_location.description,
            )

    write_lines(output, T.SELECT_DESTINATION_LIST_FOOTER)

    # Use panel callback if provided, otherwise show text-based prompt
    if show_panel_callback:
        write_lines(output, T.SELECT_DESTINATION_PANEL_PROMPT)
        show_panel_callback(available_exits)
    else:
        write_lines(output, T.SELECT_DESTINATION_TEXT_PROMPT)

    set_pending_command_callback("move_to")


def prompt_for_building(
    game_state: "GameState", output: RichLog, set_pending_command_callback, show_panel_callback=None
) -> None:
    """Show available buildings and wait for user to choose."""
    if not game_state.current_location:
        write_lines(output, T.ERROR_NO_CURRENT_LOCATION)
        return

    current = game_state.current_location

    if not current.buildings:
        write_lines(output, T.NO_BUILDINGS_HERE)
        return

    write_lines(output, T.SELECT_BUILDING_HEADER)

    for building in current.buildings:
        write_lines_fmt(output, T.SELECT_BUILDING_ENTRY, building=building)

    dynamic_blocked = _resolve_blocked_buildings(game_state, current)
    if dynamic_blocked:
        write_lines(output, T.BLOCKED_BUILDINGS_HEADER)
        for building, reason in dynamic_blocked.items():
            write_lines_fmt(output, T.BLOCKED_BUILDING_ENTRY, building=building, reason=reason)
        write_lines(output, T.BLOCKED_BUILDINGS_FOOTER)
    else:
        write_lines(output, T.SELECT_BUILDING_LIST_FOOTER)

    # Use panel callback if provided, otherwise show text-based prompt
    if show_panel_callback:
        write_lines(output, T.SELECT_BUILDING_PANEL_PROMPT)
        show_panel_callback(current.buildings)
    else:
        write_lines(output, T.SELECT_BUILDING_TEXT_PROMPT)

    set_pending_command_callback("enter_building")


def show_location_arrival(game_state: "GameState", output: RichLog, is_load: bool = False) -> None:
    """Display location arrival information with available actions."""
    if not game_state.current_location:
        write_lines(output, T.ERROR_NO_CURRENT_LOCATION)
        return

    location = game_state.current_location

    # Header
    write_lines_fmt(output, T.ARRIVAL_HEADER, location_name_upper=location.name.upper())

    # Arrival text
    if is_load:
        write_lines_fmt(output, T.ARRIVAL_LOAD_TEXT, location_name=location.name)
    else:
        write_lines_fmt(output, T.ARRIVAL_TEXT, location_name=location.name)

    write_lines_fmt(output, T.ARRIVAL_DESCRIPTION, description=location.description)

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
            write_lines_fmt(output, T.ARRIVAL_ACTIVITIES_ONE, activity1=activities[0])
        elif len(activities) == 2:
            write_lines_fmt(
                output,
                T.ARRIVAL_ACTIVITIES_TWO,
                activity1=activities[0],
                activity2=activities[1],
            )
        else:
            activity_text = ", ".join(activities[:-1]) + f", or {activities[-1]}"
            write_lines_fmt(output, T.ARRIVAL_ACTIVITIES_MANY, activity_text=activity_text)

    # Show available paths
    available_exits = location.get_available_exits()
    if available_exits:
        previous_location = game_state.game_data.get("previous_location")
        write_lines_fmt(output, T.ARRIVAL_PATHS_HEADER, location_name=location.name)
        for exit_name in available_exits:
            exit_data = location.exits[exit_name]
            direction = exit_data.get("direction", "")
            back_tag = " [cyan]↩ back[/cyan]" if exit_name == previous_location else ""

            # Get destination description
            dest_location = get_location(exit_name)
            if dest_location:
                description = get_travel_description(exit_name, dest_location)
                if direction:
                    write_lines_fmt(
                        output,
                        T.ARRIVAL_PATH_WITH_DIRECTION,
                        exit_name=exit_name,
                        direction=direction,
                        description=description,
                        back_tag=back_tag,
                    )
                else:
                    write_lines_fmt(
                        output,
                        T.ARRIVAL_PATH_WITH_DESCRIPTION,
                        exit_name=exit_name,
                        description=description,
                        back_tag=back_tag,
                    )
            else:
                write_lines_fmt(
                    output,
                    T.ARRIVAL_PATH_BASIC,
                    exit_name=exit_name,
                    back_tag=back_tag,
                )
        write_lines(output, T.ARRIVAL_PATHS_FOOTER)

    # Show blocked buildings if any (resolved dynamically against runtime flags)
    dynamic_blocked = _resolve_blocked_buildings(game_state, location)
    if dynamic_blocked:
        write_lines(output, T.ARRIVAL_BLOCKED_BUILDINGS_HEADER)
        for building, reason in dynamic_blocked.items():
            write_lines_fmt(output, T.BLOCKED_BUILDING_ENTRY, building=building, reason=reason)
        write_lines(output, T.ARRIVAL_BLOCKED_BUILDINGS_FOOTER)

    # Show exploration hint
    if location.can_explore():
        write_lines(output, T.ARRIVAL_EXPLORE_TIP)
        if location.wild_pokemon:
            write_lines(output, T.ARRIVAL_EXPLORE_WILD)
        forward_exits = [
            (n, d["min_explores"])
            for n, d in location.exits.items()
            if d.get("min_explores", 0) > 0
        ]
        if forward_exits and any(
            game_state.get_route_progress(location.name) < req for _, req in forward_exits
        ):
            write_lines(output, T.ARRIVAL_EXPLORE_UNLOCK)
        write_lines(output, T.ARRIVAL_EXPLORE_FOOTER)

    write_lines(output, T.ARRIVAL_FOOTER)


def _resolve_exit_data(
    game_state: "GameState", current_name: str, exit_name: str, exit_data: dict
) -> dict:
    """Apply all runtime gate overrides to a static exit_data entry.

    Mirrors the gate checks in ``move_to_location`` so that ``look_around``
    reflects the same dynamic availability as actual movement.
    """
    badges = game_state.game_data.get("badges", [])
    story_flags = game_state.game_data.get("story_flags", {})
    surf_unlocked = game_state.game_data.get("surf_unlocked", [])

    if exit_name == "Route 24" and current_name == "Cerulean City":
        if "cascade_badge" in badges:
            exit_data = {**exit_data, "blocked": False}

    if exit_name == "Route 21" and current_name == "Pallet Town":
        if "Route 21" in surf_unlocked or game_state.cheat_mode:
            exit_data = {**exit_data, "blocked": False}

    if exit_name == "Route 19" and current_name == "Fuchsia City":
        if "Route 19" in surf_unlocked or game_state.cheat_mode:
            exit_data = {**exit_data, "blocked": False}

    if exit_name == "Route 20" and current_name == "Route 19":
        if "Route 20" in surf_unlocked or game_state.cheat_mode:
            exit_data = {**exit_data, "blocked": False}

    if exit_name == "Route 21" and current_name == "Cinnabar Island":
        if "Route 21" in surf_unlocked or game_state.cheat_mode:
            exit_data = {**exit_data, "blocked": False}
        else:
            exit_data = {
                **exit_data,
                "blocked": True,
                "reason": "Route 21 is open water. You need a Pokemon that knows Surf.",
            }

    if exit_name == "Saffron City":
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

    if exit_name == "Victory Road":
        if "earth_badge" not in badges:
            exit_data = {
                **exit_data,
                "blocked": True,
                "reason": "The gate to Victory Road is locked. You need all 8 Badges to pass.",
            }

    if exit_name == "Cerulean Cave":
        if story_flags.get("is_champion"):
            exit_data = {**exit_data, "blocked": False}
        else:
            exit_data = {
                **exit_data,
                "blocked": True,
                "reason": (
                    "The cave is sealed with heavy barriers. "
                    'A guard says: "Only the Pokemon Champion may enter."'
                ),
            }

    if exit_name == "Champion's Garden":
        if story_flags.get("is_champion"):
            exit_data = {**exit_data, "blocked": False}
        else:
            exit_data = {
                **exit_data,
                "blocked": True,
                "reason": exit_data.get("reason", "This hidden path is only visible to Champions."),
            }

    if exit_name in ("Seafoam Islands", "Power Plant"):
        if exit_name not in surf_unlocked and not game_state.cheat_mode:
            exit_data = {
                **exit_data,
                "blocked": True,
                "reason": f"You need HM Surf to reach {exit_name}.",
            }

    return exit_data


def _resolve_blocked_buildings(game_state: "GameState", location: "Location") -> dict:
    """Return only the buildings that are still blocked at runtime.

    Filters the static ``location.blocked_buildings`` dict against current
    story flags so that buildings unlocked by in-game progress no longer
    appear as blocked in ``look_around``.
    """
    if not location.blocked_buildings:
        return {}
    story_flags = game_state.game_data.get("story_flags", {})
    result: dict = {}
    for building, reason in location.blocked_buildings.items():
        if building == "Hall of Fame" and story_flags.get("defeated_champion"):
            continue
        result[building] = reason
    return result


def look_around(game_state: "GameState", output: RichLog, auto: bool = False) -> None:
    """Look around the current location."""
    if not game_state.current_location:
        write_lines(output, T.ERROR_NO_CURRENT_LOCATION)
        return

    location = game_state.current_location

    if not auto:
        write_lines_fmt(output, T.LOOK_AROUND_HEADER, location_name=location.name)

    # Show buildings if it's a town
    if location.type == "town":
        if location.buildings:
            write_lines(output, T.LOOK_AROUND_BUILDINGS_HEADER)
            for building in location.buildings:
                write_lines_fmt(output, T.LOOK_AROUND_BUILDING_ENTRY, building=building)
            write_lines(output, T.LOOK_AROUND_BUILDINGS_FOOTER)

        dynamic_blocked_buildings = _resolve_blocked_buildings(game_state, location)
        if dynamic_blocked_buildings:
            write_lines(output, T.LOOK_AROUND_BLOCKED_BUILDINGS_HEADER)
            for building, reason in dynamic_blocked_buildings.items():
                write_lines_fmt(output, T.BLOCKED_BUILDING_ENTRY, building=building, reason=reason)
            write_lines(output, T.LOOK_AROUND_BLOCKED_BUILDINGS_FOOTER)

    # Show exploration hint for routes/forests
    if location.can_explore():
        write_lines(output, T.LOOK_AROUND_EXPLORE_HINT)
        if location.wild_pokemon:
            write_lines(output, T.LOOK_AROUND_WILD_HINT)
        if location.trainers > 0:
            write_lines_fmt(output, T.LOOK_AROUND_TRAINERS_HINT, trainer_count=location.trainers)
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
                    write_lines_fmt(
                        output,
                        T.LOOK_AROUND_FORWARD_BACKTRACK,
                        exit_name=exit_name,
                    )
                elif progress >= req:
                    bar = "█" * req
                    write_lines_fmt(
                        output,
                        T.LOOK_AROUND_FORWARD_UNLOCKED,
                        exit_name=exit_name,
                        bar=bar,
                    )
                else:
                    bar = "█" * progress + "░" * (req - progress)
                    write_lines_fmt(
                        output,
                        T.LOOK_AROUND_FORWARD_PROGRESS,
                        exit_name=exit_name,
                        bar=bar,
                        progress=progress,
                        required=req,
                    )
        hint = get_explore_hint(game_state)
        if hint:
            write_lines_fmt(output, T.LOOK_AROUND_HINT_LINE, hint=hint)
        write_lines(output, T.LOOK_AROUND_EXPLORE_FOOTER)

    # Show available exits — resolved dynamically to reflect runtime gates
    resolved_exits = {
        exit_name: _resolve_exit_data(game_state, location.name, exit_name, dict(data))
        for exit_name, data in location.exits.items()
    }
    available_exits = [
        k for k, v in resolved_exits.items() if not v.get("blocked", False)
    ]
    if available_exits:
        previous_location = game_state.game_data.get("previous_location")
        write_lines(output, T.LOOK_AROUND_AVAILABLE_PATHS_HEADER)
        for exit_name in available_exits:
            direction = location.exits[exit_name].get("direction", "")
            direction_str = f" ({direction})" if direction else ""
            if exit_name == previous_location:
                write_lines_fmt(
                    output,
                    T.LOOK_AROUND_PATH_BACK,
                    exit_name=exit_name,
                    direction_str=direction_str,
                )
            else:
                write_lines_fmt(
                    output,
                    T.LOOK_AROUND_PATH,
                    exit_name=exit_name,
                    direction_str=direction_str,
                )
        write_lines(output, T.LOOK_AROUND_AVAILABLE_PATHS_FOOTER)

    # Show blocked exits — resolved dynamically
    blocked_exits = {
        k: v.get("reason", "Blocked")
        for k, v in resolved_exits.items()
        if v.get("blocked", False)
    }
    if blocked_exits:
        write_lines(output, T.LOOK_AROUND_BLOCKED_PATHS_HEADER)
        for exit_name, reason in blocked_exits.items():
            write_lines_fmt(
                output,
                T.LOOK_AROUND_BLOCKED_PATH_ENTRY,
                exit_name=exit_name,
                reason=reason,
            )
        write_lines(output, T.LOOK_AROUND_BLOCKED_PATHS_FOOTER)


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
    write_lines_fmt(output, T.ITEM_FOUND_HEADER, emoji=emoji, item_name=item_name)
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
    write_lines_fmt(output, T.ITEM_FOUND_FLAVOUR, flavour=flavour)
    remaining = len(pool) - (already + 1)
    if remaining > 0:
        write_lines_fmt(
            output,
            T.ITEM_FOUND_MORE_NEARBY,
            remaining=remaining,
            s_suffix="s" if remaining > 1 else "",
        )
    write_lines(output, T.ITEM_FOUND_FOOTER)
    return True


def explore_area(
    game_state: "GameState", output: RichLog, trigger_wild_callback, trigger_trainer_callback
) -> None:
    """Explore the current area for wild Pokemon encounters and trainers."""
    if not game_state.current_location:
        write_lines(output, T.ERROR_NO_CURRENT_LOCATION)
        return

    location = game_state.current_location

    if not location.can_explore():
        write_lines_fmt(output, T.EXPLORE_NOTHING_HERE, location_name=location.name)
        return

    write_lines_fmt(output, T.EXPLORE_START, location_name=location.name)

    # ── Rock Tunnel darkness check ────────────────────────────────────────────
    flash_lit: list = game_state.game_data.get("flash_lit_locations", [])
    _is_dark_tunnel = location.name == "Rock Tunnel" and location.name not in flash_lit
    if _is_dark_tunnel:
        write_lines(output, T.DARK_TUNNEL_WARNING)

    # ── Dungeon floor override ────────────────────────────────────────────────
    # When inside a multi-floor dungeon, use the active floor's encounter tables
    # and trainer roster instead of the flat location-level data.
    from .dungeon import (
        get_current_floor as _get_current_floor,
        pick_floor_level,
        pick_floor_species,
    )

    _active_floor = _get_current_floor(game_state)

    # Effective wild Pokemon list (floor override or location default)
    _effective_wild_pokemon = _active_floor.wild_pokemon if _active_floor else location.wild_pokemon

    # Effective wild encounter rate (floor override or location default)
    _effective_wild_rate = (
        _active_floor.encounter_rate if _active_floor else location.wild_encounter_rate
    )

    # Effective trainer list (floor trainer IDs if in a dungeon floor, else location trainers)
    if _active_floor and _active_floor.trainer_ids:
        from .data import TRAINERS as _TRAINERS

        all_floor_trainers = [
            _TRAINERS[tid] for tid in _active_floor.trainer_ids if tid in _TRAINERS
        ]
    else:
        all_floor_trainers = None  # fall back to location-based lookup below

    # Check for undefeated trainers first (60% chance to encounter if available)
    if all_floor_trainers is not None:
        trainers_pool = all_floor_trainers
    else:
        trainers_pool = get_trainers_by_location(location.name)
    defeated_ids = game_state.game_data.get("defeated_trainers", [])
    available_trainers = [t for t in trainers_pool if t["id"] not in defeated_ids]

    pokemon_list = game_state.game_data.get("pokemon", [])
    if not pokemon_list:
        write_lines(output, T.EXPLORE_NO_POKEMON)
        return

    # Legendary encounter — takes priority over random encounters (one per area)
    from . import buildings as _bld

    if _bld.check_legendary_encounter(
        game_state, location.name, output, lambda: trigger_wild_callback(output)
    ):
        game_state.increment_route_progress(location.name)
        return

    # Prioritize trainer encounters
    _trainer_encounter_rate = (
        location.trainer_encounter_rate if not _active_floor else location.trainer_encounter_rate
    )
    if available_trainers and random.random() < _trainer_encounter_rate:
        # Encounter a random undefeated trainer
        trainer = random.choice(available_trainers)
        # In dark Rock Tunnel without Flash, trainer names/details are hidden
        if _is_dark_tunnel:
            trainer = _dataclass_replace(
                trainer,
                name="???",
                trainer_class="Trainer",
                intro_text=["[dim]Someone jumps at you from the darkness...[/dim]"],
            )
        game_state.increment_route_progress(location.name)
        _stats.record_explore(game_state, location.name)
        trigger_trainer_callback(output, trainer)
        return

    # Otherwise check for wild Pokemon
    if not _effective_wild_pokemon:
        write_lines(output, T.EXPLORE_NOTHING_FOUND)
        return

    # Small chance to find a ground item before any encounter roll
    if _try_find_item(game_state, location.name, output):
        game_state.increment_route_progress(location.name)
        _stats.record_explore(game_state, location.name)
        return

    # Bicycle halves wild encounter rate and counts as 2 explores per trip
    cycling = game_state.game_data.get("cycling", False)
    explore_step = 2 if cycling else 1
    wild_encounter_rate = _effective_wild_rate
    if _is_dark_tunnel:
        # Darkness triples the encounter rate (capped at 100%)
        wild_encounter_rate = min(1.0, wild_encounter_rate * 3.0)
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
                write_lines(output, T.REPEL_SUPPRESSED_ENCOUNTER)
                if remaining > 0:
                    write_lines_fmt(output, T.REPEL_REMAINING, remaining=remaining)
                else:
                    write_lines(output, T.REPEL_WORE_OFF)
                write_lines(output, T.REPEL_FOOTER)
                return
        # ── Silph Scope gating for Pokemon Tower ──────────────────────────────
        if location.name == "Pokemon Tower":
            _bag = game_state.game_data.get("items", {})
            has_silph_scope = bool(_bag.get("Silph Scope", 0))
            if not has_silph_scope:
                ghost_species = {"GASTLY", "HAUNTER"}
                ghost_pool = [p for p in _effective_wild_pokemon if p in ghost_species]
                if ghost_pool and random.random() < 0.70:
                    game_state.increment_route_progress(location.name, explore_step)
                    _stats.record_explore(game_state, location.name)
                    write_lines(output, T.POKEMON_TOWER_GHOST_BLOCKS)
                    return
        game_state.increment_route_progress(location.name, explore_step)
        _stats.record_explore(game_state, location.name)
        # Inject floor-specific encounter data so trigger_wild_callback uses it
        if _active_floor:
            game_state.game_data["_fishing_encounter"] = {
                "species": pick_floor_species(_active_floor),
                "level": pick_floor_level(_active_floor),
            }
        trigger_wild_callback(output)
    else:
        game_state.increment_route_progress(location.name, explore_step)
        _stats.record_explore(game_state, location.name)
        if cycling:
            write_lines(output, T.EXPLORE_NO_ENCOUNTER_CYCLING)
        else:
            write_lines(output, T.EXPLORE_NO_ENCOUNTER_WALKING)
        hint = get_explore_hint(game_state)
        if hint:
            write_lines_fmt(output, T.LOOK_AROUND_HINT_LINE, hint=hint)
        write_lines(output, T.EXPLORE_NO_ENCOUNTER_FOOTER)
        # Mt. Moon one-time discoveries
        if location.name == "Mt. Moon":
            _story_flags = game_state.game_data.setdefault("story_flags", {})
            if not _story_flags.get("received_moon_stone") and random.random() < 0.40:
                _story_flags["received_moon_stone"] = True
                _items = game_state.game_data.setdefault("items", {})
                _items["Moon Stone"] = _items.get("Moon Stone", 0) + 1
                write_lines(output, T.MT_MOON_FOUND_MOON_STONE)
            if not _story_flags.get("received_mt_moon_fossil") and random.random() < 0.30:
                _story_flags["received_mt_moon_fossil"] = True
                _fossil = random.choice(["Dome Fossil", "Helix Fossil"])
                _items = game_state.game_data.setdefault("items", {})
                _items[_fossil] = _items.get(_fossil, 0) + 1
                write_lines_fmt(output, T.MT_MOON_FOUND_FOSSIL, fossil=_fossil)
        # ── Pokemon Tower: Ghost encounter & Mr. Fuji rescue ──────────────────
        elif location.name == "Pokemon Tower":
            _tower_flags = game_state.game_data.setdefault("story_flags", {})
            _bag = game_state.game_data.setdefault("items", {})
            has_silph_scope = bool(_bag.get("Silph Scope", 0))
            if not _tower_flags.get("ghost_encounter_shown") and random.random() < 0.40:
                _tower_flags["ghost_encounter_shown"] = True
                write_lines(output, T.POKEMON_TOWER_GHOST_EVENT_HEADER)
                if has_silph_scope:
                    write_lines(output, T.POKEMON_TOWER_GHOST_EVENT_WITH_SCOPE)
                else:
                    write_lines(output, T.POKEMON_TOWER_GHOST_EVENT_NO_SCOPE)
                write_lines(output, T.POKEMON_TOWER_GHOST_EVENT_FOOTER)
            if (
                not _tower_flags.get("rescued_mr_fuji")
                and has_silph_scope
                and game_state.get_route_progress(location.name) >= 8
                and random.random() < 0.35
            ):
                _tower_flags["rescued_mr_fuji"] = True
                _bag["Poke Flute"] = _bag.get("Poke Flute", 0) + 1
                write_lines(output, T.POKEMON_TOWER_RESCUE_MR_FUJI)
        # ── Team Rocket's Hideout: Lift Key & Silph Scope from Giovanni ───────
        elif location.name == "Team Rocket's Hideout":
            _rocket_flags = game_state.game_data.setdefault("story_flags", {})
            _bag = game_state.game_data.setdefault("items", {})
            if not _rocket_flags.get("found_lift_key") and random.random() < 0.25:
                _rocket_flags["found_lift_key"] = True
                _bag["Lift Key"] = _bag.get("Lift Key", 0) + 1
                write_lines(output, T.ROCKET_HIDEOUT_FOUND_LIFT_KEY)
            if (
                not _rocket_flags.get("defeated_giovanni_hideout")
                and _rocket_flags.get("found_lift_key")
                and game_state.get_route_progress(location.name) >= 10
                and random.random() < 0.30
            ):
                _rocket_flags["defeated_giovanni_hideout"] = True
                _bag["Silph Scope"] = _bag.get("Silph Scope", 0) + 1
                write_lines(output, T.ROCKET_HIDEOUT_GIOVANNI_REWARD)


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
        if ready:
            return f"[dim][cyan]{dest_name}[/cyan] is within reach! Move ahead or linger a while longer.[/dim]"
        remaining = required - done
        bar_filled = int((done / required) * 8)
        bar = "█" * bar_filled + "░" * (8 - bar_filled)
        if remaining == 1:
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
            return f"[dim]Paths ahead are clear — {dest_list}. Move when ready.[/dim]"
        else:
            return f"[dim]Paths ahead: {dest_list}. Keep exploring to advance.[/dim]"
