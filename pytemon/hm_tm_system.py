"""
HM/TM system for the Pokemon game.

Hidden Machines (HMs) teach moves that are never consumed and can be used
in the field.  Technical Machines (TMs) teach moves and are consumed after
use.  This module handles the teaching logic and the field effects of each
HM (Surf, Fly, Cut, Strength, Flash).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import RichLog

if TYPE_CHECKING:
    from .game_state import GameState
    from .models import PartyPokemon

# ---------------------------------------------------------------------------
# Badge requirements for HM field use
# ---------------------------------------------------------------------------

# Maps HM move name → badge ID required to use it outside battle.
HM_BADGE_REQUIREMENTS: dict[str, str] = {
    "CUT": "boulder_badge",
    "FLY": "thunder_badge",
    "SURF": "cascade_badge",
    "STRENGTH": "soul_badge",
    "FLASH": "boulder_badge",
}

# Human-readable badge names for error messages
_BADGE_DISPLAY: dict[str, str] = {
    "boulder_badge": "Boulder Badge",
    "cascade_badge": "Cascade Badge",
    "thunder_badge": "Thunder Badge",
    "rainbow_badge": "Rainbow Badge",
    "soul_badge": "Soul Badge",
    "marsh_badge": "Marsh Badge",
    "volcano_badge": "Volcano Badge",
    "earth_badge": "Earth Badge",
}

# Maximum moves a Pokemon can know at once
_MAX_MOVES = 4


# ---------------------------------------------------------------------------
# Teaching moves
# ---------------------------------------------------------------------------


def teach_move(
    game_state: GameState,
    move_name: str,
    pokemon: PartyPokemon,
    item_name: str,
    is_hm: bool,
    output: RichLog,
) -> bool:
    """
    Teach *move_name* to *pokemon*.

    If the Pokemon already knows 4 moves the player is informed; no move is
    replaced automatically (a future improvement could add a replacement UI).

    Args:
        game_state: Current game state (used for Pokedex checks etc.).
        move_name:  Upper-case move name (e.g. ``"SURF"``).
        pokemon:    Target PartyPokemon dict.
        item_name:  Display name of the teaching item (e.g. ``"HM03 Surf"``).
        is_hm:      True for HMs (not consumed), False for TMs (consumed).
        output:     RichLog widget.

    Returns:
        True if the move was taught (or already known).
    """
    from .data.move_data import MOVES, MoveSlot

    poke_name = pokemon.get("name", "POKÉMON")
    move_upper = move_name.upper()

    if move_upper not in MOVES:
        output.write("")
        output.write(f"[red]❌ Move '{move_name}' is not in the move database.[/red]")
        output.write("")
        return False

    move_data = MOVES[move_upper]

    raw_moves = pokemon.get("moves", [])

    # Normalise: get move names regardless of whether moves are MoveSlot objects or strings
    def _move_name(m) -> str:
        if hasattr(m, "name"):
            return m.name
        if isinstance(m, dict):
            return m.get("name", "")
        return str(m)

    move_names = [_move_name(m) for m in raw_moves]

    # Already knows the move
    if move_upper in move_names:
        output.write("")
        output.write(f"[yellow]⚠ {poke_name} already knows {move_upper}![/yellow]")
        output.write("")
        return True

    if len(raw_moves) < _MAX_MOVES:
        # Append as a MoveSlot for consistency
        new_slot = MoveSlot(
            name=move_upper,
            pp=move_data.pp if hasattr(move_data, "pp") else move_data.get("pp", 35),
            max_pp=move_data.pp if hasattr(move_data, "pp") else move_data.get("pp", 35),
        )
        raw_moves.append(new_slot)
        pokemon["moves"] = raw_moves
        kind = "HM" if is_hm else "TM"
        output.write("")
        output.write(f"[bold green]✓ {poke_name} learned {move_upper}![/bold green]")
        output.write(
            f"[dim]  {kind}: {move_data.get('type', '').capitalize()} type, "
            f"{move_data.get('power', 0)} power, {move_data.get('pp', 0)} PP[/dim]"
        )
        if is_hm:
            output.write(f"[dim]  ({item_name} is an HM — it was not consumed)[/dim]")
        output.write("")
        return True

    # Movepool is full — inform the player
    output.write("")
    output.write(f"[yellow]⚠ {poke_name} already knows 4 moves![/yellow]")
    output.write("[dim]  A Pokemon can only know 4 moves at a time.[/dim]")
    output.write("[dim]  Future update: move replacement will be added.[/dim]")
    output.write("")
    return False


# ---------------------------------------------------------------------------
# HM field use
# ---------------------------------------------------------------------------


def use_hm_field(
    game_state: GameState,
    move_name: str,
    output: RichLog,
    show_location_callback=None,
) -> bool:
    """
    Use an HM in the field (outside battle).

    Checks badge and party requirements, then applies the move's field effect.

    Args:
        game_state:              Current game state.
        move_name:               Upper-case HM move name (e.g. ``"SURF"``).
        output:                  RichLog widget.
        show_location_callback:  Optional callback to refresh the location display
                                 (used by Surf to show the new route).

    Returns:
        True if the HM was used successfully.
    """
    move_upper = move_name.upper()

    # --- Badge check ---
    required_badge = HM_BADGE_REQUIREMENTS.get(move_upper)
    if required_badge:
        badges = game_state.game_data.get("badges", [])
        if required_badge not in badges and not game_state.cheat_mode:
            badge_display = _BADGE_DISPLAY.get(required_badge, required_badge)
            output.write("")
            output.write(
                f"[yellow]⚠ You need the {badge_display} to use {move_upper} outside battle![/yellow]"
            )
            output.write("")
            return False

    # --- Party move check ---
    party: list = game_state.game_data.get("pokemon", [])
    pokemon_with_move: PartyPokemon | None = None
    for p in party:
        raw_moves = p.get("moves", [])
        # Normalise move names (MoveSlot objects, dicts, or plain strings)
        move_names = []
        for m in raw_moves:
            if hasattr(m, "name"):
                move_names.append(m.name)
            elif isinstance(m, dict):
                move_names.append(m.get("name", ""))
            else:
                move_names.append(str(m))
        if move_upper in move_names and p.get("hp", 0) > 0:
            pokemon_with_move = p
            break

    if not pokemon_with_move and not game_state.cheat_mode:
        output.write("")
        output.write(f"[yellow]⚠ None of your Pokemon know {move_upper}![/yellow]")
        output.write(f"[dim]  Teach {move_upper} to a Pokemon using the matching HM first.[/dim]")
        output.write("")
        return False

    # --- Field effects per move ---
    if move_upper == "SURF":
        return _field_surf(game_state, pokemon_with_move, output, show_location_callback)
    if move_upper == "FLY":
        return _field_fly(game_state, pokemon_with_move, output)
    if move_upper == "CUT":
        return _field_cut(game_state, pokemon_with_move, output)
    if move_upper == "STRENGTH":
        return _field_strength(game_state, pokemon_with_move, output)
    if move_upper == "FLASH":
        return _field_flash(game_state, pokemon_with_move, output)

    output.write("")
    output.write(f"[yellow]⚠ {move_upper} has no field effect.[/yellow]")
    output.write("")
    return False


def _field_surf(
    game_state: GameState,
    pokemon: PartyPokemon | None,
    output: RichLog,
    show_location_callback=None,
) -> bool:
    """Surf — unlock water routes that require HM Surf."""
    from .locations import get_location

    location = game_state.current_location
    if not location:
        output.write("[red]❌ No current location![/red]")
        return False

    poke_name = pokemon["name"] if pokemon else "your Pokemon"

    # Find blocked exits that say they require Surf
    surf_exits: list[str] = []
    for exit_name, exit_data in location.exits.items():
        reason = exit_data.get("reason", "").lower()
        if exit_data.get("blocked") and "surf" in reason:
            surf_exits.append(exit_name)

    if surf_exits:
        output.write("")
        output.write(f"[bold cyan]🌊 {poke_name} used SURF![/bold cyan]")
        for exit_name in surf_exits:
            dest = get_location(exit_name)
            dest_display = exit_name if dest is None else dest.name
            output.write(f"[cyan]   The water path to {dest_display} is now open![/cyan]")
            # Record that Surf has been used to unlock this exit
            game_state.game_data.setdefault("surf_unlocked", [])
            if exit_name not in game_state.game_data["surf_unlocked"]:
                game_state.game_data["surf_unlocked"].append(exit_name)
        output.write("")
        if show_location_callback:
            show_location_callback()
        return True

    # Check if we're already in a surf-accessible area
    surf_unlocked = game_state.game_data.get("surf_unlocked", [])
    if any(loc in location.name for loc in ["Route 21", "Route 19", "Route 20"]):
        output.write("")
        output.write(f"[cyan]🌊 {poke_name} is riding the waves — Surf is active here![/cyan]")
        output.write("")
        return True

    if surf_unlocked or game_state.cheat_mode:
        output.write("")
        output.write(f"[cyan]🌊 {poke_name} used SURF![/cyan]")
        output.write("[dim]  You're surfing on the water.[/dim]")
        output.write("")
        return True

    output.write("")
    output.write("[yellow]⚠ There's no water to surf on here![/yellow]")
    output.write("[dim]  Find a water route to use Surf.[/dim]")
    output.write("")
    return False


def _field_fly(
    game_state: GameState,
    pokemon: PartyPokemon | None,
    output: RichLog,
) -> bool:
    """Fly — fast-travel to any previously visited city/town."""
    poke_name = pokemon["name"] if pokemon else "your Pokemon"
    visited: list[str] = game_state.game_data.get("visited_locations", [])
    current = game_state.current_location

    # Collect fly-able towns (visited towns, excluding current)
    from .locations import LOCATIONS, TYPE_TOWN

    flyable = [
        loc_name
        for loc_name in visited
        if loc_name in LOCATIONS
        and LOCATIONS[loc_name].type == TYPE_TOWN
        and (current is None or loc_name != current.name)
    ]

    if not flyable:
        output.write("")
        output.write(f"[cyan]🦅 {poke_name} used FLY![/cyan]")
        output.write("[yellow]⚠ You haven't visited any other towns yet![/yellow]")
        output.write("[dim]  Explore the world first, then use Fly to return.[/dim]")
        output.write("")
        return False

    output.write("")
    output.write(f"[bold cyan]🦅 {poke_name} used FLY![/bold cyan]")
    output.write("[cyan]   Where would you like to fly to?[/cyan]")
    output.write("")
    for i, town in enumerate(flyable, 1):
        output.write(f"  [green]{i}.[/green] {town}")
    output.write("")
    output.write("[dim]  Type 'fly to <town name>' to travel there.[/dim]")
    output.write("")
    return True


def fly_to_town(
    game_state: GameState,
    destination: str,
    output: RichLog,
) -> bool:
    """
    Teleport to a previously visited town using Fly.

    Args:
        game_state:   Current game state.
        destination:  Name (or partial name) of the destination town.
        output:       RichLog widget.

    Returns:
        True if teleportation was successful.
    """
    from .locations import LOCATIONS, TYPE_TOWN

    visited: list[str] = game_state.game_data.get("visited_locations", [])
    dest_lower = destination.lower()

    match: str | None = None
    for loc_name in visited:
        if loc_name in LOCATIONS and LOCATIONS[loc_name].type == TYPE_TOWN:
            if loc_name.lower() == dest_lower or dest_lower in loc_name.lower():
                match = loc_name
                break

    if not match:
        output.write("")
        output.write(
            f"[red]❌ Can't fly to '{destination}' — either not visited or not a town.[/red]"
        )
        output.write("[dim]  Type 'fly' to see available destinations.[/dim]")
        output.write("")
        return False

    dest_loc = LOCATIONS[match]
    game_state.game_data["previous_location"] = (
        game_state.current_location.name if game_state.current_location else ""
    )
    game_state.current_location = dest_loc
    game_state.game_data["location"] = dest_loc.name
    game_state.autosave_on_location_change()
    output.write("")
    output.write(f"[bold cyan]🦅 You flew to {dest_loc.name}![/bold cyan]")
    output.write("[cyan]   You landed safely at the Pokemon Center.[/cyan]")
    output.write("")
    return True


def _field_cut(
    game_state: GameState,
    pokemon: PartyPokemon | None,
    output: RichLog,
) -> bool:
    """Cut — clears tree obstacles in forests."""
    poke_name = pokemon["name"] if pokemon else "your Pokemon"
    location = game_state.current_location

    if location and location.type in ("forest", "route"):
        output.write("")
        output.write(f"[green]✂️  {poke_name} used CUT![/green]")
        output.write("[green]   The small tree was chopped down![/green]")
        output.write("[dim]  The path is now clear.[/dim]")
        output.write("")
        # Mark cut used at this location
        game_state.game_data.setdefault("cut_used", [])
        if location and location.name not in game_state.game_data["cut_used"]:
            game_state.game_data["cut_used"].append(location.name)
        return True

    output.write("")
    output.write(f"[cyan]✂️  {poke_name} used CUT![/cyan]")
    output.write("[yellow]⚠ There's nothing here to cut.[/yellow]")
    output.write("")
    return False


def _field_strength(
    game_state: GameState,
    pokemon: PartyPokemon | None,
    output: RichLog,
) -> bool:
    """Strength — move heavy boulders."""
    poke_name = pokemon["name"] if pokemon else "your Pokemon"
    output.write("")
    output.write(f"[bold green]💪 {poke_name} used STRENGTH![/bold green]")
    output.write("[green]   The boulder was moved![/green]")
    output.write("")
    return True


def _field_flash(
    game_state: GameState,
    pokemon: PartyPokemon | None,
    output: RichLog,
) -> bool:
    """Flash — illuminate dark areas (e.g. caves)."""
    poke_name = pokemon["name"] if pokemon else "your Pokemon"
    output.write("")
    output.write(f"[bold yellow]💡 {poke_name} used FLASH![/bold yellow]")
    output.write("[yellow]   The area is now lit up![/yellow]")
    output.write("")
    return True
