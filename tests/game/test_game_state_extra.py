"""
Extended tests for PokemonLibrary/game_state.py and PokemonLibrary/models.py.

Covers the branches not yet reached by test_game_state.py and test_models.py.
"""

import json

import pytest

from pytemon.data.move_data import MoveSlot
from pytemon.data.pokemon_data import StatsData
from pytemon.game_state import GameState
from pytemon.models import PartyPokemon


def make_party_pokemon(
    name: str = "PIKACHU",
    number: int = 25,
    level: int = 10,
    hp: int = 35,
    max_hp: int = 35,
) -> PartyPokemon:
    return PartyPokemon(
        name=name,
        number=number,
        level=level,
        types=["Electric"],
        hp=hp,
        max_hp=max_hp,
        stats=StatsData(hp=max_hp, attack=55, defense=30, special=50, speed=90),
        moves=[MoveSlot(name="TACKLE", pp=35, max_pp=35)],
        experience=0,
        next_level_exp=1000,
    )


@pytest.fixture
def gs() -> GameState:
    gs = GameState()
    gs.start_new_game()
    return gs


# ===========================================================================
# GameState - get_active_pokemon
# ===========================================================================


class TestGetActivePokemon:
    def test_returns_first_healthy_pokemon(self, gs):
        p = make_party_pokemon(hp=35, max_hp=35)
        gs.game_data["pokemon"] = [p]
        result = gs.get_active_pokemon()
        assert result is p

    def test_returns_none_when_all_fainted(self, gs):
        p = make_party_pokemon(hp=0, max_hp=35)
        gs.game_data["pokemon"] = [p]
        result = gs.get_active_pokemon()
        assert result is None

    def test_skips_fainted_pokemon(self, gs):
        fainted = make_party_pokemon(name="FAINTED", hp=0, max_hp=35)
        healthy = make_party_pokemon(name="HEALTHY", hp=35, max_hp=35)
        gs.game_data["pokemon"] = [fainted, healthy]
        result = gs.get_active_pokemon()
        assert result is healthy

    def test_empty_party_returns_none(self, gs):
        gs.game_data["pokemon"] = []
        assert gs.get_active_pokemon() is None

    def test_works_with_plain_dict_pokemon(self, gs):
        """backward-compat: plain dicts in party."""
        p = {
            "name": "RATTATA",
            "hp": 20,
            "max_hp": 20,
            "level": 3,
            "types": ["Normal"],
            "stats": {"hp": 20, "attack": 56, "defense": 35, "special": 25, "speed": 72},
            "moves": [{"name": "TACKLE", "pp": 35, "max_pp": 35}],
        }
        gs.game_data["pokemon"] = [p]
        result = gs.get_active_pokemon()
        assert result is not None


# ===========================================================================
# GameState - find_pokemon
# ===========================================================================


class TestFindPokemon:
    def test_find_by_name_exact(self, gs):
        p = make_party_pokemon(name="PIKACHU")
        gs.game_data["pokemon"] = [p]
        found, idx = gs.find_pokemon("pikachu")
        assert found is p
        assert idx == 0

    def test_find_by_partial_name(self, gs):
        p = make_party_pokemon(name="CHARMANDER")
        gs.game_data["pokemon"] = [p]
        found, _ = gs.find_pokemon("charm")
        assert found is p

    def test_find_by_slot_number(self, gs):
        p1 = make_party_pokemon(name="BULBASAUR", number=1)
        p2 = make_party_pokemon(name="CHARMANDER", number=4)
        gs.game_data["pokemon"] = [p1, p2]
        found, idx = gs.find_pokemon("2")
        assert found is p2
        assert idx == 1

    def test_not_found_returns_none_and_minus_one(self, gs):
        gs.game_data["pokemon"] = []
        found, idx = gs.find_pokemon("MEWTWO")
        assert found is None
        assert idx == -1

    def test_out_of_range_slot_falls_back_to_name_search(self, gs):
        p = make_party_pokemon(name="PIKACHU")
        gs.game_data["pokemon"] = [p]
        found, _ = gs.find_pokemon("99")
        assert found is None


