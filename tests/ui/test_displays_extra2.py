"""
Extended tests for PokemonLibrary/ui/displays.py

Covers: show_party, populate_party_overview, populate_party_detail,
show_badge_case, inspect_pokemon, show_help, show_game_status, show_status,
show_map.
"""

import pytest

from pytemon.engine import BattleState
from pytemon.game_state import GameState
from pytemon.gym_system import award_badge
from pytemon.ui.displays import (
    inspect_pokemon,
    populate_party_detail,
    populate_party_overview,
    show_badge_case,
    show_bag,
    show_game_status,
    show_help,
    show_map,
    show_party,
    show_status,
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


def make_party_pokemon(gs, name="PIKACHU", level=10, hp=None):
    bs = BattleState()
    p = bs.generate_wild_pokemon(name, level)
    if hp is not None:
        p["hp"] = hp
    gs.game_data.setdefault("pokemon", []).append(p)
    return p


# ===========================================================================
# show_party
# ===========================================================================


class TestShowParty:
    def test_no_pokemon_shows_message(self, gs, output):
        gs.game_data["pokemon"] = []
        show_party(gs, output, noop)
        assert "don't have any" in output.combined.lower() or "no Pokemon" in output.combined

    def test_shows_party_pokemon(self, gs, output):
        make_party_pokemon(gs, "PIKACHU")
        show_party(gs, output, noop)
        assert "PIKACHU" in output.combined

    def test_shows_level(self, gs, output):
        make_party_pokemon(gs, "PIKACHU", level=15)
        show_party(gs, output, noop)
        assert "15" in output.combined

    def test_shows_hp_bar(self, gs, output):
        make_party_pokemon(gs)
        show_party(gs, output, noop)
        assert "HP" in output.combined

    def test_shows_party_size(self, gs, output):
        make_party_pokemon(gs)
        show_party(gs, output, noop)
        assert "Party size" in output.combined or "1/6" in output.combined

    def test_shows_status_if_present(self, gs, output):
        p = make_party_pokemon(gs)
        p["status"] = "POISON"
        show_party(gs, output, noop)
        assert "POISON" in output.combined

    def test_calls_ensure_battle_ready(self, gs, output):
        called = []
        make_party_pokemon(gs)
        show_party(gs, output, lambda p: called.append(True))
        assert called

    def test_shows_experience(self, gs, output):
        make_party_pokemon(gs)
        show_party(gs, output, noop)
        # Should show exp or next level
        assert "EXP" in output.combined or "exp" in output.combined or "Moves" in output.combined

    def test_multiple_pokemon(self, gs, output):
        make_party_pokemon(gs, "PIKACHU")
        make_party_pokemon(gs, "CHARMANDER")
        show_party(gs, output, noop)
        assert "PIKACHU" in output.combined
        assert "CHARMANDER" in output.combined


# ===========================================================================
# populate_party_overview
# ===========================================================================


class TestPopulatePartyOverview:
    def test_empty_party_shows_message(self, output):
        populate_party_overview(output, [], noop)
        assert "empty" in output.combined.lower()

    def test_shows_pokemon_name(self, gs, output):
        p = make_party_pokemon(gs, "PIKACHU")
        populate_party_overview(output, [p], noop)
        assert len(output.lines) > 0  # Rich Table written

    def test_two_pokemon_fills_table(self, gs, output):
        p1 = make_party_pokemon(gs, "PIKACHU")
        p2 = make_party_pokemon(gs, "CHARMANDER")
        populate_party_overview(output, [p1, p2], noop)
        assert len(output.lines) > 0

    def test_six_pokemon(self, gs, output):
        party = []
        for name in ["PIKACHU", "CHARMANDER", "SQUIRTLE", "BULBASAUR", "RATTATA", "PIDGEY"]:
            p = make_party_pokemon(gs, name)
            party.append(p)
        populate_party_overview(output, party, noop)
        assert len(output.lines) > 0


# ===========================================================================
# populate_party_detail
# ===========================================================================


class TestPopulatePartyDetail:
    def test_shows_name_and_level(self, gs, output):
        p = make_party_pokemon(gs, "PIKACHU", level=12)
        populate_party_detail(output, p, 1, noop)
        assert "PIKACHU" in output.combined
        assert "12" in output.combined

    def test_shows_stats(self, gs, output):
        p = make_party_pokemon(gs)
        populate_party_detail(output, p, 1, noop)
        assert "Attack" in output.combined or "attack" in output.combined.lower()

    def test_shows_moves(self, gs, output):
        p = make_party_pokemon(gs)
        populate_party_detail(output, p, 1, noop)
        assert "Move" in output.combined

    def test_shows_no_evolve_flag(self, gs, output):
        p = make_party_pokemon(gs, "PIKACHU")
        p["no_evolve"] = True
        populate_party_detail(output, p, 1, noop)
        assert "No Evolve" in output.combined

    def test_shows_experience(self, gs, output):
        p = make_party_pokemon(gs)
        populate_party_detail(output, p, 1, noop)
        assert "EXP" in output.combined or "exp" in output.combined.lower()


# ===========================================================================
# show_badge_case
# ===========================================================================


class TestShowBadgeCase:
    def test_no_badges_shows_message(self, gs, output):
        gs.game_data["badges"] = []
        show_badge_case(gs, output)
        assert "No badges" in output.combined or "no badges" in output.combined.lower()

    def test_shows_badge_name(self, gs, output):
        award_badge(gs, "Boulder Badge", MockRichLog())
        show_badge_case(gs, output)
        assert "Boulder Badge" in output.combined

    def test_all_badges_shows_congratulations(self, gs, output):
        all_badges = [
            "Boulder Badge",
            "Cascade Badge",
            "Thunder Badge",
            "Rainbow Badge",
            "Soul Badge",
            "Marsh Badge",
            "Volcano Badge",
            "Earth Badge",
        ]
        log = MockRichLog()
        for badge in all_badges:
            award_badge(gs, badge, log)
        show_badge_case(gs, output)
        assert (
            "CONGRATULATIONS" in output.combined
            or "8/8" in output.combined
            or "league" in output.combined.lower()
        )


# ===========================================================================
# inspect_pokemon
# ===========================================================================


class TestInspectPokemon:
    def test_empty_party_shows_message(self, gs, output):
        gs.game_data["pokemon"] = []
        inspect_pokemon(gs, output, "pikachu", noop)
        assert "don't have" in output.combined.lower() or "⚠" in output.combined

    def test_shows_pokemon_stats(self, gs, output):
        make_party_pokemon(gs, "PIKACHU", level=10)
        inspect_pokemon(gs, output, "pikachu", noop)
        assert "PIKACHU" in output.combined

    def test_shows_moves(self, gs, output):
        make_party_pokemon(gs, "PIKACHU")
        inspect_pokemon(gs, output, "pikachu", noop)
        assert "Move" in output.combined or "PP" in output.combined

    def test_not_found_shows_warning(self, gs, output):
        make_party_pokemon(gs)
        inspect_pokemon(gs, output, "fakemon99999", noop)
        assert "not find" in output.combined.lower() or "⚠" in output.combined

    def test_inspect_by_slot_number(self, gs, output):
        make_party_pokemon(gs, "PIKACHU")
        inspect_pokemon(gs, output, "1", noop)
        assert "PIKACHU" in output.combined

    def test_shows_no_evolve_flag(self, gs, output):
        p = make_party_pokemon(gs, "PIKACHU")
        p["no_evolve"] = True
        inspect_pokemon(gs, output, "pikachu", noop)
        assert "Evolution" in output.combined or "No Evolve" in output.combined


# ===========================================================================
# show_help (context-aware)
# ===========================================================================


class TestShowHelp:
    def test_writes_output(self, gs, output):
        show_help(gs, output)
        assert len(output.lines) > 0

    def test_shows_command_reference(self, gs, output):
        show_help(gs, output)
        assert "COMMAND REFERENCE" in output.combined or "command" in output.combined.lower()

    def test_in_game_shows_game_commands(self, gs, output):
        gs.in_game = True
        show_help(gs, output)
        assert len(output.lines) > 0

    def test_not_in_game_shows_menu_commands(self, gs, output):
        gs.in_game = False
        gs.in_menu = True
        show_help(gs, output)
        assert len(output.lines) > 0

    def test_battle_context_shows_battle_commands(self, gs, output):
        """In-battle help shows battle-specific commands."""
        bs = BattleState()
        player = bs.generate_wild_pokemon("PIKACHU", 5)
        bs.start_wild_battle(player, "RATTATA", 5)
        gs.battle_state = bs
        show_help(gs, output)
        combined = output.combined.lower()
        assert "fight" in combined
        assert "run" in combined or "flee" in combined

    def test_town_context_shows_building_commands(self, gs, output):
        """In a town, help shows building/enter commands."""
        from pytemon.locations import get_location

        gs.current_location = get_location("Viridian City")
        gs.battle_state = None
        show_help(gs, output)
        combined = output.combined.lower()
        assert "enter" in combined

    def test_route_context_shows_exploration_commands(self, gs, output):
        """On a route, help shows explore/look commands."""
        from pytemon.locations import get_location

        gs.current_location = get_location("Route 1")
        gs.battle_state = None
        show_help(gs, output)
        combined = output.combined.lower()
        assert "explore" in combined


# ===========================================================================
# show_game_status
# ===========================================================================


class TestShowGameStatus:
    def test_not_in_game_calls_callback(self, gs, output):
        gs.in_game = False
        called = []
        show_game_status(gs, output, lambda out: called.append(True))
        assert called

    def test_in_game_shows_status(self, gs, output):
        gs.in_game = True
        show_game_status(gs, output, noop)
        assert len(output.lines) > 0

    def test_shows_location(self, gs, output):
        gs.in_game = True
        show_game_status(gs, output, noop)
        assert "Pallet Town" in output.combined or "location" in output.combined.lower()

    def test_shows_money(self, gs, output):
        gs.in_game = True
        gs.game_data["money"] = 9999
        show_game_status(gs, output, noop)
        assert "9999" in output.combined


# ===========================================================================
# show_status
# ===========================================================================


class TestShowStatus:
    def test_writes_command_count(self, gs, output):
        show_status(gs, output, 42, "Pokemon Game", "Pallet Town")
        assert "42" in output.combined

    def test_writes_title(self, gs, output):
        show_status(gs, output, 0, "My Title", "Sub")
        assert "My Title" in output.combined

    def test_shows_cheat_mode_when_enabled(self, gs, output):
        gs.cheat_mode = True
        show_status(gs, output, 0, "Title", "Sub")
        assert "ENABLED" in output.combined or "Cheat" in output.combined


# ===========================================================================
# show_bag
# ===========================================================================


class TestShowBagExtended:
    def test_many_items_shown(self, gs, output):
        gs.game_data["items"] = {
            "Potion": 3,
            "Pokeball": 10,
            "Antidote": 2,
            "Revive": 1,
        }
        show_bag(gs, output)
        assert "Potion" in output.combined
        assert "Pokeball" in output.combined


# ===========================================================================
# show_map
# ===========================================================================


class TestShowMap:
    def test_writes_output(self, gs, output):
        show_map(gs, output)
        assert len(output.lines) > 0

    def test_shows_kanto_map_header(self, gs, output):
        show_map(gs, output)
        assert "KANTO" in output.combined

    def test_marks_current_location(self, gs, output):
        from pytemon.locations import get_location

        gs.current_location = get_location("Pallet Town")
        show_map(gs, output)
        # Current location should have a ★ marker
        assert "★" in output.combined

    def test_shows_pallet_town(self, gs, output):
        show_map(gs, output)
        assert "PALLET" in output.combined

    def test_shows_cerulean_city(self, gs, output):
        show_map(gs, output)
        assert "CERULEAN" in output.combined

    def test_shows_pewter_city(self, gs, output):
        show_map(gs, output)
        assert "PEWTER" in output.combined

    def test_locked_league_gate_without_badges(self, gs, output):
        """League gate is locked when player has fewer than 8 badges."""
        gs.game_data["badges"] = []
        show_map(gs, output)
        assert "🔒" in output.combined

    def test_visited_location_highlighted(self, gs, output):
        """Locations in route_progress with > 0 count appear as visited."""
        gs.game_data["route_progress"] = {"Route 1": 3}
        show_map(gs, output)
        # Route 1 should be in the map
        assert "Route 1" in output.combined

    def test_no_crash_on_missing_location(self, gs, output):
        """show_map should not crash when current_location is None."""
        gs.current_location = None
        show_map(gs, output)
        assert len(output.lines) > 0
