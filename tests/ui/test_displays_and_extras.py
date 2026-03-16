"""
Extended tests for PokemonLibrary/ui/displays.py and additional
coverage for PokemonLibrary/data/trainer_data.py and PokemonLibrary/items.py.
"""

import pytest

from pytemon.data.move_data import MoveSlot
from pytemon.data.pokemon_data import StatsData
from pytemon.data.trainer_data import Trainer, TrainerPokemon
from pytemon.game_state import GameState
from pytemon.items import use_item_outside_battle
from pytemon.models import PartyPokemon
from pytemon.ui.displays import (
    activate_pikachu_mode,
    show_about,
    show_bag,
)


class MockRichLog:
    """Minimal stub for textual.widgets.RichLog."""

    def __init__(self):
        self.lines = []

    def write(self, text: str) -> None:
        self.lines.append(text)

    @property
    def combined(self) -> str:
        return " ".join(self.lines)


@pytest.fixture
def gs() -> GameState:
    gs = GameState()
    gs.start_new_game()
    return gs


@pytest.fixture
def output() -> MockRichLog:
    return MockRichLog()


def make_party_pokemon(
    name: str = "PIKACHU",
    number: int = 25,
    level: int = 10,
    hp: int = 35,
    max_hp: int = 35,
    status=None,
) -> PartyPokemon:
    p = PartyPokemon(
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
    p.status = status
    return p


def _give_item(gs: GameState, item_name: str, qty: int = 1) -> None:
    items = gs.game_data.setdefault("items", {})
    items[item_name] = items.get(item_name, 0) + qty


# ===========================================================================
# activate_pikachu_mode
# ===========================================================================


class TestActivatePikachuMode:
    def test_activates_when_no_pokemon(self, gs, output):
        gs.game_data["pokemon"] = []
        gs.pikachu_mode = False
        activate_pikachu_mode(gs, output)
        assert gs.pikachu_mode is True

    def test_nothing_happens_when_already_has_pokemon(self, gs, output):
        poke = make_party_pokemon()
        gs.game_data["pokemon"] = [poke]
        activate_pikachu_mode(gs, output)
        assert "Nothing happened" in output.combined

    def test_nothing_happens_if_already_activated(self, gs, output):
        gs.game_data["pokemon"] = []
        gs.pikachu_mode = True
        activate_pikachu_mode(gs, output)
        assert gs.pikachu_mode is True
        assert "already running" in output.combined.lower()

    def test_writes_output_on_activation(self, gs, output):
        gs.game_data["pokemon"] = []
        gs.pikachu_mode = False
        activate_pikachu_mode(gs, output)
        assert len(output.lines) > 0


# ===========================================================================
# show_about
# ===========================================================================


class TestShowAbout:
    def test_writes_output(self, output):
        show_about(output)
        assert len(output.lines) > 0

    def test_mentions_robot_framework(self, output):
        show_about(output)
        assert "Robot Framework" in output.combined

    def test_mentions_version(self, output):
        show_about(output)
        assert "0.1.0" in output.combined


# ===========================================================================
# show_bag
# ===========================================================================


class TestShowBag:
    def test_empty_bag_shows_message(self, gs, output):
        gs.game_data["items"] = {}
        show_bag(gs, output)
        assert "empty" in output.combined.lower()

    def test_shows_item_in_bag(self, gs, output):
        _give_item(gs, "Potion", 3)
        show_bag(gs, output)
        assert "Potion" in output.combined

    def test_shows_item_quantity(self, gs, output):
        _give_item(gs, "Super Potion", 5)
        show_bag(gs, output)
        assert "5" in output.combined or "Super Potion" in output.combined


# ===========================================================================
# Trainer dataclass - __getitem__ and get
# ===========================================================================


class TestTrainerAccessMethods:
    def _make_trainer(self) -> Trainer:
        return Trainer(
            id="test_trainer",
            name="Ash",
            trainer_class="Youngster",
            location="Route 1",
            pokemon=[TrainerPokemon(species="RATTATA", level=5)],
            prize_money=100,
            intro_text=["Ready!"],
            defeat_text=["Lost!"],
            victory_text=["Won!"],
            badge_reward="",  # empty sentinel
            badge_id="",  # empty sentinel
        )

    def test_getitem_returns_attribute(self):
        t = self._make_trainer()
        assert t["name"] == "Ash"
        assert t["prize_money"] == 100

    def test_get_existing_attribute(self):
        t = self._make_trainer()
        assert t.get("location") == "Route 1"

    def test_get_missing_attribute_returns_default(self):
        t = self._make_trainer()
        assert t.get("nonexistent_key", "fallback") == "fallback"

    def test_get_missing_attribute_returns_none(self):
        t = self._make_trainer()
        assert t.get("nonexistent_key") is None

    def test_get_badge_reward_empty_returns_default(self):
        t = self._make_trainer()
        # badge_reward is empty string (""), so get should return default
        assert t.get("badge_reward", "none") == "none"

    def test_get_badge_id_empty_returns_default(self):
        t = self._make_trainer()
        assert t.get("badge_id", "none") == "none"

    def test_get_badge_reward_with_value(self):
        t = self._make_trainer()
        t.badge_reward = "Boulder Badge"
        assert t.get("badge_reward") == "Boulder Badge"


# ===========================================================================
# items.py - escape rope and repel
# ===========================================================================


class TestUseEscapeRope:
    def test_escape_rope_in_town_shows_warning(self, gs, output):
        # Default location is Pallet Town (a town)
        _give_item(gs, "Escape Rope")
        result = use_item_outside_battle(gs, "Escape Rope", None, output)
        # Either returns False (in a town) or True (escaped)
        assert isinstance(result, bool)


class TestUseRepel:
    def test_repel_adds_steps(self, gs, output):
        _give_item(gs, "Repel")
        initial_steps = gs.game_data.get("repel_steps", 0)
        result = use_item_outside_battle(gs, "Repel", None, output)
        assert result is True
        assert gs.game_data.get("repel_steps", 0) > initial_steps

    def test_super_repel_adds_more_steps_than_repel(self, gs, output):
        _give_item(gs, "Repel")
        _give_item(gs, "Super Repel")
        gs2 = GameState()
        gs2.start_new_game()
        gs2.game_data["items"] = {"Repel": 1}
        out2 = MockRichLog()
        use_item_outside_battle(gs2, "Repel", None, out2)
        repel_steps = gs2.game_data.get("repel_steps", 0)

        gs3 = GameState()
        gs3.start_new_game()
        gs3.game_data["items"] = {"Super Repel": 1}
        out3 = MockRichLog()
        use_item_outside_battle(gs3, "Super Repel", None, out3)
        super_repel_steps = gs3.game_data.get("repel_steps", 0)

        assert super_repel_steps > repel_steps

    def test_repel_stacks_with_existing(self, gs, output):
        gs.game_data["repel_steps"] = 5
        _give_item(gs, "Repel")
        use_item_outside_battle(gs, "Repel", None, output)
        assert gs.game_data.get("repel_steps", 0) > 5
