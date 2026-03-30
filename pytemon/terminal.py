"""
Pokemon Terminal Application using Textual.

This module assembles the PokemonTerminal App from four focused mixins:

  PanelMixin      — show/hide all UI panels
  GameFlowMixin   — main-menu, save/load, quit, pending-command dispatch
  BuildingMixin   — buildings, shop, exploration, name/starter selection
  BattleMixin     — full combat system, evolution prompting

What stays here:
  • App wiring (compose, on_mount, CSS/bindings)
  • Event handlers (on_input_submitted, on_button_pressed, on_select_changed)
  • process_command — the top-level in-game command router
  • Thin display delegates (show_party, show_bag, show_pokedex, …)
"""

import asyncio
import math
import os
from pathlib import Path
from typing import Optional

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Grid, Horizontal
from textual.reactive import reactive
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    LoadingIndicator,
    ProgressBar,
    RichLog,
    Select,
    Static,
    TabbedContent,
    TabPane,
)

# ── Original modules (kept for on_input_submitted and process_command) ──────
from . import buildings, cheat_commands, exploration, pc_system, pokedex

# Game modules
from . import evolution as _evo
from . import fishing as _fishing
from . import hm_tm_system as _hm_tm
from . import items as _items
from . import stats as _stats
from .buildings import SHOP_CATALOG
from .data.pokemon_data import POKEMON, get_pokemon
from .game_state import GameState
from .texts.en import terminal as terminal_text
from .ui import displays
from .ui.battle_mixin import BattleMixin
from .ui.building_mixin import BuildingMixin
from .ui.formatters import write_lines, write_lines_fmt
from .ui.game_flow_mixin import GameFlowMixin

# Mixin modules
from .ui.panel_mixin import PanelMixin
from .ui.text_animation import AnimatedTextWriter

# ═══════════════════════════════════════════════════════════════════════════════
# PokemonTerminal
# ═══════════════════════════════════════════════════════════════════════════════


