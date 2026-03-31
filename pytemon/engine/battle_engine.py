"""
Pokemon Battle Engine.

Implements simplified Gen 1 battle mechanics for wild Pokemon and trainer battles.
"""

import random
from typing import TYPE_CHECKING, List, Optional

from ..data import get_move, get_pokemon, get_type_effectiveness
from ..data.move_data import MoveData, MoveSlot
from ..data.pokemon_data import StatsData
from ..models import PartyPokemon

if TYPE_CHECKING:
    from ..data.trainer_data import Trainer


def _stat_stage_mult(stage: int) -> float:
    """Return the Gen 1 stat-stage multiplier for a stage value in [-6, 6].

    Positive stage: (2 + stage) / 2  (e.g. +2 → 2.0×)
    Negative stage: 2 / (2 - stage)  (e.g. -2 → 0.5×)
    """
    stage = max(-6, min(6, stage))
    if stage >= 0:
        return (2.0 + stage) / 2.0
    return 2.0 / (2.0 - stage)


class BattleState:
    """Manages state and logic for Pokemon battles (wild and trainer)."""

    def __init__(self):
        """Initialize battle state."""
        self.active = False
        self.player_pokemon: Optional[PartyPokemon] = None
        self.wild_pokemon: Optional[PartyPokemon] = None
        self.turn_count = 0
        self.battle_log: list[str] = []
        self.player_can_run = True

        self.is_trainer_battle = False
        self.trainer_data: Optional[Trainer] = None
        self.trainer_pokemon_team: List[PartyPokemon] = []
        self.current_trainer_pokemon_index = 0
        self.prize_money = 0
        self.pending_evolution: Optional[tuple[PartyPokemonDict, str]] = (
            None  # (pokemon_ref, evolved_form_name)
        )
        self.enemy_moves_seen: set = set()
        self.last_player_move: Optional[dict] = None
        self.last_enemy_move: Optional[dict] = None
        self.player_stat_stages: dict = {}  # stat_name -> cumulative delta from base
        self.enemy_stat_stages: dict = {}

        # ── Two-turn move state ───────────────────────────────────────────
        # When a Pokemon is charging a two-turn move (Fly, Dig, SolarBeam),
        # this holds the move name; the next call to execute_move releases it.
        self.player_charging: Optional[str] = None  # move name being charged
        self.enemy_charging: Optional[str] = None

        # ── Trapping move state ───────────────────────────────────────────
        # Trapping moves (Wrap, Bind, Fire Spin) lock the target for 2–5 turns.
        # player_trapped_turns: turns the player has remaining while trapped.
        # enemy_trapped_turns: turns the enemy has remaining while trapped.
        self.player_trapped_turns: int = 0
        self.enemy_trapped_turns: int = 0
        self.player_trap_dmg: int = 0  # damage dealt per turn while trapped
        self.enemy_trap_dmg: int = 0

        # ── Leech Seed state ──────────────────────────────────────────────
        self.player_seeded: bool = False  # True when player's Pokemon is seeded
        self.enemy_seeded: bool = False  # True when wild/trainer Pokemon is seeded

        # ── Disable state ─────────────────────────────────────────────────
        self.player_disabled_move: Optional[str] = None  # name of disabled move
        self.player_disable_turns: int = 0
        self.enemy_disabled_move: Optional[str] = None
        self.enemy_disable_turns: int = 0

        # ── Safari Zone state ─────────────────────────────────────────────
        self.is_safari: bool = False
        self.safari_bait_turns: int = 0  # turns bait is active (reduces flee chance)
        self.safari_rock_turns: int = 0  # turns rock is active (raises flee + catch rate)

    def start_wild_battle(
        self, player_pokemon: PartyPokemon, wild_species: str, wild_level: int
    ) -> None:
        """
        Initialize a wild Pokemon battle.

        Args:
            player_pokemon: Player's Pokemon dict
            wild_species: Name of wild Pokemon species
            wild_level: Level of wild Pokemon
        """
        self.active = True
        self.is_trainer_battle = False
        self.player_pokemon = player_pokemon
        self.wild_pokemon = self.generate_wild_pokemon(wild_species, wild_level)
        self.turn_count = 0
        self.battle_log = []
        self.player_can_run = True
        self.trainer_data = None
        self.trainer_pokemon_team = []
        self.current_trainer_pokemon_index = 0
        self.prize_money = 0
        self.enemy_moves_seen = set()
        self.last_player_move = None
        self.last_enemy_move = None
        self.player_stat_stages = {}
        self.enemy_stat_stages = {}
        self.player_charging = None
        self.enemy_charging = None
        self.player_trapped_turns = 0
        self.enemy_trapped_turns = 0
        self.player_trap_dmg = 0
        self.enemy_trap_dmg = 0
        self.player_seeded = False
        self.enemy_seeded = False
        self.player_disabled_move = None
        self.player_disable_turns = 0
        self.enemy_disabled_move = None
        self.enemy_disable_turns = 0

    def start_trainer_battle(self, player_pokemon: PartyPokemon, trainer_data: "Trainer") -> None:
        """
        Initialize a trainer battle.

        Args:
            player_pokemon: Player's Pokemon object
            trainer_data: Trainer data object with pokemon team
        """
        self.active = True
        self.is_trainer_battle = True
        self.player_pokemon = player_pokemon
        self.trainer_data = trainer_data
        self.turn_count = 0
        self.battle_log = []
        self.player_can_run = False

        # Generate trainer's Pokemon team
        self.trainer_pokemon_team = []
        for pokemon_info in trainer_data.pokemon:
            pokemon = self.generate_wild_pokemon(pokemon_info.species, pokemon_info.level)
            self.trainer_pokemon_team.append(pokemon)

        # Set first Pokemon as active
        self.current_trainer_pokemon_index = 0
        if self.trainer_pokemon_team:
            self.wild_pokemon = self.trainer_pokemon_team[0]

        # Set prize money
        self.prize_money = trainer_data.prize_money
        self.enemy_moves_seen = set()
        self.last_player_move = None
        self.last_enemy_move = None
        self.player_stat_stages = {}
        self.enemy_stat_stages = {}
        self.player_charging = None
        self.enemy_charging = None
        self.player_trapped_turns = 0
        self.enemy_trapped_turns = 0
        self.player_trap_dmg = 0
        self.enemy_trap_dmg = 0
        self.player_seeded = False
        self.enemy_seeded = False
        self.player_disabled_move = None
        self.player_disable_turns = 0
        self.enemy_disabled_move = None
        self.enemy_disable_turns = 0

    def generate_wild_pokemon(self, species: str, level: int) -> PartyPokemon:
        """
        Generate a wild Pokemon with stats for the given species and level.

        Args:
            species: Pokemon species name (e.g., "PIDGEY")
            level: Level for the wild Pokemon

        Returns:
            PartyPokemon: Wild Pokemon with battle stats
        """
        # Get Pokemon base data
        pokemon_data = get_pokemon(species)
        if not pokemon_data:
            # Fallback if Pokemon not found
            return PartyPokemon(
                name=species,
                number=0,
                level=level,
                types=["Normal"],
                hp=20,
                max_hp=20,
                stats=StatsData(hp=20, attack=10, defense=10, special=10, speed=10),
                moves=[MoveSlot(name="TACKLE", pp=35, max_pp=35)],
                catch_rate=255,
                base_exp=50,
                experience=0,
                next_level_exp=level**3,
            )

        # Calculate stats based on level and base stats
        stats = self.calculate_stats(pokemon_data.stats, level)

        # Get appropriate moves for this level
        moves = self.get_moves_for_level(pokemon_data, level)

        return PartyPokemon(
            name=pokemon_data.name,
            number=pokemon_data.number,
            level=level,
            types=list(pokemon_data.types),
            hp=stats.hp,
            max_hp=stats.hp,
            stats=stats,
            moves=moves,
            catch_rate=pokemon_data.catch_rate,
            base_exp=pokemon_data.base_exp,
            experience=0,
            next_level_exp=level**3,
        )

    def calculate_stats(self, base_stats: StatsData, level: int) -> StatsData:
        """
        Calculate Pokemon stats for a given level using Gen 1 formula.
        Simplified: no IVs/EVs for wild Pokemon.

        Args:
            base_stats: Base StatsData (hp, attack, defense, special, speed)
            level: Pokemon level

        Returns:
            StatsData: Calculated stats
        """
        # Gen 1 stat formula (simplified, assuming 8 IV and 0 EV):
        # HP = ((Base + IV) * 2 * Level / 100) + Level + 10
        # Other = ((Base + IV) * 2 * Level / 100) + 5

        # For simplicity, use IV=8 for all wild Pokemon
        iv = 8

        hp = int(((base_stats.hp + iv) * 2 * level / 100) + level + 10)
        attack = int(((base_stats.attack + iv) * 2 * level / 100) + 5)
        defense = int(((base_stats.defense + iv) * 2 * level / 100) + 5)
        special = int(((base_stats.special + iv) * 2 * level / 100) + 5)
        speed = int(((base_stats.speed + iv) * 2 * level / 100) + 5)

        return StatsData(hp=hp, attack=attack, defense=defense, special=special, speed=speed)

    def get_moves_for_level(self, pokemon_data, level: int) -> List[MoveSlot]:
        """
        Get the moves a Pokemon should know at a given level.

        Args:
            pokemon_data: SpeciesData with learnset
            level: Pokemon level

        Returns:
            list: Up to 4 MoveSlot objects the Pokemon knows
        """
        learnset = pokemon_data.learnset
        known_moves: List[MoveSlot] = []

        # Get all moves learned up to this level
        for learn_level in sorted(learnset.keys()):
            if learn_level <= level:
                for move_name in learnset[learn_level]:
                    # Add move if not already known (keep last 4)
                    if move_name not in [m.name for m in known_moves]:
                        move_data = get_move(move_name)
                        if move_data:
                            known_moves.append(
                                MoveSlot(
                                    name=move_name,
                                    pp=move_data.pp,
                                    max_pp=move_data.pp,
                                )
                            )

        # Keep only the last 4 moves (Gen 1 moveset limit)
        return known_moves[-4:] if len(known_moves) > 4 else known_moves

    def get_new_moves_at_level(self, species_name: str, level: int) -> list[str]:
        """
        Get move names first learned at exactly this level for a species.

        Args:
            species_name: Pokemon species name (uppercase)
            level: Level just reached

        Returns:
            list: Move names learned at exactly this level
        """
        pokemon_data = get_pokemon(species_name)
        if not pokemon_data:
            return []
        return list(pokemon_data.learnset.get(level, []))

    def calculate_damage(
        self, attacker: PartyPokemon, defender: PartyPokemon, move_name: str
    ) -> tuple[int, str, bool]:
        """
        Calculate damage for a move using Gen 1 damage formula.

        Args:
            attacker: Attacking Pokemon dict
            defender: Defending Pokemon dict
            move_name: Name of the move being used

        Returns:
            tuple: (damage: int, message: str, is_critical: bool)
        """
        move = get_move(move_name)
        if not move:
            return 0, "Move not found!", False

        # Status moves deal no damage
        if move["category"] == "status":
            return 0, "", False

        power = move["power"]
        move_type = move["type"]

        # Check for critical hit (Gen 1: uses base speed, not battle speed)
        is_critical = self.check_critical_hit(attacker, move)

        # Type effectiveness
        effectiveness = get_type_effectiveness(move_type, defender["types"])
        if effectiveness == 0:
            return 0, f"It doesn't affect {defender['name']}...", False

        # Determine whose stat-stage dict is whose
        is_player_attacker = attacker is self.player_pokemon
        atk_stages = self.player_stat_stages if is_player_attacker else self.enemy_stat_stages
        def_stages = self.enemy_stat_stages if is_player_attacker else self.player_stat_stages

        # Attack and Defense stats — apply stat stages unless it's a critical hit
        # (Gen 1 critical hits ignore all stat changes for both attacker and defender)
        if move["category"] == "physical":
            attack_stat = attacker["stats"]["attack"]
            defense_stat = defender["stats"]["defense"]
            if not is_critical:
                attack_stat = max(
                    1, int(attack_stat * _stat_stage_mult(atk_stages.get("attack", 0)))
                )
                defense_stat = max(
                    1, int(defense_stat * _stat_stage_mult(def_stages.get("defense", 0)))
                )
        else:  # special
            attack_stat = attacker["stats"]["special"]
            defense_stat = defender["stats"]["special"]
            if not is_critical:
                attack_stat = max(
                    1, int(attack_stat * _stat_stage_mult(atk_stages.get("special", 0)))
                )
                defense_stat = max(
                    1, int(defense_stat * _stat_stage_mult(def_stages.get("special", 0)))
                )

        # Gen 1 damage formula
        level_factor = 2 * attacker["level"] / 5 + 2
        damage = int(level_factor * power * attack_stat / defense_stat / 50) + 2

        # STAB (Same Type Attack Bonus)
        if move_type in attacker["types"]:
            damage = int(damage * 1.5)

        # Critical hit doubles damage
        if is_critical:
            damage *= 2

        # Type effectiveness
        damage = int(damage * effectiveness)

        # Random factor (85% to 100%)
        damage = int(damage * random.uniform(0.85, 1.0))

        # Minimum 1 damage if move connects
        damage = max(1, damage)

        # Effectiveness message
        if effectiveness >= 2.0:
            message = "It's super effective!"
        elif effectiveness <= 0.5:
            message = "It's not very effective..."
        else:
            message = ""

        return damage, message, is_critical

    def check_critical_hit(self, attacker: PartyPokemon, move) -> bool:
        """
        Check if an attack is a critical hit.
        Gen 1: Base crit = base_speed/512, High crit moves = base_speed/64
        Uses the species base speed (not the inflated battle stat) to match Gen 1 rates.

        Args:
            attacker: Attacking Pokemon dict
            move: Move dict

        Returns:
            bool: True if critical hit
        """
        # Use base species speed to avoid inflated crit rates from leveled battle stats
        species_data = get_pokemon(attacker.get("name", "").upper())
        speed = species_data.stats.speed if species_data else attacker["stats"]["speed"]

        if move.get("effect") == "high_crit":
            crit_chance = min(speed / 64, 0.99)  # Cap at 99%
        else:
            crit_chance = min(speed / 512, 0.99)

        return random.random() < crit_chance

    def execute_move(
        self, attacker: PartyPokemon, defender: PartyPokemon, move_name: str
    ) -> list[str]:
        """
        Execute a move and return battle messages.

        Also stores a structured result dict in self.last_player_move or
        self.last_enemy_move so the battle HUD can display last-move info.

        Handles two-turn moves (charge/release), trapping moves, Leech Seed,
        Disable, recoil, and speed-priority ordering helpers.

        Args:
            attacker: Attacking Pokemon dict
            defender: Defending Pokemon dict
            move_name: Name of the move to execute

        Returns:
            list: Messages describing what happened
        """
        messages: list[str] = []
        is_player = attacker is self.player_pokemon

        # Tracking dict — persisted to last_player_move / last_enemy_move at every exit
        move_result: dict = {
            "name": move_name,
            "damage": 0,
            "crit": False,
            "effectiveness": "",
            "status_applied": None,
            "stat_changes": [],  # [{"pokemon": name, "stat": stat, "delta": n}]
            "missed": False,
        }

        def _store_result() -> None:
            if is_player:
                self.last_player_move = move_result
            else:
                self.last_enemy_move = move_result

        # ── Disable check: blocked move cannot be used ────────────────────
        if is_player and self.player_disabled_move == move_name:
            messages.append(
                f"[yellow]{attacker['name']}'s {move_name} is disabled! Choose another move.[/yellow]"
            )
            move_result["missed"] = True
            _store_result()
            return messages
        if not is_player and self.enemy_disabled_move == move_name:
            # Enemy will just skip this turn (choose-move logic should avoid it,
            # but guard here in case)
            messages.append(f"[yellow]{attacker['name']}'s {move_name} is disabled![/yellow]")
            move_result["missed"] = True
            _store_result()
            return messages

        # Status condition checks: paralysis and sleep prevent moves
        if attacker.get("status") == "PARALYSIS":
            if random.random() < 0.25:
                messages.append(f"[yellow]{attacker['name']} is paralyzed! It can't move![/yellow]")
                move_result["missed"] = True
                _store_result()
                return messages

        if attacker.get("status") == "SLEEP":
            sleep_count = attacker.get("sleep_count", 0)
            if sleep_count > 0:
                attacker["sleep_count"] = sleep_count - 1
                messages.append(f"[dim]{attacker['name']} is fast asleep...[/dim]")
                move_result["missed"] = True
                _store_result()
                return messages
            else:
                attacker["status"] = None
                messages.append(f"[green]{attacker['name']} woke up![/green]")
                # Continue to attack

        move = get_move(move_name)

        if not move:
            messages.append(f"[red]Move {move_name} not found![/red]")
            _store_result()
            return messages

        # ── Two-turn move: charge phase ───────────────────────────────────
        # Two-turn moves (Fly, Dig, SolarBeam) first charge for one turn,
        # then release with full power on the next call.
        charging_attr = "player_charging" if is_player else "enemy_charging"
        currently_charging = getattr(self, charging_attr)

        if move.get("effect") == "two_turn":
            if currently_charging != move_name:
                # First turn — charge: deduct PP and announce but don't deal damage yet
                for m in attacker["moves"]:
                    if m["name"] == move_name:
                        if m["pp"] > 0:
                            m["pp"] -= 1
                        else:
                            messages.append(
                                f"[yellow]But there was no PP left for {move_name}![/yellow]"
                            )
                            move_result["missed"] = True
                            _store_result()
                            return messages
                        break
                charge_flavor = {
                    "FLY": "flew up high",
                    "DIG": "burrowed underground",
                    "SOLARBEAM": "absorbed sunlight",
                }.get(move_name, "is charging up")
                messages.append(f"[bold]{attacker['name']} {charge_flavor}![/bold]")
                setattr(self, charging_attr, move_name)
                move_result["missed"] = True  # no damage this turn
                _store_result()
                return messages
            else:
                # Second turn — release: clear charging state and fall through to damage
                setattr(self, charging_attr, None)
                # PP was already deducted on charge turn; skip PP deduction below
                # by jumping directly to accuracy + damage logic
                accuracy = move["accuracy"]
                if accuracy > 0 and random.randint(1, 100) > accuracy:
                    messages.append(f"[yellow]{attacker['name']}'s attack missed![/yellow]")
                    move_result["missed"] = True
                    _store_result()
                    return messages

                damage, effectiveness_msg, is_critical = self.calculate_damage(
                    attacker, defender, move_name
                )
                move_result["damage"] = damage
                move_result["crit"] = is_critical
                move_result["effectiveness"] = effectiveness_msg

                if damage > 0:
                    defender["hp"] = max(0, defender["hp"] - damage)
                    messages.append(f"[cyan]{attacker['name']} dealt {damage} damage![/cyan]")
                    if is_critical:
                        messages.append("[bold yellow]A critical hit![/bold yellow]")
                    if effectiveness_msg:
                        if "super effective" in effectiveness_msg:
                            messages.append(f"[green]{effectiveness_msg}[/green]")
                        elif "not very effective" in effectiveness_msg:
                            messages.append(f"[dim]{effectiveness_msg}[/dim]")
                        else:
                            messages.append(f"[yellow]{effectiveness_msg}[/yellow]")
                else:
                    if effectiveness_msg:
                        messages.append(f"[dim]{effectiveness_msg}[/dim]")

                _store_result()
                return messages

        # ── Normal PP deduction ───────────────────────────────────────────
        for m in attacker["moves"]:
            if m["name"] == move_name:
                if m["pp"] > 0:
                    m["pp"] -= 1
                else:
                    messages.append(f"[yellow]But there was no PP left for {move_name}![/yellow]")
                    move_result["missed"] = True
                    _store_result()
                    return messages
                break

        # Check accuracy
        accuracy = move["accuracy"]
        if accuracy > 0 and random.randint(1, 100) > accuracy:
            messages.append(f"[yellow]{attacker['name']}'s attack missed![/yellow]")
            move_result["missed"] = True
            _store_result()
            return messages

        # Calculate damage
        damage, effectiveness_msg, is_critical = self.calculate_damage(
            attacker, defender, move_name
        )
        move_result["damage"] = damage
        move_result["crit"] = is_critical
        move_result["effectiveness"] = effectiveness_msg

        # Apply damage
        if damage > 0:
            defender["hp"] = max(0, defender["hp"] - damage)
            messages.append(f"[cyan]{attacker['name']} dealt {damage} damage![/cyan]")

            if is_critical:
                messages.append("[bold yellow]A critical hit![/bold yellow]")

            if effectiveness_msg:
                if "super effective" in effectiveness_msg:
                    messages.append(f"[green]{effectiveness_msg}[/green]")
                elif "not very effective" in effectiveness_msg:
                    messages.append(f"[dim]{effectiveness_msg}[/dim]")
                else:
                    messages.append(f"[yellow]{effectiveness_msg}[/yellow]")
        elif move["category"] == "status":
            # Handle status moves
            messages.append(f"[cyan]{attacker['name']} used {move_name}![/cyan]")
        else:
            # No damage dealt (immunity)
            if effectiveness_msg:
                messages.append(f"[dim]{effectiveness_msg}[/dim]")

        # Apply status / stat-change effects from this move
        effect = move.get("effect")
        effect_chance = move.get("effect_chance") or 0

        if effect in ("paralysis", "sleep", "poison", "bad_poison") and effect_chance > 0:
            status_before = defender.get("status")
            status_msgs = self.apply_status_effect(attacker, defender, move)
            messages.extend(status_msgs)
            if defender.get("status") != status_before:
                move_result["status_applied"] = defender.get("status")

        elif effect == "recoil" and damage > 0:
            # Recoil: attacker takes ¼ of damage dealt
            recoil_dmg = max(1, damage // 4)
            attacker["hp"] = max(0, attacker["hp"] - recoil_dmg)
            messages.append(f"[red]{attacker['name']} is hurt by recoil! (-{recoil_dmg} HP)[/red]")

        elif effect == "trap" and effect_chance > 0 and damage > 0:
            # Trapping moves: lock the defender for 2–5 turns
            defender_is_player = defender is self.player_pokemon
            trap_turns_attr = (
                "player_trapped_turns" if defender_is_player else "enemy_trapped_turns"
            )
            trap_dmg_attr = "player_trap_dmg" if defender_is_player else "enemy_trap_dmg"
            if getattr(self, trap_turns_attr) == 0:
                trap_turns = random.randint(2, 5)
                setattr(self, trap_turns_attr, trap_turns)
                # Trap damage is 1/16 of defender's max HP per turn
                trap_dmg = max(1, defender["max_hp"] // 16)
                setattr(self, trap_dmg_attr, trap_dmg)
                messages.append(f"[magenta]{defender['name']} is trapped by {move_name}![/magenta]")

        elif effect == "leech_seed" and effect_chance > 0:
            # Leech Seed: mark the defender as seeded (drained each end-of-turn)
            defender_is_player = defender is self.player_pokemon
            seeded_attr = "player_seeded" if defender_is_player else "enemy_seeded"
            if not getattr(self, seeded_attr):
                setattr(self, seeded_attr, True)
                messages.append(
                    f"[green]{defender['name']} was seeded! HP will be drained each turn.[/green]"
                )
            else:
                messages.append(f"[dim]{defender['name']} is already seeded.[/dim]")

        elif effect == "disable" and effect_chance > 0:
            # Disable: block one of the defender's last-used moves for 3–8 turns
            defender_is_player = defender is self.player_pokemon
            disabled_move_attr = (
                "player_disabled_move" if defender_is_player else "enemy_disabled_move"
            )
            disable_turns_attr = (
                "player_disable_turns" if defender_is_player else "enemy_disable_turns"
            )
            if getattr(self, disabled_move_attr) is None:
                # Pick the most recent move the defender used, or a random valid move
                last_move_data = (
                    self.last_player_move if defender_is_player else self.last_enemy_move
                )
                candidate = last_move_data["name"] if last_move_data else None
                if candidate is None:
                    # Fall back to first move with PP > 0
                    for m in defender["moves"]:
                        if m["pp"] > 0:
                            candidate = m["name"]
                            break
                if candidate:
                    setattr(self, disabled_move_attr, candidate)
                    setattr(self, disable_turns_attr, random.randint(3, 8))
                    messages.append(
                        f"[yellow]{defender['name']}'s {candidate} was disabled![/yellow]"
                    )
                else:
                    messages.append(f"[dim]{defender['name']} has no move to disable.[/dim]")
            else:
                messages.append(f"[dim]{defender['name']}'s move is already disabled.[/dim]")

        elif effect_chance > 0:
            # Stat-change primary / secondary effects
            _STAT_CHANGES = {
                "lower_attack": ("attack", -1, "defender"),
                "lower_defense": ("defense", -1, "defender"),
                "lower_special": ("special", -1, "defender"),
                "lower_speed": ("speed", -1, "defender"),
                "lower_accuracy": ("accuracy", -1, "defender"),
                "lower_defense_2": ("defense", -2, "defender"),
                "raise_attack": ("attack", +1, "attacker"),
                "raise_attack_2": ("attack", +2, "attacker"),
                "raise_defense": ("defense", +1, "attacker"),
                "raise_defense_2": ("defense", +2, "attacker"),
                "raise_special": ("special", +1, "attacker"),
                "raise_special_2": ("special", +2, "attacker"),
                "raise_speed_2": ("speed", +2, "attacker"),
                "raise_evasion": ("evasion", +1, "attacker"),
                "raise_evasion_2": ("evasion", +2, "attacker"),
            }
            if effect in _STAT_CHANGES and random.randint(1, 100) <= effect_chance:
                stat, delta, role = _STAT_CHANGES[effect]
                target = defender if role == "defender" else attacker
                is_player_target = target is self.player_pokemon
                stage_dict = self.player_stat_stages if is_player_target else self.enemy_stat_stages
                current_stage = stage_dict.get(stat, 0)
                new_stage = max(-6, min(6, current_stage + delta))
                if new_stage != current_stage:
                    stage_dict[stat] = new_stage
                    direction = "fell" if delta < 0 else "rose"
                    severity = "sharply " if abs(delta) >= 2 else ""
                    msg_color = "yellow" if delta < 0 else "green"
                    messages.append(
                        f"[{msg_color}]{target['name']}'s {stat} {severity}{direction}![/{msg_color}]"
                    )
                    move_result["stat_changes"].append(
                        {"pokemon": target["name"], "stat": stat, "delta": delta}
                    )

        _store_result()
        return messages

    def is_player_move_priority(self, player_move_name: str) -> bool:
        """
        Return True if the player's chosen move has priority (always goes first).

        Gen 1 priority moves: Quick Attack, Counter.

        Args:
            player_move_name: Move name chosen by the player.

        Returns:
            bool: True when the player's move has the "priority" effect.
        """
        move = get_move(player_move_name)
        if not move:
            return False
        return move.get("effect") == "priority"

    def is_enemy_move_priority(self, enemy_move_name: str) -> bool:
        """
        Return True if the enemy's chosen move has priority.

        Args:
            enemy_move_name: Move name chosen by the enemy.

        Returns:
            bool: True when the enemy's move has the "priority" effect.
        """
        move = get_move(enemy_move_name)
        if not move:
            return False
        return move.get("effect") == "priority"

    def calculate_exp_yield(self) -> int:
        """
        Calculate experience yield from defeating the wild Pokemon.
        Gen 1 formula: (base_exp * level) / 7

        Returns:
            int: Experience points to award
        """
        if not self.wild_pokemon:
            return 0

        base_exp = self.wild_pokemon.get("base_exp", 50)
        level = self.wild_pokemon.get("level", 5)

        # Simplified Gen 1 formula for wild Pokemon
        exp = int((base_exp * level) / 7)
        return max(1, exp)

    def check_level_up(self, pokemon: PartyPokemon) -> tuple[bool, int]:
        """
        Check if Pokemon should level up and apply stat increases.

        Args:
            pokemon: Player's Pokemon dict

        Returns:
            tuple: (leveled_up: bool, new_level: int)
        """
        if "experience" not in pokemon or "next_level_exp" not in pokemon:
            return False, pokemon.get("level", 5)

        if pokemon["experience"] >= pokemon["next_level_exp"]:
            _ = pokemon["level"]  # level captured before increment (informational)
            pokemon["level"] += 1
            pokemon["experience"] -= pokemon["next_level_exp"]
            pokemon["next_level_exp"] = self.calculate_exp_for_level(pokemon["level"] + 1)

            # Apply stat increases (simplified)
            self.apply_level_up_stats(pokemon)

            return True, pokemon["level"]

        return False, pokemon.get("level", 5)

    def calculate_exp_for_level(self, level: int) -> int:
        """
        Calculate experience needed to reach a level.
        Using Medium-Fast growth rate (most common).

        Args:
            level: Target level

        Returns:
            int: Total exp needed for that level
        """
        return level**3

    def apply_level_up_stats(self, pokemon: PartyPokemon) -> None:
        """
        Apply stat increases on level up.
        Simplified: just recalculate from base stats.

        Args:
            pokemon: Pokemon dict to update
        """
        # This is a simplified version - in real game we'd need to track base stats
        # For now, just increase HP and stats slightly
        _ = pokemon["level"]  # used only as a local reference; recalculation below

        # Small stat boost
        if "max_hp" in pokemon:
            hp_increase = random.randint(2, 5)
            pokemon["max_hp"] += hp_increase
            pokemon["hp"] += hp_increase  # Also heal for the bonus HP

        if "stats" in pokemon:
            for stat in ["attack", "defense", "special", "speed"]:
                increase = random.randint(1, 3)
                pokemon["stats"][stat] = pokemon["stats"].get(stat, 10) + increase

    def attempt_catch(self, ball_type: str = "Pokeball") -> tuple[bool, int, list[str]]:
        """
        Attempt to catch the wild Pokemon using Gen 1 catch mechanics.

        Args:
            ball_type: Type of Pokeball used (Pokeball, Great Ball, Ultra Ball, Master Ball)

        Returns:
            tuple: (caught: bool, shakes: int, messages: list[str])
        """
        wild = self.wild_pokemon
        messages: list[str] = []

        # Master Ball always catches
        if wild is None:
            return False, 0, messages
        if ball_type == "Master Ball":
            messages.append("[bold magenta]The MASTER BALL never fails![/bold magenta]")
            return True, 4, messages

        # Ball modifiers (lower = better)
        ball_modifiers = {
            "Pokeball": 255,
            "Great Ball": 200,
            "Ultra Ball": 150,
            "Safari Ball": 150,  # Same as Ultra Ball per Gen 1 mechanics
        }
        ball_mod = ball_modifiers.get(ball_type, 255)

        # Status bonus
        status = wild.get("status")
        if status in ("SLEEP", "FREEZE"):
            status_bonus = 25
        elif status in ("PARALYSIS", "POISON", "BURN"):
            status_bonus = 12
        else:
            status_bonus = 0

        # Catch rate from species data
        catch_rate = wild.get("catch_rate", 255)

        # Safari Zone: apply bait/rock modifier, then skip the HP formula entirely.
        # There is no HP damage in Safari battles, and running the HP formula at
        # full HP would reduce catch_rate to 1/3 — making catching nearly impossible.
        if self.is_safari:
            if self.safari_rock_turns > 0:
                catch_rate = min(255, int(catch_rate * 1.5))
            elif self.safari_bait_turns > 0:
                catch_rate = max(1, catch_rate // 2)
            catch_value = min(255, status_bonus + catch_rate)
        else:
            # HP factor: ((3 * max_hp - 2 * current_hp) * catch_rate) / (3 * max_hp)
            max_hp = wild["max_hp"]
            current_hp = wild["hp"]
            hp_factor = ((3 * max_hp - 2 * current_hp) * catch_rate) // (3 * max_hp)
            catch_value = min(255, status_bonus + hp_factor)

        # Master Ball override (shouldn't reach here, but just in case)
        if ball_mod == 0:
            return True, 4, messages

        # Calculate shake probability
        shake_prob = (catch_value * 255) // ball_mod

        # Determine number of shakes (0-4)
        shakes = 0
        for _ in range(4):
            shake_check = random.randint(0, 255)
            if shake_check <= shake_prob:
                shakes += 1
            else:
                break

        caught = shakes == 4
        return caught, shakes, messages

    def apply_status_effect(
        self, attacker: PartyPokemon, defender: PartyPokemon, move: "MoveData"
    ) -> list[str]:
        """
        Apply a status condition from a move to the defender.

        Args:
            attacker: The attacking Pokemon
            defender: The defending Pokemon that may receive the status
            move: The move dict with effect/effect_chance fields

        Returns:
            list: Messages describing applied status
        """
        messages: list[str] = []
        effect = move.get("effect")
        chance = move.get("effect_chance") or 0

        if not effect or chance <= 0:
            return messages

        # Already has a status condition
        if defender.get("status"):
            return messages

        if random.randint(1, 100) > chance:
            return messages

        if effect == "paralysis":
            defender["status"] = "PARALYSIS"
            messages.append(
                f"[yellow]{defender['name']} was paralyzed! It may be unable to move![/yellow]"
            )
        elif effect == "sleep":
            defender["status"] = "SLEEP"
            defender["sleep_count"] = random.randint(1, 3)
            messages.append(f"[dim]{defender['name']} fell asleep![/dim]")
        elif effect == "poison":
            defender["status"] = "POISON"
            messages.append(f"[magenta]{defender['name']} was poisoned![/magenta]")
        elif effect == "bad_poison":
            defender["status"] = "BAD_POISON"
            defender["toxic_counter"] = 0
            messages.append(f"[magenta]{defender['name']} was badly poisoned![/magenta]")
        elif effect == "burn":
            defender["status"] = "BURN"
            messages.append(f"[red]{defender['name']} was burned![/red]")

        return messages

    def end_of_turn_effects(self, pokemon: PartyPokemon) -> list[str]:
        """
        Apply end-of-turn effects: status damage (BURN, POISON, BAD_POISON),
        Leech Seed drain, trapping move damage, and Disable countdown.

        Args:
            pokemon: Pokemon dict to apply effects to

        Returns:
            list: Messages describing damage taken
        """
        messages: list[str] = []
        is_player = pokemon is self.player_pokemon
        status = pokemon.get("status")

        if status == "BURN":
            dmg = max(1, pokemon["max_hp"] // 8)
            pokemon["hp"] = max(0, pokemon["hp"] - dmg)
            messages.append(f"[red]{pokemon['name']} is hurt by its burn! (-{dmg} HP)[/red]")

        elif status == "POISON":
            dmg = max(1, pokemon["max_hp"] // 16)
            pokemon["hp"] = max(0, pokemon["hp"] - dmg)
            messages.append(f"[magenta]{pokemon['name']} is hurt by poison! (-{dmg} HP)[/magenta]")

        elif status == "BAD_POISON":
            counter = pokemon.get("toxic_counter", 0) + 1
            pokemon["toxic_counter"] = counter
            dmg = max(1, (pokemon["max_hp"] * counter) // 16)
            pokemon["hp"] = max(0, pokemon["hp"] - dmg)
            messages.append(
                f"[magenta]{pokemon['name']} is badly hurt by poison! (-{dmg} HP)[/magenta]"
            )

        # ── Leech Seed drain ─────────────────────────────────────────────
        seeded_attr = "player_seeded" if is_player else "enemy_seeded"
        if getattr(self, seeded_attr) and pokemon["hp"] > 0:
            seed_dmg = max(1, pokemon["max_hp"] // 8)
            pokemon["hp"] = max(0, pokemon["hp"] - seed_dmg)
            # Heal the other side
            other = self.wild_pokemon if is_player else self.player_pokemon
            if other and other["hp"] > 0:
                other["hp"] = min(other["max_hp"], other["hp"] + seed_dmg)
                messages.append(
                    f"[green]{pokemon['name']}'s health is sapped by Leech Seed!"
                    f" (-{seed_dmg} HP → {other['name']} +{seed_dmg} HP)[/green]"
                )
            else:
                messages.append(
                    f"[green]{pokemon['name']}'s health is sapped by Leech Seed!"
                    f" (-{seed_dmg} HP)[/green]"
                )

        # ── Trapping damage ───────────────────────────────────────────────
        trap_turns_attr = "player_trapped_turns" if is_player else "enemy_trapped_turns"
        trap_dmg_attr = "player_trap_dmg" if is_player else "enemy_trap_dmg"
        trap_turns = getattr(self, trap_turns_attr)
        if trap_turns > 0 and pokemon["hp"] > 0:
            trap_dmg = getattr(self, trap_dmg_attr)
            pokemon["hp"] = max(0, pokemon["hp"] - trap_dmg)
            messages.append(
                f"[magenta]{pokemon['name']} is squeezed by the trap! (-{trap_dmg} HP)[/magenta]"
            )
            trap_turns -= 1
            setattr(self, trap_turns_attr, trap_turns)
            if trap_turns == 0:
                messages.append(f"[dim]{pokemon['name']} broke free from the trap![/dim]")

        # ── Disable countdown ─────────────────────────────────────────────
        disabled_move_attr = "player_disabled_move" if is_player else "enemy_disabled_move"
        disable_turns_attr = "player_disable_turns" if is_player else "enemy_disable_turns"
        disable_turns = getattr(self, disable_turns_attr)
        if disable_turns > 0:
            disable_turns -= 1
            setattr(self, disable_turns_attr, disable_turns)
            if disable_turns == 0:
                disabled_move = getattr(self, disabled_move_attr)
                setattr(self, disabled_move_attr, None)
                if disabled_move:
                    messages.append(
                        f"[dim]{pokemon['name']}'s {disabled_move} is no longer disabled.[/dim]"
                    )

        return messages

    def end_battle(self) -> None:
        """Clean up battle state."""
        self.active = False
        self.player_pokemon = None
        self.wild_pokemon = None
        self.turn_count = 0
        self.battle_log = []
        self.is_trainer_battle = False
        self.trainer_data = None
        self.trainer_pokemon_team = []
        self.current_trainer_pokemon_index = 0
        self.prize_money = 0
        self.last_player_move = None
        self.last_enemy_move = None
        self.player_stat_stages = {}
        self.enemy_stat_stages = {}
        self.player_charging = None
        self.enemy_charging = None
        self.player_trapped_turns = 0
        self.enemy_trapped_turns = 0
        self.player_trap_dmg = 0
        self.enemy_trap_dmg = 0
        self.player_seeded = False
        self.enemy_seeded = False
        self.player_disabled_move = None
        self.player_disable_turns = 0
        self.enemy_disabled_move = None
        self.enemy_disable_turns = 0

    def has_more_pokemon(self) -> bool:
        """
        Check if trainer has more Pokemon available.

        Returns:
            bool: True if trainer has more Pokemon
        """
        if not self.is_trainer_battle:
            return False

        # Check if there are Pokemon after the current index with HP > 0
        for i in range(self.current_trainer_pokemon_index + 1, len(self.trainer_pokemon_team)):
            if self.trainer_pokemon_team[i]["hp"] > 0:
                return True
        return False

    def switch_to_next_pokemon(self) -> "Optional[PartyPokemonDict]":
        """
        Switch to trainer's next available Pokemon.

        Returns:
            Next Pokemon dict or None if no Pokemon available
        """
        if not self.is_trainer_battle:
            return None

        # Find next Pokemon with HP > 0
        for i in range(self.current_trainer_pokemon_index + 1, len(self.trainer_pokemon_team)):
            if self.trainer_pokemon_team[i]["hp"] > 0:
                self.current_trainer_pokemon_index = i
                self.wild_pokemon = self.trainer_pokemon_team[i]
                return self.wild_pokemon

        return None

    def choose_trainer_move(self) -> "Optional[MoveSlotDict]":
        """
        Choose a move for the trainer's Pokemon using intelligent weighted AI.

        Uses weighted randomization to prefer effective moves while keeping
        battles varied and unpredictable. Also considers tactical situations.

        Returns:
            Move dict to use, or None if no moves available
        """
        if not self.wild_pokemon or not self.player_pokemon:
            return None

        available_moves = [m for m in self.wild_pokemon["moves"] if m["pp"] > 0]
        if not available_moves:
            return None

        # Calculate weights for each move
        move_weights: list[tuple[MoveSlotDict, float]] = []

        for move in available_moves:
            move_data = get_move(move["name"])
            if not move_data:
                # Unknown move - give minimal weight
                move_weights.append((move, 1.0))
                continue

            weight = 10.0  # Base weight for all moves

            # === EFFECTIVENESS MULTIPLIER ===
            if move_data.get("power", 0) > 0:  # Damaging moves
                effectiveness = get_type_effectiveness(
                    move_data["type"], self.player_pokemon["types"]
                )

                # Scale weight by effectiveness
                if effectiveness >= 2.0:
                    weight *= 3.0  # Super effective - 3x more likely
                elif effectiveness > 1.0:
                    weight *= 2.0  # Slightly effective - 2x more likely
                elif effectiveness < 1.0:
                    weight *= 0.4  # Not very effective - much less likely
                # Normal effectiveness (1.0) - no change

                # === POWER SCALING ===
                # Higher power moves are more attractive
                power = move_data.get("power", 0)
                if power >= 80:
                    weight *= 1.5
                elif power >= 50:
                    weight *= 1.2
                elif power < 30:
                    weight *= 0.8

            # === TACTICAL STATUS MOVES ===
            else:  # Status moves
                # Use status moves more tactically
                effect = move_data.get("effect")

                # Don't use status moves if target already has a status
                if effect in ("paralysis", "sleep", "poison", "bad_poison"):
                    if self.player_pokemon.get("status"):
                        weight *= 0.1  # Very unlikely if already statused
                    else:
                        # Use status moves early in battle
                        if self.turn_count <= 3:
                            weight *= 2.0  # More likely early
                        else:
                            weight *= 0.5  # Less likely later

                # Stat-changing moves are good early
                elif effect in ("attack_up", "defense_up", "speed_up", "special_up"):
                    if self.turn_count <= 2:
                        weight *= 2.5  # Very good early
                    else:
                        weight *= 0.3  # Not great later

                # Generic status moves
                else:
                    weight *= 0.6  # Generally prefer damaging moves

            # === HP-BASED TACTICS ===
            hp_ratio = self.wild_pokemon["hp"] / self.wild_pokemon["max_hp"]

            # When low HP, prefer powerful finishers
            if hp_ratio < 0.3 and move_data.get("power", 0) > 0:
                weight *= 1.5

            # When high HP, more willing to use setup/status
            elif hp_ratio > 0.7 and move_data.get("power", 0) == 0:
                weight *= 1.3

            # === GYM LEADER TYPE PREFERENCE ===
            # Gym leaders strongly favour moves of their specialty type so they
            # feel noticeably harder and more thematic than random route trainers.
            if self.trainer_data and self.trainer_data.trainer_class == "Gym Leader":
                preferred = getattr(self.trainer_data, "preferred_types", [])
                if preferred and move_data.get("type") in preferred:
                    weight *= 2.5  # Strong preference for specialty-type moves

            move_weights.append((move, max(0.1, weight)))  # Ensure minimum weight

        # === WEIGHTED RANDOM SELECTION ===
        total_weight = sum(w for _, w in move_weights)
        rand_value = random.uniform(0, total_weight)

        cumulative = 0
        for move, weight in move_weights:
            cumulative += weight
            if rand_value <= cumulative:
                return move

        # Fallback (should rarely reach here)
        return available_moves[0]
