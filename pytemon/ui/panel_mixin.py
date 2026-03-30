"""
Panel management mixin for PokemonTerminal.

All show_*/hide_* methods that toggle Textual widget visibility live here,
keeping the main terminal.py focused on app structure and event routing.
"""

import json
import math
from pathlib import Path
from typing import TYPE_CHECKING, List

from textual.widgets import Button, DataTable, Input, RichLog, Select, Static, TabbedContent

from .. import gym_system, pc_system, pokedex
from ..buildings import SHOP_CATALOG
from ..data import POKEMON, get_move, get_trainer
from .displays import populate_party_detail, populate_party_overview, show_party

if TYPE_CHECKING:
    pass  # Avoid circular imports — self is always a PokemonTerminal at runtime


def _format_last_move(move_result: "dict | None") -> str:
    """Format a last-move result dict into a Rich-markup string for the HUD."""
    if not move_result:
        return ""
    name = move_result["name"]
    if move_result.get("missed"):
        return f"Last: [dim]{name} (no effect)[/dim]"

    parts: list[str] = [f"Last: [bold]{name}[/bold]"]

    dmg = move_result.get("damage", 0)
    if dmg:
        parts.append(f"[cyan]{dmg} dmg[/cyan]")

    if move_result.get("crit"):
        parts.append("[bold yellow]Crit![/bold yellow]")

    eff = move_result.get("effectiveness", "")
    if "super effective" in eff:
        parts.append("[green]Super![/green]")
    elif "not very effective" in eff:
        parts.append("[dim]Weak[/dim]")

    status = move_result.get("status_applied")
    if status:
        _status_labels = {
            "PARALYSIS": "[yellow]PAR[/yellow]",
            "SLEEP": "[dim]SLP[/dim]",
            "POISON": "[magenta]PSN[/magenta]",
            "BAD_POISON": "[magenta]TOX[/magenta]",
            "BURN": "[red]BRN[/red]",
            "FREEZE": "[bold cyan]FRZ[/bold cyan]",
        }
        parts.append(_status_labels.get(status, f"[yellow]{status}[/yellow]"))

    for change in move_result.get("stat_changes", []):
        arrow = (
            "\u2193" * abs(change["delta"]) if change["delta"] < 0 else "\u2191" * change["delta"]
        )
        color = "yellow" if change["delta"] < 0 else "green"
        parts.append(f"[{color}]{change['stat'].upper()[:3]}{arrow}[/{color}]")

    return "  ".join(parts)


def _format_stat_stages(stages: dict) -> str:
    """Format a stat-stages dict into a Rich-markup string for the HUD."""
    if not stages:
        return ""
    abbrevs = {
        "attack": "ATK",
        "defense": "DEF",
        "speed": "SPD",
        "special": "SPEC",
        "accuracy": "ACC",
        "evasion": "EVA",
    }
    parts: list[str] = []
    for stat, delta in sorted(stages.items()):
        if delta == 0:
            continue
        label = abbrevs.get(stat, stat.upper()[:3])
        arrow = "\u2193" * abs(delta) if delta < 0 else "\u2191" * delta
        color = "yellow" if delta < 0 else "green"
        parts.append(f"[{color}]{label}{arrow}[/{color}]")
    return "  ".join(parts)


