"""Tests for the rival_cerulean trainer data entry and battle flag."""

import pytest

from pytemon.battle.battle_actions import handle_trainer_defeated
from pytemon.data.trainer_data import TRAINERS
from pytemon.engine import BattleState
from pytemon.game_state import GameState


class MockRichLog:
    def __init__(self):
        self.lines: list[str] = []

    def write(self, text: str) -> None:
        self.lines.append(text)

    @property
    def combined(self) -> str:
        return "\n".join(str(line) for line in self.lines)


@pytest.fixture
def gs() -> GameState:
    state = GameState()
    state.start_new_game()
    return state


@pytest.fixture
def output() -> MockRichLog:
    return MockRichLog()


def _setup_rival_cerulean_battle(gs: GameState) -> BattleState:
    """Helper: put gs into an active rival_cerulean trainer battle."""
    bs = BattleState()
    player_pokemon = bs.generate_wild_pokemon("PIKACHU", 20)
    gs.game_data["pokemon"] = [player_pokemon]
    trainer = TRAINERS["rival_cerulean"]
    bs.start_trainer_battle(player_pokemon, trainer)
    gs.battle_state = bs
    gs.in_battle = True
    return bs


class TestRivalCerulean:
    def test_rival_cerulean_exists(self):
        """TRAINERS dict contains a 'rival_cerulean' entry."""
        assert "rival_cerulean" in TRAINERS

    def test_rival_cerulean_location(self):
        """rival_cerulean is located in Cerulean City."""
        trainer = TRAINERS["rival_cerulean"]
        assert trainer["location"] == "Cerulean City"

    def test_rival_cerulean_pokemon_count(self):
        """rival_cerulean has exactly 2 Pokemon."""
        trainer = TRAINERS["rival_cerulean"]
        assert len(trainer.pokemon) == 2

    def test_rival_cerulean_first_pokemon(self):
        """rival_cerulean's first Pokemon is CHARMELEON at level 18."""
        trainer = TRAINERS["rival_cerulean"]
        first = trainer.pokemon[0]
        assert first.species == "CHARMELEON"
        assert first.level == 18

    def test_rival_cerulean_second_pokemon(self):
        """rival_cerulean's second Pokemon is PIDGEOTTO at level 16."""
        trainer = TRAINERS["rival_cerulean"]
        second = trainer.pokemon[1]
        assert second.species == "PIDGEOTTO"
        assert second.level == 16

    def test_rival_cerulean_prize(self):
        """rival_cerulean awards ₽900 prize money."""
        trainer = TRAINERS["rival_cerulean"]
        assert trainer["prize_money"] == 900

    def test_rival_cerulean_id(self):
        """rival_cerulean trainer id field matches the dict key."""
        trainer = TRAINERS["rival_cerulean"]
        assert trainer["id"] == "rival_cerulean"

    def test_rival_cerulean_trainer_class(self):
        """rival_cerulean trainer_class is 'Rival'."""
        trainer = TRAINERS["rival_cerulean"]
        assert trainer["trainer_class"] == "Rival"

    def test_rival_cerulean_beaten_flag(self, gs, output):
        """Defeating rival_cerulean sets story_flags['rival_cerulean_beaten'] = True."""
        _setup_rival_cerulean_battle(gs)
        handle_trainer_defeated(gs, output, lambda out: None)
        story_flags = gs.game_data.get("story_flags", {})
        assert story_flags.get("rival_cerulean_beaten") is True

    def test_rival_cerulean_beaten_flag_not_set_for_other_trainer(self, gs, output):
        """Defeating a different trainer does NOT set rival_cerulean_beaten."""
        bs = BattleState()
        player_pokemon = bs.generate_wild_pokemon("PIKACHU", 10)
        gs.game_data["pokemon"] = [player_pokemon]
        other_trainer = TRAINERS.get("youngster_joey_route1") or next(
            t for t in TRAINERS.values() if t["id"] != "rival_cerulean"
        )
        bs.start_trainer_battle(player_pokemon, other_trainer)
        gs.battle_state = bs
        gs.in_battle = True
        handle_trainer_defeated(gs, output, lambda out: None)
        story_flags = gs.game_data.get("story_flags", {})
        assert story_flags.get("rival_cerulean_beaten") is not True

    def test_rival_cerulean_prize_money_awarded(self, gs, output):
        """Defeating rival_cerulean awards ₽900 to the player."""
        _setup_rival_cerulean_battle(gs)
        start_money = gs.game_data.get("money", 0)
        handle_trainer_defeated(gs, output, lambda out: None)
        assert gs.game_data.get("money", 0) == start_money + 900

    def test_rival_cerulean_marked_as_defeated(self, gs, output):
        """rival_cerulean is added to defeated_trainers after the battle."""
        _setup_rival_cerulean_battle(gs)
        handle_trainer_defeated(gs, output, lambda out: None)
        assert "rival_cerulean" in gs.game_data.get("defeated_trainers", [])

    def test_rival_cerulean_has_intro_text(self):
        """rival_cerulean has non-empty intro_text lines."""
        trainer = TRAINERS["rival_cerulean"]
        assert len(trainer.intro_text) > 0

    def test_rival_cerulean_has_defeat_text(self):
        """rival_cerulean has non-empty defeat_text lines."""
        trainer = TRAINERS["rival_cerulean"]
        assert len(trainer.defeat_text) > 0
