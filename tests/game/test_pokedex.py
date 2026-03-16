"""
Unit tests for PokemonLibrary/pokedex.py.
"""

import pytest

from pytemon.game_state import GameState
from pytemon.pokedex import (
    get_caught_milestone_message,
    get_first_type_message,
    get_pokedex_state,
    get_pokedex_stats,
    initialize_pokedex,
    is_caught,
    is_seen,
    mark_as_caught,
    mark_as_seen,
    show_pokedex,
)


@pytest.fixture
def fresh_state() -> GameState:
    """Return a GameState with a new game + initialized Pokedex."""
    gs = GameState()
    gs.start_new_game()
    initialize_pokedex(gs)
    return gs


class TestInitializePokedex:
    """Tests for initialize_pokedex()."""

    def test_creates_pokedex_key(self):
        gs = GameState()
        gs.start_new_game()
        initialize_pokedex(gs)
        assert "pokedex" in gs.game_data

    def test_initial_seen_is_empty(self):
        gs = GameState()
        gs.start_new_game()
        initialize_pokedex(gs)
        assert gs.game_data["pokedex"]["seen"] == []

    def test_initial_caught_is_empty(self):
        gs = GameState()
        gs.start_new_game()
        initialize_pokedex(gs)
        assert gs.game_data["pokedex"]["caught"] == []

    def test_does_not_overwrite_existing(self):
        gs = GameState()
        gs.start_new_game()
        gs.game_data["pokedex"] = {"seen": ["PIKACHU"], "caught": []}
        initialize_pokedex(gs)
        assert "PIKACHU" in gs.game_data["pokedex"]["seen"]


class TestMarkAsSeen:
    """Tests for mark_as_seen()."""

    def test_unseen_pokemon_is_marked(self, fresh_state):
        result = mark_as_seen(fresh_state, "PIKACHU")
        assert result is True
        assert is_seen(fresh_state, "PIKACHU")

    def test_already_seen_returns_false(self, fresh_state):
        mark_as_seen(fresh_state, "PIKACHU")
        result = mark_as_seen(fresh_state, "PIKACHU")
        assert result is False

    def test_already_seen_pokemon_returns_false(self, fresh_state):
        mark_as_seen(fresh_state, "BULBASAUR")
        result = mark_as_seen(fresh_state, "BULBASAUR")
        assert result is False

    def test_seen_does_not_mark_as_caught(self, fresh_state):
        mark_as_seen(fresh_state, "PIKACHU")
        assert not is_caught(fresh_state, "PIKACHU")


class TestMarkAsCaught:
    """Tests for mark_as_caught()."""

    def test_uncaught_pokemon_is_marked(self, fresh_state):
        result = mark_as_caught(fresh_state, "CHARMANDER")
        assert result is True
        assert is_caught(fresh_state, "CHARMANDER")

    def test_catching_also_marks_as_seen(self, fresh_state):
        mark_as_caught(fresh_state, "CHARMANDER")
        assert is_seen(fresh_state, "CHARMANDER")

    def test_already_caught_returns_false(self, fresh_state):
        mark_as_caught(fresh_state, "CHARMANDER")
        result = mark_as_caught(fresh_state, "CHARMANDER")
        assert result is False

    def test_already_caught_pokemon_returns_false_in_catch(self, fresh_state):
        mark_as_caught(fresh_state, "CHARMANDER")
        result = mark_as_caught(fresh_state, "CHARMANDER")
        assert result is False


class TestIsSeen:
    """Tests for is_seen()."""

    def test_unseen_pokemon_returns_false(self, fresh_state):
        assert not is_seen(fresh_state, "SQUIRTLE")

    def test_seen_pokemon_returns_true(self, fresh_state):
        mark_as_seen(fresh_state, "SQUIRTLE")
        assert is_seen(fresh_state, "SQUIRTLE")

    def test_caught_pokemon_is_also_seen(self, fresh_state):
        mark_as_caught(fresh_state, "BULBASAUR")
        assert is_seen(fresh_state, "BULBASAUR")


class TestIsCaught:
    """Tests for is_caught()."""

    def test_not_caught_returns_false(self, fresh_state):
        assert not is_caught(fresh_state, "RATTATA")

    def test_caught_returns_true(self, fresh_state):
        mark_as_caught(fresh_state, "RATTATA")
        assert is_caught(fresh_state, "RATTATA")

    def test_seen_but_not_caught_returns_false(self, fresh_state):
        mark_as_seen(fresh_state, "RATTATA")
        assert not is_caught(fresh_state, "RATTATA")


class TestGetPokedexStats:
    """Tests for get_pokedex_stats()."""

    def test_empty_pokedex_all_zeros(self, fresh_state):
        stats = get_pokedex_stats(fresh_state)
        assert stats["seen"] == 0
        assert stats["caught"] == 0

    def test_counts_seen(self, fresh_state):
        mark_as_seen(fresh_state, "PIKACHU")
        mark_as_seen(fresh_state, "CHARMANDER")
        stats = get_pokedex_stats(fresh_state)
        assert stats["seen"] == 2

    def test_counts_caught(self, fresh_state):
        mark_as_caught(fresh_state, "PIKACHU")
        stats = get_pokedex_stats(fresh_state)
        assert stats["caught"] == 1

    def test_caught_counted_in_seen(self, fresh_state):
        mark_as_caught(fresh_state, "PIKACHU")
        stats = get_pokedex_stats(fresh_state)
        assert stats["seen"] >= 1

    def test_returns_dict_with_required_keys(self, fresh_state):
        stats = get_pokedex_stats(fresh_state)
        assert "seen" in stats
        assert "caught" in stats
        assert "total" in stats