# ===========================================================================
# GameState - route_progress
# ===========================================================================


class TestRouteProgress:
    def test_initial_route_progress_is_zero(self, gs):
        assert gs.get_route_progress("Route 1") == 0

    def test_increment_returns_new_count(self, gs):
        count = gs.increment_route_progress("Route 1")
        assert count == 1

    def test_multiple_increments(self, gs):
        gs.increment_route_progress("Route 1")
        gs.increment_route_progress("Route 1")
        assert gs.get_route_progress("Route 1") == 2

    def test_different_routes_are_independent(self, gs):
        gs.increment_route_progress("Route 1")
        assert gs.get_route_progress("Route 2") == 0


# ===========================================================================
# GameState - autosave
# ===========================================================================


class TestAutosave:
    def test_autosave_skipped_when_not_in_game(self, gs, tmp_path):
        gs.saves_dir = tmp_path
        gs.in_game = False
        result = gs.autosave_on_location_change()
        assert result is None

    def test_autosave_skipped_when_disabled(self, gs, tmp_path):
        gs.saves_dir = tmp_path
        gs.in_game = True
        gs.autosave_enabled = False
        result = gs.autosave_on_location_change()
        assert result is None

    def test_autosave_creates_file(self, gs, tmp_path):
        gs.saves_dir = tmp_path
        gs.in_game = True
        gs.autosave_enabled = True
        gs.game_data["save_name"] = "testplayer"
        path = gs.autosave_on_location_change()
        assert path is not None
        assert path.exists()
        # Must be in the autosaves subdirectory, not the root saves dir
        assert path.parent == tmp_path / "autosaves"

    def test_autosave_file_contains_json(self, gs, tmp_path):
        gs.saves_dir = tmp_path
        gs.in_game = True
        gs.autosave_enabled = True
        gs.game_data["save_name"] = "testplayer"
        path = gs.autosave_on_location_change()
        data = json.loads(path.read_text())
        assert "save_name" in data

    def test_autosave_strips_existing_autosave_suffix(self, gs, tmp_path):
        gs.saves_dir = tmp_path
        gs.in_game = True
        gs.autosave_enabled = True
        gs.game_data["save_name"] = "player_autosave"
        path = gs.autosave_on_location_change()
        assert path is not None
        # Should produce player_autosave.json, not player_autosave_autosave.json
        assert "_autosave_autosave" not in path.name

    def test_get_available_autosaves_returns_autosave_files(self, gs, tmp_path):
        gs.saves_dir = tmp_path
        gs.in_game = True
        gs.autosave_enabled = True
        gs.game_data["save_name"] = "ash"
        path = gs.autosave_on_location_change()
        autosaves = gs.get_available_autosaves()
        assert path in autosaves

    def test_get_available_saves_excludes_autosave_files(self, gs, tmp_path):
        gs.saves_dir = tmp_path
        gs.in_game = True
        gs.autosave_enabled = True
        gs.game_data["save_name"] = "ash"
        # Write a regular save in saves_dir root
        regular = tmp_path / "ash.json"
        regular.write_text('{"save_name": "ash"}')
        # Trigger an autosave (goes to autosaves subfolder)
        gs.autosave_on_location_change()
        saves = gs.get_available_saves()
        names = [p.name for p in saves]
        assert "ash.json" in names
        assert "ash_autosave.json" not in names

    def test_get_available_autosaves_empty_when_dir_missing(self, gs, tmp_path):
        gs.saves_dir = tmp_path / "nonexistent"
        autosaves = gs.get_available_autosaves()
        assert autosaves == []


# ===========================================================================
# GameState - backward-compat load (missing fields in save)
# ===========================================================================