class PanelMixin:
    """Mixin that provides all panel show/hide helpers for PokemonTerminal."""

    # ── Main menu ────────────────────────────────────────────────────────────

    def show_main_menu_action_panel(self) -> None:
        """Show the main menu action button panel."""
        main_menu_panel = self.query_one("#main-menu-actions")
        main_menu_panel.remove_class("hidden")

    # ── Battle ───────────────────────────────────────────────────────────────

    def show_battle_action_panel(self) -> None:
        """Show the battle action button panel."""
        battle_panel = self.query_one("#battle-actions")
        move_panel = self.query_one("#move-selection")
        battle_panel.remove_class("hidden")
        move_panel.add_class("hidden")
        try:
            self.query_one("#battle-bag").add_class("hidden")
            self.query_one("#pokemon-switch").add_class("hidden")
            self.query_one("#faint-switch").add_class("hidden")
            self.hide_battle_loading()
        except Exception:
            pass

    def show_battle_loading(self) -> None:
        """Show the battle loading indicator while a turn is being processed."""
        try:
            self.query_one("#battle-loading").remove_class("hidden")
        except Exception:
            pass

    def hide_battle_loading(self) -> None:
        """Hide the battle loading indicator."""
        try:
            self.query_one("#battle-loading").add_class("hidden")
        except Exception:
            pass

    def show_battle_loading_panel(self) -> None:
        """Replace the bottom battle panel with the loading indicator.

        Hides only the action/move sub-panels — the battle HUDs are intentionally
        left untouched so the layout does not shift during turn animation.
        """
        try:
            self.query_one("#battle-actions").add_class("hidden")
            self.query_one("#move-selection").add_class("hidden")
        except Exception:
            pass
        try:
            self.query_one("#battle-bag").add_class("hidden")
            self.query_one("#pokemon-switch").add_class("hidden")
            self.query_one("#faint-switch").add_class("hidden")
        except Exception:
            pass
        self.show_battle_loading()

    def show_battle_bag_panel(self) -> None:
        """Show the battle bag panel, populating buttons with current inventory counts."""
        try:
            items = self.game_state.game_data.get("items", {})
            battle_state = self.game_state.battle_state
            player_status = battle_state.player_pokemon.get("status") if battle_state else None

            def _setup(btn_id: str, label: str, count: int, enabled: bool = True) -> None:
                try:
                    btn = self.query_one(f"#{btn_id}", Button)
                    btn.label = f"{label} x{count}" if count > 0 else label
                    btn.disabled = count <= 0 or not enabled
                except Exception:
                    pass

            _setup("btn-bag-pokeball", "🔴 Throw Pokeball", items.get("Pokeball", 0))
            _setup("btn-bag-potion", "💊 Potion", items.get("Potion", 0))
            _setup("btn-bag-super-potion", "💊 Super Potion", items.get("Super Potion", 0))
            _setup(
                "btn-bag-antidote",
                "💜 Antidote",
                items.get("Antidote", 0),
                player_status == "POISON",
            )
            _setup(
                "btn-bag-paralyze-heal",
                "💛 Paralyze Heal",
                items.get("Paralyze Heal", 0),
                player_status == "PARALYSIS",
            )
            _setup(
                "btn-bag-awakening",
                "💙 Awakening",
                items.get("Awakening", 0),
                player_status == "SLEEP",
            )

            self.query_one("#battle-actions").add_class("hidden")
            self.query_one("#move-selection").add_class("hidden")
            self.query_one("#battle-bag").remove_class("hidden")
        except Exception:
            pass

    def show_move_selection_panel(self) -> None:
        """Show the move selection button panel and update button labels."""
        battle_panel = self.query_one("#battle-actions")
        move_panel = self.query_one("#move-selection")
        battle_panel.add_class("hidden")
        move_panel.remove_class("hidden")

        # Update move buttons with actual move data
        if self.game_state.battle_state:
            player = self.game_state.battle_state.player_pokemon
            moves = player.get("moves", [])

            TYPE_COLORS = {
                "Normal": "normal",
                "Fire": "fire",
                "Water": "water",
                "Grass": "grass",
                "Electric": "electric",
                "Ice": "water",
                "Fighting": "fire",
                "Poison": "grass",
                "Ground": "normal",
                "Flying": "normal",
                "Psychic": "electric",
                "Bug": "grass",
                "Rock": "normal",
                "Ghost": "normal",
                "Dragon": "electric",
            }

            for i in range(4):
                button_id = f"btn-move-{i}"
                try:
                    button = self.query_one(f"#{button_id}", Button)
                    if i < len(moves):
                        move = moves[i]
                        move_data = get_move(move["name"])
                        pp_info = f" ({move['pp']}/{move.get('max_pp', move['pp'])} PP)"
                        button.label = f"{move['name'].upper()}{pp_info}"
                        button.disabled = move["pp"] <= 0
                        if move_data:
                            move_type = move_data.get("type", "Normal")
                            color_class = TYPE_COLORS.get(move_type, "normal")
                            for old_class in [
                                "move-button-normal",
                                "move-button-fire",
                                "move-button-water",
                                "move-button-grass",
                                "move-button-electric",
                            ]:
                                button.remove_class(old_class)
                            button.add_class(f"move-button-{color_class}")
                    else:
                        button.label = "---"
                        button.disabled = True
                        for old_class in [
                            "move-button-normal",
                            "move-button-fire",
                            "move-button-water",
                            "move-button-grass",
                            "move-button-electric",
                        ]:
                            button.remove_class(old_class)
                        button.add_class("move-button-normal")
                except Exception:
                    pass

    def show_faint_switch_panel(self, can_run: bool = False) -> None:
        """Show the faint-switch panel after the active Pokemon faints.

        Populates slot buttons from the party, excluding fainted Pokemon.
        Shows the Run Away button only in wild battles (can_run=True).

        Args:
            can_run: Whether the player is allowed to run (False in trainer battles)
        """
        try:
            battle = self.game_state.battle_state
            party = self.game_state.game_data.get("pokemon", [])
            active = battle.player_pokemon if battle else None

            for i in range(6):
                btn = self.query_one(f"#btn-faint-slot-{i}", Button)
                if i < len(party) and not isinstance(party[i], str):
                    p = party[i]
                    is_active = p is active
                    is_fainted = p["hp"] <= 0
                    status = p.get("status") or ""
                    status_str = f" [{status}]" if status else ""
                    hp_str = " (Fainted)" if is_fainted else f" {p['hp']}/{p['max_hp']}HP"
                    active_str = " ← Fainted" if is_active else ""
                    btn.label = f"{p['name']} Lv.{p['level']}{status_str}{active_str}{hp_str}"
                    btn.disabled = is_fainted or is_active
                    btn.remove_class("hidden")
                else:
                    btn.label = f"--- Slot {i + 1} empty ---"
                    btn.disabled = True
                    btn.add_class("hidden")

            # Run Away button: visible only in wild battles
            run_btn = self.query_one("#btn-faint-run", Button)
            if can_run:
                run_btn.remove_class("hidden")
            else:
                run_btn.add_class("hidden")

            self.query_one("#battle-actions").add_class("hidden")
            self.query_one("#move-selection").add_class("hidden")
            self.query_one("#battle-bag").add_class("hidden")
            self.query_one("#pokemon-switch").add_class("hidden")
            self.query_one("#faint-switch").remove_class("hidden")
        except Exception:
            pass

    def show_pokemon_switch_panel(self) -> None:
        """Show the pokemon switch button panel, updating slot buttons from current party."""
        try:
            battle = self.game_state.battle_state
            party = self.game_state.game_data.get("pokemon", [])
            active = battle.player_pokemon if battle else None

            for i in range(6):
                btn = self.query_one(f"#btn-switch-slot-{i}", Button)
                if i < len(party) and not isinstance(party[i], str):
                    p = party[i]
                    is_active = p is active
                    is_fainted = p["hp"] <= 0
                    hp_pct = int(p["hp"] / p["max_hp"] * 100) if p["max_hp"] > 0 else 0
                    status = p.get("status") or ""
                    status_str = f" [{status}]" if status else ""
                    active_str = " ← Active" if is_active else ""
                    fainted_str = " (Fainted)" if is_fainted else f" {p['hp']}/{p['max_hp']}HP"
                    btn.label = f"{p['name']} Lv.{p['level']}{status_str}{active_str}{fainted_str}"
                    btn.disabled = is_active or is_fainted
                    btn.remove_class("hidden")
                else:
                    btn.label = f"--- Slot {i + 1} empty ---"
                    btn.disabled = True
                    btn.add_class("hidden")

            self.query_one("#battle-actions").add_class("hidden")
            self.query_one("#move-selection").add_class("hidden")
            self.query_one("#battle-bag").add_class("hidden")
            self.query_one("#pokemon-switch").remove_class("hidden")
        except Exception:
            pass

    def show_choose_lead_panel(self, non_fainted: list) -> None:
        """Show the choose-lead panel with a 2×3 grid of Pokemon buttons.

        Populates each button from ``non_fainted`` (a list of party Pokemon that
        are alive and eligible to be sent first).  Slots beyond the party size are
        hidden and disabled.

        Args:
            non_fainted: Ordered list of non-fainted party Pokemon dicts / PartyPokemon objects.
        """
        try:
            # Lead selection cannot be canceled; hide the cancel button for this panel.
            self.query_one("#btn-lead-cancel", Button).display = False

            for i in range(6):
                btn = self.query_one(f"#btn-lead-slot-{i}", Button)
                if i < len(non_fainted):
                    p = non_fainted[i]
                    hp = p.get("hp", 0)
                    max_hp = p.get("max_hp", 1)
                    status = p.get("status") or ""
                    status_str = f" [{status}]" if status else ""
                    hp_str = f" {hp}/{max_hp}HP"
                    btn.label = f"{p['name']} Lv.{p.get('level', 5)}{status_str}{hp_str}"
                    btn.disabled = False
                    btn.remove_class("hidden")
                else:
                    btn.label = f"--- Empty ---"
                    btn.disabled = True
                    btn.add_class("hidden")

            self.query_one("#choose-lead-panel").remove_class("hidden")
        except Exception:
            pass

    def hide_choose_lead_panel(self) -> None:
        """Hide the choose-lead panel."""
        try:
            self.query_one("#choose-lead-panel").add_class("hidden")
        except Exception:
            pass

    def hide_all_battle_panels(self) -> None:
        """Hide all battle-related button panels and the battle HUD."""
        try:
            self.query_one("#battle-actions").add_class("hidden")
            self.query_one("#move-selection").add_class("hidden")
            self.query_one("#battle-bag").add_class("hidden")
            self.query_one("#pokemon-switch").add_class("hidden")
            self.query_one("#faint-switch").add_class("hidden")
            self.query_one("#choose-lead-panel").add_class("hidden")
            self.query_one("#hud-player").add_class("hidden")
            self.query_one("#hud-enemy").add_class("hidden")
            self.hide_battle_loading()
        except Exception:
            pass

    def show_battle_hud(self) -> None:
        """Show the player and enemy HUD panels inside the battle screen."""
        try:
            self.query_one("#hud-player").remove_class("hidden")
            self.query_one("#hud-enemy").remove_class("hidden")
        except Exception:
            pass

    def update_battle_hud(self) -> None:
        """Refresh all battle HUD widgets from the current battle state."""
        battle = self.game_state.battle_state
        if not battle:
            return
        try:
            from textual.widgets import ProgressBar, Static

            wild = battle.wild_pokemon
            player = battle.player_pokemon

            status_badges = {
                "BURN": " 🔥BRN",
                "POISON": " ☠PSN",
                "BAD_POISON": " ☠☠TOX",
                "PARALYSIS": " ⚡PAR",
                "SLEEP": " 💤SLP",
                "FREEZE": " ❄FRZ",
            }

            wild_status = status_badges.get(wild.get("status") or "", "")
            player_status = status_badges.get(player.get("status") or "", "")

            # Enemy name / level / status
            if battle.is_trainer_battle and battle.trainer_data:
                enemy_label = (
                    f"{battle.trainer_data['name']}'s "
                    f"{wild['name']}  Lv.{wild['level']}{wild_status}"
                )
            else:
                enemy_label = f"Wild {wild['name']}  Lv.{wild['level']}{wild_status}"
            self.query_one("#hud-enemy-name", Static).update(enemy_label)

            # Enemy HP bar + text
            enemy_hp = max(0, wild["hp"])
            enemy_max = max(1, wild["max_hp"])
            self.query_one("#hud-enemy-hp-bar", ProgressBar).update(
                total=enemy_max, progress=enemy_hp
            )
            self.query_one("#hud-enemy-hp-text", Static).update(f"HP  {enemy_hp} / {enemy_max}")

            # Enemy moves seen
            seen = sorted(battle.enemy_moves_seen)
            moves_seen_text = "Seen:  " + "  |  ".join(seen) if seen else "Seen:  ???"
            self.query_one("#hud-enemy-moves", Static).update(moves_seen_text)

            # Player name / level / status
            self.query_one("#hud-player-name", Static).update(
                f"{player['name']}  Lv.{player['level']}{player_status}"
            )

            # Player HP bar + text
            player_hp = max(0, player["hp"])
            player_max = max(1, player["max_hp"])
            self.query_one("#hud-player-hp-bar", ProgressBar).update(
                total=player_max, progress=player_hp
            )
            self.query_one("#hud-player-hp-text", Static).update(f"HP  {player_hp} / {player_max}")

            # Player moves with PP
            move_parts = []
            for m in player.get("moves", []):
                max_pp = m.get("max_pp", m["pp"])
                move_parts.append(f"{m['name']} ({m['pp']}/{max_pp}PP)")
            self.query_one("#hud-player-moves", Static).update(
                "  |  ".join(move_parts) if move_parts else ""
            )

            # ── Last move + stat stages ───────────────────────────────────────
            self.query_one("#hud-player-last-move", Static).update(
                _format_last_move(battle.last_player_move)
            )
            self.query_one("#hud-player-stages", Static).update(
                _format_stat_stages(battle.player_stat_stages)
            )
            self.query_one("#hud-enemy-last-move", Static).update(
                _format_last_move(battle.last_enemy_move)
            )
            self.query_one("#hud-enemy-stages", Static).update(
                _format_stat_stages(battle.enemy_stat_stages)
            )
        except Exception:
            pass

    # ── Starter / name selection ─────────────────────────────────────────────

    def show_starter_selection_panel(self, pikachu_mode: bool = False) -> None:
        """Show the starter Pokemon selection button panel."""
        self.hide_all_panels()
        starter_panel = self.query_one("#starter-selection")
        starter_panel.remove_class("hidden")
        try:
            if pikachu_mode:
                taken = " — chosen by another trainer"
                bulb_btn = self.query_one("#btn-starter-bulbasaur", Button)
                bulb_btn.label = f"🌿 Bulbasaur{taken}"
                bulb_btn.disabled = True
                char_btn = self.query_one("#btn-starter-charmander", Button)
                char_btn.label = f"🔥 Charmander{taken}"
                char_btn.disabled = True
                squi_btn = self.query_one("#btn-starter-squirtle", Button)
                squi_btn.label = f"💧 Squirtle{taken}"
                squi_btn.disabled = True
                pika_btn = self.query_one("#btn-starter-pikachu", Button)
                pika_btn.label = "⚡ Pikachu"
                pika_btn.disabled = False
            else:
                bulb_btn = self.query_one("#btn-starter-bulbasaur", Button)
                bulb_btn.label = "🌿 Bulbasaur"
                bulb_btn.disabled = False
                char_btn = self.query_one("#btn-starter-charmander", Button)
                char_btn.label = "🔥 Charmander"
                char_btn.disabled = False
                squi_btn = self.query_one("#btn-starter-squirtle", Button)
                squi_btn.label = "💧 Squirtle"
                squi_btn.disabled = False
                pika_btn = self.query_one("#btn-starter-pikachu", Button)
                pika_btn.label = ""
                pika_btn.disabled = True
        except Exception:
            pass

    def show_name_selection_panel(self) -> None:
        """Show the name selection panel for player and rival names."""
        self.hide_all_panels()
        name_panel = self.query_one("#name-selection")
        name_panel.remove_class("hidden")
        player_input = self.query_one("#input-player-name", Input)
        rival_input = self.query_one("#input-rival-name", Input)
        player_input.value = ""
        rival_input.value = ""
        player_input.focus()

    # ── Location / building selection ────────────────────────────────────────

    def show_location_selection_panel(self, locations: List[str]) -> None:
        """Show the location selection panel with Select dropdown."""
        self.hide_all_panels()
        location_panel = self.query_one("#location-selection")
        location_panel.remove_class("hidden")
        try:
            select = self.query_one("#location-select", Select)
            options = [("Choose a destination...", "")] + [(loc, loc) for loc in locations]
            select.set_options(options)
        except Exception:
            pass

    def show_building_selection_panel(self, buildings: List[str]) -> None:
        """Show the building selection panel with Select dropdown."""
        self.hide_all_panels()
        building_panel = self.query_one("#building-selection")
        building_panel.remove_class("hidden")
        try:
            select = self.query_one("#building-select", Select)
            options = [("Choose a building...", "")] + [(bld, bld) for bld in buildings]
            select.set_options(options)
        except Exception:
            pass

    # ── Master hide-all ──────────────────────────────────────────────────────

    def hide_all_panels(self) -> None:
        """Hide all button panels."""
        try:
            self.query_one("#main-menu-actions").add_class("hidden")
            self.query_one("#battle-actions").add_class("hidden")
            self.query_one("#move-selection").add_class("hidden")
            self.query_one("#battle-bag").add_class("hidden")
            self.query_one("#location-selection").add_class("hidden")
            self.query_one("#building-selection").add_class("hidden")
            self.query_one("#starter-selection").add_class("hidden")
            self.query_one("#name-selection").add_class("hidden")
            self.query_one("#confirmation-panel").add_class("hidden")
            self.query_one("#save-option-panel").add_class("hidden")
            self.query_one("#load-game-panel").add_class("hidden")
            self.query_one("#pokedex-navigation").add_class("hidden")
            self.query_one("#nurse-joy-panel").add_class("hidden")
            self.query_one("#pokemon-center-panel").add_class("hidden")
            self.query_one("#pokemon-center-loading").add_class("hidden")
            self.query_one("#pc-panel").add_class("hidden")
            self.query_one("#pc-deposit-panel").add_class("hidden")
            self.query_one("#pc-withdraw-panel").add_class("hidden")
            self.query_one("#pokemart-panel").add_class("hidden")
            self.query_one("#quit-panel").add_class("hidden")
            self.query_one("#evolution-panel").add_class("hidden")
            self.query_one("#party-panel").add_class("hidden")
            self.query_one("#gym-panel").add_class("hidden")
            self.query_one("#pokemon-switch").add_class("hidden")
            self.query_one("#faint-switch").add_class("hidden")
            self.query_one("#choose-lead-panel").add_class("hidden")
        except Exception:
            pass

    # ── Gym lobby ─────────────────────────────────────────────────────────────

    def show_gym_panel(self) -> None:
        """Show the gym lobby panel, updating dynamic content and button states."""
        self.hide_all_panels()

        location_name = (
            self.game_state.current_location.name if self.game_state.current_location else ""
        )
        gym_data = gym_system.get_gym_data(location_name)
        badge_data = gym_system.get_badge_data(gym_data["badge"]) if gym_data else None
        badge_color = badge_data["color"] if badge_data else "orange3"
        leader_name = badge_data["leader"] if badge_data else "Gym Leader"
        badge_name = gym_data["badge"] if gym_data else "Badge"
        specialty = gym_data.get("specialty", "") if gym_data else ""
        gym_name = gym_data["name"] if gym_data else "Pokemon Gym"

        try:
            self.query_one("#gym-panel-title", Static).update(
                f"[bold {badge_color}]⚔️ {gym_name}[/bold {badge_color}]"
            )
        except Exception:
            pass

        # Build info text
        info_lines: list[str] = []
        info_lines.append(f"[dim]{specialty}[/dim]")
        info_lines.append("")

        has_badge = gym_system.has_badge(self.game_state, badge_name)
        trainer_ids = gym_system.get_gym_trainers(location_name)
        defeated_set = set(self.game_state.game_data.get("defeated_trainers", []))

        if trainer_ids:
            beaten = sum(1 for t in trainer_ids if t in defeated_set)
            total = len(trainer_ids)
            info_lines.append(f"[bold]Gym Trainers:[/bold] {beaten}/{total} defeated")
            for tid in trainer_ids:
                trainer = get_trainer(tid)
                if trainer:
                    if tid in defeated_set:
                        info_lines.append(
                            f"  [green]✓ {trainer.trainer_class} {trainer.name}[/green]"
                        )
                    else:
                        info_lines.append(
                            f"  [yellow]○ {trainer.trainer_class} {trainer.name}[/yellow]"
                        )
            info_lines.append("")

        if has_badge:
            info_lines.append(
                f"[{badge_color}]✓ You have already earned the {badge_name}![/{badge_color}]"
            )
        else:
            info_lines.append(
                f"[dim]{badge_color[0].upper() + badge_color[1:]} challenge: defeat "
                f"{leader_name} to earn the {badge_name}![/dim]"
            )

        try:
            self.query_one("#gym-panel-info", Static).update("\n".join(info_lines))
        except Exception:
            pass

        # Update buttons
        next_trainer_id = gym_system.get_next_gym_trainer(self.game_state, location_name)
        can_challenge, _ = gym_system.can_challenge_gym(self.game_state, location_name)

        try:
            trainer_btn = self.query_one("#btn-gym-trainer", Button)
            if next_trainer_id:
                t = get_trainer(next_trainer_id)
                trainer_btn.label = (
                    f"🥊 Fight {t.trainer_class} {t.name}" if t else "🥊 Fight Trainer"
                )
                trainer_btn.disabled = False
            else:
                trainer_btn.label = "✓ No more trainers"
                trainer_btn.disabled = True
        except Exception:
            pass

        try:
            challenge_btn = self.query_one("#btn-gym-challenge", Button)
            if has_badge:
                challenge_btn.label = "🏆 Badge earned!"
                challenge_btn.disabled = True
            else:
                challenge_btn.label = "⚔️ Challenge Leader"
                challenge_btn.disabled = not can_challenge
        except Exception:
            pass

        try:
            self.query_one("#gym-panel").remove_class("hidden")
        except Exception:
            pass

    # ── Pokedex navigation ───────────────────────────────────────────────────

    def show_pokedex_navigation(self) -> None:
        """Show Pokedex navigation buttons."""
        try:
            panel = self.query_one("#pokedex-navigation")
            panel.remove_class("hidden")

            view_state = pokedex.get_pokedex_state(self.game_state)
            current_page = view_state.get("current_page", 1)
            filter_mode = view_state.get("filter_mode", "all")

            pokedex_data = self.game_state.game_data.get("pokedex", {})
            seen = set(pokedex_data.get("seen", []))
            caught = set(pokedex_data.get("caught", []))

            filtered_count = 0
            for _, species_data in POKEMON.items():
                species_name = species_data.get("name", "")
                is_seen = species_name in seen
                is_caught = species_name in caught
                if filter_mode == "all":
                    filtered_count += 1
                elif filter_mode == "seen" and is_seen:
                    filtered_count += 1
                elif filter_mode == "caught" and is_caught:
                    filtered_count += 1
                elif filter_mode == "missing" and not is_seen:
                    filtered_count += 1

            total_pages = (
                math.ceil(filtered_count / pokedex.POKEMON_PER_PAGE) if filtered_count > 0 else 1
            )

            first_button = self.query_one("#btn-pokedex-first", Button)
            prev_button = self.query_one("#btn-pokedex-prev", Button)
            next_button = self.query_one("#btn-pokedex-next", Button)
            last_button = self.query_one("#btn-pokedex-last", Button)

            first_button.disabled = current_page <= 1
            prev_button.disabled = current_page <= 1
            next_button.disabled = current_page >= total_pages
            last_button.disabled = current_page >= total_pages
        except Exception:
            pass

    def hide_pokedex_navigation(self) -> None:
        """Hide Pokedex navigation buttons."""
        try:
            self.query_one("#pokedex-navigation").add_class("hidden")
        except Exception:
            pass

    # ── Confirmation / save / load panels ───────────────────────────────────

    def show_confirmation_panel(
        self, title: str, confirmation_type: str, show_cancel: bool = True
    ) -> None:
        """Show the yes/no confirmation button panel."""
        self.hide_all_panels()
        try:
            self.query_one("#confirmation-title", Static).update(title)
        except Exception:
            pass
        try:
            cancel_btn = self.query_one("#btn-confirm-cancel", Button)
            cancel_btn.display = show_cancel
        except Exception:
            pass
        self.pending_command_data["confirmation_type"] = confirmation_type
        self.query_one("#confirmation-panel").remove_class("hidden")

    def show_save_option_panel(self, current_save_name: str) -> None:
        """Show the save option button panel (overwrite vs new save)."""
        self.hide_all_panels()
        try:
            self.query_one("#save-option-title", Static).update(
                f"💾 Current save: [cyan]{current_save_name}[/cyan] - What would you like to do?"
            )
        except Exception:
            pass
        try:
            self.query_one(
                "#btn-save-overwrite", Button
            ).label = f"✓ Overwrite '{current_save_name}'"
        except Exception:
            pass
        self.query_one("#save-option-panel").remove_class("hidden")

    def show_load_game_panel(self, saves: List[Path]) -> None:
        """Show the load game panel with the DataTable widget."""
        self.hide_all_panels()
        # Reset any previously selected save so the user must click a row
        self._selected_save_name = None
        try:
            table = self.query_one("#saves-table", DataTable)

            table.clear(columns=True)
            table.add_column("Save Name", key="name")
            table.add_column("Location", key="location")
            table.add_column("Badges", key="badges")
            table.add_column("Party", key="party")
            table.add_column("Unique Pokémon", key="caught")

            first_save = None
            for save_file in saves:
                save_name = save_file.stem
                try:
                    with open(save_file) as f:
                        data = json.load(f)
                    location = data.get("location", "Unknown")
                    raw_badges = data.get("badges", [])
                    badges = (
                        str(len(raw_badges)) if isinstance(raw_badges, list) else str(raw_badges)
                    )
                    party = data.get("pokemon", [])
                    if party:
                        party_names = [
                            f"{p.get('name', '???')} (Lv.{p.get('level', 1)})" for p in party[:3]
                        ]
                        party_display = (
                            f"{', '.join(party_names)}... +{len(party) - 3}"
                            if len(party) > 3
                            else ", ".join(party_names)
                        )
                    else:
                        party_display = "None"
                    unique_pokemon = {p.get("number") for p in party if p.get("number")}
                    pokedex = data.get("pokedex", {})
                    # pokedex format: {'seen': [...], 'caught': [...]}
                    caught_list = pokedex.get("caught", []) if isinstance(pokedex, dict) else []
                    caught_count = len(caught_list) if isinstance(caught_list, list) else 0
                    unique_count = max(len(unique_pokemon), caught_count)
                    table.add_row(
                        save_name, location, badges, party_display, str(unique_count), key=save_name
                    )
                except Exception:
                    table.add_row(save_name, "Unknown", "0", "None", "0", key=save_name)
                if first_save is None:
                    first_save = save_name

            # Pre-select the first row so a single click on Load works immediately
            if first_save:
                table.move_cursor(row=0)
                self._selected_save_name = first_save

            self._temp_saves_list = saves
        except Exception:
            pass
        self.query_one("#load-game-panel").remove_class("hidden")

    # ── Nurse Joy / Pokemon Center ───────────────────────────────────────────

    def show_nurse_joy_panel(self, question: str, heal_type: str) -> None:
        """Show the Nurse Joy / Mom healing confirmation panel."""
        self.pending_command_data["heal_type"] = heal_type
        self.query_one("#nurse-joy-question", Static).update(question)
        self.query_one("#nurse-joy-panel").remove_class("hidden")

    def show_pokemon_center_panel(self) -> None:
        """Show the Pokemon Center lobby panel."""
        try:
            self.hide_pokemon_center_loading()
            self.query_one("#pokemon-center-panel").remove_class("hidden")
        except Exception:
            pass

    def show_pokemon_center_loading(self) -> None:
        """Show Pokemon Center loading state while healing is in progress."""
        try:
            self.query_one("#pokemon-center-buttons").add_class("hidden")
            self.query_one("#pokemon-center-loading").remove_class("hidden")
        except Exception:
            pass

    def hide_pokemon_center_loading(self) -> None:
        """Hide Pokemon Center loading state and restore lobby buttons."""
        try:
            self.query_one("#pokemon-center-loading").add_class("hidden")
            self.query_one("#pokemon-center-buttons").remove_class("hidden")
        except Exception:
            pass

    # ── Bill's PC panels ──────────────────────────────────────────────────────

    def show_pc_main_panel(self) -> None:
        """Show the PC main hub panel, updating box summary and button labels."""
        try:
            storage = pc_system.get_pc_storage(self.game_state)
            total = pc_system.get_total_in_pc(self.game_state)
            party_count = len(self.game_state.game_data.get("pokemon", []))
            self.query_one("#pc-summary", Static).update(
                f"[dim]Party: {party_count}/6  |  Stored: {total} Pokemon in PC[/dim]"
            )
            for i in range(1, 4):
                box_key = f"Box {i}"
                box = storage[box_key]
                count = sum(1 for slot in box if slot is not None)
                label = f"📦 Box {i}" if count == 0 else f"📦 Box {i} ({count})"
                try:
                    self.query_one(f"#btn-pc-view-box-{i}", Button).label = label
                except Exception:
                    pass
            self.query_one("#pc-panel").remove_class("hidden")
            self.pending_command = "pc"
        except Exception:
            pass

    def show_pc_deposit_panel(self) -> None:
        """Show the deposit panel, labelling slot buttons with current party Pokémon."""
        try:
            pokemon = self.game_state.game_data.get("pokemon", [])
            real_pokemon = [p for p in pokemon if not isinstance(p, str)]
            can_deposit = len(real_pokemon) > 1
            for i in range(6):
                btn = self.query_one(f"#btn-pc-deposit-slot-{i}", Button)
                if i < len(real_pokemon):
                    p = real_pokemon[i]
                    btn.label = f"Slot {i + 1}: {p['name']} Lv.{p.get('level', '?')}"
                    btn.disabled = not can_deposit
                else:
                    btn.label = f"Slot {i + 1}: —"
                    btn.disabled = True
            self.query_one("#pc-deposit-panel").remove_class("hidden")
        except Exception:
            pass

    def show_pc_withdraw_panel(self, box_num: int) -> None:
        """Show the withdraw panel for the given box number."""
        try:
            storage = pc_system.get_pc_storage(self.game_state)
            box_key = f"Box {box_num}"
            box = storage.get(box_key, [])
            party_full = len(self.game_state.game_data.get("pokemon", [])) >= 6
            self.query_one("#pc-withdraw-title", Static).update(f"📤 Withdraw from Box {box_num}")
            for i in range(6):
                btn = self.query_one(f"#btn-pc-withdraw-slot-{i}", Button)
                pokemon = box[i] if i < len(box) else None
                if pokemon is not None:
                    btn.label = f"Slot {i + 1}: {pokemon['name']} Lv.{pokemon.get('level', '?')}"
                    btn.disabled = party_full
                else:
                    btn.label = f"Slot {i + 1}: —"
                    btn.disabled = True
            self.query_one("#pc-withdraw-panel").remove_class("hidden")
        except Exception:
            pass

    def show_pokemart_panel(self) -> None:
        """Show the Pokemart shop panel and populate the item Select with current catalog."""
        try:
            money = self.game_state.game_data.get("money", 0)
            self.query_one("#pokemart-money", Static).update(f"Your money:  ₽{money}")

            options = [
                (f"{info['emoji']}  {name}  —  ₽{info['price']}  ({info['description']})", name)
                for name, info in SHOP_CATALOG.items()
            ]
            self.query_one("#shop-item-select", Select).set_options(options)

            self.query_one("#pokemart-panel").remove_class("hidden")
        except Exception:
            pass

    # ── Party panel ────────────────────────────────────────────────

    def show_party_panel(self) -> None:
        """
        Populate and reveal the tabbed party panel.

        Tab 0 (Overview) shows all Pokémon in a 2-column grid.
        Tabs 1-6 show detailed stats/moves for each individual Pokémon.
        Tabs for empty slots are hidden.
        """
        try:
            pokemon = self.game_state.game_data.get("pokemon", [])
            real_pokemon = [p for p in pokemon if not isinstance(p, str)]
            party_size = len(real_pokemon)

            tabs = self.query_one("#party-tabs", TabbedContent)

            # Update per-slot tab labels and show/hide based on party size
            for i in range(1, 7):
                if i <= party_size:
                    p = real_pokemon[i - 1]
                    p_name = p.get("name", f"Slot {i}")
                    p_level = p.get("level", "?")
                    # Rename the tab label via the Tabs widget
                    try:
                        tab = tabs.get_tab(f"tab-party-{i}")
                        tab.label = f"{p_name} Lv.{p_level}"
                    except Exception:
                        pass
                    try:
                        tabs.show_tab(f"tab-party-{i}")
                    except Exception:
                        pass
                else:
                    try:
                        tabs.hide_tab(f"tab-party-{i}")
                    except Exception:
                        pass

            # Switch to overview
            try:
                tabs.active = "tab-party-overview"
            except Exception:
                pass

            # --- Overview tab ---
            overview_log = self.query_one("#party-log-overview", RichLog)
            overview_log.clear()
            populate_party_overview(overview_log, real_pokemon, self.ensure_battle_ready)

            # --- Detail tabs ---
            for i, p in enumerate(real_pokemon, 1):
                detail_log = self.query_one(f"#party-log-{i}", RichLog)
                detail_log.clear()
                populate_party_detail(detail_log, p, i, self.ensure_battle_ready)

            # Reveal panel
            self.query_one("#party-panel").remove_class("hidden")
        except Exception:
            # Fallback: write to main output log
            try:
                output = self.query_one("#output", RichLog)
                show_party(self.game_state, output, self.ensure_battle_ready)
            except Exception:
                pass
