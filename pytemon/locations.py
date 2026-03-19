"""
Location data for the Pokemon game.

This module contains all location information including towns, routes,
connections, buildings, and restrictions.
"""

from typing import Any, Dict, List, Optional

# Location type constants
TYPE_TOWN = "town"
TYPE_ROUTE = "route"
TYPE_FOREST = "forest"
TYPE_DUNGEON = "dungeon"


class Location:
    """Represents a location in the game."""

    def __init__(
        self,
        name: str,
        location_type: str,
        description: str,
        exits: Dict[str, Dict[str, Any]],
        buildings: Optional[List[str]] = None,
        blocked_buildings: Optional[Dict[str, str]] = None,
        wild_pokemon: Optional[List[str]] = None,
        wild_level_range: tuple = (2, 6),
        trainers: int = 0,
        trainer_encounter_rate: float = 0.30,
        wild_encounter_rate: float = 0.45,
    ):
        """
        Initialize a location.

        Args:
            name: Name of the location
            location_type: Type (town, route, forest)
            description: Description of the location
            exits: Dictionary of exit connections
            buildings: List of available buildings
            blocked_buildings: Dictionary of blocked buildings and reasons
            wild_pokemon: List of wild Pokemon species names that can be found here
            wild_level_range: Tuple of (min_level, max_level) for wild Pokemon
            trainers: Number of trainers in this location
            trainer_encounter_rate: Probability (0-1) of triggering a trainer battle
                when undefeated trainers are present (default 0.30)
            wild_encounter_rate: Probability (0-1) of triggering a wild encounter
                when no trainer battle triggers (default 0.45)
        """
        self.name = name
        self.type = location_type
        self.description = description
        self.exits = exits or {}
        self.buildings = buildings or []
        self.blocked_buildings = blocked_buildings or {}
        self.wild_pokemon = wild_pokemon or []
        self.wild_level_range = wild_level_range
        self.trainers = trainers
        self.trainer_encounter_rate = trainer_encounter_rate
        self.wild_encounter_rate = wild_encounter_rate

    def get_available_exits(self) -> List[str]:
        """Get list of accessible exits."""
        return [
            exit_name
            for exit_name, exit_data in self.exits.items()
            if not exit_data.get("blocked", False)
        ]

    def get_blocked_exits(self) -> Dict[str, str]:
        """Get dictionary of blocked exits and reasons."""
        return {
            exit_name: exit_data.get("reason", "Blocked")
            for exit_name, exit_data in self.exits.items()
            if exit_data.get("blocked", False)
        }

    def can_explore(self) -> bool:
        """Check if this location can be explored (routes/forests/dungeons)."""
        return self.type in [TYPE_ROUTE, TYPE_FOREST, TYPE_DUNGEON]

    def get_exit_min_explores(self, exit_name: str) -> int:
        """
        Return the minimum number of explores required before the given exit
        becomes passable.  Returns 0 for towns and for exits that have no
        traversal requirement.

        Args:
            exit_name: Name of the exit / destination.

        Returns:
            int: Required explore count (0 = unrestricted).
        """
        return self.exits.get(exit_name, {}).get("min_explores", 0)


