"""Tests for Phase 5 game content: Elite Four & Champion (Pokemon League)."""

import pytest

from pytemon.buildings import (
    enter_elite_four,
    enter_hall_of_fame,
    enter_pokemon_league_reception,
    handle_elite_four_victory,
)
from pytemon.data.trainer_data import TRAINERS
from pytemon.game_state import GameState
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


def give_all_badges(gs: GameState) -> None:
    """Give the game state all 8 badges."""
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


def add_live_pokemon_to_party(gs: GameState) -> None:
    """Ensure party has at least one conscious Pokemon."""
    from pytemon.engine import BattleState

    bs = BattleState()
    p = bs.generate_wild_pokemon("PIKACHU", 50)
    gs.game_data.setdefault("pokemon", []).append(p)


def _set_all_e4_flags(gs: GameState) -> None:
    """Set all Elite Four defeat flags (Lorelei through Lance, but not Champion)."""
    flags = gs.game_data.setdefault("story_flags", {})
    flags["defeated_lorelei"] = True
    flags["defeated_bruno"] = True
    flags["defeated_agatha"] = True
    flags["defeated_lance"] = True


def noop(*_a, **_kw):
    pass


# ===========================================================================
# TestEliteFourTrainerData
# ===========================================================================


class TestEliteFourTrainerData:
    def test_lorelei_exists(self):
        assert "elite_lorelei" in TRAINERS

    def test_lorelei_has_lapras(self):
        trainer = TRAINERS["elite_lorelei"]
        last = trainer.pokemon[-1]
        assert last.species == "LAPRAS"
        assert last.level == 60

    def test_lorelei_has_dewgong(self):
        trainer = TRAINERS["elite_lorelei"]
        first = trainer.pokemon[0]
        assert first.species == "DEWGONG"

    def test_bruno_exists(self):
        assert "elite_bruno" in TRAINERS

    def test_bruno_has_machamp(self):
        trainer = TRAINERS["elite_bruno"]
        last = trainer.pokemon[-1]
        assert last.species == "MACHAMP"

    def test_agatha_exists(self):
        assert "elite_agatha" in TRAINERS

    def test_agatha_has_gengar_as_lead(self):
        trainer = TRAINERS["elite_agatha"]
        first = trainer.pokemon[0]
        assert first.species == "GENGAR"

    def test_agatha_has_multiple_gengar(self):
        trainer = TRAINERS["elite_agatha"]
        gengar_count = sum(1 for p in trainer.pokemon if p.species == "GENGAR")
        assert gengar_count >= 2

    def test_lance_exists(self):
        assert "elite_lance" in TRAINERS

    def test_lance_has_dragonite(self):
        trainer = TRAINERS["elite_lance"]
        last = trainer.pokemon[-1]
        assert last.species == "DRAGONITE"

    def test_lance_has_two_dragonair(self):
        trainer = TRAINERS["elite_lance"]
        dragonair_count = sum(1 for p in trainer.pokemon if p.species == "DRAGONAIR")
        assert dragonair_count == 2

    def test_champion_gary_bulbasaur_exists(self):
        assert "champion_gary_bulbasaur" in TRAINERS

    def test_champion_gary_charmander_exists(self):
        assert "champion_gary_charmander" in TRAINERS

    def test_champion_gary_squirtle_exists(self):
        assert "champion_gary_squirtle" in TRAINERS

    def test_gary_bulbasaur_has_charizard(self):
        trainer = TRAINERS["champion_gary_bulbasaur"]
        last = trainer.pokemon[-1]
        assert last.species == "CHARIZARD"
        assert last.level == 65

    def test_gary_charmander_has_blastoise(self):
        trainer = TRAINERS["champion_gary_charmander"]
        last = trainer.pokemon[-1]
        assert last.species == "BLASTOISE"

    def test_gary_squirtle_has_venusaur(self):
        trainer = TRAINERS["champion_gary_squirtle"]
        last = trainer.pokemon[-1]
        assert last.species == "VENUSAUR"

    def test_gary_all_have_pidgeot(self):
        gary_ids = (
            "champion_gary_bulbasaur",
            "champion_gary_charmander",
            "champion_gary_squirtle",
        )
        for tid in gary_ids:
            trainer = TRAINERS[tid]
            species_list = [p.species for p in trainer.pokemon]
            assert "PIDGEOT" in species_list, f"{tid} is missing PIDGEOT"

    def test_all_elite_four_are_level_50_plus(self):
        e4_ids = ("elite_lorelei", "elite_bruno", "elite_agatha", "elite_lance")
        for tid in e4_ids:
            trainer = TRAINERS[tid]
            for p in trainer.pokemon:
                assert p.level >= 50, f"{tid} has {p.species} Lv.{p.level} which is below 50"


# ===========================================================================
# TestPokemonLeagueLocation
# ===========================================================================


