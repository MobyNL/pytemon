"""Tests for Phase 4 game content: Saffron City, Cinnabar Island, Victory Road."""

import pytest

from pytemon.buildings import enter_pokemon_lab, enter_pokemon_mansion, enter_silph_co
from pytemon.data.trainer_data import TRAINERS
from pytemon.exploration import move_to_location
from pytemon.game_state import GameState
from pytemon.gym_system import GYM_TRAINERS, GYMS, can_challenge_gym
from pytemon.locations import LOCATIONS


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
def log() -> MockRichLog:
    return MockRichLog()


def make_party_pokemon(gs, name="PIKACHU", level=10):
    from pytemon.engine import BattleState

    bs = BattleState()
    p = bs.generate_wild_pokemon(name, level)
    gs.game_data.setdefault("pokemon", []).append(p)
    return p


def noop(*_a, **_kw):
    pass


# ===========================================================================
# Location data tests
# ===========================================================================


class TestPhase4Locations:
    def test_saffron_city_exists(self):
        assert "Saffron City" in LOCATIONS

    def test_saffron_city_has_correct_exits(self):
        exits = LOCATIONS["Saffron City"].exits
        assert "Route 7" in exits
        assert "Route 8" in exits

    def test_saffron_city_has_correct_buildings(self):
        buildings = LOCATIONS["Saffron City"].buildings
        assert "Silph Co." in buildings
        assert "Sabrina's Gym" in buildings
        assert "Pokemon Center" in buildings
        assert "Pokemart" in buildings

    def test_cinnabar_island_exists(self):
        assert "Cinnabar Island" in LOCATIONS

    def test_cinnabar_island_exits(self):
        exits = LOCATIONS["Cinnabar Island"].exits
        assert "Route 20" in exits
        assert "Route 21" in exits

    def test_cinnabar_island_buildings(self):
        buildings = LOCATIONS["Cinnabar Island"].buildings
        assert "Pokemon Lab" in buildings
        assert "Pokemon Mansion" in buildings
        assert "Blaine's Gym" in buildings

    def test_victory_road_exists(self):
        assert "Victory Road" in LOCATIONS

    def test_victory_road_exits(self):
        exits = LOCATIONS["Victory Road"].exits
        assert "Route 22" in exits
        assert "Pokemon League" in exits

    def test_route_21_exists(self):
        assert "Route 21" in LOCATIONS

    def test_route_21_exits(self):
        exits = LOCATIONS["Route 21"].exits
        assert "Pallet Town" in exits
        assert "Cinnabar Island" in exits

    def test_pokemon_league_stub_exists(self):
        assert "Pokemon League" in LOCATIONS

    def test_pokemon_league_exits_to_victory_road(self):
        exits = LOCATIONS["Pokemon League"].exits
        assert "Victory Road" in exits


# ===========================================================================
# Gym system tests
# ===========================================================================


