"""
Unit tests for PokemonLibrary/pc_system.py.
"""

import pytest

from pytemon.game_state import GameState
from pytemon.pc_system import (
    BOX_CAPACITY,
    BOXES_COUNT,
    get_pc_storage,
    get_total_in_pc,
    process_pc_command,
    send_to_pc,
    show_pc_box,
    show_pc_menu,
    withdraw_from_pc,
)


class MockRichLog:
    """Minimal stub for textual.widgets.RichLog."""

    def __init__(self):
        self.lines = []

    def write(self, text: str) -> None:
        self.lines.append(text)


@pytest.fixture
def gs() -> GameState:
    gs = GameState()
    gs.start_new_game()
    return gs


@pytest.fixture
def output() -> MockRichLog:
    return MockRichLog()


def _make_pokemon(name: str = "PIKACHU", level: int = 10) -> dict:
    return {
        "name": name,
        "level": level,
        "types": ["Normal"],
        "hp": 35,
        "max_hp": 35,
        "stats": {"hp": 35, "attack": 55, "defense": 30, "special": 50, "speed": 90},
        "moves": [{"name": "TACKLE", "pp": 35, "max_pp": 35}],
        "experience": 0,
        "next_level_exp": 1000,
    }


# ---------------------------------------------------------------------------
# get_pc_storage
# ---------------------------------------------------------------------------


class TestGetPcStorage:
    def test_creates_all_boxes_on_first_call(self, gs):
        storage = get_pc_storage(gs)
        for i in range(1, BOXES_COUNT + 1):
            assert f"Box {i}" in storage

    def test_each_box_has_correct_capacity(self, gs):
        storage = get_pc_storage(gs)
        for box in storage.values():
            assert len(box) == BOX_CAPACITY

    def test_all_slots_initially_none(self, gs):
        storage = get_pc_storage(gs)
        for box in storage.values():
            assert all(slot is None for slot in box)

    def test_returns_same_object_on_second_call(self, gs):
        storage1 = get_pc_storage(gs)
        storage2 = get_pc_storage(gs)
        assert storage1 is storage2

    def test_pads_short_boxes_for_backward_compat(self, gs):
        # Simulate a save with a box that has fewer slots
        gs.game_data["pc_storage"] = {"Box 1": [None] * 5}
        storage = get_pc_storage(gs)
        assert len(storage["Box 1"]) == BOX_CAPACITY


# ---------------------------------------------------------------------------
# get_total_in_pc
# ---------------------------------------------------------------------------


class TestGetTotalInPc:
    def test_empty_storage_returns_zero(self, gs):
        assert get_total_in_pc(gs) == 0

    def test_counts_one_pokemon(self, gs):
        get_pc_storage(gs)["Box 1"][0] = _make_pokemon()
        assert get_total_in_pc(gs) == 1

    def test_counts_across_multiple_boxes(self, gs):
        storage = get_pc_storage(gs)
        storage["Box 1"][0] = _make_pokemon()
        storage["Box 2"][3] = _make_pokemon("BULBASAUR")
        storage["Box 3"][7] = _make_pokemon("SQUIRTLE")
        assert get_total_in_pc(gs) == 3


# ---------------------------------------------------------------------------
# send_to_pc
# ---------------------------------------------------------------------------


class TestSendToPc:
    def test_stores_pokemon_in_box_1(self, gs):
        poke = _make_pokemon()
        box_name = send_to_pc(gs, poke)
        assert box_name == "Box 1"

    def test_stored_pokemon_is_retrievable(self, gs):
        poke = _make_pokemon("CHARMANDER")
        send_to_pc(gs, poke)
        storage = get_pc_storage(gs)
        assert storage["Box 1"][0] is poke

    def test_returns_none_when_pc_full(self, gs):
        storage = get_pc_storage(gs)
        for box_key in storage:
            storage[box_key] = [_make_pokemon() for _ in range(BOX_CAPACITY)]
        result = send_to_pc(gs, _make_pokemon("MEWTWO"))
        assert result is None

    def test_fills_slots_sequentially(self, gs):
        p1 = _make_pokemon("PIKACHU")
        p2 = _make_pokemon("RATTATA")
        send_to_pc(gs, p1)
        send_to_pc(gs, p2)
        storage = get_pc_storage(gs)
        assert storage["Box 1"][0] is p1
        assert storage["Box 1"][1] is p2


