"""
Cheat/Dev mode commands for Pokemon Terminal.

This module provides developer commands for testing and debugging.
Activated by secret phrase for development purposes.
"""

from typing import TYPE_CHECKING

from textual.widgets import RichLog

from .texts.en import cheat_commands as T
from .ui.formatters import write_lines, write_lines_fmt
from . import evolution as _evo
from . import exploration
from .battle import battle_ui
from .buildings import SHOP_CATALOG
from .data.move_data import MOVES
from .data.pokemon_data import POKEMON
from .data.trainer_data import TRAINERS
from .engine import BattleState
from .hm_tm_system import teach_move
from .locations import LOCATIONS, get_location

if TYPE_CHECKING:
    from .game_state import GameState


SECRET_PHRASE_ENABLE = "i am professor oak"  # Secret phrase to enable cheat mode
SECRET_PHRASE_DISABLE = "i am not professor oak"  # Secret phrase to disable cheat mode


def check_secret_phrase(command: str, game_state: "GameState", output: RichLog) -> bool:
    """
    Check if user entered the secret phrase to enable or disable cheat mode.

    Args:
        command: User's command
        game_state: The game state
        output: The RichLog widget to write to

    Returns:
        True if cheat mode was toggled, False otherwise
    """
    cmd_lower = command.lower().strip()

    # Check for enable phrase
    if cmd_lower == SECRET_PHRASE_ENABLE:
        if not game_state.cheat_mode:
            game_state.cheat_mode = True
            write_lines(output, T.CHEAT_ACTIVATED)
        else:
            write_lines(output, T.CHEAT_ALREADY_ENABLED)
        return True

    # Check for disable phrase
    elif cmd_lower == SECRET_PHRASE_DISABLE:
        if game_state.cheat_mode:
            game_state.cheat_mode = False
            write_lines(output, T.CHEAT_DEACTIVATED)
        else:
            write_lines(output, T.CHEAT_ALREADY_DISABLED)
        return True

    return False


