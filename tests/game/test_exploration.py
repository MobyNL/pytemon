"""
Comprehensive tests for PokemonLibrary/exploration.py

Covers: move_to_location, prompt_for_location, prompt_for_building,
show_location_arrival, look_around, explore_area, get_explore_hint.
"""

import pytest

from pytemon.exploration import (
    explore_area,
    get_explore_hint,
    look_around,
    move_to_location,
    prompt_for_building,
    prompt_for_location,
    show_location_arrival,
)
from pytemon.game_state import GameState
from pytemon.locations import get_location


class MockRichLog:
    def __init__(self):
        self.lines = []

    def write(self, text: str) -> None:
        self.lines.append(text)

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


def make_party_pokemon(gs, name="PIKACHU", level=10):
    from pytemon.engine import BattleState

    bs = BattleState()
    p = bs.generate_wild_pokemon(name, level)
    gs.game_data.setdefault("pokemon", []).append(p)
    return p


# ===========================================================================
# move_to_location
# ===========================================================================


class TestMoveToLocation:
    def test_no_location_shows_error(self, gs, output):
        gs.current_location = None
        move_to_location(gs, "Route 1", output, noop)
        assert "No current location set" in output.combined

    def test_invalid_destination_shows_error(self, gs, output):
        move_to_location(gs, "Nonexistent Place 99999", output, noop)
        assert "can't go to" in output.combined.lower()

    def test_blocked_exit_shows_warning(self, gs, output):
        # Route 1 from Pallet Town blocked without Pokemon — Professor Oak stops you
        gs.cheat_mode = False
        gs.game_data["pokemon"] = []
        move_to_location(gs, "Route 1", output, noop)
        assert "Professor Oak" in output.combined

    def test_valid_move_changes_location(self, gs, output):
        gs.cheat_mode = True
        called = []
        move_to_location(gs, "Route 1", output, lambda out: called.append(True))
        assert gs.current_location.name == "Route 1"
        assert called

    def test_shows_travel_message(self, gs, output):
        gs.cheat_mode = True
        make_party_pokemon(gs)
        move_to_location(gs, "Route 1", output, noop)
        assert "Traveling" in output.combined or "traveling" in output.combined.lower()

    def test_case_insensitive_destination(self, gs, output):
        gs.cheat_mode = True
        move_to_location(gs, "route 1", output, noop)
        assert gs.current_location.name == "Route 1"

    def test_blocked_by_min_explores(self, gs, output):
        # Go to Route 1 first, then try to go to Viridian City without exploring
        gs.cheat_mode = True
        gs.current_location = get_location("Route 1")
        gs.game_data["previous_location"] = "Pallet Town"
        gs.cheat_mode = False
        make_party_pokemon(gs)
        move_to_location(gs, "Viridian City", output, noop)
        # Should be blocked because explore requirement not met
        assert "⚠" in output.combined
        assert "fully explored" in output.combined.lower()

    def test_cheat_mode_bypasses_explore_requirement(self, gs, output):
        gs.cheat_mode = True
        gs.current_location = get_location("Route 1")
        gs.game_data["previous_location"] = "Pallet Town"
        called = []
        move_to_location(gs, "Viridian City", output, lambda out: called.append(True))
        assert called  # Should have called arrival callback


# ===========================================================================
# prompt_for_location
# ===========================================================================


class TestPromptForLocation:
    def test_no_location_shows_error(self, gs, output):
        gs.current_location = None
        prompt_for_location(gs, output, noop)
        assert "No current location set" in output.combined

    def test_shows_available_exits(self, gs, output):
        pending = []
        prompt_for_location(gs, output, lambda cmd: pending.append(cmd))
        assert "Route 1" in output.combined
        assert "Where would you like to go" in output.combined

    def test_sets_move_to_pending_command(self, gs, output):
        pending = []
        prompt_for_location(gs, output, lambda cmd: pending.append(cmd))
        assert "move_to" in pending

    def test_panel_callback_called(self, gs, output):
        called = []
        prompt_for_location(
            gs, output, noop, show_panel_callback=lambda exits: called.append(exits)
        )
        assert called

    def test_no_exits_shows_message(self, gs, output):
        # Create a location with no exits
        from unittest.mock import MagicMock

        mock_loc = MagicMock()
        mock_loc.get_available_exits.return_value = []
        mock_loc.exits = {}
        mock_loc.name = "Isolated Place"
        gs.current_location = mock_loc
        pending = []
        prompt_for_location(gs, output, lambda cmd: pending.append(cmd))
        assert "no available paths" in output.combined.lower()


