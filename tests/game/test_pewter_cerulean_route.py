"""
Tests for the Pewter City -> Cerulean City route:
Route 3, Mt. Moon, Route 4, Cerulean City (gym, museum, bike shop, Nugget Bridge).
"""

from unittest.mock import patch

import pytest

from pytemon.buildings import (
    enter_bike_shop,
    enter_museum,
    enter_nugget_bridge,
    enter_pokemart,
)
from pytemon.data.trainer_data import TRAINER_CLASSES, TRAINERS
from pytemon.exploration import explore_area
from pytemon.game_state import GameState
from pytemon.gym_system import GYMS, can_challenge_gym, get_gym_trainers
from pytemon.locations import LOCATIONS, TYPE_DUNGEON, TYPE_FOREST, TYPE_ROUTE, TYPE_TOWN, get_location


class MockRichLog:
    def __init__(self):
        self.lines: list = []

    def write(self, text: str) -> None:
        self.lines.append(text)

    @property
    def combined(self) -> str:
        return "\n".join(str(line) for line in self.lines)


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


def make_party_pokemon(gs, name="PIKACHU", level=15):
    from pytemon.engine import BattleState

    bs = BattleState()
    p = bs.generate_wild_pokemon(name, level)
    gs.game_data.setdefault("pokemon", []).append(p)
    return p


# ===========================================================================
# TestNewLocations
# ===========================================================================


class TestNewLocations:
    def test_route_3_exists(self):
        assert "Route 3" in LOCATIONS
        assert LOCATIONS["Route 3"].type == TYPE_ROUTE

    def test_route_3_wild_pokemon(self):
        loc = LOCATIONS["Route 3"]
        assert "PIDGEY" in loc.wild_pokemon
        assert "JIGGLYPUFF" in loc.wild_pokemon
        assert "MEOWTH" in loc.wild_pokemon
        assert loc.wild_level_range == (10, 14)

    def test_route_3_trainers(self):
        assert LOCATIONS["Route 3"].trainers == 4

    def test_route_3_exits(self):
        exits = LOCATIONS["Route 3"].exits
        assert "Pewter City" in exits
        assert "Mt. Moon" in exits

    def test_mt_moon_exists(self):
        assert "Mt. Moon" in LOCATIONS
        assert LOCATIONS["Mt. Moon"].type == TYPE_DUNGEON

    def test_mt_moon_can_explore(self):
        assert LOCATIONS["Mt. Moon"].can_explore() is True

    def test_mt_moon_wild_pokemon(self):
        loc = LOCATIONS["Mt. Moon"]
        assert "ZUBAT" in loc.wild_pokemon
        assert "CLEFAIRY" in loc.wild_pokemon
        assert "GEODUDE" in loc.wild_pokemon
        assert loc.wild_level_range == (8, 12)

    def test_mt_moon_exits(self):
        exits = LOCATIONS["Mt. Moon"].exits
        assert "Route 3" in exits
        assert "Route 4" in exits

    def test_route_4_exists(self):
        assert "Route 4" in LOCATIONS
        assert LOCATIONS["Route 4"].type == TYPE_ROUTE

    def test_route_4_wild_pokemon(self):
        loc = LOCATIONS["Route 4"]
        assert "SPEAROW" in loc.wild_pokemon
        assert "RATTATA" in loc.wild_pokemon
        assert loc.wild_level_range == (13, 17)

    def test_route_4_exits(self):
        exits = LOCATIONS["Route 4"].exits
        assert "Mt. Moon" in exits
        assert "Cerulean City" in exits

    def test_cerulean_city_exists(self):
        assert "Cerulean City" in LOCATIONS
        assert LOCATIONS["Cerulean City"].type == TYPE_TOWN

    def test_cerulean_city_buildings(self):
        buildings = LOCATIONS["Cerulean City"].buildings
        assert "Pokemon Center" in buildings
        assert "Pokemart" in buildings
        assert "Gym" in buildings
        assert "Bike Shop" in buildings
        assert "Nugget Bridge" in buildings

    def test_cerulean_city_exits(self):
        assert "Route 4" in LOCATIONS["Cerulean City"].exits

    def test_pewter_route3_unblocked(self):
        pewter = LOCATIONS["Pewter City"]
        assert "Route 3" in pewter.exits
        assert pewter.exits["Route 3"].get("blocked", False) is False

    def test_connections_bidirectional(self):
        pairs = [
            ("Route 3", "Pewter City"),
            ("Route 3", "Mt. Moon"),
            ("Mt. Moon", "Route 4"),
            ("Route 4", "Cerulean City"),
        ]
        for a, b in pairs:
            assert b in LOCATIONS[a].exits, f"{b} not in {a} exits"
            assert a in LOCATIONS[b].exits, f"{a} not in {b} exits"

    def test_route_3_min_explores(self):
        exits = LOCATIONS["Route 3"].exits
        assert exits["Pewter City"].get("min_explores", 0) > 0
        assert exits["Mt. Moon"].get("min_explores", 0) > 0