def process_cheat_command(
    command: str,
    game_state: "GameState",
    output: RichLog,
    trigger_wild_battle,
    trigger_trainer_battle,
    set_pending_command_callback,
    show_battle_buttons_callback=None,
    handle_battle_victory_callback=None,
    handle_pokemon_fainted_callback=None,
    queue_move_learn_callback=None,
) -> bool:
    """
    Process cheat commands.

    Args:
        command: The cheat command
        game_state: The game state
        output: The RichLog widget to write to
        trigger_wild_battle: Callback to trigger wild battle (not used for cheat battles)
        trigger_trainer_battle: Callback to trigger trainer battle
        set_pending_command_callback: Callback to set pending command
        show_battle_buttons_callback: Optional callback to show battle action buttons
        handle_battle_victory_callback: Optional callback to handle battle victory
        handle_pokemon_fainted_callback: Optional callback to handle player Pokemon fainting
        queue_move_learn_callback: Optional callback for the interactive move-replacement
            flow when a Pokemon's moveset is already full.

    Returns:
        True if command was processed, False otherwise
    """
    if not game_state.cheat_mode:
        return False

    cmd = command.lower().strip()

    if not cmd.startswith("cheat "):
        return False

    # Remove "cheat " prefix
    cheat_cmd = cmd[6:].strip()
    parts = cheat_cmd.split()

    if not parts:
        show_cheat_help(output)
        return True

    action = parts[0]

    # List commands
    if action == "list":
        if len(parts) < 2:
            output.write("[red]❌ Usage: cheat list <pokemon|trainers|locations>[/red]")
            return True

        list_type = parts[1]
        if list_type == "pokemon":
            list_pokemon(output)
        elif list_type == "trainers":
            list_trainers(output)
        elif list_type == "locations":
            list_locations(game_state, output)
        else:
            output.write(f"[red]❌ Unknown list type: {list_type}[/red]")
        return True

    # Battle wild Pokemon
    elif action == "battle":
        if len(parts) < 2:
            output.write("[red]❌ Usage: cheat battle <pokemon> <level>[/red]")
            return True

        pokemon_name = (
            " ".join(parts[1:-1]) if len(parts) > 2 and parts[-1].isdigit() else " ".join(parts[1:])
        )
        level = int(parts[-1]) if len(parts) > 2 and parts[-1].isdigit() else 5

        # Trigger custom wild battle
        trigger_cheat_battle(
            game_state,
            output,
            pokemon_name,
            level,
            set_pending_command_callback,
            show_battle_buttons_callback,
        )
        return True

    # Battle trainer
    elif action == "trainer":
        if len(parts) < 2:
            output.write("[red]❌ Usage: cheat trainer <trainer_id>[/red]")
            return True

        trainer_id = parts[1]
        # Trigger trainer battle
        trigger_cheat_trainer_battle(
            game_state, output, trainer_id, trigger_trainer_battle, set_pending_command_callback
        )
        return True

    # Warp to location
    elif action == "warp":
        if len(parts) < 2:
            output.write("[red]❌ Usage: cheat warp <location>[/red]")
            return True

        # Reconstruct location name (might have spaces)
        location_name = " ".join(parts[1:])
        warp_to_location(game_state, location_name, output)
        return True

    # Give items
    elif action == "give":
        if len(parts) < 2:
            output.write("[red]❌ Usage: cheat give <item> <quantity>[/red]")
            return True

        item_name = " ".join(parts[1:-1]) if len(parts) > 2 else parts[1]
        quantity = int(parts[-1]) if len(parts) > 2 and parts[-1].isdigit() else 1

        give_item(game_state, item_name, quantity, output)
        return True

    # Add money
    elif action == "money":
        if len(parts) < 2:
            output.write("[red]❌ Usage: cheat money <amount>[/red]")
            return True

        amount = int(parts[1])
        add_money(game_state, amount, output)
        return True

    # Add Pokemon to party
    elif action == "add":
        if len(parts) < 2:
            output.write("[red]❌ Usage: cheat add <pokemon> <level>[/red]")
            return True

        pokemon_name = (
            " ".join(parts[1:-1]) if len(parts) > 2 and parts[-1].isdigit() else " ".join(parts[1:])
        )
        level = int(parts[-1]) if len(parts) > 2 and parts[-1].isdigit() else 5

        add_pokemon_to_party(game_state, pokemon_name, level, output)
        return True

    # Remove Pokemon from party
    elif action == "remove":
        if len(parts) < 2:
            output.write("[red]❌ Usage: cheat remove <pokemon/slot>[/red]")
            return True

        identifier = " ".join(parts[1:])
        remove_pokemon_from_party(game_state, identifier, output)
        return True

    # Level up Pokemon
    elif action == "level":
        if len(parts) < 3:
            output.write("[red]❌ Usage: cheat level <pokemon/slot> <level>[/red]")
            return True

        identifier = " ".join(parts[1:-1]) if len(parts) > 2 else parts[1]
        try:
            new_level = int(parts[-1])
            level_up_pokemon(game_state, identifier, new_level, output)
        except ValueError:
            output.write("[red]❌ Level must be a number[/red]")
        return True

    # Evolve Pokemon
    elif action == "evolve":
        if len(parts) < 2:
            output.write("[red]❌ Usage: cheat evolve <pokemon/slot>[/red]")
            return True

        identifier = " ".join(parts[1:])
        evolve_pokemon(game_state, identifier, output)
        return True

    # Instantly win the current battle
    elif action == "win":
        if not game_state.in_battle or not game_state.battle_state:
            output.write("[red]❌ Not in a battle! Use 'cheat win' during a battle.[/red]")
            return True
        battle = game_state.battle_state
        enemy = battle.wild_pokemon
        enemy["hp"] = 0
        output.write(
            f"[bold yellow]🎮 [CHEAT MODE] {enemy['name']} instantly fainted![/bold yellow]"
        )
        if handle_battle_victory_callback:
            handle_battle_victory_callback(output)
        return True

    # Instantly lose the current battle
    elif action == "lose":
        if not game_state.in_battle or not game_state.battle_state:
            output.write("[red]❌ Not in a battle! Use 'cheat lose' during a battle.[/red]")
            return True
        battle = game_state.battle_state
        player = battle.player_pokemon
        player["hp"] = 0
        output.write(
            f"[bold yellow]🎮 [CHEAT MODE] {player['name']} instantly fainted![/bold yellow]"
        )
        if handle_pokemon_fainted_callback:
            handle_pokemon_fainted_callback(output)
        return True

    # Faint a party Pokemon
    elif action == "faint":
        if len(parts) < 2:
            output.write("[red]❌ Usage: cheat faint <pokemon/slot>[/red]")
            return True

        identifier = " ".join(parts[1:])
        faint_pokemon(game_state, identifier, output)
        return True

    # Teach a move to a party Pokemon
    elif action == "learn":
        if len(parts) < 3:
            output.write("[red]❌ Usage: cheat learn <pokemon/slot> <move>[/red]")
            return True

        # Move is the last token; identifier is everything in between
        identifier = " ".join(parts[1:-1])
        move_name = parts[-1]
        teach_move_cheat(game_state, identifier, move_name, output, queue_move_learn_callback)
        return True

    else:
        output.write(f"[red]❌ Unknown cheat command: {action}[/red]")
        show_cheat_help(output)
        return True