# ===========================================================================
# prompt_for_building
# ===========================================================================


class TestPromptForBuilding:
    def test_no_location_shows_error(self, gs, output):
        gs.current_location = None
        prompt_for_building(gs, output, noop)
        assert "No current location set" in output.combined

    def test_non_town_shows_no_buildings(self, gs, output):
        gs.current_location = get_location("Route 1")
        pending = []
        prompt_for_building(gs, output, lambda cmd: pending.append(cmd))
        assert "no buildings" in output.combined.lower()

    def test_town_shows_buildings(self, gs, output):
        # Pallet Town has buildings including Professor Oak's Lab
        pending = []
        prompt_for_building(gs, output, lambda cmd: pending.append(cmd))
        assert "Professor Oak's Lab" in output.combined

    def test_sets_enter_building_pending(self, gs, output):
        pending = []
        prompt_for_building(gs, output, lambda cmd: pending.append(cmd))
        assert "enter_building" in pending

    def test_panel_callback_called(self, gs, output):
        called = []
        prompt_for_building(
            gs, output, noop, show_panel_callback=lambda buildings: called.append(buildings)
        )
        assert called


# ===========================================================================
# show_location_arrival
# ===========================================================================


class TestShowLocationArrival:
    def test_no_location_shows_error(self, gs, output):
        gs.current_location = None
        show_location_arrival(gs, output)
        assert "No current location set" in output.combined

    def test_shows_location_name(self, gs, output):
        show_location_arrival(gs, output)
        assert "Pallet Town" in output.combined

    def test_load_message_is_load_true(self, gs, output):
        show_location_arrival(gs, output, is_load=True)
        assert "You find yourself in" in output.combined

    def test_route_shows_different_message(self, gs, output):
        gs.cheat_mode = True
        gs.current_location = get_location("Route 1")
        show_location_arrival(gs, output)
        assert "Route 1" in output.combined

    def test_arrival_shows_decorative_border(self, gs, output):
        show_location_arrival(gs, output)
        assert "═" in output.combined


# ===========================================================================
# look_around
# ===========================================================================


class TestLookAround:
    def test_no_location_shows_error(self, gs, output):
        gs.current_location = None
        look_around(gs, output)
        assert "No current location set" in output.combined

    def test_shows_available_paths(self, gs, output):
        look_around(gs, output)
        assert "Available Paths:" in output.combined

    def test_shows_buildings_for_town(self, gs, output):
        look_around(gs, output)
        assert "Buildings:" in output.combined

    def test_auto_flag_suppresses_header(self, gs, output):
        look_around(gs, output, auto=True)
        assert "Looking around" not in output.combined

    def test_route_shows_exploration_hint(self, gs, output):
        gs.current_location = get_location("Route 1")
        look_around(gs, output)
        assert "can be explored" in output.combined

    def test_shows_blocked_exits(self, gs, output):
        # Pallet Town has Route 21 blocked (requires HM Surf)
        look_around(gs, output)
        assert "Blocked Paths:" in output.combined
        assert "Route 21" in output.combined


# ===========================================================================
# explore_area
# ===========================================================================


class TestExploreArea:
    def test_no_location_shows_error(self, gs, output):
        gs.current_location = None
        explore_area(gs, output, noop, noop)
        assert "No current location set" in output.combined

    def test_town_cannot_be_explored(self, gs, output):
        explore_area(gs, output, noop, noop)
        assert "nothing to explore" in output.combined.lower()

    def test_route_without_pokemon_shows_warning(self, gs, output):
        gs.cheat_mode = True
        gs.current_location = get_location("Route 1")
        gs.game_data["pokemon"] = []
        explore_area(gs, output, noop, noop)
        assert "without Pokemon" in output.combined or "can't explore" in output.combined.lower()

    def test_route_with_pokemon_triggers_something(self, gs, output):
        gs.cheat_mode = True
        gs.current_location = get_location("Route 1")
        make_party_pokemon(gs)
        called = []
        explore_area(gs, output, lambda out: called.append("wild"), noop)
        # Either finds something or shows "nothing found"
        assert len(output.lines) > 0

    def test_route_increments_progress(self, gs, output):
        gs.cheat_mode = True
        gs.current_location = get_location("Route 1")
        make_party_pokemon(gs)
        initial = gs.get_route_progress("Route 1")
        explore_area(gs, output, noop, noop)
        assert gs.get_route_progress("Route 1") > initial

    def test_trainer_encounter_triggers_callback(self, gs, output):
        import random

        gs.cheat_mode = True
        gs.current_location = get_location("Route 1")
        make_party_pokemon(gs)
        trainer_encounters = []

        # Force trainer encounter by mocking random
        original_random = random.random
        try:
            random.random = lambda: 0.0  # always < encounter_rate
            explore_area(
                gs,
                output,
                lambda out: None,
                lambda out, trainer: trainer_encounters.append(trainer),
            )
        finally:
            random.random = original_random

        assert len(trainer_encounters) > 0


