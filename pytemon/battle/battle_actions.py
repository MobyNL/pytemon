"""
Battle action functions for Pokemon Terminal.

This module handles all battle-related actions including move execution,
catching Pokemon, fleeing, switching Pokemon, and battle state management.
"""

import random
from typing import TYPE_CHECKING, Optional

from textual.widgets import RichLog

from .. import evolution as _evo_module
from .. import pc_system, pokedex
from .. import stats as _stats
from ..data import get_move
from ..data.move_data import MoveSlot
from ..engine.battle_engine import BattleState
from ..gym_system import handle_elite_four_victory, handle_gym_victory, handle_rematch_gym_victory
from ..locations import get_location
from ..texts.en import battle_actions as T  # noqa: N812
from ..ui.formatters import write_lines, write_lines_fmt
from . import battle_ui

if TYPE_CHECKING:
    from ..data.trainer_data import Trainer
    from ..game_state import GameState
    from ..models import PartyPokemon


def ensure_battle_ready(pokemon: "PartyPokemon") -> None:
    """
    Ensure a Pokemon dict has full battle stats.
    Initializes missing stats from species data for backward compatibility.
    This allows old save files to work with the new battle system.

    Args:
        pokemon: Pokemon dict to initialize
    """
    if (
        "hp" in pokemon
        and "stats" in pokemon
        and "moves" in pokemon
        and "next_level_exp" in pokemon
    ):
        return  # Already battle-ready

    try:
        bs = BattleState()
        data = bs.generate_wild_pokemon(pokemon["name"].upper(), pokemon.get("level", 5))

        # Copy battle stats, preserving existing flags
        pokemon.setdefault("hp", data["hp"])
        pokemon.setdefault("max_hp", data["max_hp"])
        pokemon.setdefault("stats", data["stats"])
        pokemon.setdefault("moves", data["moves"])
        pokemon.setdefault("types", data["types"])
        pokemon.setdefault("experience", 0)
        pokemon.setdefault(
            "next_level_exp", bs.calculate_exp_for_level(pokemon.get("level", 5) + 1)
        )
        pokemon.setdefault("status", None)
    except Exception:
        # Fallback to basic stats if migration fails
        pokemon.setdefault("hp", 20)
        pokemon.setdefault("max_hp", 20)
        pokemon.setdefault("stats", {"attack": 10, "defense": 10, "speed": 10, "special": 10})
        pokemon.setdefault("moves", [{"name": "Tackle", "pp": 35, "max_pp": 35}])
        pokemon.setdefault("types", ["Normal"])
        pokemon.setdefault("experience", 0)
        pokemon.setdefault("next_level_exp", 100)
        pokemon.setdefault("status", None)


def trigger_wild_encounter(
    game_state: "GameState",
    output: RichLog,
    pending_command_callback,
    show_battle_buttons_callback=None,
    show_battle_start_callback=None,
) -> None:
    """
    Trigger a wild Pokemon battle at the current location.

    If ``game_state.game_data["_fishing_encounter"]`` is set (by the fishing
    mechanic) it is consumed and used as the forced wild species/level instead
    of picking randomly from the location's wild pool.

    Args:
        game_state: The game state
        output: The RichLog widget to write to
        pending_command_callback: Callback to set pending command
        show_battle_buttons_callback: Optional callback to show battle action buttons
        show_battle_start_callback: Optional ``(output, on_ready)`` callback that
            displays the battle-start animation and calls ``on_ready()`` when done.
            When omitted the default instant display is used.
    """
    location = game_state.current_location

    # Get the first non-fainted Pokemon
    player_pokemon = game_state.get_active_pokemon()

    if not player_pokemon:
        write_lines(output, T.NO_USABLE_POKEMON)
        return

    # Check for a forced fishing encounter
    fishing_enc = game_state.game_data.pop("_fishing_encounter", None)
    if fishing_enc:
        wild_species = fishing_enc["species"]
        wild_level = fishing_enc["level"]
    else:
        # Check for a generic forced encounter (e.g. legendary, cheat)
        forced_enc = game_state.game_data.pop("_forced_encounter", None)
        if forced_enc:
            wild_species = forced_enc["species"]
            wild_level = forced_enc["level"]
        else:
            # Pick a random wild species and level
            wild_species = random.choice(location.wild_pokemon)
            min_lvl, max_lvl = location.wild_level_range
            wild_level = random.randint(min_lvl, max_lvl)

    # Create and start battle
    bs = BattleState()
    bs.start_wild_battle(player_pokemon, wild_species, wild_level)
    # Safari Zone: no HP damage, special catch mechanics
    if location and location.name == "Safari Zone":
        bs.is_safari = True
    game_state.battle_state = bs
    game_state.in_battle = True

    # Set pending command immediately so tests / headless mode can detect the battle
    # without waiting for the text animation to complete.
    pending_command_callback("battle")

    # Record stats
    _stats.record_wild_encounter(game_state, location.name if location else "Unknown")

    # Mark wild Pokemon as seen in Pokedex
    if pokedex.mark_as_seen(game_state, wild_species):
        output.write(
            f"[dim]📖 Pokedex: {bs.wild_pokemon.get('name', wild_species)} was registered as seen![/dim]"
        )

    def _on_battle_start_done() -> None:
        battle_ui.show_battle_options(game_state, output)
        pending_command_callback("battle")  # refresh (idempotent)
        if show_battle_buttons_callback:
            show_battle_buttons_callback()

    if show_battle_start_callback:
        show_battle_start_callback(output, _on_battle_start_done)
    else:
        battle_ui.show_battle_start(game_state, output)
        _on_battle_start_done()


