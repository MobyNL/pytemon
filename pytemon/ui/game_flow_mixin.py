"""
Game flow mixin for PokemonTerminal.

Handles the save/load/quit/menu state machine and the pending-command
dispatcher (handle_pending_command), keeping these flows out of the
main App class.
"""

from typing import TYPE_CHECKING, Optional

from textual.widgets import RichLog

from ..ui import menus

if TYPE_CHECKING:
    pass  # Avoid circular imports — self is always a PokemonTerminal at runtime


class GameFlowMixin:
    """Mixin providing menu, save/load, quit, and evolution-resume flows."""

    # ── Main menu ────────────────────────────────────────────────────────────

    def show_main_menu(self, output: RichLog) -> None:
        """Display the main menu."""
        menus.show_main_menu(output)
        self.show_main_menu_action_panel()

    def process_menu_command(self, command: str, output: RichLog) -> None:
        """Process commands when in the main menu."""
        menus.process_menu_command(
            self.game_state,
            command,
            output,
            self.start_new_game,
            self.show_load_menu,
            self.exit,
            self.load_selected_save,
            lambda: hasattr(self, "_temp_saves_list"),
            lambda: (
                delattr(self, "_temp_saves_list") if hasattr(self, "_temp_saves_list") else None
            ),
        )

    def start_new_game(self, output: RichLog) -> None:
        """Start a new game."""
        output.write("")
        output.write("[bold green]✓ Starting new game...[/bold green]")
        output.write("")
        self.game_state.start_new_game()
        output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
        output.write("[bold green]🌟 Welcome to the Pokemon World! 🌟[/bold green]")
        output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
        output.write("")
        output.write("Before we begin your adventure...")
        output.write("")
        self.show_name_selection_panel()

    def show_load_menu(self, output: RichLog) -> None:
        """Show the load game menu."""
        saves = self.game_state.get_available_saves()
        menus.show_load_menu(
            self.game_state,
            output,
            lambda saves_list: setattr(self, "_temp_saves_list", saves_list),
        )
        if saves:
            self.show_load_game_panel(saves)

    def load_selected_save(self, save_name: str, output: RichLog) -> None:
        """Load a save file based on user input."""
        self.hide_all_panels()
        menus.load_selected_save(
            self.game_state,
            save_name,
            output,
            lambda: getattr(self, "_temp_saves_list", None),
            lambda: (
                delattr(self, "_temp_saves_list") if hasattr(self, "_temp_saves_list") else None
            ),
            self.show_location_arrival,
            self.ensure_battle_ready,
        )
        self._refresh_subtitle()

    # ── Pending-command state machine ────────────────────────────────────────

    def handle_pending_command(self, user_input: str, output: RichLog) -> None:
        """
        Dispatch the argument for a pending multi-step command.

        Args:
            user_input: The user's input (argument)
            output: The RichLog widget to write to
        """
        cmd_type = self.pending_command
        self.pending_command = None

        if cmd_type == "move_to":
            if user_input.lower().strip() in ("cancel", "back", "exit", "exit building", "leave"):
                output.write("")
                output.write("[dim]Cancelled.[/dim]")
                output.write("")
            else:
                self.move_to_location(user_input, output)

        elif cmd_type == "enter_building":
            if user_input.lower().strip() in ("cancel", "back", "exit", "exit building", "leave"):
                output.write("")
                output.write("[dim]Cancelled.[/dim]")
                output.write("")
            else:
                self.enter_building(user_input, output)

        elif cmd_type == "choose_starter":
            self.choose_starter_pokemon(user_input, output)

        elif cmd_type == "confirm_quit":
            self.confirm_quit_response(user_input, output)

        elif cmd_type == "save_name":
            self.handle_save_name(user_input, output)

        elif cmd_type == "confirm_overwrite":
            self.handle_overwrite_confirmation(user_input, output)

        elif cmd_type == "confirm_heal_center":
            self.handle_heal_center_confirmation(user_input, output)

        elif cmd_type == "confirm_heal_mom":
            self.handle_heal_mom_confirmation(user_input, output)

        elif cmd_type == "pokemon_center":
            self._handle_pokemon_center_command(user_input, output)

        elif cmd_type == "battle":
            output.write(f"[bold yellow]\U0001f3ae >[/bold yellow] {user_input}")
            self.process_battle_command(user_input, output)

        elif cmd_type == "select_move":
            output.write(f"[bold yellow]\U0001f3ae >[/bold yellow] {user_input}")
            self.execute_player_move(user_input, output)

        elif cmd_type == "shop":
            self.process_shop_command(user_input, output)

        elif cmd_type == "switch_target":
            self.execute_switch(user_input, output)

        elif cmd_type == "faint_switch":
            self.execute_faint_switch(user_input, output)

        elif cmd_type == "pc":
            from .. import pc_system

            pc_system.process_pc_command(
                self.game_state,
                user_input,
                output,
                lambda cmd: setattr(self, "pending_command", cmd),
            )
            if self.pending_command is None:
                self._return_to_pokemon_center(output)

        elif cmd_type == "learn_move_choice":
            output = self.query_one("#output", RichLog)
            pokemon = self.pending_command_data.get("learn_pokemon", {})
            move_name = self.pending_command_data.get("learn_move_name", "")
            remaining = self.pending_command_data.get("learn_remaining", [])
            post_action = self.pending_command_data.get("learn_post_action", "wild_end")
            choice = user_input.strip().lower()

            from ..data.move_data import get_move as _get_move

            if choice in ("no", "skip", "cancel", "stop"):
                output.write(
                    f"  [dim]{pokemon.get('name', 'Pokemon')} did not learn {move_name}.[/dim]"
                )
                output.write("")
                if remaining:
                    self._queue_move_learn(pokemon, remaining, post_action, output)
                else:
                    self._resume_after_move_learn(post_action, output)
            elif choice.isdigit() and 1 <= int(choice) <= len(pokemon.get("moves", [])):
                idx = int(choice) - 1
                old_move = pokemon["moves"][idx]["name"]
                move_data = _get_move(move_name)
                new_move = (
                    {"name": move_name, "pp": move_data["pp"], "max_pp": move_data["pp"]}
                    if move_data
                    else {"name": move_name, "pp": 5, "max_pp": 5}
                )
                pokemon["moves"][idx] = new_move
                output.write(
                    f"  [bold cyan]✦ {pokemon.get('name', 'Pokemon')} forgot "
                    f"[red]{old_move}[/red] and learned [green]{move_name}[/green]![/bold cyan]"
                )
                output.write("")
                if remaining:
                    self._queue_move_learn(pokemon, remaining, post_action, output)
                else:
                    self._resume_after_move_learn(post_action, output)
            else:
                output.write(
                    f"  [yellow]Type 1-{len(pokemon.get('moves', []))} to pick a move "
                    f"to forget, or 'no' to skip.[/yellow]"
                )
                self.pending_command = "learn_move_choice"

        elif cmd_type == "confirm_evolution":
            inp = user_input.lower().strip()
            if inp in ("yes", "y", "evolve", "ok", ""):
                pokemon_ref = self.pending_command_data.get("evolving_pokemon")
                evolved_into = self.pending_command_data.get("evolves_into", "???")
                if pokemon_ref is not None:
                    from .. import evolution as _evo

                    _evo.force_evolve(
                        self.game_state, pokemon_ref, evolved_into, output, update_battle_state=True
                    )
                self._resume_after_evolution(output)
            else:
                pokemon_name = self.pending_command_data.get("evolving_pokemon", {}).get(
                    "name", "POKÉMON"
                )
                output.write("")
                output.write(f"[cyan]{pokemon_name} did not evolve.[/cyan]")
                output.write("")
                self._resume_after_evolution(output)

        # Clear pending data unless we're mid-flow
        persisted = {
            "save_name",
            "confirm_overwrite",
            "confirm_quit",
            "battle",
            "select_move",
            "shop",
            "pc",
            "confirm_evolution",
            "learn_move_choice",
        }
        if cmd_type not in persisted or self.pending_command is None:
            if cmd_type not in {"battle", "select_move"}:
                self.pending_command_data = {}

    # ── Quit flow ────────────────────────────────────────────────────────────

    def safe_exit(self) -> None:
        """Safely exit the application with lock-file cleanup."""
        from pathlib import Path as _Path

        if self.lock_file_path:
            try:
                lock_path = _Path(self.lock_file_path)
                if lock_path.exists():
                    lock_path.unlink()
            except Exception:
                pass
        self.exit()

    def prompt_for_quit(self, output: RichLog) -> None:
        """Show the quit destination panel (Close/Main Menu/Cancel) if in-game."""
        if self.game_state.in_game:
            output.write("")
            output.write("[bold yellow]⚠ Leaving the game?[/bold yellow]")
            output.write("")
            self.hide_all_panels()
            self.query_one("#quit-panel").remove_class("hidden")
        else:
            output.write("[cyan]👋 Goodbye![/cyan]")
            self.safe_exit()

    def confirm_quit_response(self, response: str, output: RichLog) -> None:
        """Handle the text response to the quit confirmation prompt."""
        response_lower = response.lower().strip()
        if response_lower in ("yes", "y", "save"):
            if self.pending_command_data.get("failed_save_quit"):
                output.write("")
                output.write("[yellow]⚠ Progress not saved[/yellow]")
                output.write("[cyan]👋 Goodbye, Trainer![/cyan]")
                self.safe_exit()
                return
            self.save_current_game(output)
            self.pending_command_data["quit_after_save"] = True
        elif response_lower in ("no", "n", "don't save", "dont save", "skip"):
            if self.pending_command_data.get("failed_save_quit"):
                output.write("")
                output.write("[green]✓ Continuing game...[/green]")
                output.write("")
                self.pending_command_data["failed_save_quit"] = False
            else:
                output.write("")
                output.write("[yellow]⚠ Progress not saved[/yellow]")
                self._do_quit_action(output)
        elif response_lower in ("cancel", "c", "back"):
            output.write("")
            output.write("[green]✓ Cancelled[/green]")
            output.write("[dim]Continuing game...[/dim]")
            output.write("")
            self.pending_command_data["quit_after_save"] = False
            self.pending_command_data["failed_save_quit"] = False
        else:
            output.write("")
            output.write("[red]❌ Invalid choice[/red]")
            output.write("[dim]Please type: Yes, No, or Cancel[/dim]")
            output.write("")
            self.pending_command = "confirm_quit"

    def _proceed_with_quit(self, output: RichLog) -> None:
        """After choosing Close Game or Main Menu, prompt to save if needed."""
        pokemon = self.game_state.game_data.get("pokemon", [])
        if self.game_state.in_game and pokemon:
            dest = self.pending_command_data.get("quit_destination", "exit")
            dest_label = "Main Menu" if dest == "main_menu" else "quit"
            output.write("")
            output.write(
                f"[bold yellow]⚠ Would you like to save before you {dest_label}?[/bold yellow]"
            )
            output.write("")
            output.write("  [green]Yes[/green] - Save first")
            output.write("  [red]No[/red] - Continue without saving")
            output.write("  [cyan]Cancel[/cyan] - Go back")
            output.write("")
            output.write("[dim]Click a button or type your choice:[/dim]")
            output.write("")
            self.show_confirmation_panel(
                f"Save before you {dest_label}?",
                "quit",
                show_cancel=True,
            )
            self.pending_command = "confirm_quit"
        else:
            self._do_quit_action(output)

    def _do_quit_action(self, output: RichLog) -> None:
        """Execute the chosen quit destination (exit or main menu)."""
        dest = self.pending_command_data.get("quit_destination", "exit")
        if dest == "main_menu":
            self._go_to_main_menu(output)
        else:
            output.write("[cyan]👋 Goodbye, Trainer![/cyan]")
            self.safe_exit()

    def _go_to_main_menu(self, output: RichLog) -> None:
        """Reset game state and return to the main menu screen."""
        self.pending_command = None
        self.pending_command_data = {}
        self.hide_all_panels()
        self.game_state.in_game = False
        self.game_state.in_menu = True
        self.game_state.battle_state = None
        self.game_state.current_location = None
        output.write("")
        output.write("[dim]Returning to main menu...[/dim]")
        output.write("")
        self.show_main_menu(output)

    def handle_confirmation_response(
        self, response: str, output: RichLog, confirmation_type: str
    ) -> None:
        """Handle yes/no/cancel confirmation responses from buttons or text."""
        if confirmation_type == "quit":
            self.confirm_quit_response(response, output)
        elif confirmation_type == "overwrite":
            self.handle_overwrite_confirmation(response, output)
        else:
            output.write(f"[red]❌ Unknown confirmation type: {confirmation_type}[/red]")

    # ── Save / load ──────────────────────────────────────────────────────────

    def check_autosave(self, command: str, output: RichLog) -> None:
        """Check if autosave should happen and perform it."""
        menus.check_autosave(self.game_state, command, output, self.perform_autosave)

    def perform_autosave(self, output: RichLog) -> None:
        """Perform an autosave."""
        menus.perform_autosave(self.game_state, output)

    def should_ignore_for_autosave(self, command: str) -> bool:
        """Check if a command should be ignored for autosave counting."""
        return menus.should_ignore_for_autosave(command)

    def show_settings(self, output: RichLog) -> None:
        """Show and allow modification of game settings."""
        menus.show_settings(self.game_state, output)

    def return_to_menu(self, output: RichLog) -> None:
        """Return to the main menu."""
        menus.return_to_menu(self.game_state, output, self.show_main_menu)

    def save_current_game(self, output: RichLog) -> None:
        """Prompt for save name and save the current game."""
        menus.save_current_game(
            self.game_state,
            output,
            lambda cmd: setattr(self, "pending_command", cmd),
            self.show_save_option_panel,
        )

    def handle_save_name(self, save_name: str, output: RichLog) -> None:
        """Handle the save name input."""
        menus.handle_save_name(
            self.game_state,
            save_name,
            output,
            self.perform_save,
            lambda cmd: setattr(self, "pending_command", cmd),
            lambda key, value: self.pending_command_data.__setitem__(key, value),
            self.show_confirmation_panel,
        )

    def handle_overwrite_confirmation(self, response: str, output: RichLog) -> None:
        """Handle the overwrite confirmation response."""
        menus.handle_overwrite_confirmation(
            response,
            output,
            lambda key: self.pending_command_data.get(key),
            self.perform_save,
            lambda cmd: setattr(self, "pending_command", cmd),
        )

    def perform_save(self, save_name: Optional[str], output: RichLog) -> None:
        """Actually perform the save operation."""

        def _after_save():
            self._do_quit_action(output)

        menus.perform_save(
            self.game_state,
            save_name,
            output,
            lambda key: self.pending_command_data.get(key),
            lambda: setattr(self, "pending_command_data", {}),
            lambda key, value: self.pending_command_data.__setitem__(key, value),
            lambda cmd: setattr(self, "pending_command", cmd),
            _after_save,
        )
