"""
Building handlers for Pokemon Terminal.

This module contains all the logic for entering and interacting with buildings
like Pokemon Centers, Pokemarts, Gyms, and story buildings.
"""

import copy
from typing import TYPE_CHECKING, Callable, Optional

from textual.widgets import RichLog

from . import gym_system, pokedex
from .battle import battle_actions
from .data.trainer_data import TRAINERS
from .engine import BattleState
from .texts.en import buildings as T  # noqa: N812
from .ui.formatters import write_lines, write_lines_fmt

if TYPE_CHECKING:
    from .game_state import GameState


# Pokemart item catalog — grouped by availability tier
# Basic tier: all Pokemarts carry these
SHOP_CATALOG_BASIC = {
    "Pokeball": {"price": 200, "description": "Catch wild Pokemon", "emoji": "🔴"},
    "Potion": {"price": 300, "description": "Restores 20 HP", "emoji": "💊"},
    "Super Potion": {"price": 700, "description": "Restores 50 HP", "emoji": "💊"},
    "Antidote": {"price": 100, "description": "Cures poison", "emoji": "🧪"},
    "Paralyze Heal": {"price": 200, "description": "Cures paralysis", "emoji": "⚡"},
    "Awakening": {"price": 250, "description": "Wakes a sleeping Pokemon", "emoji": "☀️"},
    "Repel": {"price": 350, "description": "Reduces wild encounters (10 exp)", "emoji": "🪢"},
    "Escape Rope": {"price": 550, "description": "Escape from routes/forests", "emoji": "🪢"},
}

# Advanced tier: Pewter City and beyond
SHOP_CATALOG_ADVANCED = {
    **SHOP_CATALOG_BASIC,
    "Great Ball": {"price": 600, "description": "Better catch rate", "emoji": "🔵"},
    "Hyper Potion": {"price": 1200, "description": "Restores 200 HP", "emoji": "💊"},
    "Revive": {"price": 1500, "description": "Revives a fainted Pokemon to 50% HP", "emoji": "💫"},
    "Super Repel": {"price": 500, "description": "Reduces wild encounters (20 exp)", "emoji": "🪢"},
    "Burn Heal": {"price": 250, "description": "Cures burn", "emoji": "🧊"},
    "Ice Heal": {"price": 250, "description": "Cures freeze", "emoji": "🔥"},
    "Full Heal": {"price": 600, "description": "Cures any status condition", "emoji": "🌟"},
    "HP Up": {"price": 9800, "description": "Raises max HP by 10", "emoji": "❤️"},
    "Protein": {"price": 9800, "description": "Raises Attack by 5", "emoji": "💪"},
    "Iron": {"price": 9800, "description": "Raises Defense by 5", "emoji": "🛡️"},
    "Calcium": {"price": 9800, "description": "Raises Special by 5", "emoji": "🔹"},
    "Carbos": {"price": 9800, "description": "Raises Speed by 5", "emoji": "⚡"},
    "Rare Candy": {"price": 4800, "description": "Raises a Pokemon's level by 1", "emoji": "🍬"},
    "Fire Stone": {"price": 3000, "description": "Evolves certain Pokemon", "emoji": "🔥"},
    "Water Stone": {"price": 3000, "description": "Evolves certain Pokemon", "emoji": "💧"},
    "Thunder Stone": {"price": 3000, "description": "Evolves certain Pokemon", "emoji": "⚡"},
    "Leaf Stone": {"price": 3000, "description": "Evolves certain Pokemon", "emoji": "🍃"},
    "Moon Stone": {"price": 3000, "description": "Evolves certain Pokemon", "emoji": "🌙"},
    "Ultra Ball": {"price": 1200, "description": "High catch rate", "emoji": "⚫"},
    "Max Potion": {"price": 2500, "description": "Fully restores HP", "emoji": "💊"},
    "Max Revive": {
        "price": 4000,
        "description": "Revives a fainted Pokemon to full HP",
        "emoji": "💫",
    },
    "Full Restore": {
        "price": 3000,
        "description": "Fully restores HP and cures status",
        "emoji": "✨",
    },
}

# Default catalogue used throughout the current game world
SHOP_CATALOG = SHOP_CATALOG_BASIC

# Sell prices for special items not in any catalog
# Catalog items sell for 50% of their listed price (computed at runtime)
SELL_PRICES: dict[str, int] = {
    "Nugget": 5000,
    "Dome Fossil": 3500,
    "Helix Fossil": 3500,
    "Old Amber": 3500,
}


def _set_active_building(game_state: "GameState", building_name: str) -> None:
    """Store the current building context for the top UI banner."""
    game_state.game_data["_active_building"] = building_name


def _clear_active_building(game_state: "GameState") -> None:
    """Clear current building context for the top UI banner."""
    game_state.game_data.pop("_active_building", None)


