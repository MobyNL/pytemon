"""
Unit tests for PokemonLibrary/game_state.py (GameState).
"""

import json

from pytemon.data.move_data import MoveSlot
from pytemon.data.pokemon_data import StatsData
from pytemon.game_state import GameState
from pytemon.models import PartyPokemon


def make_pokemon(name: str = "PIKACHU", number: int = 25, level: int = 10) -> PartyPokemon:
    """Helper: create a minimal valid PartyPokemon."""
    return PartyPokemon(
        name=name,
        number=number,
        level=level,
        types=["Electric"],
        hp=35,
        max_hp=35,
        stats=StatsData(hp=35, attack=55, defense=30, special=50, speed=90),
        moves=[MoveSlot(name="THUNDER SHOCK", pp=30, max_pp=30)],
        experience=0,
        next_level_exp=1000,
    )


class TestStartNewGame:
    """Tests for GameState.start_new_game()."""

    def test_transitions_to_in_game(self):
        gs = GameState()
        gs.start_new_game()
        assert gs.in_game is True
        assert gs.in_menu is False

    def test_sets_starting_location(self):
        gs = GameState()
        gs.start_new_game()
        assert gs.current_location is not None
        assert gs.current_location.name == "Pallet Town"

    def test_initializes_empty_party(self):
        gs = GameState()
        gs.start_new_game()
        assert gs.game_data["pokemon"] == []

    def test_initializes_default_money(self):
        gs = GameState()
        gs.start_new_game()
        assert gs.game_data["money"] == 3000

    def test_initializes_empty_badges(self):
        gs = GameState()
        gs.start_new_game()
        assert gs.game_data["badges"] == []

    def test_initializes_empty_items(self):
        gs = GameState()
        gs.start_new_game()
        assert gs.game_data["items"] == {}

    def test_resets_autosave_counter(self):
        gs = GameState()
        gs.commands_since_autosave = 99
        gs.start_new_game()
        assert gs.commands_since_autosave == 0