def trigger_trainer_encounter(
    game_state: "GameState",
    output: RichLog,
    trainer: "Trainer",
    pending_command_callback,
    show_battle_buttons_callback=None,
    show_battle_start_callback=None,
) -> None:
    """
    Trigger a trainer battle.

    Args:
        game_state: The game state
        output: The RichLog widget to write to
        trainer: Trainer data dict
        pending_command_callback: Callback to set pending command
        show_battle_buttons_callback: Optional callback to show battle action buttons
        show_battle_start_callback: Optional ``(output, on_ready)`` callback that
            displays the battle-start animation and calls ``on_ready()`` when done.
            When omitted the default instant display is used.
    """
    # Get the first non-fainted Pokemon
    player_pokemon = game_state.get_active_pokemon()

    if not player_pokemon:
        write_lines(output, T.NO_USABLE_POKEMON)
        return

    # Create and start trainer battle
    bs = BattleState()
    bs.start_trainer_battle(player_pokemon, trainer)
    game_state.battle_state = bs
    game_state.in_battle = True

    # Set pending command immediately so tests / headless mode can detect the battle
    # without waiting for the text animation to complete.
    pending_command_callback("battle")

    # Record stats
    _stats.record_trainer_encounter(game_state)

    # Mark all trainer Pokemon as seen in Pokedex
    trainer_pokemon = trainer.get("pokemon", [])
    for pkmn in trainer_pokemon:
        species = pkmn.get("species", "").upper()
        if species:
            pokedex.mark_as_seen(game_state, species)

    def _on_battle_start_done() -> None:
        battle_ui.show_battle_options(game_state, output)
        pending_command_callback("battle")  # refresh (idempotent)
        if show_battle_buttons_callback:
            show_battle_buttons_callback()

    if show_battle_start_callback:
        show_battle_start_callback(output, _on_battle_start_done)
    else:
        battle_ui.show_trainer_battle_start(game_state, output)
        _on_battle_start_done()


def parse_move_choice(command: str, player: "PartyPokemon") -> "Optional[MoveSlot]":
    """
    Parse a move choice from player input (name or number).

    Args:
        command: Player input
        player: Player's Pokemon dict

    Returns:
        Move dict if found, None otherwise
    """
    cmd = command.lower().strip()

    if cmd.startswith("use "):
        cmd = cmd[4:].strip()

    # Number selection
    if cmd.isdigit():
        idx = int(cmd) - 1
        if 0 <= idx < len(player["moves"]):
            return player["moves"][idx]
        return None

    # Name selection (case-insensitive): exact match first, then partial match
    for move in player["moves"]:
        if move["name"].lower() == cmd:
            return move
    for move in player["moves"]:
        if cmd in move["name"].lower():
            return move

    return None


def execute_player_move(
    game_state: "GameState",
    command: str,
    output: RichLog,
    pending_command_callback,
    show_battle_options_callback,
    show_move_selection_callback,
    handle_battle_victory_callback,
    handle_pokemon_fainted_callback,
) -> None:
    """
    Execute the player's chosen move and then run the wild Pokemon's turn.

    Args:
        game_state: The game state
        command: Player input (move name or number)
        output: The RichLog widget to write to
        pending_command_callback: Callback to set pending command
        show_battle_options_callback: Callback to show battle options
        show_move_selection_callback: Callback to show move selection
        handle_battle_victory_callback: Callback to handle battle victory
        handle_pokemon_fainted_callback: Callback to handle Pokemon fainted
    """
    battle = game_state.battle_state
    player = battle.player_pokemon

    # Handle "Back"
    if command.lower().strip() in ("back", "b"):
        show_battle_options_callback(output)
        pending_command_callback("battle")
        return

    move = parse_move_choice(command, player)

    if not move:
        write_lines(output, T.UNKNOWN_MOVE)
        show_move_selection_callback(output)
        pending_command_callback("select_move")
        return

    if move["pp"] <= 0:
        write_lines_fmt(output, T.MOVE_NO_PP, move_name=move["name"])
        show_move_selection_callback(output)
        pending_command_callback("select_move")
        return

    # ── Speed-based turn order ───────────────────────────────────────────
    # Faster Pokemon moves first. Ties broken randomly.
    player_spd = player.get("stats", {}).get("speed", 0)
    wild_spd = battle.wild_pokemon.get("stats", {}).get("speed", 0)  # type: ignore[union-attr]
    player_goes_first = player_spd > wild_spd or (player_spd == wild_spd and random.random() < 0.5)

    if player_goes_first:
        # ── Player's turn ──────────────────────────────────
        write_lines_fmt(
            output, T.PLAYER_USED_MOVE, player_name=player["name"], move_name=move["name"]
        )
        messages = battle.execute_move(player, battle.wild_pokemon, move["name"])
        for msg in messages:
            output.write(msg)

        if battle.wild_pokemon["hp"] <= 0:
            handle_battle_victory_callback(output)
            return

        # ── Wild Pokemon's turn ────────────────────────────
        execute_wild_pokemon_turn(game_state, output)

        if player["hp"] <= 0:
            handle_pokemon_fainted_callback(output)
            return
    else:
        # ── Wild Pokemon's turn first ──────────────────────
        execute_wild_pokemon_turn(game_state, output)

        if player["hp"] <= 0:
            handle_pokemon_fainted_callback(output)
            return

        # ── Player's turn ──────────────────────────────────
        write_lines_fmt(
            output, T.PLAYER_USED_MOVE, player_name=player["name"], move_name=move["name"]
        )
        messages = battle.execute_move(player, battle.wild_pokemon, move["name"])
        for msg in messages:
            output.write(msg)

        if battle.wild_pokemon["hp"] <= 0:
            handle_battle_victory_callback(output)
            return

    # ── End-of-turn status effects ─────────────────────
    battle = game_state.battle_state
    if battle:
        eot_wild = battle.end_of_turn_effects(battle.wild_pokemon)
        for msg in eot_wild:
            output.write(msg)
        if battle.wild_pokemon["hp"] <= 0:
            handle_battle_victory_callback(output)
            return

        eot_player = battle.end_of_turn_effects(player)
        for msg in eot_player:
            output.write(msg)
        if player["hp"] <= 0:
            handle_pokemon_fainted_callback(output)
            return

    # ── Continue battle ────────────────────────────────
    show_battle_options_callback(output)
    pending_command_callback("battle")


