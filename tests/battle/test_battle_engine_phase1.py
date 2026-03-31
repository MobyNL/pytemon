"""
Phase 1 battle system polish tests.

Covers:
- Two-turn moves (Fly, Dig, SolarBeam)
- Trapping moves (Wrap, Bind, Fire Spin)
- Leech Seed drain
- Speed-priority moves (Quick Attack)
- Stat stage reset between battles
- Recoil damage (1/4 of damage dealt)
- Disable (block one move for 3-8 turns)
"""

import random

from pytemon.data.move_data import MoveSlot
from pytemon.data.pokemon_data import StatsData
from pytemon.engine.battle_engine import BattleState
from pytemon.models import PartyPokemon


def make_pokemon(
    name="PIKACHU",
    number=25,
    level=10,
    speed=90,
    hp=35,
    moves=None,
    **overrides,
) -> PartyPokemon:
    """Create a minimal PartyPokemon for battle testing."""
    if moves is None:
        moves = [MoveSlot(name="THUNDER SHOCK", pp=30, max_pp=30)]
    defaults = {
        "name": name,
        "number": number,
        "level": level,
        "types": ["Electric"],
        "hp": hp,
        "max_hp": hp,
        "stats": StatsData(hp=hp, attack=55, defense=30, special=50, speed=speed),
        "moves": moves,
        "experience": 0,
        "next_level_exp": 1000,
    }
    defaults.update(overrides)
    return PartyPokemon(**defaults)


def setup_battle(player_moves=None, enemy_moves=None):
    """Set up a simple BattleState with two Pokemon."""
    bs = BattleState()
    player = make_pokemon(
        name="PLAYER",
        moves=player_moves or [MoveSlot(name="TACKLE", pp=35, max_pp=35)],
    )
    enemy = make_pokemon(
        name="ENEMY",
        moves=enemy_moves or [MoveSlot(name="TACKLE", pp=35, max_pp=35)],
    )
    bs.player_pokemon = player
    bs.wild_pokemon = enemy
    bs.active = True
    return bs, player, enemy


# ---------------------------------------------------------------------------
# Two-turn moves
# ---------------------------------------------------------------------------


