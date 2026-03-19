"""
Building handlers for Pokemon Terminal.

This module contains all the logic for entering and interacting with buildings
like Pokemon Centers, Pokemarts, Gyms, and story buildings.
"""

from typing import TYPE_CHECKING

from textual.widgets import RichLog

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
        output.write("")
        output.write("[yellow]⚠ There are no buildings here[/yellow]")
        output.write("[dim]Buildings are only found in towns and cities[/dim]")
        output.write("")
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
                    output.write("")
                    output.write(
                        "[bold yellow]🎮 [CHEAT MODE] Bypassing restriction...[/bold yellow]"
                    )
                    break
                else:
                    output.write("")
                    output.write(f"[yellow]⚠ {reason}[/yellow]")
                    output.write("")
                    return

        # If still not found, show error
        if not matching_building:
            output.write("")
            output.write(f"[red]❌ '{building_name}' is not a building here[/red]")
            output.write("[dim]Type 'Look Around' to see available buildings[/dim]")
            output.write("")
            return

    # Route to appropriate building handler
    player_name = game_state.game_data.get("player_name", "Trainer")
    rival_name = game_state.game_data.get("rival_name", "Rival")

    if "pokemon center" in matching_building.lower():
        enter_pokemon_center(game_state, output, set_pending_command_callback)
    elif "pokemart" in matching_building.lower() or "mart" in matching_building.lower():
        enter_pokemart(
            game_state, output, set_pending_command_callback, show_pokemart_panel_callback
        )
    elif "gym" in matching_building.lower():
        # Import gym system here to avoid circular imports
        from . import gym_system

        if show_gym_panel_callback:
            gym_system.enter_gym_lobby(game_state, output, show_gym_panel_callback)
        elif trigger_trainer_battle_callback:
            gym_system.enter_gym(game_state, output, trigger_trainer_battle_callback)
        else:
            output.write("")
            output.write("[yellow]⚠ Gym battles are not available in this context[/yellow]")
            output.write("")
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
        enter_museum(game_state, output)
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
    elif "silph" in matching_building.lower():
        enter_silph_co(game_state, output, trigger_trainer_battle_callback)
    elif "pokemon mansion" in matching_building.lower():
        enter_pokemon_mansion(game_state, output, trigger_trainer_battle_callback)
    elif "pokemon lab" in matching_building.lower():
        enter_pokemon_lab(game_state, output)
    elif "elite four" in matching_building.lower():
        enter_elite_four(game_state, output, trigger_trainer_battle_callback)
    elif "hall of fame" in matching_building.lower():
        enter_hall_of_fame(game_state, output)
    elif (
        "reception" in matching_building.lower()
        and "league" in game_state.current_location.name.lower()
    ):
        enter_pokemon_league_reception(game_state, output)
    else:
        output.write("")
        output.write(f"[yellow]You entered {matching_building}[/yellow]")
        output.write("[dim]This building is not yet implemented[/dim]")
        output.write("")


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
    output.write("")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("[bold cyan]           🏥 POKEMON CENTER 🏥            [/bold cyan]")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("")
    output.write("[bold]Nurse Joy:[/bold] [magenta]Welcome to the Pokemon Center![/magenta]")
    output.write("")

    # Check if player has Pokemon
    pokemon = game_state.game_data.get("pokemon", [])

    if not pokemon:
        output.write("[magenta]   But it seems you don't have any Pokemon yet![/magenta]")
        output.write("")
        output.write("[dim]You leave the Pokemon Center[/dim]")
        output.write("")
        return

    # Show Pokemon Center lobby menu
    output.write("[bold]Nurse Joy:[/bold] [magenta]How can I help you today?[/magenta]")
    output.write("")

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
    output.write("")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("[bold cyan]            🏪 POKEMART 🏪                [/bold cyan]")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("")
    output.write("[bold]Clerk:[/bold] [yellow]Welcome to the Pokemart![/yellow]")
    output.write("[yellow]   What can I get for you?[/yellow]")
    output.write("")
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
    output.write(
        "[dim]Commands: 'buy <item>'  or  'buy <qty> <item>'  (e.g. 'buy 5 pokeball')[/dim]"
    )
    output.write("[dim]          'leave' to exit the shop[/dim]")
    output.write("")


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
        output.write("")
        output.write("[bold]Clerk:[/bold] [yellow]Thank you! Come again![/yellow]")
        output.write("")
        output.write("[dim]You leave the Pokemart[/dim]")
        output.write("")
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
            output.write("")
            output.write("[red]❌ That item has no resale value[/red]")
            output.write("")
            set_pending_command_callback("shop")
            return

        # Check player has the item
        items = game_state.game_data.setdefault("items", {})
        owned_qty = items.get(sell_item_name, 0)
        if owned_qty <= 0:
            output.write("")
            output.write(f"[red]❌ You don't have any {sell_item_name}![/red]")
            output.write("")
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
        output.write("")
        output.write(
            f"[bold green]✓ Sold {sale_qty}x {sell_item_name} for ₽{total_earned}![/bold green]"
        )
        output.write(f"   [dim]Money: ₽{new_balance}[/dim]")
        output.write("")

        show_shop_menu(game_state, output)
        set_pending_command_callback("shop")
        return

    if not cmd.startswith("buy "):
        output.write("")
        output.write("[yellow]?[/yellow] [dim]I don't understand that.[/dim]")
        output.write("[dim]Type 'buy <item>', 'sell <item>' or 'leave'[/dim]")
        output.write("")
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
        output.write("")
        output.write(f"[red]❌ '{command[4:].strip()}' is not sold here[/red]")
        output.write("[dim]Check the item list above[/dim]")
        output.write("")
        set_pending_command_callback("shop")
        return

    info = catalog[matched_item]
    total_cost = info["price"] * qty
    money = game_state.game_data.get("money", 0)

    if money < total_cost:
        output.write("")
        output.write(f"[red]❌ Not enough money! Need ₽{total_cost}, have ₽{money}[/red]")
        output.write("")
        set_pending_command_callback("shop")
        return

    # Complete purchase
    game_state.game_data["money"] = money - total_cost
    items = game_state.game_data.setdefault("items", {})
    items[matched_item] = items.get(matched_item, 0) + qty

    output.write("")
    output.write(f"[bold green]✓ Bought {qty}x {matched_item} for ₽{total_cost}![/bold green]")
    output.write(f"   [dim]Remaining money: ₽{game_state.game_data['money']}[/dim]")
    output.write("")

    show_shop_menu(game_state, output)
    set_pending_command_callback("shop")


# Note: enter_gym has been moved to gym_system.py


