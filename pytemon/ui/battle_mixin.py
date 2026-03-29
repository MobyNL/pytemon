"""
Battle system mixin for PokemonTerminal.

Contains all combat logic wiring: encounter triggers, turn execution,
switch handling, victory/defeat resolution, evolution prompting, and
item use during battle.
"""

import random
from typing import TYPE_CHECKING, Optional

from textual.widgets import RichLog, Static

from .. import evolution as _evo_module
from .. import gym_system
from ..battle import battle_actions, battle_ui
from ..data import get_trainer
from ..ui.formatters import format_hp_bar

if TYPE_CHECKING:
    pass  # Avoid circular imports — self is always a PokemonTerminal at runtime


class BattleMixin:
    """Mixin providing the full battle system for PokemonTerminal."""

    # ── Battle init helpers ──────────────────────────────────────────────────

    def ensure_battle_ready(self, pokemon: dict) -> None:
        """Ensure a Pokemon dict has full battle stats."""
        battle_actions.ensure_battle_ready(pokemon)

    def trigger_wild_encounter(self, output: RichLog) -> None:
        """Trigger a wild Pokemon battle at the current location."""

        def animated_battle_start(out: RichLog, on_ready) -> None:
            lines = battle_ui.get_battle_start_lines(self.game_state)
            self.text_animator.write_medium(out, lines, on_complete=on_ready)

        battle_actions.trigger_wild_encounter(
            self.game_state,
            output,
            lambda cmd: setattr(self, "pending_command", cmd),
            lambda: self.show_battle_action_panel(),
            show_battle_start_callback=animated_battle_start,
        )
        if self.game_state.battle_state:
            self.show_battle_hud()
            self.update_battle_hud()

    def trigger_trainer_encounter(self, output: RichLog, trainer: dict) -> None:
        """Trigger a trainer battle."""

        def animated_trainer_start(out: RichLog, on_ready) -> None:
            lines = battle_ui.get_trainer_battle_start_lines(self.game_state)
            self.text_animator.write_medium(out, lines, on_complete=on_ready)

        battle_actions.trigger_trainer_encounter(
            self.game_state,
            output,
            trainer,
            lambda cmd: setattr(self, "pending_command", cmd),
            lambda: self.show_battle_action_panel(),
            show_battle_start_callback=animated_trainer_start,
        )
        if self.game_state.battle_state:
            self.show_battle_hud()
            self.update_battle_hud()

    def trigger_gym_battle(
        self, trainer_id: str, output: RichLog, is_gym_battle: bool = False
    ) -> None:
        """Trigger a gym leader battle."""
        trainer = get_trainer(trainer_id)
        if not trainer:
            output.write(f"[red]❌ Error: Trainer '{trainer_id}' not found[/red]")
            return
        self.trigger_trainer_encounter(output, trainer)

    # ── Battle display ───────────────────────────────────────────────────────

    def show_battle_start(self, output: RichLog) -> None:
        """Display the wild Pokemon encounter introduction with animation."""
        lines = battle_ui.get_battle_start_lines(self.game_state)
        self.text_animator.write_medium(
            output, lines, on_complete=lambda: self.show_battle_options(output)
        )

    def show_trainer_battle_start(self, output: RichLog) -> None:
        """Display the trainer battle introduction with animation."""
        lines = battle_ui.get_trainer_battle_start_lines(self.game_state)
        self.text_animator.write_medium(
            output, lines, on_complete=lambda: self.show_battle_options(output)
        )

    def show_battle_options(self, output: RichLog) -> None:
        """Display the main battle menu with HP bars."""
        battle_ui.show_battle_options(self.game_state, output)
        self.show_battle_action_panel()
        self.show_battle_hud()
        self.update_battle_hud()

    def show_move_selection(self, output: RichLog) -> None:
        """Display the move selection menu."""
        battle_ui.show_move_selection(self.game_state, output)
        self.show_move_selection_panel()

    def show_battle_help(self, output: RichLog) -> None:
        """Show battle-specific help information."""
        battle_ui.show_battle_help(output)

    # ── Battle command dispatch ──────────────────────────────────────────────

    def process_battle_command(self, command: str, output: RichLog) -> None:
        """Process a command during battle."""
        cmd = command.lower().strip()

        if cmd in ("quit", "exit", "q"):
            output.write("")
            output.write("[yellow]⚠️ You can't quit during a battle![/yellow]")
            output.write("[dim]Try 'Run' to flee from battle, or keep fighting[/dim]")
            output.write("")
            self.show_battle_options(output)
            self.pending_command = "battle"
            return

        elif cmd in ("save", "save game"):
            output.write("")
            output.write("[yellow]⚠️ You can't save during a battle![/yellow]")
            output.write("[dim]Finish the battle first, then save your progress[/dim]")
            output.write("")
            self.show_battle_options(output)
            self.pending_command = "battle"
            return

        elif cmd in ("help", "h", "?"):
            self.show_battle_help(output)
            self.pending_command = "battle"
            return

        if cmd in ("fight", "attack", "f"):
            # Block fight in Safari Zone
            battle = self.game_state.battle_state
            if battle and battle.is_safari:
                output.write("")
                output.write("[yellow]⚠ You can't battle in the Safari Zone![/yellow]")
                output.write("[dim]Use Bait, Rock, Safari Ball, or Run.[/dim]")
                output.write("")
                self.show_battle_options(output)
                self.pending_command = "battle"
            else:
                self.show_move_selection(output)
                self.pending_command = "select_move"

        elif cmd in ("bait",):
            self._handle_safari_action(output, "bait")

        elif cmd in ("rock",):
            self._handle_safari_action(output, "rock")

        elif cmd in (
            "safari ball",
            "throw safari ball",
            "safari",
        ):
            self._handle_safari_action(output, "ball")

        elif cmd in ("run", "flee", "r"):
            battle = self.game_state.battle_state
            if battle and battle.is_safari:
                self._handle_safari_action(output, "run")
            else:
                self.attempt_flee(output)

        elif cmd in ("bag",):
            self.hide_all_battle_panels()
            battle_ui.show_bag_menu(self.game_state, output)
            self.show_battle_bag_panel()
            self.pending_command = "battle"

        elif cmd in ("use potion", "potion"):
            items = self.game_state.game_data.get("items", {})
            potions = items.get("Potion", 0)
            battle = self.game_state.battle_state
            player = battle.player_pokemon
            if potions <= 0:
                output.write("")
                output.write("[red]❌ You have no Potions![/red]")
                output.write("")
                self.show_battle_options(output)
                self.pending_command = "battle"
                return
            heal_amount = min(20, player["max_hp"] - player["hp"])
            player["hp"] += heal_amount
            items["Potion"] -= 1
            if items["Potion"] <= 0:
                del items["Potion"]
            output.write("")
            output.write(f"[green]💊 {player['name']} recovered {heal_amount} HP![/green]")
            output.write("")
            self.execute_wild_pokemon_turn(output)
            if battle.player_pokemon["hp"] <= 0:
                self.handle_pokemon_fainted(output)
                return
            self.show_battle_options(output)
            self.pending_command = "battle"

        elif cmd in ("throw pokeball", "pokeball", "catch", "ball", "throw"):
            self.attempt_catch_pokemon(output)

        elif cmd in ("throw great ball", "great ball"):
            self.attempt_catch_pokemon(output, ball_type="Great Ball")

        elif cmd in ("throw ultra ball", "ultra ball"):
            self.attempt_catch_pokemon(output, ball_type="Ultra Ball")

        elif cmd in ("throw master ball", "master ball"):
            self.attempt_catch_pokemon(output, ball_type="Master Ball")

        elif cmd in ("use super potion", "super potion"):
            self._use_heal_item(output, "Super Potion", 50)

        elif cmd in ("use antidote", "antidote"):
            self._use_status_cure(output, "Antidote", "POISON", "cured of poison")

        elif cmd in ("use paralyze heal", "paralyze heal", "parlyz heal"):
            self._use_status_cure(output, "Paralyze Heal", "PARALYSIS", "cured of paralysis")

        elif cmd in ("use awakening", "awakening"):
            self._use_status_cure(output, "Awakening", "SLEEP", "woken up")

        elif cmd in ("pokemon", "switch", "change", "swap"):
            self.show_pokemon_switch_menu(output)

        else:
            output.write("[red]❌ Not a valid battle command[/red]")
            output.write("[dim]Try: 'Fight', 'Bag', 'Pokemon', 'Pokeball', or 'Run'[/dim]")
            output.write("[dim]Type 'Help' to see all battle commands[/dim]")
            output.write("")
            self.show_battle_options(output)
            self.pending_command = "battle"

    # ── Item use during battle ───────────────────────────────────────────────

    def _use_heal_item(self, output: RichLog, item_name: str, heal_amount: int) -> None:
        """Use a healing item during battle."""
        battle_actions.use_heal_item(
            self.game_state,
            output,
            item_name,
            heal_amount,
            lambda cmd: setattr(self, "pending_command", cmd),
            self.show_battle_options,
            self.handle_pokemon_fainted,
        )

    def _use_status_cure(
        self, output: RichLog, item_name: str, cures_status: str, cure_msg: str
    ) -> None:
        """Use a status-curing item during battle."""
        battle_actions.use_status_cure(
            self.game_state,
            output,
            item_name,
            cures_status,
            cure_msg,
            lambda cmd: setattr(self, "pending_command", cmd),
            self.show_battle_options,
            self.handle_pokemon_fainted,
        )

    # ── Move selection / execution ───────────────────────────────────────────

    def parse_move_choice(self, command: str, player: dict) -> Optional[dict]:
        """Parse a move choice from player input (name or number)."""
        cmd = command.lower().strip()
        if cmd.startswith("use "):
            cmd = cmd[4:].strip()
        if cmd.isdigit():
            idx = int(cmd) - 1
            if 0 <= idx < len(player["moves"]):
                return player["moves"][idx]
            return None
        for move in player["moves"]:
            if move["name"].lower() == cmd or cmd in move["name"].lower():
                return move
        return None

    def _build_wild_turn_messages(self) -> list:
        """Execute the opponent's turn (side-effects) and return the messages as a list.

        This companion to ``execute_wild_pokemon_turn`` allows the caller to animate
        the resulting lines with ``text_animator`` instead of writing them instantly.
        """
        battle = self.game_state.battle_state
        wild = battle.wild_pokemon
        player = battle.player_pokemon
        lines: list[str] = []

        available = [
            m for m in wild["moves"] if m["pp"] > 0 and m["name"] != battle.enemy_disabled_move
        ]
        if not available:
            opponent_name = (
                f"{battle.trainer_data['name']}'s {wild['name']}"
                if battle.is_trainer_battle
                else f"Wild {wild['name']}"
            )
            lines.append(f"[yellow]{opponent_name} has no moves left! It used Struggle![/yellow]")
            struggle_dmg = max(1, player["max_hp"] // 8)
            player["hp"] = max(0, player["hp"] - struggle_dmg)
            lines.append(f"[cyan]{player['name']} took {struggle_dmg} damage![/cyan]")
            return lines

        if battle.is_trainer_battle:
            move = battle.choose_trainer_move() or random.choice(available)
            opponent_name = f"{battle.trainer_data['name']}'s {wild['name']}"
        else:
            move = random.choice(available)
            opponent_name = f"Wild {wild['name']}"

        # Track move so HUD "Seen" section stays up to date
        battle.enemy_moves_seen.add(move["name"])

        lines.append("")
        lines.append(f"[yellow]{opponent_name} used {move['name']}![/yellow]")
        lines.extend(battle.execute_move(wild, player, move["name"]))
        return lines

    def _pick_enemy_move(self) -> Optional[str]:
        """
        Choose the enemy's next move name without executing it.

        Used to check for priority moves before committing to turn order.

        Returns:
            Move name string, or None if no moves available.
        """
        battle = self.game_state.battle_state
        wild = battle.wild_pokemon
        if not wild:
            return None
        available = [
            m for m in wild["moves"] if m["pp"] > 0 and m["name"] != battle.enemy_disabled_move
        ]
        if not available:
            return None
        if battle.is_trainer_battle:
            move = battle.choose_trainer_move() or random.choice(available)
        else:
            move = random.choice(available)
        return move["name"]

    def execute_player_move(self, command: str, output: RichLog) -> None:
        """Execute the player's chosen move and then run the opponent's turn.

        Handles speed-priority moves: if the enemy's upcoming move has the
        ``priority`` effect and the player's does not, the enemy attacks first.
        """
        battle = self.game_state.battle_state
        player = battle.player_pokemon

        if command.lower().strip() in ("back", "b"):
            self.show_battle_options(output)
            self.pending_command = "battle"
            return

        # ── If the player is charging a two-turn move, the move name was stored
        # in battle.player_charging; retrieve it so the release turn executes.
        if battle.player_charging:
            move_name = battle.player_charging
            # Fake a MoveSlot lookup so parse_move_choice isn't needed
            move = next((m for m in player["moves"] if m["name"] == move_name), None)
        else:
            move = self.parse_move_choice(command, player)

        if not move:
            output.write("[red]❌ Unknown move. Type the name, number, or 'Back'.[/red]")
            output.write("")
            self.show_move_selection(output)
            self.pending_command = "select_move"
            return

        if not battle.player_charging and move["pp"] <= 0:
            output.write(f"[red]❌ {move['name']} has no PP left! Choose another move.[/red]")
            output.write("")
            self.show_move_selection(output)
            self.pending_command = "select_move"
            return

        move_name = move["name"]

        # ── Determine turn order based on speed-priority ─────────────────
        # If the player uses a non-priority move and the enemy uses a priority
        # move, the enemy strikes first this turn.
        player_has_priority = battle.is_player_move_priority(move_name)
        enemy_move_name = self._pick_enemy_move()
        enemy_has_priority = (
            battle.is_enemy_move_priority(enemy_move_name) if enemy_move_name else False
        )
        enemy_goes_first = enemy_has_priority and not player_has_priority

        if enemy_goes_first:
            # Enemy attacks first, then player
            wild = battle.wild_pokemon
            opponent_name = (
                f"{battle.trainer_data['name']}'s {wild['name']}"
                if battle.is_trainer_battle
                else f"Wild {wild['name']}"
            )
            enemy_lines = [
                "",
                f"[bold yellow]{opponent_name} moved first with {enemy_move_name}![/bold yellow]",
                f"[yellow]{opponent_name} used {enemy_move_name}![/yellow]",
                *battle.execute_move(wild, player, enemy_move_name),
            ]
            if enemy_move_name:
                battle.enemy_moves_seen.add(enemy_move_name)

            player_lines = [
                "",
                f"[bold]{player['name']} used {move_name}![/bold]",
                *battle.execute_move(player, battle.wild_pokemon, move_name),
            ]
            wild_fainted_after_player = battle.wild_pokemon["hp"] <= 0

            def _after_priority_player_attack() -> None:
                if wild_fainted_after_player:
                    self.handle_battle_victory(output)
                    return
                current_battle = self.game_state.battle_state
                if current_battle:
                    for msg in current_battle.end_of_turn_effects(current_battle.wild_pokemon):
                        output.write(msg)
                    if current_battle.wild_pokemon["hp"] <= 0:
                        self.handle_battle_victory(output)
                        return
                    for msg in current_battle.end_of_turn_effects(player):
                        output.write(msg)
                    if player["hp"] <= 0:
                        self.handle_pokemon_fainted(output)
                        return
                self.hide_battle_loading()
                self.show_battle_options(output)
                self.pending_command = "battle"

            def _after_priority_enemy_attack() -> None:
                if player["hp"] <= 0:
                    self.handle_pokemon_fainted(output)
                    return
                self.text_animator.write_fast(
                    output, player_lines, on_complete=_after_priority_player_attack
                )

            self.text_animator.write_fast(
                output, enemy_lines, on_complete=_after_priority_enemy_attack
            )
            return

        # ── Normal order: player attacks first ───────────────────────────
        player_lines = [
            "",
            f"[bold]{player['name']} used {move_name}![/bold]",
            *battle.execute_move(player, battle.wild_pokemon, move_name),
        ]
        wild_fainted = battle.wild_pokemon["hp"] <= 0

        def _after_opponent_turn() -> None:
            if player["hp"] <= 0:
                self.handle_pokemon_fainted(output)
                return
            # ── End-of-turn status effects ───────────────────────────────────
            current_battle = self.game_state.battle_state
            if current_battle:
                for msg in current_battle.end_of_turn_effects(current_battle.wild_pokemon):
                    output.write(msg)
                if current_battle.wild_pokemon["hp"] <= 0:
                    self.handle_battle_victory(output)
                    return
                for msg in current_battle.end_of_turn_effects(player):
                    output.write(msg)
                if player["hp"] <= 0:
                    self.handle_pokemon_fainted(output)
                    return
            self.hide_battle_loading()
            self.show_battle_options(output)
            self.pending_command = "battle"

        def _after_player_attack() -> None:
            if wild_fainted:
                self.handle_battle_victory(output)
                return
            # ── Opponent's turn — execute (side-effects) then animate ────────
            opp_lines = self._build_wild_turn_messages()
            self.text_animator.write_fast(output, opp_lines, on_complete=_after_opponent_turn)

        self.text_animator.write_fast(output, player_lines, on_complete=_after_player_attack)

    def execute_wild_pokemon_turn(self, output: RichLog) -> None:
        """Execute the opponent Pokemon's turn instantly (no animation)."""
        for line in self._build_wild_turn_messages():
            output.write(line)

    # ── Flee / catch / switch ────────────────────────────────────────────────

    def _handle_safari_action(self, output: RichLog, action: str) -> None:
        """Dispatch a Safari Zone action (bait/rock/ball/run)."""
        battle_actions.handle_safari_action(
            self.game_state,
            output,
            action,
            lambda cmd: setattr(self, "pending_command", cmd),
            self.show_battle_options,
            self.end_battle,
        )

    def attempt_flee(self, output: RichLog) -> None:
        """Attempt to flee from a battle."""
        battle_actions.attempt_flee(
            self.game_state,
            output,
            lambda cmd: setattr(self, "pending_command", cmd),
            self.show_battle_options,
            self.end_battle,
            self.handle_pokemon_fainted,
        )

    def attempt_catch_pokemon(self, output: RichLog, ball_type: str = "Pokeball") -> None:
        """Attempt to catch the wild Pokemon with a Pokeball.

        Args:
            output:    RichLog widget.
            ball_type: Type of ball to throw (Pokeball, Great Ball, Ultra Ball, Master Ball).
        """

        def _animate_shake(out: RichLog, lines: list, on_complete) -> None:
            self.text_animator.write_slow(out, lines, on_complete=on_complete)

        battle_actions.attempt_catch_pokemon(
            self.game_state,
            output,
            lambda cmd: setattr(self, "pending_command", cmd),
            self.show_battle_options,
            self.end_battle,
            self.handle_pokemon_fainted,
            ball_type=ball_type,
            animate_shake_callback=_animate_shake,
        )

    def show_pokemon_switch_menu(self, output: RichLog) -> None:
        """Show the party Pokemon available for switching during battle."""
        battle = self.game_state.battle_state
        if not battle:
            return
        self.hide_all_battle_panels()
        active = battle.player_pokemon
        party = self.game_state.game_data.get("pokemon", [])

        output.write("")
        output.write("[bold cyan]👥 Switch Pokemon[/bold cyan]")
        output.write("")

        switchable_nums = []
        for i, p in enumerate(party, 1):
            if isinstance(p, str):
                continue
            self.ensure_battle_ready(p)
            is_active = p is active
            hp_bar = format_hp_bar(p["hp"], p["max_hp"], width=10)
            status = p.get("status") or ""
            status_str = f" [yellow][{status}][/yellow]" if status else ""
            active_str = " [bold yellow]← Active[/bold yellow]" if is_active else ""
            fainted_str = " [dim](Fainted)[/dim]" if p["hp"] <= 0 else ""
            output.write(
                f"  {i}. [bold]{p['name']}[/bold] Lv.{p['level']}{status_str}{active_str}{fainted_str}"
            )
            output.write(f"     {hp_bar} {p['hp']}/{p['max_hp']} HP")
            if not is_active and p["hp"] > 0:
                switchable_nums.append(str(i))

        output.write("")
        if switchable_nums:
            output.write(
                f"[dim]Type a number ({', '.join(switchable_nums)}) or name to switch, or 'back' to cancel[/dim]"
            )
            output.write("")
            self.pending_command = "switch_target"
            self.show_pokemon_switch_panel()
        else:
            output.write("[yellow]No other Pokemon available to switch![/yellow]")
            output.write("")
            self.show_battle_options(output)
            self.pending_command = "battle"

    def execute_switch(self, target: str, output: RichLog) -> None:
        """Execute a mid-battle Pokemon switch."""
        battle = self.game_state.battle_state
        if not battle:
            return

        if target.lower().strip() in ("back", "cancel", "no"):
            output.write("[dim]Switch cancelled.[/dim]")
            output.write("")
            self.show_battle_options(output)
            self.pending_command = "battle"
            return

        party = self.game_state.game_data.get("pokemon", [])
        active = battle.player_pokemon
        chosen = None
        t = target.strip()
        if t.isdigit():
            idx = int(t) - 1
            if 0 <= idx < len(party) and not isinstance(party[idx], str):
                chosen = party[idx]
        else:
            for p in party:
                if not isinstance(p, str) and t.lower() in p["name"].lower():
                    chosen = p
                    break

        if not chosen:
            output.write(f"[red]❌ Invalid selection: {target}[/red]")
            self.show_pokemon_switch_menu(output)
            return
        if chosen is active:
            output.write(f"[yellow]{chosen['name']} is already in battle![/yellow]")
            output.write("")
            self.show_battle_options(output)
            self.pending_command = "battle"
            return
        if chosen["hp"] <= 0:
            output.write(f"[red]❌ {chosen['name']} has fainted and can't battle![/red]")
            self.show_pokemon_switch_menu(output)
            return

        battle.player_pokemon = chosen
        output.write("")
        output.write(f"[bold cyan]{active['name']}, come back![/bold cyan]")
        output.write(f"[bold green]Go, {chosen['name']}![/bold green]")
        output.write("")
        self.execute_wild_pokemon_turn(output)
        if battle.player_pokemon["hp"] <= 0:
            self.handle_pokemon_fainted(output)
        else:
            self.show_battle_options(output)
            self.pending_command = "battle"

    # ── Battle outcome ───────────────────────────────────────────────────────

    def handle_battle_victory(self, output: RichLog) -> None:
        """Handle opponent Pokemon fainting (wild or trainer)."""
        battle_actions.handle_battle_victory(
            self.game_state,
            output,
            lambda cmd: setattr(self, "pending_command", cmd),
            self.show_battle_options,
            self.handle_trainer_defeated,
            self.end_battle,
            self._queue_evolution_pending,
            self._queue_move_learn,
        )

    def handle_trainer_defeated(self, output: RichLog) -> None:
        """Handle defeating a trainer (check for deferred evolution first)."""
        battle = self.game_state.battle_state
        if battle and battle.pending_evolution:
            player_ref, evo_target = battle.pending_evolution
            battle.pending_evolution = None
            self._queue_evolution_pending(player_ref, evo_target, "trainer_defeated", output)
            return
        battle_actions.handle_trainer_defeated(self.game_state, output, self.end_battle)

    def handle_pokemon_fainted(self, output: RichLog) -> None:
        """Handle player's Pokemon fainting."""
        battle_actions.handle_pokemon_fainted(
            self.game_state,
            output,
            self.end_battle,
            show_faint_options_callback=self._prompt_faint_switch,
        )

    def _prompt_faint_switch(self, can_run: bool) -> None:
        """Show the faint-switch panel and set pending state."""
        self.pending_command = "faint_switch"
        self.pending_command_data["faint_can_run"] = can_run
        self.show_faint_switch_panel(can_run)

    def execute_faint_switch(self, target: str, output: RichLog) -> None:
        """Switch to a replacement Pokemon after the active one fainted.

        Unlike a mid-battle switch, the opponent does NOT get a free attack
        — the faint already resolved that turn.
        """
        battle = self.game_state.battle_state
        if not battle:
            return

        party = self.game_state.game_data.get("pokemon", [])
        chosen = None
        t = target.strip()
        if t.isdigit():
            idx = int(t) - 1
            if 0 <= idx < len(party) and not isinstance(party[idx], str):
                chosen = party[idx]
        else:
            for p in party:
                if not isinstance(p, str) and t.lower() in p["name"].lower():
                    chosen = p
                    break

        can_run = self.pending_command_data.get("faint_can_run", False)

        if not chosen:
            output.write(f"[red]\u274c Invalid selection: {target}[/red]")
            self.pending_command = "faint_switch"
            self.show_faint_switch_panel(can_run)
            return
        if chosen["hp"] <= 0:
            output.write(f"[red]\u274c {chosen['name']} has fainted and can't battle![/red]")
            self.pending_command = "faint_switch"
            self.show_faint_switch_panel(can_run)
            return

        battle.player_pokemon = chosen
        output.write(f"[bold green]Go, {chosen['name']}![/bold green]")
        output.write("")
        # No wild/trainer turn — the faint already resolved the previous turn
        self.show_battle_options(output)
        self.pending_command = "battle"

    def end_battle(self, output: RichLog) -> None:
        """Clean up after a battle ends and return to exploration (or gym lobby)."""
        # Capture gym context BEFORE pending_command_data is cleared
        in_gym = self.pending_command_data.get("in_gym_lobby", False)

        if in_gym:
            # Manually mirror battle_actions.end_battle then re-open gym lobby
            if self.game_state.battle_state:
                self.game_state.battle_state.end_battle()
            self.game_state.battle_state = None
            self.game_state.in_battle = False
            self.pending_command = None
            self.pending_command_data = {}
            self.hide_all_battle_panels()
            gym_system.enter_gym_lobby(self.game_state, output, self.show_gym_panel)
        else:
            battle_actions.end_battle(self.game_state, output, self.look_around)
            self.pending_command = None
            self.pending_command_data = {}
            self.hide_all_battle_panels()

    # ── Evolution pending / resume ───────────────────────────────────────────

    def _queue_move_learn(
        self,
        pokemon: dict,
        new_moves: list,
        post_action: str,
        output: RichLog,
    ) -> None:
        """Queue an interactive 'which move to forget?' prompt."""
        if not new_moves:
            self._resume_after_move_learn(post_action, output)
            return

        move_name = new_moves[0]
        remaining = new_moves[1:]

        self.pending_command_data["learn_pokemon"] = pokemon
        self.pending_command_data["learn_move_name"] = move_name
        self.pending_command_data["learn_remaining"] = remaining
        self.pending_command_data["learn_post_action"] = post_action

        pokemon_name = pokemon.get("name", "POKÉMON")
        current_moves = pokemon.get("moves", [])

        output.write("")
        output.write(f"[bold yellow]  ⭐ {pokemon_name} wants to learn {move_name}![/bold yellow]")
        output.write("  [dim]But it already knows 4 moves.[/dim]")
        output.write(f"  [dim]Delete a move to make room for {move_name}?[/dim]")
        output.write("")
        for i, m in enumerate(current_moves, 1):
            pp_info = f" ({m['pp']}/{m.get('max_pp', m['pp'])} PP)" if "pp" in m else ""
            output.write(f"  [cyan]{i}.[/cyan] {m['name']}{pp_info}")
        output.write("")
        output.write(
            "  [dim]Type [bold]1-4[/bold] to forget that move, or [bold]no[/bold] to skip.[/dim]"
        )
        output.write("")

        self.pending_command = "learn_move_choice"

    def _resume_after_move_learn(self, post_action: str, output: RichLog) -> None:
        """Resume battle resolution after all move-learn prompts are resolved."""
        # Clear learn state
        pokemon = self.pending_command_data.pop("learn_pokemon", None)
        self.pending_command_data.pop("learn_move_name", None)
        self.pending_command_data.pop("learn_remaining", None)
        self.pending_command_data.pop("learn_post_action", None)
        self.pending_command = None

        # Check for evolution (mirrors the logic in battle_actions.handle_battle_victory)
        if pokemon:
            battle = self.game_state.battle_state
            evo_target = _evo_module.get_level_evolution(pokemon)
            if evo_target and battle and battle.is_trainer_battle and battle.has_more_pokemon():
                if not battle.pending_evolution:
                    battle.pending_evolution = (pokemon, evo_target)
                evo_target = None
            if evo_target:
                battle.pending_evolution = None
                self._queue_evolution_pending(pokemon, evo_target, post_action, output)
                return

        # Resume post_action
        if post_action == "trainer_next":
            battle = self.game_state.battle_state
            if battle and battle.has_more_pokemon():
                output.write("")
                next_pokemon = battle.switch_to_next_pokemon()
                trainer = battle.trainer_data
                output.write(
                    f"[yellow]{trainer['name']} sent out {next_pokemon['name']}! "
                    f"(Lv. {next_pokemon['level']})[/yellow]"
                )
                output.write("")
                self.show_battle_options(output)
                self.pending_command = "battle"
            else:
                self.handle_trainer_defeated(output)
        elif post_action == "trainer_defeated":
            self.handle_trainer_defeated(output)
        else:
            output.write("")
            self.end_battle(output)

    def _queue_evolution_pending(
        self, pokemon: dict, evolved_into: str, post_action: str, output: RichLog
    ) -> None:
        """Queue a pending evolution for player confirmation via the evolution panel."""
        pokemon_name = pokemon.get("name", "POKÉMON")
        self.pending_command_data["evolving_pokemon"] = pokemon
        self.pending_command_data["evolves_into"] = evolved_into
        self.pending_command_data["evolution_post_action"] = post_action

        try:
            self.query_one("#evolution-title", Static).update(
                f"✨ {pokemon_name} → {evolved_into}!"
            )
        except Exception:
            pass

        def show_evolution_panel() -> None:
            self.hide_all_panels()
            try:
                self.query_one("#evolution-panel").remove_class("hidden")
            except Exception:
                pass
            self.pending_command = "confirm_evolution"

        anim_lines = [
            "",
            f"[bold yellow]✨ What? {pokemon_name} is evolving![/bold yellow]",
            "",
            "[dim]  ◇ ◇ ◇ ◇ ◇ ◇ ◇ ◇ ◇ ◇[/dim]",
            "",
            f"  [dim]{pokemon_name} → {evolved_into}[/dim]",
            "",
        ]
        self.text_animator.write_slow(output, anim_lines, on_complete=show_evolution_panel)

    def _resume_after_evolution(self, output: RichLog) -> None:
        """Resume battle resolution after the player chose to evolve or stop."""
        post_action = self.pending_command_data.get("evolution_post_action", "wild_end")

        self.pending_command_data.pop("evolving_pokemon", None)
        self.pending_command_data.pop("evolves_into", None)
        self.pending_command_data.pop("evolution_post_action", None)
        self.pending_command = None

        if post_action == "wild_end":
            output.write("")
            self.end_battle(output)
        elif post_action == "trainer_defeated":
            self.handle_trainer_defeated(output)
        elif post_action == "trainer_next":
            battle = self.game_state.battle_state
            if battle and battle.has_more_pokemon():
                output.write("")
                next_pokemon = battle.switch_to_next_pokemon()
                trainer = battle.trainer_data
                output.write(
                    f"[yellow]{trainer['name']} sent out {next_pokemon['name']}! (Lv. {next_pokemon['level']})[/yellow]"
                )
                output.write("")
                self.show_battle_options(output)
                self.pending_command = "battle"
            else:
                self.handle_trainer_defeated(output)
        else:
            output.write("")
            self.end_battle(output)
