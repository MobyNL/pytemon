"""
Fishing mechanic for the Pokemon game.

Players can fish for water Pokemon using Old Rod, Good Rod, or Super Rod
at locations that have water access.  Each rod type yields different
Pokemon species and level ranges.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from textual.widgets import RichLog

if TYPE_CHECKING:
    from .game_state import GameState

from .texts.en import fishing as T
from .ui.formatters import write_lines, write_lines_fmt

# ---------------------------------------------------------------------------
# Fishing data — rod → (species, weight) tables and level ranges
# ---------------------------------------------------------------------------

# Each entry: (pokemon_name, relative_weight)
# Higher weight = more common catch.
_ROD_TABLES: dict[str, list[tuple[str, int]]] = {
    "Old Rod": [
        ("MAGIKARP", 90),
        ("GOLDEEN", 10),
    ],
    "Good Rod": [
        ("MAGIKARP", 60),
        ("GOLDEEN", 30),
        ("TENTACOOL", 10),
    ],
    "Super Rod": [
        ("MAGIKARP", 40),
        ("GOLDEEN", 35),
        ("TENTACOOL", 20),
        ("GYARADOS", 5),
    ],
}

_ROD_LEVEL_RANGES: dict[str, tuple[int, int]] = {
    "Old Rod": (5, 15),
    "Good Rod": (10, 30),
    "Super Rod": (15, 40),
}

# Locations that have water access and support fishing.
# Any town/route near a body of water is fishable.
_FISHING_LOCATIONS: set[str] = {
    "Pallet Town",
    "Viridian City",
    "Cerulean City",
    "Route 4",
    "Route 6",
    "Route 10",
    "Route 12",
    "Route 13",
    "Route 17",
    "Route 19",
    "Route 20",
    "Route 21",
    "Route 24",
    "Vermillion City",
    "Celadon City",
    "Fuchsia City",
    "Cinnabar Island",
    "Route 25",
}

# Base nibble probability per rod (probability that a Pokemon bites)
_NIBBLE_CHANCE: dict[str, float] = {
    "Old Rod": 0.70,
    "Good Rod": 0.80,
    "Super Rod": 0.90,
}


def get_best_rod(game_state: GameState) -> str | None:
    """
    Return the best fishing rod in the player's bag, or None if they have none.

    Args:
        game_state: Current game state.

    Returns:
        Canonical name of the best rod available, or None.
    """
    items = game_state.game_data.get("items", {})
    for rod in ("Super Rod", "Good Rod", "Old Rod"):
        if items.get(rod, 0) > 0:
            return rod
    return None


def get_rod_for_name(game_state: GameState, rod_hint: str) -> str | None:
    """
    Return the canonical rod name matching *rod_hint* if the player owns it.

    Args:
        game_state: Current game state.
        rod_hint:   Partial or full rod name supplied by the player.

    Returns:
        Canonical rod name, or None if not found / not owned.
    """
    items = game_state.game_data.get("items", {})
    hint_lower = rod_hint.lower()
    for rod in ("Super Rod", "Good Rod", "Old Rod"):
        if rod.lower() == hint_lower or hint_lower in rod.lower():
            if items.get(rod, 0) > 0:
                return rod
    return None


def start_fishing(
    game_state: GameState,
    output: RichLog,
    trigger_wild_callback,
    rod_name: str | None = None,
) -> None:
    """
    Begin a fishing attempt at the current location.

    Selects the appropriate rod, checks that the location supports fishing,
    rolls for a nibble, then triggers a wild Pokemon encounter with a water-
    type Pokemon if successful.

    Args:
        game_state:            Current game state.
        output:                RichLog widget.
        trigger_wild_callback: Callback(output, forced_pokemon) to start a battle
                               with a pre-selected wild Pokemon.  Signature matches
                               the ``trigger_wild_encounter`` method on the terminal.
        rod_name:              Optional rod name specified by the player.  When None,
                               the best available rod is used.
    """
    location = game_state.current_location
    if not location:
        output.write("[red]❌ No current location![/red]")
        return

    # --- Party check ---
    party = game_state.game_data.get("pokemon", [])
    if not party:
        write_lines(output, T.FISHING_NO_POKEMON)
        return

    # --- Location check ---
    if location.name not in _FISHING_LOCATIONS:
        write_lines(output, T.FISHING_WRONG_LOCATION)
        return

    # --- Rod selection ---
    if rod_name:
        chosen_rod = get_rod_for_name(game_state, rod_name)
        if not chosen_rod:
            write_lines_fmt(output, T.FISHING_WRONG_ROD, rod_name=rod_name)
            return
    else:
        chosen_rod = get_best_rod(game_state)
        if not chosen_rod:
            write_lines(output, T.FISHING_NO_ROD)
            return

    # --- Casting ---
    write_lines_fmt(output, T.FISHING_CAST, rod_name=chosen_rod)

    nibble_chance = _NIBBLE_CHANCE.get(chosen_rod, 0.75)
    if random.random() > nibble_chance:
        write_lines(output, T.FISHING_NOTHING)
        return

    # --- Pick a Pokemon from the rod's table ---
    table = _ROD_TABLES.get(chosen_rod, _ROD_TABLES["Old Rod"])
    species_pool = [name for name, _ in table]
    weights = [w for _, w in table]
    species = random.choices(species_pool, weights=weights, k=1)[0]

    level_min, level_max = _ROD_LEVEL_RANGES.get(chosen_rod, (5, 15))
    level = random.randint(level_min, level_max)

    output.write("[bold green]Oh! A bite![/bold green]")
    output.write(f"[green]   You reeled in a wild {species}![/green]")
    output.write("")

    # --- Trigger encounter ---
    trigger_wild_callback(output, species, level)
