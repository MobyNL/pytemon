"""
Evolution system for the Pokemon game.

Handles level-up evolution checks and applying evolution to Pokemon in the party.
Item-based evolutions (Thunder Stone, etc.) are not triggered automatically
during normal gameplay — they would require a separate item-use flow.
"""

from typing import TYPE_CHECKING, Optional

from textual.widgets import RichLog

from .data.pokemon_data import POKEMON
from .engine import BattleState as _BattleStateClass
from .texts.en import evolution as T
from .ui.formatters import write_lines, write_lines_fmt

if TYPE_CHECKING:
    from .game_state import GameState
    from .models import PartyPokemon

# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def get_level_evolution(pokemon: "PartyPokemon") -> Optional[str]:
    """
    Return the evolved form name if ``pokemon`` meets its level-up evolution
    condition, otherwise return None.

    Skips Pokémon that have the ``no_evolve`` flag set (e.g. the rival's
    partner Pikachu that stubbornly refuses to evolve).

    Args:
        pokemon: The Pokémon party dict (must have 'number', 'level' keys).

    Returns:
        Uppercase name of the evolved form, or None.
    """
    if pokemon.get("no_evolve"):
        return None

    pokemon_number = pokemon.get("number")
    if not pokemon_number or pokemon_number not in POKEMON:
        return None

    species = POKEMON[pokemon_number]
    evolution = species.get("evolution")
    if not evolution:
        return None

    # Only handle level-based evolutions here; skip list (multi-branch) and item evolutions
    if isinstance(evolution, list):
        return None  # multi-branch stone evolution (e.g. Eevee)
    evo_level: Optional[int] = evolution.get("level")  # type: ignore[union-attr]
    if evo_level is None:
        return None  # item-based or trade — not triggered in battle

    if pokemon.get("level", 1) >= evo_level:
        return evolution.get("into")  # type: ignore[union-attr]

    return None


def get_stone_evolution(pokemon: "PartyPokemon", item_name: str) -> Optional[str]:
    """
    Return the evolved form name if ``pokemon`` can evolve using ``item_name``.

    Handles both single-branch evolutions (dict) and multi-branch evolutions
    (list, e.g. Eevee with three stone options).

    Args:
        pokemon:   The Pokémon party dict.
        item_name: Uppercase item name, e.g. ``"FIRE STONE"``.

    Returns:
        Uppercase evolved form name, or None if no match.
    """
    if pokemon.get("no_evolve"):
        return None

    pokemon_number = pokemon.get("number")
    if not pokemon_number or pokemon_number not in POKEMON:
        return None

    evolution = POKEMON[pokemon_number].get("evolution")
    if not evolution:
        return None

    item_upper = item_name.upper()

    # Multi-branch (Eevee)
    if isinstance(evolution, list):
        for branch in evolution:
            if branch.get("item", "").upper() == item_upper:
                return branch.get("into")
        return None

    # Single branch
    if evolution.get("item", "").upper() == item_upper:
        return evolution.get("into")

    return None


def apply_evolution(
    game_state: "GameState",
    pokemon_ref: "PartyPokemon",
    output: RichLog,
    *,
    update_battle_state: bool = False,
) -> bool:
    """
    Evolve a Pokémon that already meets its level-up evolution condition.

    Finds the Pokémon in the player's party by object identity (``is``),
    creates the evolved form at the same level, preserves HP percentage and
    status condition, then replaces the slot in the party list.

    Args:
        game_state:          The current GameState.
        pokemon_ref:         The exact dict object that lives in the party.
        output:              RichLog widget to write evolution messages to.
        update_battle_state: If True, also updates ``game_state.battle_state.
                             player_pokemon`` to the new evolved dict so that
                             mid-battle references stay valid (not normally
                             needed since evolution fires after the enemy
                             faints).

    Returns:
        True if evolution was successfully applied, False otherwise.
    """
    evolved_form = get_level_evolution(pokemon_ref)
    if not evolved_form:
        return False

    return force_evolve(
        game_state,
        pokemon_ref,
        evolved_form,
        output,
        update_battle_state=update_battle_state,
    )


def force_evolve(
    game_state: "GameState",
    pokemon_ref: "PartyPokemon",
    evolved_form_name: str,
    output: RichLog,
    *,
    update_battle_state: bool = False,
    silent_preamble: bool = False,
) -> bool:
    """
    Apply evolution to ``pokemon_ref`` into ``evolved_form_name`` unconditionally.

    Used by cheat commands to bypass the level requirement.  All other logic
    (stat recalculation, HP preservation, party replacement) is identical to
    the natural evolution path.

    Args:
        game_state:          The current GameState.
        pokemon_ref:         The exact dict object that lives in the party.
        evolved_form_name:   Uppercase name of the target evolution (e.g. "CHARMELEON").
        output:              RichLog widget to write evolution messages to.
        update_battle_state: If True, also updates ``game_state.battle_state.
                             player_pokemon`` to the new evolved dict.
        silent_preamble:     If True, skip the "What? X is evolving!" preamble
                             lines (used when the caller already animated them).

    Returns:
        True if evolution was applied, False if the target form couldn't be found.
    """
    old_name = pokemon_ref.get("name", "???")
    current_level = pokemon_ref.get("level", 1)

    # ---- Locate Pokémon in party by identity --------------------------------
    party = game_state.game_data.get("pokemon", [])
    idx = next((i for i, p in enumerate(party) if p is pokemon_ref), None)
    if idx is None:
        # Fallback: match by name + level (shouldn't normally happen)
        idx = next(
            (
                i
                for i, p in enumerate(party)
                if p.get("name") == old_name and p.get("level") == current_level
            ),
            None,
        )
    if idx is None:
        return False

    # ---- Build evolved Pokémon -----------------------------------------------
    engine = _BattleStateClass()
    evolved_pokemon = engine.generate_wild_pokemon(evolved_form_name, current_level)
    if not evolved_pokemon:
        return False

    # Preserve HP percentage
    hp_pct = pokemon_ref.get("hp", 1) / max(pokemon_ref.get("max_hp", 1), 1)
    evolved_pokemon["hp"] = max(1, int(evolved_pokemon["max_hp"] * hp_pct))

    # Preserve status condition and flags
    evolved_pokemon["status"] = pokemon_ref.get("status")
    if pokemon_ref.get("no_evolve"):
        evolved_pokemon["no_evolve"] = True

    # Preserve experience total
    evolved_pokemon["experience"] = pokemon_ref.get("experience", 0)

    # ---- Replace in party ---------------------------------------------------
    party[idx] = evolved_pokemon

    # Optionally keep the battle state reference current
    if update_battle_state and game_state.battle_state:
        game_state.battle_state.player_pokemon = evolved_pokemon

    # ---- Print evolution sequence -------------------------------------------
    if not silent_preamble:
        write_lines_fmt(output, T.EVOLVING_LINE, old_name=old_name)
        write_lines(output, T.EVOLUTION_PREAMBLE)
    write_lines_fmt(
        output,
        T.EVOLUTION_SUCCESS,
        old_name=old_name,
        evolved_form=evolved_form_name,
        current_level=current_level,
        hp=evolved_pokemon["hp"],
        max_hp=evolved_pokemon["max_hp"],
    )

    return True