def enter_building(
    game_state: "GameState",
    building_name: str,
    output: RichLog,
    set_pending_command_callback,
    show_starter_panel_callback=None,
    trigger_trainer_battle_callback=None,
    show_pokemart_panel_callback=None,
    show_gym_panel_callback=None,
) -> None:
    """
    Enter a building at the current location.

    Args:
        game_state: The game state object
        building_name: Name of the building to enter
        output: The RichLog widget to write to
        set_pending_command_callback: Callback to set pending command
        show_starter_panel_callback: Optional callback to show starter selection panel
        trigger_trainer_battle_callback: Optional callback to trigger trainer battle (for gyms)
        show_pokemart_panel_callback: Optional callback to show the Pokemart button panel
        show_gym_panel_callback: Optional callback to show the gym lobby action panel
    """
    if not game_state.current_location:
        output.write("[red]❌ Error: No current location set[/red]")
        return

    current = game_state.current_location

    # Check if this is a town/city
    if current.type != "town":
        write_lines(output, T.NOT_A_TOWN)
        return

    # Find matching building (case-insensitive partial match)
    building_lower = building_name.lower()
    matching_building = None

    for building in current.buildings:
        if building.lower() == building_lower or building_lower in building.lower():
            matching_building = building
            break

    if not matching_building:
        # Check blocked buildings
        for building, reason in current.blocked_buildings.items():
            if building.lower() == building_lower or building_lower in building.lower():
                # Allow entry in cheat mode
                if game_state.cheat_mode:
                    matching_building = building
                    write_lines(output, T.CHEAT_BYPASS_BUILDING_LOCK)
                    break
                else:
                    write_lines_fmt(output, T.BUILDING_BLOCKED_REASON, reason=reason)
                    return

        # If still not found, show error
        if not matching_building:
            write_lines_fmt(output, T.BUILDING_NOT_HERE, building_name=building_name)
            return

    # Route to appropriate building handler
    player_name = game_state.game_data.get("player_name", "Trainer")
    rival_name = game_state.game_data.get("rival_name", "Rival")
    _set_active_building(game_state, matching_building)

    if "pokemon center" in matching_building.lower():
        enter_pokemon_center(game_state, output, set_pending_command_callback)
    elif "pokemart" in matching_building.lower() or "mart" in matching_building.lower():
        enter_pokemart(
            game_state, output, set_pending_command_callback, show_pokemart_panel_callback
        )
    elif "gym" in matching_building.lower():
        if show_gym_panel_callback:
            gym_system.enter_gym_lobby(game_state, output, show_gym_panel_callback)
        elif trigger_trainer_battle_callback:
            gym_system.enter_gym(game_state, output, trigger_trainer_battle_callback)
        else:
            write_lines(output, T.GYM_NOT_AVAILABLE_CONTEXT)
    elif ("player" in matching_building.lower() and "house" in matching_building.lower()) or (
        player_name.lower() in matching_building.lower() and "house" in matching_building.lower()
    ):
        enter_players_house(game_state, output, set_pending_command_callback)
    elif ("rival" in matching_building.lower() and "house" in matching_building.lower()) or (
        rival_name.lower() in matching_building.lower() and "house" in matching_building.lower()
    ):
        enter_rivals_house(game_state, output)
    elif "oak" in matching_building.lower() and "lab" in matching_building.lower():
        enter_oaks_lab(
            game_state, output, set_pending_command_callback, show_starter_panel_callback
        )
    elif "museum" in matching_building.lower():
        enter_museum(game_state, output, set_pending_command_callback)
    elif "bill" in matching_building.lower():
        enter_bills_house(game_state, output)
    elif "bike" in matching_building.lower():
        enter_bike_shop(game_state, output)
    elif "nugget" in matching_building.lower() or "bridge" in matching_building.lower():
        enter_nugget_bridge(
            game_state, output, set_pending_command_callback, trigger_trainer_battle_callback
        )
    elif "ss anne" in matching_building.lower() or "s.s. anne" in matching_building.lower():
        enter_ss_anne(game_state, output)
    elif "pokemon tower" in matching_building.lower():
        enter_pokemon_tower(game_state, output)
    elif "dock" in matching_building.lower():
        enter_ss_anne_dock(game_state, output)
    elif "mr. fuji" in matching_building.lower() or "fuji" in matching_building.lower():
        enter_mr_fujis_house(game_state, output)
    elif "game corner" in matching_building.lower():
        enter_game_corner(game_state, output)
    elif "department store" in matching_building.lower():
        enter_department_store(game_state, output)
    elif "safari zone" in matching_building.lower() or "safari" in matching_building.lower():
        enter_safari_zone(game_state, output)
    else:
        write_lines_fmt(output, T.BUILDING_NOT_IMPLEMENTED, building_name=matching_building)


def enter_pokemon_center(
    game_state: "GameState", output: RichLog, set_pending_command_callback
) -> None:
    """
    Enter the Pokemon Center and offer healing.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
        set_pending_command_callback: Callback to set pending command
    """
    write_lines(output, T.POKEMON_CENTER_HEADER)

    # Check if player has Pokemon
    pokemon = game_state.game_data.get("pokemon", [])

    if not pokemon:
        write_lines(output, T.POKEMON_CENTER_NO_POKEMON_LEAVE)
        _clear_active_building(game_state)
        return

    # Show Pokemon Center lobby menu
    write_lines(output, T.POKEMON_CENTER_LOBBY_PROMPT)

    set_pending_command_callback("pokemon_center")


def enter_pokemart(
    game_state: "GameState",
    output: RichLog,
    set_pending_command_callback,
    show_pokemart_panel_callback=None,
) -> None:
    """
    Enter the Pokemart and allow purchasing items.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
        set_pending_command_callback: Callback to set pending command
        show_pokemart_panel_callback: Optional callback to show the Pokemart button panel
    """
    write_lines(output, T.POKEMART_HEADER)
    # Determine catalog tier based on current location
    current_name = game_state.current_location.name if game_state.current_location else ""
    advanced_cities = {
        "Pewter City",
        "Cerulean City",
        "Vermillion City",
        "Lavender Town",
        "Celadon City",
        "Fuchsia City",
        "Saffron City",
        "Cinnabar Island",
        "Viridian City",
    }
    game_state.game_data["_current_shop_catalog"] = (
        "advanced" if current_name in advanced_cities else "basic"
    )
    show_shop_menu(game_state, output)
    if show_pokemart_panel_callback:
        show_pokemart_panel_callback()
    set_pending_command_callback("shop")


def show_shop_menu(game_state: "GameState", output: RichLog) -> None:
    """Display the Pokemart shop catalog."""
    catalog_key = game_state.game_data.get("_current_shop_catalog", "basic")
    catalog = SHOP_CATALOG_ADVANCED if catalog_key == "advanced" else SHOP_CATALOG_BASIC
    money = game_state.game_data.get("money", 0)
    output.write(f"   [bold]Your money:[/bold] [cyan]₽{money}[/cyan]")
    output.write("")
    output.write("[bold green]Available items:[/bold green]")
    for name, info in catalog.items():
        output.write(
            f"   {info['emoji']} [green]{name}[/green] - ₽{info['price']}  [dim]{info['description']}[/dim]"
        )
    output.write("")
    write_lines(output, T.SHOP_COMMANDS_HINT)


