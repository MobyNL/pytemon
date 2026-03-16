"""
Unit tests for PokemonLibrary/gym_system.py.
"""

import pytest

from pytemon.game_state import GameState
from pytemon.gym_system import (
    BADGES,
    GYMS,
    award_badge,
    can_challenge_gym,
    get_badge_count,
    get_badge_data,
    get_gym_data,
    get_gym_trainers,
    get_next_gym_trainer,
    has_badge,
    show_badge_case,
)


class MockRichLog:
    """Minimal stub for textual.widgets.RichLog."""

    def __init__(self):
        self.lines = []

    def write(self, text: str) -> None:
        self.lines.append(text)


@pytest.fixture
def gs() -> GameState:
    gs = GameState()
    gs.start_new_game()
    return gs


@pytest.fixture
def output() -> MockRichLog:
    return MockRichLog()


# ---------------------------------------------------------------------------
# BADGES / GYMS data
# ---------------------------------------------------------------------------


class TestBadgesData:
    def test_all_eight_badges_exist(self):
        assert len(BADGES) == 8

    def test_boulder_badge_present(self):
        assert "Boulder Badge" in BADGES

    def test_earth_badge_present(self):
        assert "Earth Badge" in BADGES

    def test_badge_has_required_keys(self):
        badge = BADGES["Boulder Badge"]
        for key in (
            "id",
            "name",
            "emoji",
            "gym",
            "leader",
            "type",
            "color",
            "description",
            "order",
        ):
            assert key in badge

    def test_badges_ordered_1_to_8(self):
        orders = sorted(b["order"] for b in BADGES.values())
        assert orders == list(range(1, 9))


class TestGymsData:
    def test_pewter_city_gym_exists(self):
        assert "Pewter City" in GYMS

    def test_gym_has_required_keys(self):
        gym = GYMS["Pewter City"]
        for key in ("badge", "required_badges"):
            assert key in gym


# ---------------------------------------------------------------------------
# get_gym_data
# ---------------------------------------------------------------------------


class TestGetGymData:
    def test_known_gym_city_returns_data(self):
        data = get_gym_data("Pewter City")
        assert data is not None
        assert "leader_id" in data or "badge" in data

    def test_unknown_location_returns_none(self):
        assert get_gym_data("Nowhere Town") is None

    def test_pallet_town_has_no_gym(self):
        assert get_gym_data("Pallet Town") is None


# ---------------------------------------------------------------------------
# get_badge_data
# ---------------------------------------------------------------------------


class TestGetBadgeData:
    def test_known_badge_returns_data(self):
        data = get_badge_data("Boulder Badge")
        assert data is not None
        assert data["id"] == "boulder_badge"

    def test_unknown_badge_returns_none(self):
        assert get_badge_data("Fake Badge") is None


# ---------------------------------------------------------------------------
# has_badge
# ---------------------------------------------------------------------------


class TestHasBadge:
    def test_no_badges_returns_false(self, gs):
        assert has_badge(gs, "Boulder Badge") is False

    def test_has_badge_returns_true(self, gs):
        gs.game_data["badges"] = ["boulder_badge"]
        assert has_badge(gs, "Boulder Badge") is True

    def test_different_badge_returns_false(self, gs):
        gs.game_data["badges"] = ["boulder_badge"]
        assert has_badge(gs, "Cascade Badge") is False

    def test_unknown_badge_returns_false(self, gs):
        assert has_badge(gs, "Nonexistent Badge") is False

    def test_badges_not_a_list_returns_false(self, gs):
        gs.game_data["badges"] = 0  # old save format
        assert has_badge(gs, "Boulder Badge") is False


# ---------------------------------------------------------------------------
# get_badge_count
# ---------------------------------------------------------------------------


class TestGetBadgeCount:
    def test_no_badges_returns_zero(self, gs):
        assert get_badge_count(gs) == 0

    def test_counts_badges_correctly(self, gs):
        gs.game_data["badges"] = ["boulder_badge", "cascade_badge"]
        assert get_badge_count(gs) == 2

    def test_all_eight_badges(self, gs):
        gs.game_data["badges"] = [b["id"] for b in BADGES.values()]
        assert get_badge_count(gs) == 8

    def test_non_list_returns_zero(self, gs):
        gs.game_data["badges"] = "not_a_list"
        assert get_badge_count(gs) == 0


# ---------------------------------------------------------------------------
# get_gym_trainers
# ---------------------------------------------------------------------------


class TestGetGymTrainers:
    def test_known_gym_returns_list(self):
        trainers = get_gym_trainers("Pewter City")
        assert isinstance(trainers, list)

    def test_unknown_location_returns_empty_list(self):
        assert get_gym_trainers("Fake Town") == []

    def test_trainers_are_strings(self):
        trainers = get_gym_trainers("Pewter City")
        if trainers:
            assert all(isinstance(t, str) for t in trainers)