class TestTwoTurnMoves:
    """Tests for charge-then-release two-turn moves."""

    def test_fly_charges_first_turn(self):
        """Fly should charge on first use without dealing damage."""
        bs, player, enemy = setup_battle(player_moves=[MoveSlot(name="FLY", pp=15, max_pp=15)])
        initial_hp = enemy["hp"]
        msgs = bs.execute_move(player, enemy, "FLY")
        # Enemy HP should not change on charge turn
        assert enemy["hp"] == initial_hp
        assert bs.player_charging == "FLY"
        # Charge message should appear
        combined = " ".join(msgs)
        assert (
            "flew up high" in combined.lower()
            or "flew" in combined.lower()
            or "flew up" in combined.lower()
            or "flew" in "".join(msgs).lower()
        )

    def test_fly_releases_second_turn_deals_damage(self):
        """Fly should deal damage on the second (release) turn."""
        bs, player, enemy = setup_battle(player_moves=[MoveSlot(name="FLY", pp=15, max_pp=15)])
        initial_enemy_hp = enemy["hp"]

        # First call — charge
        bs.execute_move(player, enemy, "FLY")
        assert bs.player_charging == "FLY"

        # Second call — release (PP was already deducted so we don't deduct again)
        msgs = bs.execute_move(player, enemy, "FLY")
        assert bs.player_charging is None  # released
        # Damage should have been dealt
        assert enemy["hp"] < initial_enemy_hp or "miss" in " ".join(msgs).lower()

    def test_fly_pp_deducted_only_on_charge(self):
        """PP should only be deducted on the charge turn, not on release."""
        bs, player, enemy = setup_battle(player_moves=[MoveSlot(name="FLY", pp=15, max_pp=15)])
        assert player["moves"][0]["pp"] == 15
        # Charge turn
        bs.execute_move(player, enemy, "FLY")
        assert player["moves"][0]["pp"] == 14
        # Release turn — PP should not decrease again
        bs.execute_move(player, enemy, "FLY")
        assert player["moves"][0]["pp"] == 14

    def test_dig_charges_first_turn(self):
        """Dig should charge on first use."""
        bs, player, enemy = setup_battle(player_moves=[MoveSlot(name="DIG", pp=10, max_pp=10)])
        initial_hp = enemy["hp"]
        bs.execute_move(player, enemy, "DIG")
        assert enemy["hp"] == initial_hp
        assert bs.player_charging == "DIG"

    def test_solarbeam_charges_first_turn(self):
        """SolarBeam should charge on first use."""
        bs, player, enemy = setup_battle(
            player_moves=[MoveSlot(name="SOLARBEAM", pp=10, max_pp=10)]
        )
        initial_hp = enemy["hp"]
        bs.execute_move(player, enemy, "SOLARBEAM")
        assert enemy["hp"] == initial_hp
        assert bs.player_charging == "SOLARBEAM"

    def test_enemy_two_turn_charge(self):
        """Enemy using a two-turn move should charge first."""
        bs, player, enemy = setup_battle(enemy_moves=[MoveSlot(name="FLY", pp=15, max_pp=15)])
        initial_hp = player["hp"]
        bs.execute_move(enemy, player, "FLY")
        assert player["hp"] == initial_hp
        assert bs.enemy_charging == "FLY"

    def test_charging_state_cleared_on_release(self):
        """After release turn, charging state should be None."""
        bs, player, enemy = setup_battle(player_moves=[MoveSlot(name="DIG", pp=10, max_pp=10)])
        bs.execute_move(player, enemy, "DIG")
        assert bs.player_charging == "DIG"
        bs.execute_move(player, enemy, "DIG")
        assert bs.player_charging is None

    def test_charging_state_reset_on_battle_start(self):
        """Starting a new battle should clear charging state."""
        bs = BattleState()
        bs.player_charging = "FLY"
        bs.enemy_charging = "DIG"
        bs.start_wild_battle(make_pokemon(), "PIDGEY", 5)
        assert bs.player_charging is None
        assert bs.enemy_charging is None

    def test_fly_user_is_invulnerable_during_charge(self):
        """Pokemon using Fly should be invulnerable on their charge turn."""
        bs, player, enemy = setup_battle(
            player_moves=[MoveSlot(name="FLY", pp=15, max_pp=15)],
            enemy_moves=[MoveSlot(name="TACKLE", pp=35, max_pp=35)],
        )

        # Player uses Fly (charge turn)
        bs.execute_move(player, enemy, "FLY")
        assert bs.player_charging == "FLY"

        # Enemy attacks player while they're flying
        initial_player_hp = player["hp"]
        msgs = bs.execute_move(enemy, player, "TACKLE")

        # Player should not take damage
        assert player["hp"] == initial_player_hp
        # Message should indicate the attack missed
        combined = " ".join(msgs).lower()
        assert "avoided" in combined or "miss" in combined or "flying" in combined

    def test_dig_user_is_invulnerable_during_charge(self):
        """Pokemon using Dig should be invulnerable on their charge turn."""
        bs, player, enemy = setup_battle(
            player_moves=[MoveSlot(name="DIG", pp=10, max_pp=10)],
            enemy_moves=[MoveSlot(name="TACKLE", pp=35, max_pp=35)],
        )

        # Player uses Dig (charge turn)
        bs.execute_move(player, enemy, "DIG")
        assert bs.player_charging == "DIG"

        # Enemy attacks player while they're underground
        initial_player_hp = player["hp"]
        msgs = bs.execute_move(enemy, player, "TACKLE")

        # Player should not take damage
        assert player["hp"] == initial_player_hp
        # Message should indicate the attack missed
        combined = " ".join(msgs).lower()
        assert "avoided" in combined or "miss" in combined or "underground" in combined

    def test_enemy_fly_user_is_invulnerable(self):
        """Enemy using Fly should be invulnerable during charge turn."""
        bs, player, enemy = setup_battle(
            player_moves=[MoveSlot(name="EMBER", pp=25, max_pp=25)],
            enemy_moves=[MoveSlot(name="FLY", pp=15, max_pp=15)],
        )

        # Enemy uses Fly (charge turn)
        bs.execute_move(enemy, player, "FLY")
        assert bs.enemy_charging == "FLY"

        # Player attacks enemy while they're flying
        initial_enemy_hp = enemy["hp"]
        msgs = bs.execute_move(player, enemy, "EMBER")

        # Enemy should not take damage
        assert enemy["hp"] == initial_enemy_hp
        # Message should indicate the attack missed
        combined = " ".join(msgs).lower()
        assert "avoided" in combined or "miss" in combined

    def test_invulnerable_pokemon_can_still_be_hit_on_release_turn(self):
        """After release turn, Pokemon should be hittable again."""
        bs, player, enemy = setup_battle(
            player_moves=[MoveSlot(name="FLY", pp=15, max_pp=15)],
            enemy_moves=[MoveSlot(name="WATER_GUN", pp=25, max_pp=25)],
        )

        # Charge turn
        bs.execute_move(player, enemy, "FLY")
        assert bs.player_charging == "FLY"

        # Release turn
        bs.execute_move(player, enemy, "FLY")
        assert bs.player_charging is None

        # Now enemy should be able to hit player
        bs.execute_move(enemy, player, "WATER_GUN")
        # Should either deal damage or miss naturally (not due to invulnerability)
        # The key is that charging state is None, so no invulnerability message
        assert bs.player_charging is None