# ---------------------------------------------------------------------------
# withdraw_from_pc
# ---------------------------------------------------------------------------


class TestWithdrawFromPc:
    def test_withdraw_returns_pokemon(self, gs):
        poke = _make_pokemon()
        send_to_pc(gs, poke)
        result = withdraw_from_pc(gs, 1, 1)
        assert result is poke

    def test_slot_is_cleared_after_withdraw(self, gs):
        poke = _make_pokemon()
        send_to_pc(gs, poke)
        withdraw_from_pc(gs, 1, 1)
        storage = get_pc_storage(gs)
        assert storage["Box 1"][0] is None

    def test_withdraw_invalid_box_returns_none(self, gs):
        result = withdraw_from_pc(gs, 99, 1)
        assert result is None

    def test_withdraw_empty_slot_returns_none(self, gs):
        get_pc_storage(gs)  # ensure boxes exist
        result = withdraw_from_pc(gs, 1, 1)
        assert result is None

    def test_withdraw_out_of_range_slot_returns_none(self, gs):
        get_pc_storage(gs)
        result = withdraw_from_pc(gs, 1, BOX_CAPACITY + 99)
        assert result is None

    def test_withdraw_slot_zero_returns_none(self, gs):
        get_pc_storage(gs)
        result = withdraw_from_pc(gs, 1, 0)
        assert result is None


# ---------------------------------------------------------------------------
# show_pc_menu
# ---------------------------------------------------------------------------


class TestShowPcMenu:
    def test_writes_output_without_error(self, gs, output):
        show_pc_menu(gs, output)
        assert len(output.lines) > 0

    def test_shows_box_overview(self, gs, output):
        show_pc_menu(gs, output)
        combined = " ".join(output.lines)
        assert "Box" in combined

    def test_shows_pokemon_preview(self, gs, output):
        storage = get_pc_storage(gs)
        storage["Box 1"][0] = _make_pokemon("CHARIZARD")
        show_pc_menu(gs, output)
        combined = " ".join(output.lines)
        assert "CHARIZARD" in combined


# ---------------------------------------------------------------------------
# show_pc_box
# ---------------------------------------------------------------------------


class TestShowPcBox:
    def test_shows_empty_box(self, gs, output):
        show_pc_box(gs, 1, output)
        combined = " ".join(output.lines)
        assert "empty" in combined.lower() or "Box 1" in combined

    def test_shows_invalid_box_error(self, gs, output):
        show_pc_box(gs, 99, output)
        combined = " ".join(output.lines)
        assert "doesn't exist" in combined or "❌" in combined

    def test_shows_pokemon_in_box(self, gs, output):
        storage = get_pc_storage(gs)
        storage["Box 2"][0] = _make_pokemon("SNORLAX", level=30)
        show_pc_box(gs, 2, output)
        combined = " ".join(output.lines)
        assert "SNORLAX" in combined


# ---------------------------------------------------------------------------
# process_pc_command
# ---------------------------------------------------------------------------