class TestPokemonLeagueLocation:
    def test_pokemon_league_exists(self):
        assert "Pokemon League" in LOCATIONS

    def test_pokemon_league_has_reception_building(self):
        loc = LOCATIONS["Pokemon League"]
        assert "Pokemon League Reception" in loc.buildings

    def test_pokemon_league_has_elite_four_building(self):
        loc = LOCATIONS["Pokemon League"]
        assert "Elite Four" in loc.buildings

    def test_pokemon_league_exits_to_victory_road(self):
        loc = LOCATIONS["Pokemon League"]
        assert "Victory Road" in loc.exits

    def test_hall_of_fame_is_blocked(self):
        loc = LOCATIONS["Pokemon League"]
        assert "Hall of Fame" in loc.blocked_buildings


# ===========================================================================
# TestEliteFourEntry
# ===========================================================================


class TestEliteFourEntry:
    def test_entry_blocked_without_8_badges(self, gs, log):
        # Give only 7 badges - missing earth_badge
        gs.game_data["badges"] = [
            "boulder_badge",
            "cascade_badge",
            "thunder_badge",
            "rainbow_badge",
            "soul_badge",
            "marsh_badge",
            "volcano_badge",
        ]
        enter_elite_four(gs, log, noop)
        assert "8 Gym Badges" in log.combined

    def test_entry_allowed_with_8_badges(self, gs, log):
        give_all_badges(gs)
        add_live_pokemon_to_party(gs)
        called_with = []

        def capture(trainer):
            called_with.append(trainer)

        enter_elite_four(gs, log, capture)
        assert len(called_with) == 1

    def test_entry_blocked_with_fainted_party(self, gs, log):
        give_all_badges(gs)
        from pytemon.engine import BattleState

        bs = BattleState()
        p = bs.generate_wild_pokemon("PIKACHU", 50)
        p["hp"] = 0
        gs.game_data.setdefault("pokemon", []).append(p)
        enter_elite_four(gs, log, noop)
        assert "fainted" in log.combined.lower()

    def test_entry_triggers_lorelei_first(self, gs, log):
        give_all_badges(gs)
        add_live_pokemon_to_party(gs)
        called_with = []

        def capture(trainer):
            called_with.append(trainer)

        enter_elite_four(gs, log, capture)
        assert len(called_with) == 1
        assert called_with[0].id == "elite_lorelei"

    def test_entry_triggers_bruno_after_lorelei(self, gs, log):
        give_all_badges(gs)
        add_live_pokemon_to_party(gs)
        gs.game_data.setdefault("story_flags", {})["defeated_lorelei"] = True
        called_with = []

        def capture(trainer):
            called_with.append(trainer)

        enter_elite_four(gs, log, capture)
        assert len(called_with) == 1
        assert called_with[0].id == "elite_bruno"

    def test_entry_triggers_agatha_after_bruno(self, gs, log):
        give_all_badges(gs)
        add_live_pokemon_to_party(gs)
        flags = gs.game_data.setdefault("story_flags", {})
        flags["defeated_lorelei"] = True
        flags["defeated_bruno"] = True
        called_with = []

        def capture(trainer):
            called_with.append(trainer)

        enter_elite_four(gs, log, capture)
        assert len(called_with) == 1
        assert called_with[0].id == "elite_agatha"

    def test_entry_triggers_lance_after_agatha(self, gs, log):
        give_all_badges(gs)
        add_live_pokemon_to_party(gs)
        flags = gs.game_data.setdefault("story_flags", {})
        flags["defeated_lorelei"] = True
        flags["defeated_bruno"] = True
        flags["defeated_agatha"] = True
        called_with = []

        def capture(trainer):
            called_with.append(trainer)

        enter_elite_four(gs, log, capture)
        assert len(called_with) == 1
        assert called_with[0].id == "elite_lance"

    def test_entry_triggers_gary_after_lance(self, gs, log):
        give_all_badges(gs)
        add_live_pokemon_to_party(gs)
        _set_all_e4_flags(gs)
        called_with = []

        def capture(trainer):
            called_with.append(trainer)

        enter_elite_four(gs, log, capture)
        assert len(called_with) == 1
        assert "champion_gary" in called_with[0].id

    def test_gary_id_matches_bulbasaur_starter(self, gs, log):
        give_all_badges(gs)
        add_live_pokemon_to_party(gs)
        _set_all_e4_flags(gs)
        gs.game_data["starter"] = "BULBASAUR"
        called_with = []

        def capture(trainer):
            called_with.append(trainer)

        enter_elite_four(gs, log, capture)
        assert called_with[0].id == "champion_gary_bulbasaur"

    def test_gary_id_matches_charmander_starter(self, gs, log):
        give_all_badges(gs)
        add_live_pokemon_to_party(gs)
        _set_all_e4_flags(gs)
        gs.game_data["starter"] = "CHARMANDER"
        called_with = []

        def capture(trainer):
            called_with.append(trainer)

        enter_elite_four(gs, log, capture)
        assert called_with[0].id == "champion_gary_charmander"

    def test_gary_id_matches_squirtle_starter(self, gs, log):
        give_all_badges(gs)
        add_live_pokemon_to_party(gs)
        _set_all_e4_flags(gs)
        gs.game_data["starter"] = "SQUIRTLE"
        called_with = []

        def capture(trainer):
            called_with.append(trainer)

        enter_elite_four(gs, log, capture)
        assert called_with[0].id == "champion_gary_squirtle"

    def test_gary_defaults_to_charmander_variant(self, gs, log):
        give_all_badges(gs)
        add_live_pokemon_to_party(gs)
        _set_all_e4_flags(gs)
        # No starter key set - empty string resolves to charmander variant
        gs.game_data.pop("starter", None)
        called_with = []

        def capture(trainer):
            called_with.append(trainer)

        enter_elite_four(gs, log, capture)
        assert called_with[0].id == "champion_gary_charmander"

    def test_entry_shows_champion_already_when_all_defeated(self, gs, log):
        give_all_badges(gs)
        add_live_pokemon_to_party(gs)
        gs.game_data.setdefault("story_flags", {})["defeated_champion"] = True
        enter_elite_four(gs, log, noop)
        assert "Champion" in log.combined


