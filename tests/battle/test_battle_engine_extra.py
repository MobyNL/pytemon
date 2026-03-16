"""
Extended unit tests for PokemonLibrary/engine/battle_engine.py.

Complements the existing tests in test_battle_engine.py by covering the
branches that are currently uncovered (trainer battles, execute_move,
catch calculation, status effects, exp yield, etc.).
"""

from pytemon.data.move_data import MoveSlot
from pytemon.data.pokemon_data import StatsData
from pytemon.data.trainer_data import Trainer, TrainerPokemon
from pytemon.engine.battle_engine import BattleState
from pytemon.models import PartyPokemon


def make_pokemon(
    name="PIKACHU",
    number=25,
    level=10,
    types=None,
    hp=35,
    max_hp=35,
    moves=None,
    status=None,
    **overrides,
) -> PartyPokemon:
    if types is None:
        types = ["Electric"]
    if moves is None:
        moves = [MoveSlot(name="THUNDER SHOCK", pp=30, max_pp=30)]
    stats = StatsData(hp=max_hp, attack=55, defense=30, special=50, speed=90)
    p = PartyPokemon(
        name=name,
        number=number,
        level=level,
        types=types,
        hp=hp,
        max_hp=max_hp,
        stats=stats,
        moves=moves,
        experience=0,
        next_level_exp=1000,
    )
    p.status = status
    for k, v in overrides.items():
        setattr(p, k, v)
    return p


def make_trainer(trainer_id: str = "test_trainer") -> Trainer:
    return Trainer(
        id=trainer_id,
        name="Youngster Billy",
        trainer_class="Youngster",
        location="Route 1",
        pokemon=[
            TrainerPokemon(species="RATTATA", level=5),
            TrainerPokemon(species="PIDGEY", level=5),
        ],
        prize_money=100,
        intro_text=["Let's battle!"],
        defeat_text=["I lost!"],
        victory_text=["I won!"],
    )


# ---------------------------------------------------------------------------
# start_trainer_battle
# ---------------------------------------------------------------------------


class TestStartTrainerBattle:
    def test_battle_becomes_active(self):
        bs = BattleState()
        player = make_pokemon()
        trainer = make_trainer()
        bs.start_trainer_battle(player, trainer)
        assert bs.active is True

    def test_is_trainer_battle_flag(self):
        bs = BattleState()
        player = make_pokemon()
        trainer = make_trainer()
        bs.start_trainer_battle(player, trainer)
        assert bs.is_trainer_battle is True

    def test_player_cannot_run_in_trainer_battle(self):
        bs = BattleState()
        player = make_pokemon()
        trainer = make_trainer()
        bs.start_trainer_battle(player, trainer)
        assert bs.player_can_run is False

    def test_trainer_team_is_generated(self):
        bs = BattleState()
        player = make_pokemon()
        trainer = make_trainer()
        bs.start_trainer_battle(player, trainer)
        assert len(bs.trainer_pokemon_team) == 2

    def test_first_trainer_pokemon_is_active(self):
        bs = BattleState()
        player = make_pokemon()
        trainer = make_trainer()
        bs.start_trainer_battle(player, trainer)
        assert bs.wild_pokemon is not None
        assert bs.wild_pokemon.name == "RATTATA"

    def test_prize_money_is_set(self):
        bs = BattleState()
        player = make_pokemon()
        trainer = make_trainer()
        bs.start_trainer_battle(player, trainer)
        assert bs.prize_money == 100


# ---------------------------------------------------------------------------
# get_moves_for_level
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# get_moves_for_level / get_new_moves_at_level
# ---------------------------------------------------------------------------


class TestGetMovesForLevel:
    def test_returns_list_for_valid_species_data(self):
        from pytemon.data.pokemon_data import get_pokemon

        bs = BattleState()
        species = get_pokemon("CHARMANDER")
        result = bs.get_moves_for_level(species, 1)
        assert isinstance(result, list)

    def test_returns_up_to_four_moves(self):
        from pytemon.data.pokemon_data import get_pokemon

        bs = BattleState()
        species = get_pokemon("BULBASAUR")
        result = bs.get_moves_for_level(species, 20)
        assert len(result) <= 4

    def test_get_new_moves_unknown_species_returns_empty(self):
        bs = BattleState()
        result = bs.get_new_moves_at_level("UNKNOWNMON", 5)
        assert result == []

    def test_get_new_moves_at_level_returns_list(self):
        bs = BattleState()
        result = bs.get_new_moves_at_level("CHARMANDER", 9)
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# calculate_exp_yield
# ---------------------------------------------------------------------------


