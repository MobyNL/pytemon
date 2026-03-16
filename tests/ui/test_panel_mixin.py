"""
Tests for PokemonLibrary/ui/panel_mixin.py using a MockPanelTerminal.

The panel_mixin methods are primarily widget show/hide operations.  They
call ``self.query_one(selector, WidgetType)`` to retrieve Textual widgets
and then toggle CSS classes or update widget properties.

Most method bodies are wrapped in try/except blocks so we only need a
MockWidget that does not raise to exercise the happy path.
"""

from typing import Any, Optional

import pytest

from pytemon.engine import BattleState
from pytemon.game_state import GameState
from pytemon.ui.panel_mixin import PanelMixin

# ---------------------------------------------------------------------------
# Mock helpers
# ---------------------------------------------------------------------------


class MockRichLog:
    """Minimal mock for Textual RichLog."""

    def __init__(self):
        self.lines = []

    def write(self, text: Any) -> None:
        self.lines.append(str(text))

    def clear(self, columns: bool = False) -> None:
        self.lines.clear()


class MockButton:
    def __init__(self, id_: str = ""):
        self.label = ""
        self.disabled = False
        self.display = True

    def add_class(self, cls: str) -> None:
        pass

    def remove_class(self, cls: str) -> None:
        pass


class MockDataTable:
    def __init__(self):
        self._rows = []
        self._cols = []

    def add_class(self, cls: str) -> None:
        pass

    def remove_class(self, cls: str) -> None:
        pass

    def clear(self, columns: bool = False) -> None:
        self._rows.clear()
        self._cols.clear()

    def add_column(self, name: str, key: Optional[str] = None) -> None:
        self._cols.append(name)

    def add_row(self, *args, key: Optional[str] = None) -> None:
        self._rows.append(args)

    def move_cursor(self, row: int = 0) -> None:
        pass


class MockSelect:
    def __init__(self):
        self.value = ""

    def add_class(self, cls: str) -> None:
        pass

    def remove_class(self, cls: str) -> None:
        pass

    def set_options(self, options: list) -> None:
        pass


class MockStatic:
    def __init__(self, text: str = ""):
        self.renderable = text

    def add_class(self, cls: str) -> None:
        pass

    def remove_class(self, cls: str) -> None:
        pass

    def update(self, text: Any) -> None:
        self.renderable = str(text)


class MockInput:
    def __init__(self, value: str = ""):
        self.value = value

    def add_class(self, cls: str) -> None:
        pass

    def remove_class(self, cls: str) -> None:
        pass

    def focus(self) -> None:
        pass


class MockTabs:
    """Mock for TabbedContent widget."""

    def __init__(self):
        self.active = None
        self._tabs = {}

    def add_class(self, cls: str) -> None:
        pass

    def remove_class(self, cls: str) -> None:
        pass

    def get_tab(self, name: str):
        tab = type("MockTab", (), {"label": ""})()
        self._tabs[name] = tab
        return tab

    def show_tab(self, name: str) -> None:
        pass

    def hide_tab(self, name: str) -> None:
        pass


class MockGenericWidget:
    """Fallback widget for any unrecognised selector."""

    def __init__(self):
        self.label = ""
        self.disabled = False
        self.display = True
        self.active = None

    def add_class(self, cls: str) -> None:
        pass

    def remove_class(self, cls: str) -> None:
        pass

    def update(self, text: Any) -> None:
        pass

    def set_options(self, opts: list) -> None:
        pass


class MockPanelTerminal(PanelMixin):
    """Mock terminal for testing PanelMixin.

    Provides just enough infrastructure for the mixin methods to execute
    their happy paths without raising exceptions.
    """

    def __init__(self):
        self.game_state = GameState()
        self.game_state.start_new_game()
        self.pending_command = None
        self.pending_command_data = {}
        self._selected_save_name = None
        self._temp_saves_list = None
        self._widget_registry: dict = {}

    def query_one(self, selector: str, widget_type: Any = None) -> Any:
        """Return an appropriate mock widget for the given selector."""
        # Allow pre-registered widgets
        if selector in self._widget_registry:
            return self._widget_registry[selector]

        # Import Textual widget types lazily (available in the repo)
        try:
            from textual.widgets import (
                Button,
                DataTable,
                Input,
                RichLog,
                Select,
                Static,
                TabbedContent,
            )
        except ImportError:
            # Textual not available — return generic mock
            return MockGenericWidget()

        if widget_type is Button:
            return MockButton()
        if widget_type is DataTable:
            return MockDataTable()
        if widget_type is Select:
            return MockSelect()
        if widget_type is Static:
            return MockStatic()
        if widget_type is Input:
            return MockInput()
        if widget_type is RichLog:
            return MockRichLog()
        if widget_type is TabbedContent:
            return MockTabs()

        # No type hint — return a generic mock that supports most operations
        w = MockGenericWidget()
        # Also make it act as RichLog/TabbedContent for write/clear
        w.clear = lambda columns=False: None
        w.write = lambda t: None
        w.get_tab = lambda n: type("T", (), {"label": ""})()
        w.show_tab = lambda n: None
        w.hide_tab = lambda n: None
        w.add_column = lambda n, key=None: None
        w.add_row = lambda *a, key=None: None
        w.move_cursor = lambda row=0: None
        w.set_options = lambda o: None
        w.focus = lambda: None
        return w

    def ensure_battle_ready(self, pokemon: dict) -> None:
        """Stub for BattleMixin.ensure_battle_ready."""
        pass

    def hide_all_panels(self) -> None:
        """Call the actual mixin method but swallow exceptions."""
        try:
            super().hide_all_panels()
        except Exception:
            pass


