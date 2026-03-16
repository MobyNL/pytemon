"""
Menu and save/load system functions for Pokemon Terminal Game.

This module handles:
- Main menu display and navigation
- New game creation
- Save game system (save, load, autosave)
- Game settings management
"""

import json
from typing import TYPE_CHECKING, Any, Callable, Optional

from textual.widgets import RichLog

if TYPE_CHECKING:
    from ..game_state import GameState


def show_main_menu(output: RichLog) -> None:
    """Display the main menu."""
    output.clear()
    output.write("")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("[bold cyan]        🎮 POKEMON TERMINAL GAME 🎮        [/bold cyan]")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("")
    output.write("[bold green]MAIN MENU:[/bold green]")
    output.write("")
    output.write("  [cyan]Start New Game[/cyan] - Begin a new adventure")
    output.write("  [cyan]Load Game[/cyan]      - Continue from a save")
    output.write("  [cyan]Exit[/cyan]           - Quit the game")
    output.write("")
    output.write("[dim]Type a command to continue...[/dim]")
    output.write("")


def process_menu_command(
    game_state: "GameState",
    command: str,
    output: RichLog,
    start_new_game_cb: Callable[[RichLog], None],
    show_load_menu_cb: Callable[[RichLog], None],
    exit_cb: Callable[[], None],
    load_selected_save_cb: Callable[[str, RichLog], None],
    has_temp_saves_list: Callable[[], bool],
    delete_temp_saves_list: Callable[[], None],
) -> None:
    """
    Process commands when in the main menu.

    Args:
        game_state: The game state object
        command: The command to process
        output: The RichLog widget to write to
        start_new_game_cb: Callback to start new game
        show_load_menu_cb: Callback to show load menu
        exit_cb: Callback to exit the application
        load_selected_save_cb: Callback to load a selected save
        has_temp_saves_list: Callback to check if temp saves list exists
        delete_temp_saves_list: Callback to delete temp saves list
    """
    cmd = command.lower().strip()

    # Check if we're in the load game submenu
    if has_temp_saves_list():
        if cmd == "menu" or cmd == "back":
            delete_temp_saves_list()
            show_main_menu(output)
            return
        else:
            # In load menu, still allow selecting by save name
            load_selected_save_cb(command, output)
            return

    # Handle main menu choices (keyword-driven only)
    if "new" in cmd or "start" in cmd:
        start_new_game_cb(output)
    elif "load" in cmd:
        show_load_menu_cb(output)
    elif cmd in ("exit", "quit", "stop", "stop playing", "q"):
        output.write("")
        output.write("[cyan]👋 Thanks for playing! Goodbye, Trainer![/cyan]")
        output.write("")
        exit_cb()
    else:
        output.write("")
        output.write(f"[red]❌ Invalid command:[/red] {command}")
        output.write("[dim]Try: 'Start New Game', 'Load Game', or 'Exit'[/dim]")
        output.write("")


def start_new_game(
    game_state: "GameState",
    output: RichLog,
    show_location_arrival_cb: Callable[[RichLog, bool], None],
) -> None:
    """Start a new game."""
    output.write("")
    output.write("[bold green]✓ Starting new game...[/bold green]")
    output.write("")

    game_state.start_new_game()

    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("[bold green]🌟 Welcome to the Pokemon World! 🌟[/bold green]")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("")
    output.write(f"💰 Money: [green]₽{game_state.game_data['money']}[/green]")
    output.write(f"🏆 Badges: [cyan]{game_state.game_data['badges']}[/cyan]")
    output.write("")

    # Show arrival at starting location (is_load=False)
    from .. import exploration

    exploration.show_location_arrival(game_state, output)


