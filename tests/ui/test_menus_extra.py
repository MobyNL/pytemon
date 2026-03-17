"""
Extended tests for PokemonLibrary/ui/menus.py

Covers: show_main_menu, process_menu_command, start_new_game, show_load_menu,
check_autosave, perform_autosave, should_ignore_for_autosave, show_settings,
return_to_menu, save_current_game, handle_save_name, handle_overwrite_confirmation,
perform_save, load_selected_save.
"""

import json
import tempfile
from pathlib import Path

import pytest

from pytemon.game_state import GameState
from pytemon.ui.menus import (
    check_autosave,
    handle_overwrite_confirmation,
    handle_save_name,
    perform_autosave,
    perform_save,
    process_menu_command,
    return_to_menu,
    save_current_game,
    should_ignore_for_autosave,
    show_load_menu,
    show_main_menu,
    show_settings,
    start_new_game,
)


class MockRichLog:
    def __init__(self):
        self.lines = []

    def write(self, text) -> None:
        self.lines.append(str(text))

    def clear(self) -> None:
        self.lines.clear()

    @property
    def combined(self) -> str:
        return " ".join(self.lines)


@pytest.fixture
def gs() -> GameState:
    gs = GameState()
    gs.start_new_game()
    return gs


@pytest.fixture
def output() -> MockRichLog:
    return MockRichLog()


def noop(*_a, **_kw):
    pass


# ===========================================================================
# show_main_menu
# ===========================================================================


class TestShowMainMenuExtra:
    def test_writes_output(self, output):
        show_main_menu(output)
        assert len(output.lines) > 0

    def test_clears_and_writes(self, output):
        output.write("old content")
        show_main_menu(output)
        # After show_main_menu, the menu contains the game title and MAIN MENU header
        assert "POKEMON" in output.combined and "MAIN MENU" in output.combined


# ===========================================================================
# process_menu_command
# ===========================================================================


class TestProcessMenuCommand:
    def _call(
        self,
        command,
        output,
        gs,
        start_cb=None,
        load_cb=None,
        exit_cb=None,
        load_save_cb=None,
        has_saves=None,
        delete_saves=None,
    ):
        """Helper to call process_menu_command with defaults."""
        process_menu_command(
            gs,
            command,
            output,
            start_new_game_cb=start_cb or noop,
            show_load_menu_cb=load_cb or noop,
            exit_cb=exit_cb or noop,
            load_selected_save_cb=load_save_cb or noop,
            has_temp_saves_list=has_saves or (lambda: False),
            delete_temp_saves_list=delete_saves or noop,
        )

    def test_start_new_game_command(self, gs, output):
        called = []
        self._call("start", output, gs, start_cb=lambda out: called.append(True))
        assert called

    def test_new_game_command(self, gs, output):
        called = []
        self._call("new game", output, gs, start_cb=lambda out: called.append(True))
        assert called

    def test_load_command(self, gs, output):
        called = []
        self._call("load", output, gs, load_cb=lambda out: called.append(True))
        assert called

    def test_exit_command(self, gs, output):
        called = []
        self._call("exit", output, gs, exit_cb=lambda: called.append(True))
        assert called

    def test_quit_command(self, gs, output):
        called = []
        self._call("quit", output, gs, exit_cb=lambda: called.append(True))
        assert called

    def test_unknown_command_shows_error(self, gs, output):
        self._call("blargblarg", output, gs)
        assert "Invalid command" in output.combined or "❌" in output.combined

    def test_in_saves_list_back_command(self, gs, output):
        deleted = []
        self._call(
            "back",
            output,
            gs,
            has_saves=lambda: True,
            delete_saves=lambda: deleted.append(True),
        )
        assert deleted

    def test_in_saves_list_delegates_to_load(self, gs, output):
        called = []
        self._call(
            "my_save",
            output,
            gs,
            load_save_cb=lambda cmd, out: called.append(cmd),
            has_saves=lambda: True,
        )
        assert "my_save" in called


# ===========================================================================
# start_new_game
# ===========================================================================


class TestStartNewGame:
    def test_writes_welcome_message(self, gs, output):
        start_new_game(gs, output, noop)
        assert "Welcome" in output.combined or "Starting" in output.combined

    def test_shows_pallet_town(self, gs, output):
        start_new_game(gs, output, noop)
        assert "Pallet Town" in output.combined

    def test_game_state_is_new_game(self, gs, output):
        start_new_game(gs, output, noop)
        assert gs.game_data.get("money", 0) > 0