def enter_museum(game_state: "GameState", output: RichLog) -> None:
    """
    Enter the Pewter City Natural Science Museum.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
    """
    output.write("")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("[bold cyan]       🏛️  PEWTER CITY MUSEUM 🏛️         [/bold cyan]")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("")
    output.write(
        "[bold]Museum Guide:[/bold] [green]Welcome to the Pewter City Natural Science Museum![/green]"
    )
    output.write("[green]   We showcase rare Pokemon fossils and space artifacts![/green]")
    output.write("")
    output.write("[bold yellow]🦕 FOSSIL EXHIBIT[/bold yellow]")
    output.write("   [dim]Ancient Pokemon fossils recovered from nearby Mt. Moon:[/dim]")
    output.write("")
    output.write(
        "   🦴 [cyan]Old Amber[/cyan]    — Prehistoric remains of an ancient flying Pokemon"
    )
    output.write(
        "   🪨 [cyan]Dome Fossil[/cyan]  — Said to contain a prehistoric Water-type Pokemon"
    )
    output.write("   🪨 [cyan]Helix Fossil[/cyan] — Holds the DNA of a curiously spiralled Pokemon")
    output.write("")
    output.write("[bold yellow]🌑 MOON STONE EXHIBIT[/bold yellow]")
    output.write(
        "   🌙 [magenta]Moon Stone[/magenta] — A mysterious stone from space; causes certain Pokemon to evolve"
    )
    output.write("   [dim]Tip: Full Moon Stones can sometimes be found in Mt. Moon![/dim]")
    output.write("")
    output.write("[bold yellow]🗿 SPACE EXHIBIT[/bold yellow]")
    output.write("   ⭐ [yellow]Meteorite Fragment[/yellow] — A chunk of rock from outer space")
    output.write(
        "   🌌 [blue]Star Charts[/blue]         — Ancient navigation maps used by Pokemon sailors"
    )
    output.write("")
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
    output.write(
        "[bold]Museum Guide:[/bold] [green]Admission is free for Pokemon trainers![/green]"
    )
    output.write("[green]   Come back if you find any fossils on your journey![/green]")
    output.write("")
    output.write("[dim]You leave the museum, inspired by the ancient history[/dim]")
    output.write("")


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

    output.write("")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("[bold cyan]           💻 BILL'S HOUSE 💻              [/bold cyan]")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("")

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

    output.write("")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("[bold cyan]          🚢 S.S. ANNE DOCK 🚢              [/bold cyan]")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("")

    if story_flags.get("ss_anne_departed"):
        output.write("[dim]The dock is empty — the S.S. Anne has already set sail.[/dim]")
        output.write(
            "[dim]You watch the faint outline of the ship disappear over the horizon.[/dim]"
        )
        output.write("")
        return

    # Check for ticket
    has_ticket = bag.get("S.S. Anne Ticket", 0) > 0 or items.get("S.S. Anne Ticket", 0) > 0
    if not has_ticket:
        output.write(
            "[bold]Guard:[/bold] [yellow]Hey! You can't board without an S.S. Anne Ticket![/yellow]"
        )
        output.write("[yellow]   Talk to Bill on Route 24 — he might be able to help.[/yellow]")
        output.write("")
        output.write("[dim]The guard blocks your path to the gangplank.[/dim]")
        output.write("")
        return

    if story_flags.get("received_hm01_cut"):
        # Already visited — ship departs
        output.write("[bold]Guard:[/bold] [yellow]The Captain thanks you for visiting![/yellow]")
        output.write("[yellow]   The S.S. Anne is preparing to depart now.[/yellow]")
        output.write("")
        output.write(
            "[dim]The crew cast off the moorings and the great ship slowly pulls away.[/dim]"
        )
        story_flags["ss_anne_departed"] = True
        output.write("[dim]The S.S. Anne has departed from Vermillion City.[/dim]")
        output.write("")
        return

    # First visit with ticket
    output.write("[bold]Guard:[/bold] [yellow]Welcome aboard the S.S. Anne![/yellow]")
    output.write("[yellow]   Present your ticket — step right this way![/yellow]")
    output.write("")
    output.write("[dim]You step onto the luxurious ocean liner. The polished decks gleam,[/dim]")
    output.write("[dim]and trainers from all over the world have gathered here.[/dim]")
    output.write("")
    output.write("[cyan]After exploring the cabins and battling a few trainers...[/cyan]")
    output.write("")
    output.write(
        "[bold]Sailor:[/bold] [yellow]The Captain's cabin is at the bow of the ship![/yellow]"
    )
    output.write("[yellow]   He's been a bit seasick, but he loves meeting trainers.[/yellow]")
    output.write("")
    output.write("[italic]You find the Captain slumped over his charts...[/italic]")
    output.write("")
    output.write("[bold]Captain:[/bold] [green]Ugh... I'm not feeling well.[/green]")
    output.write("[green]   But you remind me of a trainer from my youth![/green]")
    output.write("[green]   Take this HM — you've earned it just by making the trip![/green]")
    output.write("")

    # Award HM01 Cut
    items["HM01 Cut"] = items.get("HM01 Cut", 0) + 1
    story_flags["received_hm01_cut"] = True

    output.write("[bold yellow]★ Received HM01 Cut! ★[/bold yellow]")
    output.write("")
    output.write(
        "[bold]Captain:[/bold] [green]Cut can be used to clear small trees blocking your path.[/green]"
    )
    output.write("[green]   You'll need a Pokemon that can learn it,[/green]")
    output.write(
        "[green]   and the [bold]Cascade Badge[/bold] to use it outside of battle.[/green]"
    )
    output.write("")
    output.write("[dim]You bid the Captain farewell and make your way back to the dock.[/dim]")
    output.write("")


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

    output.write("")
    output.write("[bold purple]═══════════════════════════════════════════[/bold purple]")
    output.write("[bold purple]          👻 POKEMON TOWER 👻              [/bold purple]")
    output.write("[bold purple]═══════════════════════════════════════════[/bold purple]")
    output.write("")
    output.write("[dim]An eerie chill passes over you as you push open the heavy doors.[/dim]")
    output.write(
        "[dim]The air inside smells of incense and old stone. Flowers line the walls[/dim]"
    )
    output.write("[dim]beside small placards bearing the names of beloved Pokemon.[/dim]")
    output.write("")

    if story_flags.get("pokemon_tower_mr_fuji_rescued"):
        output.write("[bold]Mr. Fuji:[/bold] [cyan]Ah, my young friend! Thank you again.[/cyan]")
        output.write(
            "[cyan]   The spirits of this tower have grown calmer since you helped.[/cyan]"
        )
        output.write("[cyan]   Please, take this — a small token of my gratitude.[/cyan]")
        output.write("")
        items = game_state.game_data.setdefault("items", {})
        if not story_flags.get("received_poke_flute"):
            items["Poke Flute"] = items.get("Poke Flute", 0) + 1
            story_flags["received_poke_flute"] = True
            output.write("[bold yellow]★ Received the Poke Flute! ★[/bold yellow]")
            output.write(
                "[dim]   Use the Poke Flute to wake sleeping Pokemon — including Snorlax![/dim]"
            )
            output.write("")
        else:
            output.write("[cyan]   You've already received everything I can give.[/cyan]")
            output.write("[cyan]   Safe travels on your journey.[/cyan]")
            output.write("")
        return

    if story_flags.get("pokemon_tower_ghost_appeared"):
        output.write("[bold]Mr. Fuji:[/bold] [cyan]The ghost on the third floor...[/cyan]")
        output.write("[cyan]   It is a Marowak — the mother of a Cubone who lives here.[/cyan]")
        output.write("[cyan]   She cannot rest until those who wronged her are punished.[/cyan]")
        output.write("")
        output.write(
            "[dim]You feel a presence on the upper floors — something is waiting for you.[/dim]"
        )
        output.write("[dim]Type 'explore' to climb deeper into the tower.[/dim]")
        output.write("")
        return

    # First visit
    output.write("[bold]Mr. Fuji:[/bold] [cyan]Welcome to the Pokemon Tower.[/cyan]")
    output.write("[cyan]   This is a place of rest for Pokemon who have passed on.[/cyan]")
    output.write("[cyan]   Trainers come here to pay their respects.[/cyan]")
    output.write("")
    output.write("[bold]Mr. Fuji:[/bold] [cyan]But something is wrong...[/cyan]")
    output.write("[cyan]   A spirit on the upper floors has grown restless.[/cyan]")
    output.write("[cyan]   It fills the trainers here with sorrow and unease.[/cyan]")
    output.write("[cyan]   I pray someone brave will help calm it.[/cyan]")
    output.write("")
    output.write(
        "[dim]Channelers wander the upper floors, their eyes glazed over with grief.[/dim]"
    )
    output.write("[dim]Type 'explore' to climb the tower and face what awaits.[/dim]")

    story_flags["pokemon_tower_visited"] = True
    output.write("")