class TestPhase4Gyms:
    def test_sabrina_gym_registered(self):
        assert "Saffron City" in GYMS

    def test_sabrina_required_badges(self):
        assert GYMS["Saffron City"]["required_badges"] == 5

    def test_sabrina_badge_reward(self):
        assert GYMS["Saffron City"]["badge"] == "Marsh Badge"

    def test_blaine_gym_registered(self):
        assert "Cinnabar Island" in GYMS

    def test_blaine_required_badges(self):
        assert GYMS["Cinnabar Island"]["required_badges"] == 6

    def test_blaine_badge_reward(self):
        assert GYMS["Cinnabar Island"]["badge"] == "Volcano Badge"

    def test_giovanni_gym_registered(self):
        assert "Viridian City" in GYMS

    def test_giovanni_required_badges(self):
        assert GYMS["Viridian City"]["required_badges"] == 7

    def test_giovanni_badge_reward(self):
        assert GYMS["Viridian City"]["badge"] == "Earth Badge"

    def test_sabrina_requires_silph_cleared(self, gs):
        make_party_pokemon(gs)
        gs.game_data["badges"] = [
            "boulder_badge",
            "cascade_badge",
            "thunder_badge",
            "rainbow_badge",
            "soul_badge",
        ]
        gs.game_data["story_flags"]["silph_co_cleared"] = False
        can, _ = can_challenge_gym(gs, "Saffron City")
        assert can is False

    def test_sabrina_allowed_with_silph_cleared(self, gs):
        make_party_pokemon(gs)
        gs.game_data["badges"] = [
            "boulder_badge",
            "cascade_badge",
            "thunder_badge",
            "rainbow_badge",
            "soul_badge",
        ]
        gs.game_data["story_flags"]["silph_co_cleared"] = True
        can, _ = can_challenge_gym(gs, "Saffron City")
        assert can is True

    def test_blaine_requires_secret_key(self, gs):
        make_party_pokemon(gs)
        gs.game_data["badges"] = [
            "boulder_badge",
            "cascade_badge",
            "thunder_badge",
            "rainbow_badge",
            "soul_badge",
            "marsh_badge",
        ]
        gs.game_data["story_flags"]["secret_key_found"] = False
        can, _ = can_challenge_gym(gs, "Cinnabar Island")
        assert can is False

    def test_blaine_allowed_with_secret_key(self, gs):
        make_party_pokemon(gs)
        gs.game_data["badges"] = [
            "boulder_badge",
            "cascade_badge",
            "thunder_badge",
            "rainbow_badge",
            "soul_badge",
            "marsh_badge",
        ]
        gs.game_data["story_flags"]["secret_key_found"] = True
        can, _ = can_challenge_gym(gs, "Cinnabar Island")
        assert can is True

    def test_giovanni_requires_7_badges(self, gs):
        make_party_pokemon(gs)
        # Only 6 badges - falls short of the required 7
        gs.game_data["badges"] = [
            "boulder_badge",
            "cascade_badge",
            "thunder_badge",
            "rainbow_badge",
            "soul_badge",
            "marsh_badge",
        ]
        can, _ = can_challenge_gym(gs, "Viridian City")
        assert can is False

    def test_giovanni_allowed_with_7_badges(self, gs):
        make_party_pokemon(gs)
        gs.game_data["badges"] = [
            "boulder_badge",
            "cascade_badge",
            "thunder_badge",
            "rainbow_badge",
            "soul_badge",
            "marsh_badge",
            "volcano_badge",
        ]
        can, _ = can_challenge_gym(gs, "Viridian City")
        assert can is True

    def test_sabrina_reason_mentions_silph(self, gs):
        make_party_pokemon(gs)
        gs.game_data["badges"] = [
            "boulder_badge",
            "cascade_badge",
            "thunder_badge",
            "rainbow_badge",
            "soul_badge",
        ]
        gs.game_data["story_flags"]["silph_co_cleared"] = False
        _, reason = can_challenge_gym(gs, "Saffron City")
        assert "Silph" in reason or "silph" in reason.lower()

    def test_blaine_reason_mentions_secret_key(self, gs):
        make_party_pokemon(gs)
        gs.game_data["badges"] = [
            "boulder_badge",
            "cascade_badge",
            "thunder_badge",
            "rainbow_badge",
            "soul_badge",
            "marsh_badge",
        ]
        gs.game_data["story_flags"]["secret_key_found"] = False
        _, reason = can_challenge_gym(gs, "Cinnabar Island")
        assert "Key" in reason or "key" in reason.lower() or "locked" in reason.lower()

    def test_saffron_gym_trainers_registered(self):
        assert "Saffron City" in GYM_TRAINERS
        assert len(GYM_TRAINERS["Saffron City"]) > 0

    def test_cinnabar_gym_trainers_include_blaine_trainee(self):
        assert "blaine_trainee" in GYM_TRAINERS.get("Cinnabar Island", [])

    def test_viridian_gym_trainers_include_giovanni_guard(self):
        assert "giovanni_guard" in GYM_TRAINERS.get("Viridian City", [])


# ===========================================================================
# Trainer data tests
# ===========================================================================