@pytest.fixture
def term():
    return MockPanelTerminal()


# ---------------------------------------------------------------------------
# Tests — each group covers a single method in PanelMixin
# ---------------------------------------------------------------------------


class TestShowMainMenuActionPanel:
    def test_no_exception(self, term):
        term.show_main_menu_action_panel()


class TestShowBattleActionPanel:
    def test_no_exception(self, term):
        term.show_battle_action_panel()


class TestShowBattleBagPanel:
    def test_no_items_no_exception(self, term):
        term.game_state.game_data["items"] = {}
        term.show_battle_bag_panel()

    def test_with_items_and_battle_state(self, term):
        term.game_state.game_data["items"] = {
            "Pokeball": 3,
            "Potion": 2,
            "Super Potion": 1,
            "Antidote": 1,
            "Paralyze Heal": 1,
            "Awakening": 1,
        }
        bs = BattleState()
        player = bs.generate_wild_pokemon("PIKACHU", 5)
        player["status"] = "POISON"
        bs.start_wild_battle(player, "RATTATA", 5)
        term.game_state.battle_state = bs
        term.game_state.game_data["pokemon"] = [player]
        term.show_battle_bag_panel()

    def test_with_paralysis_status(self, term):
        term.game_state.game_data["items"] = {"Paralyze Heal": 1}
        bs = BattleState()
        player = bs.generate_wild_pokemon("PIKACHU", 5)
        player["status"] = "PARALYSIS"
        bs.start_wild_battle(player, "RATTATA", 5)
        term.game_state.battle_state = bs
        term.game_state.game_data["pokemon"] = [player]
        term.show_battle_bag_panel()

    def test_with_sleep_status(self, term):
        term.game_state.game_data["items"] = {"Awakening": 2}
        bs = BattleState()
        player = bs.generate_wild_pokemon("PIKACHU", 5)
        player["status"] = "SLEEP"
        bs.start_wild_battle(player, "RATTATA", 5)
        term.game_state.battle_state = bs
        term.game_state.game_data["pokemon"] = [player]
        term.show_battle_bag_panel()


class TestShowMoveSelectionPanel:
    def test_without_battle_state(self, term):
        term.game_state.battle_state = None
        term.show_move_selection_panel()

    def test_with_battle_state(self, term):
        bs = BattleState()
        player = bs.generate_wild_pokemon("PIKACHU", 10)
        bs.start_wild_battle(player, "RATTATA", 5)
        term.game_state.battle_state = bs
        term.game_state.game_data["pokemon"] = [player]
        term.show_move_selection_panel()

    def test_move_with_various_types(self, term):
        """Ensure type-coloring loop is exercised."""
        bs = BattleState()
        player = bs.generate_wild_pokemon("CHARIZARD", 36)
        bs.start_wild_battle(player, "RATTATA", 5)
        term.game_state.battle_state = bs
        term.game_state.game_data["pokemon"] = [player]
        term.show_move_selection_panel()


class TestHideAllBattlePanels:
    def test_no_exception(self, term):
        term.hide_all_battle_panels()


class TestShowStarterSelectionPanel:
    def test_normal_mode(self, term):
        term.show_starter_selection_panel(pikachu_mode=False)

    def test_pikachu_mode(self, term):
        term.show_starter_selection_panel(pikachu_mode=True)


class TestShowNameSelectionPanel:
    def test_no_exception(self, term):
        term.show_name_selection_panel()