# ===========================================================================
# show_load_menu
# ===========================================================================


class TestShowLoadMenu:
    def test_no_saves_shows_message(self, gs, output):
        with tempfile.TemporaryDirectory() as tmpdir:
            gs.saves_dir = Path(tmpdir)
            saves_list = []
            show_load_menu(gs, output, lambda saves: saves_list.extend(saves))
        assert "No save files" in output.combined or "no save" in output.combined.lower()

    def test_with_saves_shows_list(self, gs, output):
        with tempfile.TemporaryDirectory() as tmpdir:
            gs.saves_dir = Path(tmpdir)
            # Create a dummy save file
            save_data = {"location": "Pallet Town", "badges": []}
            save_file = Path(tmpdir) / "testsave.json"
            save_file.write_text(json.dumps(save_data))
            saves_list = []
            show_load_menu(gs, output, lambda saves: saves_list.extend(saves))
        assert "testsave" in output.combined


# ===========================================================================
# should_ignore_for_autosave
# ===========================================================================


class TestShouldIgnoreForAutosaveExtra:
    def test_pokedex_not_ignored(self):
        # Custom - not in the ignore list
        assert should_ignore_for_autosave("pokedex") is False

    def test_about_is_ignored(self):
        assert should_ignore_for_autosave("about") is True

    def test_autosave_command_is_ignored(self):
        assert should_ignore_for_autosave("autosave") is True


# ===========================================================================
# check_autosave
# ===========================================================================


class TestCheckAutosave:
    def test_disabled_autosave_does_nothing(self, gs, output):
        gs.autosave_enabled = False
        called = []
        check_autosave(gs, "move", output, lambda out: called.append(True))
        assert not called

    def test_in_battle_does_nothing(self, gs, output):
        gs.in_battle = True
        called = []
        check_autosave(gs, "move", output, lambda out: called.append(True))
        assert not called

    def test_ignored_command_does_not_count(self, gs, output):
        gs.autosave_enabled = True
        gs.commands_since_autosave = 0
        check_autosave(gs, "help", output, noop)
        assert gs.commands_since_autosave == 0

    def test_normal_command_increments_counter(self, gs, output):
        gs.autosave_enabled = True
        gs.commands_since_autosave = 0
        check_autosave(gs, "move north", output, noop)
        assert gs.commands_since_autosave == 1

    def test_triggers_autosave_when_at_frequency(self, gs, output):
        gs.autosave_enabled = True
        gs.autosave_frequency = 5
        gs.commands_since_autosave = 4
        called = []
        check_autosave(gs, "explore", output, lambda out: called.append(True))
        assert called


# ===========================================================================
# perform_autosave
# ===========================================================================


class TestPerformAutosave:
    def test_saves_and_writes_notification(self, gs, output):
        with tempfile.TemporaryDirectory() as tmpdir:
            gs.saves_dir = Path(tmpdir)
            gs.game_data["player_name"] = "TestPlayer"
            perform_autosave(gs, output)
        assert "Autosaved" in output.combined or "autosave" in output.combined.lower()

    def test_resets_counter(self, gs, output):
        gs.commands_since_autosave = 10
        with tempfile.TemporaryDirectory() as tmpdir:
            gs.saves_dir = Path(tmpdir)
            perform_autosave(gs, output)
        assert gs.commands_since_autosave == 0


# ===========================================================================
# show_settings
# ===========================================================================


class TestShowSettings:
    def test_shows_autosave_setting(self, gs, output):
        show_settings(gs, output)
        assert "Autosave" in output.combined

    def test_shows_enabled_status(self, gs, output):
        gs.autosave_enabled = True
        show_settings(gs, output)
        assert "Enabled" in output.combined

    def test_shows_disabled_status(self, gs, output):
        gs.autosave_enabled = False
        show_settings(gs, output)
        assert "Disabled" in output.combined

    def test_shows_frequency(self, gs, output):
        gs.autosave_frequency = 10
        show_settings(gs, output)
        assert "10" in output.combined


# ===========================================================================
# return_to_menu
# ===========================================================================


class TestReturnToMenu:
    def test_sets_in_menu(self, gs, output):
        gs.in_menu = False
        gs.in_game = True
        return_to_menu(gs, output, noop)
        assert gs.in_menu is True
        assert gs.in_game is False

    def test_calls_show_main_menu(self, gs, output):
        called = []
        return_to_menu(gs, output, lambda out: called.append(True))
        assert called


