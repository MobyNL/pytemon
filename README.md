# pytemon

An interactive Pokémon game that runs entirely in your terminal.

> **Disclaimer:** This is an unofficial fan project and is not affiliated with, endorsed by, or connected to Nintendo, Game Freak, or The Pokémon Company. Pokémon and all related names are trademarks of Nintendo / Creatures Inc. / GAME FREAK inc. This project is made for educational and entertainment purposes only, with love for the franchise.

## Overview

`pytemon` is a pure Python library that implements a full Pokémon Red/Blue adventure using the [Textual](https://textual.textualize.io/) TUI framework. It contains the complete game engine — exploration across all of Kanto, turn-based battles, items, 8 gyms, evolution, fishing, HM field moves, Bill's PC storage, and a rich terminal interface driven entirely by typed commands.

The [robotframework-pokemon](https://github.com/MobyNL/robotframework-pokemon) sibling project wraps this library as a Robot Framework keyword library — because what better way to "run your test suite" than accidentally playing Pokémon?

---

## Setup

```bash
cd pytemon/
poetry install
```

## Run the game

```bash
poetry run python run_terminal.py
```

## Run in the browser (experimental)

The game can also be served locally and played entirely in a browser tab using a
built-in PTY WebSocket server.  No cloud account or extra installs are needed —
`aiohttp` is already a transitive dependency.

```bash
poetry run python run_web_local.py
```

Then open **http://localhost:7681** in your browser.  Each tab launches a
separate game session.  Press `Ctrl+C` in the terminal to stop the server.

The terminal fills the full browser window; the layout automatically adapts when
you resize the tab.

---

## How to play

The game is controlled entirely by typing commands into the input bar at the bottom of the screen. Press `Enter` to submit a command.

### Starting a new game

When you first launch, select **New Game** from the main menu. You'll be asked to enter your name and then choose your starter Pokémon from Professor Oak's lab in Pallet Town.

```
> new game
Enter your name: Ash
Choose your starter: Bulbasaur
```

Your starter choices are **Bulbasaur**, **Charmander**, and **Squirtle**.

---

### Core commands

#### Movement

Travel between locations by name:

```
> move to Viridian City
> go to Route 1
> move to Pewter City
```

Explore your current area for wild Pokémon encounters:

```
> explore
> look around
```

Enter a building you're standing near:

```
> enter Pokemon Center
> enter Gym
> enter Pokemart
```

#### Party & bag

```
> party              # View your Pokémon team
> bag                # View your items
> inspect Pikachu    # Detailed stats for a Pokémon
> status             # Overall player status
```

#### Battle commands

During a battle the game prompts you for input. You can:

```
> 1          # Use move slot 1
> fight      # See your moves
> bag        # Open bag mid-battle
> switch     # Switch active Pokémon
> run        # Attempt to flee
> catch      # Throw a Pokéball (wild Pokémon only)
```

#### Pokémon Center & healing

Walk into any Pokémon Center and your party is healed for free:

```
> move to Cerulean City
> enter Pokemon Center
```

While in a Pokémon Center you can also access Bill's PC:

```
> pc
> deposit Pidgey       # Store a Pokémon
> withdraw Charmander  # Retrieve a Pokémon
> box 2                # View box 2
```

#### Pokémart shopping

```
> enter Pokemart
> buy Pokeball 5       # Buy 5 Pokéballs
> buy Potion 3
> sell Antidote 2
```

#### Map & badges

```
> map               # View the Kanto world map
> badges            # View your badge case
> stats             # Adventure statistics
```

#### Pokédex

```
> pokedex           # Browse all entries
> pokedex Pikachu   # Look up a specific Pokémon
> dex caught        # Filter to caught Pokémon only
> dex seen          # Filter to seen Pokémon only
> dex missing       # Show undiscovered Pokémon
> dex page 3        # Jump to page 3
```

#### Fishing

Fishing spots are available at coastal routes and cities. You receive rods as you progress through the game.

```
> fish                        # Use the best rod you have
> fish with Old Rod
> fish with Good Rod
> fish with Super Rod
```

Rod quality affects which Pokémon you can encounter:

| Rod | Common catches | Level range |
|-----|---------------|-------------|
| Old Rod | Magikarp, Goldeen | 5–15 |
| Good Rod | Magikarp, Goldeen, Tentacool | 10–30 |
| Super Rod | Magikarp, Goldeen, Tentacool, Gyarados | 15–40 |

#### HM field moves

HMs let you interact with the environment outside of battle. Each requires a specific badge:

```
> cut                  # Cut down trees (requires Boulder Badge)
> surf                 # Cross water routes (requires Cascade Badge)
> fly to Pallet Town   # Fast-travel to any visited town (requires Thunder Badge)
> strength             # Push boulders (requires Soul Badge)
> flash                # Light up dark caves (requires Boulder Badge)
```

#### Bicycle

Pick up a Bike Voucher and collect your free bicycle from the Bike Shop in Cerulean City:

```
> ride bike    # Toggle bicycle on/off (routes and forests only)
```

#### Saving & loading

```
> save             # Save your game
```

Autosave runs automatically every few commands. You can adjust it:

```
> enable autosave
> disable autosave
> set autosave frequency 10    # Autosave every 10 commands
```

---

### The Gyms — earn all 8 badges

Defeat the Gym Leader in each city to earn a badge. Badges unlock new areas and HM field moves.

| # | Leader | City | Badge | Type |
|---|--------|------|-------|------|
| 1 | Brock | Pewter City | Boulder Badge 🪨 | Rock |
| 2 | Misty | Cerulean City | Cascade Badge 💧 | Water |
| 3 | Lt. Surge | Vermillion City | Thunder Badge ⚡ | Electric |
| 4 | Erika | Celadon City | Rainbow Badge 🌈 | Grass |
| 5 | Koga | Fuchsia City | Soul Badge 👻 | Poison |
| 6 | Sabrina | Saffron City | Marsh Badge 🧠 | Psychic |
| 7 | Blaine | Cinnabar Island | Volcano Badge 🔥 | Fire |
| 8 | Giovanni | Viridian City | Earth Badge 🌍 | Ground |

```
> move to Pewter City
> enter Gym
> challenge Brock           # Beat Brock's Geodude and Onix
```

---

### The Elite Four

After collecting all 8 badges, head to the Pokémon League at Indigo Plateau:

```
> move to Pokemon League
> elite four
```

Defeat all four Elite Four members and the Champion to enter the **Hall of Fame**.

---

### Special locations

| Location | How to reach | Notable |
|---|---|---|
| Viridian Forest | Route 1 → Route 2 | Bug Pokémon, Pikachu |
| Mt. Moon | Route 3 | Fossils, Clefairy |
| Rock Tunnel | Route 10 | Requires Flash |
| Safari Zone | Fuchsia City | Catch-only zone, 30 Safari Balls |
| Power Plant | Route 10 | Zapdos encounter |
| Seafoam Islands | Route 20 | Articuno encounter |
| Cerulean Cave | Cerulean City | Mewtwo (Champion-only) |
| Silph Co. | Saffron City | Team Rocket raid |

#### Safari Zone

The Safari Zone uses special rules — you can't battle, only throw Safari Balls and Bait:

```
> move to Fuchsia City
> enter Safari Zone
> explore
# In encounter: throw ball / throw bait / run
> exit safari zone
```

#### Fossil revival

Bring a fossil to the Pokémon Lab on Cinnabar Island:

```
> move to Cinnabar Island
> enter Pokemon Lab
> revive fossil
```

---

### Example playthrough (first hour)

```
# Start the game
> new game
# (enter name, choose Charmander)

# Leave Pallet Town
> enter Oak's Lab          # Receive starter Pokémon
> move to Route 1
> explore                  # Wild encounters and levelling up

# First city
> move to Viridian City
> enter Pokemon Center     # Heal up
> enter Pokemart
> buy Pokeball 5

# Head through the forest
> move to Route 2
> move to Viridian Forest
> explore                  # Catch a Caterpie or Pikachu!

# Pewter City debut
> move to Pewter City
> enter Pokemon Center
> enter Gym
> challenge Brock           # Beat Brock's Geodude and Onix
# (earn Boulder Badge 🪨)

# Boulder Badge unlocks Cut
> use cut                   # Clear obstacles on Route 2 South
```

---

## Cheat / dev mode

Type the secret phrase to unlock cheat commands:

```
> i am professor oak
```

Then use `cheat <command>`:

```
> cheat add Pikachu 50       # Add a level 50 Pikachu to your party
> cheat give Master Ball 1   # Give yourself a Master Ball
> cheat warp Cerulean City   # Teleport to any location
> cheat battle Mewtwo 70     # Start a wild battle against Mewtwo
> cheat money 99999          # Add money
> cheat level Charmander 36  # Set a Pokémon's level
> cheat evolve Charmander    # Force evolution
> cheat win                  # Instantly win the current battle
```

Disable cheat mode:

```
> i am not professor oak
```

> **Easter egg:** Type `the truck is real` anywhere for a surprise encounter.

---

## Useful shortcuts

| Command | What it does |
|---------|-------------|
| `help` | List all available commands |
| `map` | View Kanto map |
| `party` | Check your team |
| `bag` | Check your items |
| `badges` | View badge case |
| `save` | Quick save |
| `clear` | Clear the output log |
| `menu` | Return to the main menu |
| `quit` | Exit the game |

---

## Run unit tests

```bash
poetry run pytest tests/ --tb=short -v --cov=pytemon --cov-report=term-missing
```

---

## Project structure

```
pytemon/
├── pytemon/           # The Python package
│   ├── terminal.py    # Textual TUI app
│   ├── game_state.py  # Central game state
│   ├── exploration.py # Movement and encounters
│   ├── buildings.py   # Pokemon Center, Mart, etc.
│   ├── fishing.py     # Fishing system
│   ├── gym_system.py  # Gyms and badges
│   ├── evolution.py   # Evolution logic
│   ├── hm_tm_system.py # HM/TM field and battle moves
│   ├── pc_system.py   # Bill's PC storage
│   ├── battle/        # Battle UI and actions
│   ├── engine/        # Core battle engine
│   ├── data/          # Pokemon, move, trainer data
│   ├── texts/         # All in-game dialog strings
│   └── ui/            # TUI mixin modules
├── tests/             # Pytest unit tests
├── saves/             # Save files (auto-created)
├── run_terminal.py    # Terminal launcher
├── run_web_local.py   # Browser launcher (PTY WebSocket server)
└── pyproject.toml
```
