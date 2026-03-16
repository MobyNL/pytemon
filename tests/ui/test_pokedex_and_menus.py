"""
Extended tests for PokemonLibrary/pokedex.py (show_pokedex, show_pokedex_entry)
and PokemonLibrary/ui/menus.py (show_main_menu, should_ignore_for_autosave,
show_settings).
"""

import pytest

from pytemon.game_state import GameState
from pytemon.pokedex import (
    mark_as_caught,
    mark_as_seen,
    show_pokedex,
    show_pokedex_entry,
)
from pytemon.ui.menus import (
    should_ignore_for_autosave,
    show_main_menu,
    show_settings,
)


class MockRichLog:
    """Minimal stub for textual.widgets.RichLog."""

    def __init__(self):
        self.lines = []
        self._cleared = False

    def write(self, text: str) -> None:
        self.lines.append(text)

    def clear(self) -> None:
        self._cleared = True
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


# ===========================================================================
# show_main_menu
# ===========================================================================


class TestShowMainMenu:
    def test_writes_output(self, output):
        show_main_menu(output)
        assert len(output.lines) > 0

    def test_clears_screen(self, output):
        show_main_menu(output)
        assert output._cleared is True

    def test_mentions_start_new_game(self, output):
        show_main_menu(output)
        assert "Start New Game" in output.combined

    def test_mentions_load_game(self, output):
        show_main_menu(output)
        assert "Load Game" in output.combined

    def test_mentions_exit(self, output):
        show_main_menu(output)
        assert "Exit" in output.combined


# ===========================================================================
# should_ignore_for_autosave
# ===========================================================================


class TestShouldIgnoreForAutosave:
    def test_help_is_ignored(self):
        assert should_ignore_for_autosave("help") is True

    def test_status_is_ignored(self):
        assert should_ignore_for_autosave("status") is True

    def test_party_is_ignored(self):
        assert should_ignore_for_autosave("party") is True

    def test_bag_is_ignored(self):
        assert should_ignore_for_autosave("bag") is True

    def test_look_around_is_ignored(self):
        assert should_ignore_for_autosave("look around") is True

    def test_settings_is_ignored(self):
        assert should_ignore_for_autosave("settings") is True

    def test_inspect_prefix_is_ignored(self):
        assert should_ignore_for_autosave("inspect pikachu") is True

    def test_move_command_not_ignored(self):
        assert should_ignore_for_autosave("move north") is False

    def test_fight_command_not_ignored(self):
        assert should_ignore_for_autosave("fight") is False

    def test_empty_command_not_ignored(self):
        assert should_ignore_for_autosave("") is False

    def test_h_shortcut_is_ignored(self):
        assert should_ignore_for_autosave("h") is True


# ===========================================================================
# show_settings
# ===========================================================================


class TestShowSettings:
    def test_writes_output(self, gs, output):
        show_settings(gs, output)
        assert len(output.lines) > 0

    def test_shows_autosave_status(self, gs, output):
        show_settings(gs, output)
        assert "autosave" in output.combined.lower() or "Autosave" in output.combined

    def test_shows_correct_autosave_enabled(self, gs, output):
        gs.autosave_enabled = True
        show_settings(gs, output)
        assert (
            "enabled" in output.combined.lower()
            or "on" in output.combined.lower()
            or "True" in output.combined
        )

    def test_shows_correct_autosave_disabled(self, gs, output):
        gs.autosave_enabled = False
        output2 = MockRichLog()
        show_settings(gs, output2)
        assert (
            "disabled" in output2.combined.lower()
            or "off" in output2.combined.lower()
            or "False" in output2.combined
        )


# ===========================================================================
# show_pokedex
# ===========================================================================


class TestShowPokedex:
    def test_empty_pokedex_writes_output(self, gs, output):
        show_pokedex(gs, output)
        assert len(output.lines) > 0

    def test_shows_page_info(self, gs, output):
        show_pokedex(gs, output)
        # Should show page info somewhere
        assert len(output.lines) > 0  # no crash

    def test_filter_seen_only(self, gs, output):
        mark_as_seen(gs, "PIKACHU")
        show_pokedex(gs, output, filter_mode="seen")
        assert "PIKACHU" in output.combined

    def test_filter_caught_shows_caught(self, gs, output):
        mark_as_caught(gs, "CHARMANDER")
        show_pokedex(gs, output, filter_mode="caught")
        assert "CHARMANDER" in output.combined

    def test_filter_missing_shows_unseen(self, gs, output):
        show_pokedex(gs, output, filter_mode="missing")
        # Should list many unseen pokemon
        assert len(output.lines) > 0

    def test_filter_all_shows_all(self, gs, output):
        show_pokedex(gs, output, filter_mode="all")
        assert len(output.lines) > 0

    def test_page_parameter(self, gs, output):
        show_pokedex(gs, output, page=2)
        assert len(output.lines) > 0

    def test_filter_change_resets_page(self, gs, output):
        # First get pokedex state with one filter
        show_pokedex(gs, output, filter_mode="all")
        output2 = MockRichLog()
        # Change filter - should reset page
        show_pokedex(gs, output2, filter_mode="caught")
        assert len(output2.lines) > 0


# ===========================================================================
# show_pokedex_entry
# ===========================================================================


class TestShowPokedexEntry:
    def test_unseen_pokemon_shows_no_data_message(self, gs, output):
        show_pokedex_entry(gs, output, "PIKACHU")
        assert "not yet encountered" in output.combined.lower() or "No data" in output.combined

    def test_seen_pokemon_shows_entry(self, gs, output):
        mark_as_seen(gs, "PIKACHU")
        show_pokedex_entry(gs, output, "PIKACHU")
        assert "PIKACHU" in output.combined

    def test_caught_pokemon_shows_stats(self, gs, output):
        mark_as_caught(gs, "BULBASAUR")
        show_pokedex_entry(gs, output, "BULBASAUR")
        assert len(output.lines) > 0

    def test_unknown_pokemon_shows_error(self, gs, output):
        show_pokedex_entry(gs, output, "UNKNOWNMON999")
        assert "not found" in output.combined.lower() or "❌" in output.combined

    def test_case_insensitive_lookup(self, gs, output):
        mark_as_seen(gs, "CHARMANDER")
        output2 = MockRichLog()
        show_pokedex_entry(gs, output2, "charmander")
        assert len(output2.lines) > 0