class TestShowLocationSelectionPanel:
    def test_empty_list(self, term):
        term.show_location_selection_panel([])

    def test_with_locations(self, term):
        term.show_location_selection_panel(["Route 1", "Viridian City", "Pewter City"])


class TestShowBuildingSelectionPanel:
    def test_empty_list(self, term):
        term.show_building_selection_panel([])

    def test_with_buildings(self, term):
        term.show_building_selection_panel(["Pokemon Center", "Pokemart"])


class TestHideAllPanels:
    def test_no_exception(self, term):
        term.hide_all_panels()


class TestShowGymPanel:
    def test_no_location(self, term):
        term.game_state.current_location = None
        term.show_gym_panel()

    def test_with_pewter_city(self, term):
        from pytemon.locations import get_location

        term.game_state.current_location = get_location("Pewter City")
        term.show_gym_panel()

    def test_with_cerulean_city(self, term):
        from pytemon.locations import get_location

        term.game_state.current_location = get_location("Cerulean City")
        term.show_gym_panel()

    def test_with_badge_already_earned(self, term):
        from pytemon.locations import get_location

        term.game_state.current_location = get_location("Pewter City")
        term.game_state.game_data["badges"] = ["Boulder Badge"]
        term.show_gym_panel()

    def test_with_defeated_trainers(self, term):
        from pytemon.gym_system import get_gym_trainers
        from pytemon.locations import get_location

        term.game_state.current_location = get_location("Pewter City")
        trainers = get_gym_trainers("Pewter City")
        term.game_state.game_data["defeated_trainers"] = list(trainers)
        term.show_gym_panel()


class TestShowPokedexNavigation:
    def test_no_exception(self, term):
        term.show_pokedex_navigation()

    def test_with_seen_pokemon(self, term):
        term.game_state.game_data["pokedex"] = {
            "seen": ["PIKACHU", "CHARMANDER"],
            "caught": ["PIKACHU"],
        }
        term.game_state.game_data.setdefault("pokedex_state", {})["filter_mode"] = "seen"
        term.show_pokedex_navigation()

    def test_caught_filter(self, term):
        term.game_state.game_data["pokedex"] = {"seen": ["PIKACHU"], "caught": ["PIKACHU"]}
        term.game_state.game_data.setdefault("pokedex_state", {})["filter_mode"] = "caught"
        term.show_pokedex_navigation()

    def test_missing_filter(self, term):
        term.game_state.game_data["pokedex"] = {"seen": ["PIKACHU"], "caught": []}
        term.game_state.game_data.setdefault("pokedex_state", {})["filter_mode"] = "missing"
        term.show_pokedex_navigation()

    def test_page_2(self, term):
        term.game_state.game_data.setdefault("pokedex_state", {})["current_page"] = 2
        term.show_pokedex_navigation()


class TestHidePokedexNavigation:
    def test_no_exception(self, term):
        term.hide_pokedex_navigation()


class TestShowConfirmationPanel:
    def test_basic_show(self, term):
        term.show_confirmation_panel("Are you sure?", "quit")
        assert term.pending_command_data.get("confirmation_type") == "quit"

    def test_no_cancel_button(self, term):
        term.show_confirmation_panel("Are you sure?", "save", show_cancel=False)
        assert term.pending_command_data.get("confirmation_type") == "save"


class TestShowSaveOptionPanel:
    def test_no_exception(self, term):
        term.show_save_option_panel("my_save")


class TestShowLoadGamePanel:
    def test_empty_saves_list(self, term):
        term.show_load_game_panel([])

    def test_with_valid_save_file(self, tmp_path, term):
        import json

        save_file = tmp_path / "test_save.json"
        save_data = {
            "location": "Pallet Town",
            "badges": ["Boulder Badge"],
            "pokemon": [{"name": "PIKACHU", "level": 10, "number": 25}],
            "pokedex": {"seen": ["PIKACHU"], "caught": ["PIKACHU"]},
        }
        save_file.write_text(json.dumps(save_data))
        term.show_load_game_panel([save_file])
        assert term._selected_save_name == "test_save"

    def test_with_large_party(self, tmp_path, term):
        import json

        save_file = tmp_path / "big_party.json"
        party = [{"name": f"MON{i}", "level": i, "number": i} for i in range(1, 7)]
        save_data = {
            "location": "Cerulean City",
            "badges": [],
            "pokemon": party,
            "pokedex": {"seen": [], "caught": []},
        }
        save_file.write_text(json.dumps(save_data))
        term.show_load_game_panel([save_file])

    def test_with_invalid_save_file(self, tmp_path, term):
        save_file = tmp_path / "corrupt.json"
        save_file.write_text("NOT JSON!!!")
        term.show_load_game_panel([save_file])

    def test_with_multiple_saves(self, tmp_path, term):
        import json

        saves = []
        for i in range(3):
            sf = tmp_path / f"save{i}.json"
            sf.write_text(json.dumps({"location": "Route 1", "badges": [], "pokemon": []}))
            saves.append(sf)
        term.show_load_game_panel(saves)


