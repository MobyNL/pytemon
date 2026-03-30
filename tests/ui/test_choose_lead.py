"""
Tests for the pre-battle lead-Pokemon selection flow.

Covers:
- BattleMixin._show_lead_selection_prompt (skip when 1 fighter, prompt when 2+)
- BattleMixin.trigger_wild_encounter / trigger_trainer_encounter delegation
- GameFlowMixin._handle_choose_lead (cancel, invalid input, valid choice, swap)
- handle_pending_command "choose_lead" dispatch
"""

import pytest

from pytemon.game_state import GameState
from pytemon.ui.battle_mixin import BattleMixin
from pytemon.ui.game_flow_mixin import GameFlowMixin

# Sorted import block: stdlib → third-party → local (already correct above)
# ruff I001 fix: ensure the trailing newline after the last import is clean


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class MockRichLog:
    def __init__(self):
        self.lines: list = []

    def write(self, text) -> None:
        self.lines.append(str(text))

    @property
    def combined(self) -> str:
        return " ".join(self.lines)


def _make_pokemon(name: str, hp: int = 35, max_hp: int = 35, level: int = 10) -> dict:
    return {
        "name": name,
        "hp": hp,
        "max_hp": max_hp,
        "level": level,
        "types": ["Normal"],
        "moves": [{"name": "Tackle", "pp": 35, "max_pp": 35}],
        "experience": 0,
        "next_level_exp": 100,
        "status": None,
    }


class MockAnimatedTextWriter:
    """Writes all lines instantly and calls on_complete synchronously."""

    def write_medium(self, output, lines, on_complete=None):
        for line in lines:
            output.write(line)
        if on_complete:
            on_complete()


class MockChooseLeadTerminal(BattleMixin, GameFlowMixin):
    """Combined mock terminal for choose-lead flow tests."""

    def __init__(self):
        self.game_state = GameState()
        self.game_state.start_new_game()
        self.pending_command = None
        self.pending_command_data = {}
        self.lock_file_path = None
        self.text_animator = MockAnimatedTextWriter()
        self._calls: dict = {}

    # -- BattleMixin stubs -------------------------------------------------

    def show_battle_hud(self):
        self._calls["show_battle_hud"] = True

    def update_battle_hud(self):
        self._calls["update_battle_hud"] = True

    def show_battle_action_panel(self):
        self._calls["show_battle_action_panel"] = True

    def hide_all_panels(self):
        pass

    def query_one(self, *a, **kw):
        return type("W", (), {"remove_class": lambda s, c: None, "add_class": lambda s, c: None})()

    # -- GameFlowMixin stubs -----------------------------------------------

    def exit(self, *a, **kw):
        self._calls["exit"] = True

    def show_main_menu(self, output):
        self._calls["show_main_menu"] = True

    def _refresh_subtitle(self):
        pass

    def show_location_arrival(self, output, is_load=False):
        pass

    def ensure_battle_ready(self, p):
        pass

    def move_to_location(self, loc, output):
        pass

    def enter_building(self, bld, output):
        pass

    def choose_starter_pokemon(self, name, output):
        pass

    def handle_heal_center_confirmation(self, resp, output):
        pass

    def handle_heal_mom_confirmation(self, resp, output):
        pass

    def _handle_pokemon_center_command(self, cmd, output):
        pass

    def process_battle_command(self, cmd, output):
        pass

    def execute_player_move(self, cmd, output):
        pass

    def process_shop_command(self, cmd, output):
        pass

    def execute_switch(self, target, output):
        pass

    def execute_faint_switch(self, target, output):
        pass

    def _return_to_pokemon_center(self, output):
        pass

    def _resume_after_evolution(self, output):
        pass

    def save_current_game(self, output):
        pass

    def show_main_menu_action_panel(self):
        pass

    def show_name_selection_panel(self):
        pass

    def show_load_game_panel(self, saves):
        pass

    def show_save_option_panel(self, save_name=None):
        pass

    def show_confirmation_panel(self, *a, **kw):
        pass

    def show_load_game_action_panel(self):
        pass

    def show_choose_lead_panel(self, non_fainted):
        pass

    def hide_choose_lead_panel(self):
        pass


@pytest.fixture
def term():
    return MockChooseLeadTerminal()


@pytest.fixture
def output():
    return MockRichLog()