def enter_bike_shop(game_state: "GameState", output: RichLog) -> None:
    """
    Enter the Cerulean City Bike Shop.

    On the first visit the owner gives the player a free Bicycle.
    The Bicycle reduces wild encounter rate while riding on routes (future mechanic).

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
    """
    output.write("")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("[bold cyan]          🚲 CERULEAN BIKE SHOP 🚲        [/bold cyan]")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("")
    output.write("[bold]Owner:[/bold] [yellow]Welcome to the Cerulean Bike Shop![/yellow]")
    output.write("[yellow]   We carry the finest bikes in Kanto![/yellow]")
    output.write("")
    story_flags = game_state.game_data.setdefault("story_flags", {})
    if not story_flags.get("received_bicycle"):
        output.write(
            "[bold]Owner:[/bold] [yellow]Hey! You look like a real trainer on the go![/yellow]"
        )
        output.write("")
        output.write("[yellow]   As a one-time promotional gift, I'd like to give you[/yellow]")
        output.write("[yellow]   a [bold]Bicycle[/bold] — absolutely free![/yellow]")
        output.write("[yellow]   Just spread the word and tell your friends about us![/yellow]")
        output.write("")
        output.write("[yellow]   With a Bicycle you can zip through routes at high speed[/yellow]")
        output.write("[yellow]   and encounter fewer wild Pokemon while riding![/yellow]")
        output.write("")
        items = game_state.game_data.setdefault("items", {})
        items["Bicycle"] = 1
        story_flags["received_bicycle"] = True
        output.write("[bold green]✓ Received a Bicycle![/bold green]")
        output.write("   [dim]Use 'ride bike' or 'use bicycle' on a route to cycle faster![/dim]")
        output.write("   [dim](Halves wild encounter rate while cycling)[/dim]")
        output.write("")
    else:
        output.write("[bold]Owner:[/bold] [yellow]Still enjoying that bike we gave you?[/yellow]")
        output.write("[yellow]   Great! Nothing beats a Cerulean Bike![/yellow]")
        output.write("")
        output.write(
            "[bold yellow]🚲 Premium models on display (definitely not affordable):[/bold yellow]"
        )
        output.write("   • [cyan]Mach Bike[/cyan]  ₽1,000,000 — Blazing fast")
        output.write("   • [cyan]Acro Bike[/cyan]  ₽1,000,000 — Perfect for stunts")
        output.write("   [dim](One bike is definitely enough for your journey...)[/dim]")
        output.write("")
    output.write("[dim]You leave the Bike Shop[/dim]")
    output.write("")


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
    output.write("")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("[bold cyan]          🌉 NUGGET BRIDGE 🌉              [/bold cyan]")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("")
    if story_flags.get("nugget_bridge_complete"):
        output.write(
            "[bold]Bridge Patron:[/bold] [yellow]You're the champ who beat all five![/yellow]"
        )
        output.write("[yellow]   The bridge is open to you whenever you like![/yellow]")
        output.write("")
        output.write("[dim]You stroll across Nugget Bridge[/dim]")
        output.write("")
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
        output.write("[bold yellow]🏆 You defeated all five Nugget Bridge trainers![/bold yellow]")
        output.write("")
        output.write(
            "[bold]Bridge Patron:[/bold] [yellow]Astounding! You beat every single one![/yellow]"
        )
        output.write("[yellow]   As promised — here's your Nugget![/yellow]")
        output.write("[yellow]   You can sell it at any Pokemart for a whopping ₽5000![/yellow]")
        output.write("")
        output.write("[bold green]✓ Received a Nugget![/bold green]")
        output.write("   [dim](Worth ₽5000 — sell at any Pokemart)[/dim]")
        output.write("")
        output.write("[dim]You cross Nugget Bridge triumphantly![/dim]")
        output.write("")
        # ---- Rival battle after Nugget Bridge ----
        if not story_flags.get("rival_cerulean_beaten") and trigger_trainer_battle_callback:
            import copy

            from .data.trainer_data import TRAINERS as _NB_TRAINERS

            rival_trainer = copy.deepcopy(_NB_TRAINERS.get("rival_cerulean"))
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
                output.write("")
                output.write("[dim]As you claim the Nugget, a familiar voice calls out...[/dim]")
                output.write("")
                trigger_trainer_battle_callback(rival_trainer)
                return  # Battle takes over
        return
    if defeated_count == 0:
        output.write("[dim]A long bridge stretches north over the river...[/dim]")
        output.write("[dim]Five trainers line the path, staring you down![/dim]")
        output.write("")
        output.write("[bold]Trainer:[/bold] [yellow]Welcome to Nugget Bridge![/yellow]")
        output.write(
            "[yellow]   Defeat all five of us to claim the legendary Nugget prize![/yellow]"
        )
        output.write("")
    else:
        remaining = 5 - defeated_count
        output.write(f"[dim]Progress: {defeated_count}/5 bridge trainers defeated[/dim]")
        output.write(f"[dim]{remaining} trainer(s) remain on the bridge![/dim]")
        output.write("")
    # Find and trigger the next undefeated trainer
    next_trainer_id = next((t for t in nugget_trainers if t not in defeated), None)
    if next_trainer_id and trigger_trainer_battle_callback:
        from .data.trainer_data import TRAINERS as _TRAINERS

        trainer = _TRAINERS.get(next_trainer_id)
        if trainer:
            trigger_trainer_battle_callback(trainer)
            return
    output.write("[yellow]   Prepare your team, then step onto the bridge![/yellow]")
    output.write("[dim]You hesitate at the bridge entrance[/dim]")
    output.write("")


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


def perform_pokemon_center_heal(game_state: "GameState", output: RichLog) -> None:
    """
    Actually perform the Pokemon Center healing.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
    """
    pokemon = game_state.game_data.get("pokemon", [])

    # Record this as the last visited Pokemon Center
    current_location = game_state.current_location.name if game_state.current_location else None
    if current_location:
        game_state.game_data["last_pokemon_center"] = current_location

    output.write("")
    output.write("[magenta]   Let me heal your Pokemon...[/magenta]")
    output.write("")
    output.write("[cyan]   ♪ Healing sound ♪[/cyan]")
    output.write("")

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
                output.write(f"   [green]✓ {name} restored to full health and cured![/green]")
            else:
                output.write(f"   [green]✓ {name} restored to full health![/green]")
        else:
            output.write(f"   [green]✓ {p} restored to full health![/green]")

    output.write("")
    output.write("[bold]Nurse Joy:[/bold] [magenta]Your Pokemon are now fully healed![/magenta]")
    output.write("[magenta]   All HP, PP, and status conditions restored![/magenta]")
    output.write("[magenta]   Is there anything else I can do for you?[/magenta]")
    output.write("")


def perform_mom_heal(game_state: "GameState", output: RichLog) -> None:
    """
    Actually perform Mom's healing.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
    """
    pokemon = game_state.game_data.get("pokemon", [])

    output.write("")
    output.write("[bold]Mom:[/bold] [magenta]Let me take care of your Pokemon![/magenta]")
    output.write("")
    output.write("[cyan]   ♪ Mom's cooking and care ♪[/cyan]")
    output.write("")

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

    output.write("")
    output.write("[bold]Mom:[/bold] [magenta]There! All better! ❤️[/magenta]")
    output.write("[magenta]   Your Pokemon look so happy now![/magenta]")
    output.write("[magenta]   Come back anytime you need to rest![/magenta]")
    output.write("")
    output.write("[dim]You leave the house feeling grateful[/dim]")
    output.write("")


def enter_rivals_house(game_state: "GameState", output: RichLog) -> None:
    """
    Enter the rival's house.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
    """
    rival_name = game_state.game_data.get("rival_name", "Rival")
    output.write("")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write(
        f"[bold cyan]          🏠 {rival_name.upper()}'S HOUSE 🏠             [/bold cyan]"
    )
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("")

    # Check if player has Pokemon yet
    pokemon = game_state.game_data.get("pokemon", [])

    if not pokemon:
        output.write(
            f"[bold]{rival_name}'s Sister:[/bold] [yellow]Oh! You're going to see Professor Oak?[/yellow]"
        )
        output.write(f"[yellow]   {rival_name} already left. He's always so impatient![/yellow]")
    else:
        output.write(
            f"[bold]{rival_name}'s Sister:[/bold] [yellow]{rival_name} is on his Pokemon journey too![/yellow]"
        )
        output.write(
            "[yellow]   I hope you two can be good rivals and help each other grow![/yellow]"
        )

    output.write("")
    output.write("[dim]You leave the house[/dim]")
    output.write("")


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
    output.write("")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("[bold cyan]      🔬 PROFESSOR OAK'S LAB 🔬          [/bold cyan]")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("")

    # Check if player has Pokemon yet
    pokemon = game_state.game_data.get("pokemon", [])

    if not pokemon:
        # Check if Pikachu mode (Pokemon Yellow Easter egg)
        if game_state.pikachu_mode:
            output.write("[bold]Professor Oak:[/bold] [cyan]Oh! You're finally here![/cyan]")
            output.write("")
            output.write("[cyan]   I was about to head out looking for you![/cyan]")
            output.write(
                "[cyan]   I have a special Pokemon that's been waiting for a trainer...[/cyan]"
            )
            output.write("")
            output.write("[bold yellow]The last remaining Pokemon:[/bold yellow]")
            output.write("")
            output.write("  ⚡ [yellow]Pikachu[/yellow] - Electric type")
            output.write(
                "     [dim]An energetic Pokemon that refuses to stay in its Pokeball![/dim]"
            )
            output.write("")

            # Show button panel if callback provided
            if show_starter_panel_callback:
                output.write(
                    "[dim]Click the button or type 'Choose Pikachu' to begin your journey:[/dim]"
                )
                show_starter_panel_callback(game_state.pikachu_mode)
            else:
                output.write("[yellow]Type 'Choose Pikachu' to begin your journey:[/yellow]")

            output.write("")
        else:
            output.write("[bold]Professor Oak:[/bold] [cyan]Ah! Welcome to my laboratory![/cyan]")
            output.write("")
            output.write("[cyan]   I study Pokemon as my life's work![/cyan]")
            output.write("[cyan]   Now, it's time for you to choose your first Pokemon![/cyan]")
            output.write("")
            output.write("[bold yellow]Choose your starter Pokemon:[/bold yellow]")
            output.write("")
            output.write("  🌿 [green]Bulbasaur[/green] - Grass/Poison type")
            output.write("     [dim]A tough Pokemon with great defensive abilities[/dim]")
            output.write("")
            output.write("  🔥 [red]Charmander[/red] - Fire type")
            output.write("     [dim]A fiery Pokemon that will become a powerful dragon[/dim]")
            output.write("")
            output.write("  💧 [blue]Squirtle[/blue] - Water type")
            output.write("     [dim]A cool Pokemon with strong water attacks[/dim]")
            output.write("")

            # Show button panel if callback provided
            if show_starter_panel_callback:
                output.write(
                    "[dim]Click a button or type 'Choose' followed by the Pokemon name:[/dim]"
                )
                output.write("[dim]Example: Choose Bulbasaur[/dim]")
                show_starter_panel_callback(game_state.pikachu_mode)
            else:
                output.write("[yellow]Type 'Choose' followed by the Pokemon name:[/yellow]")
                output.write("[dim]Example: Choose Bulbasaur[/dim]")

            output.write("")

        # Set pending command
        set_pending_command_callback("choose_starter")
    else:
        output.write(
            "[bold]Professor Oak:[/bold] [cyan]Hello! How is your Pokedex coming along?[/cyan]"
        )
        output.write("")
        output.write("[cyan]   Remember, to make a complete guide of all Pokemon[/cyan]")
        output.write("[cyan]   in the world... That is my dream![/cyan]")
        output.write("")

        # Show research information
        output.write("[bold]Research Data:[/bold]")
        output.write("   • Pokemon seen: [dim]Coming soon[/dim]")
        output.write(f"   • Pokemon caught: [green]{len(pokemon)}[/green]")
        output.write("")

    output.write("[dim]You leave the laboratory[/dim]")
    output.write("")


