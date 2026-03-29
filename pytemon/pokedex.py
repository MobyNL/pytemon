"""
Pokedex System for Pokemon Terminal Game.

This module handles tracking Pokemon that have been seen and caught,
displaying Pokedex entries, and calculating completion percentages.
"""

import math
from typing import TYPE_CHECKING, Any, Dict, Optional

from textual.widgets import RichLog

from .texts.en import pokedex as T
from .ui.formatters import write_lines

if TYPE_CHECKING:
    from .game_state import GameState

from .data import POKEMON

# Pagination settings — change this to control how many entries appear per page
POKEMON_PER_PAGE = 10

# Build a reverse lookup from name to number for efficiency
_NAME_TO_NUMBER = {data["name"]: num for num, data in POKEMON.items()}


def initialize_pokedex(game_state: "GameState") -> None:
    """
    Initialize the Pokedex in game state if not already present.

    Args:
        game_state: The game state object
    """
    if "pokedex" not in game_state.game_data:
        game_state.game_data["pokedex"] = {
            "seen": [],  # List of Pokemon species seen
            "caught": [],  # List of Pokemon species caught
        }


def migrate_existing_save(game_state: "GameState") -> int:
    """
    Migrate existing save files to include Pokedex data.
    Automatically registers all Pokemon in the party as caught.

    Args:
        game_state: The game state object

    Returns:
        Number of Pokemon registered during migration
    """
    # Initialize Pokedex if it doesn't exist
    initialize_pokedex(game_state)

    # Get current party
    pokemon_party = game_state.game_data.get("pokemon", [])

    # Track how many were newly registered
    registered_count = 0

    # Register all party Pokemon as caught
    for pokemon in pokemon_party:
        if isinstance(pokemon, dict):
            # Get species name
            name = pokemon.get("name", "")
            if not name:
                continue

            # Convert name to uppercase (POKEMON data uses uppercase names)
            species_name = name.upper()

            # Verify the species exists in our POKEMON data
            if species_name in _NAME_TO_NUMBER:
                # Mark as caught (which also marks as seen)
                if mark_as_caught(game_state, species_name):
                    registered_count += 1

    return registered_count


def mark_as_seen(game_state: "GameState", species: str) -> bool:
    """
    Mark a Pokemon species as seen in the Pokedex.

    Args:
        game_state: The game state object
        species: Pokemon species name (e.g., "PIKACHU")

    Returns:
        True if this is the first time seeing this Pokemon, False otherwise
    """
    initialize_pokedex(game_state)

    pokedex = game_state.game_data["pokedex"]
    seen = pokedex.get("seen", [])

    if species not in seen:
        seen.append(species)
        pokedex["seen"] = seen
        return True

    return False


def mark_as_caught(game_state: "GameState", species: str) -> bool:
    """
    Mark a Pokemon species as caught in the Pokedex.
    Also marks it as seen if not already.

    Args:
        game_state: The game state object
        species: Pokemon species name (e.g., "PIKACHU")

    Returns:
        True if this is the first time catching this Pokemon, False otherwise
    """
    initialize_pokedex(game_state)

    # Mark as seen first
    mark_as_seen(game_state, species)

    pokedex = game_state.game_data["pokedex"]
    caught = pokedex.get("caught", [])

    if species not in caught:
        caught.append(species)
        pokedex["caught"] = caught
        return True

    return False


def get_caught_milestone_message(caught_count: int) -> Optional[str]:
    """
    Return a milestone celebration message for round-number catches, or None.

    Milestones: 1 (first catch!), 10, 25, 50, 75, 100, 150 (complete!)

    Args:
        caught_count: Current total number of species caught

    Returns:
        Celebration message string, or None if not a milestone
    """
    milestones = {
        1: "📖 First Pokemon registered! Your Pokedex adventure begins!",
        10: "📖 Milestone! 10 Pokemon caught! You're becoming a real trainer!",
        25: "📖 Milestone! 25 Pokemon caught! A quarter of the way there!",
        50: "📖 Milestone! 50 Pokemon caught! Halfway through the Kanto Pokedex!",
        75: "📖 Milestone! 75 Pokemon caught! You're in the home stretch!",
        100: "📖 Milestone! 100 Pokemon caught! Phenomenal dedication!",
        150: "📖 POKEDEX COMPLETE! 150/150 — You've caught them all! 🏆",
    }
    return milestones.get(caught_count)


def get_first_type_message(game_state: "GameState", species: str) -> Optional[str]:
    """
    Return a message if this is the first Pokemon of its type the player has caught.

    Args:
        game_state: The game state object
        species: Pokemon species name (e.g., "PIKACHU")

    Returns:
        Message string if first of type, None otherwise
    """
    story_flags = game_state.game_data.setdefault("story_flags", {})

    # Look up species types from POKEMON data
    pokemon_data = POKEMON.get(_NAME_TO_NUMBER.get(species, -1))
    if not pokemon_data:
        return None

    types = pokemon_data.get("types", [])
    for type_name in types:
        flag_key = f"first_caught_type_{type_name.lower()}"
        if not story_flags.get(flag_key):
            story_flags[flag_key] = True
            return f"📖 First {type_name}-type Pokemon caught!"

    return None