class TestGetPokedexState:
    """Tests for get_pokedex_state() (pagination state)."""

    def test_returns_dict(self, fresh_state):
        state = get_pokedex_state(fresh_state)
        assert isinstance(state, dict)

    def test_contains_current_page(self, fresh_state):
        state = get_pokedex_state(fresh_state)
        assert "current_page" in state

    def test_contains_filter_mode(self, fresh_state):
        state = get_pokedex_state(fresh_state)
        assert "filter_mode" in state

    def test_default_page_is_one(self, fresh_state):
        state = get_pokedex_state(fresh_state)
        assert state["current_page"] == 1

    def test_default_filter_is_all(self, fresh_state):
        state = get_pokedex_state(fresh_state)
        assert state["filter_mode"] == "all"

    def test_returns_same_object_on_second_call(self, fresh_state):
        state1 = get_pokedex_state(fresh_state)
        state2 = get_pokedex_state(fresh_state)
        assert state1 is state2


class MockRichLog:
    def __init__(self):
        self.lines: list[str] = []

    def write(self, text: str) -> None:
        self.lines.append(str(text))

    @property
    def combined(self) -> str:
        return "\n".join(str(line) for line in self.lines)


class TestGetCaughtMilestoneMessage:
    """Tests for get_caught_milestone_message()."""

    def test_first_catch_contains_first(self):
        msg = get_caught_milestone_message(1)
        assert msg is not None
        assert "First" in msg or "first" in msg

    def test_milestone_10_contains_10(self):
        msg = get_caught_milestone_message(10)
        assert msg is not None
        assert "10" in msg

    def test_milestone_25_contains_25(self):
        msg = get_caught_milestone_message(25)
        assert msg is not None
        assert "25" in msg

    def test_milestone_50_contains_50(self):
        msg = get_caught_milestone_message(50)
        assert msg is not None
        assert "50" in msg

    def test_milestone_150_contains_complete_or_150(self):
        msg = get_caught_milestone_message(150)
        assert msg is not None
        assert "COMPLETE" in msg or "150" in msg

    def test_non_milestone_5_returns_none(self):
        assert get_caught_milestone_message(5) is None

    def test_non_milestone_11_returns_none(self):
        assert get_caught_milestone_message(11) is None

    def test_non_milestone_0_returns_none(self):
        assert get_caught_milestone_message(0) is None

    def test_milestone_75_contains_75(self):
        msg = get_caught_milestone_message(75)
        assert msg is not None
        assert "75" in msg

    def test_milestone_100_contains_100(self):
        msg = get_caught_milestone_message(100)
        assert msg is not None
        assert "100" in msg

    def test_returns_string_for_every_milestone(self):
        for m in [1, 10, 25, 50, 75, 100, 150]:
            assert isinstance(get_caught_milestone_message(m), str)


class TestGetFirstTypeMessage:
    """Tests for get_first_type_message()."""

    def test_first_catch_of_type_returns_message(self, fresh_state):
        msg = get_first_type_message(fresh_state, "PIKACHU")
        assert msg is not None
        assert isinstance(msg, str)

    def test_first_catch_message_mentions_type(self, fresh_state):
        msg = get_first_type_message(fresh_state, "PIKACHU")
        assert msg is not None
        assert "Electric" in msg or "type" in msg.lower()

    def test_second_catch_of_same_type_returns_none(self, fresh_state):
        # Call get_first_type_message twice for PIKACHU (Electric);
        # the second call should return None because the Electric flag is already set.
        get_first_type_message(fresh_state, "PIKACHU")
        msg = get_first_type_message(fresh_state, "PIKACHU")
        assert msg is None

    def test_unknown_species_returns_none(self, fresh_state):
        msg = get_first_type_message(fresh_state, "NONEXISTENTPOKEMON")
        assert msg is None

    def test_different_type_returns_message(self, fresh_state):
        # Mark Electric as first caught
        get_first_type_message(fresh_state, "PIKACHU")
        # Fire type should still get a first-type message
        msg = get_first_type_message(fresh_state, "CHARMANDER")
        assert msg is not None
        assert "Fire" in msg


class TestShowPokedexNextMilestone:
    """Tests that show_pokedex() outputs next milestone text when caught < 150."""

    def test_shows_next_milestone_when_no_pokemon_caught(self, fresh_state):
        output = MockRichLog()
        show_pokedex(fresh_state, output)
        assert "Next milestone" in output.combined or "milestone" in output.combined.lower()

    def test_next_milestone_text_not_shown_when_all_caught(self, fresh_state):
        # Artificially populate 150 caught entries
        from pytemon.data import POKEMON

        for num, data in POKEMON.items():
            name = data.get("name", f"POKEMON{num}")
            mark_as_caught(fresh_state, name)
        output = MockRichLog()
        show_pokedex(fresh_state, output)
        assert "Next milestone" not in output.combined

    def test_milestone_progress_count_shown(self, fresh_state):
        mark_as_caught(fresh_state, "PIKACHU")
        output = MockRichLog()
        show_pokedex(fresh_state, output)
        # Should show e.g. "Next milestone: 10 caught (9 to go)"
        assert "to go" in output.combined or "milestone" in output.combined.lower()