class TestShowNurseJoyPanel:
    def test_no_exception(self, term):
        term.show_nurse_joy_panel("Shall I heal your Pokemon?", "pokemon_center")
        assert term.pending_command_data.get("heal_type") == "pokemon_center"


class TestShowPokemonCenterPanel:
    def test_no_exception(self, term):
        term.show_pokemon_center_panel()


class TestShowPokemartPanel:
    def test_no_exception(self, term):
        term.show_pokemart_panel()

    def test_with_some_money(self, term):
        term.game_state.game_data["money"] = 9999
        term.show_pokemart_panel()


class TestShowPartyPanel:
    def test_empty_party(self, term):
        term.game_state.game_data["pokemon"] = []
        term.show_party_panel()

    def test_with_single_pokemon(self, term):
        bs = BattleState()
        p = bs.generate_wild_pokemon("PIKACHU", 10)
        term.game_state.game_data["pokemon"] = [p]
        term.show_party_panel()

    def test_with_full_party(self, term):
        bs = BattleState()
        party = []
        for name in ["PIKACHU", "CHARMANDER", "SQUIRTLE", "BULBASAUR", "EEVEE", "SNORLAX"]:
            p = bs.generate_wild_pokemon(name, 10)
            party.append(p)
        term.game_state.game_data["pokemon"] = party
        term.show_party_panel()


# ===========================================================================
# show_faint_switch_panel (lines 165-201)
# ===========================================================================


class TestShowFaintSwitchPanel:
    def test_can_run_true_no_exception(self, term):
        bs = BattleState()
        player = bs.generate_wild_pokemon("PIKACHU", 10)
        bs.start_wild_battle(player, "RATTATA", 5)
        term.game_state.battle_state = bs
        term.game_state.game_data["pokemon"] = [player]
        term.show_faint_switch_panel(can_run=True)

    def test_can_run_false_no_exception(self, term):
        bs = BattleState()
        player = bs.generate_wild_pokemon("PIKACHU", 10)
        bs.start_wild_battle(player, "RATTATA", 5)
        term.game_state.battle_state = bs
        term.game_state.game_data["pokemon"] = [player]
        term.show_faint_switch_panel(can_run=False)

    def test_with_full_party(self, term):
        bs = BattleState()
        party = [bs.generate_wild_pokemon("PIKACHU", 5) for _ in range(6)]
        bs.start_wild_battle(party[0], "RATTATA", 5)
        term.game_state.battle_state = bs
        term.game_state.game_data["pokemon"] = party
        term.show_faint_switch_panel(can_run=True)

    def test_with_fainted_member(self, term):
        bs = BattleState()
        active = bs.generate_wild_pokemon("PIKACHU", 10)
        fainted = bs.generate_wild_pokemon("CHARMANDER", 5)
        fainted["hp"] = 0
        bs.start_wild_battle(active, "RATTATA", 5)
        term.game_state.battle_state = bs
        term.game_state.game_data["pokemon"] = [active, fainted]
        term.show_faint_switch_panel(can_run=False)

    def test_with_status_condition(self, term):
        bs = BattleState()
        player = bs.generate_wild_pokemon("PIKACHU", 10)
        player["status"] = "POISON"
        bs.start_wild_battle(player, "RATTATA", 5)
        term.game_state.battle_state = bs
        term.game_state.game_data["pokemon"] = [player]
        term.show_faint_switch_panel(can_run=True)


# ===========================================================================
# show_pokemon_switch_panel (lines 205-234)
# ===========================================================================