class TestPhase4TrainerData:
    def test_sabrina_trainer_exists(self):
        assert "gym_leader_sabrina" in TRAINERS

    def test_sabrina_has_alakazam(self):
        species = [p.species for p in TRAINERS["gym_leader_sabrina"].pokemon]
        assert "ALAKAZAM" in species

    def test_sabrina_has_kadabra(self):
        species = [p.species for p in TRAINERS["gym_leader_sabrina"].pokemon]
        assert "KADABRA" in species

    def test_blaine_trainer_exists(self):
        assert "gym_leader_blaine" in TRAINERS

    def test_blaine_has_arcanine(self):
        species = [p.species for p in TRAINERS["gym_leader_blaine"].pokemon]
        assert "ARCANINE" in species

    def test_blaine_has_rapidash(self):
        species = [p.species for p in TRAINERS["gym_leader_blaine"].pokemon]
        assert "RAPIDASH" in species

    def test_giovanni_trainer_exists(self):
        assert "gym_leader_giovanni" in TRAINERS

    def test_giovanni_has_rhydon(self):
        species = [p.species for p in TRAINERS["gym_leader_giovanni"].pokemon]
        assert "RHYDON" in species

    def test_giovanni_has_nidoking(self):
        species = [p.species for p in TRAINERS["gym_leader_giovanni"].pokemon]
        assert "NIDOKING" in species

    def test_silph_trainers_exist(self):
        assert "rocket_grunt_silph_1" in TRAINERS
        assert "rocket_grunt_silph_2" in TRAINERS
        assert "rocket_grunt_silph_3" in TRAINERS
        assert "silph_executive" in TRAINERS

    def test_mansion_scientists_exist(self):
        assert "scientist_mansion_1" in TRAINERS
        assert "scientist_mansion_2" in TRAINERS

    def test_blaine_trainee_exists(self):
        assert "blaine_trainee" in TRAINERS

    def test_giovanni_guard_exists(self):
        assert "giovanni_guard" in TRAINERS

    def test_saffron_gym_trainers_exist(self):
        # Saffron City has three pre-leader trainers
        saffron_trainers = GYM_TRAINERS.get("Saffron City", [])
        for tid in saffron_trainers:
            assert tid in TRAINERS, f"Gym trainer '{tid}' missing from TRAINERS"


# ===========================================================================
# Silph Co. building tests
# ===========================================================================


class TestSilphCo:
    def test_silph_co_requires_saffron_location(self, gs, log):
        # Silph Co. is not available at Pallet Town - enter_building shows error
        from pytemon.buildings import enter_building

        gs.current_location = LOCATIONS["Pallet Town"]
        enter_building(gs, "Silph Co.", log, noop)
        assert "❌" in log.combined or "not found" in log.combined.lower()

    def test_silph_co_cleared_awards_master_ball(self, gs, log):
        gs.game_data["defeated_trainers"] = [
            "rocket_grunt_silph_1",
            "rocket_grunt_silph_2",
            "rocket_grunt_silph_3",
            "silph_executive",
        ]
        enter_silph_co(gs, log, trigger_trainer_battle_callback=None)
        assert gs.game_data["story_flags"]["silph_co_cleared"] is True
        assert gs.game_data["items"].get("Master Ball", 0) == 1

    def test_silph_co_cleared_sets_rescued_fuji_flag(self, gs, log):
        gs.game_data["defeated_trainers"] = [
            "rocket_grunt_silph_1",
            "rocket_grunt_silph_2",
            "rocket_grunt_silph_3",
            "silph_executive",
        ]
        enter_silph_co(gs, log, trigger_trainer_battle_callback=None)
        assert gs.game_data["story_flags"]["rescued_mr_fuji_silph"] is True

    def test_silph_co_already_cleared_message(self, gs, log):
        gs.game_data["story_flags"]["silph_co_cleared"] = True
        enter_silph_co(gs, log, trigger_trainer_battle_callback=None)
        combined_lower = log.combined.lower()
        assert (
            "safe" in combined_lower or "gratitude" in combined_lower or "thanks" in combined_lower
        )

    def test_silph_co_triggers_battle_for_next_trainer(self, gs, log):
        battles = []

        def mock_battle(trainer):
            battles.append(trainer)

        gs.game_data["defeated_trainers"] = []
        enter_silph_co(gs, log, trigger_trainer_battle_callback=mock_battle)
        assert len(battles) == 1
        assert battles[0].id == "rocket_grunt_silph_1"

    def test_silph_co_partial_progress_shows_remaining(self, gs, log):
        gs.game_data["defeated_trainers"] = ["rocket_grunt_silph_1"]
        enter_silph_co(gs, log, trigger_trainer_battle_callback=None)
        assert "1/4" in log.combined or "3 member" in log.combined

    def test_silph_co_no_duplicate_master_ball_when_already_cleared(self, gs, log):
        gs.game_data["story_flags"]["silph_co_cleared"] = True
        gs.game_data["items"]["Master Ball"] = 1
        enter_silph_co(gs, log, trigger_trainer_battle_callback=None)
        # Should NOT award another Master Ball
        assert gs.game_data["items"].get("Master Ball", 0) == 1


# ===========================================================================
# Pokemon Mansion building tests
# ===========================================================================