def show_cheat_help(output: RichLog) -> None:
    """Show cheat mode help."""
    write_lines(output, T.CHEAT_HELP)


def list_pokemon(output: RichLog) -> None:
    """List all available Pokemon."""
    write_lines(output, T.LIST_POKEMON_HEADER)

    # Show first 50 Pokemon (Gen 1)
    pokemon_list = []
    for num in sorted(POKEMON.keys())[:50]:
        data = POKEMON[num]
        pokemon_list.append(f"{num:3d}. {data['name']}")

    # Display in columns
    for i in range(0, len(pokemon_list), 3):
        row = pokemon_list[i : i + 3]
        output.write("  " + "  ".join(f"[cyan]{p}[/cyan]" for p in row))

    write_lines(output, T.LIST_POKEMON_FOOTER)


def list_trainers(output: RichLog) -> None:
    """List all available trainers."""
    write_lines(output, T.LIST_TRAINERS_HEADER)

    for trainer_id, trainer in TRAINERS.items():
        name = trainer.get("name", "Unknown")
        trainer_class = trainer.get("trainer_class", "Trainer")
        location = trainer.get("location", "Unknown")
        pokemon_count = len(trainer.get("pokemon", []))

        output.write(f"  [green]{trainer_id}[/green]")
        output.write(f"    {trainer_class} {name} - {location}")
        output.write(f"    {pokemon_count} Pokemon")
        output.write("")

    write_lines(output, T.LIST_TRAINERS_FOOTER)


def list_locations(game_state: "GameState", output: RichLog) -> None:
    """List all available locations."""
    write_lines(output, T.LIST_LOCATIONS_HEADER)

    for location_name in sorted(LOCATIONS.keys()):
        location = LOCATIONS[location_name]
        loc_type = location.type if hasattr(location, "type") else "unknown"

        marker = "🏙️" if loc_type == "town" else "🛤️"
        output.write(f"  {marker} [cyan]{location_name}[/cyan] ({loc_type})")

    write_lines(output, T.LIST_LOCATIONS_FOOTER)


def warp_to_location(game_state: "GameState", location_name: str, output: RichLog) -> None:
    """Warp to any location."""
    # Try to find matching location
    matching_location = None
    for loc_name in LOCATIONS.keys():
        if loc_name.lower() == location_name.lower() or location_name.lower() in loc_name.lower():
            matching_location = loc_name
            break

    if not matching_location:
        write_lines_fmt(output, T.WARP_NOT_FOUND, location=location_name)
        return

    # Warp to location
    location = get_location(matching_location)
    if location:
        game_state.current_location = location
        game_state.game_data["location"] = matching_location
        write_lines_fmt(output, T.WARP_SUCCESS, location=matching_location)

        # Show location arrival
        exploration.show_location_arrival(game_state, output)


def give_item(game_state: "GameState", item_name: str, quantity: int, output: RichLog) -> None:
    """Give items to player."""
    # Find matching item
    matching_item = None
    for shop_item in SHOP_CATALOG.keys():
        if shop_item.lower() == item_name.lower() or item_name.lower() in shop_item.lower():
            matching_item = shop_item
            break

    if not matching_item:
        # Add custom item name anyway
        matching_item = item_name.title()

    items = game_state.game_data.setdefault("items", {})
    items[matching_item] = items.get(matching_item, 0) + quantity

    output.write("")
    output.write(f"[bold green]✓ Received {quantity}x {matching_item}![/bold green]")
    output.write("")