def show_load_menu(
    game_state: "GameState", output: RichLog, set_temp_saves_list: Callable[[list], None]
) -> None:
    """Show the load game menu."""
    output.write("")
    output.write("[bold cyan]📂 Load Game[/bold cyan]")
    output.write("")

    saves = game_state.get_available_saves()

    if not saves:
        output.write("[yellow]⚠ No save files found![/yellow]")
        output.write("")
        output.write(f"[dim]Save files should be in: {game_state.saves_dir}[/dim]")
        output.write("[dim]Type 'menu' to return to main menu[/dim]")
        output.write("")
        return

    output.write("[green]Available saves:[/green]")
    output.write("")

    for save_file in saves:
        # Try to load save info
        try:
            with open(save_file) as f:
                data = json.load(f)
            location = data.get("location", "Unknown")
            badges = data.get("badges", 0)
            output.write(f"  [cyan]{save_file.stem}[/cyan]")
            output.write(f"    📍 {location} | 🏆 {badges} badges")
        except:
            output.write(f"  [cyan]{save_file.stem}[/cyan]")

    output.write("")
    output.write("[dim]Type the save name to load, or 'menu' to go back[/dim]")
    output.write("")

    # Store saves list for selection
    set_temp_saves_list(saves)


def load_selected_save(
    game_state: "GameState",
    save_name: str,
    output: RichLog,
    get_temp_saves_list: Callable[[], Optional[list]],
    delete_temp_saves_list: Callable[[], None],
    show_location_arrival_cb: Callable[[RichLog, bool], None],
    ensure_battle_ready_cb: Callable[[dict], None],
) -> None:
    """
    Load a save file based on user input.

    Args:
        game_state: The game state object
        save_name: The name of the save file to load
        output: The RichLog widget to write to
        get_temp_saves_list: Callback to get temp saves list
        delete_temp_saves_list: Callback to delete temp saves list
        show_location_arrival_cb: Callback to show location arrival
        ensure_battle_ready_cb: Callback to ensure Pokemon is battle ready
    """
    temp_saves_list = get_temp_saves_list()
    if not temp_saves_list:
        output.write("[red]❌ No saves menu active[/red]")
        output.write("")
        return

    # Try to find the save by name
    save_name_lower = save_name.lower().strip()
    save_file = None

    for save in temp_saves_list:
        if save.stem.lower() == save_name_lower or save_name_lower in save.stem.lower():
            save_file = save
            break

    if save_file:
        if game_state.load_game(save_file):
            output.write("")
            output.write(f"[bold green]✓ Loaded save:[/bold green] {save_file.stem}")
            output.write("")
            output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
            output.write("[bold green]🎮 Game Loaded! 🎮[/bold green]")
            output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
            output.write("")
            output.write(f"💰 Money: [green]₽{game_state.game_data.get('money', 0)}[/green]")
            output.write(f"🏆 Badges: [cyan]{game_state.game_data.get('badges', 0)}[/cyan]")
            output.write("")

            # Migrate Pokemon to full battle-ready format
            for p in game_state.game_data.get("pokemon", []):
                if not isinstance(p, str):
                    ensure_battle_ready_cb(p)

            # Show location arrival with "find yourself" message (is_load=True)
            show_location_arrival_cb(output, is_load=True)

            # Clean up temp list
            delete_temp_saves_list()
        else:
            output.write("")
            output.write("[red]❌ Failed to load save file[/red]")
            output.write("")
    else:
        output.write("")
        output.write(f"[red]❌ Save not found:[/red] {save_name}")
        output.write("")


def check_autosave(
    game_state: "GameState",
    command: str,
    output: RichLog,
    perform_autosave_cb: Callable[[RichLog], None],
) -> None:
    """
    Check if autosave should happen and perform it.

    Args:
        game_state: The game state object
        command: The command that was just executed
        output: The RichLog widget to write to
        perform_autosave_cb: Callback to perform autosave
    """
    # Skip autosave if disabled or in battle
    if not game_state.autosave_enabled or game_state.in_battle:
        return

    cmd_lower = command.lower().strip()

    # Don't count ignored commands
    if should_ignore_for_autosave(cmd_lower):
        return

    # Increment autosave counter
    game_state.commands_since_autosave += 1

    # Check if we should autosave
    if game_state.commands_since_autosave >= game_state.autosave_frequency:
        perform_autosave_cb(output)


