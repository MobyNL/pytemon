"""
Battle action functions for Pokemon Terminal.

This module handles all battle-related actions including move execution,
catching Pokemon, fleeing, switching Pokemon, and battle state management.
"""

import random
from typing import TYPE_CHECKING, Optional

from textual.widgets import RichLog

from .. import pokedex
from .. import stats as _stats
from ..data import get_move
from ..data.move_data import MoveSlot
from ..engine.battle_engine import BattleState
from ..locations import get_location

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
    from . import battle_ui

    location = game_state.current_location

    # Get the first non-fainted Pokemon
    player_pokemon = game_state.get_active_pokemon()

    if not player_pokemon:
        output.write("[red]❌ All your Pokemon have fainted! Head to a Pokemon Center![/red]")
        output.write("")
        return

    # Check for a forced fishing encounter
    fishing_enc = game_state.game_data.pop("_fishing_encounter", None)
    if fishing_enc:
        wild_species = fishing_enc["species"]
        wild_level = fishing_enc["level"]
    else:
        # Pick a random wild species and level
        wild_species = random.choice(location.wild_pokemon)
        min_lvl, max_lvl = location.wild_level_range
        wild_level = random.randint(min_lvl, max_lvl)

    # Create and start battle
    bs = BattleState()
    bs.start_wild_battle(player_pokemon, wild_species, wild_level)
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
    from . import battle_ui

    # Get the first non-fainted Pokemon
    player_pokemon = game_state.get_active_pokemon()

    if not player_pokemon:
        output.write("[red]❌ All your Pokemon have fainted! Head to a Pokemon Center![/red]")
        output.write("")
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

    # Name selection (case-insensitive, partial match)
    for move in player["moves"]:
        if move["name"].lower() == cmd or cmd in move["name"].lower():
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
        output.write("[red]❌ Unknown move. Type the name, number, or 'Back'.[/red]")
        output.write("")
        show_move_selection_callback(output)
        pending_command_callback("select_move")
        return

    if move["pp"] <= 0:
        output.write(f"[red]❌ {move['name']} has no PP left! Choose another move.[/red]")
        output.write("")
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
        output.write("")
        output.write(f"[bold]{player['name']} used {move['name']}![/bold]")
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
        output.write("")
        output.write(f"[bold]{player['name']} used {move['name']}![/bold]")
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
        output.write(f"[yellow]{opponent_name} has no moves left! It used Struggle![/yellow]")
        struggle_dmg = max(1, player["max_hp"] // 8)
        player["hp"] = max(0, player["hp"] - struggle_dmg)
        output.write(f"[cyan]{player['name']} took {struggle_dmg} damage![/cyan]")
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
    output.write("")
    output.write(f"[yellow]{opponent_name} used {move['name']}![/yellow]")
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
        output.write("")
        output.write("[red]❌ No! There's no running from a trainer battle![/red]")
        output.write("")
        show_battle_options_callback(output)
        pending_command_callback("battle")
        return

    # Wild battle - 75% flee chance
    if random.random() < 0.75:
        # Success - varied messages for flavor
        success_messages = [
            "[cyan]Got away safely![/cyan]",
            "[cyan]You managed to escape![/cyan]",
            "[cyan]Fled successfully![/cyan]",
            "[cyan]You got away![/cyan]",
        ]
        output.write("")
        output.write(random.choice(success_messages))
        output.write("")
        _stats.record_fled(game_state)
        end_battle_callback(output)
    else:
        # Failed - varied messages for flavor
        fail_messages = [
            "[yellow]Can't escape![/yellow]",
            "[yellow]Couldn't get away![/yellow]",
            "[yellow]Failed to flee![/yellow]",
            "[yellow]No! Can't escape![/yellow]",
        ]
        output.write("")
        output.write(random.choice(fail_messages))
        output.write("")
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
    """
    battle = game_state.battle_state

    # Can't catch trainer Pokemon!
    if battle and battle.is_trainer_battle:
        trainer = battle.trainer_data
        output.write("")
        output.write("[red]❌ The trainer blocked the Ball![/red]")
        output.write(f"[yellow]{trainer['name']}: Don't be a thief![/yellow]")
        output.write("")
        show_battle_options_callback(output)
        pending_command_callback("battle")
        return

    items = game_state.game_data.get("items", {})

    # Check inventory for the chosen ball type; fall back to any available ball
    if items.get(ball_type, 0) <= 0:
        # Try to find any available ball to inform the player
        output.write("")
        if ball_type == "Pokeball":
            output.write("[red]❌ You have no Pokeballs![/red]")
            output.write("[dim]Buy Pokeballs at the Pokemart[/dim]")
        else:
            output.write(f"[red]❌ You have no {ball_type}s![/red]")
            output.write("[dim]Check your bag for available Pokéballs[/dim]")
        output.write("")
        show_battle_options_callback(output)
        pending_command_callback("battle")
        return

    wild = battle.wild_pokemon

    # Consume the ball
    items[ball_type] -= 1
    if items[ball_type] <= 0:
        del items[ball_type]

    output.write("")
    output.write(f"[bold cyan]You threw a {ball_type} at wild {wild['name']}![/bold cyan]")
    output.write("")

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
                from .. import pc_system

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
                    output.write(f"[green]★ Gotcha! {wild['name']} was caught! ★[/green]")
                    output.write(
                        f"[yellow]  Your party is full — {wild['name']} was sent to {placed_box}![/yellow]"
                    )
                    output.write(
                        "[dim]  Access Bill's PC at any Pokemon Center to retrieve it.[/dim]"
                    )
                    species = wild.get("species", wild["name"]).upper()
                    if pokedex.mark_as_caught(game_state, species):
                        output.write(
                            f"[dim]📖 Pokedex: {wild['name']} was registered as caught![/dim]"
                        )
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
                    output.write(f"[green]★ Gotcha! {wild['name']} was caught! ★[/green]")
                    output.write(
                        f"[red]  Your party and PC are both full! {wild['name']} could not be stored.[/red]"
                    )
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
                output.write(f"[bold green]★ Gotcha! {wild['name']} was caught! ★[/bold green]")

                # Mark as caught in Pokedex
                species = wild.get("species", wild["name"]).upper()
                if pokedex.mark_as_caught(game_state, species):
                    output.write(f"[dim]📖 Pokedex: {wild['name']} was registered as caught![/dim]")
                    caught_count = len(game_state.game_data.get("pokedex", {}).get("caught", []))
                    milestone_msg = pokedex.get_caught_milestone_message(caught_count)
                    if milestone_msg:
                        output.write(f"[bold yellow]{milestone_msg}[/bold yellow]")
                    type_msg = pokedex.get_first_type_message(game_state, species)
                    if type_msg:
                        output.write(f"[yellow]{type_msg}[/yellow]")
                output.write("")
                output.write(f"[green]✓ {wild['name']} was added to your party![/green]")

            output.write("")
            # End battle on successful catch
            _stats.record_catch(game_state, wild.get("species", wild["name"]))
            end_battle_callback(output)
        else:
            # Failed catch
            if shakes == 0:
                output.write(f"[yellow]Oh no! {wild['name']} broke free immediately![/yellow]")
            elif shakes == 1:
                output.write("[yellow]Aww! It appeared to be caught![/yellow]")
            elif shakes == 2:
                output.write("[yellow]Aargh! Almost had it![/yellow]")
            elif shakes == 3:
                output.write("[yellow]Gah! It was so close, too![/yellow]")
            output.write("")

            # Wild Pokemon gets a free turn
            execute_wild_pokemon_turn(game_state, output)

            # Check if player fainted
            if battle.player_pokemon["hp"] <= 0:
                handle_pokemon_fainted_callback(output)
            else:
                show_battle_options_callback(output)
                pending_command_callback("battle")

    if animate_shake_callback:
        animate_shake_callback(output, shake_lines, _after_shake)
    else:
        for line in shake_lines:
            output.write(line)
        _after_shake()


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
        output.write("[dim]Switch cancelled.[/dim]")
        output.write("")
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
        output.write(f"[red]❌ Invalid selection: {target}[/red]")
        show_pokemon_switch_menu_callback(output)
        return

    if chosen is active:
        output.write(f"[yellow]{chosen['name']} is already in battle![/yellow]")
        output.write("")
        show_battle_options_callback(output)
        pending_command_callback("battle")
        return

    if chosen["hp"] <= 0:
        output.write(f"[red]❌ {chosen['name']} has fainted and can't battle![/red]")
        show_pokemon_switch_menu_callback(output)
        return

    # Perform switch
    battle.player_pokemon = chosen
    output.write("")
    output.write(f"[bold cyan]{active['name']}, come back![/bold cyan]")
    output.write(f"[bold green]Go, {chosen['name']}![/bold green]")
    output.write("")

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

    output.write("")

    # Different messages for trainer vs wild
    if battle.is_trainer_battle:
        trainer = battle.trainer_data
        output.write(f"[bold green]{trainer['name']}'s {wild['name']} fainted![/bold green]")
    else:
        output.write(f"[bold green]Wild {wild['name']} fainted![/bold green]")

    # Record KO in stats
    _stats.record_ko_dealt(game_state, player["name"])
    if not battle.is_trainer_battle:
        _stats.record_wild_battle_won(game_state)

    output.write("")

    # Award experience
    exp = battle.calculate_exp_yield()
    player["experience"] = player.get("experience", 0) + exp
    output.write(f"[cyan]{player['name']} gained {exp} Exp. Points![/cyan]")

    # Check for level up (can trigger multiple times)
    while True:
        leveled_up, new_level = battle.check_level_up(player)
        if leveled_up:
            output.write("")
            output.write(
                f"[bold yellow]★ {player['name']} grew to Level {new_level}! ★[/bold yellow]"
            )
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
                    output.write(
                        f"[bold cyan]  ✦ {player['name']} learned {move_name}![/bold cyan]"
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
                        output.write(
                            f"[bold cyan]  ✦ {player['name']} forgot {old_move} and learned {move_name}![/bold cyan]"
                        )
        else:
            break

    # Determine what comes next after this Pokemon faints
    from .. import evolution as _evo_module

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
            output.write("")
            next_pokemon = battle.switch_to_next_pokemon()
            trainer = battle.trainer_data
            output.write(
                f"[yellow]{trainer['name']} sent out {next_pokemon['name']}! (Lv. {next_pokemon['level']})[/yellow]"
            )
            output.write("")
            show_battle_options_callback(output)
            pending_command_callback("battle")
        else:
            # Trainer defeated!
            handle_trainer_defeated_callback(output)
    else:
        # Wild battle - end battle
        output.write("")
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

    output.write("")
    output.write("[bold green]═══════════════════════════════════════════[/bold green]")
    output.write(
        f"[bold green]🏆 You defeated {trainer['trainer_class']} {trainer['name']}! 🏆[/bold green]"
    )
    output.write("[bold green]═══════════════════════════════════════════[/bold green]")
    output.write("")

    # Show trainer defeat text
    for line in trainer.get("defeat_text", []):
        formatted_line = line.replace("{player_name}", player_name)
        output.write(formatted_line)

    output.write("")

    # Award prize money
    prize = battle.prize_money
    game_state.game_data["money"] = game_state.game_data.get("money", 0) + prize
    output.write(f"[bold yellow]💰 You received ₽{prize} as prize money![/bold yellow]")
    output.write("")

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
        from ..gym_system import handle_gym_victory

        handle_gym_victory(game_state, trainer["id"], output)
    else:
        output.write("[bold]You won the battle![/bold]")
        output.write("")

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

    output.write("")
    output.write(f"[bold red]{player['name']} fainted![/bold red]")
    output.write("")

    # Record faint in stats
    _stats.record_faint(game_state, player["name"])

    # Check for other usable Pokemon (Sprint 2: simplified - just whiteout)
    other_ready = [
        p
        for p in game_state.game_data.get("pokemon", [])
        if not isinstance(p, str) and p is not player and p.get("hp", 0) > 0
    ]

    if other_ready:
        # Heal the fainted Pokemon so it's ready after this battle
        player["hp"] = player["max_hp"]
        for m in player.get("moves", []):
            m["pp"] = m.get("max_pp", m["pp"])
        output.write("[yellow]Your other Pokemon are still standing![/yellow]")
        if show_faint_options_callback:
            output.write("[dim]Choose your next Pokemon...[/dim]")
            output.write("")
            is_trainer = bool(battle and battle.is_trainer_battle)
            show_faint_options_callback(not is_trainer)
        else:
            # Legacy / test fallback
            output.write(
                "[cyan]Nurse Joy healed your fainted Pokemon at the Pokemon Center.[/cyan]"
            )
            output.write("")
            end_battle_callback(output)
    else:
        output.write("[bold red]You have no more Pokemon that can battle![/bold red]")
        output.write("[dim]You black out...[/dim]")

        # Determine respawn location
        last_pokemon_center = game_state.game_data.get("last_pokemon_center")
        if last_pokemon_center:
            respawn_location = last_pokemon_center
            output.write(f"[cyan]You wake up at the {respawn_location} Pokemon Center.[/cyan]")
        else:
            # Never visited a Pokemon Center, return home
            respawn_location = "Pallet Town"
            output.write("[cyan]You wake up at home.[/cyan]")
            output.write("[cyan]Mom took care of you and your Pokemon![/cyan]")

        # Transport player to respawn location
        game_state.game_data["location"] = respawn_location
        game_state.current_location = get_location(respawn_location)

        output.write(
            "[cyan]Nurse Joy has healed all your Pokemon![/cyan]"
            if last_pokemon_center
            else "[cyan]All your Pokemon have been healed![/cyan]"
        )

        # Heal everyone
        for p in game_state.game_data.get("pokemon", []):
            if not isinstance(p, str):
                p["hp"] = p.get("max_hp", p["hp"])
                for m in p.get("moves", []):
                    m["pp"] = m.get("max_pp", m["pp"])

        output.write("")
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
        output.write("")
        output.write(f"[red]❌ You have no {item_name}s![/red]")
        output.write("")
        show_battle_options_callback(output)
        pending_command_callback("battle")
        return

    actual_heal = min(heal_amount, player["max_hp"] - player["hp"])
    player["hp"] += actual_heal
    items[item_name] -= 1
    if items[item_name] <= 0:
        del items[item_name]

    output.write("")
    output.write(f"[green]💊 {player['name']} recovered {actual_heal} HP![/green]")
    output.write("")

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
        output.write("")
        output.write(f"[red]❌ You have no {item_name}s![/red]")
        output.write("")
        show_battle_options_callback(output)
        pending_command_callback("battle")
        return

    if player.get("status") != cures_status:
        output.write("")
        output.write(f"[yellow]⚠ {player['name']} doesn't have that condition![/yellow]")
        output.write("")
        show_battle_options_callback(output)
        pending_command_callback("battle")
        return

    player["status"] = None
    player["sleep_count"] = 0
    items[item_name] -= 1
    if items[item_name] <= 0:
        del items[item_name]

    output.write("")
    output.write(f"[green]✓ {player['name']} was {cure_msg}![/green]")
    output.write("")

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