class TestLoadBackwardCompat:
    def test_load_save_without_badges_creates_empty_list(self, tmp_path):
        # Simulate old save with badges=0 (int, not list)
        save_data = {
            "player_name": "Ash",
            "location": "Pallet Town",
            "in_game": True,
            "pokemon": [],
            "badges": 0,  # old format
        }
        save_file = tmp_path / "test_save.json"
        save_file.write_text(json.dumps(save_data))

        new_gs = GameState()
        new_gs.saves_dir = tmp_path
        result = new_gs.load_game(save_file)
        assert result is True
        assert isinstance(new_gs.game_data.get("badges"), list)

    def test_load_save_without_pc_storage_creates_empty_dict(self, tmp_path):
        save_data = {
            "player_name": "Ash",
            "location": "Pallet Town",
            "in_game": True,
            "pokemon": [],
        }
        save_file = tmp_path / "no_pc_save.json"
        save_file.write_text(json.dumps(save_data))

        new_gs = GameState()
        new_gs.saves_dir = tmp_path
        result = new_gs.load_game(save_file)
        assert result is True
        assert "pc_storage" in new_gs.game_data


# ===========================================================================
# GameState - _serialize_pokemon
# ===========================================================================


class TestSerializePokemon:
    def test_serialize_none_returns_none(self):
        result = GameState._serialize_pokemon(None)
        assert result is None

    def test_serialize_party_pokemon(self):
        p = make_party_pokemon()
        result = GameState._serialize_pokemon(p)
        assert isinstance(result, dict)
        assert result["name"] == "PIKACHU"

    def test_serialize_plain_dict(self):
        d = {
            "name": "RATTATA",
            "number": 19,
            "level": 3,
            "types": ["Normal"],
            "hp": 20,
            "max_hp": 20,
            "stats": {"hp": 20, "attack": 56, "defense": 35, "special": 25, "speed": 72},
            "moves": [{"name": "TACKLE", "pp": 35, "max_pp": 35}],
            "experience": 0,
            "next_level_exp": 50,
        }
        result = GameState._serialize_pokemon(d)
        assert isinstance(result, dict)
        assert result["name"] == "RATTATA"


# ===========================================================================
# PartyPokemon - extended model tests
# ===========================================================================


class TestPartyPokemonModel:
    def test_contains_checks_attribute(self):
        p = make_party_pokemon()
        assert "name" in p
        assert "hp" in p

    def test_contains_missing_attribute_returns_false(self):
        p = make_party_pokemon()
        assert "nonexistent_attr" not in p

    def test_from_dict_with_moveslot_objects(self):
        """from_dict should handle existing MoveSlot objects."""
        d = {
            "name": "PIKACHU",
            "number": 25,
            "level": 10,
            "types": ["Electric"],
            "hp": 35,
            "max_hp": 35,
            "stats": {"hp": 35, "attack": 55, "defense": 30, "special": 50, "speed": 90},
            "moves": [MoveSlot(name="TACKLE", pp=35, max_pp=35)],
            "experience": 0,
            "next_level_exp": 1000,
        }
        p = PartyPokemon.from_dict(d)
        assert p.name == "PIKACHU"
        assert len(p.moves) == 1

    def test_from_dict_with_statsdata_object(self):
        """from_dict should handle existing StatsData objects."""
        d = {
            "name": "CHARMANDER",
            "number": 4,
            "level": 5,
            "types": ["Fire"],
            "hp": 39,
            "max_hp": 39,
            "stats": StatsData(hp=39, attack=52, defense=43, special=50, speed=65),
            "moves": [],
            "experience": 0,
            "next_level_exp": 125,
        }
        p = PartyPokemon.from_dict(d)
        assert p.stats.attack == 52

    def test_from_dict_with_raw_move_string(self):
        """from_dict should handle moves that are plain strings."""
        d = {
            "name": "BULBASAUR",
            "number": 1,
            "level": 5,
            "types": ["Grass"],
            "hp": 45,
            "max_hp": 45,
            "stats": {"hp": 45, "attack": 49, "defense": 49, "special": 65, "speed": 45},
            "moves": ["TACKLE"],  # plain string, not dict or MoveSlot
            "experience": 0,
            "next_level_exp": 125,
        }
        p = PartyPokemon.from_dict(d)
        assert len(p.moves) == 1
        assert p.moves[0].name == "TACKLE"

    def test_to_dict_round_trip(self):
        p = make_party_pokemon()
        d = p.to_dict()
        p2 = PartyPokemon.from_dict(d)
        assert p2.name == p.name
        assert p2.hp == p.hp
        assert p2.level == p.level