def process_shop_command(
    game_state: "GameState", command: str, output: RichLog, set_pending_command_callback
) -> None:
    """
    Process a Pokemart shop command.

    Args:
        game_state: The game state object
        command: Player input
        output: The RichLog widget to write to
        set_pending_command_callback: Callback to set pending command
    """
    cmd = command.lower().strip()
    catalog_key = game_state.game_data.get("_current_shop_catalog", "basic")
    catalog = SHOP_CATALOG_ADVANCED if catalog_key == "advanced" else SHOP_CATALOG_BASIC

    if cmd in (
        "leave",
        "exit",
        "exit building",
        "leave building",
        "done",
        "goodbye",
        "bye",
        "no",
        "back",
    ):
        write_lines(output, T.SHOP_LEAVE_THANK_YOU)
        _clear_active_building(game_state)
        return  # Don't set pending_command — exits the shop

    if cmd.startswith("sell "):
        sale_input = cmd[5:].strip()
        sale_qty = 1

        # Detect optional quantity prefix: "sell 3 potion"
        sale_parts = sale_input.split(None, 1)
        if len(sale_parts) == 2 and sale_parts[0].isdigit():
            sale_qty = int(sale_parts[0])
            sale_input = sale_parts[1]

        sale_qty = max(1, sale_qty)

        # Strip trailing 's' for plurals
        if sale_input.endswith("s") and not sale_input.endswith("ss"):
            sale_input = sale_input[:-1]

        # Resolve item name: check SELL_PRICES first (case-insensitive), then catalogs
        sell_item_name: str | None = None
        sell_price: int = 0

        for special_name in SELL_PRICES:
            if special_name.lower() == sale_input or sale_input in special_name.lower():
                sell_item_name = special_name
                sell_price = SELL_PRICES[special_name]
                break

        if sell_item_name is None:
            # Check both catalogs for a 50%-price sell
            for cat in (SHOP_CATALOG_ADVANCED, SHOP_CATALOG_BASIC):
                for item_name, info in cat.items():
                    if item_name.lower() == sale_input or sale_input in item_name.lower():
                        sell_item_name = item_name
                        sell_price = info["price"] // 2
                        break
                if sell_item_name:
                    break

        if sell_item_name is None:
            write_lines(output, T.SHOP_NO_RESALE_VALUE)
            set_pending_command_callback("shop")
            return

        # Check player has the item
        items = game_state.game_data.setdefault("items", {})
        owned_qty = items.get(sell_item_name, 0)
        if owned_qty <= 0:
            write_lines_fmt(output, T.SHOP_DO_NOT_HAVE_ITEM, item_name=sell_item_name)
            set_pending_command_callback("shop")
            return

        # Clamp qty to what the player actually owns
        sale_qty = min(sale_qty, owned_qty)

        total_earned = sell_price * sale_qty
        game_state.game_data["money"] = game_state.game_data.get("money", 0) + total_earned

        new_qty = owned_qty - sale_qty
        if new_qty <= 0:
            items.pop(sell_item_name, None)
        else:
            items[sell_item_name] = new_qty

        new_balance = game_state.game_data["money"]
        write_lines_fmt(
            output,
            T.SHOP_SELL_SUCCESS,
            qty=sale_qty,
            item_name=sell_item_name,
            total_earned=total_earned,
            money=new_balance,
        )

        show_shop_menu(game_state, output)
        set_pending_command_callback("shop")
        return

    if not cmd.startswith("buy "):
        write_lines(output, T.SHOP_UNKNOWN_COMMAND)
        set_pending_command_callback("shop")
        return

    purchase = cmd[4:].strip()
    qty = 1

    # Detect optional quantity prefix: "buy 5 pokeball"
    parts = purchase.split(None, 1)
    if len(parts) == 2 and parts[0].isdigit():
        qty = int(parts[0])
        purchase = parts[1]

    qty = max(1, min(qty, 99))

    # Strip trailing 's' for plurals (pokeballs -> pokeball)
    if purchase.endswith("s") and not purchase.endswith("ss"):
        purchase = purchase[:-1]

    # Find matching catalog item (case-insensitive)
    matched_item = None
    for item_name in catalog:
        if item_name.lower() == purchase or purchase in item_name.lower():
            matched_item = item_name
            break

    if not matched_item:
        write_lines_fmt(output, T.SHOP_ITEM_NOT_SOLD, item_name=command[4:].strip())
        set_pending_command_callback("shop")
        return

    info = catalog[matched_item]
    total_cost = info["price"] * qty
    money = game_state.game_data.get("money", 0)

    if money < total_cost:
        write_lines_fmt(output, T.SHOP_NOT_ENOUGH_MONEY, total_cost=total_cost, money=money)
        set_pending_command_callback("shop")
        return

    # Complete purchase
    game_state.game_data["money"] = money - total_cost
    items = game_state.game_data.setdefault("items", {})
    items[matched_item] = items.get(matched_item, 0) + qty

    write_lines_fmt(
        output,
        T.SHOP_BUY_SUCCESS,
        qty=qty,
        item_name=matched_item,
        total_cost=total_cost,
        money=game_state.game_data["money"],
    )

    show_shop_menu(game_state, output)
    set_pending_command_callback("shop")


# Note: enter_gym has been moved to gym_system.py