# ===========================================================================
# save_current_game
# ===========================================================================


class TestSaveCurrentGame:
    def test_writes_save_prompt(self, gs, output):
        pending = []
        save_current_game(gs, output, lambda cmd: pending.append(cmd))
        assert len(output.lines) > 0

    def test_sets_save_name_pending(self, gs, output):
        pending = []
        gs.game_data.pop("save_name", None)
        save_current_game(gs, output, lambda cmd: pending.append(cmd))
        assert "save_name" in pending

    def test_with_existing_save_shows_options(self, gs, output):
        gs.game_data["save_name"] = "existing_save"
        pending = []
        save_current_game(gs, output, lambda cmd: pending.append(cmd))
        assert len(output.lines) > 0


# ===========================================================================
# handle_save_name
# ===========================================================================


class TestHandleSaveName:
    def test_empty_name_without_existing_save_creates_new(self, gs, output):
        saved_names = []
        gs.game_data.pop("save_name", None)
        with tempfile.TemporaryDirectory() as tmpdir:
            gs.saves_dir = Path(tmpdir)
            handle_save_name(
                gs,
                "",
                output,
                perform_save_cb=lambda name, out: saved_names.append(name),
                set_pending_command=noop,
                set_pending_data=noop,
            )
        assert None in saved_names  # None means auto-name

    def test_empty_name_with_existing_save_overwrites(self, gs, output):
        gs.game_data["save_name"] = "mysave"
        saved_names = []
        with tempfile.TemporaryDirectory() as tmpdir:
            gs.saves_dir = Path(tmpdir)
            handle_save_name(
                gs,
                "",
                output,
                perform_save_cb=lambda name, out: saved_names.append(name),
                set_pending_command=noop,
                set_pending_data=noop,
            )
        assert "mysave" in saved_names

    def test_new_save_name_calls_perform_save(self, gs, output):
        saved_names = []
        gs.game_data.pop("save_name", None)
        with tempfile.TemporaryDirectory() as tmpdir:
            gs.saves_dir = Path(tmpdir)
            handle_save_name(
                gs,
                "newsave",
                output,
                perform_save_cb=lambda name, out: saved_names.append(name),
                set_pending_command=noop,
                set_pending_data=noop,
            )
        assert "newsave" in saved_names

    def test_existing_save_name_prompts_overwrite(self, gs, output):
        pending = []
        gs.game_data.pop("save_name", None)
        with tempfile.TemporaryDirectory() as tmpdir:
            gs.saves_dir = Path(tmpdir)
            # Create the save file
            save_file = Path(tmpdir) / "existing.json"
            save_file.write_text('{"location":"Pallet Town"}')
            handle_save_name(
                gs,
                "existing",
                output,
                perform_save_cb=noop,
                set_pending_command=lambda cmd: pending.append(cmd),
                set_pending_data=noop,
            )
        assert "confirm_overwrite" in pending

    def test_select_option_1_overwrites_current(self, gs, output):
        gs.game_data["save_name"] = "current_save"
        saved_names = []
        with tempfile.TemporaryDirectory() as tmpdir:
            gs.saves_dir = Path(tmpdir)
            handle_save_name(
                gs,
                "1",
                output,
                perform_save_cb=lambda name, out: saved_names.append(name),
                set_pending_command=noop,
                set_pending_data=noop,
            )
        assert "current_save" in saved_names

    def test_overwrite_keyword_overwrites_current(self, gs, output):
        """Typing 'overwrite' (not '1') should still overwrite the current save."""
        gs.game_data["save_name"] = "my_save"
        saved_names = []
        with tempfile.TemporaryDirectory() as tmpdir:
            gs.saves_dir = Path(tmpdir)
            handle_save_name(
                gs,
                "overwrite",
                output,
                perform_save_cb=lambda name, out: saved_names.append(name),
                set_pending_command=noop,
                set_pending_data=noop,
            )
        assert "my_save" in saved_names

    def test_overwrite_with_save_name_overwrites_current(self, gs, output):
        """Typing 'overwrite my_save' should overwrite the current save, not create a new file."""
        gs.game_data["save_name"] = "my_save"
        saved_names = []
        with tempfile.TemporaryDirectory() as tmpdir:
            gs.saves_dir = Path(tmpdir)
            handle_save_name(
                gs,
                "overwrite my_save",
                output,
                perform_save_cb=lambda name, out: saved_names.append(name),
                set_pending_command=noop,
                set_pending_data=noop,
            )
        assert "my_save" in saved_names
        assert not any("overwrite" in str(n).lower() for n in saved_names if n), (
            "Save name should not contain 'overwrite'"
        )

    def test_space_in_save_name_is_rejected(self, gs, output):
        """A save name with spaces must be rejected and pending command re-armed."""
        gs.game_data.pop("save_name", None)
        pending = []
        with tempfile.TemporaryDirectory() as tmpdir:
            gs.saves_dir = Path(tmpdir)
            handle_save_name(
                gs,
                "my save file",
                output,
                perform_save_cb=noop,
                set_pending_command=lambda cmd: pending.append(cmd),
                set_pending_data=noop,
            )
        assert "save_name" in pending
        assert any(
            "space" in str(line).lower() or "cannot" in str(line).lower() for line in output.lines
        )

    def test_option_2_rearms_pending_command(self, gs, output):
        """Selecting option '2' must re-arm the save_name pending command."""
        gs.game_data["save_name"] = "current_save"
        pending = []
        with tempfile.TemporaryDirectory() as tmpdir:
            gs.saves_dir = Path(tmpdir)
            handle_save_name(
                gs,
                "2",
                output,
                perform_save_cb=noop,
                set_pending_command=lambda cmd: pending.append(cmd),
                set_pending_data=noop,
            )
        assert "save_name" in pending