def add_money(game_state: "GameState", amount: int, output: RichLog) -> None:
    """Add money to player."""
    current = game_state.game_data.get("money", 0)
    game_state.game_data["money"] = current + amount

    output.write("")
    output.write(f"[bold green]✓ Received ₽{amount}![/bold green]")
    output.write(f"  [dim]Total money: ₽{game_state.game_data['money']}[/dim]")
    output.write("")


def trigger_cheat_battle(
    game_state: "GameState",
    output: RichLog,
    pokemon_name: str,
    level: int,
    pending_command_callback,
    show_battle_buttons_callback=None,
) -> None:
    """
    Trigger a cheat battle with a specific Pokemon at a specific level.

    Args:
        game_state: The game state
        output: The RichLog widget to write to
        pokemon_name: Name of the Pokemon to battle
        level: Level of the Pokemon
        pending_command_callback: Callback to set pending command
        show_battle_buttons_callback: Optional callback to show battle action buttons
    """
    # Find matching Pokemon
    matching_pokemon = None
    for num, data in POKEMON.items():
        if (
            data["name"].lower() == pokemon_name.lower()
            or pokemon_name.lower() in data["name"].lower()
        ):
            matching_pokemon = data["name"]
            break

    if not matching_pokemon:
        output.write("")
        output.write(f"[red]❌ Pokemon not found: {pokemon_name}[/red]")
        output.write("[dim]Use 'cheat list pokemon' to see all Pokemon[/dim]")
        output.write("")
        return

    # Get player's first non-fainted Pokemon
    player_pokemon = game_state.get_active_pokemon()

    if not player_pokemon:
        output.write("")
        output.write(
            "[red]❌ All your Pokemon have fainted! You need at least one Pokemon to battle.[/red]"
        )
        output.write("")
        return

    # Create and start battle
    bs = BattleState()
    bs.start_wild_battle(player_pokemon, matching_pokemon, level)
    game_state.battle_state = bs
    game_state.in_battle = True

    # Show battle start
    write_lines(output, T.CHEAT_BATTLE_SPAWN)
    battle_ui.show_battle_start(game_state, output)
    battle_ui.show_battle_options(game_state, output)
    pending_command_callback("battle")
    if show_battle_buttons_callback:
        show_battle_buttons_callback()


def trigger_cheat_trainer_battle(
    game_state: "GameState",
    output: RichLog,
    trainer_id: str,
    trigger_trainer_battle_callback,
    pending_command_callback,
) -> None:
    """
    Trigger a cheat trainer battle.

    Args:
        game_state: The game state
        output: The RichLog widget to write to
        trainer_id: ID of the trainer to battle
        trigger_trainer_battle_callback: Callback to trigger trainer battle
        pending_command_callback: Callback to set pending command
    """
    # Find matching trainer
    if trainer_id not in TRAINERS:
        output.write("")
        output.write(f"[red]❌ Trainer not found: {trainer_id}[/red]")
        output.write("[dim]Use 'cheat list trainers' to see all trainers[/dim]")
        output.write("")
        return

    trainer = TRAINERS[trainer_id]

    write_lines(output, T.CHEAT_TRAINER_BATTLE_SPAWN)

    # Trigger the trainer battle
    trigger_trainer_battle_callback(output, trainer)


# ═══════════════════════════════════════════════════════════════════════════
# Party Management Functions
# ═══════════════════════════════════════════════════════════════════════════


def add_pokemon_to_party(
    game_state: "GameState", pokemon_name: str, level: int, output: RichLog
) -> None:
    """
    Add a Pokemon to the party.

    Args:
        game_state: The game state
        pokemon_name: Name of the Pokemon to add
        level: Level of the Pokemon
        output: The RichLog widget to write to
    """
    # Check party size
    pokemon_list = game_state.game_data.get("pokemon", [])
    if len(pokemon_list) >= 6:
        output.write("")
        output.write("[red]❌ Party is full! Remove a Pokemon first.[/red]")
        output.write("")
        return

    # Find matching Pokemon
    matching_pokemon = None
    pokemon_number = None
    for num, data in POKEMON.items():
        if (
            data["name"].lower() == pokemon_name.lower()
            or pokemon_name.lower() in data["name"].lower()
        ):
            matching_pokemon = data["name"]
            pokemon_number = num
            break

    if not matching_pokemon:
        output.write("")
        output.write(f"[red]❌ Pokemon not found: {pokemon_name}[/red]")
        output.write("[dim]Use 'cheat list pokemon' to see all Pokemon[/dim]")
        output.write("")
        return

    # Create the Pokemon using battle engine
    battle_engine = BattleState()
    new_pokemon = battle_engine.generate_wild_pokemon(matching_pokemon, level)

    # Add to party
    if "pokemon" not in game_state.game_data:
        game_state.game_data["pokemon"] = []

    game_state.game_data["pokemon"].append(new_pokemon)

    output.write("")
    output.write(f"[bold green]✓ Added {matching_pokemon} (Lv.{level}) to party![/bold green]")
    output.write(f"  [dim]Party size: {len(game_state.game_data['pokemon'])}/6[/dim]")
    output.write("")