def choose_starter_pokemon(
    game_state: "GameState", pokemon_name: str, output: RichLog, set_pending_command_callback
) -> None:
    """
    Choose a starter Pokemon.

    Args:
        game_state: The game state object
        pokemon_name: Name of the Pokemon to choose
        output: The RichLog widget to write to
        set_pending_command_callback: Callback to set pending command
    """
    from .engine import BattleState

    # Normalize the input
    choice = pokemon_name.lower().strip()

    # Check if it starts with "choose"
    if choice.startswith("choose "):
        choice = choice[7:].strip()

    # Check for Pikachu (Easter egg)
    if "pikachu" in choice:
        if not game_state.pikachu_mode:
            # Pikachu is not available in normal mode
            output.write("")
            output.write("[red]❌ Pikachu is not an available starter Pokemon![/red]")
            output.write("[dim]Please choose: Bulbasaur, Charmander, or Squirtle[/dim]")
            output.write("")
            set_pending_command_callback("choose_starter")
            return
        else:
            # Pikachu mode activated - give Pikachu
            # Generate full battle-ready Pikachu data
            _bs = BattleState()
            pikachu_data = _bs.generate_wild_pokemon("PIKACHU", 5)
            pikachu_data["no_evolve"] = True  # This Pikachu refuses to evolve!
            game_state.game_data["pokemon"].append(pikachu_data)
            # Rival gets Eevee in Pikachu mode
            game_state.game_data["rival_pokemon"] = ["Eevee (Lv. 5)"]

            output.write("")
            output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
            output.write("[bold yellow]⚡ You chose Pikachu! ⚡[/bold yellow]")
            output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
            output.write("")
            output.write("[bold]Professor Oak:[/bold] [cyan]Wonderful![/cyan]")
            output.write("")
            output.write(
                "[cyan]   Pikachu is very special - it loves to stay outside its Pokeball![/cyan]"
            )
            output.write("[cyan]   I'm sure you two will become great friends![/cyan]")
            output.write("")
            output.write("[green]✓ Pikachu (Lv. 5) was added to your party![/green]")
            output.write("[dim]   (This Pikachu refuses to evolve)[/dim]")
            output.write("")
            # Give starter Potions
            items = game_state.game_data.setdefault("items", {})
            items["Potion"] = items.get("Potion", 0) + 5
            output.write("[green]✓ Received 5 Potions![/green]")
            output.write("")
            output.write(
                "[bold]Professor Oak:[/bold] [cyan]By the way, your rival already took Eevee![/cyan]"
            )
            output.write("")

            # Trigger rival battle for Pikachu mode!
            import copy

            from .battle import battle_actions
            from .data.trainer_data import TRAINERS

            # Get the rival trainer template and customize it (Eevee for Pikachu mode)
            rival_trainer = copy.deepcopy(TRAINERS.get("rival_oaks_lab"))
            if rival_trainer:
                # Set the rival's Pokemon to Eevee for Pikachu mode
                rival_trainer.pokemon[0].species = "EEVEE"

                # Store that we've battled the rival in Oak's lab
                defeated_trainers = game_state.game_data.get("defeated_trainers", [])

                # Only battle if we haven't already defeated them here
                if "rival_oaks_lab" not in defeated_trainers:
                    output.write("[dim]As you turn to leave...[/dim]")
                    output.write("")
                    # Trigger the battle
                    battle_actions.trigger_trainer_encounter(
                        game_state, output, rival_trainer, set_pending_command_callback
                    )
                    return  # Battle takes over, function will be called again after battle

            # This part runs after the battle (or if battle was skipped)
            output.write("")
            output.write(
                "[bold]Professor Oak:[/bold] [cyan]Now you're ready to begin your Pokemon journey![/cyan]"
            )
            output.write(
                "[cyan]   Be sure to visit the Pokemon Center if your Pokemon get hurt![/cyan]"
            )
            output.write("")
            output.write("[dim]You leave the laboratory with your electric companion![/dim]")
            output.write("")
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
        output.write("")
        if game_state.pikachu_mode:
            output.write("[red]❌ That's not the right Pokemon![/red]")
            output.write("[dim]Please choose: Pikachu[/dim]")
        else:
            output.write("[red]❌ That's not one of the starter Pokemon![/red]")
            output.write("[dim]Please choose: Bulbasaur, Charmander, or Squirtle[/dim]")
        output.write("")
        # Set pending command again to wait for valid input
        set_pending_command_callback("choose_starter")
        return

    # Pikachu mode only allows Pikachu
    if game_state.pikachu_mode:
        output.write("")
        output.write("[red]❌ That Pokemon is not available![/red]")
        output.write("[dim]Please choose: Pikachu[/dim]")
        output.write("")
        set_pending_command_callback("choose_starter")
        return

    # Add Pokemon to party (normal mode)
    # Generate full battle-ready Pokemon data
    _bs = BattleState()
    starter_data = _bs.generate_wild_pokemon(selected_starter["name"].upper(), 5)
    starter_data["no_evolve"] = False
    game_state.game_data["pokemon"].append(starter_data)

    # Rival gets the Pokemon with type advantage
    rival_pokemon = selected_starter["rival"]
    game_state.game_data["rival_pokemon"] = [f"{rival_pokemon} (Lv. 5)"]

    # Show selection confirmation
    output.write("")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write(
        f"[bold green]{selected_starter['emoji']} You chose {selected_starter['name']}! {selected_starter['emoji']}[/bold green]"
    )
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("")
    output.write("[bold]Professor Oak:[/bold] [cyan]Excellent choice![/cyan]")
    output.write("")
    output.write(f"[cyan]   {selected_starter['name']} is a wonderful Pokemon![/cyan]")
    output.write("[cyan]   Treat it with love and kindness, and it will grow strong![/cyan]")
    output.write("")
    output.write(f"[green]✓ {selected_starter['name']} (Lv. 5) was added to your party![/green]")
    output.write("")
    # Give starter Potions
    items = game_state.game_data.setdefault("items", {})
    items["Potion"] = items.get("Potion", 0) + 5
    output.write("[green]✓ Received 5 Potions![/green]")
    output.write("")
    output.write(
        f"[bold]Professor Oak:[/bold] [cyan]Oh! Your rival already chose {rival_pokemon}![/cyan]"
    )
    output.write("[cyan]   It seems he wanted to have an advantage over you![/cyan]")
    output.write("")

    # Trigger rival battle!
    import copy

    from .battle import battle_actions
    from .data.trainer_data import TRAINERS

    # Get the rival trainer template and customize it
    rival_trainer = copy.deepcopy(TRAINERS.get("rival_oaks_lab"))
    if rival_trainer:
        # Set the rival's Pokemon to match what they chose
        rival_trainer.pokemon[0].species = rival_pokemon.upper()

        # Store that we've battled the rival in Oak's lab
        defeated_trainers = game_state.game_data.get("defeated_trainers", [])

        # Only battle if we haven't already defeated them here
        if "rival_oaks_lab" not in defeated_trainers:
            output.write("[dim]As you turn to leave...[/dim]")
            output.write("")
            # Trigger the battle
            battle_actions.trigger_trainer_encounter(
                game_state, output, rival_trainer, set_pending_command_callback
            )
            return  # Battle takes over, function will be called again after battle

    # This part runs after the battle (or if battle was skipped)
    output.write("")
    output.write(
        "[bold]Professor Oak:[/bold] [cyan]Now you're ready to begin your Pokemon journey![/cyan]"
    )
    output.write("[cyan]   Be sure to visit the Pokemon Center if your Pokemon get hurt![/cyan]")
    output.write("")
    output.write("[dim]You leave the laboratory with your new partner![/dim]")
    output.write("")


