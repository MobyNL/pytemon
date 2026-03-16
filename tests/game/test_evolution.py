"""
Unit tests for PokemonLibrary/evolution.py.
"""

from pytemon.data.move_data import MoveSlot
from pytemon.data.pokemon_data import StatsData
from pytemon.evolution import get_level_evolution, get_stone_evolution
from pytemon.models import PartyPokemon


def make_pokemon(number: int, level: int, **overrides) -> PartyPokemon:
    """Helper: create a minimal PartyPokemon for evolution testing."""
    defaults = {
        "name": "TEST",
        "number": number,
        "level": level,
        "types": ["Normal"],
        "hp": 45,
        "max_hp": 45,
        "stats": StatsData(hp=45, attack=49, defense=49, special=65, speed=45),
        "moves": [MoveSlot(name="TACKLE", pp=35, max_pp=35)],
        "experience": 0,
        "next_level_exp": 125,
    }
    defaults.update(overrides)
    return PartyPokemon(**defaults)


class TestGetLevelEvolution:
    """Tests for get_level_evolution()."""

    # Bulbasaur (#1) evolves at level 16 into IVYSAUR
    def test_ready_to_evolve_returns_name(self):
        p = make_pokemon(number=1, level=16, name="BULBASAUR")
        result = get_level_evolution(p)
        assert result == "IVYSAUR"

    def test_above_evo_level_also_returns_name(self):
        p = make_pokemon(number=1, level=20, name="BULBASAUR")
        result = get_level_evolution(p)
        assert result == "IVYSAUR"

    def test_below_evo_level_returns_none(self):
        p = make_pokemon(number=1, level=15, name="BULBASAUR")
        result = get_level_evolution(p)
        assert result is None

    def test_no_evolve_flag_blocks_evolution(self):
        p = make_pokemon(number=1, level=16, name="BULBASAUR", no_evolve=True)
        result = get_level_evolution(p)
        assert result is None

    def test_pokemon_without_evolution_returns_none(self):
        # Raichu (#26) has no further evolution
        p = make_pokemon(number=26, level=100, name="RAICHU")
        result = get_level_evolution(p)
        assert result is None

    def test_unknown_pokemon_number_returns_none(self):
        p = make_pokemon(number=9999, level=50, name="FAKE")
        result = get_level_evolution(p)
        assert result is None

    def test_pikachu_has_stone_evolution_not_level(self):
        # Pikachu (#25) evolves via Thunder Stone, not by level
        p = make_pokemon(number=25, level=100, name="PIKACHU")
        result = get_level_evolution(p)
        assert result is None

    def test_eevee_has_multi_branch_stone_evolution(self):
        # Eevee (#133) has multi-branch stone evolutions (list), so level evo = None
        p = make_pokemon(number=133, level=100, name="EEVEE")
        result = get_level_evolution(p)
        assert result is None


class TestGetStoneEvolution:
    """Tests for get_stone_evolution()."""

    # Pikachu (#25) evolves with THUNDER STONE into RAICHU
    def test_correct_stone_returns_evolution(self):
        p = make_pokemon(number=25, level=10, name="PIKACHU")
        result = get_stone_evolution(p, "THUNDER STONE")
        assert result == "RAICHU"

    def test_case_insensitive_item_name(self):
        p = make_pokemon(number=25, level=10, name="PIKACHU")
        result = get_stone_evolution(p, "thunder stone")
        assert result == "RAICHU"

    def test_wrong_stone_returns_none(self):
        p = make_pokemon(number=25, level=10, name="PIKACHU")
        result = get_stone_evolution(p, "FIRE STONE")
        assert result is None

    def test_no_evolve_flag_blocks_stone_evolution(self):
        p = make_pokemon(number=25, level=10, name="PIKACHU", no_evolve=True)
        result = get_stone_evolution(p, "THUNDER STONE")
        assert result is None

    def test_pokemon_without_evolution_returns_none(self):
        # Bulbasaur (#1) has level evolution, not stone
        p = make_pokemon(number=1, level=5, name="BULBASAUR")
        result = get_stone_evolution(p, "FIRE STONE")
        assert result is None

    def test_eevee_water_stone_returns_vaporeon(self):
        # Eevee (#133) multi-branch evolution
        p = make_pokemon(number=133, level=10, name="EEVEE")
        result = get_stone_evolution(p, "WATER STONE")
        assert result == "VAPOREON"

    def test_eevee_fire_stone_returns_flareon(self):
        p = make_pokemon(number=133, level=10, name="EEVEE")
        result = get_stone_evolution(p, "FIRE STONE")
        assert result == "FLAREON"

    def test_eevee_thunder_stone_returns_jolteon(self):
        p = make_pokemon(number=133, level=10, name="EEVEE")
        result = get_stone_evolution(p, "THUNDER STONE")
        assert result == "JOLTEON"

    def test_eevee_wrong_stone_returns_none(self):
        p = make_pokemon(number=133, level=10, name="EEVEE")
        result = get_stone_evolution(p, "LEAF STONE")
        assert result is None

    def test_unknown_number_returns_none(self):
        p = make_pokemon(number=9999, level=10, name="FAKE")
        result = get_stone_evolution(p, "FIRE STONE")
        assert result is None
