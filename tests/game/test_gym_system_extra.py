"""
Extended tests for PokemonLibrary/gym_system.py

Covers: enter_gym_lobby, enter_gym, handle_gym_victory, show_badge_case (more coverage),
can_challenge_gym, has_badge, get_badge_count, award_badge, get_gym_data, get_badge_data.
"""

import pytest

from pytemon.engine import BattleState
from pytemon.game_state import GameState
from pytemon.gym_system import (
    award_badge,
    can_challenge_gym,
    enter_gym,
    enter_gym_lobby,
    get_badge_count,
    get_badge_data,
    get_gym_data,
    get_next_gym_trainer,
    handle_gym_victory,
    has_badge,
    show_badge_case,
)
from pytemon.locations import get_location


class MockRichLog:
    def __init__(self):
        self.lines = []

    def write(self, text) -> None:
        self.lines.append(str(text))

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
    bs = BattleState()
    p = bs.generate_wild_pokemon(name, level)
    gs.game_data.setdefault("pokemon", []).append(p)
    return p


def go_to_pewter(gs):
    """Navigate game state to Pewter City gym."""
    gs.cheat_mode = True
    gs.current_location = get_location("Pewter City")
    make_party_pokemon(gs, "PIKACHU", 20)


# ===========================================================================
# get_gym_data
# ===========================================================================


class TestGetGymData:
    def test_returns_gym_for_pewter(self):
        data = get_gym_data("Pewter City")
        assert data is not None
        assert "badge" in data

    def test_returns_none_for_nonexistent(self):
        data = get_gym_data("Nonexistent Place 9999")
        assert data is None

    def test_all_gyms_have_required_fields(self):
        from pytemon.gym_system import GYMS

        for _, data in GYMS.items():
            assert "badge" in data
            assert "leader_id" in data
            assert "specialty" in data


# ===========================================================================
# get_badge_data
# ===========================================================================


class TestGetBadgeData:
    def test_returns_boulder_badge(self):
        data = get_badge_data("Boulder Badge")
        assert data is not None
        assert data["leader"] == "Brock"

    def test_returns_none_for_nonexistent(self):
        data = get_badge_data("Fake Badge 9999")
        assert data is None


# ===========================================================================
# has_badge
# ===========================================================================


class TestHasBadge:
    def test_false_when_no_badges(self, gs):
        gs.game_data["badges"] = []
        assert has_badge(gs, "Boulder Badge") is False

    def test_true_when_badge_present(self, gs):
        gs.game_data["badges"] = ["boulder_badge"]
        assert has_badge(gs, "Boulder Badge") is True

    def test_false_for_nonexistent_badge(self, gs):
        assert has_badge(gs, "Fake Badge 9999") is False


# ===========================================================================
# get_badge_count
# ===========================================================================


class TestGetBadgeCount:
    def test_zero_when_no_badges(self, gs):
        gs.game_data["badges"] = []
        assert get_badge_count(gs) == 0

    def test_count_with_badges(self, gs):
        gs.game_data["badges"] = ["boulder_badge", "cascade_badge"]
        assert get_badge_count(gs) == 2


# ===========================================================================
# award_badge
# ===========================================================================


class TestAwardBadge:
    def test_awards_valid_badge(self, gs, output):
        award_badge(gs, "Boulder Badge", output)
        assert "boulder_badge" in gs.game_data.get("badges", [])

    def test_shows_badge_award_message(self, gs, output):
        award_badge(gs, "Boulder Badge", output)
        assert "BADGE EARNED" in output.combined or "Boulder Badge" in output.combined

    def test_duplicate_badge_shows_warning(self, gs, output):
        award_badge(gs, "Boulder Badge", output)
        out2 = MockRichLog()
        award_badge(gs, "Boulder Badge", out2)
        assert "already" in out2.combined.lower()

    def test_invalid_badge_shows_error(self, gs, output):
        award_badge(gs, "Fake Badge 9999", output)
        assert "Unknown badge" in output.combined or "❌" in output.combined

    def test_initializes_badges_list(self, gs, output):
        gs.game_data.pop("badges", None)
        award_badge(gs, "Boulder Badge", output)
        assert "boulder_badge" in gs.game_data.get("badges", [])


# ===========================================================================
# can_challenge_gym
# ===========================================================================


class TestCanChallengeGym:
    def test_can_challenge_pewter_with_pokemon(self, gs):
        make_party_pokemon(gs, "PIKACHU", 20)
        result, _ = can_challenge_gym(gs, "Pewter City")
        assert result is True

    def test_cannot_challenge_no_gym(self, gs):
        result, _ = can_challenge_gym(gs, "Nonexistent Place 9999")
        assert result is False

    def test_cannot_challenge_no_pokemon(self, gs):
        gs.game_data["pokemon"] = []
        result, reason = can_challenge_gym(gs, "Pewter City")
        assert result is False
        assert "Pokemon" in reason

    def test_cannot_challenge_already_beaten(self, gs):
        make_party_pokemon(gs)
        award_badge(gs, "Boulder Badge", MockRichLog())
        result, _ = can_challenge_gym(gs, "Pewter City")
        assert result is False

    def test_cannot_challenge_viridian_without_7_badges(self, gs):
        make_party_pokemon(gs)
        result, _ = can_challenge_gym(gs, "Viridian City")
        assert result is False

    def test_can_challenge_viridian_with_7_badges(self, gs):
        make_party_pokemon(gs, "PIKACHU", 60)
        badge_names = [
            "Boulder Badge",
            "Cascade Badge",
            "Thunder Badge",
            "Rainbow Badge",
            "Soul Badge",
            "Marsh Badge",
            "Volcano Badge",
        ]
        log = MockRichLog()
        for name in badge_names:
            award_badge(gs, name, log)
        result, _ = can_challenge_gym(gs, "Viridian City")
        assert result is True

    def test_cannot_challenge_all_fainted(self, gs):
        p = make_party_pokemon(gs)
        p["hp"] = 0
        result, _ = can_challenge_gym(gs, "Pewter City")
        assert result is False


