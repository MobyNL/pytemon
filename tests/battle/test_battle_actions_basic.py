"""
Tests for PokemonLibrary/battle/battle_actions.py - the functions that are
unit-testable without a running Textual terminal.
"""

from pytemon.battle.battle_actions import (
    ensure_battle_ready,
    parse_move_choice,
)
from pytemon.data.move_data import MoveSlot
from pytemon.data.pokemon_data import StatsData
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
        moves=[
            MoveSlot(name="TACKLE", pp=35, max_pp=35),
            MoveSlot(name="GROWL", pp=40, max_pp=40),
        ],
        experience=0,
        next_level_exp=1000,
    )


# ===========================================================================
# ensure_battle_ready
# ===========================================================================


class TestEnsureBattleReady:
    def test_already_battle_ready_is_a_no_op(self):
        p = make_party_pokemon()
        # Record a reference to the original stats to confirm nothing changes
        original_hp = p.hp
        ensure_battle_ready(p)
        assert p.hp == original_hp

    def test_minimal_dict_gets_all_stats(self):
        # Plain dict that only has a name and level (old save format)
        p = {"name": "CHARMANDER", "level": 5}
        ensure_battle_ready(p)
        assert "hp" in p
        assert "max_hp" in p
        assert "stats" in p
        assert "moves" in p
        assert "next_level_exp" in p
        assert "status" in p

    def test_stats_not_overwritten_when_present(self):
        p = {"name": "CHARMANDER", "level": 5, "hp": 99, "max_hp": 99, "stats": {"attack": 99}}
        # hp is present but stats/moves/next_level_exp are not, so it triggers migration
        ensure_battle_ready(p)
        # hp was present so setdefault should leave it unchanged
        assert p["hp"] == 99

    def test_unknown_pokemon_uses_fallback(self):
        p = {"name": "COMPLETELYFAKEMON", "level": 5}
        ensure_battle_ready(p)
        # Should not raise and should have defaults
        assert "hp" in p
        assert "moves" in p


# ===========================================================================
# parse_move_choice
# ===========================================================================


class TestParseMoveChoice:
    def test_number_selects_correct_move(self):
        p = make_party_pokemon()
        result = parse_move_choice("1", p)
        assert result is not None
        assert result["name"] == "TACKLE"

    def test_number_selects_second_move(self):
        p = make_party_pokemon()
        result = parse_move_choice("2", p)
        assert result is not None
        assert result["name"] == "GROWL"

    def test_number_out_of_range_returns_none(self):
        p = make_party_pokemon()
        result = parse_move_choice("9", p)
        assert result is None

    def test_name_matches_exactly(self):
        p = make_party_pokemon()
        result = parse_move_choice("TACKLE", p)
        assert result is not None
        assert result["name"] == "TACKLE"

    def test_name_case_insensitive(self):
        p = make_party_pokemon()
        result = parse_move_choice("tackle", p)
        assert result is not None

    def test_partial_name_match(self):
        p = make_party_pokemon()
        result = parse_move_choice("tack", p)
        assert result is not None

    def test_use_prefix_stripped(self):
        p = make_party_pokemon()
        result = parse_move_choice("use tackle", p)
        assert result is not None
        assert result["name"] == "TACKLE"

    def test_nonexistent_move_returns_none(self):
        p = make_party_pokemon()
        result = parse_move_choice("FLAMETHROWER", p)
        assert result is None

    def test_empty_string_matches_first_move_due_to_partial_match(self):
        # Empty string is contained in every string, so it matches the first move
        p = make_party_pokemon()
        result = parse_move_choice("", p)
        # Empty string matches the first move because "" in "TACKLE" is True
        assert result is not None
        assert result["name"] == "TACKLE"