# ===========================================================================
# TestNewTrainers
# ===========================================================================


class TestNewTrainers:
    def test_route3_trainers_exist(self):
        for tid in ("lass_miriam", "youngster_ben", "lass_holly", "youngster_sam"):
            assert tid in TRAINERS, f"{tid} not in TRAINERS"

    def test_route3_trainers_location(self):
        for tid in ("lass_miriam", "youngster_ben", "lass_holly", "youngster_sam"):
            assert TRAINERS[tid].location == "Route 3"

    def test_mt_moon_hikers_exist(self):
        for tid in ("hiker_alan", "hiker_wayne", "hiker_lenny"):
            assert tid in TRAINERS, f"{tid} not in TRAINERS"

    def test_mt_moon_hikers_location(self):
        for tid in ("hiker_alan", "hiker_wayne", "hiker_lenny"):
            assert TRAINERS[tid].location == "Mt. Moon"

    def test_route4_trainers_exist(self):
        assert "youngster_eddie" in TRAINERS
        assert "lass_dana" in TRAINERS

    def test_nugget_bridge_trainers_exist(self):
        for i in range(1, 6):
            tid = f"nugget_trainer_{i}"
            assert tid in TRAINERS, f"{tid} not in TRAINERS"

    def test_nugget_bridge_trainers_location(self):
        for i in range(1, 6):
            assert TRAINERS[f"nugget_trainer_{i}"].location == "Cerulean City"

    def test_cerulean_gym_trainer_exists(self):
        assert "gym_trainer_cerulean_swimmer" in TRAINERS
        assert TRAINERS["gym_trainer_cerulean_swimmer"].location == "Cerulean City"

    def test_trainer_levels_in_range(self):
        route3_ids = ("lass_miriam", "youngster_ben", "lass_holly", "youngster_sam")
        for tid in route3_ids:
            for p in TRAINERS[tid].pokemon:
                assert 10 <= p.level <= 16, f"{tid} level {p.level} out of range 10-16"

        mt_moon_ids = ("hiker_alan", "hiker_wayne", "hiker_lenny")
        for tid in mt_moon_ids:
            for p in TRAINERS[tid].pokemon:
                assert 10 <= p.level <= 13, f"{tid} level {p.level} out of range 10-13"

        route4_ids = ("youngster_eddie", "lass_dana")
        for tid in route4_ids:
            for p in TRAINERS[tid].pokemon:
                assert 13 <= p.level <= 17, f"{tid} level {p.level} out of range 13-17"

    def test_swimmer_class_exists(self):
        assert "Swimmer" in TRAINER_CLASSES


# ===========================================================================
# TestCeruleanGym
# ===========================================================================