def remove_pokemon_from_party(game_state: "GameState", identifier: str, output: RichLog) -> None:
    """
    Remove a Pokemon from the party.

    Args:
        game_state: The game state
        identifier: Pokemon name or slot number
        output: The RichLog widget to write to
    """
    pokemon_list = game_state.game_data.get("pokemon", [])

    if not pokemon_list:
        output.write("")
        output.write("[red]❌ Your party is empty![/red]")
        output.write("")
        return

    pokemon, idx = game_state.find_pokemon(identifier)

    if pokemon is None:
        output.write("")
        output.write(f"[red]❌ Pokemon not found in party: {identifier}[/red]")
        output.write("[dim]Use 'party' to see your Pokemon[/dim]")
        output.write("")
        return

    # Don't allow removing the last Pokemon
    if len(pokemon_list) == 1:
        output.write("")
        output.write("[red]❌ Can't remove your last Pokemon![/red]")
        output.write("")
        return

    pokemon_name = pokemon.get("name", "Unknown")
    pokemon_level = pokemon.get("level", 0)

    # Remove from party
    game_state.game_data["pokemon"].pop(idx)

    output.write("")
    output.write(
        f"[bold yellow]Removed {pokemon_name} (Lv.{pokemon_level}) from party[/bold yellow]"
    )
    output.write(f"  [dim]Party size: {len(game_state.game_data['pokemon'])}/6[/dim]")
    output.write("")


def level_up_pokemon(
    game_state: "GameState", identifier: str, new_level: int, output: RichLog
) -> None:
    """
    Set a Pokemon's level.

    Args:
        game_state: The game state
        identifier: Pokemon name or slot number
        new_level: New level (1-100)
        output: The RichLog widget to write to
    """
    if not 1 <= new_level <= 100:
        output.write("")
        output.write("[red]❌ Level must be between 1 and 100[/red]")
        output.write("")
        return

    pokemon, idx = game_state.find_pokemon(identifier)

    if pokemon is None:
        output.write("")
        output.write(f"[red]❌ Pokemon not found in party: {identifier}[/red]")
        output.write("[dim]Use 'party' to see your Pokemon[/dim]")
        output.write("")
        return

    pokemon_name = pokemon.get("name", "Unknown")
    old_level = pokemon.get("level", 1)

    # Update level
    pokemon["level"] = new_level

    # Recalculate stats based on new level
    pokemon_number = pokemon.get("number")
    if pokemon_number and pokemon_number in POKEMON:
        pokemon_data = POKEMON[pokemon_number]
        battle_engine = BattleState()
        new_stats = battle_engine.calculate_stats(pokemon_data["stats"], new_level)

        # Update stats
        pokemon["max_hp"] = new_stats["hp"]
        pokemon["hp"] = new_stats["hp"]  # Fully heal
        pokemon["stats"] = new_stats  # Keep as StatsData so to_dict() works correctly

        # Update moves for new level
        new_moves = battle_engine.get_moves_for_level(pokemon_data, new_level)
        pokemon["moves"] = new_moves

    output.write("")
    output.write(f"[bold green]✓ {pokemon_name} leveled up![/bold green]")
    output.write(f"  Level: {old_level} → {new_level}")
    output.write(f"  [dim]HP: {pokemon['max_hp']} | Stats recalculated[/dim]")
    output.write("")