def enter_ss_anne_dock(game_state: "GameState", output: RichLog) -> None:
    """
    Enter the S.S. Anne Dock building in Vermillion City.

    Checks for the S.S. Anne Ticket and provides instructions on boarding the ship.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
    """
    output.write("")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("[bold cyan]           ⚓ S.S. ANNE DOCK ⚓            [/bold cyan]")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("")

    bag = game_state.game_data.get("items", {})
    story_flags = game_state.game_data.setdefault("story_flags", {})
    has_ticket = bag.get("S.S. Anne Ticket", 0) > 0
    already_boarded = story_flags.get("boarded_ss_anne", False)

    output.write(
        "[bold]Dock Worker:[/bold] [cyan]Welcome to the Vermillion Harbour S.S. Anne Dock![/cyan]"
    )
    output.write("")

    if has_ticket or already_boarded:
        output.write("[cyan]   I can see you have a ticket — the ship is ready to board![/cyan]")
        output.write("[cyan]   Head around to the gangplank and use 'Move to S.S. Anne'.[/cyan]")
        output.write("")
        output.write("[dim]   The S.S. Anne is filled with trainers from around the world.[/dim]")
        output.write(
            "[dim]   The captain's cabin is somewhere aboard — he may have a reward for you.[/dim]"
        )
    else:
        output.write("[cyan]   Sorry, I can't let you through without an S.S. Anne Ticket.[/cyan]")
        output.write("[cyan]   Have you spoken to Bill north of Cerulean City?[/cyan]")
        output.write("")
        output.write("[dim]   Bill hands out tickets to trainers he trusts.[/dim]")
        output.write("[dim]   Visit Bill's House on Route 24 to obtain an S.S. Anne Ticket.[/dim]")

    output.write("")


def enter_mr_fujis_house(game_state: "GameState", output: RichLog) -> None:
    """
    Enter Mr. Fuji's House in Lavender Town.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
    """
    output.write("")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("[bold cyan]        🏠 MR. FUJI'S HOUSE 🏠            [/bold cyan]")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("")

    story_flags = game_state.game_data.setdefault("story_flags", {})
    rescued = story_flags.get("rescued_mr_fuji", False)

    if rescued:
        bag = game_state.game_data.setdefault("items", {})
        output.write("[bold]Mr. Fuji:[/bold] [cyan]Ah, my young rescuer! Welcome back.[/cyan]")
        output.write("[cyan]   I hope the Poke Flute serves you well on your journey.[/cyan]")
        output.write("[cyan]   The Pokemon laid to rest in the tower deserve peace.[/cyan]")
        output.write("[cyan]   Thank you for driving out Team Rocket.[/cyan]")
        if not bag.get("Poke Flute"):
            # Give flute again if somehow lost
            bag["Poke Flute"] = 1
            output.write("")
            output.write("[bold yellow]★ Received Poke Flute! ★[/bold yellow]")
    else:
        output.write("[bold]Old Woman:[/bold] [cyan]Mr. Fuji isn't here...[/cyan]")
        output.write(
            "[cyan]   He went up to Pokemon Tower as always, but he hasn't returned.[/cyan]"
        )
        output.write("[cyan]   We're all very worried.[/cyan]")
        output.write("")
        output.write("[dim]   The Pokemon Tower looms just east of town.[/dim]")
        output.write("[dim]   If you're headed there, please see if Mr. Fuji is all right.[/dim]")

    output.write("")


def enter_game_corner(game_state: "GameState", output: RichLog) -> None:
    """
    Enter the Game Corner in Celadon City.

    Provides flavour text and hints about Team Rocket's hidden base.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
    """
    output.write("")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("[bold cyan]         🎰 CELADON GAME CORNER 🎰        [/bold cyan]")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("")

    story_flags = game_state.game_data.setdefault("story_flags", {})
    hideout_cleared = story_flags.get("defeated_giovanni_hideout", False)

    output.write("[bold]Attendant:[/bold] [yellow]Welcome to the Celadon Game Corner![/yellow]")
    output.write("[yellow]   Try your luck on the slot machines![/yellow]")
    output.write("")

    if hideout_cleared:
        output.write("[dim]   The suspicious poster on the back wall has been removed.[/dim]")
        output.write("[dim]   Team Rocket's presence here seems to have faded.[/dim]")
    else:
        output.write("[dim]   The machines chime and flash all around you.[/dim]")
        output.write("[dim]   A suspicious-looking poster adorns the back wall...[/dim]")
        output.write(
            "[dim]   Something feels off about this place — "
            "those men in black uniforms are everywhere.[/dim]"
        )
        output.write("")
        output.write(
            "[yellow]💡 Tip:[/yellow] [dim]Team Rocket's Hideout is accessible from Celadon City.[/dim]"
        )
        output.write("[dim]   Use 'Move to Team Rocket's Hideout' to investigate.[/dim]")

    output.write("")


def enter_department_store(game_state: "GameState", output: RichLog) -> None:
    """
    Enter the Celadon Department Store.

    Offers a wide selection of items for sale.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
    """
    output.write("")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("[bold cyan]     🏬 CELADON DEPARTMENT STORE 🏬        [/bold cyan]")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("")
    output.write("[bold]Clerk:[/bold] [yellow]Welcome to the Celadon Department Store![/yellow]")
    output.write("[yellow]   We have six floors of Pokemon goods![/yellow]")
    output.write("")
    output.write("[bold green]Available items (selection):[/bold green]")

    money = game_state.game_data.get("money", 0)
    output.write(f"   [bold]Your money:[/bold] [cyan]₽{money}[/cyan]")
    output.write("")

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

    output.write("")
    output.write("[dim]   This is a display only — use the Pokemart for purchases.[/dim]")
    output.write("[dim]   Tip: The Pokemart in Celadon stocks the full advanced catalogue.[/dim]")
    output.write("")


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
        output.write("[red]❌ Start a game first![/red]")
        return

    output.write("")
    output.write("[bold green]═══════════════════════════════════════════[/bold green]")
    output.write("[bold green]          🦁 SAFARI ZONE ENTRANCE 🦁       [/bold green]")
    output.write("[bold green]═══════════════════════════════════════════[/bold green]")
    output.write("")
    output.write("[bold]Warden:[/bold] [green]Welcome, Trainer![/green]")
    output.write("[green]   The Safari Zone is home to rare Pokemon found nowhere else![/green]")
    output.write("[green]   The admission fee is ₽500 for 30 Safari Balls.[/green]")
    output.write("")

    money = game_state.game_data.get("money", 0)
    if money < 500:
        output.write(
            "[red]Warden: You don't have enough money for admission (₽500 required).[/red]"
        )
        output.write("")
        return

    game_state.game_data["money"] = money - 500

    # Give 30 Safari Balls
    bag = game_state.game_data.get("bag", {})
    bag["Safari Ball"] = bag.get("Safari Ball", 0) + 30
    game_state.game_data["bag"] = bag

    # Move player into the Safari Zone
    from pytemon.locations import get_location

    safari_location = get_location("Safari Zone")
    if safari_location:
        game_state.previous_location = (
            game_state.current_location.name if game_state.current_location else "Fuchsia City"
        )
        game_state.current_location = safari_location

    output.write("[green]   You paid ₽500 and received [bold]30 Safari Balls[/bold]![/green]")
    output.write("")
    output.write("[bold]Safari Zone Rules:[/bold]")
    output.write("   🎯 [cyan]throw ball[/cyan]  — throw a Safari Ball directly")
    output.write("   🥩 [cyan]bait[/cyan]        — toss bait to make Pokemon easier to catch")
    output.write(
        "   🪨 [cyan]rock[/cyan]        — throw a rock to anger Pokemon (boosts catch rate briefly)"
    )
    output.write("   🏃 [cyan]run[/cyan]         — flee from the wild Pokemon")
    output.write("")
    output.write("[yellow]⚠️  You cannot battle wild Pokemon in the Safari Zone![/yellow]")
    output.write("[dim]   Explore to encounter wild Pokemon. You have 30 Safari Balls.[/dim]")
    output.write("")

    remaining = bag.get("Safari Ball", 0)
    output.write(f"[dim]Safari Balls remaining: {remaining}[/dim]")
    output.write("")