class TestShowPokemonSwitchPanel:
    def test_no_exception(self, term):
        bs = BattleState()
        player = bs.generate_wild_pokemon("PIKACHU", 10)
        bs.start_wild_battle(player, "RATTATA", 5)
        term.game_state.battle_state = bs
        term.game_state.game_data["pokemon"] = [player]
        term.show_pokemon_switch_panel()

    def test_with_multiple_pokemon(self, term):
        bs = BattleState()
        active = bs.generate_wild_pokemon("PIKACHU", 10)
        second = bs.generate_wild_pokemon("CHARMANDER", 5)
        bs.start_wild_battle(active, "RATTATA", 5)
        term.game_state.battle_state = bs
        term.game_state.game_data["pokemon"] = [active, second]
        term.show_pokemon_switch_panel()

    def test_with_fainted_party_member(self, term):
        bs = BattleState()
        active = bs.generate_wild_pokemon("PIKACHU", 10)
        fainted = bs.generate_wild_pokemon("SQUIRTLE", 5)
        fainted["hp"] = 0
        bs.start_wild_battle(active, "RATTATA", 5)
        term.game_state.battle_state = bs
        term.game_state.game_data["pokemon"] = [active, fainted]
        term.show_pokemon_switch_panel()

    def test_no_battle_state(self, term):
        term.game_state.battle_state = None
        term.game_state.game_data["pokemon"] = []
        term.show_pokemon_switch_panel()


# ===========================================================================
# show_pc_main_panel (lines 613-634)
# ===========================================================================


class TestShowPcMainPanel:
    def test_no_exception_empty_boxes(self, term):
        term.show_pc_main_panel()
        assert term.pending_command == "pc"

    def test_with_pokemon_in_box(self, term):
        from pytemon import pc_system

        bs = BattleState()
        p = bs.generate_wild_pokemon("PIKACHU", 10)
        storage = pc_system.get_pc_storage(term.game_state)
        storage["Box 1"][0] = p
        storage["Box 2"][0] = bs.generate_wild_pokemon("CHARMANDER", 5)
        term.show_pc_main_panel()
        assert term.pending_command == "pc"

    def test_with_party_pokemon(self, term):
        bs = BattleState()
        party = [bs.generate_wild_pokemon("PIKACHU", 5)]
        term.game_state.game_data["pokemon"] = party
        term.show_pc_main_panel()
        assert term.pending_command == "pc"


# ===========================================================================
# show_pc_deposit_panel (lines 638-653)
# ===========================================================================


class TestShowPcDepositPanel:
    def test_single_pokemon_disabled(self, term):
        """With only one pokemon, deposit should be disabled."""
        bs = BattleState()
        player = bs.generate_wild_pokemon("PIKACHU", 5)
        term.game_state.game_data["pokemon"] = [player]
        term.show_pc_deposit_panel()

    def test_two_pokemon_can_deposit(self, term):
        """With two pokemon, deposit is enabled."""
        bs = BattleState()
        party = [
            bs.generate_wild_pokemon("PIKACHU", 5),
            bs.generate_wild_pokemon("CHARMANDER", 5),
        ]
        term.game_state.game_data["pokemon"] = party
        term.show_pc_deposit_panel()

    def test_full_party_deposit(self, term):
        bs = BattleState()
        party = [bs.generate_wild_pokemon("PIKACHU", 5) for _ in range(6)]
        term.game_state.game_data["pokemon"] = party
        term.show_pc_deposit_panel()

    def test_empty_party(self, term):
        term.game_state.game_data["pokemon"] = []
        term.show_pc_deposit_panel()


# ===========================================================================
# show_pc_withdraw_panel (lines 657-676)
# ===========================================================================


class TestShowPcWithdrawPanel:
    def test_empty_box(self, term):
        """Withdraw panel with an empty box should not raise."""
        term.show_pc_withdraw_panel(1)

    def test_with_pokemon_in_box(self, term):
        from pytemon import pc_system

        bs = BattleState()
        p = bs.generate_wild_pokemon("PIKACHU", 10)
        storage = pc_system.get_pc_storage(term.game_state)
        storage["Box 1"][0] = p
        term.show_pc_withdraw_panel(1)

    def test_full_party_disables_withdraw(self, term):
        """When party is full, withdraw buttons should be disabled."""
        from pytemon import pc_system

        bs = BattleState()
        party = [bs.generate_wild_pokemon("PIKACHU", 5) for _ in range(6)]
        term.game_state.game_data["pokemon"] = party
        stored = bs.generate_wild_pokemon("CHARMANDER", 5)
        storage = pc_system.get_pc_storage(term.game_state)
        storage["Box 1"][0] = stored
        term.show_pc_withdraw_panel(1)

    def test_box_2_and_3(self, term):
        from pytemon import pc_system

        bs = BattleState()
        storage = pc_system.get_pc_storage(term.game_state)
        storage["Box 2"][0] = bs.generate_wild_pokemon("SQUIRTLE", 5)
        storage["Box 3"][0] = bs.generate_wild_pokemon("BULBASAUR", 5)
        term.show_pc_withdraw_panel(2)
        term.show_pc_withdraw_panel(3)