def perform_autosave(game_state: "GameState", output: RichLog) -> None:
    """
    Perform an autosave.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
    """
    try:
        # Update location in game data before saving
        if game_state.current_location:
            game_state.game_data["location"] = game_state.current_location.name

        # Update settings in game data
        if "settings" not in game_state.game_data:
            game_state.game_data["settings"] = {}
        game_state.game_data["settings"]["autosave_enabled"] = game_state.autosave_enabled
        game_state.game_data["settings"]["autosave_frequency"] = game_state.autosave_frequency

        # Use current save file or create default
        save_file = game_state.save_game()

        # Reset counter
        game_state.commands_since_autosave = 0

        # Show subtle autosave notification
        output.write("")
        output.write(f"[dim]💾 Autosaved to {save_file.name}[/dim]")
        output.write("")
    except Exception as e:
        # Don't interrupt gameplay for autosave failures
        output.write(f"[dim][yellow]⚠ Autosave failed: {e}[/yellow][/dim]")


def should_ignore_for_autosave(command: str) -> bool:
    """
    Check if a command should be ignored for autosave counting.

    Args:
        command: The command to check (already lowercased and stripped)

    Returns:
        bool: True if the command should be ignored
    """
    # Exact match commands to ignore
    ignored_commands = [
        "help",
        "h",
        "about",
        "status",
        "party",
        "show party",
        "bag",
        "look around",
        "look",
        "settings",
        "autosave",
    ]

    if command in ignored_commands:
        return True

    # Command prefixes to ignore
    ignored_prefixes = ["inspect "]

    for prefix in ignored_prefixes:
        if command.startswith(prefix):
            return True

    return False


def show_settings(game_state: "GameState", output: RichLog) -> None:
    """
    Show and allow modification of game settings.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
    """
    output.write("")
    output.write("[bold cyan]⚙️  GAME SETTINGS ⚙️[/bold cyan]")
    output.write("")
    output.write("[bold yellow]Autosave Settings:[/bold yellow]")
    output.write(
        f"  Autosave: [{'green' if game_state.autosave_enabled else 'red'}]{'Enabled' if game_state.autosave_enabled else 'Disabled'}[/{'green' if game_state.autosave_enabled else 'red'}]"
    )
    output.write(f"  Frequency: [cyan]Every {game_state.autosave_frequency} commands[/cyan]")
    output.write(
        f"  Commands since last save: [yellow]{game_state.commands_since_autosave}[/yellow]/{game_state.autosave_frequency}"
    )
    output.write("")
    output.write("[bold yellow]Available Commands:[/bold yellow]")
    output.write("  [green]Autosave On[/green]  - Enable autosave")
    output.write("  [green]Autosave Off[/green] - Disable autosave")
    output.write("  [green]Autosave 10[/green]  - Set frequency to 10 commands")
    output.write("  [green]Autosave 20[/green]  - Set frequency to 20 commands")
    output.write("  [green]Autosave 50[/green]  - Set frequency to 50 commands")
    output.write("")


def return_to_menu(
    game_state: "GameState", output: RichLog, show_main_menu_cb: Callable[[RichLog], None]
) -> None:
    """Return to the main menu."""
    output.write("")
    output.write("[yellow]⚠ Returning to main menu...[/yellow]")
    output.write("[dim]Don't forget to save your game first![/dim]")
    output.write("")

    game_state.in_menu = True
    game_state.in_game = False
    show_main_menu_cb(output)