def enter_silph_co(
    game_state: "GameState",
    output: RichLog,
    trigger_trainer_battle_callback=None,
) -> None:
    """
    Enter Silph Co. headquarters in Saffron City.

    Team Rocket has seized the building. Fight through four enemy encounters
    (three Rocket Grunts plus the Rocket Executive) to clear the building and
    receive the Master Ball from the grateful president.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
        trigger_trainer_battle_callback: Optional callback for triggering trainer battles
    """
    story_flags = game_state.game_data.setdefault("story_flags", {})
    output.write("")
    output.write("[bold red]═══════════════════════════════════════════[/bold red]")
    output.write("[bold red]          🚀 SILPH CO. — SAFFRON CITY 🚀   [/bold red]")
    output.write("[bold red]═══════════════════════════════════════════[/bold red]")
    output.write("")

    if story_flags.get("silph_co_cleared"):
        output.write(
            "[bold]Silph Receptionist:[/bold] [cyan]Thanks to you, Silph Co. is safe![/cyan]"
        )
        output.write("[cyan]   The President extends his warmest gratitude.[/cyan]")
        output.write("[dim]   The lobby is peaceful once more.[/dim]")
        output.write("")
        return

    silph_trainers = [
        "rocket_grunt_silph_1",
        "rocket_grunt_silph_2",
        "rocket_grunt_silph_3",
        "silph_executive",
    ]
    defeated = game_state.game_data.get("defeated_trainers", [])
    defeated_count = sum(1 for t in silph_trainers if t in defeated)

    if defeated_count >= 4:
        # All enemies just defeated — clear the building and award the Master Ball
        story_flags["silph_co_cleared"] = True
        story_flags["received_master_ball"] = True
        story_flags["rescued_mr_fuji_silph"] = True

        items = game_state.game_data.setdefault("items", {})
        items["Master Ball"] = items.get("Master Ball", 0) + 1

        output.write("[bold yellow]🏆 Team Rocket has been driven out of Silph Co.![/bold yellow]")
        output.write("")
        output.write("[bold]Silph Co. President:[/bold] [cyan]You've saved us![/cyan]")
        output.write("[cyan]   I can't thank you enough.[/cyan]")
        output.write("[cyan]   Please — take the Master Ball, our greatest creation.[/cyan]")
        output.write("[cyan]   It catches any wild Pokemon without fail.[/cyan]")
        output.write("")
        output.write("[bold green]✓ Received a Master Ball![/bold green]")
        output.write("   [dim](Catches any wild Pokemon without fail — one-time use)[/dim]")
        output.write("")
        return

    if defeated_count == 0:
        output.write("[dim]Team Rocket grunts patrol every floor...[/dim]")
        output.write("[dim]The building is locked down and employees cower at their desks![/dim]")
        output.write("")
        output.write("[bold]Employee:[/bold] [yellow]Please! You have to help us![/yellow]")
        output.write("[yellow]   Team Rocket has taken over the whole building![/yellow]")
        output.write("[yellow]   The president is trapped on the top floor![/yellow]")
        output.write("")
    else:
        remaining = 4 - defeated_count
        output.write(f"[dim]Progress: {defeated_count}/4 Rocket members defeated[/dim]")
        output.write(f"[dim]{remaining} member(s) still patrolling the floors![/dim]")
        output.write("")

    # Find and trigger the next undefeated trainer
    next_trainer_id = next((t for t in silph_trainers if t not in defeated), None)
    if next_trainer_id and trigger_trainer_battle_callback:
        from .data.trainer_data import TRAINERS as _SILPH_TRAINERS

        trainer = _SILPH_TRAINERS.get(next_trainer_id)
        if trainer:
            trigger_trainer_battle_callback(trainer)
            return

    output.write("[yellow]   Prepare your team, then head inside![/yellow]")
    output.write("[dim]The automatic doors slide open with a hiss[/dim]")
    output.write("")


def enter_pokemon_mansion(
    game_state: "GameState",
    output: RichLog,
    trigger_trainer_battle_callback=None,
) -> None:
    """
    Enter the Pokemon Mansion on Cinnabar Island.

    Two rogue scientists guard the crumbling mansion. Defeat them to progress
    deeper inside and find the Secret Key needed to unlock Blaine's Gym.
    Scattered research notes hint at the origin of the legendary Pokemon Mewtwo.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
        trigger_trainer_battle_callback: Optional callback for triggering trainer battles
    """
    story_flags = game_state.game_data.setdefault("story_flags", {})
    output.write("")
    output.write("[bold yellow]═══════════════════════════════════════════[/bold yellow]")
    output.write("[bold yellow]         🔥 POKEMON MANSION 🔥             [/bold yellow]")
    output.write("[bold yellow]═══════════════════════════════════════════[/bold yellow]")
    output.write("")

    if story_flags.get("secret_key_found"):
        output.write("[dim]The burnt-out mansion creaks in the sea wind.[/dim]")
        output.write("[dim]You already have the Secret Key — nothing left to find here.[/dim]")
        output.write("")
        return

    mansion_trainers = [
        "scientist_mansion_1",
        "scientist_mansion_2",
    ]
    defeated = game_state.game_data.get("defeated_trainers", [])
    defeated_count = sum(1 for t in mansion_trainers if t in defeated)

    if defeated_count >= 2:
        # Both scientists defeated — award the Secret Key
        story_flags["secret_key_found"] = True
        items = game_state.game_data.setdefault("items", {})
        items["Secret Key"] = items.get("Secret Key", 0) + 1

        output.write("[bold yellow]🗝️  You found the Secret Key![/bold yellow]")
        output.write("")
        output.write(
            "[dim]Hidden behind a cracked wall panel, you discover a burnished key...[/dim]"
        )
        output.write("")
        output.write("[bold]Research Journal Entry — Dr. Fuji:[/bold]")
        output.write(
            "[italic dim]   Feb 6 — Mewtwo is far too powerful. We have failed to control it.[/italic dim]"
        )
        output.write(
            "[italic dim]   It destroyed the laboratory and fled. God forgive us.[/italic dim]"
        )
        output.write("")
        output.write("[bold green]✓ Received the Secret Key![/bold green]")
        output.write("   [dim](Unlocks the Cinnabar Island Gym)[/dim]")
        output.write("")
        return

    if defeated_count == 0:
        output.write(
            "[dim]The mansion has been abandoned for years — but not entirely empty...[/dim]"
        )
        output.write(
            "[dim]Wild Magmar stalk the charred halls, and rogue scientists lurk inside.[/dim]"
        )
        output.write("")
        output.write(
            "[bold]Faded Sign:[/bold] [yellow]CINNABAR POKEMON LAB ANNEX — AUTHORIZED PERSONNEL ONLY[/yellow]"
        )
        output.write("[dim]   Scrawled below: 'Don't look for the Mewtwo files.'[/dim]")
        output.write("")
    else:
        output.write("[dim]Progress: 1/2 scientists defeated[/dim]")
        output.write("[dim]The Secret Key must be somewhere deeper inside...[/dim]")
        output.write("")

    # Find and trigger the next undefeated scientist
    next_trainer_id = next((t for t in mansion_trainers if t not in defeated), None)
    if next_trainer_id and trigger_trainer_battle_callback:
        from .data.trainer_data import TRAINERS as _MANSION_TRAINERS

        trainer = _MANSION_TRAINERS.get(next_trainer_id)
        if trainer:
            trigger_trainer_battle_callback(trainer)
            return

    output.write("[yellow]   Something crashes on the upper floors...[/yellow]")
    output.write("[dim]You step cautiously into the ruined mansion[/dim]")
    output.write("")


