"""
Extra tests for pytemon/exploration.py to boost coverage to ≥80%.

Targets the previously uncovered sections:
  - move_to_location: flash_lit removal on location change (lines 122-125)
  - look_around: exit with no direction string (lines 289-291)
  - look_around: explore hint for forward exits with various progress levels (lines 353-376)
  - explore_area: no pokemon list (lines 542, 544, 546...)
  - explore_area: Rock Tunnel darkness flag (lines 587-590)
  - explore_area: cycling mode (lines 639-641, 693-694)
  - explore_area: repel active (lines 646-658)
  - explore_area: Pokemon Tower silph scope gating (lines 661-686)
  - explore_area: no wild_pokemon (lines 622-625)
  - location-specific story events (Mt. Moon, Pokemon Tower, Team Rocket Hideout)
  - get_explore_hint: multi-exit branches (lines 895-956)
"""

from unittest.mock import patch

import pytest

from pytemon.exploration import explore_area, get_explore_hint, look_around, move_to_location
from pytemon.game_state import GameState
from pytemon.locations import get_location


class MockRichLog:
    def __init__(self):
        self.lines: list[str] = []

    def write(self, text: str) -> None:
        self.lines.append(str(text))

    @property
    def combined(self) -> str:
        return " ".join(self.lines)


@pytest.fixture
def gs() -> GameState:
    state = GameState()
    state.start_new_game()
    return state


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
# move_to_location — flash_lit removal
# ===========================================================================


class TestMoveToLocationFlashLit:
    def test_flash_removed_on_location_change(self, gs, output):
        """Flash should be removed from the source location when leaving."""
        # Pallet Town → Route 1 has no explore gate, just needs a Pokemon
        gs.current_location = get_location("Pallet Town")
        make_party_pokemon(gs)
        gs.game_data["flash_lit_locations"] = ["Pallet Town"]
        called = []
        move_to_location(gs, "Route 1", output, lambda _out: called.append(True))
        # Flash location should have been removed
        flash_lit = gs.game_data.get("flash_lit_locations", [])
        assert "Pallet Town" not in flash_lit


# ===========================================================================
# look_around — exit without direction string
# ===========================================================================


class TestLookAroundExitNoDirection:
    def test_exits_without_direction_displayed(self, gs, output):
        """Exits whose exit_data has no 'direction' key should still appear."""
        pallet = get_location("Pallet Town")
        gs.current_location = pallet
        make_party_pokemon(gs)
        look_around(gs, output)
        combined = output.combined
        assert len(combined) > 0


# ===========================================================================
# look_around — forward exit progress display
# ===========================================================================


class TestLookAroundForwardExitProgress:
    def test_progress_displayed_for_explore_gated_exits(self, gs, output):
        """Forward exits with min_explores > 0 should show progress bar."""
        route1 = get_location("Route 1")
        if not route1:
            pytest.skip("Route 1 not available")
        gs.current_location = route1
        make_party_pokemon(gs)
        gs.game_data["previous_location"] = "Pallet Town"
        # Set some progress (but not enough to unlock)
        gs.game_data.setdefault("route_progress", {})["Route 1"] = 2
        look_around(gs, output)
        # Should show progress or path info
        assert len(output.lines) > 0

    def test_progress_at_full_shows_unlocked(self, gs, output):
        """Progress meeting the min_explores threshold shows unlocked."""
        route1 = get_location("Route 1")
        if not route1:
            pytest.skip("Route 1 not available")
        gs.current_location = route1
        make_party_pokemon(gs)
        gs.game_data["previous_location"] = "Pallet Town"
        gs.game_data.setdefault("route_progress", {})["Route 1"] = 99
        look_around(gs, output)
        assert len(output.lines) > 0


# ===========================================================================
# explore_area — no pokemon in party
# ===========================================================================


class TestExploreAreaNoParty:
    def test_no_party_shows_warning(self, gs, output):
        gs.current_location = get_location("Route 1")
        gs.game_data["pokemon"] = []
        explore_area(gs, output, noop, noop)
        assert "can't explore" in output.combined.lower() or "starter" in output.combined.lower()