class TestSaveAndLoadGame:
    """Tests for GameState.save_game() / load_game()."""

    def test_save_creates_file(self, tmp_path):
        gs = GameState()
        gs.start_new_game()
        gs.saves_dir = tmp_path
        save_path = gs.save_game("test_save")
        assert save_path.exists()

    def test_save_file_is_valid_json(self, tmp_path):
        gs = GameState()
        gs.start_new_game()
        gs.saves_dir = tmp_path
        save_path = gs.save_game("test_save")
        with open(save_path) as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_load_restores_location(self, tmp_path):
        gs = GameState()
        gs.start_new_game()
        gs.saves_dir = tmp_path
        save_path = gs.save_game("test_save")

        gs2 = GameState()
        gs2.saves_dir = tmp_path
        result = gs2.load_game(save_path)

        assert result is True
        assert gs2.current_location is not None
        assert gs2.current_location.name == "Pallet Town"

    def test_load_restores_in_game_state(self, tmp_path):
        gs = GameState()
        gs.start_new_game()
        gs.saves_dir = tmp_path
        save_path = gs.save_game("test_save")

        gs2 = GameState()
        gs2.load_game(save_path)

        assert gs2.in_game is True
        assert gs2.in_menu is False

    def test_load_missing_file_returns_false(self, tmp_path):
        gs = GameState()
        result = gs.load_game(tmp_path / "nonexistent.json")
        assert result is False

    def test_save_name_stored_in_game_data(self, tmp_path):
        gs = GameState()
        gs.start_new_game()
        gs.saves_dir = tmp_path
        gs.save_game("my_save")
        assert gs.game_data["save_name"] == "my_save"

    def test_save_and_load_preserves_money(self, tmp_path):
        gs = GameState()
        gs.start_new_game()
        gs.game_data["money"] = 9999
        gs.saves_dir = tmp_path
        save_path = gs.save_game("test")

        gs2 = GameState()
        gs2.saves_dir = tmp_path
        gs2.load_game(save_path)
        assert gs2.game_data["money"] == 9999

    def test_save_and_load_preserves_party(self, tmp_path):
        gs = GameState()
        gs.start_new_game()
        gs.game_data["pokemon"].append(make_pokemon())
        gs.saves_dir = tmp_path
        save_path = gs.save_game("test")

        gs2 = GameState()
        gs2.saves_dir = tmp_path
        gs2.load_game(save_path)
        assert len(gs2.game_data["pokemon"]) == 1
        p = gs2.game_data["pokemon"][0]
        assert isinstance(p, PartyPokemon)
        assert p.name == "PIKACHU"

    def test_save_and_load_preserves_pokemon_level(self, tmp_path):
        """Level must survive a full save → load round-trip."""
        gs = GameState()
        gs.start_new_game()
        squirtle = make_pokemon("SQUIRTLE", number=7, level=7)
        gs.game_data["pokemon"].append(squirtle)
        gs.saves_dir = tmp_path
        save_path = gs.save_game("test_level")

        gs2 = GameState()
        gs2.saves_dir = tmp_path
        gs2.load_game(save_path)
        p = gs2.game_data["pokemon"][0]
        assert p.level == 7, f"Expected level 7, got {p.level}"

    def test_save_and_load_preserves_squirtle_level_7(self, tmp_path):
        """Regression: SQUIRTLE at level 7 must be restored at level 7."""
        gs = GameState()
        gs.start_new_game()
        squirtle = make_pokemon("SQUIRTLE", number=7, level=7)
        gs.game_data["pokemon"].append(squirtle)
        gs.saves_dir = tmp_path
        save_path = gs.save_game("save_mark")

        gs2 = GameState()
        gs2.saves_dir = tmp_path
        gs2.load_game(save_path)
        assert len(gs2.game_data["pokemon"]) == 1
        p = gs2.game_data["pokemon"][0]
        assert p.name == "SQUIRTLE"
        assert p.level == 7

    def test_save_file_contains_correct_level_in_json(self, tmp_path):
        """The JSON on disk must store the correct level value."""
        gs = GameState()
        gs.start_new_game()
        gs.game_data["pokemon"].append(make_pokemon("SQUIRTLE", number=7, level=7))
        gs.saves_dir = tmp_path
        save_path = gs.save_game("check_json")

        with open(save_path) as f:
            data = json.load(f)
        assert data["pokemon"][0]["level"] == 7

    def test_save_and_load_preserves_hp_and_max_hp(self, tmp_path):
        """HP values must be preserved through a save/load cycle."""
        gs = GameState()
        gs.start_new_game()
        squirtle = make_pokemon("SQUIRTLE", number=7, level=7)
        gs.game_data["pokemon"].append(squirtle)
        gs.saves_dir = tmp_path
        save_path = gs.save_game("hp_test")

        gs2 = GameState()
        gs2.saves_dir = tmp_path
        gs2.load_game(save_path)
        p = gs2.game_data["pokemon"][0]
        assert p.hp == squirtle.hp
        assert p.max_hp == squirtle.max_hp

    def test_overwriting_save_updates_existing_file(self, tmp_path):
        """Saving twice to the same name must update the file, not create a second one."""
        gs = GameState()
        gs.start_new_game()
        gs.game_data["pokemon"].append(make_pokemon("SQUIRTLE", number=7, level=6))
        gs.saves_dir = tmp_path
        gs.save_game("save_mark")

        # Level up Squirtle and save again to the same slot
        gs.game_data["pokemon"][0].level = 7
        gs.save_game("save_mark")

        saves = gs.get_available_saves()
        assert len(saves) == 1, "Expected exactly one save file"

        gs2 = GameState()
        gs2.saves_dir = tmp_path
        gs2.load_game(saves[0])
        assert gs2.game_data["pokemon"][0].level == 7

    """Tests for GameState.get_available_saves()."""

    def test_no_saves_dir_returns_empty(self, tmp_path):
        gs = GameState()
        gs.saves_dir = tmp_path / "missing_dir"
        assert gs.get_available_saves() == []

    def test_returns_json_files(self, tmp_path):
        gs = GameState()
        gs.start_new_game()
        gs.saves_dir = tmp_path
        gs.save_game("save1")
        gs.save_game("save2")
        saves = gs.get_available_saves()
        assert len(saves) == 2
        assert all(s.suffix == ".json" for s in saves)

    def test_ignores_non_json_files(self, tmp_path):
        gs = GameState()
        gs.saves_dir = tmp_path
        (tmp_path / "note.txt").write_text("hello")
        saves = gs.get_available_saves()
        assert len(saves) == 0