def enter_museum(game_state: "GameState", output: RichLog, set_pending_command_callback) -> None:
    """
    Enter the Pewter City Natural Science Museum.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
        set_pending_command_callback: Callback to set pending command
    """
    write_lines(output, T.MUSEUM_HEADER)
    write_lines(output, T.MUSEUM_FOSSIL_EXHIBIT)
    write_lines(output, T.MUSEUM_MOON_STONE_EXHIBIT)
    write_lines(output, T.MUSEUM_SPACE_EXHIBIT)
    story_flags = game_state.game_data.get("story_flags", {})
    if story_flags.get("received_mt_moon_fossil"):
        output.write(
            "[bold]Museum Guide:[/bold] [green]Oh! Is that the fossil you found in Mt. Moon?[/green]"
        )
        output.write(
            "[green]   Remarkable specimen! Let me introduce you to our resident scientist...[/green]"
        )
        output.write("")
        # Scientist NPC — checks which fossil the player actually has
        bag = game_state.game_data.get("bag", {})
        has_dome = bag.get("Dome Fossil", 0) > 0
        has_helix = bag.get("Helix Fossil", 0) > 0
        output.write("[bold]Scientist:[/bold] [cyan]Oh my! Is that a fossil from Mt. Moon?![/cyan]")
        output.write("")
        if has_dome and has_helix:
            output.write(
                "[cyan]   You have BOTH a Dome Fossil and a Helix Fossil — incredible![/cyan]"
            )
            output.write("")
            output.write(
                "[cyan]   The Dome Fossil contains the ancient DNA of KABUTO, "
                "a prehistoric Water/Rock-type Pokemon![/cyan]"
            )
            output.write(
                "[cyan]   The Helix Fossil holds the DNA of OMANYTE, "
                "another prehistoric Water/Rock-type Pokemon![/cyan]"
            )
            output.write("")
            output.write(
                "[cyan]   The revival lab at the Cinnabar Island Pokémon Lab can bring "
                "both back to life![/cyan]"
            )
            output.write(
                "[cyan]   Visit Cinnabar Island when you're ready to resurrect them...[/cyan]"
            )
        elif has_dome:
            output.write(
                "[cyan]   That's a Dome Fossil! It contains the ancient DNA of KABUTO, "
                "a prehistoric Water/Rock-type Pokemon![/cyan]"
            )
            output.write(
                "[cyan]   The revival lab at the Cinnabar Island Pokémon Lab can bring it "
                "back to life.[/cyan]"
            )
            output.write(
                "[cyan]   You'll want to visit Cinnabar Island when you're ready...[/cyan]"
            )
        elif has_helix:
            output.write(
                "[cyan]   That's a Helix Fossil! It contains the ancient DNA of OMANYTE, "
                "a prehistoric Water/Rock-type Pokemon![/cyan]"
            )
            output.write(
                "[cyan]   The revival lab at the Cinnabar Island Pokémon Lab can bring it "
                "back to life.[/cyan]"
            )
            output.write(
                "[cyan]   You'll want to visit Cinnabar Island when you're ready...[/cyan]"
            )
        else:
            output.write(
                "[cyan]   I see you found a fossil in Mt. Moon... Did you already pass it "
                "to someone?[/cyan]"
            )
            output.write(
                "[cyan]   The Cinnabar Island lab is the only place that can revive "
                "ancient Pokemon.[/cyan]"
            )
        output.write("")
    write_lines(output, T.MUSEUM_FOOTER)
    set_pending_command_callback("museum")


def enter_bills_house(game_state: "GameState", output: RichLog) -> None:
    """
    Enter Bill's House on Route 24.

    First visit: Bill introduces himself, explains the PC storage system, and gives the
    player an S.S. Anne Ticket.  Repeat visits: Bill reminds the player about Vermillion
    City and the PC system.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
    """
    story_flags = game_state.game_data.setdefault("story_flags", {})

    write_lines(output, T.BILLS_HOUSE_HEADER)

    if not story_flags.get("visited_bills_house"):
        # First visit
        output.write(
            "[bold]Bill:[/bold] [cyan]Ah, a trainer! I'm Bill, Pokemon researcher and "
            "inventor of the PC Storage System.[/cyan]"
        )
        output.write("")
        output.write(
            "[cyan]   You see, I've always believed trainers shouldn't be limited to carrying "
            "just six Pokemon at a time.[/cyan]"
        )
        output.write(
            "[cyan]   So I built a network of computer terminals — Bill's PC — that links "
            "every Pokemon Center across Kanto![/cyan]"
        )
        output.write(
            "[cyan]   When your party is full, caught Pokemon are automatically stored. "
            "You can retrieve them anytime at a Center.[/cyan]"
        )
        output.write("")
        output.write(
            "[bold]Bill:[/bold] [cyan]Oh! I almost forgot — I have something for you.[/cyan]"
        )
        output.write("")

        # Give S.S. Anne Ticket (only once — guard with received_ss_ticket flag)
        if not story_flags.get("received_ss_ticket"):
            bag = game_state.game_data.setdefault("bag", {})
            bag["S.S. Anne Ticket"] = bag.get("S.S. Anne Ticket", 0) + 1
            story_flags["received_ss_ticket"] = True
            output.write("[bold yellow]★ Received S.S. Anne Ticket! ★[/bold yellow]")
            output.write("")
            output.write(
                "[bold]Bill:[/bold] [cyan]Take this S.S. Anne Ticket. The ship docks at "
                "Vermillion City — there may be special items aboard![/cyan]"
            )
            output.write(
                "[cyan]   Vermillion City is south of Cerulean City, past Diglett's Cave "
                "or through the Underground Path.[/cyan]"
            )

        story_flags["visited_bills_house"] = True
    else:
        # Repeat visit
        output.write(
            "[bold]Bill:[/bold] [cyan]Welcome back! The PC storage system is running "
            "smoothly today.[/cyan]"
        )
        output.write("")
        output.write(
            "[cyan]   Remember, you can access Bill's PC at any Pokemon Center to manage "
            "your stored Pokemon.[/cyan]"
        )
        if story_flags.get("received_ss_ticket"):
            output.write("")
            output.write(
                "[cyan]   Don't forget about the S.S. Anne in Vermillion City — "
                "it's worth a visit![/cyan]"
            )

    output.write("")
    output.write("[bold yellow]💻 PC STORAGE SYSTEM[/bold yellow]")
    output.write(
        "   [dim]Visit the PC terminal at any Pokemon Center to access your stored Pokemon.[/dim]"
    )
    output.write("   [dim]Type 'pc' at a Pokemon Center to open Bill's PC.[/dim]")
    output.write("")
    output.write("[dim]You leave Bill's House on Route 24[/dim]")
    output.write("")


def enter_ss_anne(game_state: "GameState", output: RichLog) -> None:
    """
    Enter the S.S. Anne docked at Vermillion City.

    First visit with a valid S.S. Anne Ticket: tour the ship, receive HM01 Cut
    from the Captain.  Repeat visits: the ship has departed.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
    """
    story_flags = game_state.game_data.setdefault("story_flags", {})
    bag = game_state.game_data.setdefault("bag", {})
    items = game_state.game_data.setdefault("items", {})

    write_lines(output, T.SS_ANNE_HEADER)

    if story_flags.get("ss_anne_departed"):
        write_lines(output, T.SS_ANNE_ALREADY_DEPARTED)
        return

    # Check for ticket
    has_ticket = bag.get("S.S. Anne Ticket", 0) > 0 or items.get("S.S. Anne Ticket", 0) > 0
    if not has_ticket:
        write_lines(output, T.SS_ANNE_NO_TICKET)
        return

    if story_flags.get("received_hm01_cut"):
        # Already visited — ship departs
        story_flags["ss_anne_departed"] = True
        write_lines(output, T.SS_ANNE_DEPARTING_AFTER_VISIT)
        return

    # First visit with ticket
    write_lines(output, T.SS_ANNE_FIRST_VISIT_STORY)

    # Award HM01 Cut
    items["HM01 Cut"] = items.get("HM01 Cut", 0) + 1
    story_flags["received_hm01_cut"] = True

    write_lines(output, T.SS_ANNE_RECEIVED_HM01_CUT)
    write_lines(output, T.SS_ANNE_HM01_EXPLANATION)