class TestProcessPcCommand:
    def _make_pending_callback(self):
        state = {"last": None}

        def callback(val):
            state["last"] = val

        return callback, state

    def test_leave_command_does_not_call_pending(self, gs, output):
        cb, state = self._make_pending_callback()
        process_pc_command(gs, "leave", output, cb)
        # leave should NOT call set_pending
        assert state["last"] is None

    def test_box_command_shows_box(self, gs, output):
        cb, _ = self._make_pending_callback()
        process_pc_command(gs, "box 1", output, cb)
        combined = " ".join(output.lines)
        assert "Box 1" in combined

    def test_box_command_invalid_number_shows_error(self, gs, output):
        cb, _ = self._make_pending_callback()
        process_pc_command(gs, "box 99", output, cb)
        combined = " ".join(output.lines)
        assert "❌" in combined or "between" in combined

    def test_box_command_no_number_shows_usage(self, gs, output):
        cb, _ = self._make_pending_callback()
        process_pc_command(gs, "box", output, cb)
        combined = " ".join(output.lines)
        assert "Usage" in combined or "❌" in combined

    def test_deposit_command_removes_from_party(self, gs, output):
        cb, _ = self._make_pending_callback()
        # Add 2 pokemon to party (can't deposit last one)
        gs.game_data["pokemon"] = [_make_pokemon("BULBASAUR"), _make_pokemon("PIKACHU")]
        process_pc_command(gs, "deposit 1", output, cb)
        assert len(gs.game_data["pokemon"]) == 1
        assert get_total_in_pc(gs) == 1

    def test_deposit_last_pokemon_is_rejected(self, gs, output):
        cb, _ = self._make_pending_callback()
        gs.game_data["pokemon"] = [_make_pokemon()]
        process_pc_command(gs, "deposit 1", output, cb)
        combined = " ".join(output.lines)
        assert "last" in combined.lower() or "❌" in combined

    def test_deposit_invalid_slot_shows_error(self, gs, output):
        cb, _ = self._make_pending_callback()
        gs.game_data["pokemon"] = [_make_pokemon(), _make_pokemon("RATTATA")]
        process_pc_command(gs, "deposit 9", output, cb)
        combined = " ".join(output.lines)
        assert "❌" in combined

    def test_deposit_no_arg_shows_usage(self, gs, output):
        cb, _ = self._make_pending_callback()
        process_pc_command(gs, "deposit", output, cb)
        combined = " ".join(output.lines)
        assert "Usage" in combined or "❌" in combined

    def test_withdraw_adds_to_party(self, gs, output):
        cb, _ = self._make_pending_callback()
        poke = _make_pokemon("MAGIKARP")
        send_to_pc(gs, poke)
        gs.game_data["pokemon"] = [_make_pokemon()]
        process_pc_command(gs, "withdraw 1 1", output, cb)
        assert len(gs.game_data["pokemon"]) == 2

    def test_withdraw_full_party_rejected(self, gs, output):
        cb, _ = self._make_pending_callback()
        poke = _make_pokemon("MAGIKARP")
        send_to_pc(gs, poke)
        gs.game_data["pokemon"] = [_make_pokemon() for _ in range(6)]
        process_pc_command(gs, "withdraw 1 1", output, cb)
        combined = " ".join(output.lines)
        assert "full" in combined.lower() or "❌" in combined

    def test_withdraw_empty_slot_shows_error(self, gs, output):
        cb, _ = self._make_pending_callback()
        gs.game_data["pokemon"] = [_make_pokemon()]
        process_pc_command(gs, "withdraw 1 1", output, cb)
        combined = " ".join(output.lines)
        assert "No Pokemon" in combined or "❌" in combined

    def test_withdraw_no_args_shows_usage(self, gs, output):
        cb, _ = self._make_pending_callback()
        process_pc_command(gs, "withdraw", output, cb)
        combined = " ".join(output.lines)
        assert "Usage" in combined or "❌" in combined

    def test_unknown_command_shows_help(self, gs, output):
        cb, _ = self._make_pending_callback()
        process_pc_command(gs, "frobnicate", output, cb)
        combined = " ".join(output.lines)
        assert "Unknown" in combined or "?" in combined

    def test_exit_aliases_for_leave(self, gs, output):
        for cmd in ("exit", "done", "back", "bye", "close", "log out"):
            out = MockRichLog()
            cb, state = self._make_pending_callback()
            process_pc_command(gs, cmd, out, cb)
            assert state["last"] is None  # never called