def evolve_pokemon(game_state: "GameState", identifier: str, output: RichLog) -> None:
    """
    Force evolve a Pokemon (cheat command — bypasses level requirement).

    Args:
        game_state: The game state
        identifier: Pokemon name or slot number
        output: The RichLog widget to write to
    """
    pokemon, idx = game_state.find_pokemon(identifier)

    if pokemon is None:
        output.write("")
        output.write(f"[red]❌ Pokemon not found in party: {identifier}[/red]")
        output.write("[dim]Use 'party' to see your Pokemon[/dim]")
        output.write("")
        return

    pokemon_name = pokemon.get("name", "Unknown")
    pokemon_number = pokemon.get("number")

    if not pokemon_number or pokemon_number not in POKEMON:
        output.write("")
        output.write(f"[red]❌ Can't find evolution data for {pokemon_name}[/red]")
        output.write("")
        return

    species = POKEMON[pokemon_number]
    evolution = species.get("evolution")

    if not evolution:
        output.write("")
        output.write(f"[yellow]⚠ {pokemon_name} doesn't evolve[/yellow]")
        output.write("")
        return

    evolved_form = evolution.get("into")
    if not evolved_form:
        output.write("")
        output.write(f"[red]❌ Evolution data error for {pokemon_name}[/red]")
        output.write("")
        return

    success = _evo.force_evolve(game_state, pokemon, evolved_form, output)
    if not success:
        output.write("")
        output.write(f"[red]❌ Evolved form not found in data: {evolved_form}[/red]")
        output.write("")


def faint_pokemon(game_state: "GameState", identifier: str, output: RichLog) -> None:
    """
    Force a party Pokemon to faint (HP → 0).

    Args:
        game_state: The game state
        identifier: Pokemon name or slot number
        output: The RichLog widget to write to
    """
    pokemon, idx = game_state.find_pokemon(identifier)

    if pokemon is None:
        output.write("")
        output.write(f"[red]❌ Pokemon not found: {identifier}[/red]")
        output.write("[dim]Use 'party' to see your Pokemon[/dim]")
        output.write("")
        return

    if pokemon.get("hp", 0) <= 0:
        output.write("")
        output.write(f"[yellow]⚠ {pokemon['name']} is already fainted![/yellow]")
        output.write("")
        return

    # Don't allow fainting the last healthy Pokemon
    pokemon_list = game_state.game_data.get("pokemon", [])
    healthy = [p for p in pokemon_list if p.get("hp", 0) > 0]
    if len(healthy) <= 1:
        output.write("")
        output.write("[red]❌ Can't faint your last healthy Pokemon![/red]")
        output.write("")
        return

    pokemon["hp"] = 0

    output.write("")
    output.write(f"[bold yellow]🎮 [CHEAT MODE] {pokemon['name']} fainted![/bold yellow]")
    output.write("")


def teach_move_cheat(
    game_state: "GameState", identifier: str, move_name: str, output: RichLog,
    queue_move_learn_callback=None,
) -> None:
    """
    Teach any move to a party Pokemon, bypassing TM/HM item requirements.

    Args:
        game_state: The game state
        identifier: Pokemon name or slot number
        move_name: Name of the move to teach
        output: The RichLog widget to write to
        queue_move_learn_callback: Optional callback for the interactive
            move-replacement flow when the Pokemon already knows 4 moves.
    """
    pokemon, idx = game_state.find_pokemon(identifier)

    if pokemon is None:
        output.write("")
        output.write(f"[red]❌ Pokemon not found: {identifier}[/red]")
        output.write("[dim]Use 'party' to see your Pokemon[/dim]")
        output.write("")
        return

    # Find matching move (case-insensitive, partial match allowed)
    move_upper = move_name.upper()
    matching_move = None
    for key in MOVES:
        if key == move_upper:
            matching_move = key
            break
    if not matching_move:
        for key in MOVES:
            if move_upper in key:
                matching_move = key
                break

    if not matching_move:
        output.write("")
        output.write(f"[red]❌ Move not found: {move_name}[/red]")
        output.write("[dim]Check the move name and try again[/dim]")
        output.write("")
        return

    output.write(f"[bold yellow]🎮 [CHEAT MODE] Teaching {matching_move}...[/bold yellow]")
    teach_move(game_state, matching_move, pokemon, f"TM {matching_move}", False, output, queue_move_learn_callback)