# Define all locations
LOCATIONS: Dict[str, Location] = {
    "Pallet Town": Location(
        name="Pallet Town",
        location_type=TYPE_TOWN,
        description="A tranquil seaside hamlet of two houses and a lab — the birthplace of legends, if the Professor has anything to say about it.",
        exits={
            "Route 1": {"direction": "north", "blocked": False},
            "Route 21": {
                "direction": "south",
                "blocked": True,
                "reason": "You need HM Surf to cross the water — teach Surf to a Pokemon and use it here",
            },
        },
        buildings=["Player's House", "Rival's House", "Professor Oak's Lab"],
    ),
    "Route 1": Location(
        name="Route 1",
        location_type=TYPE_ROUTE,
        description="A well-worn dirt path through tall grasses — the first taste of the wild, where Pidgey and Rattata have ruled over nervous new trainers since time immemorial.",
        exits={
            "Pallet Town": {
                "direction": "south",
                "blocked": False,
                "min_explores": 5,
            },
            "Viridian City": {
                "direction": "north",
                "blocked": False,
                "min_explores": 5,
            },
        },
        wild_pokemon=["PIDGEY", "RATTATA"],
        wild_level_range=(2, 5),
    ),
    "Viridian City": Location(
        name="Viridian City",
        location_type=TYPE_TOWN,
        description="The last major stop before the wilderness of Viridian Forest. Its Gym is said to be locked — the mysterious Leader never seems to be in.",
        exits={
            "Route 1": {"direction": "south", "blocked": False},
            "Route 2 South": {"direction": "north", "blocked": False},
            "Route 22": {"direction": "west", "blocked": False},
        },
        buildings=["Pokemon Center", "Pokemart", "Gym"],
    ),
    "Route 22": Location(
        name="Route 22",
        location_type=TYPE_ROUTE,
        description="A short but tense westward road haunted by your Rival, who always seems to find you here. The distant silhouette of the Pokemon League gate looms at the end.",
        exits={
            "Viridian City": {
                "direction": "east",
                "blocked": False,
                "min_explores": 6,
            },
            "Victory Road": {
                "direction": "west",
                "blocked": False,
                "min_explores": 6,
            },
        },
        wild_pokemon=["PIDGEY", "RATTATA", "SPEAROW"],
        wild_level_range=(4, 7),
        trainers=1,  # Rival battle
    ),
    "Route 2 South": Location(
        name="Route 2 South",
        location_type=TYPE_ROUTE,
        description="The quieter half of Route 2, sandwiched between Viridian City's safety and the dark tree-line of Viridian Forest. The rustling gets louder as you head north.",
        exits={
            "Viridian City": {
                "direction": "south",
                "blocked": False,
                "min_explores": 4,
            },
            "Viridian Forest": {
                "direction": "north",
                "blocked": False,
                "min_explores": 4,
            },
        },
        wild_pokemon=["PIDGEY", "RATTATA"],
        wild_level_range=(3, 5),
    ),
    "Route 2 North": Location(
        name="Route 2 North",
        location_type=TYPE_ROUTE,
        description="You've made it through the forest — but the route north of Viridian Forest is no picnic either. Pewter City's rocky skyline is just visible through the trees, and a dark cave entrance beckons to the east.",
        exits={
            "Viridian Forest": {
                "direction": "south",
                "blocked": False,
                "min_explores": 4,
            },
            "Pewter City": {
                "direction": "north",
                "blocked": False,
                "min_explores": 4,
            },
            "Diglett's Cave": {
                "direction": "east",
                "blocked": False,
            },
        },
        wild_pokemon=["PIDGEY", "RATTATA", "SPEAROW"],
        wild_level_range=(5, 7),
    ),
    "Viridian Forest": Location(
        name="Viridian Forest",
        location_type=TYPE_FOREST,
        description="An ancient, labyrinthine woodland that splits Route 2 in two. Bug Catchers lurk behind every other tree, and Pikachu has been spotted darting between the roots.",
        exits={
            "Route 2 South": {
                "direction": "south",
                "blocked": False,
                "min_explores": 7,
            },
            "Route 2 North": {
                "direction": "north",
                "blocked": False,
                "min_explores": 7,
            },
        },
        wild_pokemon=["CATERPIE", "WEEDLE", "PIKACHU"],
        wild_level_range=(3, 6),
        trainers=3,  # Bug Catchers
        trainer_encounter_rate=0.25,  # Slightly lower — forest feels wilder than roads
        wild_encounter_rate=0.55,  # Dense undergrowth means more wild encounters
    ),
    "Pewter City": Location(
        name="Pewter City",
        location_type=TYPE_TOWN,
        description="A grey, stony city wedged between the mountains, home to the Natural Science Museum and Brock — the undefeated Rock-type Gym Leader who will test your mettle.",
        exits={
            "Route 2 North": {"direction": "south", "blocked": False},
            "Route 3": {"direction": "east", "blocked": False},
        },
        buildings=["Pokemon Center", "Pokemart", "Gym", "Museum"],
    ),
    "Route 3": Location(
        name="Route 3",
        location_type=TYPE_ROUTE,
        description="A long eastbound road stretching from Pewter City toward Mt. Moon. Lasses and Youngsters patrol the tall grass, training hard under the mountain's shadow.",
        exits={
            "Pewter City": {"direction": "west", "blocked": False, "min_explores": 7},
            "Mt. Moon": {"direction": "east", "blocked": False, "min_explores": 7},
        },
        wild_pokemon=["PIDGEY", "JIGGLYPUFF", "MEOWTH"],
        wild_level_range=(10, 14),
        trainers=4,
        trainer_encounter_rate=0.35,
        wild_encounter_rate=0.45,
    ),
    "Mt. Moon": Location(
        name="Mt. Moon",
        location_type=TYPE_FOREST,
        description="A twisting cave system riddled with Zubat and Clefairy. Deep inside, researchers dig for fossils, and a strange sparkling stone has been sighted near the exit tunnel.",
        exits={
            "Route 3": {"direction": "west", "blocked": False, "min_explores": 8},
            "Route 4": {"direction": "east", "blocked": False, "min_explores": 8},
        },
        wild_pokemon=["ZUBAT", "CLEFAIRY", "GEODUDE"],
        wild_level_range=(8, 12),
        trainers=3,
        trainer_encounter_rate=0.30,
        wild_encounter_rate=0.55,
    ),
    "Route 4": Location(
        name="Route 4",
        location_type=TYPE_ROUTE,
        description="The eastern side of Mt. Moon drops onto this short road that leads straight into Cerulean City. Spearow circle overhead as Rattata dart through the underbrush.",
        exits={
            "Mt. Moon": {"direction": "west", "blocked": False, "min_explores": 6},
            "Cerulean City": {"direction": "east", "blocked": False, "min_explores": 6},
        },
        wild_pokemon=["SPEAROW", "RATTATA"],
        wild_level_range=(13, 17),
        trainers=2,
        trainer_encounter_rate=0.30,
        wild_encounter_rate=0.45,
    ),
    "Cerulean City": Location(
        name="Cerulean City",
        location_type=TYPE_TOWN,
        description="A quiet city nestled beside a flowing river. Misty rules its Gym with an iron fist and a Water-type army, while the Bike Shop on the corner tempts every passerby.",
        exits={
            "Route 4": {"direction": "west", "blocked": False},
            "Route 5": {"direction": "south", "blocked": False},
            "Route 9": {"direction": "east", "blocked": False},
            "Route 24": {
                "direction": "north",
                "blocked": True,
                "reason": "Nugget Bridge — You must earn the Cascade Badge first",
            },
            "Cerulean Cave": {
                "direction": "northwest",
                "blocked": True,
                "reason": "The cave is sealed. Only the Pokemon Champion may enter.",
            },
        },
        buildings=["Pokemon Center", "Pokemart", "Gym", "Bike Shop", "Nugget Bridge"],
    ),
    "Route 24": Location(
        name="Route 24",
        location_type=TYPE_ROUTE,
        description=(
            "A wide road running north of Cerulean City. Trainers line up along Nugget Bridge, "
            "each one eager to prove their worth. The bridge leads to the tall grass where "
            "Bill's House sits at the far end."
        ),
        exits={
            "Cerulean City": {"direction": "south", "blocked": False},
        },
        buildings=["Bill's House"],
        wild_pokemon=["BELLSPROUT", "ABRA", "ODDISH"],
        wild_level_range=(14, 18),
        trainers=3,
        trainer_encounter_rate=0.35,
        wild_encounter_rate=0.40,
    ),
    "Route 21": Location(
        name="Route 21",
        location_type=TYPE_ROUTE,
        description=(
            "A long water route stretching south of Pallet Town. Surfers patrol the waves "
            "on the backs of their Water-type Pokemon, and the distant silhouette of "
            "Cinnabar Island shimmers on the horizon."
        ),
        exits={
            "Pallet Town": {"direction": "north", "blocked": False},
            "Cinnabar Island": {
                "direction": "south",
                "blocked": False,
                "min_explores": 4,
            },
        },
        wild_pokemon=["TENTACOOL", "TENTACRUEL", "MAGIKARP"],
        wild_level_range=(15, 35),
        trainers=2,
        trainer_encounter_rate=0.25,
        wild_encounter_rate=0.55,
    ),
    "Route 5": Location(
        name="Route 5",
        location_type=TYPE_ROUTE,
        description=(
            "A busy southbound road leading from Cerulean City toward Saffron City. "
            "Trainers patrol the tall grass, and a small gatehouse at the south end "
            "leads to the Underground Path."
        ),
        exits={
            "Cerulean City": {"direction": "north", "blocked": False, "min_explores": 6},
            "Underground Path (North)": {
                "direction": "south",
                "blocked": False,
                "min_explores": 6,
            },
        },
        wild_pokemon=["PIDGEY", "MEOWTH", "MANKEY", "NIDORAN♀", "NIDORAN♂"],
        wild_level_range=(13, 17),
        trainers=3,
        trainer_encounter_rate=0.30,
        wild_encounter_rate=0.45,
    ),
    "Route 6": Location(
        name="Route 6",
        location_type=TYPE_ROUTE,
        description=(
            "A wide road running north of Vermillion City. The grass here is tall and "
            "untamed, and the salty sea breeze from Vermillion Harbour drifts up the path. "
            "A gatehouse at the north end connects to the Underground Path."
        ),
        exits={
            "Underground Path (South)": {
                "direction": "north",
                "blocked": False,
                "min_explores": 6,
            },
            "Vermillion City": {"direction": "south", "blocked": False, "min_explores": 6},
        },
        wild_pokemon=["PIDGEY", "MEOWTH", "MANKEY", "NIDORAN♀", "NIDORAN♂"],
        wild_level_range=(14, 18),
        trainers=3,
        trainer_encounter_rate=0.30,
        wild_encounter_rate=0.45,
    ),
    "Underground Path (North)": Location(
        name="Underground Path (North)",
        location_type=TYPE_DUNGEON,
        description=(
            "The northern entrance to the long tunnel connecting Routes 5 and 6. "
            "Vendors sell rare items in the cool underground air, and the tunnel "
            "stretches south under Saffron City all the way to Route 6."
        ),
        exits={
            "Route 5": {"direction": "north", "blocked": False},
            "Underground Path (South)": {"direction": "south", "blocked": False},
        },
        wild_pokemon=[],
        wild_level_range=(1, 1),
        trainers=0,
        wild_encounter_rate=0.0,
    ),
    "Underground Path (South)": Location(
        name="Underground Path (South)",
        location_type=TYPE_DUNGEON,
        description=(
            "The southern exit of the Underground Path, emerging just north of Vermillion City. "
            "The tunnel has no wild Pokemon — just the echo of footsteps and the distant "
            "smell of the sea."
        ),
        exits={
            "Underground Path (North)": {"direction": "north", "blocked": False},
            "Route 6": {"direction": "south", "blocked": False},
        },
        wild_pokemon=[],
        wild_level_range=(1, 1),
        trainers=0,
        wild_encounter_rate=0.0,
    ),
    "Vermillion City": Location(
        name="Vermillion City",
        location_type=TYPE_TOWN,
        description=(
            "A bustling port city on the southern coast. The S.S. Anne docks here "
            "occasionally, and Lt. Surge — the Lightning American — guards the Gym "
            "with a ferocious team of Electric-type Pokemon."
        ),
        exits={
            "Route 6": {"direction": "north", "blocked": False},
            "Route 11": {"direction": "east", "blocked": False},
            "S.S. Anne": {
                "direction": "south",
                "blocked": True,
                "reason": "The S.S. Anne is docked here — show your S.S. Anne Ticket to board",
            },
        },
        buildings=["Pokemon Center", "Pokemart", "Gym", "S.S. Anne Dock"],
    ),
    "Route 11": Location(
        name="Route 11",
        location_type=TYPE_ROUTE,
        description=(
            "A long eastbound road stretching from Vermillion City. Drowzee shuffle "
            "through the tall grass as Spearow circle overhead. The entrance to "
            "Diglett's Cave is visible on the north side of the road."
        ),
        exits={
            "Vermillion City": {
                "direction": "west",
                "blocked": False,
                "min_explores": 7,
            },
            "Diglett's Cave": {"direction": "north", "blocked": False},
        },
        wild_pokemon=["EKANS", "SPEAROW", "DROWZEE", "KOFFING"],
        wild_level_range=(13, 19),
        trainers=3,
        trainer_encounter_rate=0.30,
        wild_encounter_rate=0.45,
    ),
    "Diglett's Cave": Location(
        name="Diglett's Cave",
        location_type=TYPE_DUNGEON,
        description=(
            "A narrow tunnel dug out entirely by Diglett and their evolved forms. "
            "The cave runs from Route 2 all the way to Route 11, making it a "
            "useful shortcut — and a great place to catch a Diglett or Dugtrio."
        ),
        exits={
            "Route 2 North": {"direction": "north", "blocked": False},
            "Route 11": {"direction": "south", "blocked": False},
        },
        wild_pokemon=["DIGLETT", "DUGTRIO"],
        wild_level_range=(15, 22),
        trainers=0,
        wild_encounter_rate=0.60,
    ),
    "Route 9": Location(
        name="Route 9",
        location_type=TYPE_ROUTE,
        description=(
            "A rocky eastbound road that curves around the base of a mountain range. "
            "The terrain is rough underfoot, and trainers here mean business — "
            "they're all heading toward Rock Tunnel."
        ),
        exits={
            "Cerulean City": {
                "direction": "west",
                "blocked": False,
                "min_explores": 7,
            },
            "Route 10": {"direction": "east", "blocked": False, "min_explores": 7},
        },
        wild_pokemon=["RATTATA", "EKANS", "SPEAROW", "NIDORAN♀", "NIDORAN♂"],
        wild_level_range=(15, 21),
        trainers=3,
        trainer_encounter_rate=0.35,
        wild_encounter_rate=0.45,
    ),
    "Route 10": Location(
        name="Route 10",
        location_type=TYPE_ROUTE,
        description=(
            "A power plant route split in two by Rock Tunnel. The hum of electricity "
            "fills the air near the Power Plant to the east, and Voltorb are known "
            "to lurk in the tall grass beside the rocky path."
        ),
        exits={
            "Route 9": {"direction": "west", "blocked": False, "min_explores": 6},
            "Rock Tunnel": {"direction": "south", "blocked": False, "min_explores": 6},
            "Power Plant": {
                "direction": "east",
                "blocked": True,
                "reason": "You need HM Surf to reach the Power Plant across the river",
            },
        },
        wild_pokemon=["VOLTORB", "MAGNEMITE", "SPEAROW"],
        wild_level_range=(17, 23),
        trainers=2,
        trainer_encounter_rate=0.25,
        wild_encounter_rate=0.45,
    ),
    "Rock Tunnel": Location(
        name="Rock Tunnel",
        location_type=TYPE_DUNGEON,
        description=(
            "A pitch-black labyrinth carved through the mountains. Without the HM Flash, "
            "navigating is a nightmare — Zubat swarm from every direction and Onix "
            "rumble beneath your feet. Bring Repels."
        ),
        exits={
            "Route 10": {"direction": "north", "blocked": False, "min_explores": 10},
            "Lavender Town": {"direction": "south", "blocked": False, "min_explores": 10},
        },
        wild_pokemon=["ZUBAT", "GEODUDE", "MACHOP", "ONIX", "GRAVELER"],
        wild_level_range=(15, 23),
        trainers=5,
        trainer_encounter_rate=0.30,
        wild_encounter_rate=0.65,
    ),
    "Lavender Town": Location(
        name="Lavender Town",
        location_type=TYPE_TOWN,
        description=(
            "A quiet, eerie town overshadowed by the looming Pokemon Tower. "
            "A haunting melody drifts through the streets, and townspeople speak in hushed tones "
            "about the ghost that wanders the tower's upper floors. Mr. Fuji tends to the "
            "memorial here — a gentle soul amid the sorrow."
        ),
        exits={
            "Rock Tunnel": {"direction": "north", "blocked": False},
            "Route 8": {"direction": "west", "blocked": False},
            "Route 12": {"direction": "south", "blocked": False},
        },
        buildings=["Pokemon Center", "Pokemart", "Pokemon Tower"],
    ),
    "Route 8": Location(
        name="Route 8",
        location_type=TYPE_ROUTE,
        description=(
            "A winding road that runs between Saffron City and Lavender Town. "
            "Bikers tear up the asphalt, and the grass rustles with Growlithe and Vulpix "
            "on the western side. The spires of Pokemon Tower are visible to the east."
        ),
        exits={
            "Lavender Town": {
                "direction": "east",
                "blocked": False,
                "min_explores": 7,
            },
            "Saffron City": {
                "direction": "west",
                "blocked": False,
            },
        },
        wild_pokemon=["GROWLITHE", "VULPIX", "MEOWTH", "DROWZEE"],
        wild_level_range=(19, 25),
        trainers=4,
        trainer_encounter_rate=0.35,
        wild_encounter_rate=0.45,
    ),
    "Route 7": Location(
        name="Route 7",
        location_type=TYPE_ROUTE,
        description=(
            "A short but lively route stretching between Celadon City and Saffron City. "
            "Gamblers and trainers heading to the city compete in the grassy median, "
            "and Slowpoke lumber through the tall grass at the route's heart."
        ),
        exits={
            "Celadon City": {
                "direction": "west",
                "blocked": True,
                "reason": "Celadon City is still ahead — you'll need to find another way in",
            },
            "Saffron City": {
                "direction": "east",
                "blocked": False,
            },
        },
        wild_pokemon=["PIDGEY", "DROWZEE", "SLOWPOKE", "MEOWTH"],
        wild_level_range=(22, 28),
        trainers=3,
        trainer_encounter_rate=0.30,
        wild_encounter_rate=0.45,
    ),
    # ── Celadon City ──────────────────────────────────────────────────────────
    "Celadon City": Location(
        name="Celadon City",
        location_type=TYPE_TOWN,
        description=(
            "A sprawling, lush city famous for its enormous Department Store and its "
            "fragrant Gym. Beneath the neon lights of the Game Corner, however, "
            "Team Rocket operates a hidden hideout — and they're not hiding very well."
        ),
        exits={
            "Route 7": {"direction": "east", "blocked": False},
            "Route 16": {"direction": "west", "blocked": False},
            "Team Rocket's Hideout": {
                "direction": "underground",
                "blocked": False,
            },
        },
        buildings=[
            "Pokemon Center",
            "Pokemart",
            "Gym",
            "Game Corner",
            "Celadon Department Store",
        ],
    ),
    # ── Team Rocket's Hideout ─────────────────────────────────────────────────
    "Team Rocket's Hideout": Location(
        name="Team Rocket's Hideout",
        location_type=TYPE_DUNGEON,
        description=(
            "A labyrinthine underground base hidden beneath Celadon's Game Corner. "
            "Team Rocket Grunts patrol every corridor, and spinning floor tiles make "
            "navigation treacherous. Giovanni, the Rocket boss, waits at the bottom "
            "— defeat him and you'll recover the Silph Scope."
        ),
        exits={
            "Celadon City": {"direction": "up", "blocked": False},
        },
        wild_pokemon=["RATTATA", "EKANS", "KOFFING", "DROWZEE"],
        wild_level_range=(25, 33),
        trainers=10,
        trainer_encounter_rate=0.50,
        wild_encounter_rate=0.35,
    ),
    "Route 12": Location(
        name="Route 12",
        location_type=TYPE_ROUTE,
        description=(
            "A long north-south coastal route ideal for fishing. Fishermen line the piers, "
            "and the sound of waves crashing accompanies every step. Snorlax is said to "
            "block the southern portion of this route, but the north is wide open."
        ),
        exits={
            "Lavender Town": {
                "direction": "north",
                "blocked": False,
                "min_explores": 5,
            },
            "Route 13": {
                "direction": "south",
                "blocked": True,
                "reason": "A sleeping Snorlax blocks the path south — you'll need the Poke Flute to wake it",
            },
        },
        wild_pokemon=["TENTACOOL", "GOLDEEN", "MAGIKARP", "TANGELA"],
        wild_level_range=(20, 28),
        trainers=3,
        trainer_encounter_rate=0.25,
        wild_encounter_rate=0.50,
    ),
    "Pokemon Tower": Location(
        name="Pokemon Tower",
        location_type=TYPE_DUNGEON,
        description=(
            "A seven-story tower in Lavender Town where beloved Pokemon are laid to rest. "
            "The upper floors are thick with the spiritual energy of Ghost-type Pokemon, "
            "and a sorrowful Marowak wanders the third floor. Mr. Fuji tends to the memorial "
            "on the ground floor, though something troubles him deeply."
        ),
        exits={
            "Lavender Town": {"direction": "down", "blocked": False},
        },
        wild_pokemon=["GASTLY", "HAUNTER", "CUBONE"],
        wild_level_range=(20, 28),
        trainers=3,
        trainer_encounter_rate=0.25,
        wild_encounter_rate=0.55,
    ),
    # ── Routes 13-15 (South Coast) ────────────────────────────────────────────
    "Route 13": Location(
        name="Route 13",
        location_type=TYPE_ROUTE,
        description=(
            "A windswept coastal path south of Lavender Town. Birdkeepers and Fishermen "
            "patrol the clifftops, and the salty sea breeze carries the cry of Farfetch'd."
        ),
        exits={
            "Route 12": {
                "direction": "north",
                "blocked": True,
                "reason": "A sleeping Snorlax blocks the path north — you'll need the Poke Flute to wake it",
            },
            "Route 14": {"direction": "west", "blocked": False, "min_explores": 6},
        },
        wild_pokemon=["PIDGEY", "PIDGEOTTO", "FARFETCH'D", "DITTO", "VENONAT"],
        wild_level_range=(22, 30),
        trainers=4,
        trainer_encounter_rate=0.30,
        wild_encounter_rate=0.40,
    ),
    "Route 14": Location(
        name="Route 14",
        location_type=TYPE_ROUTE,
        description=(
            "A tangled path of tall grass and narrow walkways. Birdkeepers challenge any "
            "trainer who passes, and the Weepinbell lurking here are deceptively fast."
        ),
        exits={
            "Route 13": {"direction": "east", "blocked": False, "min_explores": 6},
            "Route 15": {"direction": "west", "blocked": False, "min_explores": 6},
        },
        wild_pokemon=["PIDGEOTTO", "WEEPINBELL", "GLOOM", "VENONAT", "DITTO"],
        wild_level_range=(25, 32),
        trainers=4,
        trainer_encounter_rate=0.30,
        wild_encounter_rate=0.40,
    ),
    "Route 15": Location(
        name="Route 15",
        location_type=TYPE_ROUTE,
        description=(
            "The final stretch of the south coast leading into Fuchsia City. "
            "A Pokemaniac watches the tall grass from the side of the road, and the "
            "distant Safari Zone gates are already visible to the west."
        ),
        exits={
            "Route 14": {"direction": "east", "blocked": False, "min_explores": 6},
            "Fuchsia City": {"direction": "west", "blocked": False, "min_explores": 5},
        },
        wild_pokemon=["PIDGEOTTO", "GLOOM", "WEEPINBELL", "VENONAT", "DITTO"],
        wild_level_range=(25, 33),
        trainers=4,
        trainer_encounter_rate=0.30,
        wild_encounter_rate=0.40,
    ),
    # ── Routes 16-18 (Cycling Road) ───────────────────────────────────────────
    "Route 16": Location(
        name="Route 16",
        location_type=TYPE_ROUTE,
        description=(
            "The start of the famous Cycling Road leading west out of Celadon City. "
            "The gate attendant waves you through, and the road ahead drops sharply downhill. "
            "Snorlax is said to nap beside the northern grass."
        ),
        exits={
            "Celadon City": {"direction": "east", "blocked": False},
            "Route 17": {"direction": "south", "blocked": False, "min_explores": 5},
        },
        wild_pokemon=["DODUO", "RATTATA", "SPEAROW"],
        wild_level_range=(20, 28),
        trainers=2,
        trainer_encounter_rate=0.25,
        wild_encounter_rate=0.35,
    ),
    "Route 17": Location(
        name="Route 17",
        location_type=TYPE_ROUTE,
        description=(
            "The long, steep downhill stretch of Cycling Road. Bikers race past at full "
            "speed, and the tall grass on either side hides surprisingly strong Pokemon. "
            "Once you start going, it's hard to stop."
        ),
        exits={
            "Route 16": {"direction": "north", "blocked": False, "min_explores": 7},
            "Route 18": {"direction": "south", "blocked": False, "min_explores": 7},
        },
        wild_pokemon=["DODUO", "RATTATA", "FEAROW", "DITTO"],
        wild_level_range=(22, 30),
        trainers=5,
        trainer_encounter_rate=0.35,
        wild_encounter_rate=0.40,
    ),
    "Route 18": Location(
        name="Route 18",
        location_type=TYPE_ROUTE,
        description=(
            "The flat end of Cycling Road, where the downhill rush levels out into open "
            "grassland east of Fuchsia City. The gate marks the end of the famous road."
        ),
        exits={
            "Route 17": {"direction": "north", "blocked": False, "min_explores": 5},
            "Fuchsia City": {"direction": "east", "blocked": False, "min_explores": 4},
        },
        wild_pokemon=["DODUO", "FEAROW", "RATTATA"],
        wild_level_range=(23, 30),
        trainers=2,
        trainer_encounter_rate=0.25,
        wild_encounter_rate=0.35,
    ),
    # ── Fuchsia City ──────────────────────────────────────────────────────────
    "Fuchsia City": Location(
        name="Fuchsia City",
        location_type=TYPE_TOWN,
        description=(
            "A quiet city famous for its Safari Zone and its ninja-themed Gym. "
            "Koga, the Gym Leader, is a master of Poison-type tactics and invisible traps. "
            "The Safari Zone to the north lets you catch rare Pokemon that can't be found elsewhere."
        ),
        exits={
            "Route 15": {"direction": "east", "blocked": False},
            "Route 18": {"direction": "west", "blocked": False},
            "Safari Zone": {"direction": "north", "blocked": False},
            "Route 19": {
                "direction": "south",
                "blocked": True,
                "reason": "You need HM Surf to cross the water — defeat Koga and teach Surf to a Pokemon",
            },
        },
        buildings=["Pokemon Center", "Pokemart", "Gym", "Safari Zone"],
    ),
    # ── Safari Zone ───────────────────────────────────────────────────────────
    "Safari Zone": Location(
        name="Safari Zone",
        location_type=TYPE_DUNGEON,
        description=(
            "A vast nature reserve where rare Pokemon roam freely. You're given Safari Balls "
            "and must use Bait or Rocks to improve your catch odds — no battling allowed here! "
            "Scyther, Kangaskhan, and Tauros have all been spotted roaming the tall grass."
        ),
        exits={
            "Fuchsia City": {"direction": "south", "blocked": False},
        },
        wild_pokemon=[
            "NIDORAN♀",
            "NIDORAN♂",
            "PARAS",
            "VENONAT",
            "SCYTHER",
            "KANGASKHAN",
            "TAUROS",
            "CHANSEY",
            "PINSIR",
            "EXEGGCUTE",
        ],
        wild_level_range=(22, 35),
        trainers=0,
        trainer_encounter_rate=0.0,
        wild_encounter_rate=0.60,
    ),
    # ── Routes 19-20 (Sea Routes to Cinnabar) ─────────────────────────────────
    "Route 19": Location(
        name="Route 19",
        location_type=TYPE_ROUTE,
        description=(
            "A wide open sea route south of Fuchsia City. Swimmers and Divers compete to "
            "cross the rough waters, and Tentacool swarms make every step treacherous."
        ),
        exits={
            "Fuchsia City": {
                "direction": "north",
                "blocked": True,
                "reason": "You need HM Surf to cross the water",
            },
            "Route 20": {
                "direction": "south",
                "blocked": True,
                "reason": "You need HM Surf to cross the water",
            },
        },
        wild_pokemon=["TENTACOOL", "TENTACRUEL", "HORSEA", "GOLDEEN"],
        wild_level_range=(25, 35),
        trainers=4,
        trainer_encounter_rate=0.30,
        wild_encounter_rate=0.65,
    ),
    "Route 20": Location(
        name="Route 20",
        location_type=TYPE_ROUTE,
        description=(
            "The sea route curving around the south coast toward Cinnabar Island. "
            "Sea Swimmers patrol the choppy waters, and the volcanic silhouette of "
            "Cinnabar Island grows larger on the western horizon. Rumour has it the "
            "Seafoam Islands lie somewhere along this frozen stretch of sea."
        ),
        exits={
            "Route 19": {
                "direction": "east",
                "blocked": True,
                "reason": "You need HM Surf to cross the water",
            },
            "Cinnabar Island": {
                "direction": "west",
                "blocked": False,
            },
            "Seafoam Islands": {
                "direction": "north",
                "blocked": True,
                "reason": "You need HM Surf to reach the Seafoam Islands",
            },
        },
        wild_pokemon=["TENTACOOL", "TENTACRUEL", "HORSEA", "SEADRA", "GOLDEEN"],
        wild_level_range=(28, 38),
        trainers=4,
        trainer_encounter_rate=0.30,
        wild_encounter_rate=0.65,
    ),
    # ── Saffron City ──────────────────────────────────────────────────────────────
    "Saffron City": Location(
        name="Saffron City",
        location_type=TYPE_TOWN,
        description=(
            "A thriving metropolis in central Kanto. "
            "The imposing Silph Co. headquarters dominates the skyline."
        ),
        exits={
            "Route 7": {"direction": "west", "blocked": False},
            "Route 8": {"direction": "east", "blocked": False},
        },
        buildings=["Silph Co.", "Sabrina's Gym", "Pokemon Center", "Pokemart"],
    ),
    # ── Cinnabar Island ──────────────────────────────────────────────────────────
    "Cinnabar Island": Location(
        name="Cinnabar Island",
        location_type=TYPE_TOWN,
        description=(
            "A small volcanic island in the south. "
            "Home to a world-famous research lab and the ruins of a Pokémon Mansion."
        ),
        exits={
            "Route 20": {"direction": "east", "blocked": False},
            "Route 21": {"direction": "north", "blocked": False},
        },
        buildings=["Pokemon Lab", "Pokemon Mansion", "Blaine's Gym", "Pokemon Center", "Pokemart"],
    ),
    # ── Pokemon League ───────────────────────────────────────────────────────────────
    "Pokemon League": Location(
        name="Pokemon League",
        location_type=TYPE_TOWN,
        description=(
            "The Indigo Plateau — seat of the Pokemon League. "
            "The greatest trainers in Kanto have gathered here. "
            "Four Elite trainers and the reigning Champion stand between you and glory."
        ),
        exits={
            "Victory Road": {"direction": "south", "blocked": False},
        },
        buildings=["Pokemon League Reception", "Elite Four", "Hall of Fame"],
        blocked_buildings={
            "Hall of Fame": "You haven't become Champion yet.",
        },
        wild_pokemon=[],
    ),
    # ── Victory Road ─────────────────────────────────────────────────────────────────
    "Victory Road": Location(
        name="Victory Road",
        location_type=TYPE_DUNGEON,
        description=(
            "A treacherous mountain cave on the path to the Pokemon League. "
            "Only the strongest trainers make it through. "
            "Legends speak of a fiery bird deep within the cave — Moltres, the legendary fire Pokemon."
        ),
        exits={
            "Route 22": {"direction": "west", "blocked": False},
            "Pokemon League": {
                "direction": "east",
                "blocked": True,
                "reason": "The Pokemon League awaits beyond Victory Road — finish the cave first",
            },
        },
        wild_pokemon=["MACHOKE", "GEODUDE", "GRAVELER", "ONIX", "VENOMOTH"],
        wild_level_range=(36, 44),
        trainers=4,
        trainer_encounter_rate=0.35,
        wild_encounter_rate=0.55,
    ),
    # ── Power Plant ───────────────────────────────────────────────────────────────────
    "Power Plant": Location(
        name="Power Plant",
        location_type=TYPE_DUNGEON,
        description=(
            "An abandoned power station on the banks of Route 10. "
            "Electric-type Pokemon lurk behind every generator and inside every machine. "
            "A powerful presence crackles in the deepest room — Zapdos, the legendary electric Pokemon."
        ),
        exits={
            "Route 10": {
                "direction": "west",
                "blocked": True,
                "reason": "You need HM Surf to cross back to Route 10",
            },
        },
        wild_pokemon=["VOLTORB", "ELECTRODE", "MAGNEMITE", "MAGNETON", "ELECTABUZZ"],
        wild_level_range=(30, 46),
        trainers=0,
        trainer_encounter_rate=0.0,
        wild_encounter_rate=0.60,
    ),
    # ── Seafoam Islands ────────────────────────────────────────────────────────────────
    "Seafoam Islands": Location(
        name="Seafoam Islands",
        location_type=TYPE_DUNGEON,
        description=(
            "A pair of icy caverns embedded in the sea south of Cinnabar Island. "
            "Freezing mist rolls through the tunnels, Water and Ice Pokemon make their home here, "
            "and a legendary frozen bird slumbers deep inside — Articuno, the legendary ice Pokemon."
        ),
        exits={
            "Route 20": {
                "direction": "south",
                "blocked": True,
                "reason": "You need HM Surf to return to Route 20",
            },
        },
        wild_pokemon=["SEEL", "DEWGONG", "SLOWPOKE", "PSYDUCK", "GOLDUCK"],
        wild_level_range=(35, 48),
        trainers=0,
        trainer_encounter_rate=0.0,
        wild_encounter_rate=0.55,
    ),
    # ── Cerulean Cave ──────────────────────────────────────────────────────────────────
    "Cerulean Cave": Location(
        name="Cerulean Cave",
        location_type=TYPE_DUNGEON,
        description=(
            "An eerie cave northwest of Cerulean City, sealed to all but the Pokemon Champion. "
            "Strong Pokemon wander its labyrinthine passages, drawn by an overwhelming psychic presence. "
            "At the deepest level waits Mewtwo — the most powerful Pokemon ever created."
        ),
        exits={
            "Cerulean City": {
                "direction": "southeast",
                "blocked": False,
            },
        },
        wild_pokemon=["DITTO", "GOLBAT", "PARASECT", "RHYDON", "KADABRA"],
        wild_level_range=(46, 60),
        trainers=0,
        trainer_encounter_rate=0.0,
        wild_encounter_rate=0.55,
    ),
}


def get_location(name: str) -> Optional[Location]:
    """
    Get a location by name.

    Args:
        name: Name of the location

    Returns:
        Location object or None if not found
    """
    return LOCATIONS.get(name)


def get_starting_location() -> str:
    """Get the name of the starting location."""
    return "Pallet Town"
