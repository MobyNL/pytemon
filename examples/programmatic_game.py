#!/usr/bin/env python
"""
Programmatic example: Interact with GameState directly.

This example shows how to use the game engine without the terminal UI.
Useful for automation, testing, or building alternative interfaces.
"""
from pytemon.game_state import GameState
from pytemon.exploration import start_wild_encounter
from pytemon.data.pokemon_data import POKEMON


def print_party(game_state: GameState) -> None:
    """Print the player's current party."""
    party = game_state.game_data.get("party", [])
    print(f"\n{'='*50}")
    print(f"Party ({len(party)}/6):")
    print(f"{'='*50}")
    for i, mon in enumerate(party, 1):
        hp_pct = (mon['hp'] / mon['max_hp']) * 100
        print(
            f"{i}. {mon['name']} (Lv.{mon['level']}) "
            f"HP: {mon['hp']}/{mon['max_hp']} ({hp_pct:.0f}%)"
        )
    print()


def main():
    """Demonstrate programmatic game state manipulation."""
    # Create a new game state
    gs = GameState()
    gs.start_new_game()

    # Set player name
    gs.game_data["player"] = {"name": "Red", "money": 3000, "gender": "boy"}

    # Add starter Pokemon (Charmander)
    starter = gs.create_pokemon("Charmander", level=5)
    gs.game_data["party"] = [starter]

    print("🎮 Pokemon Game - Programmatic Example")
    print(f"Player: {gs.game_data['player']['name']}")
    print(f"Starting location: {gs.location}")
    print(f"Money: ${gs.game_data['player']['money']}")

    print_party(gs)

    # Simulate catching a wild Pokemon
    print("🌿 Exploring Route 1...")
    wild_pokemon = gs.create_pokemon("Pidgey", level=3)
    print(f"A wild {wild_pokemon['name']} (Lv.{wild_pokemon['level']}) appeared!")

    # Add it to the party (simulating a successful catch)
    gs.game_data["party"].append(wild_pokemon)
    print(f"✅ Caught {wild_pokemon['name']}!")

    print_party(gs)

    # Add an item to the bag
    if "Pokeball" not in gs.game_data["bag"]:
        gs.game_data["bag"]["Pokeball"] = 0
    gs.game_data["bag"]["Pokeball"] += 5
    print(f"📦 Added 5 Pokeballs to bag")
    print(f"Bag contents: {dict(gs.game_data['bag'])}")

    # Level up the starter
    print(f"\n⬆️ Leveling up {starter['name']}...")
    starter['level'] += 1
    starter['max_hp'] += 5
    starter['hp'] = starter['max_hp']

    print_party(gs)

    # Move to a new location
    gs.location = "Viridian City"
    print(f"📍 Moved to: {gs.location}")

    # Check Pokedex entries
    seen = gs.game_data.get("pokedex_seen", [])
    caught = gs.game_data.get("pokedex_caught", [])
    print(f"\n📖 Pokedex: {len(caught)} caught, {len(seen)} seen")

    # Save the game
    save_path = gs.save_game("example_save")
    print(f"\n💾 Game saved to: {save_path}")

    print("\n✅ Programmatic game example complete!")


if __name__ == "__main__":
    main()