class TestPokemonMansion:
    def test_mansion_awards_secret_key_when_all_defeated(self, gs, log):
        gs.game_data["defeated_trainers"] = [
            "scientist_mansion_1",
            "scientist_mansion_2",
        ]
        enter_pokemon_mansion(gs, log, trigger_trainer_battle_callback=None)
        assert gs.game_data["story_flags"]["secret_key_found"] is True
        assert gs.game_data["items"].get("Secret Key", 0) == 1

    def test_mansion_already_has_key_message(self, gs, log):
        gs.game_data["story_flags"]["secret_key_found"] = True
        enter_pokemon_mansion(gs, log, trigger_trainer_battle_callback=None)
        combined_lower = log.combined.lower()
        assert "already" in combined_lower or "nothing" in combined_lower

    def test_mansion_triggers_first_scientist_battle(self, gs, log):
        battles = []

        def mock_battle(trainer):
            battles.append(trainer)

        gs.game_data["defeated_trainers"] = []
        enter_pokemon_mansion(gs, log, trigger_trainer_battle_callback=mock_battle)
        assert len(battles) == 1
        assert battles[0].id == "scientist_mansion_1"

    def test_mansion_triggers_second_scientist_after_first_defeated(self, gs, log):
        battles = []

        def mock_battle(trainer):
            battles.append(trainer)

        gs.game_data["defeated_trainers"] = ["scientist_mansion_1"]
        enter_pokemon_mansion(gs, log, trigger_trainer_battle_callback=mock_battle)
        assert len(battles) == 1
        assert battles[0].id == "scientist_mansion_2"

    def test_mansion_no_duplicate_secret_key_if_already_cleared(self, gs, log):
        gs.game_data["story_flags"]["secret_key_found"] = True
        gs.game_data["items"]["Secret Key"] = 1
        enter_pokemon_mansion(gs, log, trigger_trainer_battle_callback=None)
        assert gs.game_data["items"].get("Secret Key", 0) == 1


# ===========================================================================
# Pokemon Lab fossil revival tests
# ===========================================================================


class TestPokemonLab:
    def test_lab_revives_dome_fossil_to_kabuto(self, gs, log):
        gs.game_data["items"] = {"Dome Fossil": 1}
        enter_pokemon_lab(gs, log)
        party = gs.game_data.get("pokemon", [])
        assert any(p.name == "KABUTO" for p in party)
        assert gs.game_data["story_flags"]["revived_dome_fossil"] is True

    def test_lab_revives_helix_fossil_to_omanyte(self, gs, log):
        gs.game_data["items"] = {"Helix Fossil": 1}
        enter_pokemon_lab(gs, log)
        party = gs.game_data.get("pokemon", [])
        assert any(p.name == "OMANYTE" for p in party)
        assert gs.game_data["story_flags"]["revived_helix_fossil"] is True

    def test_lab_no_fossils_message(self, gs, log):
        gs.game_data["items"] = {}
        enter_pokemon_lab(gs, log)
        assert "fossil" in log.combined.lower()

    def test_lab_revives_both_fossils(self, gs, log):
        gs.game_data["items"] = {"Dome Fossil": 1, "Helix Fossil": 1}
        enter_pokemon_lab(gs, log)
        party = gs.game_data.get("pokemon", [])
        names = [p.name for p in party]
        assert "KABUTO" in names
        assert "OMANYTE" in names

    def test_fossil_already_revived_not_duplicated(self, gs, log):
        gs.game_data["items"] = {"Dome Fossil": 1}
        gs.game_data["story_flags"]["revived_dome_fossil"] = True
        enter_pokemon_lab(gs, log)
        party = gs.game_data.get("pokemon", [])
        kabuto_count = sum(1 for p in party if p.name == "KABUTO")
        assert kabuto_count == 0

    def test_lab_removes_dome_fossil_from_bag_after_revival(self, gs, log):
        gs.game_data["items"] = {"Dome Fossil": 1}
        enter_pokemon_lab(gs, log)
        assert gs.game_data["items"].get("Dome Fossil", 0) == 0

    def test_lab_removes_helix_fossil_from_bag_after_revival(self, gs, log):
        gs.game_data["items"] = {"Helix Fossil": 1}
        enter_pokemon_lab(gs, log)
        assert gs.game_data["items"].get("Helix Fossil", 0) == 0

    def test_lab_kabuto_is_level_5(self, gs, log):
        gs.game_data["items"] = {"Dome Fossil": 1}
        enter_pokemon_lab(gs, log)
        party = gs.game_data.get("pokemon", [])
        kabuto = next(p for p in party if p.name == "KABUTO")
        assert kabuto.level == 5

    def test_lab_omanyte_is_level_5(self, gs, log):
        gs.game_data["items"] = {"Helix Fossil": 1}
        enter_pokemon_lab(gs, log)
        party = gs.game_data.get("pokemon", [])
        omanyte = next(p for p in party if p.name == "OMANYTE")
        assert omanyte.level == 5


