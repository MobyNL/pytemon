"""
PokemonLibraryTest — headless Robot Framework test-support library.

Runs the Textual ``PokemonTerminal`` app in headless mode inside a
background asyncio event loop so that synchronous Robot Framework keywords
can drive the full application stack.

Lifecycle (must appear in every suite):
    Suite Setup        Open Pokemon Terminal
    Suite Teardown     Close Pokemon Terminal

All state-setter keywords are safe to call between test cases because each
test's ``[Setup]`` calls ``Bootstrap Game`` (directly or via a common.resource
helper), which resets the app to a clean game state.
"""

import asyncio
import shutil
import tempfile
import threading
from pathlib import Path
from typing import Optional

from robot.api import logger
from robot.api.deco import keyword


class PokemonLibraryTest:
    """Headless Robot Framework test library for PokemonTerminal."""

    ROBOT_LIBRARY_SCOPE = "SUITE"

    def __init__(self):
        self._app = None
        self._pilot = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._ready_event: Optional[threading.Event] = None
        self._stop_event = None  # asyncio.Event — created inside the loop
        self._last_output: str = ""
        self._tmp_saves_dir: Optional[str] = None

    # ── Private helpers ─────────────────────────────────────────────────────

    def _run_async(self, coro, timeout: int = 30):
        """Submit *coro* to the app event loop and block until it finishes."""
        if self._loop is None:
            raise RuntimeError(
                "Pokemon Terminal is not running. "
                "Call 'Open Pokemon Terminal' (Suite Setup) first."
            )
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result(timeout=timeout)

    def _capture_output(self):
        """Snapshot the current ``#output`` RichLog into ``self._last_output``."""
        from textual.widgets import RichLog

        output = self._app.query_one("#output", RichLog)
        lines = ["".join(seg.text for seg in strip) for strip in output.lines]
        self._last_output = "\n".join(lines)

    def _run_app_loop(self):
        """Background thread: owns the asyncio event loop and Textual app."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._app_session())
        finally:
            self._loop.close()
            self._loop = None

    async def _app_session(self):
        """Keep the Textual app alive until ``Close Pokemon Terminal`` is called."""
        from pytemon.terminal import PokemonTerminal

        self._app = PokemonTerminal()
        self._stop_event = asyncio.Event()
        # Redirect saves_dir to an isolated empty temp directory so that the app
        # never finds existing save files (avoids overwrite-confirmation prompts).
        self._tmp_saves_dir = tempfile.mkdtemp(prefix="pokemon_test_saves_")
        self._app.game_state.saves_dir = Path(self._tmp_saves_dir)
        async with self._app.run_test(headless=True) as pilot:
            self._pilot = pilot
            self._ready_event.set()
            await self._stop_event.wait()

    async def _do_stop(self):
        self._stop_event.set()

    # ── Lifecycle ────────────────────────────────────────────────────────────

    @keyword("Open Pokemon Terminal")
    def open_pokemon_terminal(self):
        """Start the headless PokemonTerminal app. Use as ``Suite Setup``."""
        self._ready_event = threading.Event()
        self._thread = threading.Thread(target=self._run_app_loop, daemon=True)
        self._thread.start()
        if not self._ready_event.wait(timeout=30):
            raise RuntimeError("Timed out waiting for PokemonTerminal to start (30 s).")
        # Capture the initial main-menu output so Output Should Contain works immediately.
        self._run_async(self._do_initial_capture())
        logger.info("PokemonTerminal started in headless mode.")

    async def _do_initial_capture(self):
        await self._pilot.pause()
        self._capture_output()

    @keyword("Close Pokemon Terminal")
    def close_pokemon_terminal(self):
        """Stop the headless PokemonTerminal app. Use as ``Suite Teardown``."""
        if self._loop and self._stop_event:
            asyncio.run_coroutine_threadsafe(self._do_stop(), self._loop).result(timeout=10)
        if self._thread:
            self._thread.join(timeout=15)
        self._app = None
        self._pilot = None
        self._thread = None
        self._loop = None
        if self._tmp_saves_dir:
            shutil.rmtree(self._tmp_saves_dir, ignore_errors=True)
            self._tmp_saves_dir = None
        logger.info("PokemonTerminal stopped.")

    # ── Game bootstrap ───────────────────────────────────────────────────────

    @keyword("Bootstrap Game")
    def bootstrap_game(self, location: str = "Pallet Town", player_name: str = "Ash"):
        """
        Reset the app to a clean game state.

        Sets up a fresh game with SQUIRTLE as the starter at the given
        *location* (default ``Pallet Town``) and *player_name* (default ``Ash``).

        Use this as ``[Setup]`` directly or through one of the helper keywords
        in ``resources/common.resource``.
        """
        self._run_async(self._do_bootstrap(location, player_name))

    async def _do_bootstrap(self, location: str, player_name: str):
        from pytemon.engine import BattleState
        from pytemon.locations import get_location
        from textual.widgets import RichLog

        gs = self._app.game_state
        gs.start_new_game()
        gs.game_data["player_name"] = player_name
        gs.game_data["location"] = location
        loc = get_location(location)
        if loc:
            gs.current_location = loc

        # Reset transient battle / pending state
        gs.in_battle = False
        gs.battle_state = None
        self._app.pending_command = None
        self._app.pending_command_data = {}

        # Default starter party
        bs = BattleState()
        starter = bs.generate_wild_pokemon("SQUIRTLE", 10)
        gs.game_data["pokemon"] = [starter]
        gs.game_data["pokedex"]["seen"] = ["SQUIRTLE"]
        gs.game_data["pokedex"]["caught"] = ["SQUIRTLE"]

        output = self._app.query_one("#output", RichLog)
        output.clear()
        self._last_output = ""
        await self._pilot.pause()

    # ── Command execution ────────────────────────────────────────────────────

    @keyword("Type Command")
    def type_command(self, command: str):
        """
        Execute *command* in the terminal and capture its output.

        Routes through the same logic as the real input handler:
        - active pending state  → ``handle_pending_command``
        - main menu             → ``process_menu_command``
        - in-game               → ``process_command``
        """
        self._run_async(self._do_command(command))

    async def _do_command(self, command: str):
        from textual.widgets import RichLog

        output = self._app.query_one("#output", RichLog)
        output.clear()

        if self._app.pending_command:
            self._app.handle_pending_command(command, output)
        elif self._app.game_state.in_menu:
            self._app.process_menu_command(command, output)
        else:
            self._app.process_command(command, output)

        await self._pilot.pause()
        self._capture_output()

    # ── Output / UI assertions ───────────────────────────────────────────────

    @keyword("Output Should Contain")
    def output_should_contain(self, text: str, case_insensitive: bool = False):
        """
        Fail if the last command's output does not contain *text*.

        Arguments:
        - ``text``: Expected substring.
        - ``case_insensitive``: Set to ``True`` for a case-insensitive check.
        """
        haystack = self._last_output
        needle = text
        if str(case_insensitive).lower() in ("true", "yes", "1"):
            haystack = haystack.lower()
            needle = needle.lower()
        if needle not in haystack:
            raise AssertionError(
                f"Output did not contain '{text}'.\n\nActual output:\n{self._last_output}"
            )

    @keyword("Widget Should Be Visible")
    def widget_should_be_visible(self, locator: str):
        """
        Fail if the widget identified by *locator* is not currently visible.

        *locator* may be ``id=some-id`` or any valid CSS selector.
        """
        visible = self._run_async(self._check_widget_visible(locator))
        if not visible:
            raise AssertionError(f"Widget '{locator}' is not visible.")

    async def _check_widget_visible(self, locator: str) -> bool:
        selector = f"#{locator[3:]}" if locator.startswith("id=") else locator
        try:
            widget = self._app.query_one(selector)
            return bool(widget.display)
        except Exception:
            return False

    @keyword("Click Widget")
    def click_widget(self, locator: str):
        """
        Click the widget identified by *locator* and capture output.

        *locator* may be ``id=some-id`` or any valid CSS selector.
        """
        self._run_async(self._do_click(locator))

    async def _do_click(self, locator: str):
        selector = f"#{locator[3:]}" if locator.startswith("id=") else locator
        await self._pilot.click(selector)
        await self._pilot.pause()
        self._capture_output()

    @keyword("Badge Count Should Be")
    def badge_count_should_be(self, expected):
        """Fail if the player does not have exactly *expected* badges."""
        badges = self._app.game_state.game_data.get("badges", [])
        count = len(badges) if isinstance(badges, list) else 0
        if count != int(expected):
            raise AssertionError(f"Expected {expected} badge(s) but got {count}.")

    @keyword("Item Count Should Be")
    def item_count_should_be(self, item_name: str, expected):
        """Fail if the bag does not hold exactly *expected* of *item_name*."""
        items = self._app.game_state.game_data.get("items", {})
        count = items.get(item_name, 0)
        if count != int(expected):
            raise AssertionError(
                f"Expected {expected}x '{item_name}' but bag has {count}x."
            )

    @keyword("Money Should Be")
    def money_should_be(self, expected):
        """Fail if the player's money does not equal *expected*."""
        money = self._app.game_state.game_data.get("money", 0)
        if money != int(expected):
            raise AssertionError(f"Expected ₽{expected} but got ₽{money}.")

    @keyword("Party Pokemon Should Be")
    def party_pokemon_should_be(self, index, species: str):
        """Fail if the party Pokémon at *index* (0-based) is not *species*."""
        party = self._app.game_state.game_data.get("pokemon", [])
        idx = int(index)
        if idx >= len(party):
            raise AssertionError(f"No Pokémon at party index {idx} (party size {len(party)}).")
        actual = str(party[idx].get("name", "")).upper()
        if actual != species.upper():
            raise AssertionError(
                f"Expected {species.upper()} at party[{idx}] but got {actual}."
            )

    @keyword("Party Pokemon Level Should Be")
    def party_pokemon_level_should_be(self, index, expected_level):
        """Fail if the party Pokémon at *index* (0-based) does not have *expected_level*."""
        party = self._app.game_state.game_data.get("pokemon", [])
        idx = int(index)
        if idx >= len(party):
            raise AssertionError(f"No Pokémon at party index {idx} (party size {len(party)}).")
        actual = party[idx].get("level", 0)
        if actual != int(expected_level):
            raise AssertionError(
                f"Expected level {expected_level} at party[{idx}] but got {actual}."
            )

    @keyword("Should Be In Battle")
    def should_be_in_battle(self):
        """Fail if the game is not currently in a battle."""
        if not self._app.game_state.in_battle:
            raise AssertionError("Expected to be in battle but the game is NOT in battle state.")

    @keyword("Should Not Be In Battle")
    def should_not_be_in_battle(self):
        """Fail if the game is currently in a battle."""
        if self._app.game_state.in_battle:
            raise AssertionError("Expected NOT to be in battle but the game IS in battle state.")

    @keyword("Pending Command Should Be")
    def pending_command_should_be(self, expected: str):
        """Fail if the current pending command is not *expected*."""
        actual = self._app.pending_command
        if actual != expected:
            raise AssertionError(
                f"Expected pending command '{expected}' but got '{actual}'."
            )

    @keyword("Pending Command Should Be Empty")
    def pending_command_should_be_empty(self):
        """Fail if any pending command is active."""
        actual = self._app.pending_command
        if actual is not None:
            raise AssertionError(
                f"Expected no pending command but got '{actual}'."
            )

    # ── Game-state setters ───────────────────────────────────────────────────

    @keyword("Set Money")
    def set_money(self, amount):
        """Set the player's money to *amount*."""
        self._app.game_state.game_data["money"] = int(amount)

    @keyword("Set Item")
    def set_item(self, item_name: str, quantity=1):
        """
        Set the quantity of *item_name* in the bag to *quantity*.

        Setting *quantity* to ``0`` removes the item from the bag.
        """
        items = self._app.game_state.game_data.setdefault("items", {})
        qty = int(quantity)
        if qty <= 0:
            items.pop(item_name, None)
        else:
            items[item_name] = qty

    @keyword("Set Lead Pokemon")
    def set_lead_pokemon(self, species: str, level=15):
        """Replace the party lead with a freshly generated *species* at *level*."""
        self._run_async(self._do_set_lead_pokemon(species.upper(), int(level)))

    async def _do_set_lead_pokemon(self, species: str, level: int):
        from pytemon.engine import BattleState

        bs = BattleState()
        poke = bs.generate_wild_pokemon(species, level)
        self._app.game_state.game_data["pokemon"] = [poke]
        await self._pilot.pause()

    @keyword("Set Pokemon HP")
    def set_pokemon_hp(self, index, hp):
        """Set the HP of the party Pokémon at *index* (0-based) to *hp*."""
        party = self._app.game_state.game_data.get("pokemon", [])
        party[int(index)]["hp"] = int(hp)

    @keyword("Set Location")
    def set_location(self, location_name: str):
        """Teleport the player to *location_name* without triggering travel events."""
        from pytemon.locations import get_location

        gs = self._app.game_state
        gs.game_data["location"] = location_name
        loc = get_location(location_name)
        if loc:
            gs.current_location = loc

    @keyword("Set Pending Command")
    def set_pending_command(self, command: str, **kwargs):
        """
        Set the active pending command and any associated game-data fields.

        Extra keyword arguments are stored directly in ``game_state.game_data``.
        This is used, for example, to enter shop mode::

            Set Pending Command    shop    _current_shop_catalog=basic
        """
        self._app.pending_command = command
        for key, value in kwargs.items():
            self._app.game_state.game_data[key] = value

    @keyword("Set Story Flag")
    def set_story_flag(self, flag_name: str, value=True):
        """Set story flag *flag_name* to ``True`` (default) or ``False``."""
        flags = self._app.game_state.game_data.setdefault("story_flags", {})
        if isinstance(value, str):
            value = value.lower() not in ("false", "0", "no")
        flags[flag_name] = bool(value)

    @keyword("Set Learn Move Prompt")
    def set_learn_move_prompt(self, move_name: str, remaining: str = ""):
        """
        Queue an interactive move-learn prompt for the lead Pokémon.

        Arguments:
        - ``move_name``: The new move to learn.
        - ``remaining``: Optional additional move name to queue after this one.
        """
        self._run_async(self._do_set_learn_move_prompt(move_name, remaining))

    async def _do_set_learn_move_prompt(self, move_name: str, remaining: str):
        from textual.widgets import RichLog

        output = self._app.query_one("#output", RichLog)
        output.clear()
        pokemon = self._app.game_state.game_data["pokemon"][0]
        new_moves = [move_name] + ([remaining] if remaining else [])
        self._app._queue_move_learn(pokemon, new_moves, "field", output)
        await self._pilot.pause()
        self._capture_output()

    @keyword("Add Badge")
    def add_badge(self, badge_name: str):
        """Award the named badge to the player."""
        from pytemon.gym_system import get_badge_data

        badge = get_badge_data(badge_name)
        if not badge:
            raise ValueError(f"Unknown badge: '{badge_name}'")
        badges = self._app.game_state.game_data.setdefault("badges", [])
        if badge["id"] not in badges:
            badges.append(badge["id"])

    @keyword("Add Defeated Trainer")
    def add_defeated_trainer(self, trainer_id: str):
        """Mark *trainer_id* as defeated in the game state."""
        defeated = self._app.game_state.game_data.setdefault("defeated_trainers", [])
        if trainer_id not in defeated:
            defeated.append(trainer_id)

    @keyword("Register Pokemon As Seen")
    def register_pokemon_as_seen(self, species: str):
        """Register *species* as seen in the Pokédex."""
        seen = (
            self._app.game_state.game_data
            .setdefault("pokedex", {})
            .setdefault("seen", [])
        )
        name = species.upper()
        if name not in seen:
            seen.append(name)

    # ── Battle-specific keywords ─────────────────────────────────────────────

    @keyword("Set Wild Encounter")
    def set_wild_encounter(self, species: str, level: int):
        """
        Queue a specific *species* at *level* for the next wild encounter.

        The next time the player triggers a wild encounter (e.g., via exploration),
        this Pokemon will appear instead of a random wild species.

        Arguments:
        - ``species``: Species name (e.g., ``RATTATA``).
        - ``level``: Pokemon level (e.g., ``5``).

        Example:
        | Set Wild Encounter    PIDGEY    10 |
        | Type Command          search for wild pokemon |
        | Should Be In Battle |
        """
        self._app.game_state.game_data["_next_wild_encounter"] = {
            "species": species.upper(),
            "level": int(level),
        }

    @keyword("Level Up Pokemon")
    def level_up_pokemon(self, party_index: int):
        """
        Force the Pokemon at *party_index* (0-based) to level up immediately.

        This triggers stat recalculation and evolution checks (if applicable).

        Arguments:
        - ``party_index``: Index of the Pokemon in the party (0 for lead).

        Example:
        | Level Up Pokemon    0 |
        | Party Pokemon Level Should Be    0    16 |
        """
        self._run_async(self._do_level_up_pokemon(int(party_index)))

    async def _do_level_up_pokemon(self, party_index: int):
        from textual.widgets import RichLog

        party = self._app.game_state.game_data.get("pokemon", [])
        if party_index >= len(party):
            raise AssertionError(
                f"No Pokemon at party index {party_index} (party size {len(party)})."
            )

        pokemon = party[party_index]
        pokemon["level"] += 1

        # Recalculate stats at the new level
        from pytemon.engine import BattleState

        bs = BattleState()
        bs._update_stats_for_level(pokemon)

        # Check for evolution
        from pytemon import evolution

        output = self._app.query_one("#output", RichLog)
        output.clear()

        # Trigger evolution check (level-up based)
        evolution.check_for_evolution(
            pokemon, self._app.game_state, "level_up", output, self._app._prompt_evolution
        )

        await self._pilot.pause()
        self._capture_output()

    @keyword("Choose Move")
    def choose_move(self, move_slot: int):
        """
        Select move slot *move_slot* (1-4) during an active battle.

        Arguments:
        - ``move_slot``: Move slot number (1-4).

        Example:
        | Choose Move    1 |
        """
        self._run_async(self._do_choose_move(int(move_slot)))

    async def _do_choose_move(self, move_slot: int):
        from textual.widgets import RichLog

        if not self._app.game_state.in_battle:
            raise AssertionError("Cannot choose move: not in battle.")

        output = self._app.query_one("#output", RichLog)
        output.clear()

        # Simulate the user entering the move number
        self._app.handle_pending_command(str(move_slot), output)

        await self._pilot.pause()
        self._capture_output()

    @keyword("Use Item In Battle")
    def use_item_in_battle(self, item_name: str):
        """
        Use *item_name* during an active battle.

        Works for Potions, Pokeballs, and other battle items.

        Arguments:
        - ``item_name``: Name of the item (e.g., ``Potion``, ``Pokeball``).

        Example:
        | Use Item In Battle    Pokeball |
        """
        self._run_async(self._do_use_item_in_battle(item_name))

    async def _do_use_item_in_battle(self, item_name: str):
        from textual.widgets import RichLog

        if not self._app.game_state.in_battle:
            raise AssertionError("Cannot use item: not in battle.")

        output = self._app.query_one("#output", RichLog)
        output.clear()

        # Enter "item" command then the item name
        # First, trigger item menu
        self._app.process_command("item", output)
        await self._pilot.pause()

        # Then select the item
        self._app.handle_pending_command(item_name, output)
        await self._pilot.pause()
        self._capture_output()

    @keyword("Flee Battle")
    def flee_battle(self):
        """
        Attempt to flee from the current battle.

        Example:
        | Flee Battle |
        | Should Not Be In Battle |
        """
        self._run_async(self._do_flee_battle())

    async def _do_flee_battle(self):
        from textual.widgets import RichLog

        if not self._app.game_state.in_battle:
            raise AssertionError("Cannot flee: not in battle.")

        output = self._app.query_one("#output", RichLog)
        output.clear()

        self._app.process_command("flee", output)

        await self._pilot.pause()
        self._capture_output()

    @keyword("Party Size Should Be")
    def party_size_should_be(self, expected: int):
        """Fail if the party does not have exactly *expected* Pokemon."""
        party = self._app.game_state.game_data.get("pokemon", [])
        actual = len(party)
        if actual != int(expected):
            raise AssertionError(f"Expected party size {expected} but got {actual}.")