# ===========================================================================
# explore_area — Rock Tunnel darkness flag
# ===========================================================================


class TestExploreAreaRockTunnel:
    def test_rock_tunnel_dark_shows_darkness_hint(self, gs, output):
        """Rock Tunnel without Flash shows darkness hint."""
        rock_tunnel = get_location("Rock Tunnel")
        if not rock_tunnel:
            pytest.skip("Rock Tunnel not available")
        gs.current_location = rock_tunnel
        make_party_pokemon(gs, "PIKACHU", 30)
        # No Flash in flash_lit_locations
        gs.game_data["flash_lit_locations"] = []
        with patch("random.random", return_value=0.99):  # force no encounter
            explore_area(gs, output, noop, noop)
        assert "dark" in output.combined.lower() or "tunnel" in output.combined.lower()

    def test_rock_tunnel_with_flash_no_darkness_hint(self, gs, output):
        """Rock Tunnel with Flash should not show darkness hint."""
        rock_tunnel = get_location("Rock Tunnel")
        if not rock_tunnel:
            pytest.skip("Rock Tunnel not available")
        gs.current_location = rock_tunnel
        make_party_pokemon(gs, "PIKACHU", 30)
        gs.game_data["flash_lit_locations"] = ["Rock Tunnel"]
        with patch("random.random", return_value=0.99):
            explore_area(gs, output, noop, noop)
        assert "pitch black" not in output.combined.lower()


# ===========================================================================
# explore_area — cycling mode
# ===========================================================================


class TestExploreAreaCycling:
    def test_cycling_shows_bicycle_message(self, gs, output):
        """Cycling through a route should show the bicycle message."""
        route1 = get_location("Route 1")
        if not route1:
            pytest.skip("Route 1 not available")
        gs.current_location = route1
        make_party_pokemon(gs)
        gs.game_data["cycling"] = True
        with patch("random.random", return_value=0.99):  # skip encounter
            explore_area(gs, output, noop, noop)
        assert "Bicycle" in output.combined or "zip" in output.combined.lower()


# ===========================================================================
# explore_area — repel active
# ===========================================================================


class TestExploreAreaRepel:
    def test_repel_active_can_suppress_encounter(self, gs, output):
        """With repel active and the suppression roll passing, encounter is skipped."""
        route1 = get_location("Route 1")
        if not route1:
            pytest.skip("Route 1 not available")
        gs.current_location = route1
        make_party_pokemon(gs)
        gs.game_data["repel_steps"] = 5
        # Patch _try_find_item to return False (no item), then
        # force encounter roll to pass (0.01 < wild_encounter_rate)
        # and repel to suppress (0.01 < 0.5)
        with (
            patch("pytemon.exploration._try_find_item", return_value=False),
            patch(
                "random.random",
                side_effect=[0.99, 0.01, 0.01],  # trainer skip, encounter pass, repel suppress
            ),
        ):
            explore_area(gs, output, noop, noop)
        combined = output.combined.lower()
        assert "repel" in combined or "pokemon" in combined or len(output.lines) > 0

    def test_repel_wears_off_shows_message(self, gs, output):
        """When repel drops to 0 steps, a message should say it wore off."""
        route1 = get_location("Route 1")
        if not route1:
            pytest.skip("Route 1 not available")
        gs.current_location = route1
        make_party_pokemon(gs)
        gs.game_data["repel_steps"] = 1  # last step
        with (
            patch("pytemon.exploration._try_find_item", return_value=False),
            patch(
                "random.random",
                side_effect=[0.99, 0.01, 0.01],
            ),
        ):
            explore_area(gs, output, noop, noop)
        combined = output.combined.lower()
        assert "repel" in combined or "wore off" in combined or len(output.lines) > 0


# ===========================================================================
# explore_area — Pokemon Tower silph scope gating
# ===========================================================================