# ===========================================================================
# Navigation gate tests
# ===========================================================================


class TestPhase4Navigation:
    def test_saffron_gate_blocks_without_badge_or_flag(self, gs, log):
        gs.current_location = LOCATIONS["Route 7"]
        gs.cheat_mode = False
        gs.game_data["badges"] = []
        gs.game_data["story_flags"]["silph_co_cleared"] = False
        move_to_location(gs, "Saffron City", log, noop)
        assert gs.current_location.name == "Route 7"
        assert "⚠" in log.combined or "sealed" in log.combined.lower()

    def test_saffron_gate_allows_with_marsh_badge(self, gs, log):
        gs.current_location = LOCATIONS["Route 7"]
        gs.cheat_mode = False
        gs.game_data["badges"] = ["marsh_badge"]
        move_to_location(gs, "Saffron City", log, noop)
        assert gs.current_location.name == "Saffron City"

    def test_saffron_gate_allows_with_silph_cleared(self, gs, log):
        gs.current_location = LOCATIONS["Route 7"]
        gs.cheat_mode = False
        gs.game_data["badges"] = []
        gs.game_data["story_flags"]["silph_co_cleared"] = True
        move_to_location(gs, "Saffron City", log, noop)
        assert gs.current_location.name == "Saffron City"

    def test_victory_road_requires_all_8_badges(self, gs, log):
        gs.current_location = LOCATIONS["Route 22"]
        gs.cheat_mode = False
        # Only 7 badges - missing earth_badge
        gs.game_data["badges"] = [
            "boulder_badge",
            "cascade_badge",
            "thunder_badge",
            "rainbow_badge",
            "soul_badge",
            "marsh_badge",
            "volcano_badge",
        ]
        move_to_location(gs, "Victory Road", log, noop)
        assert gs.current_location.name == "Route 22"
        assert "⚠" in log.combined or "8" in log.combined

    def test_victory_road_allows_with_8_badges(self, gs, log):
        gs.current_location = LOCATIONS["Route 22"]
        gs.cheat_mode = False
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
        # Satisfy Route 22's min_explores requirement (6)
        gs.game_data.setdefault("route_progress", {})["Route 22"] = 6
        move_to_location(gs, "Victory Road", log, noop)
        assert gs.current_location.name == "Victory Road"

    def test_route_21_surf_gate_from_pallet_town(self, gs, log):
        gs.current_location = LOCATIONS["Pallet Town"]
        gs.cheat_mode = False
        gs.game_data["surf_unlocked"] = []
        move_to_location(gs, "Route 21", log, noop)
        assert gs.current_location.name == "Pallet Town"
        assert "⚠" in log.combined or "surf" in log.combined.lower()

    def test_route_21_surf_gate_from_cinnabar(self, gs, log):
        gs.current_location = LOCATIONS["Cinnabar Island"]
        gs.cheat_mode = False
        gs.game_data["surf_unlocked"] = []
        move_to_location(gs, "Route 21", log, noop)
        assert gs.current_location.name == "Cinnabar Island"
        assert "⚠" in log.combined or "surf" in log.combined.lower()

    def test_route_21_allowed_with_surf_from_pallet_town(self, gs, log):
        gs.current_location = LOCATIONS["Pallet Town"]
        gs.cheat_mode = False
        gs.game_data["surf_unlocked"] = ["Route 21"]
        move_to_location(gs, "Route 21", log, noop)
        assert gs.current_location.name == "Route 21"

    def test_route_21_allowed_with_surf_from_cinnabar(self, gs, log):
        gs.current_location = LOCATIONS["Cinnabar Island"]
        gs.cheat_mode = False
        gs.game_data["surf_unlocked"] = ["Route 21"]
        move_to_location(gs, "Route 21", log, noop)
        assert gs.current_location.name == "Route 21"

    def test_saffron_gate_block_reason_mentions_silph(self, gs, log):
        gs.current_location = LOCATIONS["Route 8"]
        gs.cheat_mode = False
        gs.game_data["badges"] = []
        gs.game_data["story_flags"]["silph_co_cleared"] = False
        move_to_location(gs, "Saffron City", log, noop)
        combined_lower = log.combined.lower()
        assert "silph" in combined_lower or "sealed" in combined_lower or "gate" in combined_lower

    def test_victory_road_gate_reason_mentions_badges(self, gs, log):
        gs.current_location = LOCATIONS["Route 22"]
        gs.cheat_mode = False
        gs.game_data["badges"] = []
        move_to_location(gs, "Victory Road", log, noop)
        assert "badge" in log.combined.lower() or "8" in log.combined