def enter_pokemon_lab(
    game_state: "GameState",
    output: RichLog,
) -> None:
    """
    Enter the Pokemon Lab on Cinnabar Island.

    Scientists here can revive ancient Pokemon from fossils. Bring a Dome Fossil
    to receive a Kabuto, or a Helix Fossil for an Omanyte.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
    """
    story_flags = game_state.game_data.setdefault("story_flags", {})
    output.write("")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("[bold cyan]         🔬 CINNABAR POKEMON LAB 🔬        [/bold cyan]")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("")
    output.write(
        "[bold]Lab Researcher:[/bold] [cyan]Welcome! This is the famous Cinnabar Pokemon Lab.[/cyan]"
    )
    output.write("[cyan]   We specialise in restoring Pokemon from ancient fossils.[/cyan]")
    output.write("[cyan]   If you have a Dome Fossil or Helix Fossil, we can help![/cyan]")
    output.write("")

    bag = game_state.game_data.get("bag", {})
    has_dome = bag.get("Dome Fossil", 0) > 0
    has_helix = bag.get("Helix Fossil", 0) > 0

    if not has_dome and not has_helix:
        output.write("[dim]   You don't have any fossils to revive right now.[/dim]")
        output.write("[dim]   (Fossils can be found in Mt. Moon)[/dim]")
        output.write("")
        return

    from .engine.battle_engine import BattleState as _BattleState

    party = game_state.game_data.get("pokemon", [])

    if has_dome and not story_flags.get("revived_dome_fossil"):
        # Remove fossil from bag
        bag["Dome Fossil"] -= 1
        if bag["Dome Fossil"] <= 0:
            del bag["Dome Fossil"]
        game_state.game_data["bag"] = bag

        story_flags["revived_dome_fossil"] = True
        story_flags["fossil_revived"] = True

        # Revive Kabuto at level 5
        _bs_instance = _BattleState()
        kabuto = _bs_instance.generate_wild_pokemon("KABUTO", 5)
        kabuto["no_evolve"] = False

        if len(party) < 6:
            party.append(kabuto)
            game_state.game_data["pokemon"] = party
            output.write("[bold yellow]⏳ The scientists get to work...[/bold yellow]")
            output.write("[dim]   Hours pass as they extract DNA from the fossil...[/dim]")
            output.write("")
            output.write(
                "[bold green]✓ The Dome Fossil was restored to Kabuto (Lv. 5)![/bold green]"
            )
            output.write("   [cyan]Kabuto joined your party![/cyan]")
        else:
            from .pc_system import send_to_pc

            send_to_pc(game_state, kabuto)
            output.write("[bold yellow]⏳ The scientists get to work...[/bold yellow]")
            output.write("[dim]   Hours pass as they extract DNA from the fossil...[/dim]")
            output.write("")
            output.write(
                "[bold green]✓ The Dome Fossil was restored to Kabuto (Lv. 5)![/bold green]"
            )
            output.write("   [yellow]Your party is full — Kabuto was sent to Bill's PC![/yellow]")
        output.write("")

    if has_helix and not story_flags.get("revived_helix_fossil"):
        # Remove fossil from bag
        bag["Helix Fossil"] -= 1
        if bag["Helix Fossil"] <= 0:
            del bag["Helix Fossil"]
        game_state.game_data["bag"] = bag

        story_flags["revived_helix_fossil"] = True
        story_flags["fossil_revived"] = True

        # Revive Omanyte at level 5
        _bs_instance2 = _BattleState()
        omanyte = _bs_instance2.generate_wild_pokemon("OMANYTE", 5)
        omanyte["no_evolve"] = False

        party = game_state.game_data.get("pokemon", [])
        if len(party) < 6:
            party.append(omanyte)
            game_state.game_data["pokemon"] = party
            output.write("[bold yellow]⏳ The scientists get to work...[/bold yellow]")
            output.write("[dim]   Hours pass as they extract DNA from the fossil...[/dim]")
            output.write("")
            output.write(
                "[bold green]✓ The Helix Fossil was restored to Omanyte (Lv. 5)![/bold green]"
            )
            output.write("   [cyan]Omanyte joined your party![/cyan]")
        else:
            from .pc_system import send_to_pc

            send_to_pc(game_state, omanyte)
            output.write("[bold yellow]⏳ The scientists get to work...[/bold yellow]")
            output.write("[dim]   Hours pass as they extract DNA from the fossil...[/dim]")
            output.write("")
            output.write(
                "[bold green]✓ The Helix Fossil was restored to Omanyte (Lv. 5)![/bold green]"
            )
            output.write("   [yellow]Your party is full — Omanyte was sent to Bill's PC![/yellow]")
        output.write("")

    if (has_dome and story_flags.get("revived_dome_fossil")) or (
        has_helix and story_flags.get("revived_helix_fossil")
    ):
        if not has_dome and not has_helix:
            pass  # already revived, no message needed
        else:
            output.write("[dim]Researcher: You've already revived the fossils you brought![/dim]")
            output.write("")


def enter_pokemon_league_reception(
    game_state: "GameState",
    output: RichLog,
) -> None:
    """
    Enter the Pokemon League Reception at Indigo Plateau.

    Displays league rules, Elite Four challenge order and the player's current
    progress through the gauntlet.  No battle or story flag changes here — it
    is purely informational.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
    """
    story_flags = game_state.game_data.setdefault("story_flags", {})

    output.write("")
    output.write(
        "[bold yellow]═══════════════════════════════════════════════════════[/bold yellow]"
    )
    output.write("[bold yellow]   🏆  INDIGO PLATEAU — THE POKÉMON LEAGUE  🏆   [/bold yellow]")
    output.write(
        "[bold yellow]═══════════════════════════════════════════════════════[/bold yellow]"
    )
    output.write("")
    output.write("[bold]Receptionist:[/bold] [cyan]Welcome, Trainer, to the Pokémon League![/cyan]")
    output.write("[cyan]   Only those who carry all eight Gym Badges may challenge[/cyan]")
    output.write("[cyan]   the Elite Four.  Beyond them awaits the reigning Champion.[/cyan]")
    output.write("")
    output.write("[bold yellow]📜 RULES OF THE POKÉMON LEAGUE[/bold yellow]")
    output.write("   Defeat all four Elite Four members in order, then face the Champion:")
    output.write("   [bold]1.[/bold] Lorelei  — Ice & Water specialist")
    output.write("   [bold]2.[/bold] Bruno    — Fighting & Rock specialist")
    output.write("   [bold]3.[/bold] Agatha   — Ghost & Poison specialist")
    output.write("   [bold]4.[/bold] Lance    — Dragon master")
    output.write("   [bold]5.[/bold] Champion — The current Champion awaits beyond")
    output.write("")

    # Show Elute Four progress
    elite_order = [
        ("defeated_lorelei", "Lorelei", "❄️"),
        ("defeated_bruno", "Bruno", "💪"),
        ("defeated_agatha", "Agatha", "👻"),
        ("defeated_lance", "Lance", "🐉"),
        ("defeated_champion", "Champion", "🏆"),
    ]
    output.write("[bold]Your Progress:[/bold]")
    next_found = False
    for flag, name, emoji in elite_order:
        if story_flags.get(flag):
            output.write(f"   [green]✓ {emoji} {name} — defeated[/green]")
        elif not next_found:
            next_found = True
            output.write(f"   [yellow]→ {emoji} {name} — NEXT CHALLENGER[/yellow]")
        else:
            output.write(f"   [dim]○ {emoji} {name}[/dim]")
    output.write("")

    if story_flags.get("defeated_champion"):
        output.write("[bold green]🏆 You are the Pokémon League Champion! 🏆[/bold green]")
        output.write("[dim]   Visit the Hall of Fame to relive your legend.[/dim]")
    else:
        output.write("[bold cyan]🏥 HEALING SERVICES[/bold cyan]")
        output.write("   [cyan]A nurse at the counter can restore your Pokemon before[/cyan]")
        output.write("   [cyan]you enter the Elite Four chambers.[/cyan]")
        output.write("   [dim](Enter the Pokemon Center here on the Plateau to heal.)[/dim]")
        output.write("")
        output.write("[bold]Receptionist:[/bold] [cyan]That wall over there holds the names[/cyan]")
        output.write("[cyan]   of every Trainer who has bested the Elite Four.[/cyan]")
        output.write("[cyan]   Will your name be added today?[/cyan]")
    output.write("")
    output.write("[dim]You leave the reception hall[/dim]")
    output.write("")


