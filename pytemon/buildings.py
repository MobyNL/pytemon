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