def save_current_game(
    game_state: "GameState",
    output: RichLog,
    set_pending_command: Callable[[str], None],
    show_save_option_panel_cb: Callable[[str], None] = None,
) -> None:
    """Prompt for save name and save the current game.

    Args:
        game_state: The game state object
        output: The RichLog widget to write to
        set_pending_command: Callback to set pending command
        show_save_option_panel_cb: Optional callback to show save option panel with buttons
    """
    output.write("")
    output.write("[bold cyan]💾 Save Game[/bold cyan]")
    output.write("")

    # Check if this save has a known name
    current_save_name = game_state.game_data.get("save_name")

    if current_save_name:
        # Suggest overwriting the current save first
        output.write(f"[bold green]Current save:[/bold green] [cyan]{current_save_name}[/cyan]")
        output.write("")
        output.write("[yellow]What would you like to do?[/yellow]")
        output.write(
            f"  [green]1.[/green] Overwrite current save ([cyan]{current_save_name}[/cyan])"
        )
        output.write("  [green]2.[/green] Create a new save file")
        output.write("")
        output.write(
            "[dim]Click a button, type 1/2, or press Enter to overwrite current save[/dim]"
        )
        output.write("")

        # Show save option panel if callback provided
        if show_save_option_panel_cb:
            show_save_option_panel_cb(current_save_name)
    else:
        # Show existing saves
        saves = game_state.get_available_saves()
        if saves:
            output.write("[bold yellow]Existing saves:[/bold yellow]")
            for save_file in saves:
                save_name = save_file.stem  # filename without extension
                output.write(f"  • [cyan]{save_name}[/cyan]")
            output.write("")

        output.write("[yellow]Enter a name for your save file:[/yellow]")
        output.write("[dim]Or press Enter to create a new one[/dim]")

    output.write("")

    # Set pending command
    set_pending_command("save_name")


def handle_save_name(
    game_state: "GameState",
    save_name: str,
    output: RichLog,
    perform_save_cb: Callable[[Optional[str], RichLog], None],
    set_pending_command: Callable[[str], None],
    set_pending_data: Callable[[str, Any], None],
    show_confirmation_panel_cb: Callable[[str, str, bool], None] = None,
) -> None:
    """
    Handle the save name input.

    Args:
        game_state: The game state object
        save_name: The save name entered by user
        output: The RichLog widget to write to
        perform_save_cb: Callback to perform save
        set_pending_command: Callback to set pending command
        set_pending_data: Callback to set pending command data
        show_confirmation_panel_cb: Optional callback to show confirmation panel with buttons
    """
    save_name = save_name.strip()

    current_save_name = game_state.game_data.get("save_name")

    # ── Keyword shortcuts ────────────────────────────────────────────────────
    # Recognise "1", "overwrite", or "overwrite <current_name>" as: overwrite.
    # Recognise "2" as: start a blank new-name prompt.
    if current_save_name:
        lower = save_name.lower()
        is_overwrite = lower in ("1", "overwrite") or lower in (
            f"overwrite {current_save_name.lower()}",
            f"overwrite '{current_save_name.lower()}'",
        )
        if is_overwrite:
            perform_save_cb(current_save_name, output)
            return
        if save_name == "2":
            output.write("")
            output.write("[yellow]Enter a name for your new save file:[/yellow]")
            output.write("[dim]Or press Enter to use a timestamp[/dim]")
            output.write("")
            # Re-arm the pending command so the next input is treated as a name
            set_pending_command("save_name")
            return

    # If empty, use current save name if available, otherwise create new
    if not save_name:
        if current_save_name:
            perform_save_cb(current_save_name, output)
        else:
            perform_save_cb(None, output)
        return

    # Clean the save name (remove .json if user added it)
    if save_name.endswith(".json"):
        save_name = save_name[:-5]

    # Reject names containing spaces — they cause confusing file names and
    # are usually the result of typing a command instead of a plain name.
    if " " in save_name:
        output.write("")
        output.write("[red]❌ Save name cannot contain spaces.[/red]")
        output.write("[dim]Use underscores instead, e.g. 'my_save'[/dim]")
        output.write("")
        set_pending_command("save_name")
        return

    # Check if save already exists
    save_path = game_state.saves_dir / f"{save_name}.json"

    if save_path.exists():
        # Check if it's the current save
        current_save_name = game_state.game_data.get("save_name")
        if save_name == current_save_name:
            # Overwriting current save, no confirmation needed
            perform_save_cb(save_name, output)
            return

        # Prompt for overwrite confirmation for different save
        output.write("")
        output.write(f"[bold yellow]⚠ Save '{save_name}' already exists![/bold yellow]")
        output.write("")
        output.write("[yellow]Do you want to overwrite it?[/yellow]")
        output.write("  [green]Yes[/green] - Overwrite the save")
        output.write("  [red]No[/red] - Cancel and choose a different name")
        output.write("")
        output.write("[dim]Click a button or type your choice:[/dim]")
        output.write("")

        # Store the save name for later
        set_pending_data("save_name", save_name)
        set_pending_command("confirm_overwrite")

        # Show confirmation panel if callback provided
        if show_confirmation_panel_cb:
            show_confirmation_panel_cb(
                f"Overwrite save '{save_name}'?",
                "overwrite",
                False,  # No cancel button for overwrite - only yes/no
            )
    else:
        # Save doesn't exist, just save
        perform_save_cb(save_name, output)