def is_seen(game_state: "GameState", species: str) -> bool:
    """
    Check if a Pokemon species has been seen.

    Args:
        game_state: The game state object
        species: Pokemon species name

    Returns:
        True if seen, False otherwise
    """
    pokedex = game_state.game_data.get("pokedex", {})
    seen = pokedex.get("seen", [])
    return species in seen


def is_caught(game_state: "GameState", species: str) -> bool:
    """
    Check if a Pokemon species has been caught.

    Args:
        game_state: The game state object
        species: Pokemon species name

    Returns:
        True if caught, False otherwise
    """
    pokedex = game_state.game_data.get("pokedex", {})
    caught = pokedex.get("caught", [])
    return species in caught


def get_pokedex_stats(game_state: "GameState") -> Dict[str, int]:
    """
    Get Pokedex statistics.

    Args:
        game_state: The game state object

    Returns:
        Dictionary with 'seen', 'caught', 'total', 'seen_percent', 'caught_percent'
    """
    pokedex = game_state.game_data.get("pokedex", {})
    seen = pokedex.get("seen", [])
    caught = pokedex.get("caught", [])
    total = len(POKEMON)

    return {
        "seen": len(seen),
        "caught": len(caught),
        "total": total,
        "seen_percent": int(len(seen) / total * 100) if total > 0 else 0,
        "caught_percent": int(len(caught) / total * 100) if total > 0 else 0,
    }


def get_pokedex_state(game_state: "GameState") -> Dict[str, Any]:
    """
    Get or initialize Pokedex viewing state (for pagination).

    Args:
        game_state: The game state object

    Returns:
        Dictionary with pagination state
    """
    if "pokedex_view" not in game_state.game_data:
        game_state.game_data["pokedex_view"] = {"current_page": 1, "filter_mode": "all"}
    return game_state.game_data["pokedex_view"]


def show_pokedex(
    game_state: "GameState", output: RichLog, filter_mode: str = "all", page: Optional[int] = None
) -> None:
    """
    Display the Pokedex with pagination.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
        filter_mode: Display mode - 'all', 'seen', 'caught', or 'missing'
        page: Optional page number (if None, uses current page from state)
    """
    initialize_pokedex(game_state)

    # Get pagination state
    view_state = get_pokedex_state(game_state)

    # Update filter mode if changed
    if filter_mode != view_state["filter_mode"]:
        view_state["filter_mode"] = filter_mode
        view_state["current_page"] = 1  # Reset to page 1 when filter changes

    # Use provided page or current page
    current_page = page if page is not None else view_state["current_page"]

    pokedex = game_state.game_data["pokedex"]
    seen = set(pokedex.get("seen", []))
    caught = set(pokedex.get("caught", []))

    stats = get_pokedex_stats(game_state)

    # Prepare sorted list of Pokemon by number
    pokemon_list = []
    for _, data in POKEMON.items():
        number = data.number
        species_name = data.name  # use the name string, not the int key
        pokemon_list.append((number, species_name, data))

    pokemon_list.sort(key=lambda x: x[0])

    # Filter Pokemon based on mode
    filtered_list = []
    for number, species_name, data in pokemon_list:
        is_seen_flag = species_name in seen
        is_caught_flag = species_name in caught

        # Apply filter
        if filter_mode == "seen" and not is_seen_flag:
            continue
        elif filter_mode == "caught" and not is_caught_flag:
            continue
        elif filter_mode == "missing" and is_seen_flag:
            continue

        filtered_list.append((number, species_name, data, is_seen_flag, is_caught_flag))

    # Calculate pagination
    total_entries = len(filtered_list)
    total_pages = math.ceil(total_entries / POKEMON_PER_PAGE) if total_entries > 0 else 1

    # Clamp current page to valid range
    current_page = max(1, min(current_page, total_pages))
    view_state["current_page"] = current_page

    # Get entries for current page
    start_idx = (current_page - 1) * POKEMON_PER_PAGE
    end_idx = start_idx + POKEMON_PER_PAGE
    page_entries = filtered_list[start_idx:end_idx]

    # Display header
    write_lines(output, T.POKEDEX_HEADER)

    # Show statistics
    output.write(
        f"[bold]Seen:[/bold]   [yellow]{stats['seen']}/{stats['total']}[/yellow] ({stats['seen_percent']}%)"
    )
    output.write(
        f"[bold]Caught:[/bold] [green]{stats['caught']}/{stats['total']}[/green] ({stats['caught_percent']}%)"
    )

    # Show next milestone progress
    next_milestone = None
    for m in [1, 10, 25, 50, 75, 100, 150]:
        if stats["caught"] < m:
            next_milestone = m
            break
    if next_milestone:
        output.write(
            f"[dim]Next milestone: {next_milestone} caught "
            f"({next_milestone - stats['caught']} to go)[/dim]"
        )
    output.write("")

    # Filter info and pagination
    filter_display = {
        "all": "All Pokemon",
        "seen": "Seen Pokemon",
        "caught": "Caught Pokemon",
        "missing": "Unseen Pokemon",
    }
    output.write(
        f"[bold]Filter:[/bold] {filter_display.get(filter_mode, 'All Pokemon')} ({total_entries} entries)"
    )
    output.write(f"[bold]Page:[/bold] {current_page} of {total_pages}")
    output.write("")

    # Display Pokemon entries for current page
    if not page_entries:
        write_lines(output, T.POKEDEX_NO_MATCH)
    else:
        for number, species_name, data, is_seen_flag, is_caught_flag in page_entries:
            # Format entry
            # Ensure species_name is a string for the fallback
            species_display = (
                str(species_name).replace("_", " ").title()
                if isinstance(species_name, str)
                else f"Pokemon #{number}"
            )

            if is_caught_flag:
                status = "[green]●[/green]"  # Caught
                name = data.get("name", species_display)
                types = "/".join(data.get("types", []))
                output.write(
                    f"{status} [bold green]#{number:03d} {name}[/bold green]  [dim]{types}[/dim]"
                )
            elif is_seen_flag:
                status = "[yellow]○[/yellow]"  # Seen but not caught
                name = data.get("name", species_display)
                types = "/".join(data.get("types", []))
                output.write(
                    f"{status} [bold yellow]#{number:03d} {name}[/bold yellow]  [dim]{types}[/dim]"
                )
            else:
                status = "[dim]●[/dim]"  # Not seen
                output.write(f"{status} [dim]#{number:03d} ???[/dim]")

    write_lines(output, T.POKEDEX_DIVIDER)

    # Navigation help
    if total_pages > 1:
        output.write(f"[dim]Page {current_page} of {total_pages}[/dim]")
        output.write("")


