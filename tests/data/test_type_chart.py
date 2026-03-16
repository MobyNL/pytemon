"""
Unit tests for PokemonLibrary/data/type_chart.py.
"""

import pytest

from pytemon.data.pokemon_data import (
    BUG,
    DRAGON,
    ELECTRIC,
    FIGHTING,
    FIRE,
    FLYING,
    GHOST,
    GRASS,
    GROUND,
    ICE,
    NORMAL,
    POISON,
    PSYCHIC,
    ROCK,
    WATER,
)
from pytemon.data.type_chart import TYPE_CHART, get_type_effectiveness


class TestGetTypeEffectiveness:
    """Tests for get_type_effectiveness()."""

    def test_neutral_matchup_returns_one(self):
        assert get_type_effectiveness(NORMAL, [NORMAL]) == 1.0

    def test_super_effective_returns_two(self):
        assert get_type_effectiveness(FIRE, [GRASS]) == 2.0

    def test_not_very_effective_returns_half(self):
        assert get_type_effectiveness(FIRE, [WATER]) == 0.5

    def test_immune_returns_zero(self):
        assert get_type_effectiveness(NORMAL, [GHOST]) == 0.0

    def test_dual_type_super_effective_squared(self):
        # Fire vs. Grass/Ice should be 2.0 * 2.0 = 4.0
        result = get_type_effectiveness(FIRE, [GRASS, ICE])
        assert result == pytest.approx(4.0)

    def test_dual_type_one_neutral_one_super(self):
        # Water vs. Fire/Normal: 2.0 * 1.0 = 2.0
        result = get_type_effectiveness(WATER, [FIRE, NORMAL])
        assert result == pytest.approx(2.0)

    def test_dual_type_cancel_out(self):
        # Fire vs. Water/Grass: 0.5 * 2.0 = 1.0
        result = get_type_effectiveness(FIRE, [WATER, GRASS])
        assert result == pytest.approx(1.0)

    def test_dual_type_immune_overrides(self):
        # Normal vs. Ghost/Normal: 0.0 * 1.0 = 0.0
        result = get_type_effectiveness(NORMAL, [GHOST, NORMAL])
        assert result == pytest.approx(0.0)

    def test_electric_vs_ground_immune(self):
        assert get_type_effectiveness(ELECTRIC, [GROUND]) == 0.0

    def test_electric_vs_flying_super_effective(self):
        assert get_type_effectiveness(ELECTRIC, [FLYING]) == 2.0

    def test_unknown_attack_type_neutral(self):
        # A type not in TYPE_CHART should default to 1.0
        result = get_type_effectiveness("???", [FIRE])
        assert result == 1.0

    def test_empty_defender_types(self):
        # Edge case: no defender types → neutral
        result = get_type_effectiveness(FIRE, [])
        assert result == 1.0

    def test_psychic_vs_psychic_half(self):
        assert get_type_effectiveness(PSYCHIC, [PSYCHIC]) == 0.5

    def test_ghost_vs_psychic_no_effect_gen1(self):
        # Gen 1 bug: Ghost has 0 effect on Psychic
        assert get_type_effectiveness(GHOST, [PSYCHIC]) == 0.0

    def test_fighting_vs_normal_super_effective(self):
        assert get_type_effectiveness(FIGHTING, [NORMAL]) == 2.0

    def test_type_chart_contains_all_types(self):
        """TYPE_CHART should have entries for all Gen 1 types."""
        expected = {
            NORMAL,
            FIRE,
            WATER,
            GRASS,
            ELECTRIC,
            ICE,
            FIGHTING,
            POISON,
            GROUND,
            FLYING,
            PSYCHIC,
            BUG,
            ROCK,
            GHOST,
            DRAGON,
        }
        assert set(TYPE_CHART.keys()) == expected
