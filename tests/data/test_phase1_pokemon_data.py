"""
Phase 1 Pokemon data tests.

Covers:
- Full SpeciesData for Machop/Machoke/Machamp
- Full SpeciesData for Gastly/Haunter/Gengar
- Link Cable evolution for trade-evolvers
- Link Cable item in ITEM_DATA
"""

from pytemon.data.pokemon_data import (
    FIGHTING,
    GHOST,
    POISON,
    POKEMON,
    ItemEvolution,
    LevelEvolution,
)
from pytemon.items import ITEM_DATA

# ---------------------------------------------------------------------------
# Machop family
# ---------------------------------------------------------------------------


class TestMachopFamily:
    """Tests for Machop, Machoke, Machamp full SpeciesData."""

    def test_machop_has_full_data(self):
        """Machop (#66) should have real SpeciesData, not a stub."""
        assert 66 in POKEMON
        m = POKEMON[66]
        assert m.name == "MACHOP"
        assert m.types == [FIGHTING]
        # Real stats differ from stub (50/50/50/50/50)
        stats = m.stats
        assert not (
            stats.hp == 50
            and stats.attack == 50
            and stats.defense == 50
            and stats.special == 50
            and stats.speed == 50
        ), "Machop should have real stats, not stub values"

    def test_machop_learnset_non_empty(self):
        """Machop should have a proper learnset."""
        m = POKEMON[66]
        assert len(m.learnset) > 0

    def test_machop_evolves_to_machoke(self):
        """Machop should evolve to Machoke at level 28 via level-up."""
        m = POKEMON[66]
        assert m.evolution is not None
        assert isinstance(m.evolution, LevelEvolution)
        assert m.evolution.into_species == "MACHOKE"
        assert m.evolution.level == 28

    def test_machoke_has_full_data(self):
        """Machoke (#67) should have real SpeciesData."""
        assert 67 in POKEMON
        m = POKEMON[67]
        assert m.name == "MACHOKE"
        assert m.types == [FIGHTING]

    def test_machoke_evolves_via_link_cable(self):
        """Machoke should evolve to Machamp via Link Cable (not level-up)."""
        m = POKEMON[67]
        assert m.evolution is not None
        assert isinstance(m.evolution, ItemEvolution)
        assert m.evolution.item.upper() == "LINK CABLE"
        assert m.evolution.into_species == "MACHAMP"

    def test_machamp_has_full_data(self):
        """Machamp (#68) should have real SpeciesData."""
        assert 68 in POKEMON
        m = POKEMON[68]
        assert m.name == "MACHAMP"
        assert m.types == [FIGHTING]
        assert m.evolution is None


# ---------------------------------------------------------------------------
# Gastly family
# ---------------------------------------------------------------------------


class TestGastlyFamily:
    """Tests for Gastly, Haunter, Gengar full SpeciesData."""

    def test_gastly_has_full_data(self):
        """Gastly (#92) should have real SpeciesData."""
        assert 92 in POKEMON
        g = POKEMON[92]
        assert g.name == "GASTLY"
        assert GHOST in g.types
        assert POISON in g.types

    def test_gastly_learnset_non_empty(self):
        """Gastly should have a proper learnset."""
        g = POKEMON[92]
        assert len(g.learnset) > 0

    def test_gastly_evolves_to_haunter(self):
        """Gastly should evolve to Haunter at level 25."""
        g = POKEMON[92]
        assert g.evolution is not None
        assert isinstance(g.evolution, LevelEvolution)
        assert g.evolution.into_species == "HAUNTER"
        assert g.evolution.level == 25

    def test_haunter_has_full_data(self):
        """Haunter (#93) should have real SpeciesData."""
        assert 93 in POKEMON
        h = POKEMON[93]
        assert h.name == "HAUNTER"
        assert GHOST in h.types

    def test_haunter_evolves_via_link_cable(self):
        """Haunter should evolve to Gengar via Link Cable (trade-evolver)."""
        h = POKEMON[93]
        assert h.evolution is not None
        assert isinstance(h.evolution, ItemEvolution)
        assert h.evolution.item.upper() == "LINK CABLE"
        assert h.evolution.into_species == "GENGAR"

    def test_gengar_has_full_data(self):
        """Gengar (#94) should have real SpeciesData."""
        assert 94 in POKEMON
        g = POKEMON[94]
        assert g.name == "GENGAR"
        assert GHOST in g.types
        assert g.evolution is None


