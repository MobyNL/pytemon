"""Tests for the sell command in process_shop_command."""

import pytest

from pytemon.buildings import SELL_PRICES, process_shop_command
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


def noop_pending(cmd: str) -> None:
    pass


class TestSellItems:
    def test_sell_nugget(self, gs, output):
        """Player has 1 Nugget, sells it — gets ₽5000, Nugget removed from bag."""
        gs.game_data.setdefault("items", {})["Nugget"] = 1
        start_money = gs.game_data.get("money", 0)
        pending: list[str] = []
        process_shop_command(gs, "sell nugget", output, lambda cmd: pending.append(cmd))
        assert gs.game_data["money"] == start_money + 5000
        assert gs.game_data.get("items", {}).get("Nugget", 0) == 0
        assert "5000" in output.combined

    def test_sell_nugget_multi(self, gs, output):
        """Player has 3 Nuggets, 'sell 3 nugget' — gets ₽15000."""
        gs.game_data.setdefault("items", {})["Nugget"] = 3
        start_money = gs.game_data.get("money", 0)
        pending: list[str] = []
        process_shop_command(gs, "sell 3 nugget", output, lambda cmd: pending.append(cmd))
        assert gs.game_data["money"] == start_money + 15000
        assert gs.game_data.get("items", {}).get("Nugget", 0) == 0
        assert "15000" in output.combined

    def test_sell_potion(self, gs, output):
        """Potion buys for ₽300; sell earns ₽150 (50%)."""
        gs.game_data.setdefault("items", {})["Potion"] = 1
        start_money = gs.game_data.get("money", 0)
        pending: list[str] = []
        process_shop_command(gs, "sell potion", output, lambda cmd: pending.append(cmd))
        assert gs.game_data["money"] == start_money + 150
        assert gs.game_data.get("items", {}).get("Potion", 0) == 0
        assert "150" in output.combined

    def test_sell_qty_clamped_to_stock(self, gs, output):
        """Player has 2 Potions, tries 'sell 5 potion' — only 2 are sold."""
        gs.game_data.setdefault("items", {})["Potion"] = 2
        start_money = gs.game_data.get("money", 0)
        pending: list[str] = []
        process_shop_command(gs, "sell 5 potion", output, lambda cmd: pending.append(cmd))
        # 2 sold at ₽150 each = ₽300
        assert gs.game_data["money"] == start_money + 300
        assert gs.game_data.get("items", {}).get("Potion", 0) == 0

    def test_sell_no_resale(self, gs, output):
        """Selling an item with no resale value shows an appropriate error."""
        gs.game_data.setdefault("items", {})["Bicycle"] = 1
        pending: list[str] = []
        process_shop_command(gs, "sell bicycle", output, lambda cmd: pending.append(cmd))
        assert "no resale value" in output.combined.lower()
        # Item should still be in bag
        assert gs.game_data["items"].get("Bicycle", 1) == 1

    def test_sell_not_owned(self, gs, output):
        """Trying to sell an item the player doesn't own shows an error."""
        gs.game_data.setdefault("items", {})  # empty bag
        pending: list[str] = []
        process_shop_command(gs, "sell nugget", output, lambda cmd: pending.append(cmd))
        assert "don't have any" in output.combined.lower()

    def test_buy_still_works(self, gs, output):
        """Regression: 'buy potion' still works after sell command was added."""
        gs.game_data["money"] = 1000
        pending: list[str] = []
        process_shop_command(gs, "buy potion", output, lambda cmd: pending.append(cmd))
        assert gs.game_data.get("items", {}).get("Potion", 0) >= 1
        assert gs.game_data["money"] == 700

    def test_unknown_command_message(self, gs, output):
        """An unrecognised shop command mentions 'sell' in the help text."""
        pending: list[str] = []
        process_shop_command(gs, "look around", output, lambda cmd: pending.append(cmd))
        assert "sell" in output.combined.lower()

    def test_sell_prices_dict_has_nugget(self):
        """SELL_PRICES contains Nugget with value 5000."""
        assert SELL_PRICES.get("Nugget") == 5000

    def test_sell_prices_dict_fossils(self):
        """SELL_PRICES contains all three fossil entries at ₽3500."""
        assert SELL_PRICES.get("Dome Fossil") == 3500
        assert SELL_PRICES.get("Helix Fossil") == 3500
        assert SELL_PRICES.get("Old Amber") == 3500

    def test_sell_leaves_remaining_stock(self, gs, output):
        """Selling fewer than the full stack leaves the remainder in the bag."""
        gs.game_data.setdefault("items", {})["Nugget"] = 3
        start_money = gs.game_data.get("money", 0)
        pending: list[str] = []
        process_shop_command(gs, "sell 2 nugget", output, lambda cmd: pending.append(cmd))
        assert gs.game_data["money"] == start_money + 10000
        assert gs.game_data["items"].get("Nugget", 0) == 1

    def test_sell_advanced_catalog_item(self, gs, output):
        """Items from the advanced catalog can also be sold at 50% price."""
        gs.game_data["_current_shop_catalog"] = "advanced"
        gs.game_data.setdefault("items", {})["Revive"] = 1
        start_money = gs.game_data.get("money", 0)
        pending: list[str] = []
        process_shop_command(gs, "sell revive", output, lambda cmd: pending.append(cmd))
        # Revive costs 1500, sells for 750
        assert gs.game_data["money"] == start_money + 750
        assert gs.game_data.get("items", {}).get("Revive", 0) == 0