# ===========================================================================
# _show_lead_selection_prompt — BattleMixin
# ===========================================================================


class TestShowLeadSelectionPrompt:
    def test_single_fighter_wild_triggers_immediately(self, term, output):
        """When only 1 Pokemon can fight, skip selection and start battle."""
        pikachu = _make_pokemon("Pikachu")
        term.game_state.game_data["pokemon"] = [pikachu]
        term.game_state.current_location = term.game_state.current_location  # already set

        triggered = []
        term._do_trigger_wild_encounter = lambda out: triggered.append("wild")

        term._show_lead_selection_prompt(output, battle_type="wild")

        assert triggered == ["wild"]
        assert term.pending_command != "choose_lead"

    def test_single_alive_among_fainted_triggers_immediately(self, term, output):
        """First Pokemon fainted but second is alive — still auto-selects the alive one."""
        fainted = _make_pokemon("Rattata", hp=0)
        alive = _make_pokemon("Pidgey")
        term.game_state.game_data["pokemon"] = [fainted, alive]

        triggered = []
        term._do_trigger_wild_encounter = lambda out: triggered.append("wild")

        term._show_lead_selection_prompt(output, battle_type="wild")

        assert triggered == ["wild"]
        assert term.pending_command != "choose_lead"

    def test_multiple_fighters_sets_pending_command(self, term, output):
        """Multiple non-fainted Pokemon → pending_command = 'choose_lead'."""
        term.game_state.game_data["pokemon"] = [
            _make_pokemon("Pikachu"),
            _make_pokemon("Charmander"),
        ]

        term._show_lead_selection_prompt(output, battle_type="wild")

        assert term.pending_command == "choose_lead"
        assert term.pending_command_data["battle_type"] == "wild"

    def test_multiple_fighters_writes_party_list(self, term, output):
        """Prompt displays all non-fainted Pokemon with numbers."""
        term.game_state.game_data["pokemon"] = [
            _make_pokemon("Pikachu"),
            _make_pokemon("Squirtle"),
        ]

        term._show_lead_selection_prompt(output, battle_type="wild")

        assert any("Pikachu" in line for line in output.lines)
        assert any("Squirtle" in line for line in output.lines)
        assert any("1." in line for line in output.lines)
        assert any("2." in line for line in output.lines)
        assert not any("or 'cancel'" in line.lower() for line in output.lines)

    def test_wild_prompt_mentions_run_instead_of_cancel(self, term, output):
        """Wild lead prompt teaches run mechanic rather than canceling."""
        term.game_state.game_data["pokemon"] = [
            _make_pokemon("Pikachu"),
            _make_pokemon("Squirtle"),
        ]

        term._show_lead_selection_prompt(output, battle_type="wild")

        assert any("use 'run'" in line.lower() for line in output.lines)

    def test_trainer_prompt_mentions_must_choose(self, term, output):
        """Trainer lead prompt states that selection is required."""
        trainer = {"name": "Brock", "pokemon": [], "prize": 100}
        term.game_state.game_data["pokemon"] = [
            _make_pokemon("Pikachu"),
            _make_pokemon("Squirtle"),
        ]

        term._show_lead_selection_prompt(output, battle_type="trainer", trainer=trainer)

        assert any("require you to choose" in line.lower() for line in output.lines)

    def test_fainted_pokemon_excluded_from_list(self, term, output):
        """Fainted Pokemon are not shown in the selection list."""
        fainted = _make_pokemon("Rattata", hp=0)
        alive = _make_pokemon("Pikachu")
        alive2 = _make_pokemon("Bulbasaur")
        term.game_state.game_data["pokemon"] = [fainted, alive, alive2]

        term._show_lead_selection_prompt(output, battle_type="wild")

        assert not any("Rattata" in line for line in output.lines)
        assert any("Pikachu" in line for line in output.lines)
        assert any("Bulbasaur" in line for line in output.lines)

    def test_trainer_stores_trainer_in_pending_data(self, term, output):
        """Trainer dict is stored in pending_command_data for later use."""
        trainer = {"name": "Brock", "pokemon": [], "prize": 100}
        term.game_state.game_data["pokemon"] = [
            _make_pokemon("Pikachu"),
            _make_pokemon("Charmander"),
        ]

        term._show_lead_selection_prompt(output, battle_type="trainer", trainer=trainer)

        assert term.pending_command_data["battle_type"] == "trainer"
        assert term.pending_command_data["trainer"] is trainer

    def test_single_trainer_fight_triggers_immediately(self, term, output):
        """Single alive Pokemon triggers trainer battle without selection."""
        trainer = {"name": "Brock", "pokemon": [], "prize": 100}
        term.game_state.game_data["pokemon"] = [_make_pokemon("Pikachu")]

        triggered = []
        term._do_trigger_trainer_encounter = lambda out, tr: triggered.append(tr)

        term._show_lead_selection_prompt(output, battle_type="trainer", trainer=trainer)

        assert triggered == [trainer]