def enter_pokemon_tower(game_state: "GameState", output: RichLog) -> None:
    """
    Enter the Pokemon Tower in Lavender Town.

    A seven-story tower where Pokemon are laid to rest. Ghost-type Pokemon and
    Channeler trainers roam the upper floors. Mr. Fuji can be found at the top.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
    """
    story_flags = game_state.game_data.setdefault("story_flags", {})

    write_lines(output, T.POKEMON_TOWER_HEADER)
    write_lines(output, T.POKEMON_TOWER_AMBIENCE)

    if story_flags.get("pokemon_tower_mr_fuji_rescued"):
        write_lines(output, T.POKEMON_TOWER_RESCUED_DIALOGUE)
        items = game_state.game_data.setdefault("items", {})
        if not story_flags.get("received_poke_flute"):
            items["Poke Flute"] = items.get("Poke Flute", 0) + 1
            story_flags["received_poke_flute"] = True
            write_lines(output, T.POKEMON_TOWER_RESCUED_REWARD)
        else:
            write_lines(output, T.POKEMON_TOWER_RESCUED_ALREADY_REWARDED)
        return

    if story_flags.get("pokemon_tower_ghost_appeared"):
        write_lines(output, T.POKEMON_TOWER_GHOST_APPEARED_DIALOGUE)
        return

    # First visit
    write_lines(output, T.POKEMON_TOWER_FIRST_VISIT_DIALOGUE)
    story_flags["pokemon_tower_visited"] = True


def enter_bike_shop(game_state: "GameState", output: RichLog) -> None:
    """
    Enter the Cerulean City Bike Shop.

    On the first visit the owner gives the player a free Bicycle.
    The Bicycle reduces wild encounter rate while riding on routes (future mechanic).

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
    """
    write_lines(output, T.BIKE_SHOP_HEADER)
    write_lines(output, T.BIKE_SHOP_WELCOME)
    story_flags = game_state.game_data.setdefault("story_flags", {})
    if not story_flags.get("received_bicycle"):
        write_lines(output, T.BIKE_SHOP_FIRST_VISIT_DIALOGUE)
        items = game_state.game_data.setdefault("items", {})
        items["Bicycle"] = 1
        story_flags["received_bicycle"] = True
        write_lines(output, T.BIKE_SHOP_RECEIVED_BICYCLE)
    else:
        write_lines(output, T.BIKE_SHOP_REPEAT_DIALOGUE)
    write_lines(output, T.BIKE_SHOP_EXIT)


def enter_nugget_bridge(
    game_state: "GameState",
    output: RichLog,
    set_pending_command_callback,
    trigger_trainer_battle_callback=None,
) -> None:
    """
    Enter Nugget Bridge north of Cerulean City.

    Five trainers guard the bridge in sequence. Defeat all five to earn a Nugget
    worth 5000 Pokedollars.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
        set_pending_command_callback: Callback to set pending command
        trigger_trainer_battle_callback: Optional callback for triggering trainer battles
    """
    story_flags = game_state.game_data.setdefault("story_flags", {})
    write_lines(output, T.NUGGET_BRIDGE_HEADER)
    if story_flags.get("nugget_bridge_complete"):
        write_lines(output, T.NUGGET_BRIDGE_ALREADY_COMPLETE)
        return
    nugget_trainers = [
        "nugget_trainer_1",
        "nugget_trainer_2",
        "nugget_trainer_3",
        "nugget_trainer_4",
        "nugget_trainer_5",
    ]
    defeated = game_state.game_data.get("defeated_trainers", [])
    defeated_count = sum(1 for t in nugget_trainers if t in defeated)
    if defeated_count >= 5:
        # All five just defeated — award prize
        story_flags["nugget_bridge_complete"] = True
        items = game_state.game_data.setdefault("items", {})
        items["Nugget"] = items.get("Nugget", 0) + 1
        write_lines(output, T.NUGGET_BRIDGE_ALL_TRAINERS_BEATEN)
        # ---- Rival battle after Nugget Bridge ----
        if not story_flags.get("rival_cerulean_beaten") and trigger_trainer_battle_callback:
            rival_trainer = copy.deepcopy(TRAINERS.get("rival_cerulean"))
            if rival_trainer:
                rival_starter_map = {
                    "CHARMANDER": "CHARMELEON",
                    "SQUIRTLE": "WARTORTLE",
                    "BULBASAUR": "IVYSAUR",
                    "EEVEE": "EEVEE",
                }
                raw_starter = game_state.game_data.get("rival_starter", "CHARMANDER").upper()
                evolved = rival_starter_map.get(raw_starter, "CHARMELEON")
                rival_trainer.pokemon[0].species = evolved
                rival_trainer.name = game_state.game_data.get("rival_name", "Rival")
                write_lines(output, T.NUGGET_BRIDGE_RIVAL_CALL_OUT)
                trigger_trainer_battle_callback(rival_trainer)
                return  # Battle takes over
        return
    if defeated_count == 0:
        write_lines(output, T.NUGGET_BRIDGE_FIRST_CHALLENGE)
    else:
        remaining = 5 - defeated_count
        write_lines_fmt(
            output,
            T.NUGGET_BRIDGE_PROGRESS,
            defeated_count=defeated_count,
            remaining=remaining,
        )
    # Find and trigger the next undefeated trainer
    next_trainer_id = next((t for t in nugget_trainers if t not in defeated), None)
    if next_trainer_id and trigger_trainer_battle_callback:
        trainer = TRAINERS.get(next_trainer_id)
        if trainer:
            trigger_trainer_battle_callback(trainer)
            return
    write_lines(output, T.NUGGET_BRIDGE_WAITING_PROMPT)


