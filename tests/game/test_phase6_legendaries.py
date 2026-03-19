"""Tests for Phase 6 game content: Legendary encounters, Cerulean Cave, rematch system."""

import pytest

from pytemon.buildings import (
    check_legendary_encounter,
    check_pokedex_completion,
    enter_cerulean_cave,
    enter_oaks_lab,
    enter_power_plant,
    enter_seafoam_islands,
    mark_legendary_encountered,
)
from pytemon.data.pokemon_data import POKEMON
from pytemon.data.trainer_data import TRAINERS
from pytemon.game_state import GameState
from pytemon.gym_system import can_rematch_gym, handle_rematch_gym_victory
from pytemon.locations import LOCATIONS

# ===========================================================================
# Test helpers
# ===========================================================================


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


def set_champion(gs: GameState) -> None:
    """Set all badges and champion flag."""
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
    gs.game_data.setdefault("story_flags", {})["is_champion"] = True


def add_party_pokemon(gs: GameState) -> None:
    """Add a basic party Pokemon so the player can explore."""
    gs.game_data["pokemon"] = [
        {
            "name": "PIKACHU",
            "number": 25,
            "level": 50,
            "types": ["Electric"],
            "hp": 100,
            "max_hp": 100,
            "moves": [{"name": "THUNDER SHOCK", "pp": 30, "max_pp": 30}],
            "experience": 0,
        }
    ]


# ===========================================================================
# Legendary Pokemon data
# ===========================================================================


class TestLegendaryPokemonData:
    """Verify all legendary species have correct types and stats."""

    def test_articuno_is_ice_flying(self):
        articuno = POKEMON[144]
        assert "Ice" in articuno.types
        assert "Flying" in articuno.types
        assert articuno.catch_rate == 3

    def test_zapdos_is_electric_flying(self):
        zapdos = POKEMON[145]
        assert "Electric" in zapdos.types
        assert "Flying" in zapdos.types
        assert zapdos.catch_rate == 3

    def test_moltres_is_fire_flying(self):
        moltres = POKEMON[146]
        assert "Fire" in moltres.types
        assert "Flying" in moltres.types
        assert moltres.catch_rate == 3

    def test_mewtwo_is_psychic(self):
        mewtwo = POKEMON[150]
        assert mewtwo.types == ["Psychic"]
        assert mewtwo.stats.hp == 106
        assert mewtwo.catch_rate == 3

    def test_mew_is_psychic(self):
        mew = POKEMON[151]
        assert mew.types == ["Psychic"]
        assert mew.stats.hp == 100
        assert mew.catch_rate == 45

    def test_no_legendary_is_normal_type(self):
        for num in [144, 145, 146, 150, 151]:
            species = POKEMON[num]
            assert "Normal" not in species.types, f"#{num} {species.name} should not be Normal type"

    def test_dratini_is_dragon(self):
        assert POKEMON[147].types == ["Dragon"]

    def test_dragonite_is_dragon_flying(self):
        dragonite = POKEMON[149]
        assert "Dragon" in dragonite.types
        assert "Flying" in dragonite.types

    def test_legendary_birds_have_learnsets(self):
        for num in [144, 145, 146]:
            learnset = POKEMON[num].learnset
            assert learnset, f"#{num} has empty learnset"
            assert any(learnset.values()), f"#{num} learnset has no moves"


# ===========================================================================
# New locations
# ===========================================================================


class TestNewLocations:
    """Verify Power Plant, Seafoam Islands, and Cerulean Cave exist."""

    def test_power_plant_in_locations(self):
        assert "Power Plant" in LOCATIONS

    def test_seafoam_islands_in_locations(self):
        assert "Seafoam Islands" in LOCATIONS

    def test_cerulean_cave_in_locations(self):
        assert "Cerulean Cave" in LOCATIONS

    def test_power_plant_exit_from_route_10(self):
        route_10 = LOCATIONS["Route 10"]
        assert "Power Plant" in route_10.exits

    def test_seafoam_islands_exit_from_route_20(self):
        route_20 = LOCATIONS["Route 20"]
        assert "Seafoam Islands" in route_20.exits

    def test_cerulean_cave_exit_from_cerulean_city(self):
        cerulean = LOCATIONS["Cerulean City"]
        assert "Cerulean Cave" in cerulean.exits

    def test_power_plant_has_wild_pokemon(self):
        assert LOCATIONS["Power Plant"].wild_pokemon

    def test_seafoam_islands_has_wild_pokemon(self):
        assert LOCATIONS["Seafoam Islands"].wild_pokemon

    def test_cerulean_cave_has_wild_pokemon(self):
        assert LOCATIONS["Cerulean Cave"].wild_pokemon