# ===========================================================================
# get_explore_hint
# ===========================================================================


class TestGetExploreHint:
    def test_town_returns_empty_string(self, gs):
        result = get_explore_hint(gs)
        assert result == ""

    def test_route_returns_hint(self, gs):
        gs.current_location = get_location("Route 1")
        result = get_explore_hint(gs)
        # Route 1 → Viridian City requires 3 explores; at 0 progress expect "more exploring needed"
        assert "Viridian City" in result

    def test_no_location_returns_empty(self, gs):
        gs.current_location = None
        result = get_explore_hint(gs)
        assert result == ""

    def test_route_with_progress(self, gs):
        gs.current_location = get_location("Route 1")
        # With Route 1 requiring 5 explores: at progress=4 (remaining=1) expect "almost there"
        loc = get_location("Route 1")
        required = loc.exits["Viridian City"].get("min_explores", 5)
        gs.game_data.setdefault("route_progress", {})["Route 1"] = required - 1
        result = get_explore_hint(gs)
        assert "Viridian City" in result
        assert "almost there" in result


# ===========================================================================
# Additional exploration tests
# ===========================================================================


class TestExploreAreaExtra:
    def test_no_location_shows_error(self, gs, output):
        from pytemon.exploration import explore_area

        gs.current_location = None
        explore_area(gs, output, lambda o: None, lambda o, t: None)
        assert "No current location set" in output.combined

    def test_cannot_explore_in_town(self, gs, output):
        from pytemon.exploration import explore_area

        # Pallet Town is a town - can't explore
        explore_area(gs, output, lambda o: None, lambda o, t: None)
        assert "nothing to explore" in output.combined.lower() or "⚠" in output.combined

    def test_no_pokemon_shows_warning(self, gs, output):
        from pytemon.exploration import explore_area
        from pytemon.locations import get_location

        gs.current_location = get_location("Route 1")
        gs.game_data["pokemon"] = []
        explore_area(gs, output, lambda o: None, lambda o, t: None)
        assert "without Pokemon" in output.combined or "⚠" in output.combined

    def test_explore_triggers_wild(self, gs, output):
        import random

        from pytemon.engine import BattleState
        from pytemon.exploration import explore_area
        from pytemon.locations import get_location

        gs.current_location = get_location("Route 1")
        bs = BattleState()
        p = bs.generate_wild_pokemon("PIKACHU", 5)
        gs.game_data["pokemon"] = [p]
        # Defeat Route 1 trainers so the wild-encounter branch is reached
        gs.game_data["defeated_trainers"] = ["youngster_joey"]
        wild_triggered = []
        original_random = random.random
        try:
            # 0.06 > _ITEM_FIND_CHANCE (0.05) → no item; 0.06 < wild_encounter_rate (0.45) → encounter
            random.random = lambda: 0.06
            explore_area(gs, output, lambda o: wild_triggered.append(True), lambda o, t: None)
        finally:
            random.random = original_random
        assert len(wild_triggered) > 0

    def test_explore_with_repel(self, gs, output):
        import random

        from pytemon.engine import BattleState
        from pytemon.exploration import explore_area
        from pytemon.locations import get_location

        gs.current_location = get_location("Route 1")
        bs = BattleState()
        p = bs.generate_wild_pokemon("PIKACHU", 5)
        gs.game_data["pokemon"] = [p]
        gs.game_data["repel_steps"] = 5
        # Defeat Route 1 trainers so the encounter branch is reached
        gs.game_data["defeated_trainers"] = ["youngster_joey"]
        original_random = random.random
        try:
            # 0.06 > _ITEM_FIND_CHANCE (0.05) → no item; 0.06 < wild_encounter_rate (0.45) → encounter;
            # 0.06 < 0.5 repel suppress threshold → repel fires
            random.random = lambda: 0.06
            explore_area(gs, output, lambda o: None, lambda o, t: None)
        finally:
            random.random = original_random
        assert "Repel" in output.combined