def enter_players_house(
    game_state: "GameState", output: RichLog, set_pending_command_callback
) -> None:
    """
    Enter the player's house.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
        set_pending_command_callback: Callback to set pending command
    """
    player_name = game_state.game_data.get("player_name", "Trainer")
    output.write("")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write(
        f"[bold cyan]          🏠 {player_name.upper()}'S HOUSE 🏠            [/bold cyan]"
    )
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("")
    output.write("[bold]Mom:[/bold] [magenta]Welcome home, sweetie! ❤️[/magenta]")
    output.write("")

    # Check if player has Pokemon
    pokemon = game_state.game_data.get("pokemon", [])

    if pokemon:
        # Check if any Pokemon need healing
        needs_healing = any(
            not isinstance(p, str)
            and (
                p.get("hp", 0) < p.get("max_hp", 0)
                or p.get("status") is not None
                or any(m.get("pp", 0) < m.get("max_pp", 0) for m in p.get("moves", []))
            )
            for p in pokemon
        )

        if needs_healing:
            output.write("[bold]Mom:[/bold] [magenta]Oh my! Your Pokemon look tired![/magenta]")
            output.write("[magenta]   Would you like me to make them feel better?[/magenta]")
            output.write("")

            # Show Yes/No healing panel
            set_pending_command_callback("confirm_heal_mom")
            return
        else:
            output.write(
                "[bold]Mom:[/bold] [magenta]Your Pokemon look happy and healthy![/magenta]"
            )
            output.write("")
    else:
        output.write(
            "[bold]Mom:[/bold] [magenta]Did you get a Pokemon from Professor Oak yet?[/magenta]"
        )
        output.write("")

    output.write("[magenta]   Your room is upstairs if you need anything.[/magenta]")
    output.write("[magenta]   There's a TV in the living room if you want to watch.[/magenta]")
    output.write("")
    output.write("[bold]Mom:[/bold] [magenta]Take care on your journey![/magenta]")
    output.write("")
    output.write("[dim]You leave the house[/dim]")
    output.write("")


def perform_pokemon_center_heal(
    game_state: "GameState",
    output: RichLog,
    line_writer: Optional[Callable[[RichLog, list[str]], None]] = None,
) -> None:
    """
    Actually perform the Pokemon Center healing.

    Args:
        game_state: The game state object.
        output: The RichLog widget to write to.
        line_writer: Optional callback to write all produced lines. If omitted,
            lines are written instantly in order.
    """
    pokemon = game_state.game_data.get("pokemon", [])

    # Record this as the last visited Pokemon Center
    current_location = game_state.current_location.name if game_state.current_location else None
    if current_location:
        game_state.game_data["last_pokemon_center"] = current_location

    heal_lines: list[str] = [
        "",
        "[magenta]   Let me heal your Pokemon...[/magenta]",
        "",
        "[cyan]   ♪ Healing sound ♪[/cyan]",
        "",
    ]

    # Show healed Pokemon and restore HP + PP + status
    for p in pokemon:
        if not isinstance(p, str):
            p["hp"] = p.get("max_hp", p["hp"])
            for move in p.get("moves", []):
                move["pp"] = move.get("max_pp", move["pp"])
            had_status = p.get("status") is not None
            p["status"] = None
            name = p["name"]
            if had_status:
                heal_lines.append(f"   [green]✓ {name} restored to full health and cured![/green]")
            else:
                heal_lines.append(f"   [green]✓ {name} restored to full health![/green]")
        else:
            heal_lines.append(f"   [green]✓ {p} restored to full health![/green]")

    heal_lines.extend(
        [
            "",
            "[bold]Nurse Joy:[/bold] [magenta]Your Pokemon are now fully healed![/magenta]",
            "[magenta]   All HP, PP, and status conditions restored![/magenta]",
            "[magenta]   Is there anything else I can do for you?[/magenta]",
            "",
        ]
    )

    if line_writer is None:
        for line in heal_lines:
            output.write(line)
        return

    line_writer(output, heal_lines)


def perform_mom_heal(game_state: "GameState", output: RichLog) -> None:
    """
    Actually perform Mom's healing.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
    """
    pokemon = game_state.game_data.get("pokemon", [])

    write_lines(output, T.MOM_HEAL_HEADER)

    # Show healed Pokemon and restore HP + PP + status
    for p in pokemon:
        if not isinstance(p, str):
            p["hp"] = p.get("max_hp", p["hp"])
            for move in p.get("moves", []):
                move["pp"] = move.get("max_pp", move["pp"])
            had_status = p.get("status") is not None
            p["status"] = None
            name = p["name"]
            if had_status:
                output.write(f"   [green]✓ {name} is feeling much better![/green]")
            else:
                output.write(f"   [green]✓ {name} is full of energy![/green]")
        else:
            output.write(f"   [green]✓ {p} is feeling great![/green]")

    write_lines(output, T.MOM_HEAL_SUCCESS)


def enter_rivals_house(game_state: "GameState", output: RichLog) -> None:
    """
    Enter the rival's house.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
    """
    rival_name = game_state.game_data.get("rival_name", "Rival")
    write_lines_fmt(output, T.RIVALS_HOUSE_HEADER, rival_name_upper=rival_name.upper())

    # Check if player has Pokemon yet
    pokemon = game_state.game_data.get("pokemon", [])

    if not pokemon:
        write_lines_fmt(output, T.RIVALS_HOUSE_NO_POKEMON, rival_name=rival_name)
    else:
        write_lines_fmt(output, T.RIVALS_HOUSE_WITH_POKEMON, rival_name=rival_name)

    write_lines(output, T.RIVALS_HOUSE_EXIT)