# ---------------------------------------------------------------------------
# Graveler -> Golem (Link Cable)
# ---------------------------------------------------------------------------


class TestGravelerLinkCable:
    """Graveler should evolve via Link Cable, not by level."""

    def test_graveler_evolves_via_link_cable(self):
        """Graveler (#75) should evolve to Golem via Link Cable."""
        g = POKEMON[75]
        assert g.evolution is not None
        assert isinstance(g.evolution, ItemEvolution)
        assert g.evolution.item.upper() == "LINK CABLE"
        assert g.evolution.into_species == "GOLEM"


# ---------------------------------------------------------------------------
# Link Cable item
# ---------------------------------------------------------------------------


class TestLinkCableItem:
    """Tests for the Link Cable item."""

    def test_link_cable_in_item_data(self):
        """Link Cable should be in ITEM_DATA."""
        assert "Link Cable" in ITEM_DATA

    def test_link_cable_is_stone_category(self):
        """Link Cable should have category 'stone' for evolution use."""
        from pytemon.items import CAT_STONE

        item = ITEM_DATA["Link Cable"]
        assert item.cat == CAT_STONE

    def test_link_cable_has_description(self):
        """Link Cable should have a non-empty description."""
        item = ITEM_DATA["Link Cable"]
        assert len(item.desc) > 0

    def test_link_cable_use_on_machoke(self):
        """Using Link Cable on Machoke should trigger evolution."""
        from pytemon.data.pokemon_data import StatsData
        from pytemon.evolution import get_stone_evolution
        from pytemon.models import PartyPokemon

        machoke = PartyPokemon(
            name="MACHOKE",
            number=67,
            level=30,
            types=["Fighting"],
            hp=80,
            max_hp=80,
            stats=StatsData(hp=80, attack=100, defense=70, special=50, speed=45),
            moves=[],
            catch_rate=90,
            base_exp=146,
            experience=0,
            next_level_exp=1000,
        )
        target = get_stone_evolution(machoke, "Link Cable")
        assert target == "MACHAMP"

    def test_link_cable_use_on_haunter(self):
        """Using Link Cable on Haunter should trigger evolution."""
        from pytemon.data.pokemon_data import StatsData
        from pytemon.evolution import get_stone_evolution
        from pytemon.models import PartyPokemon

        haunter = PartyPokemon(
            name="HAUNTER",
            number=93,
            level=28,
            types=["Ghost", "Poison"],
            hp=45,
            max_hp=45,
            stats=StatsData(hp=45, attack=50, defense=45, special=115, speed=95),
            moves=[],
            catch_rate=90,
            base_exp=126,
            experience=0,
            next_level_exp=1000,
        )
        target = get_stone_evolution(haunter, "Link Cable")
        assert target == "GENGAR"

    def test_link_cable_no_effect_on_pikachu(self):
        """Using Link Cable on Pikachu (non-trade-evolver) should return None."""
        from pytemon.data.pokemon_data import StatsData
        from pytemon.evolution import get_stone_evolution
        from pytemon.models import PartyPokemon

        pikachu = PartyPokemon(
            name="PIKACHU",
            number=25,
            level=10,
            types=["Electric"],
            hp=35,
            max_hp=35,
            stats=StatsData(hp=35, attack=55, defense=30, special=50, speed=90),
            moves=[],
            catch_rate=190,
            base_exp=82,
            experience=0,
            next_level_exp=1000,
        )
        target = get_stone_evolution(pikachu, "Link Cable")
        assert target is None
