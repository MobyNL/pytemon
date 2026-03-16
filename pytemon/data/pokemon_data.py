"""
Generation I Pokémon data.

Each entry contains:
  - name, national dex number
  - types (one or two)
  - base stats: hp, attack, defense, special, speed
  - catch rate (Gen 1 value, 0-255)
  - base XP yield
  - level-up learnset: {level: [move_name, ...]}
  - evolution: LevelEvolution, ItemEvolution, list of ItemEvolution, or None
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

# Type constants
NORMAL = "Normal"
FIRE = "Fire"
WATER = "Water"
GRASS = "Grass"
ELECTRIC = "Electric"
ICE = "Ice"
FIGHTING = "Fighting"
POISON = "Poison"
GROUND = "Ground"
FLYING = "Flying"
PSYCHIC = "Psychic"
BUG = "Bug"
ROCK = "Rock"
GHOST = "Ghost"
DRAGON = "Dragon"


@dataclass
class StatsData:
    hp: int
    attack: int
    defense: int
    special: int
    speed: int

    def __getitem__(self, key: str):
        return getattr(self, key)

    def __setitem__(self, key: str, value):
        setattr(self, key, value)

    def get(self, key: str, default=None):
        try:
            return getattr(self, key)
        except AttributeError:
            return default


@dataclass
class LevelEvolution:
    level: int
    into_species: str

    def __getitem__(self, key: str):
        if key == "into":
            return self.into_species
        return getattr(self, key)

    def get(self, key: str, default=None):
        try:
            return self[key]
        except AttributeError:
            return default


@dataclass
class ItemEvolution:
    item: str
    into_species: str

    def __getitem__(self, key: str):
        if key == "into":
            return self.into_species
        return getattr(self, key)

    def get(self, key: str, default=None):
        try:
            return self[key]
        except AttributeError:
            return default


@dataclass
class SpeciesData:
    name: str
    number: int
    types: list
    stats: StatsData
    catch_rate: int
    base_exp: int
    learnset: dict
    evolution: Optional[object] = None

    def __getitem__(self, key: str):
        return getattr(self, key)

    def get(self, key: str, default=None):
        try:
            return getattr(self, key)
        except AttributeError:
            return default


POKEMON: dict[int, SpeciesData] = {
    1: SpeciesData(
        name="BULBASAUR",
        number=1,
        types=[GRASS, POISON],
        stats=StatsData(hp=45, attack=49, defense=49, special=65, speed=45),
        catch_rate=45,
        base_exp=64,
        learnset={
            1: ["TACKLE", "GROWL"],
            7: ["LEECH SEED"],
            13: ["VINE WHIP"],
            20: ["POISONPOWDER"],
            22: ["RAZOR LEAF"],
            29: ["GROWTH"],
            38: ["SLEEP POWDER"],
            46: ["SOLARBEAM"],
        },
        evolution=LevelEvolution(level=16, into_species="IVYSAUR"),
    ),
    2: SpeciesData(
        name="IVYSAUR",
        number=2,
        types=[GRASS, POISON],
        stats=StatsData(hp=60, attack=62, defense=63, special=80, speed=60),
        catch_rate=45,
        base_exp=141,
        learnset={
            1: ["TACKLE", "GROWL", "LEECH SEED"],
            22: ["VINE WHIP"],
            30: ["POISONPOWDER"],
            32: ["RAZOR LEAF"],
            40: ["GROWTH"],
            50: ["SLEEP POWDER"],
            59: ["SOLARBEAM"],
        },
        evolution=LevelEvolution(level=32, into_species="VENUSAUR"),
    ),
    3: SpeciesData(
        name="VENUSAUR",
        number=3,
        types=[GRASS, POISON],
        stats=StatsData(hp=80, attack=82, defense=83, special=100, speed=80),
        catch_rate=45,
        base_exp=208,
        learnset={
            1: ["TACKLE", "GROWL", "LEECH SEED", "VINE WHIP"],
            32: ["POISONPOWDER"],
            36: ["RAZOR LEAF"],
            44: ["GROWTH"],
            55: ["SLEEP POWDER"],
            65: ["SOLARBEAM"],
        },
        evolution=None,
    ),
    4: SpeciesData(
        name="CHARMANDER",
        number=4,
        types=[FIRE],
        stats=StatsData(hp=39, attack=52, defense=43, special=50, speed=65),
        catch_rate=45,
        base_exp=65,
        learnset={
            1: ["SCRATCH", "GROWL"],
            9: ["EMBER"],
            15: ["LEER"],
            22: ["RAGE"],
            30: ["SLASH"],
            38: ["FLAMETHROWER"],
            46: ["FIRE SPIN"],
        },
        evolution=LevelEvolution(level=16, into_species="CHARMELEON"),
    ),
    5: SpeciesData(
        name="CHARMELEON",
        number=5,
        types=[FIRE],
        stats=StatsData(hp=58, attack=64, defense=58, special=65, speed=80),
        catch_rate=45,
        base_exp=142,
        learnset={
            1: ["SCRATCH", "GROWL", "EMBER"],
            23: ["LEER"],
            33: ["RAGE"],
            42: ["SLASH"],
            56: ["FLAMETHROWER"],
            62: ["FIRE SPIN"],
        },
        evolution=LevelEvolution(level=36, into_species="CHARIZARD"),
    ),
    6: SpeciesData(
        name="CHARIZARD",
        number=6,
        types=[FIRE, FLYING],
        stats=StatsData(hp=78, attack=84, defense=78, special=85, speed=100),
        catch_rate=45,
        base_exp=209,
        learnset={
            1: ["SCRATCH", "GROWL", "EMBER", "LEER"],
            36: ["RAGE"],
            46: ["SLASH"],
            55: ["FLAMETHROWER"],
            61: ["FIRE SPIN"],
        },
        evolution=None,
    ),
    7: SpeciesData(
        name="SQUIRTLE",
        number=7,
        types=[WATER],
        stats=StatsData(hp=44, attack=48, defense=65, special=50, speed=43),
        catch_rate=45,
        base_exp=66,
        learnset={
            1: ["TACKLE", "TAIL WHIP"],
            8: ["BUBBLE"],
            15: ["WITHDRAW"],
            22: ["WATER GUN"],
            28: ["BITE"],
            35: ["SKULL BASH"],
            42: ["HYDRO PUMP"],
        },
        evolution=LevelEvolution(level=16, into_species="WARTORTLE"),
    ),
    8: SpeciesData(
        name="WARTORTLE",
        number=8,
        types=[WATER],
        stats=StatsData(hp=59, attack=63, defense=80, special=65, speed=58),
        catch_rate=45,
        base_exp=143,
        learnset={
            1: ["TACKLE", "TAIL WHIP", "BUBBLE"],
            24: ["WITHDRAW"],
            31: ["WATER GUN"],
            39: ["BITE"],
            47: ["SKULL BASH"],
            54: ["HYDRO PUMP"],
        },
        evolution=LevelEvolution(level=36, into_species="BLASTOISE"),
    ),
    9: SpeciesData(
        name="BLASTOISE",
        number=9,
        types=[WATER],
        stats=StatsData(hp=79, attack=83, defense=100, special=85, speed=78),
        catch_rate=45,
        base_exp=210,
        learnset={
            1: ["TACKLE", "TAIL WHIP", "BUBBLE", "WITHDRAW"],
            31: ["WATER GUN"],
            39: ["BITE"],
            47: ["SKULL BASH"],
            55: ["HYDRO PUMP"],
        },
        evolution=None,
    ),
    10: SpeciesData(
        name="CATERPIE",
        number=10,
        types=[BUG],
        stats=StatsData(hp=45, attack=30, defense=35, special=20, speed=45),
        catch_rate=255,
        base_exp=53,
        learnset={1: ["TACKLE", "STRING SHOT"]},
        evolution=LevelEvolution(level=7, into_species="METAPOD"),
    ),
    11: SpeciesData(
        name="METAPOD",
        number=11,
        types=[BUG],
        stats=StatsData(hp=50, attack=20, defense=55, special=25, speed=30),
        catch_rate=120,
        base_exp=72,
        learnset={1: ["HARDEN"]},
        evolution=LevelEvolution(level=10, into_species="BUTTERFREE"),
    ),
    12: SpeciesData(
        name="BUTTERFREE",
        number=12,
        types=[BUG, FLYING],
        stats=StatsData(hp=60, attack=45, defense=50, special=80, speed=70),
        catch_rate=45,
        base_exp=160,
        learnset={
            1: ["CONFUSION"],
            12: ["POISONPOWDER"],
            15: ["STUN SPORE"],
            16: ["SLEEP POWDER"],
            21: ["SUPERSONIC"],
            26: ["WHIRLWIND"],
            32: ["PSYBEAM"],
            36: ["SAFEGUARD"],
        },
        evolution=None,
    ),
    13: SpeciesData(
        name="WEEDLE",
        number=13,
        types=[BUG, POISON],
        stats=StatsData(hp=40, attack=35, defense=30, special=20, speed=50),
        catch_rate=255,
        base_exp=52,
        learnset={1: ["POISON STING", "STRING SHOT"]},
        evolution=LevelEvolution(level=7, into_species="KAKUNA"),
    ),
    14: SpeciesData(
        name="KAKUNA",
        number=14,
        types=[BUG, POISON],
        stats=StatsData(hp=45, attack=25, defense=50, special=25, speed=35),
        catch_rate=120,
        base_exp=71,
        learnset={1: ["HARDEN"]},
        evolution=LevelEvolution(level=10, into_species="BEEDRILL"),
    ),
    15: SpeciesData(
        name="BEEDRILL",
        number=15,
        types=[BUG, POISON],
        stats=StatsData(hp=65, attack=80, defense=40, special=45, speed=75),
        catch_rate=45,
        base_exp=159,
        learnset={
            1: ["FURY ATTACK"],
            12: ["FOCUS ENERGY"],
            16: ["TWINEEDLE"],
            20: ["RAGE"],
            25: ["PIN MISSILE"],
            30: ["AGILITY"],
        },
        evolution=None,
    ),
    16: SpeciesData(
        name="PIDGEY",
        number=16,
        types=[NORMAL, FLYING],
        stats=StatsData(hp=40, attack=45, defense=40, special=35, speed=56),
        catch_rate=255,
        base_exp=55,
        learnset={
            1: ["GUST"],
            5: ["SAND ATTACK"],
            12: ["QUICK ATTACK"],
            19: ["WHIRLWIND"],
            28: ["WING ATTACK"],
            36: ["AGILITY"],
            44: ["MIRROR MOVE"],
        },
        evolution=LevelEvolution(level=18, into_species="PIDGEOTTO"),
    ),
    17: SpeciesData(
        name="PIDGEOTTO",
        number=17,
        types=[NORMAL, FLYING],
        stats=StatsData(hp=63, attack=60, defense=55, special=50, speed=71),
        catch_rate=120,
        base_exp=113,
        learnset={
            1: ["GUST", "SAND ATTACK"],
            21: ["QUICK ATTACK"],
            31: ["WHIRLWIND"],
            40: ["WING ATTACK"],
            49: ["AGILITY"],
            58: ["MIRROR MOVE"],
        },
        evolution=LevelEvolution(level=36, into_species="PIDGEOT"),
    ),
    18: SpeciesData(
        name="PIDGEOT",
        number=18,
        types=[NORMAL, FLYING],
        stats=StatsData(hp=83, attack=80, defense=75, special=70, speed=101),
        catch_rate=45,
        base_exp=172,
        learnset={
            1: ["GUST", "SAND ATTACK", "QUICK ATTACK"],
            44: ["WHIRLWIND"],
            54: ["WING ATTACK"],
            62: ["AGILITY"],
            70: ["MIRROR MOVE"],
        },
        evolution=None,
    ),
    19: SpeciesData(
        name="RATTATA",
        number=19,
        types=[NORMAL],
        stats=StatsData(hp=30, attack=56, defense=35, special=25, speed=72),
        catch_rate=255,
        base_exp=57,
        learnset={
            1: ["TACKLE", "TAIL WHIP"],
            7: ["QUICK ATTACK"],
            14: ["HYPER FANG"],
            23: ["FOCUS ENERGY"],
            34: ["SUPER FANG"],
        },
        evolution=LevelEvolution(level=20, into_species="RATICATE"),
    ),
    20: SpeciesData(
        name="RATICATE",
        number=20,
        types=[NORMAL],
        stats=StatsData(hp=55, attack=81, defense=60, special=50, speed=97),
        catch_rate=90,
        base_exp=116,
        learnset={
            1: ["TACKLE", "TAIL WHIP", "QUICK ATTACK"],
            24: ["HYPER FANG"],
            30: ["FOCUS ENERGY"],
            44: ["SUPER FANG"],
        },
        evolution=None,
    ),
    21: SpeciesData(
        name="SPEAROW",
        number=21,
        types=[NORMAL, FLYING],
        stats=StatsData(hp=40, attack=60, defense=30, special=31, speed=70),
        catch_rate=255,
        base_exp=58,
        learnset={
            1: ["PECK", "GROWL"],
            9: ["LEER"],
            15: ["FURY ATTACK"],
            22: ["MIRROR MOVE"],
            29: ["DRILL PECK"],
            36: ["AGILITY"],
        },
        evolution=LevelEvolution(level=20, into_species="FEAROW"),
    ),
    22: SpeciesData(
        name="FEAROW",
        number=22,
        types=[NORMAL, FLYING],
        stats=StatsData(hp=65, attack=90, defense=65, special=61, speed=100),
        catch_rate=90,
        base_exp=162,
        learnset={
            1: ["PECK", "GROWL", "LEER"],
            25: ["FURY ATTACK"],
            31: ["MIRROR MOVE"],
            39: ["DRILL PECK"],
            47: ["AGILITY"],
        },
        evolution=None,
    ),
    # Ekans line — Nugget Bridge trainers
    23: SpeciesData(
        name="EKANS",
        number=23,
        types=[POISON],
        stats=StatsData(hp=35, attack=60, defense=44, special=40, speed=55),
        catch_rate=255,
        base_exp=62,
        learnset={
            1: ["WRAP", "LEER"],
            10: ["POISON STING"],
            17: ["BITE"],
            24: ["GLARE"],
            31: ["SCREECH"],
            38: ["SLUDGE"],
        },
        evolution=LevelEvolution(level=22, into_species="ARBOK"),
    ),
    24: SpeciesData(
        name="ARBOK",
        number=24,
        types=[POISON],
        stats=StatsData(hp=60, attack=85, defense=69, special=65, speed=80),
        catch_rate=90,
        base_exp=147,
        learnset={
            1: ["WRAP", "LEER", "POISON STING"],
            27: ["BITE"],
            36: ["GLARE"],
            47: ["SCREECH"],
            58: ["SLUDGE"],
        },
        evolution=None,
    ),
    25: SpeciesData(
        name="PIKACHU",
        number=25,
        types=[ELECTRIC],
        stats=StatsData(hp=35, attack=55, defense=30, special=50, speed=90),
        catch_rate=190,
        base_exp=82,
        learnset={
            1: ["THUNDERSHOCK", "GROWL"],
            9: ["THUNDER WAVE"],
            16: ["QUICK ATTACK"],
            26: ["SWIFT"],
            33: ["AGILITY"],
            43: ["THUNDER"],
        },
        evolution=ItemEvolution(item="THUNDER STONE", into_species="RAICHU"),
    ),
    # Sandshrew line — Pewter Gym
    27: SpeciesData(
        name="SANDSHREW",
        number=27,
        types=[GROUND],
        stats=StatsData(hp=50, attack=75, defense=85, special=30, speed=40),
        catch_rate=255,
        base_exp=93,
        learnset={
            1: ["SCRATCH"],
            10: ["SAND ATTACK"],
            17: ["SLASH"],
            24: ["POISON STING"],
            31: ["SWIFT"],
            38: ["FURY SWIPES"],
        },
        evolution=LevelEvolution(level=22, into_species="SANDSLASH"),
    ),
    28: SpeciesData(
        name="SANDSLASH",
        number=28,
        types=[GROUND],
        stats=StatsData(hp=75, attack=100, defense=110, special=55, speed=65),
        catch_rate=90,
        base_exp=163,
        learnset={
            1: ["SCRATCH", "SAND ATTACK"],
            27: ["SLASH"],
            36: ["POISON STING"],
            47: ["SWIFT"],
            58: ["FURY SWIPES"],
        },
        evolution=None,
    ),
    # Clefairy line — Mt. Moon
    35: SpeciesData(
        name="CLEFAIRY",
        number=35,
        types=[NORMAL],
        stats=StatsData(hp=70, attack=45, defense=48, special=60, speed=35),
        catch_rate=150,
        base_exp=68,
        learnset={
            1: ["POUND", "GROWL"],
            13: ["SING"],
            18: ["DOUBLE SLAP"],
            24: ["MINIMIZE"],
            31: ["METRONOME"],
            39: ["DEFENSE CURL"],
            48: ["LIGHT SCREEN"],
        },
        evolution=ItemEvolution(item="MOON STONE", into_species="CLEFABLE"),
    ),
    36: SpeciesData(
        name="CLEFABLE",
        number=36,
        types=[NORMAL],
        stats=StatsData(hp=95, attack=70, defense=73, special=85, speed=60),
        catch_rate=25,
        base_exp=129,
        learnset={
            1: ["SING", "DOUBLE SLAP", "MINIMIZE", "METRONOME"],
        },
        evolution=None,
    ),
    # Jigglypuff line — Route 3, Route 4
    39: SpeciesData(
        name="JIGGLYPUFF",
        number=39,
        types=[NORMAL],
        stats=StatsData(hp=115, attack=45, defense=20, special=25, speed=20),
        catch_rate=170,
        base_exp=76,
        learnset={
            1: ["SING"],
            9: ["POUND"],
            14: ["DISABLE"],
            19: ["DEFENSE CURL"],
            24: ["DOUBLE SLAP"],
            29: ["REST"],
            34: ["BODY SLAM"],
            39: ["DOUBLE-EDGE"],
        },
        evolution=ItemEvolution(item="MOON STONE", into_species="WIGGLYTUFF"),
    ),
    40: SpeciesData(
        name="WIGGLYTUFF",
        number=40,
        types=[NORMAL],
        stats=StatsData(hp=140, attack=70, defense=45, special=50, speed=45),
        catch_rate=50,
        base_exp=109,
        learnset={
            1: ["SING", "DISABLE", "DEFENSE CURL", "DOUBLE SLAP"],
        },
        evolution=None,
    ),
    # Zubat line — Mt. Moon, Route 22
    41: SpeciesData(
        name="ZUBAT",
        number=41,
        types=[POISON, FLYING],
        stats=StatsData(hp=40, attack=45, defense=35, special=40, speed=55),
        catch_rate=255,
        base_exp=54,
        learnset={
            1: ["LEECH LIFE"],
            10: ["SUPERSONIC"],
            15: ["BITE"],
            21: ["CONFUSE RAY"],
            28: ["WING ATTACK"],
        },
        evolution=LevelEvolution(level=22, into_species="GOLBAT"),
    ),
    42: SpeciesData(
        name="GOLBAT",
        number=42,
        types=[POISON, FLYING],
        stats=StatsData(hp=75, attack=80, defense=70, special=75, speed=90),
        catch_rate=90,
        base_exp=171,
        learnset={
            1: ["LEECH LIFE", "SUPERSONIC"],
            21: ["BITE"],
            28: ["CONFUSE RAY"],
            36: ["WING ATTACK"],
        },
        evolution=None,
    ),
    # Oddish line — Route 24
    43: SpeciesData(
        name="ODDISH",
        number=43,
        types=[GRASS, POISON],
        stats=StatsData(hp=45, attack=50, defense=55, special=75, speed=30),
        catch_rate=255,
        base_exp=78,
        learnset={
            1: ["ABSORB"],
            15: ["POISONPOWDER"],
            17: ["STUN SPORE"],
            19: ["SLEEP POWDER"],
            24: ["SLUDGE"],
            33: ["MEGA DRAIN"],
            46: ["SOLARBEAM"],
        },
        evolution=LevelEvolution(level=21, into_species="GLOOM"),
    ),
    44: SpeciesData(
        name="GLOOM",
        number=44,
        types=[GRASS, POISON],
        stats=StatsData(hp=60, attack=65, defense=70, special=85, speed=40),
        catch_rate=120,
        base_exp=132,
        learnset={
            1: ["ABSORB", "POISONPOWDER"],
            28: ["STUN SPORE"],
            33: ["SLEEP POWDER"],
            38: ["SLUDGE"],
            52: ["MEGA DRAIN"],
        },
        evolution=ItemEvolution(item="LEAF STONE", into_species="VILEPLUME"),
    ),
    45: SpeciesData(
        name="VILEPLUME",
        number=45,
        types=[GRASS, POISON],
        stats=StatsData(hp=75, attack=80, defense=85, special=100, speed=50),
        catch_rate=45,
        base_exp=184,
        learnset={
            1: ["STUN SPORE", "SLEEP POWDER", "SLUDGE"],
        },
        evolution=None,
    ),
    # Meowth line — Route 3
    52: SpeciesData(
        name="MEOWTH",
        number=52,
        types=[NORMAL],
        stats=StatsData(hp=40, attack=45, defense=35, special=40, speed=90),
        catch_rate=255,
        base_exp=69,
        learnset={
            1: ["SCRATCH", "GROWL"],
            12: ["BITE"],
            17: ["PAY DAY"],
            24: ["SCREECH"],
            33: ["FURY SWIPES"],
            44: ["SLASH"],
        },
        evolution=LevelEvolution(level=28, into_species="PERSIAN"),
    ),
    53: SpeciesData(
        name="PERSIAN",
        number=53,
        types=[NORMAL],
        stats=StatsData(hp=65, attack=70, defense=60, special=65, speed=115),
        catch_rate=90,
        base_exp=148,
        learnset={
            1: ["SCRATCH", "GROWL", "BITE"],
            29: ["PAY DAY"],
            38: ["SCREECH"],
            51: ["FURY SWIPES"],
            64: ["SLASH"],
        },
        evolution=None,
    ),
    # Abra line — Route 24
    63: SpeciesData(
        name="ABRA",
        number=63,
        types=[PSYCHIC],
        stats=StatsData(hp=25, attack=20, defense=15, special=105, speed=90),
        catch_rate=200,
        base_exp=73,
        learnset={
            1: ["TELEPORT"],
        },
        evolution=LevelEvolution(level=16, into_species="KADABRA"),
    ),
    64: SpeciesData(
        name="KADABRA",
        number=64,
        types=[PSYCHIC],
        stats=StatsData(hp=40, attack=35, defense=30, special=120, speed=105),
        catch_rate=100,
        base_exp=145,
        learnset={
            1: ["TELEPORT", "CONFUSION"],
            16: ["CONFUSION"],
            20: ["DISABLE"],
            27: ["PSYBEAM"],
            31: ["RECOVER"],
            38: ["PSYCHIC"],
            42: ["REFLECT"],
        },
        evolution=LevelEvolution(level=38, into_species="ALAKAZAM"),
    ),
    65: SpeciesData(
        name="ALAKAZAM",
        number=65,
        types=[PSYCHIC],
        stats=StatsData(hp=55, attack=50, defense=45, special=135, speed=120),
        catch_rate=50,
        base_exp=186,
        learnset={
            1: ["TELEPORT", "CONFUSION", "DISABLE"],
            27: ["PSYBEAM"],
            31: ["RECOVER"],
            38: ["PSYCHIC"],
            42: ["REFLECT"],
        },
        evolution=None,
    ),
    # Bellsprout line — Route 24
    69: SpeciesData(
        name="BELLSPROUT",
        number=69,
        types=[GRASS, POISON],
        stats=StatsData(hp=50, attack=75, defense=35, special=70, speed=40),
        catch_rate=255,
        base_exp=84,
        learnset={
            1: ["VINE WHIP", "GROWTH"],
            13: ["WRAP"],
            15: ["POISONPOWDER"],
            18: ["SLEEP POWDER"],
            21: ["STUN SPORE"],
            26: ["SLUDGE"],
            33: ["RAZOR LEAF"],
            42: ["SLAM"],
        },
        evolution=LevelEvolution(level=21, into_species="WEEPINBELL"),
    ),
    70: SpeciesData(
        name="WEEPINBELL",
        number=70,
        types=[GRASS, POISON],
        stats=StatsData(hp=65, attack=90, defense=50, special=85, speed=55),
        catch_rate=120,
        base_exp=151,
        learnset={
            1: ["VINE WHIP", "GROWTH", "WRAP"],
            23: ["POISONPOWDER"],
            29: ["SLEEP POWDER"],
            38: ["STUN SPORE"],
            49: ["SLUDGE"],
            54: ["RAZOR LEAF"],
        },
        evolution=ItemEvolution(item="LEAF STONE", into_species="VICTREEBEL"),
    ),
    71: SpeciesData(
        name="VICTREEBEL",
        number=71,
        types=[GRASS, POISON],
        stats=StatsData(hp=80, attack=105, defense=65, special=100, speed=70),
        catch_rate=45,
        base_exp=191,
        learnset={
            1: ["SLEEP POWDER", "STUN SPORE", "SLUDGE", "RAZOR LEAF"],
        },
        evolution=None,
    ),
    # Geodude family — Brock's team
    74: SpeciesData(
        name="GEODUDE",
        number=74,
        types=[ROCK, GROUND],
        stats=StatsData(hp=40, attack=80, defense=100, special=30, speed=20),
        catch_rate=255,
        base_exp=86,
        learnset={
            1: ["TACKLE"],
            11: ["DEFENSE CURL"],
            16: ["ROCK THROW"],
            21: ["SELFDESTRUCT"],
            26: ["HARDEN"],
            31: ["EARTHQUAKE"],
            36: ["EXPLOSION"],
        },
        evolution=LevelEvolution(level=25, into_species="GRAVELER"),
    ),
    75: SpeciesData(
        name="GRAVELER",
        number=75,
        types=[ROCK, GROUND],
        stats=StatsData(hp=55, attack=95, defense=115, special=45, speed=35),
        catch_rate=120,
        base_exp=134,
        learnset={
            1: ["TACKLE", "DEFENSE CURL"],
            16: ["ROCK THROW"],
            21: ["SELFDESTRUCT"],
            29: ["HARDEN"],
            36: ["EARTHQUAKE"],
            43: ["EXPLOSION"],
        },
        evolution=LevelEvolution(level=36, into_species="GOLEM"),
    ),
    76: SpeciesData(
        name="GOLEM",
        number=76,
        types=[ROCK, GROUND],
        stats=StatsData(hp=80, attack=110, defense=130, special=55, speed=45),
        catch_rate=45,
        base_exp=177,
        learnset={
            1: ["TACKLE", "DEFENSE CURL", "ROCK THROW"],
            29: ["SELFDESTRUCT"],
            36: ["HARDEN"],
            43: ["EARTHQUAKE"],
            50: ["EXPLOSION"],
        },
        evolution=None,
    ),
    # Onix — Brock's ace
    95: SpeciesData(
        name="ONIX",
        number=95,
        types=[ROCK, GROUND],
        stats=StatsData(hp=35, attack=45, defense=160, special=30, speed=70),
        catch_rate=45,
        base_exp=108,
        learnset={
            1: ["TACKLE", "SCREECH"],
            15: ["BIND"],
            19: ["ROCK THROW"],
            25: ["RAGE"],
            33: ["SLAM"],
            43: ["HARDEN"],
        },
        evolution=None,
    ),
    # Horsea line — Cerulean Gym
    116: SpeciesData(
        name="HORSEA",
        number=116,
        types=[WATER],
        stats=StatsData(hp=30, attack=40, defense=70, special=70, speed=60),
        catch_rate=225,
        base_exp=83,
        learnset={
            1: ["BUBBLE"],
            19: ["SMOKESCREEN"],
            24: ["LEER"],
            30: ["WATER GUN"],
            37: ["AGILITY"],
            45: ["HYDRO PUMP"],
        },
        evolution=LevelEvolution(level=32, into_species="SEADRA"),
    ),
    117: SpeciesData(
        name="SEADRA",
        number=117,
        types=[WATER],
        stats=StatsData(hp=55, attack=65, defense=95, special=95, speed=85),
        catch_rate=75,
        base_exp=155,
        learnset={
            1: ["BUBBLE", "SMOKESCREEN"],
            32: ["LEER"],
            40: ["WATER GUN"],
            48: ["AGILITY"],
            55: ["HYDRO PUMP"],
        },
        evolution=None,
    ),
    # Goldeen line — Cerulean Gym
    118: SpeciesData(
        name="GOLDEEN",
        number=118,
        types=[WATER],
        stats=StatsData(hp=45, attack=67, defense=60, special=50, speed=63),
        catch_rate=225,
        base_exp=111,
        learnset={
            1: ["PECK", "TAIL WHIP"],
            19: ["SUPERSONIC"],
            24: ["HORN ATTACK"],
            30: ["FURY ATTACK"],
            37: ["WATERFALL"],
            45: ["HORN DRILL"],
            54: ["AGILITY"],
        },
        evolution=LevelEvolution(level=33, into_species="SEAKING"),
    ),
    119: SpeciesData(
        name="SEAKING",
        number=119,
        types=[WATER],
        stats=StatsData(hp=80, attack=92, defense=65, special=80, speed=68),
        catch_rate=60,
        base_exp=170,
        learnset={
            1: ["PECK", "TAIL WHIP", "SUPERSONIC"],
            33: ["HORN ATTACK"],
            41: ["FURY ATTACK"],
            49: ["WATERFALL"],
            54: ["HORN DRILL"],
            61: ["AGILITY"],
        },
        evolution=None,
    ),
    # Staryu line — Misty's team
    120: SpeciesData(
        name="STARYU",
        number=120,
        types=[WATER],
        stats=StatsData(hp=30, attack=45, defense=55, special=70, speed=85),
        catch_rate=225,
        base_exp=106,
        learnset={
            1: ["TACKLE"],
            17: ["WATER GUN"],
            22: ["HARDEN"],
            27: ["RECOVER"],
            32: ["SWIFT"],
            37: ["MINIMIZE"],
            42: ["LIGHT SCREEN"],
            47: ["HYDRO PUMP"],
        },
        evolution=ItemEvolution(item="WATER STONE", into_species="STARMIE"),
    ),
    121: SpeciesData(
        name="STARMIE",
        number=121,
        types=[WATER, PSYCHIC],
        stats=StatsData(hp=60, attack=75, defense=85, special=100, speed=115),
        catch_rate=60,
        base_exp=207,
        learnset={
            1: ["TACKLE", "WATER GUN", "HARDEN", "RECOVER"],
        },
        evolution=None,
    ),
    29: SpeciesData(
        name="NIDORAN♀",
        number=29,
        types=[POISON],
        stats=StatsData(hp=55, attack=47, defense=52, special=40, speed=41),
        catch_rate=235,
        base_exp=59,
        learnset={
            1: ["GROWL", "TACKLE"],
            8: ["POISON STING"],
            14: ["FURY ATTACK"],
            23: ["BITE"],
            32: ["DOUBLE KICK"],
            41: ["SCREECH"],
            50: ["HORN ATTACK"],
        },
        evolution=LevelEvolution(level=16, into_species="NIDORINA"),
    ),
    30: SpeciesData(
        name="NIDORINA",
        number=30,
        types=[POISON],
        stats=StatsData(hp=70, attack=62, defense=67, special=55, speed=56),
        catch_rate=120,
        base_exp=117,
        learnset={
            1: ["GROWL", "TACKLE", "POISON STING"],
            23: ["BITE"],
            32: ["DOUBLE KICK"],
            38: ["LEER"],
            50: ["HORN ATTACK"],
        },
        evolution=ItemEvolution(item="MOON STONE", into_species="NIDOQUEEN"),
    ),
    31: SpeciesData(
        name="NIDOQUEEN",
        number=31,
        types=[POISON, GROUND],
        stats=StatsData(hp=90, attack=82, defense=87, special=75, speed=76),
        catch_rate=45,
        base_exp=194,
        learnset={
            1: ["TACKLE", "SCRATCH", "BODY SLAM", "DOUBLE KICK", "STOMP", "HORN ATTACK"],
        },
        evolution=None,
    ),
    32: SpeciesData(
        name="NIDORAN♂",
        number=32,
        types=[POISON],
        stats=StatsData(hp=46, attack=57, defense=40, special=40, speed=50),
        catch_rate=235,
        base_exp=60,
        learnset={
            1: ["GROWL", "TACKLE"],
            8: ["POISON STING"],
            14: ["FURY ATTACK"],
            23: ["BITE"],
            32: ["DOUBLE KICK"],
            41: ["SCREECH"],
            50: ["HORN ATTACK"],
        },
        evolution=LevelEvolution(level=16, into_species="NIDORINO"),
    ),
    33: SpeciesData(
        name="NIDORINO",
        number=33,
        types=[POISON],
        stats=StatsData(hp=61, attack=72, defense=57, special=55, speed=65),
        catch_rate=120,
        base_exp=118,
        learnset={
            1: ["GROWL", "TACKLE", "POISON STING"],
            23: ["BITE"],
            32: ["DOUBLE KICK"],
            38: ["LEER"],
            50: ["HORN ATTACK"],
        },
        evolution=ItemEvolution(item="MOON STONE", into_species="NIDOKING"),
    ),
    34: SpeciesData(
        name="NIDOKING",
        number=34,
        types=[POISON, GROUND],
        stats=StatsData(hp=81, attack=92, defense=77, special=75, speed=85),
        catch_rate=45,
        base_exp=195,
        learnset={
            1: ["TACKLE", "SCRATCH", "BODY SLAM", "DOUBLE KICK", "STOMP", "HORN ATTACK"],
        },
        evolution=None,
    ),
    56: SpeciesData(
        name="MANKEY",
        number=56,
        types=[FIGHTING],
        stats=StatsData(hp=40, attack=80, defense=35, special=35, speed=70),
        catch_rate=190,
        base_exp=74,
        learnset={
            1: ["SCRATCH", "LEER"],
            9: ["KARATE CHOP"],
            15: ["FOCUS ENERGY"],
            21: ["SEISMIC TOSS"],
            27: ["RAGE"],
            33: ["SCREECH"],
            39: ["SUBMISSION"],
            45: ["LOW KICK"],
        },
        evolution=LevelEvolution(level=28, into_species="PRIMEAPE"),
    ),
    57: SpeciesData(
        name="PRIMEAPE",
        number=57,
        types=[FIGHTING],
        stats=StatsData(hp=65, attack=105, defense=60, special=60, speed=95),
        catch_rate=75,
        base_exp=149,
        learnset={
            1: ["SCRATCH", "LEER", "KARATE CHOP", "FOCUS ENERGY"],
            33: ["SCREECH"],
            39: ["SUBMISSION"],
            45: ["LOW KICK"],
        },
        evolution=None,
    ),
    58: SpeciesData(
        name="GROWLITHE",
        number=58,
        types=[FIRE],
        stats=StatsData(hp=55, attack=70, defense=45, special=50, speed=60),
        catch_rate=190,
        base_exp=91,
        learnset={
            1: ["BITE", "ROAR"],
            18: ["EMBER"],
            23: ["LEER"],
            30: ["TAKE DOWN"],
            42: ["FLAMETHROWER"],
            50: ["FIRE SPIN"],
        },
        evolution=ItemEvolution(item="FIRE STONE", into_species="ARCANINE"),
    ),
    59: SpeciesData(
        name="ARCANINE",
        number=59,
        types=[FIRE],
        stats=StatsData(hp=90, attack=110, defense=80, special=80, speed=95),
        catch_rate=75,
        base_exp=213,
        learnset={
            1: ["BITE", "ROAR", "EMBER", "LEER", "TAKE DOWN", "FLAMETHROWER", "FIRE SPIN"],
        },
        evolution=None,
    ),
    72: SpeciesData(
        name="TENTACOOL",
        number=72,
        types=[WATER, POISON],
        stats=StatsData(hp=40, attack=40, defense=35, special=100, speed=70),
        catch_rate=190,
        base_exp=105,
        learnset={
            1: ["POISON STING", "GROWL"],
            7: ["SUPERSONIC"],
            13: ["WRAP"],
            18: ["WATER GUN"],
            27: ["SLUDGE"],
            33: ["HYDRO PUMP"],
        },
        evolution=LevelEvolution(level=30, into_species="TENTACRUEL"),
    ),
    73: SpeciesData(
        name="TENTACRUEL",
        number=73,
        types=[WATER, POISON],
        stats=StatsData(hp=80, attack=70, defense=65, special=120, speed=100),
        catch_rate=60,
        base_exp=205,
        learnset={
            1: ["POISON STING", "GROWL", "SUPERSONIC", "WRAP", "WATER GUN", "SLUDGE"],
            35: ["HYDRO PUMP"],
        },
        evolution=None,
    ),
    100: SpeciesData(
        name="VOLTORB",
        number=100,
        types=[ELECTRIC],
        stats=StatsData(hp=40, attack=30, defense=50, special=55, speed=100),
        catch_rate=190,
        base_exp=103,
        learnset={
            1: ["TACKLE", "SCREECH"],
            17: ["SONIC BOOM"],
            22: ["SELFDESTRUCT"],
            29: ["THUNDER WAVE"],
            36: ["THUNDERBOLT"],
        },
        evolution=LevelEvolution(level=30, into_species="ELECTRODE"),
    ),
    101: SpeciesData(
        name="ELECTRODE",
        number=101,
        types=[ELECTRIC],
        stats=StatsData(hp=60, attack=50, defense=70, special=80, speed=140),
        catch_rate=60,
        base_exp=150,
        learnset={
            1: ["TACKLE", "SCREECH", "SONIC BOOM", "SELFDESTRUCT", "THUNDER WAVE"],
            40: ["THUNDERBOLT"],
        },
        evolution=None,
    ),
    109: SpeciesData(
        name="KOFFING",
        number=109,
        types=[POISON],
        stats=StatsData(hp=40, attack=65, defense=95, special=60, speed=35),
        catch_rate=190,
        base_exp=114,
        learnset={
            1: ["TACKLE", "SMOKESCREEN"],
            9: ["SLUDGE"],
            14: ["POISON GAS"],
            25: ["SELFDESTRUCT"],
            33: ["TOXIC"],
        },
        evolution=LevelEvolution(level=35, into_species="WEEZING"),
    ),
    110: SpeciesData(
        name="WEEZING",
        number=110,
        types=[POISON],
        stats=StatsData(hp=65, attack=90, defense=120, special=85, speed=60),
        catch_rate=60,
        base_exp=173,
        learnset={
            1: ["TACKLE", "SMOKESCREEN", "SLUDGE", "POISON GAS"],
            35: ["SELFDESTRUCT"],
            42: ["TOXIC"],
        },
        evolution=None,
    ),
    129: SpeciesData(
        name="MAGIKARP",
        number=129,
        types=[WATER],
        stats=StatsData(hp=20, attack=10, defense=55, special=15, speed=80),
        catch_rate=255,
        base_exp=20,
        learnset={
            1: ["TACKLE"],
        },
        evolution=LevelEvolution(level=20, into_species="GYARADOS"),
    ),
    130: SpeciesData(
        name="GYARADOS",
        number=130,
        types=[WATER, FLYING],
        stats=StatsData(hp=95, attack=125, defense=79, special=100, speed=81),
        catch_rate=45,
        base_exp=214,
        learnset={
            1: ["BITE", "HYDRO PUMP"],
            32: ["DRAGON RAGE"],
            41: ["HYPER BEAM"],
        },
        evolution=None,
    ),
}

# Populate any missing national dex entries with placeholder stubs so
# code that iterates 1-151 doesn't explode.  Full data omitted for brevity
# (this is a joke library after all).
_STUB_NAMES = {
    26: "RAICHU",
    37: "VULPIX",
    38: "NINETALES",
    46: "PARAS",
    47: "PARASECT",
    48: "VENONAT",
    49: "VENOMOTH",
    50: "DIGLETT",
    51: "DUGTRIO",
    54: "PSYDUCK",
    55: "GOLDUCK",
    60: "POLIWAG",
    61: "POLIWHIRL",
    62: "POLIWRATH",
    66: "MACHOP",
    67: "MACHOKE",
    68: "MACHAMP",
    77: "PONYTA",
    78: "RAPIDASH",
    79: "SLOWPOKE",
    80: "SLOWBRO",
    81: "MAGNEMITE",
    82: "MAGNETON",
    83: "FARFETCH'D",
    84: "DODUO",
    85: "DODRIO",
    86: "SEEL",
    87: "DEWGONG",
    88: "GRIMER",
    89: "MUK",
    90: "SHELLDER",
    91: "CLOYSTER",
    92: "GASTLY",
    93: "HAUNTER",
    94: "GENGAR",
    96: "DROWZEE",
    97: "HYPNO",
    98: "KRABBY",
    99: "KINGLER",
    102: "EXEGGCUTE",
    103: "EXEGGUTOR",
    104: "CUBONE",
    105: "MAROWAK",
    106: "HITMONLEE",
    107: "HITMONCHAN",
    108: "LICKITUNG",
    111: "RHYHORN",
    112: "RHYDON",
    113: "CHANSEY",
    114: "TANGELA",
    115: "KANGASKHAN",
    122: "MR. MIME",
    123: "SCYTHER",
    124: "JYNX",
    125: "ELECTABUZZ",
    126: "MAGMAR",
    127: "PINSIR",
    128: "TAUROS",
    131: "LAPRAS",
    132: "DITTO",
    133: "EEVEE",
    134: "VAPOREON",
    135: "JOLTEON",
    136: "FLAREON",
    137: "PORYGON",
    138: "OMANYTE",
    139: "OMASTAR",
    140: "KABUTO",
    141: "KABUTOPS",
    142: "AERODACTYL",
    143: "SNORLAX",
    144: "ARTICUNO",
    145: "ZAPDOS",
    146: "MOLTRES",
    147: "DRATINI",
    148: "DRAGONAIR",
    149: "DRAGONITE",
    150: "MEWTWO",
    151: "MEW",
}

for _num, _name in _STUB_NAMES.items():
    if _num not in POKEMON:
        POKEMON[_num] = SpeciesData(
            name=_name,
            number=_num,
            types=[NORMAL],
            stats=StatsData(hp=50, attack=50, defense=50, special=50, speed=50),
            catch_rate=45,
            base_exp=100,
            learnset={1: ["TACKLE"]},
            evolution=None,
        )

# Patch item-based evolution fields.
# Eevee gets a list so all three branches are discoverable.
_ITEM_EVOLUTIONS = {
    35: ItemEvolution(item="MOON STONE", into_species="CLEFABLE"),
    37: ItemEvolution(item="FIRE STONE", into_species="NINETALES"),
    39: ItemEvolution(item="MOON STONE", into_species="WIGGLYTUFF"),
    44: ItemEvolution(item="LEAF STONE", into_species="VILEPLUME"),
    61: ItemEvolution(item="WATER STONE", into_species="POLIWRATH"),
    70: ItemEvolution(item="LEAF STONE", into_species="VICTREEBEL"),
    90: ItemEvolution(item="WATER STONE", into_species="CLOYSTER"),
    102: ItemEvolution(item="LEAF STONE", into_species="EXEGGUTOR"),
    120: ItemEvolution(item="WATER STONE", into_species="STARMIE"),
    133: [
        ItemEvolution(item="WATER STONE", into_species="VAPOREON"),
        ItemEvolution(item="THUNDER STONE", into_species="JOLTEON"),
        ItemEvolution(item="FIRE STONE", into_species="FLAREON"),
    ],
}
for _num, _evo in _ITEM_EVOLUTIONS.items():
    if _num in POKEMON:
        POKEMON[_num].evolution = _evo


def get_pokemon(name_or_number: str | int) -> Optional[SpeciesData]:
    """Look up a Pokémon by name (str) or dex number (int)."""
    if isinstance(name_or_number, int):
        return POKEMON.get(name_or_number)
    target = name_or_number.upper()
    for p in POKEMON.values():
        if p.name == target:
            return p
    return None