def enter_oaks_lab(
    game_state: "GameState",
    output: RichLog,
    set_pending_command_callback,
    show_starter_panel_callback=None,
) -> None:
    """
    Enter Professor Oak's Laboratory.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
        set_pending_command_callback: Callback to set pending command
        show_starter_panel_callback: Optional callback to show starter selection panel
    """
    write_lines(output, T.OAKS_LAB_HEADER)

    # Check if player has Pokemon yet
    pokemon = game_state.game_data.get("pokemon", [])

    if not pokemon:
        # Check if Pikachu mode (Pokemon Yellow Easter egg)
        if game_state.pikachu_mode:
            write_lines(output, T.OAKS_LAB_PIKACHU_INTRO)

            # Show button panel if callback provided
            if show_starter_panel_callback:
                write_lines(output, T.OAKS_LAB_PIKACHU_PROMPT_PANEL)
                show_starter_panel_callback(game_state.pikachu_mode)
            else:
                write_lines(output, T.OAKS_LAB_PIKACHU_PROMPT_TEXT)

            output.write("")
        else:
            write_lines(output, T.OAKS_LAB_STARTER_INTRO)

            # Show button panel if callback provided
            if show_starter_panel_callback:
                write_lines(output, T.OAKS_LAB_STARTER_PROMPT_PANEL)
                show_starter_panel_callback(game_state.pikachu_mode)
            else:
                write_lines(output, T.OAKS_LAB_STARTER_PROMPT_TEXT)

            output.write("")

        # Set pending command
        set_pending_command_callback("choose_starter")
    else:
        write_lines(output, T.OAKS_LAB_PROGRESS_DIALOGUE)
        write_lines_fmt(output, T.OAKS_LAB_CAUGHT_COUNT, caught_count=len(pokemon))

    write_lines(output, T.OAKS_LAB_EXIT)


def choose_starter_pokemon(
    game_state: "GameState",
    pokemon_name: str,
    output: RichLog,
    set_pending_command_callback,
    trigger_trainer_battle_callback=None,
) -> None:
    """
    Choose a starter Pokemon.

    Args:
        game_state: The game state object
        pokemon_name: Name of the Pokemon to choose
        output: The RichLog widget to write to
        set_pending_command_callback: Callback to set pending command
        trigger_trainer_battle_callback: Optional callback ``(trainer) -> None`` that
            starts the rival battle with full TUI panels.  When omitted the battle is
            started headlessly via ``battle_actions.trigger_trainer_encounter``.
    """
    # Normalize the input
    choice = pokemon_name.lower().strip()

    if choice.startswith("choose "):
        choice = choice[7:].strip()

    # Check for Pikachu (Easter egg)
    if "pikachu" in choice:
        if not game_state.pikachu_mode:
            # Pikachu is not available in normal mode
            write_lines(output, T.STARTER_INVALID_NOT_AVAILABLE)
            set_pending_command_callback("choose_starter")
            return
        else:
            # Pikachu mode activated - give Pikachu
            # Generate full battle-ready Pikachu data
            _bs = BattleState()
            pikachu_data = _bs.generate_wild_pokemon("PIKACHU", 5)
            pikachu_data["no_evolve"] = True  # This Pikachu refuses to evolve!
            game_state.game_data["pokemon"].append(pikachu_data)
            pokedex.mark_as_caught(game_state, str(pikachu_data.get("name", "PIKACHU")).upper())
            # Rival gets Eevee in Pikachu mode
            game_state.game_data["rival_pokemon"] = ["Eevee (Lv. 5)"]

            write_lines(output, T.STARTER_PIKACHU_SELECTED)
            # Give starter Potions
            items = game_state.game_data.setdefault("items", {})
            items["Potion"] = items.get("Potion", 0) + 5

            # Trigger rival battle for Pikachu mode!
            rival_trainer = copy.deepcopy(TRAINERS.get("rival_oaks_lab"))
            if rival_trainer:
                # Set the rival's Pokemon to Eevee for Pikachu mode
                rival_trainer.pokemon[0].species = "EEVEE"

                # Store that we've battled the rival in Oak's lab
                defeated_trainers = game_state.game_data.get("defeated_trainers", [])

                # Only battle if we haven't already defeated them here
                if "rival_oaks_lab" not in defeated_trainers:
                    write_lines(output, T.STARTER_TURN_TO_LEAVE)
                    # Trigger the battle
                    if trigger_trainer_battle_callback:
                        trigger_trainer_battle_callback(rival_trainer)
                    else:
                        battle_actions.trigger_trainer_encounter(
                            game_state, output, rival_trainer, set_pending_command_callback
                        )
                    return  # Battle takes over, function will be called again after battle

            # This part runs after the battle (or if battle was skipped)
            write_lines(output, T.STARTER_JOURNEY_READY_PIKACHU)
            return

    # Map of valid starters (normal mode)
    starters = {
        "bulbasaur": {
            "name": "Bulbasaur",
            "type": "Grass/Poison",
            "emoji": "🌿",
            "rival": "Charmander",
        },
        "charmander": {"name": "Charmander", "type": "Fire", "emoji": "🔥", "rival": "Squirtle"},
        "squirtle": {"name": "Squirtle", "type": "Water", "emoji": "💧", "rival": "Bulbasaur"},
    }

    # Find matching starter
    selected_starter = None
    for key, data in starters.items():
        if key in choice or choice in key:
            selected_starter = data
            break

    if not selected_starter:
        if game_state.pikachu_mode:
            write_lines(output, T.STARTER_SELECTION_INVALID_PIKACHU_MODE)
        else:
            write_lines(output, T.STARTER_SELECTION_INVALID_NORMAL_MODE)
        # Set pending command again to wait for valid input
        set_pending_command_callback("choose_starter")
        return

    # Pikachu mode only allows Pikachu
    if game_state.pikachu_mode:
        write_lines(output, T.STARTER_SELECTION_PIKACHU_ONLY)
        set_pending_command_callback("choose_starter")
        return

    # Add Pokemon to party (normal mode)
    # Generate full battle-ready Pokemon data
    _bs = BattleState()
    starter_data = _bs.generate_wild_pokemon(selected_starter["name"].upper(), 5)
    starter_data["no_evolve"] = False
    game_state.game_data["pokemon"].append(starter_data)
    pokedex.mark_as_caught(game_state, str(starter_data.get("name", "")).upper())

    # Rival gets the Pokemon with type advantage
    rival_pokemon = selected_starter["rival"]
    game_state.game_data["rival_pokemon"] = [f"{rival_pokemon} (Lv. 5)"]

    # Show selection confirmation
    write_lines_fmt(
        output,
        T.STARTER_SELECTION_CONFIRMED,
        emoji=selected_starter["emoji"],
        starter_name=selected_starter["name"],
        rival_pokemon=rival_pokemon,
    )
    # Give starter Potions
    items = game_state.game_data.setdefault("items", {})
    items["Potion"] = items.get("Potion", 0) + 5

    # Trigger rival battle!
    rival_trainer = copy.deepcopy(TRAINERS.get("rival_oaks_lab"))
    if rival_trainer:
        # Set the rival's Pokemon to match what they chose
        rival_trainer.pokemon[0].species = rival_pokemon.upper()

        # Store that we've battled the rival in Oak's lab
        defeated_trainers = game_state.game_data.get("defeated_trainers", [])

        # Only battle if we haven't already defeated them here
        if "rival_oaks_lab" not in defeated_trainers:
            write_lines(output, T.STARTER_TURN_TO_LEAVE)
            # Trigger the battle
            if trigger_trainer_battle_callback:
                trigger_trainer_battle_callback(rival_trainer)
            else:
                battle_actions.trigger_trainer_encounter(
                    game_state, output, rival_trainer, set_pending_command_callback
                )
            return  # Battle takes over, function will be called again after battle

    # This part runs after the battle (or if battle was skipped)
    write_lines(output, T.STARTER_JOURNEY_READY)


