"""Tests for terminal subtitle rendering in the top welcome banner."""

from pytemon.game_state import GameState
from pytemon.locations import get_location
from pytemon.terminal import PokemonTerminal


class _MockWelcome:
    def __init__(self):
        self.last_text = ""

    def update(self, text: str) -> None:
        self.last_text = str(text)


class _SubtitleTerminal:
    """Minimal terminal double that reuses PokemonTerminal._refresh_subtitle."""

    _refresh_subtitle = PokemonTerminal._refresh_subtitle

    def __init__(self):
        self.game_state = GameState()
        self.game_state.start_new_game()
        self._welcome = _MockWelcome()

    def query_one(self, selector, widget_type=None):
        if selector == "#welcome":
            return self._welcome
        raise AssertionError(f"Unexpected selector: {selector}")


class TestTerminalSubtitle:
    def test_shows_location_when_not_in_building(self):
        term = _SubtitleTerminal()
        term.game_state.current_location = get_location("Pallet Town")
        term.game_state.game_data.pop("_active_building", None)

        term._refresh_subtitle()

        assert "📍" in term._welcome.last_text
        assert "Pallet Town" in term._welcome.last_text

    def test_shows_building_header_when_in_building_context(self):
        term = _SubtitleTerminal()
        term.game_state.current_location = get_location("Pallet Town")
        term.game_state.game_data["_active_building"] = "Professor Oak's Lab"

        term._refresh_subtitle()

        assert "🏛" in term._welcome.last_text
        assert "Professor Oak's Lab" in term._welcome.last_text
        assert "Inside Pallet Town" in term._welcome.last_text