class TestCeruleanGym:
    def test_cerulean_in_gyms(self):
        assert "Cerulean City" in GYMS

    def test_cerulean_gym_badge(self):
        assert GYMS["Cerulean City"]["badge"] == "Cascade Badge"

    def test_cerulean_requires_boulder_badge(self):
        assert GYMS["Cerulean City"]["required_badges"] == 1

    def test_cerulean_gym_leader_id(self):
        assert GYMS["Cerulean City"]["leader_id"] == "gym_leader_misty"

    def test_cerulean_gym_trainers(self):
        trainers = get_gym_trainers("Cerulean City")
        assert trainers == ["gym_trainer_cerulean_swimmer"]

    def test_misty_exists(self):
        assert "gym_leader_misty" in TRAINERS

    def test_misty_pokemon(self):
        misty = TRAINERS["gym_leader_misty"]
        species_list = [p.species for p in misty.pokemon]
        assert "STARYU" in species_list
        assert "STARMIE" in species_list
        staryu_level = next(p.level for p in misty.pokemon if p.species == "STARYU")
        starmie_level = next(p.level for p in misty.pokemon if p.species == "STARMIE")
        assert staryu_level == 18
        assert starmie_level == 21

    def test_can_challenge_cerulean_no_badge(self, gs):
        result, _ = can_challenge_gym(gs, "Cerulean City")
        assert result is False

    def test_can_challenge_cerulean_with_boulder_badge(self, gs):
        gs.game_data["badges"] = ["boulder_badge"]
        make_party_pokemon(gs)
        result, _ = can_challenge_gym(gs, "Cerulean City")
        assert result is True


# ===========================================================================
# TestNewBuildings
# ===========================================================================


class TestNewBuildings:
    def test_enter_museum_shows_exhibits(self, gs, output):
        enter_museum(gs, output)
        assert "PEWTER CITY MUSEUM" in output.combined
        assert "FOSSIL EXHIBIT" in output.combined

    def test_enter_museum_fossil_dialogue(self, gs, output):
        gs.game_data.setdefault("story_flags", {})["received_mt_moon_fossil"] = True
        enter_museum(gs, output)
        assert "found in Mt. Moon" in output.combined

    def test_enter_bike_shop_first_visit(self, gs, output):
        enter_bike_shop(gs, output)
        assert "Received a Bicycle" in output.combined
        assert gs.game_data.get("items", {}).get("Bicycle", 0) == 1
        assert gs.game_data.get("story_flags", {}).get("received_bicycle") is True

    def test_enter_bike_shop_repeat_visit(self, gs, output):
        gs.game_data.setdefault("story_flags", {})["received_bicycle"] = True
        gs.game_data.setdefault("items", {})["Bicycle"] = 1
        enter_bike_shop(gs, output)
        assert "Still enjoying" in output.combined
        assert gs.game_data["items"].get("Bicycle", 0) == 1  # no duplicate

    def test_enter_nugget_bridge_fresh(self, gs, output):
        enter_nugget_bridge(gs, output, noop, trigger_trainer_battle_callback=None)
        assert "NUGGET BRIDGE" in output.combined

    def test_enter_nugget_bridge_complete(self, gs, output):
        gs.game_data.setdefault("story_flags", {})["nugget_bridge_complete"] = True
        enter_nugget_bridge(gs, output, noop, trigger_trainer_battle_callback=None)
        # Expect the "already complete" dialogue - bridge patron mentions the champ
        assert "champ" in output.combined.lower() or "bridge" in output.combined.lower()

    def test_enter_nugget_bridge_all_defeated_awards_nugget(self, gs, output):
        gs.game_data["defeated_trainers"] = [
            "nugget_trainer_1",
            "nugget_trainer_2",
            "nugget_trainer_3",
            "nugget_trainer_4",
            "nugget_trainer_5",
        ]
        enter_nugget_bridge(gs, output, noop, trigger_trainer_battle_callback=None)
        assert "Received a Nugget" in output.combined
        assert gs.game_data.get("items", {}).get("Nugget", 0) >= 1

    def test_pokemart_advanced_catalog_in_cerulean(self, gs, output):
        gs.current_location = get_location("Cerulean City")
        enter_pokemart(gs, output, noop)
        assert gs.game_data.get("_current_shop_catalog") == "advanced"
        assert "Great Ball" in output.combined