# ===========================================================================
# handle_overwrite_confirmation
# ===========================================================================


class TestHandleOverwriteConfirmation:
    def test_yes_performs_save(self, output):
        saved = []
        handle_overwrite_confirmation(
            "yes",
            output,
            get_pending_data=lambda key: "oldsave",
            perform_save_cb=lambda name, out: saved.append(name),
            set_pending_command=noop,
        )
        assert "oldsave" in saved

    def test_y_performs_save(self, output):
        saved = []
        handle_overwrite_confirmation(
            "y",
            output,
            get_pending_data=lambda key: "oldsave",
            perform_save_cb=lambda name, out: saved.append(name),
            set_pending_command=noop,
        )
        assert "oldsave" in saved

    def test_no_cancels(self, output):
        pending = []
        handle_overwrite_confirmation(
            "no",
            output,
            get_pending_data=lambda key: "oldsave",
            perform_save_cb=noop,
            set_pending_command=lambda cmd: pending.append(cmd),
        )
        assert "save_name" in pending

    def test_invalid_response_asks_again(self, output):
        pending = []
        handle_overwrite_confirmation(
            "maybe",
            output,
            get_pending_data=lambda key: "oldsave",
            perform_save_cb=noop,
            set_pending_command=lambda cmd: pending.append(cmd),
        )
        assert "confirm_overwrite" in pending


# ===========================================================================
# perform_save
# ===========================================================================


class TestPerformSave:
    def test_saves_game_successfully(self, gs, output):
        with tempfile.TemporaryDirectory() as tmpdir:
            gs.saves_dir = Path(tmpdir)
            perform_save(
                gs,
                "testsave",
                output,
                get_pending_data=lambda key: None,
                clear_pending_data=noop,
                set_pending_data=noop,
                set_pending_command=noop,
                safe_exit_cb=noop,
            )
        assert "saved" in output.combined.lower() or "✓" in output.combined

    def test_quit_after_save_triggers_exit(self, gs, output):
        exited = []
        with tempfile.TemporaryDirectory() as tmpdir:
            gs.saves_dir = Path(tmpdir)
            perform_save(
                gs,
                "qsave",
                output,
                get_pending_data=lambda key: True if key == "quit_after_save" else None,
                clear_pending_data=noop,
                set_pending_data=noop,
                set_pending_command=noop,
                safe_exit_cb=lambda: exited.append(True),
            )
        assert exited

    def test_exception_shows_error_message(self, gs, output):
        # Use a path that cannot be written to
        gs.saves_dir = Path("/nonexistent/path/99999")
        perform_save(
            gs,
            "badsave",
            output,
            get_pending_data=lambda key: None,
            clear_pending_data=noop,
            set_pending_data=noop,
            set_pending_command=noop,
            safe_exit_cb=noop,
        )
        assert "❌" in output.combined or "Failed" in output.combined