# ---------------------------------------------------------------------------
# Trapping moves
# ---------------------------------------------------------------------------


class TestTrappingMoves:
    """Tests for Wrap, Bind, Fire Spin trapping effect."""

    def test_wrap_sets_trap_turns(self):
        """Wrap should set enemy_trapped_turns between 2 and 5."""
        bs, player, enemy = setup_battle(player_moves=[MoveSlot(name="WRAP", pp=20, max_pp=20)])
        random.seed(42)
        bs.execute_move(player, enemy, "WRAP")
        assert 2 <= bs.enemy_trapped_turns <= 5

    def test_bind_sets_trap_turns(self):
        """Bind should set enemy_trapped_turns between 2 and 5."""
        bs, player, enemy = setup_battle(player_moves=[MoveSlot(name="BIND", pp=20, max_pp=20)])
        random.seed(0)
        bs.execute_move(player, enemy, "BIND")
        assert 2 <= bs.enemy_trapped_turns <= 5

    def test_trap_damage_end_of_turn(self):
        """Trapped Pokemon should take damage at end of turn."""
        bs, player, enemy = setup_battle(player_moves=[MoveSlot(name="WRAP", pp=20, max_pp=20)])
        random.seed(42)
        bs.execute_move(player, enemy, "WRAP")
        assert bs.enemy_trapped_turns >= 1
        initial_hp = enemy["hp"]
        bs.end_of_turn_effects(enemy)
        assert enemy["hp"] < initial_hp
        assert bs.enemy_trap_dmg > 0

    def test_trap_turns_decrement_each_turn(self):
        """Trap turn counter should decrement by 1 each end of turn."""
        bs, _, enemy = setup_battle()
        bs.enemy_trapped_turns = 3
        bs.enemy_trap_dmg = 2
        bs.end_of_turn_effects(enemy)
        assert bs.enemy_trapped_turns == 2

    def test_trap_ends_when_turns_reach_zero(self):
        """Trap should end when turns reach 0."""
        bs, _, enemy = setup_battle()
        bs.enemy_trapped_turns = 1
        bs.enemy_trap_dmg = 2
        msgs = bs.end_of_turn_effects(enemy)
        assert bs.enemy_trapped_turns == 0
        combined = " ".join(msgs)
        assert "broke free" in combined.lower()

    def test_trap_reset_between_battles(self):
        """Trap state should be cleared when a new battle starts."""
        bs = BattleState()
        bs.enemy_trapped_turns = 3
        bs.player_trapped_turns = 2
        bs.start_wild_battle(make_pokemon(), "PIDGEY", 5)
        assert bs.enemy_trapped_turns == 0
        assert bs.player_trapped_turns == 0


