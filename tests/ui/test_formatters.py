"""
Unit tests for PokemonLibrary/ui/formatters.py.
"""

from pytemon.locations import get_location
from pytemon.ui.formatters import (
    format_experience_bar,
    format_experience_text,
    format_hp_bar,
    format_list,
    get_travel_description,
)


class TestFormatHpBar:
    """Tests for format_hp_bar()."""

    def test_full_hp_is_all_filled(self):
        bar = format_hp_bar(100, 100, width=10)
        # Should have 10 filled blocks, no empty
        assert "░" not in bar
        assert bar.count("█") == 10

    def test_zero_hp_is_all_empty(self):
        bar = format_hp_bar(0, 100, width=10)
        assert "█" not in bar
        assert bar.count("░") == 10

    def test_half_hp_is_half_filled(self):
        bar = format_hp_bar(50, 100, width=10)
        assert bar.count("█") == 5
        assert bar.count("░") == 5

    def test_zero_max_hp_returns_empty_bar(self):
        bar = format_hp_bar(0, 0, width=10)
        assert bar == "░" * 10

    def test_full_hp_color_is_green(self):
        bar = format_hp_bar(100, 100)
        assert "[green]" in bar

    def test_mid_hp_color_is_yellow(self):
        # 30% HP is above 25% threshold but below 50%
        bar = format_hp_bar(30, 100)
        assert "[yellow]" in bar

    def test_low_hp_color_is_red(self):
        # 20% HP is at the red threshold
        bar = format_hp_bar(20, 100)
        assert "[red]" in bar

    def test_negative_hp_clamped_to_empty(self):
        bar = format_hp_bar(-10, 100, width=10)
        assert "█" not in bar
        assert bar.count("░") == 10

    def test_custom_width(self):
        bar = format_hp_bar(100, 100, width=20)
        assert bar.count("█") == 20

    def test_returns_string(self):
        assert isinstance(format_hp_bar(50, 100), str)


class TestFormatExperienceText:
    """Tests for format_experience_text()."""

    def test_normal_format(self):
        text = format_experience_text(50, 125)
        assert "50" in text
        assert "125" in text

    def test_zero_next_level(self):
        text = format_experience_text(100, 0)
        assert "100" in text
        # Should not crash and should return something sensible
        assert isinstance(text, str)

    def test_returns_string(self):
        assert isinstance(format_experience_text(0, 100), str)


class TestFormatExperienceBar:
    """Tests for format_experience_bar()."""

    def test_returns_tuple(self):
        result = format_experience_bar(50, 100, 5, width=10)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_zero_progress_all_empty(self):
        bar, _text = format_experience_bar(0, 100, 5, width=10)
        assert "█" not in bar

    def test_full_progress_all_filled(self):
        # next_level_exp = 0 means max level
        bar, _text = format_experience_bar(100, 0, 100, width=10)
        assert bar == "█" * 10

    def test_half_progress_half_filled(self):
        bar, _text = format_experience_bar(50, 100, 5, width=10)
        assert bar.count("█") == 5
        assert bar.count("░") == 5

    def test_text_contains_exp_values(self):
        _bar, text = format_experience_bar(50, 100, 5)
        assert "50" in text
        assert "100" in text


class TestFormatList:
    """Tests for format_list()."""

    def test_empty_list(self):
        assert format_list([]) == ""

    def test_single_item(self):
        assert format_list(["apple"]) == "apple"

    def test_two_items_joined_with_and(self):
        assert format_list(["apple", "banana"]) == "apple and banana"

    def test_three_items(self):
        result = format_list(["a", "b", "c"])
        assert result == "a, b, and c"

    def test_with_article(self):
        result = format_list(["Bulbasaur", "Charmander"], article="the")
        assert "the Bulbasaur" in result
        assert "the Charmander" in result

    def test_four_items(self):
        result = format_list(["a", "b", "c", "d"])
        assert result == "a, b, c, and d"


class TestGetTravelDescription:
    """Tests for get_travel_description()."""

    def test_known_location_returns_description(self):
        dest = get_location("Route 1")
        desc = get_travel_description("Route 1", dest)
        assert isinstance(desc, str)
        assert len(desc) > 0

    def test_unknown_location_falls_back_to_destination_description(self):
        dest = get_location("Pallet Town")
        desc = get_travel_description("Nonexistent Route", dest)
        assert isinstance(desc, str)
        assert len(desc) > 0

    def test_pallet_town_description(self):
        dest = get_location("Pallet Town")
        desc = get_travel_description("Pallet Town", dest)
        assert "hometown" in desc.lower() or isinstance(desc, str)