class PokemonTerminal(PanelMixin, GameFlowMixin, BuildingMixin, BattleMixin, App):
    """Pokemon terminal application using Textual."""

    CSS_PATH = "terminal.tcss"

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        ("q", "quit", "Quit"),
        ("h", "help", "Help"),
    ]

    TITLE = "Pokemon Terminal Game"
    SUB_TITLE = "A Robot Framework Adventure"

    command_count = reactive(0)
    typewriter_enabled = True
    typewriter_delay = 0.03

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def __init__(self, *args, **kwargs):
        """Initialize the Pokemon Terminal."""
        super().__init__(*args, **kwargs)
        self.lock_file_path = os.environ.get("POKEMON_LOCK_FILE")
        self.game_state = GameState()
        self.pending_command = None
        self.pending_command_data = {}
        self.text_animator = AnimatedTextWriter(self)
        if os.environ.get("POKEMON_TYPEWRITER", "").lower() == "true":
            self.typewriter_enabled = True

    def on_unmount(self) -> None:
        """Clean up when the app is unmounted."""
        if self.lock_file_path:
            try:
                lock_path = Path(self.lock_file_path)
                if lock_path.exists():
                    lock_path.unlink()
            except Exception:
                pass

    async def write_animated(self, output: RichLog, text: str) -> None:
        """Write text with optional line-by-line delay effect."""
        output.write(text)
        if self.typewriter_enabled and text.strip():
            delay = min(self.typewriter_delay * len(text), 0.3)
            await asyncio.sleep(delay)

    # ── UI composition ───────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        """Compose the terminal UI."""
        yield Static(
            "[bold cyan]🎮 Pokemon Terminal Game[/bold cyan]\n"
            "Type commands below. Press 'h' for help, 'q' to quit.",
            id="welcome",
        )
        yield Header()
        with Horizontal(id="battle-screen"):
            yield RichLog(id="output", highlight=True, markup=True)
            with Container(id="hud-player", classes="hud-panel hidden"):
                yield Static("", id="hud-player-name", classes="hud-name")
                yield ProgressBar(
                    total=100,
                    show_eta=False,
                    show_percentage=False,
                    id="hud-player-hp-bar",
                    classes="hud-hp-bar player-hp-bar",
                )
                yield Static("", id="hud-player-hp-text", classes="hud-hp-text")
                yield Static("", id="hud-player-moves", classes="hud-moves")
                yield Static("", id="hud-player-last-move", classes="hud-last-move")
                yield Static("", id="hud-player-stages", classes="hud-stages")
            with Container(id="hud-enemy", classes="hud-panel hidden"):
                yield Static("", id="hud-enemy-name", classes="hud-name")
                yield ProgressBar(
                    total=100,
                    show_eta=False,
                    show_percentage=False,
                    id="hud-enemy-hp-bar",
                    classes="hud-hp-bar enemy-hp-bar",
                )
                yield Static("", id="hud-enemy-hp-text", classes="hud-hp-text")
                yield Static("", id="hud-enemy-moves", classes="hud-moves")
                yield Static("", id="hud-enemy-last-move", classes="hud-last-move")
                yield Static("", id="hud-enemy-stages", classes="hud-stages")

        with Container(id="main-menu-actions", classes="hidden"):
            yield Static("What would you like to do?", id="main-menu-title")
            with Horizontal(id="main-menu-row1", classes="button-row"):
                yield Button("🆕 Start New Game", id="btn-new-game", classes="main-menu-button")
                yield Button("📂 Load Game", id="btn-load-game", classes="main-menu-button")
            with Horizontal(id="main-menu-row2", classes="button-row"):
                yield Button("❓ Help", id="btn-help", classes="main-menu-button")
                yield Button("❌ Exit", id="btn-exit", classes="main-menu-button")

        with Container(id="battle-actions", classes="hidden"):
            yield Static("What will you do?", id="battle-actions-title")
            with Horizontal(id="battle-actions-row1", classes="button-row"):
                yield Button("⚔️ Fight", id="btn-fight", classes="battle-button battle-button-fight")
                yield Button(
                    "🔄 Switch", id="btn-switch", classes="battle-button battle-button-switch"
                )
            with Horizontal(id="battle-actions-row2", classes="button-row"):
                yield Button("🎒 Item", id="btn-item", classes="battle-button battle-button-item")
                yield Button("🏃 Run", id="btn-run", classes="battle-button battle-button-run")

        with Container(id="move-selection", classes="hidden"):
            yield Static("Select a move:", id="move-selection-title")
            with Horizontal(id="move-selection-row1", classes="button-row"):
                yield Button("Move 1", id="btn-move-0", classes="move-button move-button-normal")
                yield Button("Move 2", id="btn-move-1", classes="move-button move-button-normal")
            with Horizontal(id="move-selection-row2", classes="button-row"):
                yield Button("Move 3", id="btn-move-2", classes="move-button move-button-normal")
                yield Button("Move 4", id="btn-move-3", classes="move-button move-button-normal")
                yield Button("← Back", id="btn-move-back", classes="move-button-back")

        with Container(id="battle-loading", classes="hidden"):
            yield LoadingIndicator(id="battle-loading-indicator")

        with Container(id="battle-bag", classes="hidden"):
            yield Static("🎒 Battle Bag", id="battle-bag-title")
            with Horizontal(id="battle-bag-row1", classes="button-row"):
                yield Button(
                    "🔴 Pokeball",
                    id="btn-bag-pokeball",
                    classes="bag-button bag-button-catch",
                )
                yield Button(
                    "🔵 Great Ball",
                    id="btn-bag-great-ball",
                    classes="bag-button bag-button-catch",
                )
                yield Button(
                    "🟡 Ultra Ball",
                    id="btn-bag-ultra-ball",
                    classes="bag-button bag-button-catch",
                )
                yield Button(
                    "⚪ Master Ball",
                    id="btn-bag-master-ball",
                    classes="bag-button bag-button-catch",
                )
            with Horizontal(id="battle-bag-row2", classes="button-row"):
                yield Button("💊 Potion", id="btn-bag-potion", classes="bag-button bag-button-heal")
                yield Button(
                    "💊 Super Potion",
                    id="btn-bag-super-potion",
                    classes="bag-button bag-button-heal",
                )
                yield Button(
                    "💊 Hyper Potion",
                    id="btn-bag-hyper-potion",
                    classes="bag-button bag-button-heal",
                )
                yield Button(
                    "✨ Full Restore",
                    id="btn-bag-full-restore",
                    classes="bag-button bag-button-heal",
                )
            with Horizontal(id="battle-bag-row3", classes="button-row"):
                yield Button(
                    "💜 Antidote", id="btn-bag-antidote", classes="bag-button bag-button-status"
                )
                yield Button(
                    "💛 Paralyze Heal",
                    id="btn-bag-paralyze-heal",
                    classes="bag-button bag-button-status",
                )
                yield Button(
                    "💙 Awakening", id="btn-bag-awakening", classes="bag-button bag-button-status"
                )
            yield Button("← Cancel", id="btn-bag-cancel", classes="bag-button-cancel")

        with Container(id="pokemon-switch", classes="hidden"):
            yield Static("👥 Switch Pokemon", id="pokemon-switch-title")
            yield Button("Slot 1", id="btn-switch-slot-0", classes="switch-slot-button")
            yield Button("Slot 2", id="btn-switch-slot-1", classes="switch-slot-button")
            yield Button("Slot 3", id="btn-switch-slot-2", classes="switch-slot-button")
            yield Button("Slot 4", id="btn-switch-slot-3", classes="switch-slot-button")
            yield Button("Slot 5", id="btn-switch-slot-4", classes="switch-slot-button")
            yield Button("Slot 6", id="btn-switch-slot-5", classes="switch-slot-button")
            yield Button("← Cancel", id="btn-switch-cancel", classes="switch-cancel-button")

        with Container(id="faint-switch", classes="hidden"):
            yield Static("⚠️ Your Pokemon fainted! Choose who to send in:", id="faint-switch-title")
            yield Button("Slot 1", id="btn-faint-slot-0", classes="switch-slot-button")
            yield Button("Slot 2", id="btn-faint-slot-1", classes="switch-slot-button")
            yield Button("Slot 3", id="btn-faint-slot-2", classes="switch-slot-button")
            yield Button("Slot 4", id="btn-faint-slot-3", classes="switch-slot-button")
            yield Button("Slot 5", id="btn-faint-slot-4", classes="switch-slot-button")
            yield Button("Slot 6", id="btn-faint-slot-5", classes="switch-slot-button")
            yield Button("🏃 Run Away", id="btn-faint-run", classes="faint-run-button")

        with Container(id="choose-lead-panel", classes="hidden"):
            yield Static("👥 Choose your lead Pokemon!", id="choose-lead-title")
            with Grid(id="choose-lead-grid"):
                yield Button("Slot 1", id="btn-lead-slot-0", classes="lead-slot-button")
                yield Button("Slot 2", id="btn-lead-slot-1", classes="lead-slot-button")
                yield Button("Slot 3", id="btn-lead-slot-2", classes="lead-slot-button")
                yield Button("Slot 4", id="btn-lead-slot-3", classes="lead-slot-button")
                yield Button("Slot 5", id="btn-lead-slot-4", classes="lead-slot-button")
                yield Button("Slot 6", id="btn-lead-slot-5", classes="lead-slot-button")
            yield Button("← Cancel", id="btn-lead-cancel", classes="lead-cancel-button")

        with Container(id="location-selection", classes="hidden"):
            yield Static("🗺️  Where would you like to go?", id="location-selection-title")
            yield Select([("Choose a destination...", "")], id="location-select", allow_blank=False)
            with Horizontal(id="location-buttons"):
                yield Button("✓ Go", id="btn-location-go", classes="location-button location-go")
                yield Button(
                    "← Cancel", id="btn-location-cancel", classes="location-button location-cancel"
                )

        with Container(id="building-selection", classes="hidden"):
            yield Static(
                "🏛️  Which building would you like to enter?", id="building-selection-title"
            )
            yield Select([("Choose a building...", "")], id="building-select", allow_blank=False)
            with Horizontal(id="building-buttons"):
                yield Button("✓ Enter", id="btn-building-go", classes="building-button building-go")
                yield Button(
                    "← Cancel", id="btn-building-cancel", classes="building-button building-cancel"
                )

        with Container(id="starter-selection", classes="hidden"):
            yield Static("🎯 Choose your starter Pokemon!", id="starter-selection-title")
            with Grid(id="starter-selection-grid"):
                yield Button(
                    "🌿 Bulbasaur",
                    id="btn-starter-bulbasaur",
                    classes="starter-button starter-button-grass",
                )
                yield Button(
                    "🔥 Charmander",
                    id="btn-starter-charmander",
                    classes="starter-button starter-button-fire",
                )
                yield Button(
                    "💧 Squirtle",
                    id="btn-starter-squirtle",
                    classes="starter-button starter-button-water",
                )
                yield Button(
                    "⚡ Pikachu",
                    id="btn-starter-pikachu",
                    classes="starter-button starter-button-electric",
                )

        with Container(id="name-selection", classes="hidden"):
            yield Static("👤 Choose names for your adventure!", id="name-selection-title")
            yield Static("What is your name?", id="name-selection-player-label")
            yield Input(
                placeholder="Enter your name (e.g., Ash)",
                id="input-player-name",
                classes="name-input",
            )
            yield Static("What is your rival's name?", id="name-selection-rival-label")
            yield Input(
                placeholder="Enter rival's name (e.g., Gary)",
                id="input-rival-name",
                classes="name-input",
            )
            with Horizontal(id="name-selection-buttons"):
                yield Button(
                    "✓ Confirm Names", id="btn-name-confirm", classes="name-button name-confirm"
                )
                yield Button(
                    "🎲 Random Names", id="btn-name-random", classes="name-button name-random"
                )

        with Container(id="evolution-panel", classes="hidden"):
            yield Static("✨ POKÉMON is evolving!", id="evolution-title")
            with Horizontal(id="evolution-buttons", classes="button-row"):
                yield Button(
                    "✨ Evolve!",
                    id="btn-evolve-confirm",
                    classes="evolution-button evolution-confirm",
                )
                yield Button(
                    "🚫 Stop", id="btn-evolve-cancel", classes="evolution-button evolution-stop"
                )

        with Container(id="confirmation-panel", classes="hidden"):
            yield Static("Confirmation", id="confirmation-title")
            with Horizontal(id="confirmation-buttons"):
                yield Button("✓ Yes", id="btn-confirm-yes", classes="confirm-button confirm-yes")
                yield Button("✗ No", id="btn-confirm-no", classes="confirm-button confirm-no")
                yield Button(
                    "← Cancel", id="btn-confirm-cancel", classes="confirm-button confirm-cancel"
                )

        with Container(id="save-option-panel", classes="hidden"):
            yield Static("💾 What would you like to do?", id="save-option-title")
            with Horizontal(id="save-option-buttons"):
                yield Button(
                    "✓ Overwrite current save",
                    id="btn-save-overwrite",
                    classes="save-button save-overwrite",
                )
                yield Button(
                    "📝 Create new save file", id="btn-save-new", classes="save-button save-new"
                )

        with Container(id="load-game-panel", classes="hidden"):
            yield Static("📂 Load Game", id="load-game-title")
            yield DataTable(id="saves-table", cursor_type="row")
            with Horizontal(id="load-game-buttons"):
                yield Button("📂 Load", id="btn-load-confirm", classes="load-button load-confirm")
                yield Button("← Back", id="btn-load-cancel", classes="load-button load-cancel")

        with Container(id="pokedex-navigation", classes="hidden"):
            with Horizontal(id="pokedex-nav-buttons", classes="button-row"):
                yield Button(
                    "⏮ First", id="btn-pokedex-first", classes="pokedex-button pokedex-first"
                )
                yield Button(
                    "← Previous", id="btn-pokedex-prev", classes="pokedex-button pokedex-prev"
                )
                yield Button("Next →", id="btn-pokedex-next", classes="pokedex-button pokedex-next")
                yield Button("Last ⏭", id="btn-pokedex-last", classes="pokedex-button pokedex-last")
                yield Button(
                    "✕ Close", id="btn-pokedex-close", classes="pokedex-button pokedex-close"
                )

        with Container(id="nurse-joy-panel", classes="hidden"):
            yield Static("", id="nurse-joy-question")
            with Horizontal(id="nurse-joy-buttons"):
                yield Button(
                    "✅ Yes", id="btn-nurse-joy-yes", classes="nurse-joy-button nurse-joy-yes"
                )
                yield Button(
                    "❌ No", id="btn-nurse-joy-no", classes="nurse-joy-button nurse-joy-no"
                )

        with Container(id="pokemon-center-panel", classes="hidden"):
            yield Static("Nurse Joy: How can I help you?", id="pokemon-center-title")
            with Horizontal(id="pokemon-center-buttons", classes="button-row"):
                yield Button(
                    "💊 Heal Pokemon", id="btn-pc-center-heal", classes="pokemon-center-button"
                )
                yield Button("💾 Use PC", id="btn-pc-center-usepc", classes="pokemon-center-button")
                yield Button("🚪 Leave", id="btn-pc-center-leave", classes="pokemon-center-button")
            with Horizontal(id="pokemon-center-loading", classes="hidden"):
                yield LoadingIndicator(id="pokemon-center-loading-indicator")
                yield Static("Healing in progress...", id="pokemon-center-loading-text")

        with Container(id="pc-panel", classes="hidden"):
            yield Static("💾 Bill's PC Storage System", id="pc-panel-title")
            yield Static("", id="pc-summary")
            with Horizontal(id="pc-box-buttons", classes="button-row"):
                yield Button("📦 Box 1", id="btn-pc-view-box-1", classes="pc-box-button")
                yield Button("📦 Box 2", id="btn-pc-view-box-2", classes="pc-box-button")
                yield Button("📦 Box 3", id="btn-pc-view-box-3", classes="pc-box-button")
            with Horizontal(id="pc-action-buttons", classes="button-row"):
                yield Button("📥 Deposit Pokémon", id="btn-pc-deposit", classes="pc-action-button")
                yield Button(
                    "🚪 Leave PC",
                    id="btn-pc-leave",
                    classes="pc-action-button pc-leave-button",
                )

        with Container(id="pc-deposit-panel", classes="hidden"):
            yield Static("📥 Deposit — which Pokémon to store?", id="pc-deposit-title")
            with Horizontal(id="pc-deposit-row1", classes="button-row"):
                yield Button("Slot 1", id="btn-pc-deposit-slot-0", classes="pc-slot-button")
                yield Button("Slot 2", id="btn-pc-deposit-slot-1", classes="pc-slot-button")
                yield Button("Slot 3", id="btn-pc-deposit-slot-2", classes="pc-slot-button")
            with Horizontal(id="pc-deposit-row2", classes="button-row"):
                yield Button("Slot 4", id="btn-pc-deposit-slot-3", classes="pc-slot-button")
                yield Button("Slot 5", id="btn-pc-deposit-slot-4", classes="pc-slot-button")
                yield Button("Slot 6", id="btn-pc-deposit-slot-5", classes="pc-slot-button")
            yield Button("← Back", id="btn-pc-deposit-back", classes="pc-back-button")

        with Container(id="pc-withdraw-panel", classes="hidden"):
            yield Static("📤 Withdraw from Box", id="pc-withdraw-title")
            with Horizontal(id="pc-withdraw-row1", classes="button-row"):
                yield Button("Slot 1", id="btn-pc-withdraw-slot-0", classes="pc-slot-button")
                yield Button("Slot 2", id="btn-pc-withdraw-slot-1", classes="pc-slot-button")
                yield Button("Slot 3", id="btn-pc-withdraw-slot-2", classes="pc-slot-button")
            with Horizontal(id="pc-withdraw-row2", classes="button-row"):
                yield Button("Slot 4", id="btn-pc-withdraw-slot-3", classes="pc-slot-button")
                yield Button("Slot 5", id="btn-pc-withdraw-slot-4", classes="pc-slot-button")
                yield Button("Slot 6", id="btn-pc-withdraw-slot-5", classes="pc-slot-button")
            yield Button("← Back", id="btn-pc-withdraw-back", classes="pc-back-button")

        with Container(id="pokemart-panel", classes="hidden"):
            yield Static("🏪  Clerk: What can I get for you?", id="pokemart-title")
            yield Static("", id="pokemart-money")
            with Horizontal(id="pokemart-shop-row"):
                yield Select([], id="shop-item-select", prompt="📦 Choose an item...")
                with Horizontal(id="shop-qty-controls"):
                    yield Button("-", id="btn-shop-qty-minus", classes="shop-qty-button")
                    yield Input(value="1", id="shop-qty-input", restrict=r"[0-9]*", max_length=2)
                    yield Button("+", id="btn-shop-qty-plus", classes="shop-qty-button")
                yield Button("🛒 Buy", id="btn-shop-buy", classes="shop-buy-button")
            with Horizontal(id="pokemart-leave-row"):
                yield Button("🚪 Leave Shop", id="btn-shop-leave", classes="shop-leave-button")

        with Container(id="quit-panel", classes="hidden"):
            yield Static("⚠ Leaving the game?", id="quit-panel-title")
            with Horizontal(id="quit-panel-buttons", classes="button-row"):
                yield Button(
                    "🚪 Close Game", id="btn-quit-close", classes="quit-button quit-button-close"
                )
                yield Button(
                    "🏠 Main Menu",
                    id="btn-quit-mainmenu",
                    classes="quit-button quit-button-mainmenu",
                )
                yield Button(
                    "← Cancel", id="btn-quit-cancel", classes="quit-button quit-button-cancel"
                )

        with Container(id="party-panel", classes="hidden"):
            with TabbedContent(id="party-tabs", initial="tab-party-overview"):
                with TabPane("📋 Overview", id="tab-party-overview"):
                    yield RichLog(id="party-log-overview", markup=True, highlight=True)
                with TabPane("Slot 1", id="tab-party-1"):
                    yield RichLog(id="party-log-1", markup=True, highlight=True)
                with TabPane("Slot 2", id="tab-party-2"):
                    yield RichLog(id="party-log-2", markup=True, highlight=True)
                with TabPane("Slot 3", id="tab-party-3"):
                    yield RichLog(id="party-log-3", markup=True, highlight=True)
                with TabPane("Slot 4", id="tab-party-4"):
                    yield RichLog(id="party-log-4", markup=True, highlight=True)
                with TabPane("Slot 5", id="tab-party-5"):
                    yield RichLog(id="party-log-5", markup=True, highlight=True)
                with TabPane("Slot 6", id="tab-party-6"):
                    yield RichLog(id="party-log-6", markup=True, highlight=True)
            with Horizontal(id="party-close-row"):
                yield Button("✕ Close Party", id="btn-party-close", classes="party-close-button")

        with Container(id="gym-panel", classes="hidden"):
            yield Static("⚔️  Pokemon Gym", id="gym-panel-title")
            yield Static("", id="gym-panel-info")
            with Horizontal(id="gym-panel-buttons", classes="button-row"):
                yield Button(
                    "🥊 Fight Gym Trainer",
                    id="btn-gym-trainer",
                    classes="gym-button gym-button-trainer",
                )
                yield Button(
                    "⚔️ Challenge Leader",
                    id="btn-gym-challenge",
                    classes="gym-button gym-button-leader",
                )
                yield Button(
                    "� Rematch Leader",
                    id="btn-gym-rematch",
                    classes="gym-button gym-button-rematch hidden",
                )
                yield Button(
                    "�🚪 Leave Gym", id="btn-gym-leave", classes="gym-button gym-button-leave"
                )

        with Container(id="input-container"):
            yield Input(placeholder="Enter command... (e.g., 'help', 'status')", id="command-input")

        yield Footer()

    def on_mount(self) -> None:
        """Initialize the terminal on mount."""
        self.hide_all_panels()
        output = self.query_one("#output", RichLog)
        self.show_main_menu(output)
        self.query_one("#command-input", Input).focus()

    def _refresh_subtitle(self) -> None:
        """Update the #welcome banner to show the current location and its description."""
        try:
            welcome = self.query_one("#welcome", Static)
            if self.game_state.in_game and self.game_state.current_location:
                active_building = self.game_state.game_data.get("_active_building")
                if active_building:
                    location_name = self.game_state.current_location.name
                    welcome.update(
                        f"[bold yellow]🏛 {active_building}[/bold yellow]\n"
                        f"[dim]Inside {location_name}[/dim]"
                    )
                    return
                loc = self.game_state.current_location
                welcome.update(
                    f"[bold cyan]📍 {loc.name}[/bold cyan]\n[dim]{loc.description}[/dim]"
                )
            else:
                welcome.update(
                    "[bold cyan]🎮 Pokemon Terminal Game[/bold cyan]\n"
                    "Type commands below. Press 'h' for help, 'q' to quit."
                )
        except Exception:
            pass

    # ── Event handlers ───────────────────────────────────────────────────────

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        button_id = event.button.id
        output = self.query_one("#output", RichLog)

        # Main menu buttons
        if button_id == "btn-new-game":
            output.write("[bold yellow]🎮 >[/bold yellow] Start New Game")
            self.hide_all_panels()
            self.process_menu_command("start new game", output)
        elif button_id == "btn-load-game":
            output.write("[bold yellow]🎮 >[/bold yellow] Load Game")
            self.hide_all_panels()
            self.process_menu_command("load game", output)
        elif button_id == "btn-help":
            output.write("[bold yellow]🎮 >[/bold yellow] Help")
            self.hide_all_panels()
            self.show_help(output)
        elif button_id == "btn-exit":
            output.write("[bold yellow]🎮 >[/bold yellow] Exit")
            self.hide_all_panels()
            self.process_menu_command("exit", output)

        # Battle action buttons
        elif button_id == "btn-fight":
            if self.game_state.battle_state and self.game_state.battle_state.is_safari:
                output.write("[bold yellow]🎮 >[/bold yellow] Bait")
                self.process_battle_command("bait", output)
            else:
                output.write("[bold yellow]🎮 >[/bold yellow] Fight")
                self.process_battle_command("fight", output)
        elif button_id == "btn-switch":
            if self.game_state.battle_state and self.game_state.battle_state.is_safari:
                output.write("[bold yellow]🎮 >[/bold yellow] Rock")
                self.process_battle_command("rock", output)
            else:
                output.write("[bold yellow]🎮 >[/bold yellow] Switch")
                self.process_battle_command("switch", output)
        elif button_id == "btn-item":
            if self.game_state.battle_state and self.game_state.battle_state.is_safari:
                output.write("[bold yellow]🎮 >[/bold yellow] Throw Safari Ball")
                self.process_battle_command("safari ball", output)
            else:
                output.write("[bold yellow]🎮 >[/bold yellow] Item")
                self.process_battle_command("bag", output)

        # Battle bag item buttons
        elif button_id == "btn-bag-pokeball":
            output.write("[bold yellow]🎮 >[/bold yellow] Throw Pokeball")
            self.hide_all_battle_panels()
            self.process_battle_command("throw pokeball", output)
        elif button_id == "btn-bag-great-ball":
            output.write("[bold yellow]🎮 >[/bold yellow] Throw Great Ball")
            self.hide_all_battle_panels()
            self.process_battle_command("throw great ball", output)
        elif button_id == "btn-bag-ultra-ball":
            output.write("[bold yellow]🎮 >[/bold yellow] Throw Ultra Ball")
            self.hide_all_battle_panels()
            self.process_battle_command("throw ultra ball", output)
        elif button_id == "btn-bag-master-ball":
            output.write("[bold yellow]🎮 >[/bold yellow] Throw Master Ball")
            self.hide_all_battle_panels()
            self.process_battle_command("throw master ball", output)
        elif button_id == "btn-bag-potion":
            output.write("[bold yellow]🎮 >[/bold yellow] Use Potion")
            self.hide_all_battle_panels()
            self.process_battle_command("use potion", output)
        elif button_id == "btn-bag-super-potion":
            output.write("[bold yellow]🎮 >[/bold yellow] Use Super Potion")
            self.hide_all_battle_panels()
            self.process_battle_command("use super potion", output)
        elif button_id == "btn-bag-hyper-potion":
            output.write("[bold yellow]🎮 >[/bold yellow] Use Hyper Potion")
            self.hide_all_battle_panels()
            self.process_battle_command("use hyper potion", output)
        elif button_id == "btn-bag-full-restore":
            output.write("[bold yellow]🎮 >[/bold yellow] Use Full Restore")
            self.hide_all_battle_panels()
            self.process_battle_command("use full restore", output)
        elif button_id == "btn-bag-antidote":
            output.write("[bold yellow]🎮 >[/bold yellow] Use Antidote")
            self.hide_all_battle_panels()
            self.process_battle_command("use antidote", output)
        elif button_id == "btn-bag-paralyze-heal":
            output.write("[bold yellow]🎮 >[/bold yellow] Use Paralyze Heal")
            self.hide_all_battle_panels()
            self.process_battle_command("use paralyze heal", output)
        elif button_id == "btn-bag-awakening":
            output.write("[bold yellow]🎮 >[/bold yellow] Use Awakening")
            self.hide_all_battle_panels()
            self.process_battle_command("use awakening", output)
        elif button_id == "btn-bag-cancel":
            output.write("[bold yellow]🎮 >[/bold yellow] Cancel")
            self.hide_all_battle_panels()
            self.show_battle_options(output)

        # Pokemon switch slot buttons
        elif button_id.startswith("btn-switch-slot-"):
            slot_idx = int(button_id.split("-")[-1])
            if self.game_state.battle_state:
                party = self.game_state.game_data.get("pokemon", [])
                if slot_idx < len(party) and not isinstance(party[slot_idx], str):
                    output.write(
                        f"[bold yellow]🎮 >[/bold yellow] Switch to {party[slot_idx]['name']}"
                    )
            self.hide_all_battle_panels()
            self.execute_switch(str(slot_idx + 1), output)
        elif button_id == "btn-switch-cancel":
            output.write("[bold yellow]🎮 >[/bold yellow] Cancel switch")
            self.hide_all_battle_panels()
            self.pending_command = "battle"
            self.show_battle_options(output)

        # Faint-switch slot buttons
        elif button_id.startswith("btn-faint-slot-"):
            slot_idx = int(button_id.split("-")[-1])
            if self.game_state.battle_state:
                party = self.game_state.game_data.get("pokemon", [])
                if slot_idx < len(party) and not isinstance(party[slot_idx], str):
                    output.write(
                        f"[bold yellow]🎮 >[/bold yellow] Send out {party[slot_idx]['name']}"
                    )
            self.hide_all_battle_panels()
            self.execute_faint_switch(str(slot_idx + 1), output)
        elif button_id == "btn-faint-run":
            output.write("[bold yellow]🎮 >[/bold yellow] Run Away")
            self.hide_all_battle_panels()
            self.end_battle(output)

        # Choose-lead slot buttons (pre-battle lead selection)
        elif button_id.startswith("btn-lead-slot-"):
            slot_idx = int(button_id.split("-")[-1])
            self.hide_choose_lead_panel()
            self.handle_pending_command(str(slot_idx + 1), output)
        elif button_id == "btn-lead-cancel":
            output.write("[bold yellow]🎮 >[/bold yellow] Cancel")
            self.handle_pending_command("cancel", output)

        elif button_id == "btn-run":
            output.write("[bold yellow]🎮 >[/bold yellow] Run")
            self.process_battle_command("run", output)

        # Move selection buttons
        elif button_id.startswith("btn-move-"):
            if button_id == "btn-move-back":
                output.write("[bold yellow]🎮 >[/bold yellow] Back")
                self.execute_player_move("back", output)
            else:
                move_index = int(button_id.split("-")[-1])
                if self.game_state.battle_state:
                    player = self.game_state.battle_state.player_pokemon
                    moves = player.get("moves", [])
                    if move_index < len(moves):
                        move_name = moves[move_index]["name"]
                        output.write(f"[bold yellow]🎮 >[/bold yellow] {move_name}")
                        # Replace only the move panel with a loading indicator;
                        # HUDs are left in place so the layout does not shift.
                        self.show_battle_loading_panel()
                        self.execute_player_move(move_name, output)

        # Starter Pokemon selection buttons
        elif button_id.startswith("btn-starter-"):
            pokemon_name = button_id.replace("btn-starter-", "").capitalize()
            output.write(f"[bold yellow]🎮 >[/bold yellow] Choose {pokemon_name}")
            self.hide_all_panels()
            self.pending_command = None
            self.choose_starter_pokemon(pokemon_name, output)

        # Name selection buttons
        elif button_id.startswith("btn-name-"):
            if button_id == "btn-name-confirm":
                output.write("[bold yellow]🎮 >[/bold yellow] Confirm names")
                self.confirm_name_selection(output)
            elif button_id == "btn-name-random":
                output.write("[bold yellow]🎮 >[/bold yellow] Random names")
                self.random_name_selection(output)

        # Confirmation buttons (Yes/No/Cancel)
        elif button_id.startswith("btn-confirm-"):
            confirmation_type = self.pending_command_data.get("confirmation_type", "")
            if button_id == "btn-confirm-yes":
                output.write("[bold yellow]🎮 >[/bold yellow] Yes")
                self.hide_all_panels()
                self.handle_confirmation_response("yes", output, confirmation_type)
            elif button_id == "btn-confirm-no":
                output.write("[bold yellow]🎮 >[/bold yellow] No")
                self.hide_all_panels()
                self.handle_confirmation_response("no", output, confirmation_type)
            elif button_id == "btn-confirm-cancel":
                output.write("[bold yellow]🎮 >[/bold yellow] Cancel")
                self.hide_all_panels()
                self.handle_confirmation_response("cancel", output, confirmation_type)

        # Save option buttons
        elif button_id.startswith("btn-save-"):
            if button_id == "btn-save-overwrite":
                output.write("[bold yellow]🎮 >[/bold yellow] Overwrite current save")
                self.hide_all_panels()
                self.handle_pending_command("", output)
            elif button_id == "btn-save-new":
                output.write("[bold yellow]🎮 >[/bold yellow] Create new save file")
                self.hide_all_panels()
                write_lines(output, terminal_text.SAVE_NEW_FILE_PROMPT)

        # Load game buttons
        elif button_id.startswith("btn-load-"):
            if button_id == "btn-load-confirm":
                selected_value = getattr(self, "_selected_save_name", None)
                if selected_value:
                    output.write(f"[bold yellow]🎮 >[/bold yellow] Load {selected_value}")
                    self.hide_all_panels()
                    self.load_selected_save(selected_value, output)
                else:
                    write_lines(output, terminal_text.LOAD_SELECT_SAVE_REQUIRED)
            elif button_id == "btn-load-cancel":
                output.write("[bold yellow]🎮 >[/bold yellow] Back to menu")
                self.hide_all_panels()
                if hasattr(self, "_temp_saves_list"):
                    delattr(self, "_temp_saves_list")
                self.show_main_menu(output)

        # Location selection buttons
        elif button_id.startswith("btn-location-"):
            if button_id == "btn-location-go":
                select = self.query_one("#location-select", Select)
                selected_value = select.value
                if selected_value and str(selected_value) != "":
                    location_name = str(selected_value)
                    output.write(f"[bold yellow]🎮 >[/bold yellow] Go to {location_name}")
                    self.hide_all_panels()
                    self.handle_pending_command(location_name, output)
                else:
                    write_lines(output, terminal_text.LOCATION_SELECT_REQUIRED)
            elif button_id == "btn-location-cancel":
                output.write("[bold yellow]🎮 >[/bold yellow] Cancel")
                self.hide_all_panels()
                self.handle_pending_command("cancel", output)

        # Building selection buttons
        elif button_id.startswith("btn-building-"):
            if button_id == "btn-building-go":
                select = self.query_one("#building-select", Select)
                selected_value = select.value
                if selected_value and str(selected_value) != "":
                    building_name = str(selected_value)
                    output.write(f"[bold yellow]🎮 >[/bold yellow] Enter {building_name}")
                    self.hide_all_panels()
                    self.handle_pending_command(building_name, output)
                else:
                    write_lines(output, terminal_text.BUILDING_SELECT_REQUIRED)
            elif button_id == "btn-building-cancel":
                output.write("[bold yellow]🎮 >[/bold yellow] Cancel")
                self.hide_all_panels()
                self.handle_pending_command("cancel", output)

        # Pokedex navigation buttons
        elif button_id == "btn-pokedex-first":
            output.write("[bold yellow]🎮 >[/bold yellow] First Page")
            self.pokedex_first_page(output)
        elif button_id == "btn-pokedex-prev":
            output.write("[bold yellow]🎮 >[/bold yellow] Previous Page")
            self.pokedex_prev_page(output)
        elif button_id == "btn-pokedex-next":
            output.write("[bold yellow]🎮 >[/bold yellow] Next Page")
            self.pokedex_next_page(output)
        elif button_id == "btn-pokedex-last":
            output.write("[bold yellow]🎮 >[/bold yellow] Last Page")
            self.pokedex_last_page(output)
        elif button_id == "btn-pokedex-close":
            output.write("[bold yellow]🎮 >[/bold yellow] Close Pokedex")
            self.hide_pokedex_navigation()
            write_lines(output, terminal_text.POKEDEX_CLOSED)

        # Party panel close
        elif button_id == "btn-party-close":
            output.write("[bold yellow]🎮 >[/bold yellow] Close Party")
            self.hide_all_panels()
            output.write("[dim]Party screen closed.[/dim]")

        # Nurse Joy / Mom healing buttons
        elif button_id == "btn-nurse-joy-yes":
            output.write("[bold yellow]🎮 >[/bold yellow] Yes")
            self.hide_all_panels()
            self.pending_command = None
            self.pending_command_data = {}
            buildings.perform_mom_heal(self.game_state, output)
        elif button_id == "btn-nurse-joy-no":
            output.write("[bold yellow]🎮 >[/bold yellow] No")
            self._clear_active_building_context()
            self.hide_all_panels()
            self.pending_command = None
            self.pending_command_data = {}
            write_lines(output, terminal_text.MOM_HEAL_DECLINED)

        # Pokemon Center lobby buttons
        elif button_id == "btn-pc-center-heal":
            output.write("[bold yellow]🎮 >[/bold yellow] Heal Pokemon")
            self._handle_pokemon_center_command("heal", output)
        elif button_id == "btn-pc-center-usepc":
            output.write("[bold yellow]🎮 >[/bold yellow] Use PC")
            self._open_pc_from_center(output)
        elif button_id == "btn-pc-center-leave":
            output.write("[bold yellow]🎮 >[/bold yellow] Leave")
            self._clear_active_building_context()
            self.hide_all_panels()
            self.pending_command = None
            self.pending_command_data = {}
            write_lines(output, terminal_text.LEAVE_POKEMON_CENTER)

        # Bill's PC panel buttons
        elif button_id.startswith("btn-pc-view-box-"):
            box_num = int(button_id.split("-")[-1])
            output.write(f"[bold yellow]🎮 >[/bold yellow] View Box {box_num}")
            pc_system.show_pc_box(self.game_state, box_num, output)
            self.query_one("#pc-panel").add_class("hidden")
            self.pending_command_data["pc_box"] = box_num
            self.show_pc_withdraw_panel(box_num)
        elif button_id == "btn-pc-deposit":
            output.write("[bold yellow]🎮 >[/bold yellow] Deposit Pokémon")
            self.query_one("#pc-panel").add_class("hidden")
            self.show_pc_deposit_panel()
        elif button_id == "btn-pc-leave":
            output.write("[bold yellow]🎮 >[/bold yellow] Leave PC")
            self.hide_all_panels()
            write_lines(output, terminal_text.PC_LOG_OUT)
            self.pending_command = None
            self.pending_command_data = {}
            self._return_to_pokemon_center(output)
        elif button_id.startswith("btn-pc-deposit-slot-"):
            slot_idx = int(button_id.split("-")[-1])
            slot_num = slot_idx + 1
            output.write(f"[bold yellow]🎮 >[/bold yellow] Deposit slot {slot_num}")
            self.query_one("#pc-deposit-panel").add_class("hidden")
            pc_system.process_pc_command(
                self.game_state,
                f"deposit {slot_num}",
                output,
                lambda _cmd: None,
            )
            self.show_pc_main_panel()
        elif button_id == "btn-pc-deposit-back":
            output.write("[bold yellow]🎮 >[/bold yellow] Back")
            self.query_one("#pc-deposit-panel").add_class("hidden")
            self.show_pc_main_panel()
        elif button_id.startswith("btn-pc-withdraw-slot-"):
            slot_idx = int(button_id.split("-")[-1])
            slot_num = slot_idx + 1
            box_num = self.pending_command_data.get("pc_box", 1)
            output.write(f"[bold yellow]🎮 >[/bold yellow] Withdraw Box {box_num} Slot {slot_num}")
            self.query_one("#pc-withdraw-panel").add_class("hidden")
            pc_system.process_pc_command(
                self.game_state,
                f"withdraw {box_num} {slot_num}",
                output,
                lambda _cmd: None,
            )
            self.show_pc_main_panel()
        elif button_id == "btn-pc-withdraw-back":
            output.write("[bold yellow]🎮 >[/bold yellow] Back")
            self.query_one("#pc-withdraw-panel").add_class("hidden")
            self.show_pc_main_panel()

        # Pokemart shop panel buttons
        elif button_id == "btn-shop-leave":
            output.write("[bold yellow]🎮 >[/bold yellow] Leave Shop")
            self._clear_active_building_context()
            self.hide_all_panels()
            self.pending_command = None
            self.pending_command_data = {}
            write_lines(output, terminal_text.SHOP_THANK_YOU_LEAVE)
        elif button_id in ("btn-shop-qty-minus", "btn-shop-qty-plus"):
            qty_input = self.query_one("#shop-qty-input", Input)
            try:
                current = int(qty_input.value or "1")
            except ValueError:
                current = 1
            if button_id == "btn-shop-qty-minus":
                current = max(1, current - 1)
            else:
                current = min(99, current + 1)
            qty_input.value = str(current)
            qty_input.remove_class("shop-error")
        elif button_id == "btn-shop-buy":
            selected = self.query_one("#shop-item-select", Select).value
            qty_raw = self.query_one("#shop-qty-input", Input).value.strip()
            qty = qty_raw if qty_raw.isdigit() and int(qty_raw) > 0 else "1"
            qty_input = self.query_one("#shop-qty-input", Input)
            if selected is Select.BLANK or not selected:
                output.write("[yellow]⚠ Please choose an item first.[/yellow]")
            else:
                item_name = str(selected)
                output.write(f"[bold yellow]🎮 >[/bold yellow] Buy {qty}x {item_name}")
                result = self.process_shop_command(f"buy {qty} {item_name}", output)
                if result == "cant_afford":
                    qty_input.add_class("shop-error")
                    money = self.game_state.game_data.get("money", 0)
                    self.query_one("#pokemart-money", Static).update(f"Your money:  ₽{money}")
                elif result == "ok":
                    qty_input.remove_class("shop-error")
                    money = self.game_state.game_data.get("money", 0)
                    self.query_one("#pokemart-money", Static).update(f"Your money:  ₽{money}")
                    options = [
                        (
                            f"{info['emoji']}  {name}  —  ₽{info['price']}  ({info['description']})",
                            name,
                        )
                        for name, info in SHOP_CATALOG.items()
                    ]
                    self.query_one("#shop-item-select", Select).set_options(options)
        elif button_id == "btn-quit-close":
            output.write("[bold yellow]🎮 >[/bold yellow] Close Game")
            self.hide_all_panels()
            self.pending_command_data["quit_destination"] = "exit"
            self._proceed_with_quit(output)
        elif button_id == "btn-quit-mainmenu":
            output.write("[bold yellow]🎮 >[/bold yellow] Main Menu")
            self.hide_all_panels()
            self.pending_command_data["quit_destination"] = "main_menu"
            self._proceed_with_quit(output)
        elif button_id == "btn-quit-cancel":
            output.write("[bold yellow]🎮 >[/bold yellow] Cancel")
            self.hide_all_panels()
            write_lines(output, terminal_text.QUIT_CANCELLED)

        # Gym panel buttons
        elif button_id == "btn-gym-challenge":
            output.write("[bold yellow]🎮 >[/bold yellow] Challenge Gym Leader")
            self.hide_all_panels()
            self._gym_challenge_leader(output)
        elif button_id == "btn-gym-trainer":
            output.write("[bold yellow]🎮 >[/bold yellow] Fight Gym Trainer")
            self.hide_all_panels()
            self._gym_fight_trainer(output)
        elif button_id == "btn-gym-rematch":
            output.write("[bold yellow]🎮 >[/bold yellow] Rematch Gym Leader")
            self.hide_all_panels()
            self._gym_rematch_leader(output)
        elif button_id == "btn-gym-leave":
            output.write("[bold yellow]🎮 >[/bold yellow] Leave Gym")
            self.hide_all_panels()
            write_lines(output, terminal_text.GYM_LEAVE)
            self.look_around(output)

        # Evolution confirmation buttons
        elif button_id == "btn-evolve-confirm":
            evolved_into = self.pending_command_data.get("evolves_into", "???")
            pokemon_ref = self.pending_command_data.get("evolving_pokemon")
            pokemon_name = pokemon_ref.get("name", "POKÉMON") if pokemon_ref else "POKÉMON"

            output.write("[bold yellow]🎮 >[/bold yellow] Evolve!")
            self.hide_all_panels()
            self.pending_command = None  # unblock typing during animation

            anim_lines = [
                "",
                f"[bold yellow]✨ {pokemon_name} is evolving![/bold yellow]",
                "",
                "[dim]  ◇ ◈ ◇ ◈ ◇ ◈ ◇ ◈ ◇ ◈[/dim]",
                "[bold cyan]  ◆ ◈ ◆ ◈ ◆ ◈ ◆ ◈ ◆ ◈[/bold cyan]",
                "[bold magenta]  ★ ✦ ★ ✦ ★ ✦ ★ ✦ ★ ✦[/bold magenta]",
                "",
            ]

            def do_evolve() -> None:
                if pokemon_ref is not None:
                    _evo.force_evolve(
                        self.game_state,
                        pokemon_ref,
                        evolved_into,
                        output,
                        update_battle_state=True,
                        silent_preamble=True,
                    )
                self._resume_after_evolution(output)
                self._refresh_subtitle()

            self.text_animator.write_slow(output, anim_lines, on_complete=do_evolve)
        elif button_id == "btn-evolve-cancel":
            pokemon_name = self.pending_command_data.get("evolving_pokemon", {}).get(
                "name", "POKÉMON"
            )
            output.write("[bold yellow]🎮 >[/bold yellow] Stop")
            self.hide_all_panels()
            self.pending_command = None
            write_lines_fmt(output, terminal_text.EVOLUTION_STOPPED, pokemon_name=pokemon_name)
            self._resume_after_evolution(output)

        self._refresh_subtitle()

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle select widget changes."""
        if event.select.id == "shop-item-select":
            try:
                self.query_one("#shop-qty-input", Input).remove_class("shop-error")
            except Exception:
                pass

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Track the save row clicked in the saves-table."""
        if event.data_table.id != "saves-table":
            return
        self._selected_save_name = str(event.row_key.value)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle command submission."""
        command = event.value.strip()
        output = self.query_one("#output", RichLog)
        input_field = self.query_one("#command-input", Input)
        input_field.value = ""

        if not command:
            input_field.focus()
            return

        if self.pending_command:
            # Allow cheat commands to bypass battle pending states so that
            # e.g. "cheat win" works while waiting for a battle action.
            _battle_pending = {"battle", "select_move", "switch_target", "faint_switch"}
            if (
                self.game_state.cheat_mode
                and command.lower().strip().startswith("cheat ")
                and self.pending_command in _battle_pending
            ):
                output.write(f"[bold yellow]🎮 >[/bold yellow] {command}")
                self.process_command(command, output)
                self._refresh_subtitle()
                return
            self.handle_pending_command(command, output)
            self._refresh_subtitle()
            input_field.focus()
            return

        output.write(f"[bold yellow]🎮 >[/bold yellow] {command}")

        if self.game_state.in_menu:
            self.process_menu_command(command, output)
        else:
            self.process_command(command, output)

        self.command_count += 1
        self._refresh_subtitle()
        if self.game_state.in_game:
            self.check_autosave(command, output)
        input_field.focus()

    # ── In-game command router ────────────────────────────────────────────────

    def process_command(self, command: str, output: RichLog) -> None:
        """
        Process an in-game command and update the output.

        Args:
            command: The command to process
            output: The RichLog widget to write to
        """
        cmd = command.lower()

        if cheat_commands.check_secret_phrase(command, self.game_state, output):
            # If a forced encounter was queued (e.g. Mew secret phrase), trigger it now
            if self.game_state.game_data.get("_forced_encounter"):
                self.trigger_wild_encounter(output)
            return

        if self.game_state.cheat_mode and cmd.startswith("cheat "):
            cheat_commands.process_cheat_command(
                command,
                self.game_state,
                output,
                self.trigger_wild_encounter,
                self.trigger_trainer_encounter,
                lambda cmd: setattr(self, "pending_command", cmd),
                lambda: self.show_battle_action_panel(),
                self.handle_battle_victory,
                self.handle_pokemon_fainted,
                queue_move_learn_callback=self._queue_move_learn,
            )
            return

        # Movement / exploration
        if cmd.startswith("move to ") or cmd.startswith("go to "):
            location_name = (
                command[8:].strip() if cmd.startswith("move to ") else command[6:].strip()
            )
            if location_name:
                self.move_to_location(location_name, output)
            else:
                self.prompt_for_location(output)
        elif cmd in ("move to", "go to"):
            self.prompt_for_location(output)
        elif cmd.startswith("enter "):
            building_name = command[6:].strip()
            if building_name:
                self.enter_building(building_name, output)
            else:
                self.prompt_for_building(output)
        elif cmd == "enter":
            self.prompt_for_building(output)
        elif cmd in ("look around", "look"):
            exploration.look_around(self.game_state, output)
        elif cmd in ("explore area", "explore"):
            exploration.explore_area(
                self.game_state, output, self.trigger_wild_encounter, self.trigger_trainer_encounter
            )

        # Menu / save / settings
        elif cmd in ("go to main menu", "menu", "main menu"):
            self.return_to_menu(output)
        elif cmd in ("save game", "save"):
            self.save_current_game(output)
        elif cmd in ("show help", "help", "commands", "h"):
            self.show_help(output)
        elif cmd in ("show status", "status"):
            self.show_game_status(output)
        elif cmd in ("map", "show map", "kanto map"):
            self.show_map(output)

        # Party / bag / badges
        elif cmd in ("show party", "party", "check party"):
            self.show_party(output)
        elif cmd in ("show bag", "bag", "check bag"):
            self.show_bag(output)

        # Item usage
        elif cmd.startswith("use "):
            self._handle_use_item_command(command, output)

        elif cmd in ("show badges", "badges", "badge case", "badge"):
            self.show_badge_case(output)

        # Statistics
        elif cmd in ("stats", "show stats", "statistics", "adventure stats"):
            self.show_adventure_stats(output)

        # Pokedex
        elif cmd in ("show pokedex", "show pokedex all", "pokedex", "dex", "pokedex all"):
            self.show_pokedex(output, "all")
        elif cmd in ("show pokedex seen", "pokedex seen", "dex seen"):
            self.show_pokedex(output, "seen")
        elif cmd in ("show pokedex caught", "pokedex caught", "dex caught"):
            self.show_pokedex(output, "caught")
        elif cmd in ("show pokedex missing", "pokedex missing", "dex missing"):
            self.show_pokedex(output, "missing")
        elif cmd in ("show next pokedex page", "pokedex next", "dex next"):
            self.pokedex_next_page(output)
        elif cmd in (
            "show previous pokedex page",
            "pokedex prev",
            "dex prev",
            "pokedex previous",
            "dex previous",
        ):
            self.pokedex_prev_page(output)
        elif (
            cmd.startswith("show pokedex page ")
            or cmd.startswith("pokedex page ")
            or cmd.startswith("dex page ")
        ):
            parts = command.split()
            page_token = parts[-1]
            if page_token.isdigit():
                self.pokedex_goto_page(output, int(page_token))
            else:
                write_lines(output, terminal_text.USAGE_SHOW_POKEDEX_PAGE)
        elif cmd.startswith("show pokedex entry "):
            self.show_pokedex_entry(output, command[19:].strip())
        elif (
            cmd.startswith("pokedex ") or cmd.startswith("dex ") or cmd.startswith("show pokedex ")
        ):
            parts = command.split(maxsplit=1)
            if len(parts) >= 2:
                pokemon_search = parts[1].strip()
                search_lower = pokemon_search.lower()
                if search_lower in ("all", "seen", "caught", "missing"):
                    self.show_pokedex(output, search_lower)
                elif search_lower == "next":
                    self.pokedex_next_page(output)
                elif search_lower in ("prev", "previous"):
                    self.pokedex_prev_page(output)
                elif search_lower.startswith("page "):
                    page_parts = pokemon_search.split()
                    if len(page_parts) >= 2 and page_parts[1].isdigit():
                        self.pokedex_goto_page(output, int(page_parts[1]))
                elif search_lower.startswith("entry "):
                    self.show_pokedex_entry(output, pokemon_search[6:].strip())
                else:
                    self.show_pokedex_entry(output, pokemon_search)
            else:
                self.show_pokedex(output, "all")
        elif cmd.startswith("inspect "):
            target = command[8:].strip()
            if target:
                self.inspect_pokemon(output, target)
            else:
                write_lines(output, terminal_text.USAGE_INSPECT)

        # Autosave settings
        elif cmd in ("show settings", "settings"):
            self.show_settings(output)
        elif cmd == "enable autosave":
            self.game_state.autosave_enabled = True
            write_lines_fmt(
                output,
                terminal_text.AUTOSAVE_ENABLED,
                frequency=self.game_state.autosave_frequency,
            )
        elif cmd == "disable autosave":
            self.game_state.autosave_enabled = False
            write_lines(output, terminal_text.AUTOSAVE_DISABLED)
        elif cmd.startswith("set autosave frequency ") or cmd.startswith("autosave "):
            parts = cmd.split()
            setting = parts[-1]
            if setting == "on":
                self.game_state.autosave_enabled = True
                write_lines_fmt(
                    output,
                    terminal_text.AUTOSAVE_ENABLED,
                    frequency=self.game_state.autosave_frequency,
                )
            elif setting == "off":
                self.game_state.autosave_enabled = False
                write_lines(output, terminal_text.AUTOSAVE_DISABLED)
            elif setting.isdigit():
                frequency = int(setting)
                if 5 <= frequency <= 100:
                    self.game_state.autosave_frequency = frequency
                    write_lines_fmt(
                        output,
                        terminal_text.AUTOSAVE_FREQUENCY_SET,
                        frequency=frequency,
                    )
                else:
                    write_lines(output, terminal_text.AUTOSAVE_FREQUENCY_RANGE_ERROR)
            else:
                self.show_settings(output)
        elif cmd == "autosave":
            self.show_settings(output)

        # Misc
        elif cmd == "hello":
            output.write("[green]👋 Hello, Trainer![/green]")
        elif cmd in ("oh no, i overslept", "oh no i overslept"):
            self.activate_pikachu_mode(output)
        elif cmd in ("show about", "about"):
            self.show_about(output)
        elif cmd in ("clear output", "clear"):
            output.clear()
            output.write("[dim]Output cleared[/dim]")
        elif cmd in ("pc", "use pc", "bill's pc", "check pc"):
            write_lines(output, terminal_text.PC_CENTER_REQUIRED)
        elif cmd in ("ride bike", "ride bicycle", "use bike", "use bicycle", "cycle", "bike"):
            items = self.game_state.game_data.get("items", {})
            if not items.get("Bicycle"):
                write_lines(output, terminal_text.NO_BICYCLE)
            elif (
                not self.game_state.current_location
                or not self.game_state.current_location.can_explore()
            ):
                write_lines(output, terminal_text.BICYCLE_LOCATION_RESTRICTED)
            else:
                cycling = self.game_state.game_data.get("cycling", False)
                if cycling:
                    self.game_state.game_data["cycling"] = False
                    write_lines(output, terminal_text.BICYCLE_OFF)
                else:
                    self.game_state.game_data["cycling"] = True
                    write_lines(output, terminal_text.BICYCLE_ON)

        # Fishing
        elif (
            cmd in ("fish", "go fishing")
            or cmd.startswith("fish with ")
            or cmd.startswith("go fishing with ")
        ):
            self._handle_fish_command(command, output)

        # HM field use — "use surf", "use fly", "use cut", "use strength", "use flash"
        elif cmd in ("use surf", "surf"):
            self._handle_hm_field(output, "SURF")
        elif cmd in ("use fly", "fly"):
            self._handle_hm_field(output, "FLY")
        elif cmd in ("use cut", "cut"):
            self._handle_hm_field(output, "CUT")
        elif cmd in ("use strength", "strength"):
            self._handle_hm_field(output, "STRENGTH")
        elif cmd in ("use flash", "flash"):
            self._handle_hm_field(output, "FLASH")
        elif cmd.startswith("fly to "):
            destination = command[7:].strip()
            if destination:
                _hm_tm.fly_to_town(self.game_state, destination, output)
            else:
                self._handle_hm_field(output, "FLY")

        elif cmd in ("exit safari zone", "leave safari zone"):
            if (
                self.game_state.current_location
                and self.game_state.current_location.name == "Safari Zone"
            ):
                from .locations import get_location

                fuchsia = get_location("Fuchsia City")
                if fuchsia:
                    self.game_state.game_data["previous_location"] = "Safari Zone"
                    self.game_state.current_location = fuchsia
                    self.game_state.game_data["location"] = "Fuchsia City"
                    output.write("")
                    output.write(
                        "[bold cyan]➜ You leave the Safari Zone through the gatehouse...[/bold cyan]"
                    )
                    output.write("")
                    self.show_location_arrival(output)
            else:
                output.write("")
                output.write("[yellow]⚠  You're not in the Safari Zone.[/yellow]")
                output.write("")

        elif cmd in ("exit", "exit building", "leave building"):
            write_lines(output, terminal_text.NOT_INSIDE_BUILDING)
            return

        elif cmd in ("quit game", "quit", "stop", "stop playing", "q"):
            self.prompt_for_quit(output)

        # ── Phase 4 building shortcuts ────────────────────────────────────────
        elif cmd in ("silph co", "silph co.", "silph"):
            self.enter_building("Silph Co.", output)
        elif cmd in ("pokemon mansion", "mansion"):
            self.enter_building("Pokemon Mansion", output)
        elif cmd in ("pokemon lab", "cinnabar lab"):
            self.enter_building("Pokemon Lab", output)

        # ── Phase 4 location shortcuts ───────────────────────────────────────
        elif cmd in (
            "go saffron city",
            "go saffron",
            "saffron city",
            "saffron",
            "move saffron",
            "move saffron city",
        ):
            self.move_to_location("Saffron City", output)
        elif cmd in (
            "go cinnabar island",
            "go cinnabar",
            "cinnabar island",
            "cinnabar",
            "move cinnabar",
            "move cinnabar island",
        ):
            self.move_to_location("Cinnabar Island", output)
        elif cmd in ("go victory road", "victory road", "move victory road"):
            self.move_to_location("Victory Road", output)
        elif cmd in (
            "go pokemon league",
            "pokemon league",
            "move pokemon league",
            "indigo plateau",
        ):
            self.move_to_location("Pokemon League", output)

        # ── Phase 5 building shortcuts ────────────────────────────────────────
        elif cmd in ("elite four", "enter elite four", "challenge elite four", "face elite four"):
            self.enter_building("Elite Four", output)
        elif cmd in ("hall of fame", "enter hall of fame"):
            self.enter_building("Hall of Fame", output)
        elif cmd in ("reception", "league reception", "pokemon league reception"):
            self.enter_building("Pokemon League Reception", output)

        # ── Fossil revival shortcut ─────────────────────────────────────────
        elif cmd in ("revive fossil", "fossil revival", "revive fossils"):
            if (
                not self.game_state.current_location
                or self.game_state.current_location.name != "Cinnabar Island"
            ):
                output.write("")
                output.write(
                    "[yellow]⚠ You need to go to the Pokemon Lab on Cinnabar Island"
                    " to revive fossils.[/yellow]"
                )
                output.write("[dim]Travel to Cinnabar Island and enter the Pokemon Lab.[/dim]")
                output.write("")
            else:
                from . import buildings as _bld

                _bld.enter_pokemon_lab(self.game_state, output)

        else:
            output.write(f"[red]❌ Unknown command:[/red] {command}")
            output.write("[dim]Type 'help' to see available commands[/dim]")

        output.write("")

    # ── Display delegates ────────────────────────────────────────────────────

    def activate_pikachu_mode(self, output: RichLog) -> None:
        """Activate Pokemon Yellow Easter egg mode."""
        displays.activate_pikachu_mode(self.game_state, output)

    def open_pc(self, output: RichLog) -> None:
        """Open Bill's PC storage system."""
        pc_system.show_pc_menu(self.game_state, output)
        self.pending_command = "pc"

    def show_party(self, output: RichLog) -> None:
        """Display the Pokemon party as a tabbed panel."""
        self.show_party_panel()

    def show_bag(self, output: RichLog) -> None:
        """Display the items in the bag."""
        displays.show_bag(self.game_state, output)

    def _handle_use_item_command(self, command: str, output: RichLog) -> None:
        """Parse and execute a 'use <item> [on <pokemon>]' command.

        Examples: ``use potion`` / ``use fire stone on eevee`` / ``use revive on 2``
        """
        # Strip leading "use " (case-insensitive already handled by cmd)
        rest = command[4:].strip()

        # Split on " on " to extract optional target
        lower_rest = rest.lower()
        if " on " in lower_rest:
            split_pos = lower_rest.index(" on ")
            item_name_raw = rest[:split_pos].strip()
            target_raw = rest[split_pos + 4 :].strip()
        else:
            item_name_raw = rest
            target_raw = None

        if not item_name_raw:
            write_lines(output, terminal_text.USAGE_USE_ITEM)
            return

        # Delegate all logic (including error messages) to items module
        _items.use_item_outside_battle(
            self.game_state,
            item_name_raw,
            target_raw,
            output,
            queue_move_learn_callback=self._queue_move_learn,
        )

    def show_badge_case(self, output: RichLog) -> None:
        """Display the badge case."""
        displays.show_badge_case(self.game_state, output)

    def _handle_fish_command(self, command: str, output: RichLog) -> None:
        """Parse and execute a fishing command.

        Examples: ``fish`` / ``fish with old rod`` / ``go fishing with super rod``
        """
        cmd = command.lower()
        rod_hint = None
        if "with " in cmd:
            rod_hint = command[cmd.index("with ") + 5 :].strip()

        _fishing.start_fishing(
            self.game_state,
            output,
            self._trigger_fishing_encounter,
            rod_hint,
        )

    def _trigger_fishing_encounter(self, output: RichLog, species: str, level: int) -> None:
        """Trigger a wild encounter with a specific fishing Pokemon."""
        species_upper = species.upper()

        # Build a wild Pokemon dict for the encounter
        species_data = get_pokemon(species_upper)
        if species_data is None:
            # Fallback: stub entry
            for _num, pdata in POKEMON.items():
                if pdata.name == species_upper:
                    species_data = pdata
                    break

        if species_data is None:
            output.write(f"[yellow]⚠ Pokemon data for {species_upper} not found.[/yellow]")
            return

        # Store the forced species on game_state so trigger_wild_encounter can use it
        self.game_state.game_data["_fishing_encounter"] = {
            "species": species_upper,
            "level": level,
        }
        self.trigger_wild_encounter(output)

    def _handle_hm_field(self, output: RichLog, move_name: str) -> None:
        """Handle HM field use (outside battle).

        Args:
            output:    RichLog widget.
            move_name: Upper-case HM move name (e.g. ``"SURF"``).
        """
        _hm_tm.use_hm_field(self.game_state, move_name, output)

    def show_map(self, output: RichLog) -> None:
        """Display the Kanto region map."""
        displays.show_map(self.game_state, output)

    def show_adventure_stats(self, output: RichLog) -> None:
        """Display battle and exploration statistics."""
        _stats.show_stats(self.game_state, output)

    def show_pokedex(
        self, output: RichLog, filter_mode: str = "all", page: Optional[int] = None
    ) -> None:
        """Display the Pokedex with pagination."""
        pokedex.show_pokedex(self.game_state, output, filter_mode, page)
        self.show_pokedex_navigation()

    def pokedex_next_page(self, output: RichLog) -> None:
        """Navigate to next Pokedex page."""
        view_state = pokedex.get_pokedex_state(self.game_state)
        pokedex.show_pokedex(
            self.game_state,
            output,
            view_state.get("filter_mode", "all"),
            view_state.get("current_page", 1) + 1,
        )
        self.show_pokedex_navigation()

    def pokedex_prev_page(self, output: RichLog) -> None:
        """Navigate to previous Pokedex page."""
        view_state = pokedex.get_pokedex_state(self.game_state)
        current_page = view_state.get("current_page", 1)
        if current_page > 1:
            pokedex.show_pokedex(
                self.game_state, output, view_state.get("filter_mode", "all"), current_page - 1
            )
            self.show_pokedex_navigation()
        else:
            write_lines(output, terminal_text.POKEDEX_FIRST_PAGE_ALREADY)

    def pokedex_first_page(self, output: RichLog) -> None:
        """Navigate to the first Pokedex page."""
        view_state = pokedex.get_pokedex_state(self.game_state)
        pokedex.show_pokedex(self.game_state, output, view_state.get("filter_mode", "all"), 1)
        self.show_pokedex_navigation()

    def pokedex_last_page(self, output: RichLog) -> None:
        """Navigate to the last Pokedex page."""
        view_state = pokedex.get_pokedex_state(self.game_state)
        filter_mode = view_state.get("filter_mode", "all")
        pokedex_data = self.game_state.game_data.get("pokedex", {})
        seen = set(pokedex_data.get("seen", []))
        caught = set(pokedex_data.get("caught", []))
        filtered_count = sum(
            1
            for _, d in POKEMON.items()
            if filter_mode == "all"
            or (filter_mode == "seen" and d["name"] in seen)
            or (filter_mode == "caught" and d["name"] in caught)
            or (filter_mode == "missing" and d["name"] not in seen)
        )
        total_pages = (
            math.ceil(filtered_count / pokedex.POKEMON_PER_PAGE) if filtered_count > 0 else 1
        )
        pokedex.show_pokedex(self.game_state, output, filter_mode, total_pages)
        self.show_pokedex_navigation()

    def pokedex_goto_page(self, output: RichLog, page_num: int) -> None:
        """Go to specific Pokedex page."""
        view_state = pokedex.get_pokedex_state(self.game_state)
        if page_num < 1:
            write_lines(output, terminal_text.POKEDEX_PAGE_MINIMUM)
        else:
            pokedex.show_pokedex(
                self.game_state, output, view_state.get("filter_mode", "all"), page_num
            )
            self.show_pokedex_navigation()

    def show_pokedex_entry(self, output: RichLog, species: str) -> None:
        """Display a specific Pokedex entry."""
        pokedex.show_pokedex_entry(self.game_state, output, species)

    def inspect_pokemon(self, output: RichLog, target: str) -> None:
        """Display detailed information about a specific Pokemon."""
        displays.inspect_pokemon(self.game_state, output, target, self.ensure_battle_ready)

    def show_help(self, output: RichLog) -> None:
        """Display help information."""
        displays.show_help(self.game_state, output)

    def show_game_status(self, output: RichLog) -> None:
        """Display current game status."""
        displays.show_game_status(self.game_state, output, self.show_status)

    def show_status(self, output: RichLog) -> None:
        """Display application status."""
        displays.show_status(
            self.game_state, output, self.command_count, self.TITLE, self.SUB_TITLE
        )

    def show_about(self, output: RichLog) -> None:
        """Display about information."""
        displays.show_about(output)

    # ── Textual actions ──────────────────────────────────────────────────────

    def action_help(self) -> None:
        """Show help (bound to 'h' key)."""
        output = self.query_one("#output", RichLog)
        self.show_help(output)
        output.write("")

    async def action_quit(self) -> None:
        """Quit the application (bound to 'q' and Ctrl+C)."""
        output = self.query_one("#output", RichLog)
        self.prompt_for_quit(output)


# ── Module entry point ───────────────────────────────────────────────────────


def launch_terminal() -> None:
    """Launch the Pokemon terminal application."""
    app = PokemonTerminal()
    try:
        app.run()
    finally:
        lock_file = os.environ.get("POKEMON_LOCK_FILE")
        if lock_file:
            try:
                Path(lock_file).unlink()
            except Exception:
                pass


if __name__ == "__main__":
    launch_terminal()