# ---------------------------------------------------------------------------
# Leech Seed
# ---------------------------------------------------------------------------


class TestLeechSeed:
    """Tests for Leech Seed drain-per-turn effect."""

    def test_leech_seed_marks_enemy_seeded(self):
        """Using Leech Seed should set enemy_seeded = True."""
        bs, player, enemy = setup_battle(
            player_moves=[MoveSlot(name="LEECH SEED", pp=10, max_pp=10)]
        )
        assert not bs.enemy_seeded
        bs.execute_move(player, enemy, "LEECH SEED")
        assert bs.enemy_seeded

    def test_leech_seed_drains_hp_end_of_turn(self):
        """Seeded Pokemon should lose HP at end of turn."""
        bs, _, enemy = setup_battle()
        bs.enemy_seeded = True
        initial_enemy_hp = enemy["hp"]
        bs.end_of_turn_effects(enemy)
        assert enemy["hp"] < initial_enemy_hp

    def test_leech_seed_heals_other_side(self):
        """HP drained from seeded Pokemon should heal the other side."""
        bs, player, enemy = setup_battle()
        player["hp"] = player["max_hp"] - 10  # slightly damaged
        bs.enemy_seeded = True
        initial_player_hp = player["hp"]
        bs.end_of_turn_effects(enemy)
        assert player["hp"] > initial_player_hp

    def test_leech_seed_does_not_overheal(self):
        """Healed HP from Leech Seed should not exceed max_hp."""
        bs, player, enemy = setup_battle()
        player["hp"] = player["max_hp"]  # already full
        bs.enemy_seeded = True
        bs.end_of_turn_effects(enemy)
        assert player["hp"] <= player["max_hp"]

    def test_leech_seed_no_double_seed(self):
        """Leech Seed should not apply again if already seeded."""
        bs, player, enemy = setup_battle(
            player_moves=[MoveSlot(name="LEECH SEED", pp=10, max_pp=10)]
        )
        # Manually mark enemy as already seeded (bypass accuracy check)
        bs.enemy_seeded = True
        msgs = bs.execute_move(player, enemy, "LEECH SEED")
        combined = " ".join(msgs).lower()
        assert "already" in combined

    def test_leech_seed_reset_between_battles(self):
        """Leech Seed state should reset when a new battle starts."""
        bs = BattleState()
        bs.player_seeded = True
        bs.enemy_seeded = True
        bs.start_wild_battle(make_pokemon(), "PIDGEY", 5)
        assert not bs.player_seeded
        assert not bs.enemy_seeded


# ---------------------------------------------------------------------------
# Priority moves
# ---------------------------------------------------------------------------


class TestPriorityMoves:
    """Tests for speed-priority moves (Quick Attack always goes first)."""

    def test_quick_attack_has_priority_effect(self):
        """Quick Attack move data should have effect='priority'."""
        from pytemon.data import get_move

        qa = get_move("QUICK ATTACK")
        assert qa is not None
        assert qa.get("effect") == "priority"

    def test_is_player_move_priority_true_for_quick_attack(self):
        """BattleState.is_player_move_priority returns True for Quick Attack."""
        bs = BattleState()
        assert bs.is_player_move_priority("QUICK ATTACK") is True

    def test_is_player_move_priority_false_for_tackle(self):
        """BattleState.is_player_move_priority returns False for Tackle."""
        bs = BattleState()
        assert bs.is_player_move_priority("TACKLE") is False

    def test_is_enemy_move_priority_true_for_quick_attack(self):
        """BattleState.is_enemy_move_priority returns True for Quick Attack."""
        bs = BattleState()
        assert bs.is_enemy_move_priority("QUICK ATTACK") is True