# ===========================================================================
# TestEliteFourVictory
# ===========================================================================


class TestEliteFourVictory:
    def test_lorelei_victory_sets_flag(self, gs, log):
        handle_elite_four_victory(gs, "elite_lorelei", log)
        assert gs.game_data["story_flags"].get("defeated_lorelei") is True

    def test_bruno_victory_sets_flag(self, gs, log):
        handle_elite_four_victory(gs, "elite_bruno", log)
        assert gs.game_data["story_flags"].get("defeated_bruno") is True

    def test_agatha_victory_sets_flag(self, gs, log):
        handle_elite_four_victory(gs, "elite_agatha", log)
        assert gs.game_data["story_flags"].get("defeated_agatha") is True

    def test_lance_victory_sets_flag(self, gs, log):
        handle_elite_four_victory(gs, "elite_lance", log)
        assert gs.game_data["story_flags"].get("defeated_lance") is True

    def test_champion_victory_sets_defeated_champion(self, gs, log):
        handle_elite_four_victory(gs, "champion_gary_charmander", log)
        assert gs.game_data["story_flags"].get("defeated_champion") is True

    def test_champion_victory_sets_is_champion(self, gs, log):
        handle_elite_four_victory(gs, "champion_gary_bulbasaur", log)
        assert gs.game_data["story_flags"].get("is_champion") is True

    def test_champion_victory_saves_hall_of_fame_party(self, gs, log):
        add_live_pokemon_to_party(gs)
        handle_elite_four_victory(gs, "champion_gary_charmander", log)
        hof_party = gs.game_data["story_flags"].get("hall_of_fame_party")
        assert isinstance(hof_party, list)
        assert len(hof_party) >= 1

    def test_hall_of_fame_party_snapshot_contains_names(self, gs, log):
        add_live_pokemon_to_party(gs)
        handle_elite_four_victory(gs, "champion_gary_squirtle", log)
        hof_party = gs.game_data["story_flags"]["hall_of_fame_party"]
        for entry in hof_party:
            assert "name" in entry
            assert "level" in entry


# ===========================================================================
# TestHallOfFame
# ===========================================================================


class TestHallOfFame:
    def test_hall_of_fame_locked_before_champion(self, gs, log):
        enter_hall_of_fame(gs, log)
        assert "reserved" in log.combined.lower()

    def test_hall_of_fame_shows_after_champion(self, gs, log):
        gs.game_data.setdefault("story_flags", {})["defeated_champion"] = True
        enter_hall_of_fame(gs, log)
        assert "Champion" in log.combined

    def test_hall_of_fame_displays_party_snapshot(self, gs, log):
        flags = gs.game_data.setdefault("story_flags", {})
        flags["defeated_champion"] = True
        flags["hall_of_fame_party"] = [{"name": "PIKACHU", "level": 50}]
        enter_hall_of_fame(gs, log)
        assert "PIKACHU" in log.combined

    def test_hall_of_fame_shows_player_name(self, gs, log):
        gs.game_data["player_name"] = "AshKetchum"
        gs.game_data.setdefault("story_flags", {})["defeated_champion"] = True
        enter_hall_of_fame(gs, log)
        assert "AshKetchum" in log.combined


# ===========================================================================
# TestPokemonLeagueReception
# ===========================================================================


class TestPokemonLeagueReception:
    def test_reception_can_be_entered(self, gs, log):
        enter_pokemon_league_reception(gs, log)
        assert len(log.lines) > 0

    def test_reception_shows_next_challenger_lorelei(self, gs, log):
        # No flags set - Lorelei is the first unchallenged opponent
        enter_pokemon_league_reception(gs, log)
        assert "Lorelei" in log.combined

    def test_reception_shows_next_challenger_bruno(self, gs, log):
        gs.game_data.setdefault("story_flags", {})["defeated_lorelei"] = True
        enter_pokemon_league_reception(gs, log)
        assert "Bruno" in log.combined

    def test_reception_shows_champion_already(self, gs, log):
        gs.game_data.setdefault("story_flags", {})["defeated_champion"] = True
        enter_pokemon_league_reception(gs, log)
        assert "Champion" in log.combined