# ===========================================================================
# trigger_wild_encounter / trigger_trainer_encounter delegation
# ===========================================================================


class TestTriggerDelegation:
    def test_trigger_wild_delegates_to_prompt(self, term, output):
        """trigger_wild_encounter calls _show_lead_selection_prompt."""
        term.game_state.game_data["pokemon"] = [
            _make_pokemon("Pikachu"),
            _make_pokemon("Bulbasaur"),
        ]
        term.trigger_wild_encounter(output)
        assert term.pending_command == "choose_lead"
        assert term.pending_command_data["battle_type"] == "wild"

    def test_trigger_trainer_delegates_to_prompt(self, term, output):
        """trigger_trainer_encounter calls _show_lead_selection_prompt."""
        trainer = {"name": "Gary", "pokemon": [], "prize": 200}
        term.game_state.game_data["pokemon"] = [
            _make_pokemon("Pikachu"),
            _make_pokemon("Bulbasaur"),
        ]
        term.trigger_trainer_encounter(output, trainer)
        assert term.pending_command == "choose_lead"
        assert term.pending_command_data["battle_type"] == "trainer"
        assert term.pending_command_data["trainer"] is trainer


# ===========================================================================
# _handle_choose_lead — GameFlowMixin
# ===========================================================================


class TestHandleChooseLead:
    def _setup_two_pokemon(self, term) -> tuple:
        """Add two alive Pokemon and return (pikachu, charmander) dicts."""
        pikachu = _make_pokemon("Pikachu")
        charmander = _make_pokemon("Charmander")
        term.game_state.game_data["pokemon"] = [pikachu, charmander]
        return pikachu, charmander

    def test_cancel_wild_reprompts_and_keeps_state(self, term, output):
        """Wild lead selection cannot be canceled; player is told to use run later."""
        triggered = []
        term._do_trigger_wild_encounter = lambda out: triggered.append("wild")
        self._setup_two_pokemon(term)
        term.pending_command_data = {"battle_type": "wild"}

        term._handle_choose_lead("cancel", output)

        assert triggered == []
        assert term.pending_command == "choose_lead"
        assert term.pending_command_data.get("battle_type") == "wild"
        assert any("use [bold]run[/bold]" in line.lower() for line in output.lines)

    def test_back_wild_also_reprompts(self, term, output):
        """'back' is treated like cancel and does not exit wild lead selection."""
        triggered = []
        term._do_trigger_wild_encounter = lambda out: triggered.append("wild")
        self._setup_two_pokemon(term)
        term.pending_command_data = {"battle_type": "wild"}

        term._handle_choose_lead("back", output)

        assert triggered == []
        assert term.pending_command == "choose_lead"

    def test_cancel_trainer_reprompts_and_blocks_cancel(self, term, output):
        """Trainer lead selection cannot be canceled."""
        trainer = {"name": "Misty", "pokemon": [], "prize": 300}
        self._setup_two_pokemon(term)
        term.pending_command_data = {"battle_type": "trainer", "trainer": trainer}

        term._handle_choose_lead("cancel", output)

        assert term.pending_command == "choose_lead"
        assert term.pending_command_data.get("battle_type") == "trainer"
        assert any("can't cancel" in line.lower() for line in output.lines)

    def test_non_digit_input_reprompts(self, term, output):
        """Non-numeric input sets pending_command back to 'choose_lead'."""
        self._setup_two_pokemon(term)
        term.pending_command_data = {"battle_type": "wild"}

        term._handle_choose_lead("pikachu", output)

        assert term.pending_command == "choose_lead"
        assert any("number" in line.lower() for line in output.lines)

    def test_out_of_range_reprompts(self, term, output):
        """Number outside 1-N re-prompts."""
        self._setup_two_pokemon(term)
        term.pending_command_data = {"battle_type": "wild"}

        term._handle_choose_lead("5", output)

        assert term.pending_command == "choose_lead"

    def test_choose_first_no_swap(self, term, output):
        """Choosing slot 1 (already the lead) triggers battle without swapping."""
        pikachu, charmander = self._setup_two_pokemon(term)
        term.pending_command_data = {"battle_type": "wild"}

        triggered = []
        term._do_trigger_wild_encounter = lambda out: triggered.append("wild")

        term._handle_choose_lead("1", output)

        assert triggered == ["wild"]
        # Party order unchanged
        party = term.game_state.game_data["pokemon"]
        assert party[0] is pikachu
        assert party[1] is charmander

    def test_choose_second_swaps_to_front(self, term, output):
        """Choosing slot 2 swaps that Pokemon into the lead position."""
        pikachu, charmander = self._setup_two_pokemon(term)
        term.pending_command_data = {"battle_type": "wild"}

        triggered = []
        term._do_trigger_wild_encounter = lambda out: triggered.append("wild")

        term._handle_choose_lead("2", output)

        assert triggered == ["wild"]
        party = term.game_state.game_data["pokemon"]
        assert party[0] is charmander
        assert party[1] is pikachu

    def test_go_message_uses_chosen_name(self, term, output):
        """Output confirms the chosen Pokemon with a 'Go!' message."""
        self._setup_two_pokemon(term)
        term.pending_command_data = {"battle_type": "wild"}
        term._do_trigger_wild_encounter = lambda out: None

        term._handle_choose_lead("2", output)

        assert any("Charmander" in line for line in output.lines)

    def test_trainer_battle_triggers_trainer_encounter(self, term, output):
        """Trainer battles call _do_trigger_trainer_encounter with the trainer."""
        pikachu, charmander = self._setup_two_pokemon(term)
        trainer = {"name": "Misty", "pokemon": [], "prize": 300}
        term.pending_command_data = {"battle_type": "trainer", "trainer": trainer}

        triggered = []
        term._do_trigger_trainer_encounter = lambda out, tr: triggered.append(tr)

        term._handle_choose_lead("1", output)

        assert triggered == [trainer]

    def test_choose_with_fainted_at_front(self, term, output):
        """Fainted Pokemon at front is skipped; selection is among non-fainted."""
        fainted = _make_pokemon("Rattata", hp=0)
        pikachu = _make_pokemon("Pikachu")
        charmander = _make_pokemon("Charmander")
        term.game_state.game_data["pokemon"] = [fainted, pikachu, charmander]
        term.pending_command_data = {"battle_type": "wild"}

        triggered = []
        term._do_trigger_wild_encounter = lambda out: triggered.append("wild")

        # Choose slot 2 among non-fainted → Charmander
        term._handle_choose_lead("2", output)

        assert triggered == ["wild"]
        party = term.game_state.game_data["pokemon"]
        # Charmander should now be in the first non-fainted slot (index 1, after fainted)
        assert party[1] is charmander
        assert party[2] is pikachu