# ===========================================================================
# Legendary encounter logic
# ===========================================================================


class TestCheckLegendaryEncounter:
    """Test check_legendary_encounter one-time trigger."""

    def test_power_plant_triggers_zapdos(self, gs, log):
        triggered_count = [0]

        def fake_trigger():
            triggered_count[0] += 1

        result = check_legendary_encounter(gs, "Power Plant", log, fake_trigger)
        assert result is True
        assert triggered_count[0] == 1
        assert gs.game_data.get("_forced_encounter", {}).get("species") == "ZAPDOS"

    def test_seafoam_islands_triggers_articuno(self, gs, log):
        triggered_count = [0]

        def fake_trigger():
            triggered_count[0] += 1

        result = check_legendary_encounter(gs, "Seafoam Islands", log, fake_trigger)
        assert result is True
        assert triggered_count[0] == 1
        assert gs.game_data.get("_forced_encounter", {}).get("species") == "ARTICUNO"

    def test_cerulean_cave_triggers_mewtwo(self, gs, log):
        triggered_count = [0]

        def fake_trigger():
            triggered_count[0] += 1

        result = check_legendary_encounter(gs, "Cerulean Cave", log, fake_trigger)
        assert result is True
        assert triggered_count[0] == 1
        assert gs.game_data.get("_forced_encounter", {}).get("species") == "MEWTWO"

    def test_does_not_trigger_twice(self, gs, log):
        triggered = [0]
        check_legendary_encounter(
            gs, "Power Plant", log, lambda: triggered.__setitem__(0, triggered[0] + 1)
        )
        second = check_legendary_encounter(
            gs, "Power Plant", log, lambda: triggered.__setitem__(0, triggered[0] + 1)
        )
        assert second is False
        assert triggered[0] == 1

    def test_sets_flag_on_first_trigger(self, gs, log):
        check_legendary_encounter(gs, "Power Plant", log, lambda: None)
        assert gs.game_data["story_flags"].get("found_zapdos") is True

    def test_unknown_location_returns_false(self, gs, log):
        result = check_legendary_encounter(gs, "Pallet Town", log, lambda: None)
        assert result is False

    def test_non_legendary_location_returns_false(self, gs, log):
        result = check_legendary_encounter(gs, "Viridian City", log, lambda: None)
        assert result is False


class TestMarkLegendaryEncountered:
    """Test manual flag setting."""

    def test_mark_sets_flag(self, gs):
        mark_legendary_encountered(gs, "Power Plant")
        assert gs.game_data["story_flags"].get("found_zapdos") is True

    def test_mark_unknown_location_noop(self, gs):
        mark_legendary_encountered(gs, "Nowhere")
        # No exception and no flags set
        assert "found_nowhere" not in gs.game_data.get("story_flags", {})


# ===========================================================================
# Dungeon entry helpers
# ===========================================================================


class TestEnterPowerPlant:
    def test_outputs_flavor_text(self, gs, log):
        enter_power_plant(gs, log, lambda: None)
        assert any("Power Plant" in str(line) for line in log.lines)

    def test_triggers_legendary_on_first_visit(self, gs, log):
        triggered = [0]
        enter_power_plant(gs, log, lambda: triggered.__setitem__(0, triggered[0] + 1))
        assert triggered[0] == 1

    def test_no_double_trigger_on_second_entry(self, gs, log):
        triggered = [0]
        enter_power_plant(gs, log, lambda: triggered.__setitem__(0, triggered[0] + 1))
        log2 = MockRichLog()
        enter_power_plant(gs, log2, lambda: triggered.__setitem__(0, triggered[0] + 1))
        assert triggered[0] == 1


class TestEnterSeafoamIslands:
    def test_outputs_flavor_text(self, gs, log):
        enter_seafoam_islands(gs, log, lambda: None)
        assert any("Seafoam" in str(line) for line in log.lines)

    def test_triggers_articuno(self, gs, log):
        triggered = [0]
        enter_seafoam_islands(gs, log, lambda: triggered.__setitem__(0, triggered[0] + 1))
        assert triggered[0] == 1
        assert gs.game_data.get("_forced_encounter", {}).get("species") == "ARTICUNO"