class TestFindPokemon:
    """Tests for GameState.find_pokemon()."""

    def test_find_by_name(self, game_state):
        game_state.game_data["pokemon"].append(make_pokemon("PIKACHU", 25))
        p, idx = game_state.find_pokemon("PIKACHU")
        assert p is not None
        assert idx == 0

    def test_find_by_partial_name(self, game_state):
        game_state.game_data["pokemon"].append(make_pokemon("PIKACHU", 25))
        p, _idx = game_state.find_pokemon("pika")
        assert p is not None

    def test_find_by_slot_number(self, game_state):
        game_state.game_data["pokemon"].append(make_pokemon("PIKACHU", 25))
        game_state.game_data["pokemon"].append(make_pokemon("CHARMANDER", 4))
        p, idx = game_state.find_pokemon("2")
        assert p is not None
        assert p.name == "CHARMANDER"
        assert idx == 1

    def test_not_found_returns_none_and_minus_one(self, game_state):
        p, idx = game_state.find_pokemon("GHOSTMON")
        assert p is None
        assert idx == -1

    def test_find_case_insensitive(self, game_state):
        game_state.game_data["pokemon"].append(make_pokemon("PIKACHU", 25))
        p, _idx = game_state.find_pokemon("pikachu")
        assert p is not None

    def test_slot_out_of_range(self, game_state):
        game_state.game_data["pokemon"].append(make_pokemon("PIKACHU", 25))
        p, idx = game_state.find_pokemon("9")
        assert p is None
        assert idx == -1


class TestRouteProgress:
    """Tests for GameState.get_route_progress() / increment_route_progress()."""

    def test_initial_progress_is_zero(self, game_state):
        assert game_state.get_route_progress("Route 1") == 0

    def test_increment_increases_count(self, game_state):
        game_state.increment_route_progress("Route 1")
        assert game_state.get_route_progress("Route 1") == 1

    def test_multiple_increments(self, game_state):
        for _ in range(5):
            game_state.increment_route_progress("Route 1")
        assert game_state.get_route_progress("Route 1") == 5

    def test_different_routes_independent(self, game_state):
        game_state.increment_route_progress("Route 1")
        game_state.increment_route_progress("Route 1")
        game_state.increment_route_progress("Viridian Forest")
        assert game_state.get_route_progress("Route 1") == 2
        assert game_state.get_route_progress("Viridian Forest") == 1

    def test_increment_with_steps_two(self, game_state):
        game_state.increment_route_progress("Route 1", steps=2)
        assert game_state.get_route_progress("Route 1") == 2

    def test_increment_with_steps_default_is_one(self, game_state):
        game_state.increment_route_progress("Route 1")
        assert game_state.get_route_progress("Route 1") == 1

    def test_increment_steps_accumulates(self, game_state):
        game_state.increment_route_progress("Route 1", steps=2)
        game_state.increment_route_progress("Route 1", steps=1)
        assert game_state.get_route_progress("Route 1") == 3


class TestGetActivePokemon:
    """Tests for GameState.get_active_pokemon()."""

    def test_no_party_returns_none(self, game_state):
        result = game_state.get_active_pokemon()
        assert result is None

    def test_returns_first_alive_pokemon(self, game_state):
        p1 = make_pokemon("PIKACHU", 25, 10)
        game_state.game_data["pokemon"].append(p1)
        result = game_state.get_active_pokemon()
        assert result is p1

    def test_skips_fainted_pokemon(self, game_state):
        fainted = make_pokemon("PIKACHU", 25, 10)
        fainted.hp = 0
        alive = make_pokemon("CHARMANDER", 4, 5)
        game_state.game_data["pokemon"].extend([fainted, alive])
        result = game_state.get_active_pokemon()
        assert result is alive

    def test_all_fainted_returns_none(self, game_state):
        p = make_pokemon("PIKACHU", 25, 10)
        p.hp = 0
        game_state.game_data["pokemon"].append(p)
        result = game_state.get_active_pokemon()
        assert result is None


class TestAutosave:
    """Tests for GameState.autosave_on_location_change()."""

    def test_no_autosave_when_not_in_game(self, tmp_path):
        gs = GameState()
        gs.saves_dir = tmp_path
        gs.in_game = False
        result = gs.autosave_on_location_change()
        assert result is None

    def test_no_autosave_when_disabled(self, tmp_path):
        gs = GameState()
        gs.start_new_game()
        gs.saves_dir = tmp_path
        gs.autosave_enabled = False
        result = gs.autosave_on_location_change()
        assert result is None

    def test_autosave_creates_file(self, tmp_path):
        gs = GameState()
        gs.start_new_game()
        gs.game_data["save_name"] = "player"
        gs.saves_dir = tmp_path
        path = gs.autosave_on_location_change()
        assert path is not None
        assert path.exists()
        assert "_autosave" in path.stem

    def test_autosave_does_not_stack_suffix(self, tmp_path):
        gs = GameState()
        gs.start_new_game()
        gs.game_data["save_name"] = "player_autosave"
        gs.saves_dir = tmp_path
        path = gs.autosave_on_location_change()
        assert path is not None
        # Should not be "player_autosave_autosave.json"
        assert path.stem == "player_autosave"