def enter_elite_four(
    game_state: "GameState",
    output: RichLog,
    trigger_trainer_battle_callback,
) -> None:
    """
    Enter the Elite Four chambers and trigger the next battle in the gauntlet.

    Enforces the 8-badge gate and conscious-party check before starting.
    Determines which opponent (Lorelei → Bruno → Agatha → Lance → Champion Gary)
    is next based on story flags.  Calls trigger_trainer_battle_callback with the
    next Trainer object — the victory flag is set by handle_elite_four_victory()
    after the battle ends.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
        trigger_trainer_battle_callback: Callback(trainer) that starts a trainer battle
    """
    from .gym_system import get_badge_count

    story_flags = game_state.game_data.setdefault("story_flags", {})

    output.write("")
    output.write("[bold yellow]═══════════════════════════════════════════[/bold yellow]")
    output.write("[bold yellow]       ⚔️  ELITE FOUR CHAMBERS ⚔️         [/bold yellow]")
    output.write("[bold yellow]═══════════════════════════════════════════[/bold yellow]")
    output.write("")

    # Already Champion — show celebration and return
    if story_flags.get("defeated_champion"):
        output.write("[bold green]🏆 You are the Pokémon Champion! 🏆[/bold green]")
        output.write("[green]Your name is written in the Hall of Fame forever.[/green]")
        output.write("[green]The Pokédex awaits completion — your legend begins here.[/green]")
        output.write("")
        return

    # Gate 1: need all 8 badges
    badge_count = get_badge_count(game_state)
    cheat_mode = getattr(game_state, "cheat_mode", False)
    if badge_count < 8 and not cheat_mode:
        output.write("[yellow]⚠ You need all 8 Gym Badges to challenge the Elite Four![/yellow]")
        output.write(f"[dim]   You have {badge_count}/8 badges.[/dim]")
        output.write("[dim]   Travel Kanto and defeat all 8 Gym Leaders first.[/dim]")
        output.write("")
        output.write("[dim]The guard at the door turns you away.[/dim]")
        output.write("")
        return

    # Gate 2: party must have at least one conscious Pokemon
    pokemon = game_state.game_data.get("pokemon", [])
    alive = [p for p in pokemon if not isinstance(p, str) and p.get("hp", 0) > 0]
    if not alive:
        output.write("[yellow]⚠ All your Pokemon have fainted![/yellow]")
        output.write("[dim]   Heal at the Pokemon Center before entering the Elite Four.[/dim]")
        output.write("")
        return

    # Determine next opponent in order
    elite_order = [
        ("defeated_lorelei", "elite_lorelei", "Lorelei", "❄️", "Ice specialist"),
        ("defeated_bruno", "elite_bruno", "Bruno", "💪", "Fighting specialist"),
        ("defeated_agatha", "elite_agatha", "Agatha", "👻", "Ghost specialist"),
        ("defeated_lance", "elite_lance", "Lance", "🐉", "Dragon master"),
    ]
    next_trainer_id = None
    next_description = None
    for flag, tid, name, emoji, specialty in elite_order:
        if not story_flags.get(flag):
            next_trainer_id = tid
            next_description = f"{emoji} {name} — {specialty}"
            break

    # All four Elite Four defeated → face Champion Gary
    if next_trainer_id is None:
        starter = game_state.game_data.get("starter", "").upper()
        if starter == "BULBASAUR":
            next_trainer_id = "champion_gary_bulbasaur"
        elif starter == "SQUIRTLE":
            next_trainer_id = "champion_gary_squirtle"
        else:
            next_trainer_id = "champion_gary_charmander"
        rival_name = game_state.game_data.get("rival_name", "Gary")
        next_description = f"🏆 Champion {rival_name}"

    output.write(f"[bold]Next challenger: [yellow]{next_description}[/yellow][/bold]")
    output.write("")
    output.write("[dim]The heavy doors swing open.  The air is still.[/dim]")
    output.write("[dim]Every step echoes in the vast chamber...[/dim]")
    output.write("")

    if not trigger_trainer_battle_callback:
        output.write("[yellow]⚠ Battle system not available in this context[/yellow]")
        output.write("")
        return

    from .data.trainer_data import TRAINERS as _E4_TRAINERS

    trainer = _E4_TRAINERS.get(next_trainer_id)
    if trainer:
        trigger_trainer_battle_callback(trainer)
    else:
        output.write(f"[red]❌ Error: Trainer '{next_trainer_id}' not found[/red]")
        output.write("")


def enter_hall_of_fame(
    game_state: "GameState",
    output: RichLog,
) -> None:
    """
    Enter the Hall of Fame at the Pokemon League.

    If the player has not yet defeated the Champion the door is locked.
    Champions see a Rich-formatted record of their name, title, and the party
    snapshot saved when they first became Champion.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
    """
    story_flags = game_state.game_data.setdefault("story_flags", {})

    output.write("")
    output.write("[bold yellow]═══════════════════════════════════════════[/bold yellow]")
    output.write("[bold yellow]              🏆 HALL OF FAME 🏆           [/bold yellow]")
    output.write("[bold yellow]═══════════════════════════════════════════[/bold yellow]")
    output.write("")

    if not story_flags.get("defeated_champion"):
        output.write("[yellow]⚠ The Hall of Fame is reserved for Champions.[/yellow]")
        output.write("[dim]   Defeat the Elite Four and Champion first.[/dim]")
        output.write("")
        output.write("[dim]The doors remain sealed.  Your legend is still unwritten.[/dim]")
        output.write("")
        return

    player_name = game_state.game_data.get("player_name", "Trainer")
    output.write(f"[bold green]Champion: {player_name}[/bold green]")
    output.write("[bold yellow]✨ Pokémon League Champion ✨[/bold yellow]")
    output.write("")

    hall_party = story_flags.get("hall_of_fame_party", [])
    if hall_party:
        output.write("[bold]Champion's Party:[/bold]")
        for p in hall_party:
            output.write(f"   ⭐ [cyan]{p['name']}[/cyan]  Lv. {p['level']}")
        output.write("")

    output.write("[bold green]Your name is immortalised in the Hall of Fame![/bold green]")
    output.write("[dim]Trainers from across Kanto will remember your triumph forever.[/dim]")
    output.write("")
    output.write("[dim]You gaze at the golden plaque bearing your name...[/dim]")
    output.write("")


def handle_elite_four_victory(
    game_state: "GameState",
    trainer_id: str,
    output: RichLog,
) -> None:
    """
    Handle post-battle victory against an Elite Four member or Champion.

    Sets the appropriate story flag for the defeated trainer.  For the Champion,
    also sets is_champion, saves a Hall of Fame party snapshot, and displays the
    full championship celebration text.

    Args:
        game_state: The game state object
        trainer_id: ID of the defeated trainer
        output: The RichLog widget to write to
    """
    story_flags = game_state.game_data.setdefault("story_flags", {})

    elite_flag_map = {
        "elite_lorelei": "defeated_lorelei",
        "elite_bruno": "defeated_bruno",
        "elite_agatha": "defeated_agatha",
        "elite_lance": "defeated_lance",
    }
    champion_ids = {
        "champion_gary_bulbasaur",
        "champion_gary_charmander",
        "champion_gary_squirtle",
    }

    if trainer_id in elite_flag_map:
        flag = elite_flag_map[trainer_id]
        story_flags[flag] = True
        output.write("[bold]You won the battle![/bold]")
        output.write("")
        output.write("[dim]The next chamber awaits...[/dim]")
        output.write("")
    elif trainer_id in champion_ids:
        story_flags["defeated_champion"] = True
        story_flags["is_champion"] = True
        # Save party snapshot for the Hall of Fame
        pokemon = game_state.game_data.get("pokemon", [])
        story_flags["hall_of_fame_party"] = [
            {"name": p["name"], "level": p.get("level", 1)}
            for p in pokemon
            if not isinstance(p, str)
        ]
        player_name = game_state.game_data.get("player_name", "Trainer")
        output.write("")
        output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
        output.write("[bold yellow]★ ★ ★  CONGRATULATIONS!  ★ ★ ★[/bold yellow]")
        output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
        output.write("")
        output.write(f"[bold green]{player_name} is the new Pokémon League Champion![/bold green]")
        output.write("")
        output.write("[bold green]🏆 You are the Pokémon Champion! 🏆[/bold green]")
        output.write("[green]Your name is written in the Hall of Fame forever.[/green]")
        output.write("[green]The Pokédex awaits completion — your legend begins here.[/green]")
        output.write("")
        output.write("[dim]Visit the Hall of Fame to see your eternal record.[/dim]")
        output.write("")
    else:
        output.write("[bold]You won the battle![/bold]")
        output.write("")