# ===========================================================================
# get_next_gym_trainer
# ===========================================================================


class TestGetNextGymTrainer:
    def test_returns_first_trainer_when_none_defeated(self, gs):
        result = get_next_gym_trainer(gs, "Pewter City")
        assert result == "gym_trainer_pewter_hiker"

    def test_returns_none_after_all_defeated(self, gs):
        from pytemon.gym_system import get_gym_trainers

        trainers = get_gym_trainers("Pewter City")
        gs.game_data["defeated_trainers"] = list(trainers)
        result = get_next_gym_trainer(gs, "Pewter City")
        assert result is None


# ===========================================================================
# enter_gym_lobby
# ===========================================================================


class TestEnterGymLobby:
    def test_no_location_shows_error(self, gs, output):
        gs.current_location = None
        enter_gym_lobby(gs, output, noop)
        assert "❌" in output.combined

    def test_no_gym_shows_message(self, gs, output):
        # Pallet Town has no gym
        enter_gym_lobby(gs, output, noop)
        assert "Gym" in output.combined

    def test_pewter_gym_shows_lobby(self, gs, output):
        go_to_pewter(gs)
        called = []
        enter_gym_lobby(gs, output, lambda: called.append(True))
        assert called
        assert len(output.lines) > 0

    def test_shows_brock_as_leader(self, gs, output):
        go_to_pewter(gs)
        enter_gym_lobby(gs, output, noop)
        assert "Brock" in output.combined

    def test_already_have_badge_shows_message(self, gs, output):
        go_to_pewter(gs)
        award_badge(gs, "Boulder Badge", MockRichLog())
        called = []
        enter_gym_lobby(gs, output, lambda: called.append(True))
        assert "already earned" in output.combined.lower() or "Boulder Badge" in output.combined

    def test_cannot_challenge_viridian_shows_absent(self, gs, output):
        gs.cheat_mode = True
        gs.current_location = get_location("Viridian City")
        make_party_pokemon(gs, "PIKACHU", 60)
        enter_gym_lobby(gs, output, noop)
        assert (
            "Giovanni" in output.combined
            or "away" in output.combined
            or "business" in output.combined
        )


# ===========================================================================
# enter_gym
# ===========================================================================


class TestEnterGym:
    def test_no_location_shows_error(self, gs, output):
        gs.current_location = None
        enter_gym(gs, output, noop)
        assert "❌" in output.combined

    def test_no_gym_shows_message(self, gs, output):
        # Pallet Town has no gym
        enter_gym(gs, output, noop)
        assert "Gym" in output.combined

    def test_cannot_challenge_shows_message(self, gs, output):
        go_to_pewter(gs)
        gs.game_data["pokemon"] = []
        enter_gym(gs, output, noop)
        assert len(output.lines) > 0

    def test_valid_challenge_triggers_battle(self, gs, output):
        go_to_pewter(gs)
        called = []
        enter_gym(gs, output, lambda leader_id, out, is_gym_battle=False: called.append(leader_id))
        assert called

    def test_viridian_no_badges_shows_absent(self, gs, output):
        gs.cheat_mode = True
        gs.current_location = get_location("Viridian City")
        make_party_pokemon(gs)
        enter_gym(gs, output, noop)
        assert "business" in output.combined.lower() or "away" in output.combined.lower()


# ===========================================================================
# handle_gym_victory
# ===========================================================================


class TestHandleGymVictory:
    def test_awards_badge_for_brock(self, gs, output):
        handle_gym_victory(gs, "gym_leader_brock", output)
        assert "boulder_badge" in gs.game_data.get("badges", [])

    def test_shows_badge_award_message(self, gs, output):
        handle_gym_victory(gs, "gym_leader_brock", output)
        assert "Boulder Badge" in output.combined or "BADGE" in output.combined

    def test_unknown_trainer_shows_warning(self, gs, output):
        handle_gym_victory(gs, "fake_trainer_99999", output)
        assert "Warning" in output.combined or "⚠" in output.combined


# ===========================================================================
# show_badge_case
# ===========================================================================


class TestShowBadgeCaseExtra:
    def test_shows_unearned_placeholder(self, gs, output):
        gs.game_data["badges"] = []
        show_badge_case(gs, output)
        assert "No badges" in output.combined

    def test_shows_earned_badge(self, gs, output):
        gs.game_data["badges"] = ["boulder_badge"]
        show_badge_case(gs, output)
        assert "Boulder Badge" in output.combined

    def test_eight_badges_shows_congratulations(self, gs, output):
        gs.game_data["badges"] = [
            "boulder_badge",
            "cascade_badge",
            "thunder_badge",
            "rainbow_badge",
            "soul_badge",
            "marsh_badge",
            "volcano_badge",
            "earth_badge",
        ]
        show_badge_case(gs, output)
        assert (
            "CONGRATULATIONS" in output.combined
            or "8/8" in output.combined
            or "League" in output.combined
        )