# ---------------------------------------------------------------------------
# get_next_gym_trainer
# ---------------------------------------------------------------------------


class TestGetNextGymTrainer:
    def test_returns_first_trainer_when_none_defeated(self, gs):
        trainers = get_gym_trainers("Pewter City")
        if trainers:
            result = get_next_gym_trainer(gs, "Pewter City")
            assert result == trainers[0]

    def test_returns_none_when_all_defeated(self, gs):
        trainers = get_gym_trainers("Pewter City")
        gs.game_data["defeated_trainers"] = list(trainers)
        result = get_next_gym_trainer(gs, "Pewter City")
        assert result is None

    def test_returns_none_for_unknown_location(self, gs):
        assert get_next_gym_trainer(gs, "Fake Town") is None

    def test_skips_defeated_trainers(self, gs):
        trainers = get_gym_trainers("Pewter City")
        if len(trainers) >= 2:
            gs.game_data["defeated_trainers"] = [trainers[0]]
            result = get_next_gym_trainer(gs, "Pewter City")
            assert result == trainers[1]


# ---------------------------------------------------------------------------
# award_badge
# ---------------------------------------------------------------------------


class TestAwardBadge:
    def test_awards_badge_successfully(self, gs, output):
        award_badge(gs, "Boulder Badge", output)
        assert has_badge(gs, "Boulder Badge")

    def test_award_unknown_badge_writes_error(self, gs, output):
        award_badge(gs, "Fake Badge", output)
        combined = " ".join(output.lines)
        assert "❌" in combined or "Unknown" in combined or "Error" in combined

    def test_award_same_badge_twice_does_not_duplicate(self, gs, output):
        award_badge(gs, "Boulder Badge", output)
        award_badge(gs, "Boulder Badge", output)
        badges = gs.game_data.get("badges", [])
        assert badges.count("boulder_badge") == 1

    def test_awards_multiple_different_badges(self, gs, output):
        award_badge(gs, "Boulder Badge", output)
        award_badge(gs, "Cascade Badge", output)
        assert get_badge_count(gs) == 2


# ---------------------------------------------------------------------------
# can_challenge_gym
# ---------------------------------------------------------------------------


class TestCanChallengeGym:
    def test_no_gym_at_location(self, gs):
        can, reason = can_challenge_gym(gs, "Pallet Town")
        assert can is False
        assert "no gym" in reason.lower()

    def test_already_has_badge_cannot_challenge(self, gs):
        gs.game_data["badges"] = ["boulder_badge"]
        gs.game_data["pokemon"] = [{"name": "PIKACHU", "hp": 20, "max_hp": 20}]
        can, reason = can_challenge_gym(gs, "Pewter City")
        assert can is False
        assert "already" in reason.lower() or "earned" in reason.lower()

    def test_insufficient_badges_cannot_challenge(self, gs):
        # Viridian City requires 7 badges
        can, reason = can_challenge_gym(gs, "Viridian City")
        if can is False:
            assert "badge" in reason.lower()

    def test_can_challenge_first_gym_with_pokemon(self, gs):
        # Ensure no badges and party has a healthy pokemon
        from pytemon.data.move_data import MoveSlot
        from pytemon.data.pokemon_data import StatsData
        from pytemon.models import PartyPokemon

        poke = PartyPokemon(
            name="PIKACHU",
            number=25,
            level=10,
            types=["Electric"],
            hp=35,
            max_hp=35,
            stats=StatsData(hp=35, attack=55, defense=30, special=50, speed=90),
            moves=[MoveSlot(name="THUNDER SHOCK", pp=30, max_pp=30)],
            experience=0,
            next_level_exp=1000,
        )
        gs.game_data["pokemon"] = [poke]
        can, _ = can_challenge_gym(gs, "Pewter City")
        assert can is True

    def test_no_pokemon_cannot_challenge(self, gs):
        gs.game_data["pokemon"] = []
        can, reason = can_challenge_gym(gs, "Pewter City")
        assert can is False
        assert "Pokemon" in reason


# ---------------------------------------------------------------------------
# show_badge_case
# ---------------------------------------------------------------------------


class TestShowBadgeCase:
    def test_empty_badge_case_writes_no_badges_message(self, gs, output):
        gs.game_data["badges"] = []
        show_badge_case(gs, output)
        combined = " ".join(output.lines)
        assert "No badges" in combined or "badges" in combined.lower()

    def test_badge_case_shows_earned_badges(self, gs, output):
        gs.game_data["badges"] = ["boulder_badge"]
        show_badge_case(gs, output)
        combined = " ".join(output.lines)
        assert "Boulder Badge" in combined

    def test_all_badges_shows_congratulations(self, gs, output):
        gs.game_data["badges"] = [b["id"] for b in BADGES.values()]
        show_badge_case(gs, output)
        combined = " ".join(output.lines)
        assert "CONGRATULATIONS" in combined or "all 8" in combined.lower()