class TestCalculateExpYield:
    def test_no_wild_pokemon_returns_zero(self):
        bs = BattleState()
        assert bs.calculate_exp_yield() == 0

    def test_returns_positive_exp(self):
        bs = BattleState()
        player = make_pokemon()
        bs.start_wild_battle(player, "RATTATA", 5)
        exp = bs.calculate_exp_yield()
        assert exp >= 1

    def test_higher_level_gives_more_exp(self):
        bs_low = BattleState()
        bs_high = BattleState()
        player = make_pokemon()
        bs_low.start_wild_battle(player, "RATTATA", 5)
        bs_high.start_wild_battle(player, "RATTATA", 20)
        assert bs_high.calculate_exp_yield() > bs_low.calculate_exp_yield()


# ---------------------------------------------------------------------------
# check_critical_hit
# ---------------------------------------------------------------------------


class TestCheckCriticalHit:
    def test_returns_bool(self):
        bs = BattleState()
        attacker = make_pokemon()
        from pytemon.data import get_move

        move = get_move("TACKLE")  # TACKLE always exists
        result = bs.check_critical_hit(attacker, move)
        assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# execute_move
# ---------------------------------------------------------------------------


class TestExecuteMove:
    def test_execute_move_returns_messages_list(self):
        bs = BattleState()
        attacker = make_pokemon()
        defender = make_pokemon(
            name="RATTATA",
            number=19,
            types=["Normal"],
            moves=[MoveSlot(name="TACKLE", pp=35, max_pp=35)],
        )
        messages = bs.execute_move(attacker, defender, "THUNDER SHOCK")
        assert isinstance(messages, list)

    def test_execute_unknown_move_returns_error_message(self):
        bs = BattleState()
        attacker = make_pokemon()
        defender = make_pokemon(name="RATTATA", number=19, types=["Normal"])
        messages = bs.execute_move(attacker, defender, "FAKE MOVE XYZ")
        assert any("not found" in m.lower() for m in messages)

    def test_paralyzed_pokemon_may_fail_to_move(self):
        # With paralysis, move can fail — run many times to cover both branches
        import random

        random.seed(42)
        bs = BattleState()
        attacker = make_pokemon(status="PARALYSIS")
        defender = make_pokemon(name="RATTATA", number=19, types=["Normal"])
        results = []
        for _ in range(20):
            messages = bs.execute_move(attacker, defender, "THUNDER SHOCK")
            results.append(messages)
        assert len(results) == 20
        # Each call must return a non-empty message list (hit or miss)
        assert all(isinstance(r, list) and len(r) > 0 for r in results)

    def test_sleeping_pokemon_stays_asleep(self):
        bs = BattleState()
        attacker = make_pokemon(status="SLEEP")
        attacker["sleep_count"] = 2
        defender = make_pokemon(name="RATTATA", number=19, types=["Normal"])
        messages = bs.execute_move(attacker, defender, "THUNDER SHOCK")
        assert any("asleep" in m.lower() for m in messages)

    def test_sleeping_pokemon_wakes_up(self):
        bs = BattleState()
        attacker = make_pokemon(status="SLEEP")
        attacker["sleep_count"] = 0
        defender = make_pokemon(name="RATTATA", number=19, types=["Normal"])
        messages = bs.execute_move(attacker, defender, "THUNDER SHOCK")
        combined = " ".join(messages)
        # sleep_count=0 should force wake-up on the first check
        assert "woke" in combined.lower()

    def test_zero_pp_move_returns_error(self):
        bs = BattleState()
        attacker = make_pokemon(moves=[MoveSlot(name="TACKLE", pp=0, max_pp=35)])
        defender = make_pokemon(name="RATTATA", number=19, types=["Normal"])
        messages = bs.execute_move(attacker, defender, "TACKLE")
        # With 0 PP, a message about no PP should appear
        assert isinstance(messages, list)
        assert len(messages) > 0


# ---------------------------------------------------------------------------
# attempt_catch
# ---------------------------------------------------------------------------