def execute_wild_pokemon_turn(game_state: "GameState", output: RichLog) -> None:
    """
    Execute the opponent Pokemon's turn (random for wild, AI for trainers).

    Args:
        game_state: The game state
        output: The RichLog widget to write to
    """
    battle = game_state.battle_state
    wild = battle.wild_pokemon
    player = battle.player_pokemon

    # Check for available moves
    available = [m for m in wild["moves"] if m["pp"] > 0]

    if not available:
        # Struggle
        opponent_name = (
            f"{battle.trainer_data['name']}'s {wild['name']}"
            if battle.is_trainer_battle
            else f"Wild {wild['name']}"
        )
        write_lines_fmt(output, T.OPPONENT_USED_STRUGGLE, opponent_name=opponent_name)
        struggle_dmg = max(1, player["max_hp"] // 8)
        player["hp"] = max(0, player["hp"] - struggle_dmg)
        write_lines_fmt(output, T.STRUGGLE_DAMAGE, player_name=player["name"], damage=struggle_dmg)
        return

    # Choose move based on battle type
    if battle.is_trainer_battle:
        # Use trainer AI
        move = battle.choose_trainer_move()
        if not move:
            move = random.choice(available)
        opponent_name = f"{battle.trainer_data['name']}'s {wild['name']}"
    else:
        # Wild Pokemon use random moves
        move = random.choice(available)
        opponent_name = f"Wild {wild['name']}"

    battle.enemy_moves_seen.add(move["name"])
    write_lines_fmt(
        output, T.OPPONENT_USED_MOVE, opponent_name=opponent_name, move_name=move["name"]
    )
    messages = battle.execute_move(wild, player, move["name"])
    for msg in messages:
        output.write(msg)


def attempt_flee(
    game_state: "GameState",
    output: RichLog,
    pending_command_callback,
    show_battle_options_callback,
    end_battle_callback,
    handle_pokemon_fainted_callback,
) -> None:
    """
    Attempt to flee from a battle.

    Args:
        game_state: The game state
        output: The RichLog widget to write to
        pending_command_callback: Callback to set pending command
        show_battle_options_callback: Callback to show battle options
        end_battle_callback: Callback to end battle
        handle_pokemon_fainted_callback: Callback to handle Pokemon fainted
    """
    battle = game_state.battle_state

    # Can't flee from trainer battles
    if battle and battle.is_trainer_battle:
        write_lines(output, T.TRAINER_FLEE_BLOCKED)
        show_battle_options_callback(output)
        pending_command_callback("battle")
        return

    # Wild battle - 75% flee chance
    if random.random() < 0.75:
        # Success - varied messages for flavor
        write_lines_fmt(
            output, T.FLEE_RESULT_WRAPPER, message=random.choice(T.FLEE_SUCCESS_MESSAGES)
        )
        _stats.record_fled(game_state)
        end_battle_callback(output)
    else:
        # Failed - varied messages for flavor
        write_lines_fmt(
            output, T.FLEE_RESULT_WRAPPER, message=random.choice(T.FLEE_FAILED_MESSAGES)
        )
        # Wild Pokemon still attacks
        execute_wild_pokemon_turn(game_state, output)
        if battle and battle.player_pokemon["hp"] > 0:
            show_battle_options_callback(output)
            pending_command_callback("battle")
        else:
            handle_pokemon_fainted_callback(output)


def attempt_catch_pokemon(
    game_state: "GameState",
    output: RichLog,
    pending_command_callback,
    show_battle_options_callback,
    end_battle_callback,
    handle_pokemon_fainted_callback,
    ball_type: str = "Pokeball",
    animate_shake_callback=None,
    post_fail_delay_callback=None,
) -> None:
    """
    Attempt to catch the wild Pokemon with a Pokeball.

    Args:
        game_state: The game state
        output: The RichLog widget to write to
        pending_command_callback: Callback to set pending command
        show_battle_options_callback: Callback to show battle options
        end_battle_callback: Callback to end battle
        handle_pokemon_fainted_callback: Callback to handle Pokemon fainted
        ball_type: Type of ball to use (Pokeball, Great Ball, Ultra Ball, Master Ball)
        animate_shake_callback: Optional ``(output, lines, on_complete)`` callback that
            displays the shake animation and calls ``on_complete()`` when done.
            When omitted the shake lines are written instantly.
        post_fail_delay_callback: Optional ``(on_complete)`` callback used only when
            a catch fails. It should invoke ``on_complete()`` after a short delay.
            When omitted, continuation happens immediately.
    """
    battle = game_state.battle_state

    # Can't catch trainer Pokemon!
    if battle and battle.is_trainer_battle:
        trainer = battle.trainer_data
        write_lines_fmt(output, T.TRAINER_BLOCKED_BALL, trainer_name=trainer["name"])
        show_battle_options_callback(output)
        pending_command_callback("battle")
        return

    items = game_state.game_data.get("items", {})

    # Check inventory for the chosen ball type; fall back to any available ball
    if items.get(ball_type, 0) <= 0:
        # Try to find any available ball to inform the player
        if ball_type == "Pokeball":
            write_lines(output, T.NO_POKEBALLS)
        else:
            write_lines_fmt(output, T.NO_BALL_TYPE, ball_type=ball_type)
        show_battle_options_callback(output)
        pending_command_callback("battle")
        return

    wild = battle.wild_pokemon

    # Consume the ball
    items[ball_type] -= 1
    if items[ball_type] <= 0:
        del items[ball_type]

    write_lines_fmt(output, T.THREW_BALL_AT_WILD, ball_type=ball_type, wild_name=wild["name"])

    # Attempt catch (computes result, has no display side-effects)
    caught, shakes, messages = battle.attempt_catch(ball_type)

    # Build the shake sequence lines (animated or instant)
    wiggle_text = "● " * shakes + "○ " * (4 - shakes)
    shake_lines = [*messages, f"[dim]{wiggle_text.strip()}[/dim]", ""]

    def _after_shake() -> None:
        if caught:
            # Successful catch!
            pokemon_party = game_state.game_data.get("pokemon", [])

            if len(pokemon_party) >= 6:
                caught_pokemon = {
                    "name": wild["name"],
                    "number": wild.get("number", 0),
                    "level": wild["level"],
                    "types": wild["types"],
                    "hp": wild["hp"],
                    "max_hp": wild["max_hp"],
                    "stats": wild["stats"],
                    "moves": wild["moves"],
                    "experience": 0,
                    "next_level_exp": battle.calculate_exp_for_level(wild["level"] + 1),
                    "status": wild.get("status"),
                    "no_evolve": False,
                }
                placed_box = pc_system.send_to_pc(game_state, caught_pokemon)
                if placed_box:
                    write_lines_fmt(output, T.CATCH_SUCCESS_PLAIN, wild_name=wild["name"])
                    write_lines_fmt(
                        output,
                        T.PARTY_FULL_SENT_TO_PC,
                        wild_name=wild["name"],
                        box_name=placed_box,
                    )
                    write_lines(output, T.PC_RETRIEVE_HINT)
                    species = wild.get("species", wild["name"]).upper()
                    if pokedex.mark_as_caught(game_state, species):
                        write_lines_fmt(output, T.POKEDEX_CAUGHT_REGISTERED, wild_name=wild["name"])
                        caught_count = len(
                            game_state.game_data.get("pokedex", {}).get("caught", [])
                        )
                        milestone_msg = pokedex.get_caught_milestone_message(caught_count)
                        if milestone_msg:
                            output.write(f"[bold yellow]{milestone_msg}[/bold yellow]")
                        type_msg = pokedex.get_first_type_message(game_state, species)
                        if type_msg:
                            output.write(f"[yellow]{type_msg}[/yellow]")
                else:
                    write_lines_fmt(output, T.CATCH_SUCCESS_PLAIN, wild_name=wild["name"])
                    write_lines_fmt(output, T.PARTY_AND_PC_FULL, wild_name=wild["name"])
            else:
                # Add to party
                caught_pokemon = {
                    "name": wild["name"],
                    "number": wild.get("number", 0),
                    "level": wild["level"],
                    "types": wild["types"],
                    "hp": wild["hp"],
                    "max_hp": wild["max_hp"],
                    "stats": wild["stats"],
                    "moves": wild["moves"],
                    "experience": 0,
                    "next_level_exp": battle.calculate_exp_for_level(wild["level"] + 1),
                    "status": wild.get("status"),
                    "no_evolve": False,
                }
                pokemon_party.append(caught_pokemon)
                write_lines_fmt(output, T.CATCH_SUCCESS, wild_name=wild["name"])

                # Mark as caught in Pokedex
                species = wild.get("species", wild["name"]).upper()
                if pokedex.mark_as_caught(game_state, species):
                    write_lines_fmt(output, T.POKEDEX_CAUGHT_REGISTERED, wild_name=wild["name"])
                    caught_count = len(game_state.game_data.get("pokedex", {}).get("caught", []))
                    milestone_msg = pokedex.get_caught_milestone_message(caught_count)
                    if milestone_msg:
                        output.write(f"[bold yellow]{milestone_msg}[/bold yellow]")
                    type_msg = pokedex.get_first_type_message(game_state, species)
                    if type_msg:
                        output.write(f"[yellow]{type_msg}[/yellow]")
                write_lines_fmt(output, T.ADDED_TO_PARTY, wild_name=wild["name"])

            write_lines(output, T.TRAILING_BLANK)
            # End battle on successful catch
            _stats.record_catch(game_state, wild.get("species", wild["name"]))
            end_battle_callback(output)
        else:
            # Failed catch
            if shakes == 0:
                write_lines_fmt(output, T.CATCH_FAIL_0, wild_name=wild["name"])
            elif shakes == 1:
                write_lines(output, T.CATCH_FAIL_1)
            elif shakes == 2:
                write_lines(output, T.CATCH_FAIL_2)
            elif shakes == 3:
                write_lines(output, T.CATCH_FAIL_3)
            write_lines(output, T.TRAILING_BLANK)

            def _continue_after_failed_catch() -> None:
                # Wild Pokemon gets a free turn
                execute_wild_pokemon_turn(game_state, output)

                # Check if player fainted
                if battle.player_pokemon["hp"] <= 0:
                    handle_pokemon_fainted_callback(output)
                else:
                    show_battle_options_callback(output)
                    pending_command_callback("battle")

            if post_fail_delay_callback:
                post_fail_delay_callback(_continue_after_failed_catch)
            else:
                _continue_after_failed_catch()

    if animate_shake_callback:
        animate_shake_callback(output, shake_lines, _after_shake)
    else:
        for line in shake_lines:
            output.write(line)
        _after_shake()


def handle_safari_action(
    game_state: "GameState",
    output: RichLog,
    action: str,
    pending_command_callback,
    show_battle_options_callback,
    end_battle_callback,
) -> None:
    """
    Handle a Safari Zone action: bait, rock, ball, or run.

    Args:
        game_state: The game state
        output: The RichLog widget to write to
        action: One of "bait", "rock", "ball", "run"
        pending_command_callback: Callback to set pending command
        show_battle_options_callback: Callback to show battle options
        end_battle_callback: Callback to end battle cleanly
    """
    battle = game_state.battle_state
    if not battle or not battle.is_safari:
        return

    wild = battle.wild_pokemon

    if action == "bait":
        battle.safari_bait_turns = 3
        battle.safari_rock_turns = 0
        write_lines_fmt(output, T.SAFARI_BAIT, wild_name=wild["name"])

    elif action == "rock":
        battle.safari_rock_turns = 2
        battle.safari_bait_turns = 0
        write_lines_fmt(output, T.SAFARI_ROCK, wild_name=wild["name"])

    elif action == "ball":
        items = game_state.game_data.get("items", {})
        safari_balls = items.get("Safari Ball", 0)
        if safari_balls <= 0:
            write_lines(output, T.NO_SAFARI_BALLS)
            show_battle_options_callback(output)
            pending_command_callback("battle")
            return

        items["Safari Ball"] = safari_balls - 1

        write_lines_fmt(output, T.THREW_SAFARI_BALL, wild_name=wild["name"])

        caught, shakes, messages = battle.attempt_catch("Safari Ball")

        wiggle_text = "● " * shakes + "○ " * (4 - shakes)
        for msg in messages:
            output.write(msg)
        output.write(f"[dim]{wiggle_text.strip()}[/dim]")
        output.write("")

        if caught:
            pokemon_party = game_state.game_data.get("pokemon", [])
            caught_pokemon = {
                "name": wild["name"],
                "number": wild.get("number", 0),
                "level": wild["level"],
                "types": wild["types"],
                "hp": wild["hp"],
                "max_hp": wild["max_hp"],
                "stats": wild["stats"],
                "moves": wild["moves"],
                "experience": 0,
                "next_level_exp": battle.calculate_exp_for_level(wild["level"] + 1),
                "status": None,
                "no_evolve": False,
            }
            if len(pokemon_party) >= 6:
                placed_box = pc_system.send_to_pc(game_state, caught_pokemon)
                if placed_box:
                    write_lines_fmt(output, T.CATCH_SUCCESS, wild_name=wild["name"])
                    write_lines_fmt(
                        output,
                        T.PARTY_FULL_SENT_TO_PC,
                        wild_name=wild["name"],
                        box_name=placed_box,
                    )
                else:
                    write_lines_fmt(output, T.CATCH_SUCCESS, wild_name=wild["name"])
                    write_lines_fmt(output, T.PARTY_AND_PC_FULL, wild_name=wild["name"])
            else:
                pokemon_party.append(caught_pokemon)
                write_lines_fmt(output, T.CATCH_SUCCESS, wild_name=wild["name"])
                write_lines_fmt(output, T.ADDED_TO_PARTY, wild_name=wild["name"])

            species = wild.get("species", wild["name"]).upper()
            if pokedex.mark_as_caught(game_state, species):
                write_lines_fmt(output, T.POKEDEX_CAUGHT_REGISTERED, wild_name=wild["name"])
                caught_count = len(game_state.game_data.get("pokedex", {}).get("caught", []))
                milestone_msg = pokedex.get_caught_milestone_message(caught_count)
                if milestone_msg:
                    output.write(f"[bold yellow]{milestone_msg}[/bold yellow]")

            write_lines(output, T.TRAILING_BLANK)
            _stats.record_catch(game_state, wild.get("species", wild["name"]))
            end_battle_callback(output)
            return
        else:
            if shakes == 0:
                write_lines_fmt(output, T.CATCH_FAIL_0, wild_name=wild["name"])
            elif shakes == 1:
                write_lines(output, T.CATCH_FAIL_1)
            elif shakes == 2:
                write_lines(output, T.CATCH_FAIL_2)
            elif shakes == 3:
                write_lines(output, T.CATCH_FAIL_3)
            write_lines(output, T.TRAILING_BLANK)

    elif action == "run":
        write_lines(output, T.SAFARI_FLED_SAFE)
        end_battle_callback(output)
        return

    # After action: check if wild Pokemon flees (except on run which already returned)
    flee_chance = 0.10  # base flee chance per turn
    if battle.safari_rock_turns > 0:
        flee_chance = 0.35  # angry Pokemon flee more
        battle.safari_rock_turns -= 1
    elif battle.safari_bait_turns > 0:
        flee_chance = 0.02  # baited Pokemon rarely flee
        battle.safari_bait_turns -= 1

    if random.random() < flee_chance:
        write_lines_fmt(output, T.WILD_FLED, wild_name=wild["name"])
        end_battle_callback(output)
        return

    show_battle_options_callback(output)
    pending_command_callback("battle")


def execute_switch(
    game_state: "GameState",
    target: str,
    output: RichLog,
    pending_command_callback,
    show_battle_options_callback,
    show_pokemon_switch_menu_callback,
    handle_pokemon_fainted_callback,
) -> None:
    """
    Execute a mid-battle Pokemon switch.

    Args:
        game_state: The game state
        target: Number or name of the Pokemon to switch to
        output: The RichLog widget to write to
        pending_command_callback: Callback to set pending command
        show_battle_options_callback: Callback to show battle options
        show_pokemon_switch_menu_callback: Callback to show switch menu
        handle_pokemon_fainted_callback: Callback to handle Pokemon fainted
    """
    battle = game_state.battle_state
    if not battle:
        return

    if target.lower().strip() in ("back", "cancel", "no"):
        write_lines(output, T.SWITCH_CANCELLED)
        show_battle_options_callback(output)
        pending_command_callback("battle")
        return

    party = game_state.game_data.get("pokemon", [])
    active = battle.player_pokemon

    # Parse target by number or name
    chosen = None
    t = target.strip()
    if t.isdigit():
        idx = int(t) - 1
        if 0 <= idx < len(party) and not isinstance(party[idx], str):
            chosen = party[idx]
    else:
        for p in party:
            if not isinstance(p, str) and t.lower() in p["name"].lower():
                chosen = p
                break

    if not chosen:
        write_lines_fmt(output, T.INVALID_SWITCH_SELECTION, target=target)
        show_pokemon_switch_menu_callback(output)
        return

    if chosen is active:
        write_lines_fmt(output, T.ALREADY_IN_BATTLE, pokemon_name=chosen["name"])
        show_battle_options_callback(output)
        pending_command_callback("battle")
        return

    if chosen["hp"] <= 0:
        write_lines_fmt(output, T.FAINTED_CANNOT_BATTLE, pokemon_name=chosen["name"])
        show_pokemon_switch_menu_callback(output)
        return

    # Perform switch
    battle.player_pokemon = chosen
    write_lines_fmt(
        output,
        T.SWITCH_PERFORMED,
        active_name=active["name"],
        chosen_name=chosen["name"],
    )

    # Wild Pokemon gets a free attack on the incoming Pokemon
    execute_wild_pokemon_turn(game_state, output)

    if battle.player_pokemon["hp"] <= 0:
        handle_pokemon_fainted_callback(output)
    else:
        show_battle_options_callback(output)
        pending_command_callback("battle")


def handle_battle_victory(
    game_state: "GameState",
    output: RichLog,
    pending_command_callback,
    show_battle_options_callback,
    handle_trainer_defeated_callback,
    end_battle_callback,
    queue_evolution_callback=None,
    queue_move_learn_callback=None,
) -> None:
    """
    Handle opponent Pokemon fainting (wild or trainer).

    Args:
        game_state: The game state
        output: The RichLog widget to write to
        pending_command_callback: Callback to set pending command
        show_battle_options_callback: Callback to show battle options
        handle_trainer_defeated_callback: Callback to handle trainer defeated
        end_battle_callback: Callback to end battle
    """
    battle = game_state.battle_state
    wild = battle.wild_pokemon
    player = battle.player_pokemon

    write_lines(output, T.TRAILING_BLANK)

    # Different messages for trainer vs wild
    if battle.is_trainer_battle:
        trainer = battle.trainer_data
        write_lines_fmt(
            output,
            T.OPPONENT_FAINTED_TRAINER,
            trainer_name=trainer["name"],
            wild_name=wild["name"],
        )
    else:
        write_lines_fmt(output, T.OPPONENT_FAINTED_WILD, wild_name=wild["name"])

    # Record KO in stats
    _stats.record_ko_dealt(game_state, player["name"])
    if not battle.is_trainer_battle:
        _stats.record_wild_battle_won(game_state)

    write_lines(output, T.TRAILING_BLANK)

    # Award experience
    exp = battle.calculate_exp_yield()
    player["experience"] = player.get("experience", 0) + exp
    write_lines_fmt(output, T.EXP_GAINED, player_name=player["name"], exp=exp)

    # Check for level up (can trigger multiple times)
    while True:
        leveled_up, new_level = battle.check_level_up(player)
        if leveled_up:
            write_lines_fmt(output, T.LEVEL_UP, player_name=player["name"], new_level=new_level)
            # Check for new moves at this level
            new_move_names = battle.get_new_moves_at_level(player["name"].upper(), new_level)
            for move_name in new_move_names:
                move_data = get_move(move_name)
                if not move_data:
                    continue
                existing_names = [m["name"] for m in player.get("moves", [])]
                if move_name in existing_names:
                    continue
                new_move = MoveSlot(name=move_name, pp=move_data["pp"], max_pp=move_data["pp"])
                if len(player.get("moves", [])) < 4:
                    player["moves"].append(new_move)
                    write_lines_fmt(
                        output,
                        T.LEARNED_MOVE,
                        player_name=player["name"],
                        move_name=move_name,
                    )
                else:
                    if queue_move_learn_callback:
                        # Determine post-battle action for the resume call
                        if battle.is_trainer_battle:
                            if battle.has_more_pokemon():
                                post_action = "trainer_next"
                            else:
                                post_action = "trainer_defeated"
                        else:
                            post_action = "wild_end"
                        # Collect all overflow moves from the full list that aren't already known
                        known = [m["name"] for m in player.get("moves", [])]
                        all_new = [mn for mn in new_move_names if mn not in known]
                        queue_move_learn_callback(player, all_new, post_action, output)
                        return  # callback owns the rest
                    else:
                        old_move = player["moves"][-1]["name"]
                        player["moves"][-1] = new_move
                        write_lines_fmt(
                            output,
                            T.FORGOT_AND_LEARNED_MOVE,
                            player_name=player["name"],
                            old_move=old_move,
                            move_name=move_name,
                        )
        else:
            break

    # Determine what comes next after this Pokemon faints
    evo_target = _evo_module.get_level_evolution(player)

    # If the trainer has more Pokemon left, defer evolution until after the whole battle.
    # Don't overwrite a pending_evolution that is already queued for this same pokemon.
    if evo_target and battle.is_trainer_battle and battle.has_more_pokemon():
        if not battle.pending_evolution:
            battle.pending_evolution = (player, evo_target)
        evo_target = None

    # Battle is over (wild fainted or trainer's last Pokemon) — trigger evolution prompt now.
    # Clear any stale deferred evolution first: it is for the same pokemon and would otherwise
    # fire a second prompt when handle_trainer_defeated runs after the player confirms.
    if evo_target and queue_evolution_callback:
        battle.pending_evolution = None
        post_action = "trainer_defeated" if battle.is_trainer_battle else "wild_end"
        queue_evolution_callback(player, evo_target, post_action, output)
        return

    # No interactive evolution queue — apply immediately (or no evolution needed)
    if evo_target:
        if _evo_module.apply_evolution(game_state, player, output, update_battle_state=True):
            player = game_state.battle_state.player_pokemon

    # Handle trainer battle continuation or victory
    if battle.is_trainer_battle:
        if battle.has_more_pokemon():
            # Trainer switches to next Pokemon
            next_pokemon = battle.switch_to_next_pokemon()
            trainer = battle.trainer_data
            write_lines_fmt(
                output,
                T.TRAINER_SENT_NEXT,
                trainer_name=trainer["name"],
                next_name=next_pokemon["name"],
                next_level=next_pokemon["level"],
            )
            show_battle_options_callback(output)
            pending_command_callback("battle")
        else:
            # Trainer defeated!
            handle_trainer_defeated_callback(output)
    else:
        # Wild battle - end battle
        write_lines(output, T.TRAILING_BLANK)
        end_battle_callback(output)


def handle_trainer_defeated(game_state: "GameState", output: RichLog, end_battle_callback) -> None:
    """
    Handle defeating a trainer.

    Args:
        game_state: The game state
        output: The RichLog widget to write to
        end_battle_callback: Callback to end battle
    """
    battle = game_state.battle_state
    trainer = battle.trainer_data
    player_name = game_state.game_data.get("player_name", "Trainer")

    write_lines_fmt(
        output,
        T.TRAINER_DEFEATED_HEADER,
        trainer_class=trainer["trainer_class"],
        trainer_name=trainer["name"],
    )

    # Show trainer defeat text
    for line in trainer.get("defeat_text", []):
        formatted_line = line.replace("{player_name}", player_name)
        output.write(formatted_line)

    write_lines(output, T.TRAILING_BLANK)

    # Award prize money
    prize = battle.prize_money
    game_state.game_data["money"] = game_state.game_data.get("money", 0) + prize
    write_lines_fmt(output, T.PRIZE_MONEY, prize=prize)

    # Mark trainer as defeated
    defeated = game_state.game_data.get("defeated_trainers", [])
    if trainer["id"] not in defeated:
        defeated.append(trainer["id"])
        game_state.game_data["defeated_trainers"] = defeated

    # Set rival Cerulean beaten flag
    if trainer.get("id") == "rival_cerulean":
        game_state.game_data.setdefault("story_flags", {})["rival_cerulean_beaten"] = True

    # Record trainer battle win
    _stats.record_trainer_battle_won(game_state)

    # Check if this was a gym leader and award badge
    if trainer.get("trainer_class") == "Gym Leader":
        if trainer["id"].endswith("_rematch"):
            from ..gym_system import handle_rematch_gym_victory

            handle_rematch_gym_victory(game_state, trainer["id"], output)
        else:
            handle_gym_victory(game_state, trainer["id"], output)
    elif trainer.get("trainer_class") in ("Elite Four", "Champion"):
        handle_elite_four_victory(game_state, trainer["id"], output)
    else:
        write_lines(output, T.BATTLE_WON)

    end_battle_callback(output)


def handle_pokemon_fainted(
    game_state: "GameState",
    output: RichLog,
    end_battle_callback,
    show_faint_options_callback=None,
) -> None:
    """
    Handle player's Pokemon fainting.

    Args:
        game_state: The game state
        output: The RichLog widget to write to
        end_battle_callback: Callback to end battle
        show_faint_options_callback: Optional callback(can_run: bool) called when
            the player has other usable Pokemon — shows the faint-switch panel.
            If None, falls back to legacy auto-end behaviour.
    """
    battle = game_state.battle_state
    player = battle.player_pokemon

    write_lines_fmt(output, T.PLAYER_FAINTED, player_name=player["name"])

    # Record faint in stats
    _stats.record_faint(game_state, player["name"])

    # Check for other usable Pokemon (Sprint 2: simplified - just whiteout)
    other_ready = [
        p
        for p in game_state.game_data.get("pokemon", [])
        if not isinstance(p, str) and p is not player and p.get("hp", 0) > 0
    ]

    if other_ready:
        write_lines(output, T.OTHER_POKEMON_STILL_STANDING)
        if show_faint_options_callback:
            write_lines(output, T.CHOOSE_NEXT_POKEMON)
            is_trainer = bool(battle and battle.is_trainer_battle)
            show_faint_options_callback(not is_trainer)
        else:
            # Legacy / test fallback keeps old behavior for callers that
            # don't support the faint-switch interaction.
            player["hp"] = player["max_hp"]
            for m in player.get("moves", []):
                m["pp"] = m.get("max_pp", m["pp"])
            write_lines(output, T.NURSE_HEALED_FAINTED)
            end_battle_callback(output)
    else:
        write_lines(output, T.NO_MORE_POKEMON)

        # Determine respawn location
        last_pokemon_center = game_state.game_data.get("last_pokemon_center")
        if last_pokemon_center:
            respawn_location = last_pokemon_center
            write_lines_fmt(output, T.WAKE_UP_CENTER, respawn_location=respawn_location)
        else:
            # Never visited a Pokemon Center, return home
            respawn_location = "Pallet Town"
            write_lines(output, T.WAKE_UP_HOME)

        # Transport player to respawn location
        game_state.game_data["location"] = respawn_location
        game_state.current_location = get_location(respawn_location)

        if last_pokemon_center:
            write_lines(output, T.ALL_HEALED_AFTER_BLACKOUT)
        else:
            write_lines(output, T.ALL_HEALED_AT_HOME)

        # Heal everyone
        for p in game_state.game_data.get("pokemon", []):
            if not isinstance(p, str):
                p["hp"] = p.get("max_hp", p["hp"])
                for m in p.get("moves", []):
                    m["pp"] = m.get("max_pp", m["pp"])

        write_lines(output, T.TRAILING_BLANK)
        end_battle_callback(output)


def use_heal_item(
    game_state: "GameState",
    output: RichLog,
    item_name: str,
    heal_amount: int,
    pending_command_callback,
    show_battle_options_callback,
    handle_pokemon_fainted_callback,
) -> None:
    """
    Use a healing item during battle.

    Args:
        game_state: The game state
        output: The RichLog widget to write to
        item_name: Name of the healing item
        heal_amount: Amount of HP to heal
        pending_command_callback: Callback to set pending command
        show_battle_options_callback: Callback to show battle options
        handle_pokemon_fainted_callback: Callback to handle Pokemon fainted
    """
    items = game_state.game_data.get("items", {})
    count = items.get(item_name, 0)
    battle = game_state.battle_state
    player = battle.player_pokemon

    if count <= 0:
        write_lines_fmt(output, T.NO_ITEM_LEFT, item_name=item_name)
        show_battle_options_callback(output)
        pending_command_callback("battle")
        return

    actual_heal = min(heal_amount, player["max_hp"] - player["hp"])
    player["hp"] += actual_heal
    items[item_name] -= 1
    if items[item_name] <= 0:
        del items[item_name]

    write_lines_fmt(
        output,
        T.HEAL_ITEM_USED,
        player_name=player["name"],
        heal_amount=actual_heal,
    )

    execute_wild_pokemon_turn(game_state, output)

    if battle.player_pokemon["hp"] <= 0:
        handle_pokemon_fainted_callback(output)
        return

    show_battle_options_callback(output)
    pending_command_callback("battle")


def use_status_cure(
    game_state: "GameState",
    output: RichLog,
    item_name: str,
    cures_status: str,
    cure_msg: str,
    pending_command_callback,
    show_battle_options_callback,
    handle_pokemon_fainted_callback,
) -> None:
    """
    Use a status-curing item during battle.

    Args:
        game_state: The game state
        output: The RichLog widget to write to
        item_name: Name of the status cure item
        cures_status: Status condition it cures
        cure_msg: Message to display when cured
        pending_command_callback: Callback to set pending command
        show_battle_options_callback: Callback to show battle options
        handle_pokemon_fainted_callback: Callback to handle Pokemon fainted
    """
    items = game_state.game_data.get("items", {})
    count = items.get(item_name, 0)
    battle = game_state.battle_state
    player = battle.player_pokemon

    if count <= 0:
        write_lines_fmt(output, T.NO_ITEM_LEFT, item_name=item_name)
        show_battle_options_callback(output)
        pending_command_callback("battle")
        return

    if player.get("status") != cures_status:
        write_lines_fmt(output, T.WRONG_STATUS_CONDITION, player_name=player["name"])
        show_battle_options_callback(output)
        pending_command_callback("battle")
        return

    player["status"] = None
    player["sleep_count"] = 0
    items[item_name] -= 1
    if items[item_name] <= 0:
        del items[item_name]

    write_lines_fmt(output, T.STATUS_CURED, player_name=player["name"], cure_msg=cure_msg)

    execute_wild_pokemon_turn(game_state, output)

    if battle.player_pokemon["hp"] <= 0:
        handle_pokemon_fainted_callback(output)
        return

    show_battle_options_callback(output)
    pending_command_callback("battle")


def use_full_restore(
    game_state: "GameState",
    output: RichLog,
    pending_command_callback,
    show_battle_options_callback,
    handle_pokemon_fainted_callback,
) -> None:
    """
    Use a Full Restore during battle.

    Fully heals the player's active Pokemon and clears any status condition.

    Args:
        game_state: The game state
        output: The RichLog widget to write to
        pending_command_callback: Callback to set pending command
        show_battle_options_callback: Callback to show battle options
        handle_pokemon_fainted_callback: Callback to handle Pokemon fainted
    """
    item_name = "Full Restore"
    items = game_state.game_data.get("items", {})
    count = items.get(item_name, 0)
    battle = game_state.battle_state
    player = battle.player_pokemon

    if count <= 0:
        write_lines_fmt(output, T.NO_ITEM_LEFT, item_name=item_name)
        show_battle_options_callback(output)
        pending_command_callback("battle")
        return

    actual_heal = player["max_hp"] - player["hp"]
    player["hp"] = player["max_hp"]
    old_status = player.get("status")
    player["status"] = None
    player["sleep_count"] = 0
    items[item_name] -= 1
    if items[item_name] <= 0:
        del items[item_name]

    write_lines_fmt(
        output,
        T.HEAL_ITEM_USED,
        player_name=player["name"],
        heal_amount=actual_heal,
    )
    if old_status:
        write_lines_fmt(
            output, T.STATUS_CURED, player_name=player["name"], cure_msg="fully restored"
        )

    execute_wild_pokemon_turn(game_state, output)

    if battle.player_pokemon["hp"] <= 0:
        handle_pokemon_fainted_callback(output)
        return

    show_battle_options_callback(output)
    pending_command_callback("battle")


def end_battle(game_state: "GameState", output: RichLog, look_around_callback) -> None:
    """
    Clean up after a battle ends and return to exploration.

    Args:
        game_state: The game state
        output: The RichLog widget to write to
        look_around_callback: Callback to show location after battle
    """
    if game_state.battle_state:
        game_state.battle_state.end_battle()
    game_state.battle_state = None
    game_state.in_battle = False

    # Show location after battle
    look_around_callback(output)