def enter_ss_anne_dock(game_state: "GameState", output: RichLog) -> None:
    """
    Enter the S.S. Anne Dock building in Vermillion City.

    Checks for the S.S. Anne Ticket and provides instructions on boarding the ship.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
    """
    write_lines(output, T.SS_ANNE_DOCK_HEADER)

    bag = game_state.game_data.get("items", {})
    story_flags = game_state.game_data.setdefault("story_flags", {})
    has_ticket = bag.get("S.S. Anne Ticket", 0) > 0
    already_boarded = story_flags.get("boarded_ss_anne", False)

    write_lines(output, T.SS_ANNE_DOCK_WELCOME)

    if has_ticket or already_boarded:
        write_lines(output, T.SS_ANNE_DOCK_HAS_TICKET)
    else:
        write_lines(output, T.SS_ANNE_DOCK_NO_TICKET)

    write_lines(output, T.SS_ANNE_DOCK_FOOTER)


def enter_mr_fujis_house(game_state: "GameState", output: RichLog) -> None:
    """
    Enter Mr. Fuji's House in Lavender Town.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
    """
    write_lines(output, T.MR_FUJIS_HOUSE_HEADER)

    story_flags = game_state.game_data.setdefault("story_flags", {})
    rescued = story_flags.get("rescued_mr_fuji", False)

    if rescued:
        bag = game_state.game_data.setdefault("items", {})
        write_lines(output, T.MR_FUJIS_RESCUED_DIALOGUE)
        if not bag.get("Poke Flute"):
            # Give flute again if somehow lost
            bag["Poke Flute"] = 1
            write_lines(output, T.MR_FUJIS_REWARD)
    else:
        write_lines(output, T.MR_FUJIS_NOT_HOME_DIALOGUE)

    write_lines(output, T.MR_FUJIS_HOUSE_FOOTER)


def enter_game_corner(game_state: "GameState", output: RichLog) -> None:
    """
    Enter the Game Corner in Celadon City.

    Provides flavour text and hints about Team Rocket's hidden base.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
    """
    write_lines(output, T.GAME_CORNER_HEADER)

    story_flags = game_state.game_data.setdefault("story_flags", {})
    hideout_cleared = story_flags.get("defeated_giovanni_hideout", False)

    write_lines(output, T.GAME_CORNER_ATTENDANT)

    if hideout_cleared:
        write_lines(output, T.GAME_CORNER_AFTER_HIDEOUT)
    else:
        write_lines(output, T.GAME_CORNER_HIDEOUT_HINT)

    write_lines(output, T.GAME_CORNER_FOOTER)


def enter_department_store(game_state: "GameState", output: RichLog) -> None:
    """
    Enter the Celadon Department Store.

    Offers a wide selection of items for sale.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
    """
    write_lines(output, T.DEPARTMENT_STORE_HEADER)
    write_lines(output, T.DEPARTMENT_STORE_WELCOME)

    money = game_state.game_data.get("money", 0)
    write_lines_fmt(output, T.DEPARTMENT_STORE_MONEY, money=money)

    dept_items = [
        ("🔴", "Pokeball", 200),
        ("🔵", "Great Ball", 600),
        ("⚫", "Ultra Ball", 1200),
        ("💊", "Hyper Potion", 1200),
        ("✨", "Full Restore", 3000),
        ("💫", "Revive", 1500),
        ("🌟", "Full Heal", 600),
        ("🍬", "Rare Candy", 4800),
        ("🔥", "Fire Stone", 2100),
        ("💧", "Water Stone", 2100),
        ("⚡", "Thunder Stone", 2100),
        ("🍃", "Leaf Stone", 2100),
        ("🌙", "Moon Stone", 2100),
        ("❤️", "HP Up", 9800),
        ("💪", "Protein", 9800),
    ]
    for emoji, name, price in dept_items:
        output.write(f"   {emoji} [green]{name}[/green] - ₽{price}")

    write_lines(output, T.DEPARTMENT_STORE_FOOTER)


def enter_safari_zone(game_state: "GameState", output: RichLog) -> None:
    """
    Enter the Safari Zone in Fuchsia City.

    Players receive 30 Safari Balls and must catch Pokemon using Bait or Rocks
    instead of battling. Explores inside the Safari Zone trigger wild encounters
    using the standard exploration engine but with Safari-mode catch mechanics.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
    """
    if not game_state.in_game:
        write_lines(output, T.SAFARI_START_GAME_FIRST)
        return

    write_lines(output, T.SAFARI_ZONE_HEADER)
    write_lines(output, T.SAFARI_WARDEN_INTRO)

    money = game_state.game_data.get("money", 0)
    if money < 500:
        write_lines(output, T.SAFARI_NOT_ENOUGH_MONEY)
        return

    game_state.game_data["money"] = money - 500

    # Give 30 Safari Balls (stored in the standard items dict)
    bag = game_state.game_data.setdefault("items", {})
    bag["Safari Ball"] = bag.get("Safari Ball", 0) + 30

    # Move player into the Safari Zone
    from pytemon.locations import get_location

    safari_location = get_location("Safari Zone")
    if safari_location:
        game_state.previous_location = (
            game_state.current_location.name if game_state.current_location else "Fuchsia City"
        )
        game_state.current_location = safari_location

    write_lines(output, T.SAFARI_ENTRY_SUCCESS)
    write_lines(output, T.SAFARI_RULES)

    remaining = bag.get("Safari Ball", 0)
    write_lines_fmt(output, T.SAFARI_BALLS_REMAINING, remaining=remaining)
