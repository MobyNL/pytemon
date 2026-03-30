"""
Building and exploration mixin for PokemonTerminal.

Handles all in-game location/building entry, the Pokemart shop loop,
Pokemon Center and Mom healing flows, and exploration delegates.
"""

import random
from typing import TYPE_CHECKING

from textual.widgets import Input, RichLog

from .. import buildings, exploration, gym_system, pc_system
from ..locations import get_location as _get_location
from ..texts.en import building_mixin as T  # noqa: N812
from .formatters import write_lines, write_lines_fmt

if TYPE_CHECKING:
    pass  # Avoid circular imports — self is always a PokemonTerminal at runtime


class BuildingMixin:
    """Mixin providing buildings, shop, location movement, and name selection."""

    def _set_active_building_context(self, building_name: str) -> None:
        """Set the active building label used by the top subtitle banner."""
        self.game_state.game_data["_active_building"] = building_name

    def _clear_active_building_context(self) -> None:
        """Clear active building subtitle context when back outside."""
        self.game_state.game_data.pop("_active_building", None)

    # ── Exploration / movement ───────────────────────────────────────────────

    def move_to_location(self, destination: str, output: RichLog) -> None:
        """Move to a new location (delegates to exploration module)."""
        self._clear_active_building_context()
        exploration.move_to_location(
            self.game_state, destination, output, self.show_location_arrival
        )

    def prompt_for_location(self, output: RichLog) -> None:
        """Prompt for location (delegates to exploration module)."""
        exploration.prompt_for_location(
            self.game_state,
            output,
            lambda cmd: setattr(self, "pending_command", cmd),
            show_panel_callback=self.show_location_selection_panel,
        )

    def prompt_for_building(self, output: RichLog) -> None:
        """Prompt for building (delegates to exploration module)."""
        exploration.prompt_for_building(
            self.game_state,
            output,
            lambda cmd: setattr(self, "pending_command", cmd),
            show_panel_callback=self.show_building_selection_panel,
        )

    def show_location_arrival(self, output: RichLog, is_load: bool = False) -> None:
        """Display location arrival (delegates to exploration module)."""
        self._clear_active_building_context()
        exploration.show_location_arrival(self.game_state, output, is_load)

    def look_around(self, output: RichLog, auto: bool = False) -> None:
        """Look around (delegates to exploration module)."""
        self._clear_active_building_context()
        exploration.look_around(self.game_state, output, auto)

    def explore_area(self, output: RichLog) -> None:
        """Explore area (delegates to exploration module)."""
        exploration.explore_area(
            self.game_state, output, self.trigger_wild_encounter, self.trigger_trainer_encounter
        )

    # ── Healing confirmation (Pokemon Center & Mom) ──────────────────────────

    def _heal_at_pokemon_center(self, output: RichLog) -> None:
        """Heal party at the Pokemon Center, animating output when available."""

        def _after_heal() -> None:
            hide_loading = getattr(self, "hide_pokemon_center_loading", None)
            if callable(hide_loading):
                hide_loading()
            self._return_to_pokemon_center(output)

        show_loading = getattr(self, "show_pokemon_center_loading", None)
        if callable(show_loading):
            show_loading()

        self.pending_command = "pokemon_center_healing"

        animator = getattr(self, "text_animator", None)
        if animator:
            buildings.perform_pokemon_center_heal(
                self.game_state,
                output,
                line_writer=lambda out, lines: animator.write_medium(
                    out, lines, on_complete=_after_heal
                ),
            )
            return

        buildings.perform_pokemon_center_heal(self.game_state, output)
        _after_heal()

    def handle_heal_center_confirmation(self, response: str, output: RichLog) -> None:
        """Handle Pokemon Center healing confirmation."""
        response_lower = response.lower().strip()
        if response_lower in ("yes", "y", "heal"):
            self._heal_at_pokemon_center(output)
        elif response_lower in ("no", "n", "leave", "exit"):
            self._clear_active_building_context()
            self.hide_all_panels()
            write_lines(output, T.HEAL_CENTER_DECLINED)
        else:
            write_lines(output, T.INVALID_RESPONSE_YES_NO)
            self.pending_command = "confirm_heal_center"

    def handle_heal_mom_confirmation(self, response: str, output: RichLog) -> None:
        """Handle Mom's healing confirmation."""
        response_lower = response.lower().strip()
        if response_lower in ("yes", "y", "rest", "heal"):
            buildings.perform_mom_heal(self.game_state, output)
        elif response_lower in ("no", "n", "leave"):
            self._clear_active_building_context()
            self.hide_all_panels()
            write_lines(output, T.HEAL_MOM_DECLINED)
        else:
            write_lines(output, T.INVALID_RESPONSE_YES_NO)
            self.pending_command = "confirm_heal_mom"
        output.write("")

    # ── Pokemon Center ───────────────────────────────────────────────────────

    def set_pending_and_show_heal_panel(self, cmd: str) -> None:
        """Set pending command and show the appropriate healing panel."""
        self.pending_command = cmd
        if cmd == "pokemon_center":
            self._set_active_building_context("Pokemon Center")
            self.show_pokemon_center_panel()
        elif cmd == "confirm_heal_mom":
            self._set_active_building_context("Player's House")
            self.show_nurse_joy_panel("Would you like me to make them feel better?", "mom")

    def _return_to_pokemon_center(self, output: RichLog) -> None:
        """Return to the Pokemon Center lobby after healing or using the PC."""
        self._set_active_building_context("Pokemon Center")
        self.pending_command = "pokemon_center"
        self.show_pokemon_center_panel()

    def _open_pc_from_center(self, output: RichLog) -> None:
        """Open Bill's PC from inside the Pokemon Center."""
        self._set_active_building_context("Bill's PC")
        pc_system.show_pc_menu(self.game_state, output)
        self.hide_all_panels()
        self.show_pc_main_panel()

    def _handle_pokemon_center_command(self, user_input: str, output: RichLog) -> None:
        """Handle text commands while in the Pokemon Center lobby."""
        cmd = user_input.lower().strip()
        if cmd in ("heal", "heal pokemon", "yes"):
            self._heal_at_pokemon_center(output)
        elif cmd in ("pc", "use pc", "computer", "bill", "bill's pc"):
            self._open_pc_from_center(output)
        elif cmd in ("leave", "exit", "bye", "back", "no"):
            self._clear_active_building_context()
            self.hide_all_panels()
            write_lines(output, T.POKEMON_CENTER_LEAVE)
        else:
            write_lines(output, T.POKEMON_CENTER_UNKNOWN_COMMAND)
            self._return_to_pokemon_center(output)

    # ── Building entry ───────────────────────────────────────────────────────

    def enter_building(self, building_name: str, output: RichLog) -> None:
        """Enter a building (delegates to buildings module)."""
        buildings.enter_building(
            self.game_state,
            building_name,
            output,
            lambda cmd: self.set_pending_and_show_heal_panel(cmd),
            self.show_starter_selection_panel,
            lambda trainer: self.trigger_trainer_encounter(output, trainer),
            self.show_pokemart_panel,
            show_gym_panel_callback=self.show_gym_panel,
        )
        if self.pending_command is None:
            self._clear_active_building_context()
        self._refresh_subtitle()

    def enter_pokemon_center(self, output: RichLog) -> None:
        """Enter Pokemon Center (delegates to buildings module)."""
        buildings.enter_pokemon_center(self.game_state, output)

    # ── Gym lobby helpers ────────────────────────────────────────────────────

    def _gym_challenge_leader(self, output: RichLog) -> None:
        """Challenge the gym leader at the current location."""
        if not self.game_state.current_location:
            output.write("[red]❌ No current location[/red]")
            return
        location_name = self.game_state.current_location.name
        gym_data = gym_system.get_gym_data(location_name)
        if not gym_data:
            output.write("[yellow]⚠ No gym at this location[/yellow]")
            return

        can_challenge, reason = gym_system.can_challenge_gym(self.game_state, location_name)
        if not can_challenge:
            output.write(f"[yellow]⚠ {reason}[/yellow]")
            output.write("")
            self.show_gym_panel()
            return

        leader_id = gym_data["leader_id"]
        badge_data = gym_system.get_badge_data(gym_data["badge"])
        badge_color = badge_data["color"] if badge_data else "orange3"
        output.write("")
        output.write(
            f"[bold {badge_color}]⚔️  Stepping forward to face the Gym Leader...[/bold {badge_color}]"
        )
        output.write("")
        # Leader battle — no in_gym_lobby flag so end_battle returns to exploration
        self.trigger_gym_battle(leader_id, output, is_gym_battle=True)

    def _gym_fight_trainer(self, output: RichLog) -> None:
        """Challenge the next gym trainer at the current location."""
        if not self.game_state.current_location:
            output.write("[red]❌ No current location[/red]")
            return
        location_name = self.game_state.current_location.name
        next_trainer_id = gym_system.get_next_gym_trainer(self.game_state, location_name)
        if not next_trainer_id:
            output.write("[yellow]✓ No more gym trainers to fight![/yellow]")
            output.write("")
            self.show_gym_panel()
            return

        # Flag this as an in-gym trainer battle so end_battle re-opens the gym lobby
        self.pending_command_data["in_gym_lobby"] = True
        self.pending_command_data["gym_location"] = location_name
        self.trigger_gym_battle(next_trainer_id, output, is_gym_battle=False)

    def enter_pokemart(self, output: RichLog) -> None:
        """Enter the Pokemart and allow purchasing items."""
        write_lines(output, T.POKEMART_HEADER)
        self.show_shop_menu(output)
        self.show_pokemart_panel()
        self.pending_command = "shop"

    # ── Pokemart shop ────────────────────────────────────────────────────────

    @property
    def SHOP_CATALOG(self) -> dict:  # noqa: N802
        """Delegate to the authoritative catalog in buildings module."""
        return buildings.SHOP_CATALOG

    def show_shop_menu(self, output: RichLog) -> None:
        """Display the Pokemart shop catalog."""
        money = self.game_state.game_data.get("money", 0)
        output.write(f"   [bold]Your money:[/bold] [cyan]₽{money}[/cyan]")
        output.write("")
        output.write("[bold green]Available items:[/bold green]")
        for name, info in self.SHOP_CATALOG.items():
            output.write(
                f"   {info['emoji']} [green]{name}[/green] - ₽{info['price']}  [dim]{info['description']}[/dim]"
            )
        output.write("")
        output.write(
            "[dim]Commands: 'buy <item>'  or  'buy <qty> <item>'  (e.g. 'buy 5 pokeball')[/dim]"
        )
        output.write("[dim]          'leave' to exit the shop[/dim]")
        output.write("")

    def process_shop_command(self, command: str, output: RichLog) -> str:
        """Process a Pokemart shop command. Returns 'ok', 'cant_afford', or 'leave'."""
        cmd = command.lower().strip()

        if cmd in ("leave", "exit", "done", "goodbye", "bye", "no", "back"):
            self._clear_active_building_context()
            self.hide_all_panels()
            write_lines(output, T.POKEMART_LEAVE)
            return "leave"  # Don't set pending_command — exits the shop

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

            # Resolve item name: check SELL_PRICES first, then main catalog at 50%
            sell_item_name: str | None = None
            sell_price: int = 0

            for special_name in buildings.SELL_PRICES:
                if special_name.lower() == sale_input or sale_input in special_name.lower():
                    sell_item_name = special_name
                    sell_price = buildings.SELL_PRICES[special_name]
                    break

            if sell_item_name is None:
                for item_name, info in self.SHOP_CATALOG.items():
                    if item_name.lower() == sale_input or sale_input in item_name.lower():
                        sell_item_name = item_name
                        sell_price = info["price"] // 2
                        break

            if sell_item_name is None:
                write_lines(output, T.SHOP_NO_RESALE_VALUE)
                self.pending_command = "shop"
                return "error"

            items = self.game_state.game_data.setdefault("items", {})
            owned_qty = items.get(sell_item_name, 0)
            if owned_qty <= 0:
                write_lines_fmt(output, T.SHOP_DO_NOT_HAVE_ITEM, item_name=sell_item_name)
                self.pending_command = "shop"
                return "error"

            sale_qty = min(sale_qty, owned_qty)
            total_earned = sell_price * sale_qty
            self.game_state.game_data["money"] = (
                self.game_state.game_data.get("money", 0) + total_earned
            )

            new_qty = owned_qty - sale_qty
            if new_qty <= 0:
                items.pop(sell_item_name, None)
            else:
                items[sell_item_name] = new_qty

            new_balance = self.game_state.game_data["money"]
            write_lines_fmt(
                output,
                T.SHOP_SELL_SUCCESS,
                qty=sale_qty,
                item_name=sell_item_name,
                total_earned=total_earned,
                money=new_balance,
            )
            self.show_shop_menu(output)
            self.pending_command = "shop"
            return "ok"

        if not cmd.startswith("buy "):
            write_lines(output, T.SHOP_UNKNOWN_COMMAND)
            self.pending_command = "shop"
            return "error"

        purchase = cmd[4:].strip()
        qty = 1
        parts = purchase.split(None, 1)
        if len(parts) == 2 and parts[0].isdigit():
            qty = int(parts[0])
            purchase = parts[1]
        qty = max(1, min(qty, 99))

        if purchase.endswith("s") and not purchase.endswith("ss"):
            purchase = purchase[:-1]

        matched_item = None
        for item_name in self.SHOP_CATALOG:
            if item_name.lower() == purchase or purchase in item_name.lower():
                matched_item = item_name
                break

        if not matched_item:
            write_lines_fmt(output, T.SHOP_ITEM_NOT_SOLD, item_name=command[4:].strip())
            self.pending_command = "shop"
            return "error"

        info = self.SHOP_CATALOG[matched_item]
        total_cost = info["price"] * qty
        money = self.game_state.game_data.get("money", 0)

        if money < total_cost:
            write_lines_fmt(output, T.SHOP_NOT_ENOUGH_MONEY, total_cost=total_cost, money=money)
            self.pending_command = "shop"
            return "cant_afford"

        self.game_state.game_data["money"] = money - total_cost
        items = self.game_state.game_data.setdefault("items", {})
        items[matched_item] = items.get(matched_item, 0) + qty

        write_lines_fmt(
            output,
            T.SHOP_BUY_SUCCESS,
            qty=qty,
            item_name=matched_item,
            total_cost=total_cost,
            money=self.game_state.game_data["money"],
        )

        self.show_shop_menu(output)
        self.pending_command = "shop"
        return "ok"

    # ── Gyms ─────────────────────────────────────────────────────────────────

    def enter_gym(self, gym_name: str, output: RichLog) -> None:
        """Enter a Pokemon Gym."""
        write_lines(output, T.GYM_HEADER)
        location_name = (
            self.game_state.current_location.name if self.game_state.current_location else ""
        )
        if "Pewter" in location_name:
            write_lines(output, T.GYM_PEWTER_DIALOGUE)
        elif "Viridian" in location_name:
            write_lines(output, T.GYM_VIRIDIAN_DIALOGUE)
        else:
            write_lines(output, T.GYM_CLOSED)
        write_lines(output, T.GYM_EXIT)

    # ── Story buildings ──────────────────────────────────────────────────────

    def enter_players_house(self, output: RichLog) -> None:
        """Enter the player's house."""
        write_lines(output, T.PLAYER_HOUSE_VISIT)

    def enter_rivals_house(self, output: RichLog) -> None:
        """Enter the rival's house."""
        write_lines(output, T.RIVALS_HOUSE_HEADER)
        pokemon = self.game_state.game_data.get("pokemon", [])
        if not pokemon:
            write_lines(output, T.RIVALS_HOUSE_NO_POKEMON)
        else:
            write_lines(output, T.RIVALS_HOUSE_WITH_POKEMON)
        write_lines(output, T.RIVALS_HOUSE_EXIT)

    def enter_oaks_lab(self, output: RichLog) -> None:
        """Enter Professor Oak's Laboratory."""
        output.write("")
        output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
        output.write("[bold cyan]      🔬 PROFESSOR OAK'S LAB 🔬          [/bold cyan]")
        output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
        output.write("")
        pokemon = self.game_state.game_data.get("pokemon", [])
        if not pokemon:
            if self.game_state.pikachu_mode:
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
                output.write("[yellow]Type 'Choose Pikachu' to begin your journey:[/yellow]")
                output.write("")
            else:
                output.write(
                    "[bold]Professor Oak:[/bold] [cyan]Ah! Welcome to my laboratory![/cyan]"
                )
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
                output.write("[yellow]Type 'Choose' followed by the Pokemon name:[/yellow]")
                output.write("[dim]Example: Choose Bulbasaur[/dim]")
                output.write("")
            self.pending_command = "choose_starter"
        else:
            output.write(
                "[bold]Professor Oak:[/bold] [cyan]Hello! How is your Pokedex coming along?[/cyan]"
            )
            output.write("")
            output.write("[cyan]   Remember, to make a complete guide of all Pokemon[/cyan]")
            output.write("[cyan]   in the world... That is my dream![/cyan]")
            output.write("")
            output.write("[bold]Research Data:[/bold]")
            output.write("   • Pokemon seen: [dim]Coming soon[/dim]")
            output.write(f"   • Pokemon caught: [green]{len(pokemon)}[/green]")
            output.write("")
        output.write("[dim]You leave the laboratory[/dim]")
        output.write("")

    # ── Name selection ───────────────────────────────────────────────────────

    def confirm_name_selection(self, output: RichLog) -> None:
        """Confirm and set player and rival names."""
        player_input = self.query_one("#input-player-name", Input)
        rival_input = self.query_one("#input-rival-name", Input)
        player_name = player_input.value.strip()
        rival_name = rival_input.value.strip()

        if not player_name:
            write_lines(output, T.NAME_REQUIRED_PLAYER)
            return
        if not rival_name:
            write_lines(output, T.NAME_REQUIRED_RIVAL)
            return

        self.game_state.game_data["player_name"] = player_name
        self.game_state.game_data["rival_name"] = rival_name
        self.hide_all_panels()

        write_lines_fmt(output, T.NAMES_SET, player_name=player_name, rival_name=rival_name)

        self.update_pallet_town_buildings()
        exploration.show_location_arrival(self.game_state, output)

    def random_name_selection(self, output: RichLog) -> None:
        """Generate random names for player and rival."""
        player_names = [
            "Ash",
            "Red",
            "Ethan",
            "Brendan",
            "Lucas",
            "Hilbert",
            "Nate",
            "Calem",
            "Elio",
            "Victor",
        ]
        rival_names = [
            "Gary",
            "Blue",
            "Silver",
            "May",
            "Barry",
            "Cheren",
            "Hugh",
            "Serena",
            "Hau",
            "Hop",
        ]

        player_name = random.choice(player_names)
        rival_name = random.choice(rival_names)

        player_input = self.query_one("#input-player-name", Input)
        rival_input = self.query_one("#input-rival-name", Input)
        player_input.value = player_name
        rival_input.value = rival_name

        write_lines_fmt(
            output,
            T.RANDOM_NAMES_GENERATED,
            player_name=player_name,
            rival_name=rival_name,
        )

    def update_pallet_town_buildings(self) -> None:
        """Update Pallet Town building names based on player and rival names."""
        pallet_town = _get_location("Pallet Town")
        if pallet_town:
            player_name = self.game_state.game_data.get("player_name", "Trainer")
            rival_name = self.game_state.game_data.get("rival_name", "Rival")
            pallet_town.buildings = [
                f"{player_name}'s House",
                f"{rival_name}'s House",
                "Professor Oak's Lab",
            ]

    def choose_starter_pokemon(self, pokemon_name: str, output: RichLog) -> None:
        """Choose starter Pokemon (delegates to buildings module)."""
        buildings.choose_starter_pokemon(
            self.game_state,
            pokemon_name,
            output,
            lambda cmd: setattr(self, "pending_command", cmd),
            trigger_trainer_battle_callback=lambda trainer: self.trigger_trainer_encounter(
                output, trainer
            ),
        )