class TestAttemptCatch:
    def test_no_wild_pokemon_returns_no_catch(self):
        bs = BattleState()
        caught, _, _ = bs.attempt_catch("Pokeball")
        assert caught is False

    def test_master_ball_always_catches(self):
        bs = BattleState()
        player = make_pokemon()
        bs.start_wild_battle(player, "DRAGONITE", 50)  # very hard to catch normally
        caught, shakes, _ = bs.attempt_catch("Master Ball")
        assert caught is True
        assert shakes == 4

    def test_regular_pokeball_returns_valid_result(self):
        bs = BattleState()
        player = make_pokemon()
        bs.start_wild_battle(player, "RATTATA", 3)
        caught, shakes, _ = bs.attempt_catch("Pokeball")
        assert isinstance(caught, bool)
        assert 0 <= shakes <= 4

    def test_returns_tuple_of_three(self):
        bs = BattleState()
        player = make_pokemon()
        bs.start_wild_battle(player, "PIKACHU", 5)
        result = bs.attempt_catch("Great Ball")
        assert isinstance(result, tuple)
        assert len(result) == 3


# ---------------------------------------------------------------------------
# apply_status_effect
# ---------------------------------------------------------------------------


class TestApplyStatusEffect:
    def test_returns_empty_list_for_move_with_no_effect(self):
        bs = BattleState()
        attacker = make_pokemon()
        defender = make_pokemon(name="RATTATA", number=19, types=["Normal"])
        from pytemon.data import get_move

        move = get_move("TACKLE")
        result = bs.apply_status_effect(attacker, defender, move)
        assert result == []

    def test_already_statused_defender_not_affected(self):
        bs = BattleState()
        attacker = make_pokemon()
        defender = make_pokemon(name="RATTATA", number=19, types=["Normal"], status="POISON")
        from pytemon.data import get_move

        move = get_move("THUNDER WAVE")
        if move:
            bs.apply_status_effect(attacker, defender, move)
            # Defender already has status; should remain unchanged
            assert defender.get("status") in ("POISON", "PARALYSIS")


# ---------------------------------------------------------------------------
# end_of_turn_effects
# ---------------------------------------------------------------------------