# ===========================================================================
# handle_pending_command dispatch ("choose_lead" token)
# ===========================================================================


class TestHandlePendingCommandChooseLead:
    def test_dispatches_to_handle_choose_lead(self, term, output):
        """handle_pending_command routes 'choose_lead' to _handle_choose_lead."""
        term.game_state.game_data["pokemon"] = [
            _make_pokemon("Pikachu"),
            _make_pokemon("Bulbasaur"),
        ]
        term.pending_command = "choose_lead"
        term.pending_command_data = {"battle_type": "wild"}

        triggered = []
        term._do_trigger_wild_encounter = lambda out: triggered.append("wild")

        term.handle_pending_command("1", output)

        assert triggered == ["wild"]

    def test_invalid_input_keeps_pending_command(self, term, output):
        """Invalid input during choose_lead re-sets pending_command for re-prompt."""
        term.game_state.game_data["pokemon"] = [
            _make_pokemon("Pikachu"),
            _make_pokemon("Bulbasaur"),
        ]
        term.pending_command = "choose_lead"
        term.pending_command_data = {"battle_type": "wild"}

        term.handle_pending_command("xyz", output)

        assert term.pending_command == "choose_lead"
        # pending_command_data must survive the re-prompt
        assert term.pending_command_data.get("battle_type") == "wild"