def show_pokedex_entry(game_state: "GameState", output: RichLog, species: str) -> None:
    """
    Display detailed Pokedex entry for a specific Pokemon.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
        species: Pokemon species name or number
    """
    initialize_pokedex(game_state)

    # Try to find Pokemon by name or number
    pokemon_data = None
    found_species = None
    search_species = species.upper().replace(" ", "_")

    # First try direct name match using the name-to-number lookup
    if search_species in _NAME_TO_NUMBER:
        dex_num = _NAME_TO_NUMBER[search_species]
        pokemon_data = POKEMON.get(dex_num)
        found_species = search_species
    else:
        # Try by number
        try:
            search_number = int(species)
            data = POKEMON.get(search_number)
            if data:
                pokemon_data = data
                found_species = data.name
        except ValueError:
            # Try partial name match against the species name stored in each entry
            for data in POKEMON.values():
                sp_name = data.name  # always a string
                if search_species in sp_name or sp_name in search_species:
                    pokemon_data = data
                    found_species = sp_name
                    break

    if not pokemon_data:
        output.write("")
        output.write(f"[red]❌ Pokemon '{species}' not found in Pokedex data[/red]")
        output.write("")
        return

    pokedex = game_state.game_data["pokedex"]
    seen = set(pokedex.get("seen", []))
    caught = set(pokedex.get("caught", []))

    is_seen_flag = found_species in seen
    is_caught_flag = found_species in caught

    write_lines(output, T.POKEDEX_ENTRY_HEADER)

    if not is_seen_flag:
        write_lines(output, T.POKEDEX_ENTRY_NOT_SEEN)
        return

    # Display entry
    number = pokemon_data.get("number", "???")
    name = pokemon_data.get("name", "???")
    types = "/".join(pokemon_data.get("types", ["???"]))

    status = "Caught" if is_caught_flag else "Seen"
    status_color = "green" if is_caught_flag else "yellow"

    output.write(f"  [bold]No.:[/bold] #{number:03d}")
    output.write(f"  [bold]Name:[/bold] {name}")
    output.write(f"  [bold]Type:[/bold] {types}")
    output.write(f"  [bold]Status:[/bold] [{status_color}]{status}[/{status_color}]")
    output.write("")

    # Show base stats if caught
    if is_caught_flag:
        base_stats = pokemon_data.get("base_stats", {})
        if base_stats:
            output.write("  [bold]Base Stats:[/bold]")
            output.write(f"    HP:      {base_stats.get('hp', '?')}")
            output.write(f"    Attack:  {base_stats.get('attack', '?')}")
            output.write(f"    Defense: {base_stats.get('defense', '?')}")
            output.write(f"    Special: {base_stats.get('special', '?')}")
            output.write(f"    Speed:   {base_stats.get('speed', '?')}")
            output.write("")

    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("")