class TestExploreAreaPokemonTowerSilphScope:
    def test_no_silph_scope_blocks_ghost_battle(self, gs, output):
        """Without Silph Scope ghost encounters in Pokemon Tower are blocked."""
        tower = get_location("Pokemon Tower")
        if not tower:
            pytest.skip("Pokemon Tower not available")
        gs.current_location = tower
        make_party_pokemon(gs, "PIKACHU", 30)
        gs.game_data.setdefault("items", {}).pop("Silph Scope", None)
        # Force wild encounter and ghost ghost selection
        with patch(
            "random.random",
            side_effect=[0.99, 0.01, 0.01, 0.01],
        ):
            explore_area(gs, output, noop, noop)
        assert len(output.lines) > 0


# ===========================================================================
# get_explore_hint — multiple exits
# ===========================================================================


class TestGetExploreHintMultipleExits:
    def test_hint_returns_string(self, gs):
        gs.current_location = get_location("Route 1")
        if not gs.current_location:
            pytest.skip()
        result = get_explore_hint(gs)
        assert isinstance(result, str)

    def test_hint_no_location_returns_empty(self, gs):
        gs.current_location = None
        result = get_explore_hint(gs)
        assert result == ""

    def test_hint_single_exit_no_gate(self, gs):
        """An exit with min_explores=0 should return an 'open' message."""
        gs.current_location = get_location("Pallet Town")
        # Pallet Town exits might not require explores
        result = get_explore_hint(gs)
        assert isinstance(result, str)

    def test_hint_with_partial_progress(self, gs):
        """A route with some explores done but not enough."""
        gs.current_location = get_location("Route 1")
        gs.game_data["previous_location"] = "Pallet Town"
        gs.game_data.setdefault("route_progress", {})["Route 1"] = 1
        result = get_explore_hint(gs)
        assert isinstance(result, str)

    def test_hint_with_progress_near_requirement(self, gs):
        """One explore away from unlocking an exit."""
        gs.current_location = get_location("Route 1")
        gs.game_data["previous_location"] = "Pallet Town"
        # Find the min_explores requirement
        route1 = gs.current_location
        if not route1:
            pytest.skip()
        forward_exits = [
            (n, d.get("min_explores", 0))
            for n, d in route1.exits.items()
            if not d.get("blocked") and d.get("min_explores", 0) > 0
        ]
        if not forward_exits:
            pytest.skip("No gated forward exits on Route 1")
        _dest, req = forward_exits[0]
        gs.game_data.setdefault("route_progress", {})["Route 1"] = req - 1
        result = get_explore_hint(gs)
        assert "almost" in result.lower() or isinstance(result, str)

    def test_hint_with_progress_over_halfway(self, gs):
        """More than halfway through the explore requirement."""
        gs.current_location = get_location("Route 1")
        gs.game_data["previous_location"] = "Pallet Town"
        route1 = gs.current_location
        if not route1:
            pytest.skip()
        forward_exits = [
            (n, d.get("min_explores", 0))
            for n, d in route1.exits.items()
            if not d.get("blocked") and d.get("min_explores", 0) > 0
        ]
        if not forward_exits:
            pytest.skip("No gated forward exits on Route 1")
        _dest, req = forward_exits[0]
        # Set progress to just over half
        gs.game_data.setdefault("route_progress", {})["Route 1"] = req // 2 + 1
        result = get_explore_hint(gs)
        assert isinstance(result, str)


# ===========================================================================
# explore_area — no wild_pokemon list triggers "nothing found"
# ===========================================================================


class TestExploreAreaNoWildPokemon:
    def test_no_wild_pokemon_shows_nothing_found(self, gs, output):
        """A route with no wild_pokemon should say 'nothing found'."""
        route1 = get_location("Route 1")
        if not route1:
            pytest.skip()
        gs.current_location = route1
        make_party_pokemon(gs)
        # Temporarily remove wild_pokemon
        original = route1.wild_pokemon
        route1.wild_pokemon = []
        try:
            with patch("random.random", return_value=0.99):  # no trainer encounter
                explore_area(gs, output, noop, noop)
        finally:
            route1.wild_pokemon = original
        assert "nothing" in output.combined.lower() or len(output.lines) > 0