class TestMoveToLocationExtra:
    def test_blocked_exit_without_cheat_mode(self, gs, output):
        from pytemon.exploration import move_to_location
        from pytemon.locations import get_location

        gs.current_location = get_location("Pallet Town")
        gs.cheat_mode = False
        # Route 22 is not an exit from Pallet Town, so we expect a "can't go to" error
        move_to_location(gs, "Route 22", output, lambda o: None)
        assert "can't go to" in output.combined.lower()

    def test_move_blocked_by_explore_requirement(self, gs, output):
        from pytemon.engine import BattleState
        from pytemon.exploration import move_to_location
        from pytemon.locations import get_location

        gs.current_location = get_location("Route 1")
        gs.cheat_mode = False
        # Route 1 requires some exploration before going to Viridian
        bs = BattleState()
        p = bs.generate_wild_pokemon("PIKACHU", 5)
        gs.game_data["pokemon"] = [p]
        gs.game_data.setdefault("route_progress", {})["Route 1"] = 0
        move_to_location(gs, "Viridian City", output, lambda o: None)
        # Route 1 requires 3 explores before advancing to Viridian City
        assert "haven't fully explored" in output.combined.lower()

    def test_cheat_mode_bypasses_block(self, gs, output):
        from pytemon.engine import BattleState
        from pytemon.exploration import move_to_location
        from pytemon.locations import get_location

        gs.current_location = get_location("Route 1")
        gs.cheat_mode = True
        bs = BattleState()
        p = bs.generate_wild_pokemon("PIKACHU", 5)
        gs.game_data["pokemon"] = [p]
        move_to_location(gs, "Viridian City", output, lambda o: None)
        # Cheat mode bypasses the min_explores gate — should arrive at Viridian City
        assert gs.current_location.name == "Viridian City"

    def test_no_pokemon_blocked_from_route_1(self, gs, output):
        from pytemon.exploration import move_to_location
        from pytemon.locations import get_location

        gs.current_location = get_location("Pallet Town")
        gs.cheat_mode = False
        gs.game_data["pokemon"] = []
        move_to_location(gs, "Route 1", output, lambda o: None)
        assert "Oak" in output.combined or "Pokemon" in output.combined


class TestShowLocationArrivalExtra:
    def test_is_load_shows_different_message(self, gs, output):
        from pytemon.exploration import show_location_arrival

        show_location_arrival(gs, output, is_load=True)
        assert "You find yourself in" in output.combined

    def test_regular_arrival_shows_location(self, gs, output):
        from pytemon.exploration import show_location_arrival

        show_location_arrival(gs, output, is_load=False)
        assert "You have arrived in" in output.combined
        assert "Pallet Town" in output.combined


# ===========================================================================
# Route 24 dynamic unlock via cascade_badge
# ===========================================================================


class TestRoute24DynamicUnlock:
    def test_route_24_blocked_without_cascade_badge(self, gs, output):
        gs.current_location = get_location("Cerulean City")
        gs.cheat_mode = False
        gs.game_data["badges"] = []
        move_to_location(gs, "Route 24", output, noop)
        assert gs.current_location.name == "Cerulean City"
        assert "⚠" in output.combined or "blocked" in output.combined.lower()

    def test_route_24_blocked_shows_badge_reason(self, gs, output):
        gs.current_location = get_location("Cerulean City")
        gs.cheat_mode = False
        gs.game_data["badges"] = []
        move_to_location(gs, "Route 24", output, noop)
        combined_lower = output.combined.lower()
        assert (
            "cascade" in combined_lower or "badge" in combined_lower or "nugget" in combined_lower
        )

    def test_route_24_accessible_with_cascade_badge(self, gs, output):
        gs.current_location = get_location("Cerulean City")
        gs.cheat_mode = False
        gs.game_data["badges"] = ["cascade_badge"]
        called = []
        move_to_location(gs, "Route 24", output, lambda o: called.append(True))
        assert gs.current_location.name == "Route 24"

    def test_route_24_accessible_in_cheat_mode_without_badge(self, gs, output):
        gs.current_location = get_location("Cerulean City")
        gs.cheat_mode = True
        gs.game_data["badges"] = []
        called = []
        move_to_location(gs, "Route 24", output, lambda o: called.append(True))
        assert gs.current_location.name == "Route 24"