def handle_overwrite_confirmation(
    response: str,
    output: RichLog,
    get_pending_data: Callable[[str], Any],
    perform_save_cb: Callable[[Optional[str], RichLog], None],
    set_pending_command: Callable[[str], None],
) -> None:
    """
    Handle the overwrite confirmation response.

    Args:
        response: User's response
        output: The RichLog widget to write to
        get_pending_data: Callback to get pending command data
        perform_save_cb: Callback to perform save
        set_pending_command: Callback to set pending command
    """
    response_lower = response.lower().strip()
    save_name = get_pending_data("save_name")

    if response_lower in ("yes", "y", "overwrite"):
        # Overwrite the save
        perform_save_cb(save_name, output)
    elif response_lower in ("no", "n", "cancel"):
        # Cancel and ask for name again
        output.write("")
        output.write("[yellow]Cancelled. Enter a different save name:[/yellow]")
        output.write("")
        set_pending_command("save_name")
    else:
        # Invalid response
        output.write("")
        output.write("[red]❌ Invalid choice[/red]")
        output.write("[dim]Please type: Yes or No[/dim]")
        output.write("")
        # Ask again
        set_pending_command("confirm_overwrite")


def perform_save(
    game_state: "GameState",
    save_name: Optional[str],
    output: RichLog,
    get_pending_data: Callable[[str], Any],
    clear_pending_data: Callable[[], None],
    set_pending_data: Callable[[str, Any], None],
    set_pending_command: Callable[[str], None],
    safe_exit_cb: Callable[[], None],
) -> None:
    """
    Actually perform the save operation.

    Args:
        game_state: The game state object
        save_name: Optional save name
        output: The RichLog widget to write to
        get_pending_data: Callback to get pending command data
        clear_pending_data: Callback to clear pending command data
        set_pending_data: Callback to set pending command data
        set_pending_command: Callback to set pending command
        safe_exit_cb: Callback to safely exit the application
    """
    try:
        # Update location in game data before saving
        if game_state.current_location:
            game_state.game_data["location"] = game_state.current_location.name

        # Update settings in game data
        if "settings" not in game_state.game_data:
            game_state.game_data["settings"] = {}
        game_state.game_data["settings"]["autosave_enabled"] = game_state.autosave_enabled
        game_state.game_data["settings"]["autosave_frequency"] = game_state.autosave_frequency

        save_file = game_state.save_game(save_name)
        output.write("")
        output.write("[bold green]✓ Game saved![/bold green]")
        output.write(f"  📁 {save_file.name}")
        output.write(f"  [dim]{save_file}[/dim]")
        output.write("")

        # Check if we should quit after saving
        if get_pending_data("quit_after_save"):
            # Clear the flag before exiting
            set_pending_data("quit_after_save", False)
            safe_exit_cb()
        else:
            # Clear any save-related flags after successful save
            clear_pending_data()
    except Exception as e:
        output.write("")
        output.write(f"[red]❌ Failed to save game:[/red] {e}")
        output.write("")

        # If save failed and we were trying to quit, still ask if user wants to quit
        if get_pending_data("quit_after_save"):
            output.write("[yellow]Save failed! Do you still want to quit without saving?[/yellow]")
            output.write("  [red]Yes[/red] - Quit without saving")
            output.write("  [green]No[/green] - Stay in game")
            output.write("")
            # Clear quit flag and set confirm to handle failed save quit
            set_pending_data("quit_after_save", False)
            set_pending_data("failed_save_quit", True)
            set_pending_command("confirm_quit")
