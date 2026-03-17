"""
Phase 1 Pokemon data tests.

Covers:
- Full SpeciesData for Machop/Machoke/Machamp
- Full SpeciesData for Gastly/Haunter/Gengar
- Level-based evolution for formerly-trade-only evolvers
"""

from pytemon.data.pokemon_data import (
    FIGHTING,
    GHOST,
    POISON,
    POKEMON,
    LevelEvolution,
)

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

    def test_machoke_evolves_to_machamp_by_level(self):
        """Machoke should evolve to Machamp by levelling up (no trade required)."""
        m = POKEMON[67]
        assert m.evolution is not None
        assert isinstance(m.evolution, LevelEvolution)
        assert m.evolution.into_species == "MACHAMP"
        assert m.evolution.level > 0

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

    def test_haunter_evolves_to_gengar_by_level(self):
        """Haunter should evolve to Gengar by levelling up (no trade required)."""
        h = POKEMON[93]
        assert h.evolution is not None
        assert isinstance(h.evolution, LevelEvolution)
        assert h.evolution.into_species == "GENGAR"
        assert h.evolution.level > 0

    def test_gengar_has_full_data(self):
        """Gengar (#94) should have real SpeciesData."""
        assert 94 in POKEMON
        g = POKEMON[94]
        assert g.name == "GENGAR"
        assert GHOST in g.types
        assert g.evolution is None


# ---------------------------------------------------------------------------
# Trade-evolvers restored to level-based evolution
# ---------------------------------------------------------------------------


class TestTradeEvolversUseLevel:
    """Graveler and Kadabra should use level-based evolutions (no trade)."""

    def test_graveler_evolves_to_golem_by_level(self):
        """Graveler (#75) should evolve to Golem via level-up."""
        g = POKEMON[75]
        assert g.evolution is not None
        assert isinstance(g.evolution, LevelEvolution)
        assert g.evolution.into_species == "GOLEM"
        assert g.evolution.level > 0

    def test_kadabra_evolves_to_alakazam_by_level(self):
        """Kadabra (#64) should evolve to Alakazam via level-up."""
        k = POKEMON[64]
        assert k.evolution is not None
        assert isinstance(k.evolution, LevelEvolution)
        assert k.evolution.into_species == "ALAKAZAM"
        assert k.evolution.level > 0