# ===========================================================================
# Cycling (Bicycle) explore-step tests
# ===========================================================================


class TestCyclingExploreStep:
    """Bicycle should count each explore as 2 progress steps."""

    def test_cycling_increments_progress_by_two(self, gs, output):
        import random

        gs.current_location = get_location("Route 1")
        gs.game_data["cycling"] = True
        make_party_pokemon(gs)
        gs.game_data["defeated_trainers"] = ["youngster_joey"]  # skip trainers

        initial = gs.get_route_progress("Route 1")
        # Force no wild encounter so we always hit the "no encounter" branch
        original = random.random
        try:
            random.random = lambda: 0.99  # > encounter rate
            explore_area(gs, output, noop, noop)
        finally:
            random.random = original

        assert gs.get_route_progress("Route 1") == initial + 2

    def test_walking_increments_progress_by_one(self, gs, output):
        import random

        gs.current_location = get_location("Route 1")
        gs.game_data["cycling"] = False
        make_party_pokemon(gs)
        gs.game_data["defeated_trainers"] = ["youngster_joey"]

        initial = gs.get_route_progress("Route 1")
        original = random.random
        try:
            random.random = lambda: 0.99  # no wild encounter
            explore_area(gs, output, noop, noop)
        finally:
            random.random = original

        assert gs.get_route_progress("Route 1") == initial + 1

    def test_cycling_message_shown_when_no_encounter(self, gs, output):
        import random

        gs.current_location = get_location("Route 1")
        gs.game_data["cycling"] = True
        make_party_pokemon(gs)
        gs.game_data["defeated_trainers"] = ["youngster_joey"]

        original = random.random
        try:
            random.random = lambda: 0.99
            explore_area(gs, output, noop, noop)
        finally:
            random.random = original

        assert "🚲" in output.combined or "Bicycle" in output.combined

    def test_cycling_on_off_affects_step(self, gs, output):
        """Toggling cycling off should revert to single-step increments."""
        import random

        gs.current_location = get_location("Route 1")
        make_party_pokemon(gs)
        gs.game_data["defeated_trainers"] = ["youngster_joey"]

        original = random.random
        try:
            random.random = lambda: 0.99
            gs.game_data["cycling"] = True
            explore_area(gs, output, noop, noop)
            after_cycling = gs.get_route_progress("Route 1")

            gs.game_data["cycling"] = False
            explore_area(gs, output, noop, noop)
            after_walking = gs.get_route_progress("Route 1")
        finally:
            random.random = original

        assert after_cycling - 0 == 2  # first explore: +2
        assert after_walking - after_cycling == 1  # second explore: +1


# ===========================================================================
# Updated min_explores values
# ===========================================================================


class TestUpdatedMinExplores:
    """Verify that explore requirements have been raised above 3-4."""

    def test_route_1_min_explores_gte_5(self):
        loc = get_location("Route 1")
        assert loc.exits["Viridian City"]["min_explores"] >= 5

    def test_viridian_forest_min_explores_gte_6(self):
        loc = get_location("Viridian Forest")
        assert loc.exits["Route 2 North"]["min_explores"] >= 6

    def test_mt_moon_min_explores_gte_7(self):
        loc = get_location("Mt. Moon")
        assert loc.exits["Route 4"]["min_explores"] >= 7

    def test_route_3_min_explores_gte_5(self):
        loc = get_location("Route 3")
        assert loc.exits["Mt. Moon"]["min_explores"] >= 5

    def test_route_9_min_explores_gte_5(self):
        loc = get_location("Route 9")
        assert loc.exits["Route 10"]["min_explores"] >= 5

    def test_rock_tunnel_min_explores_gte_8(self):
        loc = get_location("Rock Tunnel")
        assert loc.exits["Route 10"]["min_explores"] >= 8