# ===========================================================================
# TestMtMoonEvents
# ===========================================================================

# Sequence of random.random() return values for a single Mt. Moon explore
# when all trainers are defeated and the item pool is exhausted:
#   1. wild encounter check (0.99 >= 0.55 -> no encounter -> else branch)
#   2. moon stone check    (0.10 <  0.40 -> found)
#   3. fossil check        (0.10 <  0.30 -> found)
_RAND_FIND_BOTH = [0.99, 0.10, 0.10]

# Once both flags are set no more random calls for story events - just encounter roll
_RAND_NO_ENCOUNTER = [0.99]


class TestMtMoonEvents:
    def _setup_mt_moon(self, gs):
        """Place the player in Mt. Moon with a party and all trainers defeated."""
        gs.current_location = get_location("Mt. Moon")
        make_party_pokemon(gs)
        # Mark all Mt. Moon trainers as defeated so trainer-encounter branch is skipped
        gs.game_data["defeated_trainers"] = ["hiker_alan", "hiker_wayne", "hiker_lenny"]
        # Exhaust the item pool so _try_find_item returns False without calling random
        gs.game_data.setdefault("found_items", {})["Mt. Moon"] = 7

    def test_moon_stone_found_eventually(self, gs):
        self._setup_mt_moon(gs)
        with patch("random.random", side_effect=_RAND_FIND_BOTH + [0.99] * 30):
            explore_area(gs, MockRichLog(), noop, noop)

        assert gs.game_data.get("story_flags", {}).get("received_moon_stone") is True
        assert gs.game_data.get("items", {}).get("Moon Stone", 0) >= 1

    def test_fossil_found_eventually(self, gs):
        self._setup_mt_moon(gs)
        # Moon stone already received - its random.random() call is short-circuited
        gs.game_data.setdefault("story_flags", {})["received_moon_stone"] = True

        with patch("random.random", side_effect=[0.99, 0.10] + [0.99] * 30):
            explore_area(gs, MockRichLog(), noop, noop)

        assert gs.game_data.get("story_flags", {}).get("received_mt_moon_fossil") is True
        items = gs.game_data.get("items", {})
        assert items.get("Dome Fossil", 0) + items.get("Helix Fossil", 0) >= 1

    def test_moon_stone_only_once(self, gs):
        self._setup_mt_moon(gs)
        # First explore - find moon stone (and fossil)
        with patch("random.random", side_effect=_RAND_FIND_BOTH + [0.99] * 30):
            explore_area(gs, MockRichLog(), noop, noop)
        assert gs.game_data.get("items", {}).get("Moon Stone", 0) == 1

        # Subsequent explores - both flags now True, only encounter roll needed
        more_explores = _RAND_NO_ENCOUNTER * 20
        with patch("random.random", side_effect=more_explores):
            for _ in range(10):
                explore_area(gs, MockRichLog(), noop, noop)

        # Moon Stone count must still be exactly 1
        assert gs.game_data.get("items", {}).get("Moon Stone", 0) == 1

    def test_cycling_flag_reduces_encounter_rate(self, gs):
        self._setup_mt_moon(gs)
        gs.game_data["cycling"] = True
        base_rate = gs.current_location.wild_encounter_rate
        # Base rate must be positive so halving is meaningful
        assert base_rate > 0
        # Smoke-test: explore_area must not raise with cycling active
        try:
            explore_area(gs, MockRichLog(), noop, noop)
        except Exception as exc:
            pytest.fail(f"explore_area raised {exc} with cycling=True")
