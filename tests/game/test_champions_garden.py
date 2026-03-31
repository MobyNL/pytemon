"""Test Champion's Garden location and access mechanics."""

import pytest

from pytemon.game_state import GameState
from pytemon.locations import get_location


class TestChampionsGarden:
    """Test Champion's Garden location functionality."""

    def test_champions_garden_exists(self):
        """Verify Champion's Garden location is defined."""
        garden = get_location("Champion's Garden")
        assert garden is not None
        assert garden.name == "Champion's Garden"
        assert garden.type == "route"

    def test_champions_garden_has_starters_and_eevee(self):
        """Verify all starters, Eevee, and fighting Pokemon are in wild encounters."""
        garden = get_location("Champion's Garden")
        assert "BULBASAUR" in garden.wild_pokemon
        assert "CHARMANDER" in garden.wild_pokemon
        assert "SQUIRTLE" in garden.wild_pokemon
        assert "EEVEE" in garden.wild_pokemon
        assert "HITMONLEE" in garden.wild_pokemon
        assert "HITMONCHAN" in garden.wild_pokemon
        # Should have 6 total species
        assert len(garden.wild_pokemon) == 6

    def test_champions_garden_level_range(self):
        """Verify wild Pokemon level range is 25-30."""
        garden = get_location("Champion's Garden")
        min_level, max_level = garden.wild_level_range
        assert min_level == 25
        assert max_level == 30

    def test_champions_garden_high_encounter_rate(self):
        """Verify high encounter rate for easy catching."""
        garden = get_location("Champion's Garden")
        assert garden.wild_encounter_rate == 0.65  # 65% encounter rate

    def test_champions_garden_connected_to_cerulean_cave(self):
        """Verify Champion's Garden is accessible from Cerulean Cave."""
        cerulean_cave = get_location("Cerulean Cave")
        assert "Champion's Garden" in cerulean_cave.exits

        # Check it's initially blocked
        exit_data = cerulean_cave.exits["Champion's Garden"]
        assert exit_data.get("blocked") is True
        assert "reason" in exit_data

    def test_champions_garden_exit_to_cerulean_cave(self):
        """Verify Champion's Garden has exit back to Cerulean Cave."""
        garden = get_location("Champion's Garden")
        assert "Cerulean Cave" in garden.exits
        assert garden.exits["Cerulean Cave"].get("blocked") is False

    def test_champions_garden_no_trainers(self):
        """Verify no trainers in Champion's Garden (peaceful sanctuary)."""
        garden = get_location("Champion's Garden")
        assert garden.trainers == 0
        assert garden.trainer_encounter_rate == 0.0


class TestChampionsGardenAccess:
    """Test Champion's Garden access gating logic."""

    @pytest.fixture
    def gs(self):
        """Create a fresh game state."""
        state = GameState()
        state.start_new_game()
        return state

    def test_champion_garden_blocked_before_champion(self, gs):
        """Verify Champion's Garden is blocked before becoming Champion."""
        from pytemon.exploration import move_to_location
        from pytemon.locations import get_location

        class MockOutput:
            def __init__(self):
                self.lines = []

            def write(self, text: str) -> None:
                self.lines.append(text)

            @property
            def combined(self) -> str:
                return "\n".join(str(line) for line in self.lines)

        def mock_callback(output):
            pass

        # Set location to Cerulean Cave (normally Champion-only, but bypass for test)
        gs.current_location = get_location("Cerulean Cave")
        gs.game_data["location"] = "Cerulean Cave"
        gs.game_data["story_flags"]["is_champion"] = False  # NOT Champion yet

        output = MockOutput()

        # Try to move to Champion's Garden
        move_to_location(gs, "Champion's Garden", output, mock_callback)

        # Should be blocked
        assert gs.game_data["location"] == "Cerulean Cave"  # Still at Cerulean Cave
        assert any("blocked" in line.lower() or "champion" in line.lower() for line in output.lines)

    def test_champion_garden_accessible_after_champion(self, gs):
        """Verify Champion's Garden is accessible after becoming Champion."""
        from pytemon.exploration import move_to_location
        from pytemon.locations import get_location

        class MockOutput:
            def __init__(self):
                self.lines = []

            def write(self, text: str) -> None:
                self.lines.append(text)

            @property
            def combined(self) -> str:
                return "\n".join(str(line) for line in self.lines)

        def mock_callback(output):
            pass

        # Set up as Champion at Cerulean Cave
        gs.current_location = get_location("Cerulean Cave")
        gs.game_data["location"] = "Cerulean Cave"
        gs.game_data["story_flags"]["is_champion"] = True  # IS Champion

        output = MockOutput()

        # Try to move to Champion's Garden
        move_to_location(gs, "Champion's Garden", output, mock_callback)

        # Should succeed
        assert gs.game_data["location"] == "Champion's Garden"
        assert not any("blocked" in line.lower() for line in output.lines)
