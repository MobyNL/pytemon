#!/usr/bin/env python
"""
Battle simulation example: Run a Pokemon battle programmatically.

Demonstrates using the battle engine without the terminal UI.
"""
from pytemon.game_state import GameState
from pytemon.engine.battle_engine import BattleState
from pytemon.data.move_data import MOVES


def print_battle_state(bs: BattleState) -> None:
    """Print current battle state."""
    player_mon = bs.player_pokemon
    opponent_mon = bs.opponent_pokemon

    print(f"\n{'='*60}")
    print(f"BATTLE: {player_mon['name']} vs {opponent_mon['name']}")
    print(f"{'='*60}")
    print(
        f"  Your {player_mon['name']} (Lv.{player_mon['level']}) "
        f"HP: {player_mon['hp']}/{player_mon['max_hp']}"
    )
    print(
        f"  Foe {opponent_mon['name']} (Lv.{opponent_mon['level']}) "
        f"HP: {opponent_mon['hp']}/{opponent_mon['max_hp']}"
    )
    print()


def main():
    """Simulate a Pokemon battle programmatically."""
    # Setup game state
    gs = GameState()
    gs.start_new_game()

    # Create battling Pokemon
    player_mon = gs.create_pokemon("Pikachu", level=10)
    opponent_mon = gs.create_pokemon("Rattata", level=8)

    # Give Pikachu some moves
    player_mon["moves"] = ["Thunder Shock", "Growl", "Quick Attack", "Tail Whip"]

    print("⚔️  Pokemon Battle Simulation")
    print_battle_state_header(player_mon, opponent_mon)

    # Create battle state
    bs = BattleState(player_mon, opponent_mon, is_trainer_battle=False)

    turn = 1
    while not bs.is_battle_over():
        print(f"\n{'─'*60}")
        print(f"Turn {turn}")
        print(f"{'─'*60}")

        # Player uses a move (Thunder Shock)
        player_move = "Thunder Shock"
        print(f"\n{player_mon['name']} used {player_move}!")

        player_result = bs.execute_move(player_move, is_player_move=True)

        if player_result["damage"] > 0:
            effectiveness = player_result.get("effectiveness", 1.0)
            if effectiveness > 1.0:
                print("It's super effective!")
            elif effectiveness < 1.0:
                print("It's not very effective...")
            print(f"Dealt {player_result['damage']} damage!")

        if player_result.get("critical"):
            print("A critical hit!")

        # Check if opponent fainted
        if bs.is_battle_over():
            print(f"\n💥 Foe {opponent_mon['name']} fainted!")
            print(f"✅ {player_mon['name']} wins!")
            break

        # Opponent uses a move
        opponent_moves = opponent_mon.get("moves", ["Tackle"])
        opponent_move = opponent_moves[0]  # Simple AI: always use first move

        print(f"\nFoe {opponent_mon['name']} used {opponent_move}!")
        opponent_result = bs.execute_move(opponent_move, is_player_move=False)

        if opponent_result["damage"] > 0:
            print(f"Took {opponent_result['damage']} damage!")

        if opponent_result.get("critical"):
            print("A critical hit!")

        # Check if player fainted
        if bs.is_battle_over():
            print(f"\n💥 {player_mon['name']} fainted!")
            print(f"❌ You lose!")
            break

        # Show HP after turn
        print(
            f"\n{player_mon['name']}: {player_mon['hp']}/{player_mon['max_hp']} HP"
        )
        print(
            f"Foe {opponent_mon['name']}: "
            f"{opponent_mon['hp']}/{opponent_mon['max_hp']} HP"
        )

        turn += 1

    print(f"\n{'='*60}")
    print("Battle ended!")
    print(f"{'='*60}\n")


def print_battle_state_header(player_mon: dict, opponent_mon: dict) -> None:
    """Print battle header."""
    print(f"\n{'='*60}")
    print(f"  Your {player_mon['name']} (Lv.{player_mon['level']})")
    print("    vs")
    print(f"  Foe {opponent_mon['name']} (Lv.{opponent_mon['level']})")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