class TestEnterCeruleanCave:
    def test_blocked_before_champion(self, gs, log):
        result = enter_cerulean_cave(gs, log, lambda: None)
        assert result is False
        assert any(
            "sealed" in str(line).lower() or "champion" in str(line).lower() for line in log.lines
        )

    def test_allowed_after_champion(self, gs, log):
        set_champion(gs)
        result = enter_cerulean_cave(gs, log, lambda: None)
        assert result is True

    def test_triggers_mewtwo_after_champion(self, gs, log):
        set_champion(gs)
        triggered = [0]
        enter_cerulean_cave(gs, log, lambda: triggered.__setitem__(0, triggered[0] + 1))
        assert triggered[0] == 1
        assert gs.game_data.get("_forced_encounter", {}).get("species") == "MEWTWO"


# ===========================================================================
# Forced encounter consumption
# ===========================================================================


class TestForcedEncounterConsumed:
    """Verify that trigger_wild_encounter pops _forced_encounter."""

    def test_forced_encounter_is_popped(self, gs):
        from pytemon.battle.battle_actions import trigger_wild_encounter

        add_party_pokemon(gs)
        from pytemon.locations import get_location

        gs.current_location = get_location("Power Plant")
        gs.game_data["_forced_encounter"] = {"species": "ZAPDOS", "level": 50}

        log = MockRichLog()
        trigger_wild_encounter(
            gs,
            log,
            pending_command_callback=lambda cmd: None,
        )
        # The forced encounter key should have been consumed
        assert "_forced_encounter" not in gs.game_data


# ===========================================================================
# Cerulean Cave champion gate (exploration movement)
# ===========================================================================


class TestCeruleanCaveChampionGate:
    """Verify move_to_location respects the champion gate."""

    def test_cave_blocked_before_champion(self, gs, log):
        from pytemon.exploration import move_to_location
        from pytemon.locations import get_location

        gs.current_location = get_location("Cerulean City")
        move_to_location(
            gs, "Cerulean Cave", log, show_arrival_callback=lambda out, load=False: None
        )
        # Should stay in Cerulean City
        assert gs.current_location.name == "Cerulean City"
        assert any("champion" in str(line).lower() for line in log.lines)

    def test_cave_accessible_after_champion(self, gs, log):
        from pytemon.exploration import move_to_location
        from pytemon.locations import get_location

        gs.current_location = get_location("Cerulean City")
        set_champion(gs)
        move_to_location(
            gs, "Cerulean Cave", log, show_arrival_callback=lambda out, load=False: None
        )
        assert gs.current_location.name == "Cerulean Cave"


# ===========================================================================
# Mew secret trigger
# ===========================================================================


class TestMewSecretTrigger:
    """Verify 'the truck is real' queues a Mew forced encounter."""

    def test_phrase_queues_mew_encounter(self, gs, log):
        from pytemon.cheat_commands import check_secret_phrase

        add_party_pokemon(gs)
        from pytemon.locations import get_location

        gs.current_location = get_location("Pallet Town")
        result = check_secret_phrase("the truck is real", gs, log)
        assert result is True
        enc = gs.game_data.get("_forced_encounter")
        assert enc is not None
        assert enc["species"] == "MEW"
        assert enc["level"] == 5

    def test_phrase_only_works_once(self, gs, log):
        from pytemon.cheat_commands import check_secret_phrase

        add_party_pokemon(gs)
        from pytemon.locations import get_location

        gs.current_location = get_location("Pallet Town")
        check_secret_phrase("the truck is real", gs, log)
        # Consume the forced encounter manually
        gs.game_data.pop("_forced_encounter", None)
        log2 = MockRichLog()
        check_secret_phrase("the truck is real", gs, log2)
        # Second time should not re-queue
        assert "_forced_encounter" not in gs.game_data

    def test_mew_flag_set_after_phrase(self, gs, log):
        from pytemon.cheat_commands import check_secret_phrase

        add_party_pokemon(gs)
        from pytemon.locations import get_location

        gs.current_location = get_location("Pallet Town")
        check_secret_phrase("the truck is real", gs, log)
        assert gs.game_data["story_flags"].get("found_mew") is True


# ===========================================================================
# Rematch system
# ===========================================================================


class TestCanRematchGym:
    def test_cannot_rematch_without_champion(self, gs):
        assert can_rematch_gym(gs, "Pewter City") is False

    def test_cannot_rematch_without_badge(self, gs):
        gs.game_data.setdefault("story_flags", {})["is_champion"] = True
        # No badges awarded
        assert can_rematch_gym(gs, "Pewter City") is False

    def test_can_rematch_with_champion_and_badge(self, gs):
        set_champion(gs)
        assert can_rematch_gym(gs, "Pewter City") is True

    def test_rematch_false_for_non_gym_location(self, gs):
        set_champion(gs)
        assert can_rematch_gym(gs, "Pallet Town") is False

    def test_rematch_available_for_all_gyms_as_champion(self, gs):
        set_champion(gs)
        gym_locations = [
            "Pewter City",
            "Cerulean City",
            "Vermillion City",
            "Celadon City",
            "Fuchsia City",
            "Saffron City",
            "Cinnabar Island",
            "Viridian City",
        ]
        for loc in gym_locations:
            assert can_rematch_gym(gs, loc) is True, f"Rematch should be available at {loc}"