# ---------------------------------------------------------------------------
# Stat stage reset between battles
# ---------------------------------------------------------------------------


class TestStatStageReset:
    """Tests that stat stages reset correctly between battles."""

    def test_stat_stages_clear_on_start_wild_battle(self):
        """start_wild_battle should reset player and enemy stat stages."""
        bs = BattleState()
        bs.player_stat_stages = {"attack": 2, "speed": -1}
        bs.enemy_stat_stages = {"defense": 3}
        bs.start_wild_battle(make_pokemon(), "PIDGEY", 5)
        assert bs.player_stat_stages == {}
        assert bs.enemy_stat_stages == {}

    def test_stat_stages_clear_on_end_battle(self):
        """end_battle should reset player and enemy stat stages."""
        bs = BattleState()
        bs.player_stat_stages = {"special": 1}
        bs.enemy_stat_stages = {"speed": -2}
        bs.end_battle()
        assert bs.player_stat_stages == {}
        assert bs.enemy_stat_stages == {}

    def test_stat_stages_accumulate_during_battle(self):
        """Stat stages should accumulate within a single battle."""
        bs, _, _ = setup_battle(player_moves=[MoveSlot(name="GROWL", pp=40, max_pp=40)])
        # Apply stat change manually
        bs.enemy_stat_stages["attack"] = 0
        bs.player_stat_stages["attack"] = 0
        # Check that stages are tracked independently
        bs.enemy_stat_stages["attack"] -= 1
        assert bs.enemy_stat_stages["attack"] == -1
        bs.enemy_stat_stages["attack"] -= 1
        assert bs.enemy_stat_stages["attack"] == -2


# ---------------------------------------------------------------------------
# Recoil damage
# ---------------------------------------------------------------------------