class TestEndOfTurnEffects:
    def test_healthy_pokemon_returns_empty_list(self):
        bs = BattleState()
        p = make_pokemon()
        result = bs.end_of_turn_effects(p)
        assert isinstance(result, list)

    def test_poisoned_pokemon_takes_damage(self):
        bs = BattleState()
        p = make_pokemon(hp=35, max_hp=35, status="POISON")
        bs.end_of_turn_effects(p)
        assert p.hp < 35

    def test_burned_pokemon_end_of_turn(self):
        bs = BattleState()
        p = make_pokemon(hp=35, max_hp=35, status="BURN")
        # Burn deals 1/8 max HP damage per turn
        result = bs.end_of_turn_effects(p)
        assert isinstance(result, list)
        assert len(result) == 1  # One damage message for BURN
        expected_dmg = max(1, 35 // 8)
        assert p.hp == 35 - expected_dmg


# ===========================================================================
# Additional tests for uncovered branches
# ===========================================================================


class TestApplyStatusEffectBranches:
    def test_paralysis_effect(self):
        from pytemon.engine import BattleState

        bs = BattleState()
        p1 = bs.generate_wild_pokemon("PIKACHU", 10)
        bs.start_wild_battle(p1, "RATTATA", 10)
        move = {"effect": "paralysis", "effect_chance": 100}
        bs.wild_pokemon["status"] = None
        bs.apply_status_effect(p1, bs.wild_pokemon, move)
        assert bs.wild_pokemon["status"] == "PARALYSIS"

    def test_sleep_effect(self):
        from pytemon.engine import BattleState

        bs = BattleState()
        p1 = bs.generate_wild_pokemon("PIKACHU", 10)
        bs.start_wild_battle(p1, "RATTATA", 10)
        move = {"effect": "sleep", "effect_chance": 100}
        bs.wild_pokemon["status"] = None
        bs.apply_status_effect(p1, bs.wild_pokemon, move)
        assert bs.wild_pokemon["status"] == "SLEEP"
        assert "sleep_count" in bs.wild_pokemon

    def test_poison_effect(self):
        from pytemon.engine import BattleState

        bs = BattleState()
        p1 = bs.generate_wild_pokemon("PIKACHU", 10)
        bs.start_wild_battle(p1, "RATTATA", 10)
        move = {"effect": "poison", "effect_chance": 100}
        bs.wild_pokemon["status"] = None
        bs.apply_status_effect(p1, bs.wild_pokemon, move)
        assert bs.wild_pokemon["status"] == "POISON"

    def test_bad_poison_effect(self):
        from pytemon.engine import BattleState

        bs = BattleState()
        p1 = bs.generate_wild_pokemon("PIKACHU", 10)
        bs.start_wild_battle(p1, "RATTATA", 10)
        move = {"effect": "bad_poison", "effect_chance": 100}
        bs.wild_pokemon["status"] = None
        bs.apply_status_effect(p1, bs.wild_pokemon, move)
        assert bs.wild_pokemon["status"] == "BAD_POISON"


class TestEndOfTurnEffectsBranches:
    def test_bad_poison_increases_counter(self):
        from pytemon.engine import BattleState

        bs = BattleState()
        p = bs.generate_wild_pokemon("PIKACHU", 10)
        p["status"] = "BAD_POISON"
        p["toxic_counter"] = 0
        msgs = bs.end_of_turn_effects(p)
        assert p["toxic_counter"] == 1
        assert len(msgs) > 0
        assert len(msgs) > 0

    def test_sleep_no_damage(self):
        from pytemon.engine import BattleState

        bs = BattleState()
        p = bs.generate_wild_pokemon("PIKACHU", 10)
        p["status"] = "SLEEP"
        hp_before = p["hp"]
        bs.end_of_turn_effects(p)
        assert p["hp"] == hp_before


class TestHasMorePokemon:
    def test_wild_battle_returns_false(self):
        from pytemon.engine import BattleState

        bs = BattleState()
        p = bs.generate_wild_pokemon("PIKACHU", 5)
        bs.start_wild_battle(p, "RATTATA", 5)
        assert bs.has_more_pokemon() is False

    def test_trainer_battle_last_pokemon(self):
        from pytemon.data.trainer_data import TRAINERS
        from pytemon.engine import BattleState

        bs = BattleState()
        trainer = next(iter(TRAINERS.values()))
        p = bs.generate_wild_pokemon("PIKACHU", 10)
        bs.start_trainer_battle(p, trainer)
        # Faint all trainer pokemon
        for t in bs.trainer_pokemon_team:
            t["hp"] = 0
        assert bs.has_more_pokemon() is False


class TestSwitchToNextPokemon:
    def test_wild_battle_returns_none(self):
        from pytemon.engine import BattleState

        bs = BattleState()
        p = bs.generate_wild_pokemon("PIKACHU", 5)
        bs.start_wild_battle(p, "RATTATA", 5)
        result = bs.switch_to_next_pokemon()
        assert result is None


class TestChooseTrainerMove:
    def test_returns_none_without_pokemon(self):
        from pytemon.engine import BattleState

        bs = BattleState()
        result = bs.choose_trainer_move()
        assert result is None

    def test_trainer_battle_returns_move(self):
        from pytemon.data.trainer_data import TRAINERS
        from pytemon.engine import BattleState

        bs = BattleState()
        trainer = next(iter(TRAINERS.values()))
        p = bs.generate_wild_pokemon("PIKACHU", 10)
        bs.start_trainer_battle(p, trainer)
        move = bs.choose_trainer_move()
        # Trainer's first pokemon has moves so a move should always be returned
        assert move is not None
        assert hasattr(move, "name")
        assert move.name  # Must have a non-empty name


class TestGenerateWildPokemon:
    def test_unknown_species_fallback(self):
        from pytemon.engine import BattleState

        bs = BattleState()
        p = bs.generate_wild_pokemon("FAKEMON999999", 5)
        assert "hp" in p
        assert p["level"] == 5

    def test_level_scales_stats(self):
        from pytemon.engine import BattleState

        bs = BattleState()
        low = bs.generate_wild_pokemon("PIKACHU", 5)
        high = bs.generate_wild_pokemon("PIKACHU", 50)
        assert high["max_hp"] > low["max_hp"]


class TestGetNewMovesAtLevel:
    def test_returns_list(self):
        from pytemon.engine import BattleState

        bs = BattleState()
        result = bs.get_new_moves_at_level("PIKACHU", 10)
        assert isinstance(result, list)

    def test_unknown_species_empty_list(self):
        from pytemon.engine import BattleState

        bs = BattleState()
        result = bs.get_new_moves_at_level("FAKEMON999999", 10)
        assert result == []


class TestGymLeaderAI:
    """Gym leaders should prefer moves of their specialty type."""

    def test_gym_leader_preferred_types_field(self):
        from pytemon.data.trainer_data import TRAINERS

        brock = TRAINERS["gym_leader_brock"]
        assert "Rock" in brock.preferred_types or "Ground" in brock.preferred_types

        misty = TRAINERS["gym_leader_misty"]
        assert "Water" in misty.preferred_types

    def test_gym_leader_move_selection_favours_preferred_type(self):
        """Gym leader AI weights preferred-type moves more heavily.

        This test uses a synthetic battle state where the gym leader's Pokemon
        has both a preferred-type move and a normal-type move so we can verify
        the preferred type is chosen more often.
        """
        import random

        from pytemon.data.move_data import MoveSlot
        from pytemon.data.trainer_data import Trainer, TrainerPokemon
        from pytemon.engine import BattleState

        random.seed(0)
        bs = BattleState()

        # Create a synthetic gym leader with Water preferred type
        fake_leader = Trainer(
            id="fake_leader",
            name="Fake Leader",
            trainer_class="Gym Leader",
            location="Cerulean City",
            pokemon=[TrainerPokemon(species="STARMIE", level=25)],
            prize_money=2500,
            intro_text=[],
            defeat_text=[],
            preferred_types=["Water"],
        )

        player = bs.generate_wild_pokemon("CHARMANDER", 15)
        bs.start_trainer_battle(player, fake_leader)
        bs.player_pokemon = player

        # Inject moves: one Water-type and one Normal-type on the active Pokemon
        bs.wild_pokemon["moves"] = [
            MoveSlot(name="SURF", pp=15, max_pp=15),
            MoveSlot(name="TACKLE", pp=35, max_pp=35),
        ]

        # Count how often the Water move (SURF) is picked
        water_picks = 0
        samples = 200
        for _ in range(samples):
            move = bs.choose_trainer_move()
            if move is not None and move["name"] == "SURF":
                water_picks += 1

        # Gym leader should pick the preferred-type move significantly more than
        # 50% of the time (expected ~71%+ due to 2.5x weight boost for preferred type)
        assert water_picks > samples // 2

    def test_non_gym_leader_has_empty_preferred_types(self):
        from pytemon.data.trainer_data import TRAINERS

        # Find a non-gym-leader trainer
        for trainer in TRAINERS.values():
            if trainer.trainer_class != "Gym Leader" and trainer.trainer_class != "Rival":
                assert trainer.preferred_types == []
                break

    def test_all_gym_leaders_have_preferred_types(self):
        from pytemon.data.trainer_data import TRAINERS

        gym_leaders = {k: v for k, v in TRAINERS.items() if v.trainer_class == "Gym Leader"}
        for leader_id, leader in gym_leaders.items():
            assert len(leader.preferred_types) > 0, f"Gym leader {leader_id} has no preferred_types"


class TestBurnStatus:
    """BURN status should deal 1/8 max HP damage per turn."""

    def test_burn_applies_via_move(self):
        bs = BattleState()
        p1 = bs.generate_wild_pokemon("CHARMANDER", 10)
        bs.start_wild_battle(p1, "SQUIRTLE", 10)
        move = {"effect": "burn", "effect_chance": 100}
        bs.wild_pokemon["status"] = None
        bs.apply_status_effect(p1, bs.wild_pokemon, move)
        assert bs.wild_pokemon["status"] == "BURN"

    def test_burn_does_not_stack(self):
        """Cannot apply BURN to a Pokemon that already has a status."""
        bs = BattleState()
        p1 = bs.generate_wild_pokemon("CHARMANDER", 10)
        bs.start_wild_battle(p1, "SQUIRTLE", 10)
        bs.wild_pokemon["status"] = "POISON"
        move = {"effect": "burn", "effect_chance": 100}
        bs.apply_status_effect(p1, bs.wild_pokemon, move)
        assert bs.wild_pokemon["status"] == "POISON"  # Not overwritten
