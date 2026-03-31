"""
Tests for new cheat commands: cheat catch and cheat champion.
"""

import pytest

from pytemon.cheat_commands import become_champion, catch_wild_pokemon_cheat
from pytemon.engine import BattleState
from pytemon.game_state import GameState
from pytemon.gym_system import BADGES


class MockRichLog:
    """Mock RichLog for testing."""

    def __init__(self):
        self.lines: list[str] = []

    def write(self, text: str) -> None:
        self.lines.append(text)

    @property
    def combined(self) -> str:
        return "\n".join(str(line) for line in self.lines)


@pytest.fixture
def gs():
    """Create a GameState with a starter Pokemon."""
    state = GameState()
    state.start_new_game()
    # Add Bulbasaur as starter
    state.game_data["pokemon"] = [
        {
            "name": "BULBASAUR",
            "number": 1,
            "level": 5,
            "types": ["Grass", "Poison"],
            "hp": 20,
            "max_hp": 20,
            "stats": {"hp": 20, "attack": 10, "defense": 10, "speed": 10},
            "moves": ["TACKLE", "GROWL"],
            "experience": 0,
            "next_level_exp": 100,
            "status": None,
            "no_evolve": False,
        }
    ]
    return state


@pytest.fixture
def output():
    """Create a mock RichLog."""
    return MockRichLog()


class TestCheatCatch:
    """Tests for the 'cheat catch' command."""

    def test_catch_wild_pokemon_adds_to_party(self, gs, output):
        """Test that cheat catch adds wild Pokemon to party."""
        # Setup a wild battle
        bs = BattleState()
        player_pokemon = gs.get_active_pokemon()
        bs.start_wild_battle(player_pokemon, "PIDGEY", 5)
        gs.battle_state = bs
        gs.in_battle = True

        # Catch the Pokemon
        catch_wild_pokemon_cheat(gs, output)

        # Verify Pokemon was added to party
        assert len(gs.game_data["pokemon"]) == 2
        assert gs.game_data["pokemon"][1]["name"] == "PIDGEY"
        assert "PIDGEY" in output.combined

    def test_catch_wild_pokemon_sends_to_pc_when_party_full(self, gs, output):
        """Test that cheat catch sends Pokemon to PC when party is full."""
        # Fill party with 6 Pokemon
        for i in range(5):
            gs.game_data["pokemon"].append(
                {
                    "name": f"POKEMON_{i}",
                    "number": i + 2,
                    "level": 5,
                    "types": ["Normal"],
                    "hp": 20,
                    "max_hp": 20,
                    "stats": {"hp": 20, "attack": 10, "defense": 10, "speed": 10},
                    "moves": ["TACKLE"],
                    "experience": 0,
                    "next_level_exp": 100,
                    "status": None,
                    "no_evolve": False,
                }
            )

        # Setup a wild battle
        bs = BattleState()
        player_pokemon = gs.get_active_pokemon()
        bs.start_wild_battle(player_pokemon, "PIDGEY", 5)
        gs.battle_state = bs
        gs.in_battle = True

        # Catch the Pokemon
        catch_wild_pokemon_cheat(gs, output)

        # Verify party is still 6
        assert len(gs.game_data["pokemon"]) == 6

        # Verify the catch was successful (either to PC or PC full message)
        assert "PIDGEY" in output.combined or "Box" in output.combined

    def test_catch_updates_pokedex(self, gs, output):
        """Test that cheat catch updates the Pokedex."""
        # Setup a wild battle
        bs = BattleState()
        player_pokemon = gs.get_active_pokemon()
        bs.start_wild_battle(player_pokemon, "PIDGEY", 5)
        gs.battle_state = bs
        gs.in_battle = True

        # Catch the Pokemon
        catch_wild_pokemon_cheat(gs, output)

        # Verify Pokedex was updated
        caught = gs.game_data.get("pokedex", {}).get("caught", [])
        assert "PIDGEY" in caught


class TestCheatChampion:
    """Tests for the 'cheat champion' command."""

    def test_become_champion_unlocks_all_badges(self, gs, output):
        """Test that cheat champion unlocks all 8 badges."""
        # Initially no badges
        assert gs.game_data.get("badges", []) == []

        # Become champion
        become_champion(gs, output)

        # Verify all badges were unlocked
        badges = gs.game_data.get("badges", [])
        assert len(badges) == 8

        all_badge_ids = [badge["id"] for badge in BADGES.values()]
        for badge_id in all_badge_ids:
            assert badge_id in badges

        # Check output contains champion message
        assert "CHAMPION" in output.combined

    def test_become_champion_when_already_champion(self, gs, output):
        """Test cheat champion when already having all badges."""
        # Give all badges
        all_badge_ids = [badge["id"] for badge in BADGES.values()]
        gs.game_data["badges"] = all_badge_ids.copy()

        # Try to become champion again
        become_champion(gs, output)

        # Verify still has 8 badges (no duplicates)
        badges = gs.game_data.get("badges", [])
        assert len(badges) == 8

        # Check output says already champion
        assert "already" in output.combined.lower()

    def test_become_champion_with_partial_badges(self, gs, output):
        """Test cheat champion when having some badges already."""
        # Give 3 badges
        gs.game_data["badges"] = ["boulder_badge", "cascade_badge", "thunder_badge"]

        # Become champion
        become_champion(gs, output)

        # Verify all badges were unlocked
        badges = gs.game_data.get("badges", [])
        assert len(badges) == 8

        all_badge_ids = [badge["id"] for badge in BADGES.values()]
        for badge_id in all_badge_ids:
            assert badge_id in badges

    def test_become_champion_displays_all_badges(self, gs, output):
        """Test that become_champion displays all badge information."""
        become_champion(gs, output)

        # Check that all 8 badge names appear in the output
        for badge_name in BADGES.keys():
            assert badge_name in output.combined