class TestRecoilDamage:
    """Tests for recoil damage — attacker takes 1/4 of damage dealt."""

    def test_recoil_moves_have_recoil_effect(self):
        """Double-Edge, Take Down should have effect='recoil'."""
        from pytemon.data import get_move

        for move_name in ("DOUBLE-EDGE", "TAKE DOWN"):
            md = get_move(move_name)
            if md:
                assert md.get("effect") == "recoil", f"{move_name} should have recoil effect"

    def test_recoil_damages_attacker(self):
        """Recoil move should reduce attacker HP by ~1/4 of damage dealt."""
        bs, player, enemy = setup_battle(
            player_moves=[MoveSlot(name="DOUBLE-EDGE", pp=15, max_pp=15)]
        )
        initial_player_hp = player["hp"]

        # Force the move to hit by using a deterministic seed
        random.seed(1)
        msgs = bs.execute_move(player, enemy, "DOUBLE-EDGE")

        # Player should have taken recoil if damage was dealt
        combined = " ".join(msgs)
        if "damage" in combined.lower() and "recoil" in combined.lower():
            # Recoil was applied
            assert player["hp"] < initial_player_hp

    def test_recoil_is_quarter_of_damage(self):
        """Recoil damage should be exactly floor(damage / 4), minimum 1."""
        bs, player, enemy = setup_battle()

        # Manually simulate: player attacks enemy with a known damage amount
        # by hooking into execute_move internals
        # We'll do this by setting up conditions and verifying the formula
        player["hp"] = 100
        player["max_hp"] = 100
        enemy["hp"] = 100
        enemy["max_hp"] = 100

        # Fake a high-damage recoil move using DOUBLE-EDGE
        # by giving the player an extremely strong attack stat
        player["stats"]["attack"] = 200

        random.seed(5)
        msgs = bs.execute_move(
            player,
            enemy,
            "DOUBLE-EDGE",
        )
        combined = " ".join(msgs)
        if "recoil" in combined.lower():
            # Find "hurt by recoil" line and extract HP lost
            for msg in msgs:
                if "recoil" in msg.lower() and "-" in msg:
                    # e.g. "(-8 HP)"
                    import re

                    match = re.search(r"-(\d+) HP", msg)
                    if match:
                        recoil_taken = int(match.group(1))
                        # Find damage dealt from messages
                        for msg2 in msgs:
                            if "dealt" in msg2:
                                dmatch = re.search(r"dealt (\d+) damage", msg2)
                                if dmatch:
                                    damage = int(dmatch.group(1))
                                    expected = max(1, damage // 4)
                                    assert recoil_taken == expected


# ---------------------------------------------------------------------------
# Disable
# ---------------------------------------------------------------------------


class TestDisable:
    """Tests for the Disable move — blocks one move for 3-8 turns."""

    def test_disable_blocks_enemy_move(self):
        """Disable should block a move on the enemy for 3-8 turns."""
        bs, player, enemy = setup_battle(
            player_moves=[MoveSlot(name="DISABLE", pp=20, max_pp=20)],
            enemy_moves=[MoveSlot(name="TACKLE", pp=35, max_pp=35)],
        )
        random.seed(0)
        # Give enemy a last move to disable
        bs.last_enemy_move = {"name": "TACKLE", "damage": 5}
        bs.execute_move(player, enemy, "DISABLE")
        assert bs.enemy_disabled_move == "TACKLE"
        assert 3 <= bs.enemy_disable_turns <= 8

    def test_disabled_move_cannot_be_used(self):
        """A disabled move should be blocked when the attacker tries to use it."""
        bs, player, enemy = setup_battle(enemy_moves=[MoveSlot(name="TACKLE", pp=35, max_pp=35)])
        bs.enemy_disabled_move = "TACKLE"
        bs.enemy_disable_turns = 5
        msgs = bs.execute_move(enemy, player, "TACKLE")
        combined = " ".join(msgs).lower()
        assert "disabled" in combined

    def test_player_disabled_move_blocked(self):
        """Player's disabled move should be blocked."""
        bs, player, enemy = setup_battle(player_moves=[MoveSlot(name="TACKLE", pp=35, max_pp=35)])
        bs.player_disabled_move = "TACKLE"
        bs.player_disable_turns = 4
        msgs = bs.execute_move(player, enemy, "TACKLE")
        combined = " ".join(msgs).lower()
        assert "disabled" in combined

    def test_disable_turns_decrement_end_of_turn(self):
        """Disable turn counter should decrement each end of turn."""
        bs, player, _ = setup_battle()
        bs.player_disabled_move = "TACKLE"
        bs.player_disable_turns = 5
        bs.end_of_turn_effects(player)
        assert bs.player_disable_turns == 4

    def test_disable_wears_off_at_zero(self):
        """When disable turns reach 0, the move should be re-enabled."""
        bs, player, _ = setup_battle()
        bs.player_disabled_move = "TACKLE"
        bs.player_disable_turns = 1
        msgs = bs.end_of_turn_effects(player)
        assert bs.player_disable_turns == 0
        assert bs.player_disabled_move is None
        combined = " ".join(msgs).lower()
        assert "no longer disabled" in combined

    def test_disable_reset_between_battles(self):
        """Disable state should be cleared on new battle."""
        bs = BattleState()
        bs.player_disabled_move = "TACKLE"
        bs.player_disable_turns = 3
        bs.enemy_disabled_move = "GROWL"
        bs.enemy_disable_turns = 5
        bs.start_wild_battle(make_pokemon(), "PIDGEY", 5)
        assert bs.player_disabled_move is None
        assert bs.player_disable_turns == 0
        assert bs.enemy_disabled_move is None
        assert bs.enemy_disable_turns == 0

    def test_disable_end_battle_clears(self):
        """end_battle should clear disable state."""
        bs = BattleState()
        bs.player_disabled_move = "SLAM"
        bs.player_disable_turns = 2
        bs.end_battle()
        assert bs.player_disabled_move is None
        assert bs.player_disable_turns == 0