class TestRematchTrainerData:
    """Verify rematch trainers exist with correct data."""

    def test_all_rematch_trainers_exist(self):
        rematch_ids = [
            "gym_leader_brock_rematch",
            "gym_leader_misty_rematch",
            "gym_leader_lt_surge_rematch",
            "gym_leader_erika_rematch",
            "gym_leader_koga_rematch",
            "gym_leader_sabrina_rematch",
            "gym_leader_blaine_rematch",
            "gym_leader_giovanni_rematch",
        ]
        for tid in rematch_ids:
            assert tid in TRAINERS, f"Missing rematch trainer: {tid}"

    def test_rematch_trainers_have_no_badge_reward(self):
        from pytemon.data.trainer_data import get_trainer

        rematch_ids = [
            "gym_leader_brock_rematch",
            "gym_leader_misty_rematch",
            "gym_leader_lt_surge_rematch",
        ]
        for tid in rematch_ids:
            trainer = get_trainer(tid)
            assert trainer is not None
            assert trainer.badge_reward is None

    def test_rematch_trainers_are_gym_leader_class(self):
        from pytemon.data.trainer_data import get_trainer

        trainer = get_trainer("gym_leader_brock_rematch")
        assert trainer.trainer_class == "Gym Leader"

    def test_rematch_trainers_have_higher_levels(self):
        from pytemon.data.trainer_data import get_trainer

        brock = get_trainer("gym_leader_brock_rematch")
        assert all(p.level >= 50 for p in brock.pokemon)


class TestHandleRematchGymVictory:
    def test_outputs_success_message(self, gs, log):
        set_champion(gs)
        handle_rematch_gym_victory(gs, "gym_leader_brock_rematch", log)
        assert any(
            "rematch" in str(line).lower() or "champion" in str(line).lower() for line in log.lines
        )

    def test_no_badge_awarded(self, gs, log):
        set_champion(gs)
        badges_before = list(gs.game_data.get("badges", []))
        handle_rematch_gym_victory(gs, "gym_leader_brock_rematch", log)
        assert gs.game_data.get("badges", []) == badges_before


# ===========================================================================
# Pokedex completion reward
# ===========================================================================


class TestCheckPokedexCompletion:
    def test_no_reward_below_151(self, gs, log):
        gs.game_data["pokedex"] = {"caught": list(range(1, 50))}
        result = check_pokedex_completion(gs, log)
        assert result is False

    def test_reward_at_151_caught(self, gs, log):
        gs.game_data["pokedex"] = {"caught": list(range(1, 152))}
        result = check_pokedex_completion(gs, log)
        assert result is True
        assert any(
            "certificate" in str(line).lower() or "complete" in str(line).lower()
            for line in log.lines
        )

    def test_reward_only_once(self, gs, log):
        gs.game_data["pokedex"] = {"caught": list(range(1, 152))}
        check_pokedex_completion(gs, log)
        log2 = MockRichLog()
        result2 = check_pokedex_completion(gs, log2)
        assert result2 is False

    def test_flag_set_after_award(self, gs, log):
        gs.game_data["pokedex"] = {"caught": list(range(1, 152))}
        check_pokedex_completion(gs, log)
        assert gs.game_data["story_flags"].get("oaks_certificate") is True


class TestEnterOaksLabPokedexCheck:
    """Verify Oak's Lab calls check_pokedex_completion."""

    def test_oaks_lab_awards_certificate_when_complete(self, gs, log):
        add_party_pokemon(gs)
        gs.game_data["pokedex"] = {"caught": list(range(1, 152))}
        pending = []
        enter_oaks_lab(gs, log, lambda cmd: pending.append(cmd))
        assert gs.game_data["story_flags"].get("oaks_certificate") is True
        assert any(
            "certificate" in str(line).lower() or "caught all" in str(line).lower()
            for line in log.lines
        )

    def test_oaks_lab_no_certificate_when_incomplete(self, gs, log):
        add_party_pokemon(gs)
        gs.game_data["pokedex"] = {"caught": list(range(1, 50))}
        pending = []
        enter_oaks_lab(gs, log, lambda cmd: pending.append(cmd))
        assert not gs.game_data.get("story_flags", {}).get("oaks_certificate")
