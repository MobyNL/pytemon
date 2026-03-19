"""
Trainer data for Pokemon battles.

This module defines trainers that can be encountered throughout the game.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class TrainerPokemon:
    """A Pokémon slot in a trainer's roster."""

    species: str  # uppercase, e.g. "CHARMANDER"
    level: int

    def __getitem__(self, key: str):
        return getattr(self, key)

    def get(self, key: str, default=None):
        try:
            return getattr(self, key)
        except AttributeError:
            return default


@dataclass
class Trainer:
    """A trainer definition."""

    id: str
    name: str
    trainer_class: str
    location: str
    pokemon: List[TrainerPokemon]
    prize_money: int
    intro_text: List[str]
    defeat_text: List[str]
    badge_reward: str = ""
    badge_id: str = ""
    victory_text: List[str] = field(default_factory=list)
    preferred_types: List[str] = field(default_factory=list)  # Gym leader type specialty

    def __getitem__(self, key: str):
        return getattr(self, key)

    def get(self, key: str, default=None):
        try:
            val = getattr(self, key)
            # Return default for empty-string sentinel values on optional fields
            if val == "" and key in ("badge_reward", "badge_id"):
                return default
            return val
        except AttributeError:
            return default


# Trainer class types
TRAINER_CLASSES = {
    "Bug Catcher": {
        "sprite": "🐛",
        "prize_money_multiplier": 10,
        "description": "Young trainers who love Bug Pokemon",
    },
    "Youngster": {
        "sprite": "👦",
        "prize_money_multiplier": 15,
        "description": "Young boys beginning their Pokemon journey",
    },
    "Lass": {
        "sprite": "👧",
        "prize_money_multiplier": 15,
        "description": "Young girls beginning their Pokemon journey",
    },
    "Hiker": {
        "sprite": "🥾",
        "prize_money_multiplier": 20,
        "description": "Mountain climbers with Rock and Fighting Pokemon",
    },
    "Rival": {
        "sprite": "😏",
        "prize_money_multiplier": 30,
        "description": "Your childhood rival - a skilled trainer",
    },
    "Gym Leader": {
        "sprite": "⭐",
        "prize_money_multiplier": 100,
        "description": "Elite trainers who test your skills",
    },
    "Swimmer": {
        "sprite": "🏊",
        "prize_money_multiplier": 20,
        "description": "Trainers who specialise in Water-type Pokemon",
    },
    "Sailor": {
        "sprite": "⚓",
        "prize_money_multiplier": 25,
        "description": "Seafarers who train Water and Normal-type Pokemon",
    },
    "Jr. Trainer♂": {
        "sprite": "👦",
        "prize_money_multiplier": 18,
        "description": "Young male trainers showing off on the S.S. Anne",
    },
    "Jr. Trainer♀": {
        "sprite": "👧",
        "prize_money_multiplier": 18,
        "description": "Young female trainers showing off on the S.S. Anne",
    },
    "Fisherman": {
        "sprite": "🎣",
        "prize_money_multiplier": 20,
        "description": "Anglers who specialise in Water-type Pokemon",
    },
    "Channeler": {
        "sprite": "👻",
        "prize_money_multiplier": 30,
        "description": "Spiritual trainers who communicate with Ghost-type Pokemon",
    },
    "Biker": {
        "sprite": "🏍️",
        "prize_money_multiplier": 20,
        "description": "Motorcycle-riding trainers with Poison-type Pokemon",
    },
    "Gambler": {
        "sprite": "🎲",
        "prize_money_multiplier": 35,
        "description": "High-rollers who rely on luck and Psychic Pokemon",
    },
    "Team Rocket": {
        "sprite": "🚀",
        "prize_money_multiplier": 25,
        "description": "Criminals who exploit Pokemon for profit",
    },
    "Beauty": {
        "sprite": "💄",
        "prize_money_multiplier": 50,
        "description": "Stylish trainers who favour elegant Grass-type Pokemon",
    },
    "Juggler": {
        "sprite": "🤹",
        "prize_money_multiplier": 40,
        "description": "Circus performers who specialise in tricky Poison-type Pokemon",
    },
    "Bird Keeper": {
        "sprite": "🦅",
        "prize_money_multiplier": 36,
        "description": "Trainers with a passion for Flying-type Pokemon",
    },
    "Pokemaniac": {
        "sprite": "🧟",
        "prize_money_multiplier": 60,
        "description": "Obsessive collectors who often use rare or unusual Pokemon",
    },
    "Psychic": {
        "sprite": "🔮",
        "prize_money_multiplier": 32,
        "description": "Trainers who harness psychic powers and Psychic-type Pokemon",
    },
    "Medium": {
        "sprite": "🧿",
        "prize_money_multiplier": 32,
        "description": "Spiritual mediums who commune with Ghost and Psychic-type Pokemon",
    },
    "Super Nerd": {
        "sprite": "🤓",
        "prize_money_multiplier": 24,
        "description": "Tech-savvy trainers who favour evolved and powerful Pokemon",
    },
    "Tamer": {
        "sprite": "🦁",
        "prize_money_multiplier": 40,
        "description": "Wild Pokemon handlers who specialise in Ground and Rock-type Pokemon",
    },
    "Veteran": {
        "sprite": "🎖️",
        "prize_money_multiplier": 100,
        "description": "Experienced trainers with high-level and rare Pokemon",
    },
    "Cool Trainer": {
        "sprite": "😎",
        "prize_money_multiplier": 100,
        "description": "Elite trainers who dominate with powerful and well-trained Pokemon",
    },
    "Black Belt": {
        "sprite": "🥋",
        "prize_money_multiplier": 30,
        "description": "Martial arts masters who rely on Fighting-type Pokemon",
    },
    "Rocket Grunt": {
        "sprite": "🚀",
        "prize_money_multiplier": 30,
        "description": "Team Rocket foot soldiers enforcing criminal operations",
    },
    "Rocket Executive": {
        "sprite": "💼",
        "prize_money_multiplier": 50,
        "description": "Senior Team Rocket officers who command Silph Co. operations",
    },
}


# Trainer definitions
TRAINERS: Dict[str, Trainer] = {
    # ===== Oak's Lab - First Rival Battle =====
    "rival_oaks_lab": Trainer(
        id="rival_oaks_lab",
        name="Rival",
        trainer_class="Rival",
        location="Professor Oak's Lab",
        pokemon=[
            TrainerPokemon(species="CHARMANDER", level=5),  # Will vary by player's choice
        ],
        prize_money=175,
        intro_text=[
            "😏 [bold]Rival:[/bold] [cyan]Wait! {player_name}![/cyan]",
            "[cyan]   Let's test out our new Pokemon![/cyan]",
            "[cyan]   Come on! I bet my Pokemon is stronger than yours![/cyan]",
        ],
        defeat_text=[
            "[cyan]What?! Unbelievable![/cyan]",
            "[cyan]   I picked the superior Pokemon![/cyan]",
            "[cyan]   ...but I still lost?[/cyan]",
        ],
        victory_text=[
            "[cyan]Yeah! Am I great or what?[/cyan]",
            "[cyan]   You better train hard if you want to catch up![/cyan]",
        ],
    ),
    # ===== Route 22 - Rival Battle 2 =====
    "rival_route22": Trainer(
        id="rival_route22",
        name="Rival",
        trainer_class="Rival",
        location="Route 22",
        pokemon=[
            TrainerPokemon(species="SQUIRTLE", level=5),  # Will vary by player's choice
        ],
        prize_money=175,
        intro_text=[
            "😏 [bold]Rival:[/bold] [cyan]Hey! {player_name}![/cyan]",
            "[cyan]   You're trying to sneak past me?[/cyan]",
            "[cyan]   No way! Let's battle![/cyan]",
        ],
        defeat_text=[
            "[cyan]What? I can't believe I lost![/cyan]",
            "[cyan]   I picked the wrong Pokemon![/cyan]",
        ],
        victory_text=[
            "[cyan]Heh! Am I great or what?[/cyan]",
            "[cyan]   You better keep training![/cyan]",
        ],
    ),
    # ===== Cerulean City - Rival Battle 3 (Nugget Bridge) =====
    "rival_cerulean": Trainer(
        id="rival_cerulean",
        name="Rival",
        trainer_class="Rival",
        location="Cerulean City",
        pokemon=[
            TrainerPokemon(
                species="CHARMELEON", level=18
            ),  # Runtime: set to rival's actual evolved starter
            TrainerPokemon(species="PIDGEOTTO", level=16),
        ],
        prize_money=900,
        intro_text=[
            "😏 [bold]Rival:[/bold] [cyan]{player_name}! I knew I'd find you here![/cyan]",
            "[cyan]   I heard you beat all the trainers on Nugget Bridge![/cyan]",
            "[cyan]   Pretty impressive... but you won't beat ME![/cyan]",
            "[cyan]   I've been training nonstop since Oak's lab![/cyan]",
        ],
        defeat_text=[
            "[cyan]What?! That can't be right![/cyan]",
            "[cyan]   I've been training this whole time...[/cyan]",
            "[cyan]   This isn't over, {player_name}![/cyan]",
        ],
        victory_text=[
            "[cyan]Hah! Did you really think you could beat me?[/cyan]",
            "[cyan]   I've been training hard while you were dawdling![/cyan]",
        ],
    ),
    # ===== Viridian Forest - Bug Catchers =====
    "bug_catcher_rick": Trainer(
        id="bug_catcher_rick",
        name="Rick",
        trainer_class="Bug Catcher",
        location="Viridian Forest",
        pokemon=[
            TrainerPokemon(species="WEEDLE", level=6),
            TrainerPokemon(species="CATERPIE", level=6),
        ],
        prize_money=60,
        intro_text=[
            "🐛 [bold]Bug Catcher Rick:[/bold] [green]Hey! I caught loads of Pokemon![/green]",
            "[green]   Wanna see what I got?[/green]",
        ],
        defeat_text=["[green]No! My bugs were too weak![/green]"],
        victory_text=["[green]See? Bug Pokemon are strong![/green]"],
    ),
    "bug_catcher_doug": Trainer(
        id="bug_catcher_doug",
        name="Doug",
        trainer_class="Bug Catcher",
        location="Viridian Forest",
        pokemon=[
            TrainerPokemon(species="WEEDLE", level=7),
            TrainerPokemon(species="KAKUNA", level=7),
            TrainerPokemon(species="WEEDLE", level=7),
        ],
        prize_money=70,
        intro_text=[
            "🐛 [bold]Bug Catcher Doug:[/bold] [green]Bug Pokemon evolve really fast![/green]",
            "[green]   Mine are super strong![/green]",
        ],
        defeat_text=["[green]Aww, I need to train more...[/green]"],
        victory_text=["[green]Told ya! Bug Pokemon rule![/green]"],
    ),
    "bug_catcher_anthony": Trainer(
        id="bug_catcher_anthony",
        name="Anthony",
        trainer_class="Bug Catcher",
        location="Viridian Forest",
        pokemon=[
            TrainerPokemon(species="CATERPIE", level=7),
            TrainerPokemon(species="CATERPIE", level=8),
        ],
        prize_money=80,
        intro_text=[
            "🐛 [bold]Bug Catcher Anthony:[/bold] [green]Caterpie is the best![/green]",
            "[green]   I'm gonna fill my team with them![/green]",
        ],
        defeat_text=["[green]My Caterpies weren't strong enough?[/green]"],
        victory_text=["[green]Ha! Caterpie power![/green]"],
    ),
    # ===== Route 1 - Starting trainers =====
    "youngster_joey": Trainer(
        id="youngster_joey",
        name="Joey",
        trainer_class="Youngster",
        location="Route 1",
        pokemon=[
            TrainerPokemon(species="RATTATA", level=4),
        ],
        prize_money=60,
        intro_text=[
            "👦 [bold]Youngster Joey:[/bold] [yellow]Hi! I like shorts![/yellow]",
            "[yellow]   They're comfy and easy to wear![/yellow]",
            "[yellow]   Let's battle![/yellow]",
        ],
        defeat_text=["[yellow]Aww... my Rattata...[/yellow]"],
        victory_text=["[yellow]My Rattata is the top percentage of Rattata![/yellow]"],
    ),
    # ═════════════════════════════════════════════════════════════
    # ROUTE 3 TRAINERS
    # ═════════════════════════════════════════════════════════════
    "lass_miriam": Trainer(
        id="lass_miriam",
        name="Miriam",
        trainer_class="Lass",
        location="Route 3",
        pokemon=[
            TrainerPokemon("PIDGEY", 12),
            TrainerPokemon("CLEFAIRY", 12),
        ],
        prize_money=180,
        intro_text=[
            "👧 [bold]Lass Miriam:[/bold] [yellow]La la la! I love cute Pokemon![/yellow]",
            "[yellow]   I hope mine are strong enough![/yellow]",
        ],
        defeat_text=["[yellow]Waaah! My Pokemon...[/yellow]"],
        victory_text=["[yellow]Yay! Cute AND strong![/yellow]"],
    ),
    "youngster_ben": Trainer(
        id="youngster_ben",
        name="Ben",
        trainer_class="Youngster",
        location="Route 3",
        pokemon=[
            TrainerPokemon("MEOWTH", 13),
            TrainerPokemon("RATTATA", 12),
        ],
        prize_money=195,
        intro_text=[
            "👦 [bold]Youngster Ben:[/bold] [yellow]Hey! You look like a trainer![/yellow]",
            "[yellow]   Battle me before you get to Mt. Moon![/yellow]",
        ],
        defeat_text=["[yellow]Not bad... not bad at all.[/yellow]"],
        victory_text=["[yellow]Ha! You were no match for my Meowth![/yellow]"],
    ),
    "lass_holly": Trainer(
        id="lass_holly",
        name="Holly",
        trainer_class="Lass",
        location="Route 3",
        pokemon=[
            TrainerPokemon("JIGGLYPUFF", 14),
            TrainerPokemon("PIDGEY", 13),
        ],
        prize_money=210,
        intro_text=[
            "👧 [bold]Lass Holly:[/bold] [yellow]My Jigglypuff will put you to sleep![/yellow]",
        ],
        defeat_text=["[yellow]Not even a lullaby could save me...[/yellow]"],
        victory_text=["[yellow]Sweet dreams, loser![/yellow]"],
    ),
    "youngster_sam": Trainer(
        id="youngster_sam",
        name="Sam",
        trainer_class="Youngster",
        location="Route 3",
        pokemon=[
            TrainerPokemon("SPEAROW", 13),
            TrainerPokemon("MEOWTH", 13),
        ],
        prize_money=195,
        intro_text=[
            "👦 [bold]Youngster Sam:[/bold] [yellow]I'm training to beat Misty![/yellow]",
            "[yellow]   Start with me first![/yellow]",
        ],
        defeat_text=["[yellow]I still need more training...[/yellow]"],
        victory_text=["[yellow]See? I'm almost ready for Misty![/yellow]"],
    ),
    # ═════════════════════════════════════════════════════════════
    # MT. MOON TRAINERS
    # ═════════════════════════════════════════════════════════════
    "hiker_alan": Trainer(
        id="hiker_alan",
        name="Alan",
        trainer_class="Hiker",
        location="Mt. Moon",
        pokemon=[
            TrainerPokemon("GEODUDE", 10),
            TrainerPokemon("GEODUDE", 11),
        ],
        prize_money=220,
        intro_text=[
            "🥾 [bold]Hiker Alan:[/bold] [orange3]There are rare fossils in this cave![/orange3]",
            "[orange3]   I'll protect them from thieves like you![/orange3]",
        ],
        defeat_text=["[orange3]The fossils... I failed...[/orange3]"],
        victory_text=["[orange3]Ha! These caves belong to us Hikers![/orange3]"],
    ),
    "hiker_wayne": Trainer(
        id="hiker_wayne",
        name="Wayne",
        trainer_class="Hiker",
        location="Mt. Moon",
        pokemon=[
            TrainerPokemon("ZUBAT", 12),
            TrainerPokemon("GEODUDE", 11),
        ],
        prize_money=220,
        intro_text=[
            "🥾 [bold]Hiker Wayne:[/bold] [orange3]This is my territory![/orange3]",
            "[orange3]   No one passes without a battle![/orange3]",
        ],
        defeat_text=["[orange3]You're a tough one...[/orange3]"],
        victory_text=["[orange3]Rock your world![/orange3]"],
    ),
    "hiker_lenny": Trainer(
        id="hiker_lenny",
        name="Lenny",
        trainer_class="Hiker",
        location="Mt. Moon",
        pokemon=[
            TrainerPokemon("ZUBAT", 11),
            TrainerPokemon("ZUBAT", 11),
            TrainerPokemon("GEODUDE", 12),
        ],
        prize_money=240,
        intro_text=[
            "🥾 [bold]Hiker Lenny:[/bold] [orange3]Zubats everywhere in here![/orange3]",
            "[orange3]   I call them my cave guardians![/orange3]",
        ],
        defeat_text=["[orange3]Even my cave guardians fell...[/orange3]"],
        victory_text=["[orange3]Zubat swarm overwhelmed you![/orange3]"],
    ),
    # ═════════════════════════════════════════════════════════════
    # ROUTE 4 TRAINERS
    # ═════════════════════════════════════════════════════════════
    "youngster_eddie": Trainer(
        id="youngster_eddie",
        name="Eddie",
        trainer_class="Youngster",
        location="Route 4",
        pokemon=[
            TrainerPokemon("SPEAROW", 14),
            TrainerPokemon("RATTATA", 15),
        ],
        prize_money=225,
        intro_text=[
            "👦 [bold]Youngster Eddie:[/bold] [yellow]I just made it through Mt. Moon![/yellow]",
            "[yellow]   Now I'm pumped to fight![/yellow]",
        ],
        defeat_text=["[yellow]Ugh... I was so pumped too...[/yellow]"],
        victory_text=["[yellow]Cave training paid off![/yellow]"],
    ),
    "lass_dana": Trainer(
        id="lass_dana",
        name="Dana",
        trainer_class="Lass",
        location="Route 4",
        pokemon=[
            TrainerPokemon("PIDGEY", 15),
            TrainerPokemon("JIGGLYPUFF", 15),
            TrainerPokemon("MEOWTH", 14),
        ],
        prize_money=225,
        intro_text=[
            "👧 [bold]Lass Dana:[/bold] [yellow]I'm almost in Cerulean City![/yellow]",
            "[yellow]   One more battle first![/yellow]",
        ],
        defeat_text=["[yellow]So close to the city...[/yellow]"],
        victory_text=["[yellow]Almost there, just one detour![/yellow]"],
    ),
    # ═════════════════════════════════════════════════════════════
    # NUGGET BRIDGE TRAINERS (Cerulean City area)
    # ═════════════════════════════════════════════════════════════
    "nugget_trainer_1": Trainer(
        id="nugget_trainer_1",
        name="Chad",
        trainer_class="Youngster",
        location="Cerulean City",
        pokemon=[
            TrainerPokemon("EKANS", 14),
            TrainerPokemon("ZUBAT", 14),
        ],
        prize_money=210,
        intro_text=[
            "👦 [bold]Youngster Chad:[/bold] [yellow]I'm the first of five! Beat me if you can![/yellow]",
        ],
        defeat_text=["[yellow]You made it past me![/yellow]"],
        victory_text=["[yellow]You can't beat all five of us![/yellow]"],
    ),
    "nugget_trainer_2": Trainer(
        id="nugget_trainer_2",
        name="Ethan",
        trainer_class="Youngster",
        location="Cerulean City",
        pokemon=[
            TrainerPokemon("SPEAROW", 14),
            TrainerPokemon("GEODUDE", 14),
        ],
        prize_money=210,
        intro_text=[
            "👦 [bold]Youngster Ethan:[/bold] [yellow]Second challenger here! Ready?[/yellow]",
        ],
        defeat_text=["[yellow]Three more to go... good luck![/yellow]"],
        victory_text=["[yellow]Ha! Two down on you![/yellow]"],
    ),
    "nugget_trainer_3": Trainer(
        id="nugget_trainer_3",
        name="Lara",
        trainer_class="Lass",
        location="Cerulean City",
        pokemon=[
            TrainerPokemon("CLEFAIRY", 15),
            TrainerPokemon("PIDGEY", 14),
        ],
        prize_money=225,
        intro_text=[
            "👧 [bold]Lass Lara:[/bold] [yellow]Halfway there! I'm your third opponent![/yellow]",
        ],
        defeat_text=["[yellow]You're so strong! Keep going![/yellow]"],
        victory_text=["[yellow]Better turn back now![/yellow]"],
    ),
    "nugget_trainer_4": Trainer(
        id="nugget_trainer_4",
        name="Giselle",
        trainer_class="Lass",
        location="Cerulean City",
        pokemon=[
            TrainerPokemon("MEOWTH", 16),
            TrainerPokemon("CLEFAIRY", 15),
        ],
        prize_money=240,
        intro_text=[
            "👧 [bold]Lass Giselle:[/bold] [yellow]Fourth! Just one after me![/yellow]",
        ],
        defeat_text=["[yellow]You're almost there![/yellow]"],
        victory_text=["[yellow]My Meowth is unstoppable![/yellow]"],
    ),
    "nugget_trainer_5": Trainer(
        id="nugget_trainer_5",
        name="Kevin",
        trainer_class="Youngster",
        location="Cerulean City",
        pokemon=[
            TrainerPokemon("RATTATA", 16),
            TrainerPokemon("SPEAROW", 16),
            TrainerPokemon("EKANS", 15),
        ],
        prize_money=240,
        intro_text=[
            "👦 [bold]Youngster Kevin:[/bold] [yellow]Last one! The Nugget is almost yours![/yellow]",
            "[yellow]   If you can beat me![/yellow]",
        ],
        defeat_text=["[yellow]Incredible! You beat all five! Here's your Nugget![/yellow]"],
        victory_text=["[yellow]Ha! The Nugget is MINE![/yellow]"],
    ),
    # ═════════════════════════════════════════════════════════════
    # ROUTE 5 TRAINERS
    # ═════════════════════════════════════════════════════════════
    "youngster_mikey": Trainer(
        id="youngster_mikey",
        name="Mikey",
        trainer_class="Youngster",
        location="Route 5",
        pokemon=[
            TrainerPokemon("MANKEY", 15),
            TrainerPokemon("NIDORAN♂", 15),
        ],
        prize_money=225,
        intro_text=[
            "👦 [bold]Youngster Mikey:[/bold] [yellow]You better be tough if you're heading south![/yellow]",
        ],
        defeat_text=["[yellow]My Mankey never lets me down... until now...[/yellow]"],
        victory_text=["[yellow]Mankey's fury attack was too much for you![/yellow]"],
    ),
    "lass_emily": Trainer(
        id="lass_emily",
        name="Emily",
        trainer_class="Lass",
        location="Route 5",
        pokemon=[
            TrainerPokemon("NIDORAN♀", 15),
            TrainerPokemon("PIDGEY", 14),
        ],
        prize_money=210,
        intro_text=[
            "👧 [bold]Lass Emily:[/bold] [yellow]Nidoran is small, but don't underestimate her![/yellow]",
        ],
        defeat_text=["[yellow]My Nidoran tried her best...[/yellow]"],
        victory_text=["[yellow]Poison Sting got you, didn't it?[/yellow]"],
    ),
    "youngster_calvin": Trainer(
        id="youngster_calvin",
        name="Calvin",
        trainer_class="Youngster",
        location="Route 5",
        pokemon=[
            TrainerPokemon("MEOWTH", 16),
            TrainerPokemon("MANKEY", 16),
        ],
        prize_money=240,
        intro_text=[
            "👦 [bold]Youngster Calvin:[/bold] [yellow]I've been training on this route for weeks![/yellow]",
        ],
        defeat_text=["[yellow]All that training and I still lost...[/yellow]"],
        victory_text=["[yellow]Scratch and Karate Chop — unbeatable![/yellow]"],
    ),
    # ═════════════════════════════════════════════════════════════
    # ROUTE 6 TRAINERS
    # ═════════════════════════════════════════════════════════════
    "youngster_chad_r6": Trainer(
        id="youngster_chad_r6",
        name="Chad",
        trainer_class="Youngster",
        location="Route 6",
        pokemon=[
            TrainerPokemon("MANKEY", 17),
            TrainerPokemon("NIDORAN♂", 17),
        ],
        prize_money=255,
        intro_text=[
            "👦 [bold]Youngster Chad:[/bold] [yellow]The sea breeze makes me want to battle![/yellow]",
        ],
        defeat_text=["[yellow]Blown away like the sea breeze...[/yellow]"],
        victory_text=["[yellow]Fighting spirit wins every time![/yellow]"],
    ),
    "lass_shannon": Trainer(
        id="lass_shannon",
        name="Shannon",
        trainer_class="Lass",
        location="Route 6",
        pokemon=[
            TrainerPokemon("NIDORAN♀", 17),
            TrainerPokemon("MEOWTH", 16),
        ],
        prize_money=240,
        intro_text=[
            "👧 [bold]Lass Shannon:[/bold] [yellow]My Nidoran's horn is razor sharp![/yellow]",
        ],
        defeat_text=["[yellow]I almost had you with poison...[/yellow]"],
        victory_text=["[yellow]Pay Day and Poison Sting — combo![/yellow]"],
    ),
    "youngster_dale": Trainer(
        id="youngster_dale",
        name="Dale",
        trainer_class="Youngster",
        location="Route 6",
        pokemon=[
            TrainerPokemon("EKANS", 18),
            TrainerPokemon("MANKEY", 17),
        ],
        prize_money=255,
        intro_text=[
            "👦 [bold]Youngster Dale:[/bold] [yellow]Ekans can Wrap you up in seconds![/yellow]",
        ],
        defeat_text=["[yellow]You broke free before I could squeeze...[/yellow]"],
        victory_text=["[yellow]Wrapped tight! You couldn't escape![/yellow]"],
    ),
    # ═════════════════════════════════════════════════════════════
    # ROUTE 9 TRAINERS
    # ═════════════════════════════════════════════════════════════
    "youngster_dan": Trainer(
        id="youngster_dan",
        name="Dan",
        trainer_class="Youngster",
        location="Route 9",
        pokemon=[
            TrainerPokemon("SPEAROW", 19),
            TrainerPokemon("EKANS", 18),
        ],
        prize_money=270,
        intro_text=[
            "👦 [bold]Youngster Dan:[/bold] [yellow]Rocky roads call for tough Pokemon![/yellow]",
        ],
        defeat_text=["[yellow]The terrain didn't help me this time...[/yellow]"],
        victory_text=["[yellow]Spearow's Fury Attack tore you apart![/yellow]"],
    ),
    "youngster_kent": Trainer(
        id="youngster_kent",
        name="Kent",
        trainer_class="Youngster",
        location="Route 9",
        pokemon=[
            TrainerPokemon("NIDORAN♂", 20),
            TrainerPokemon("SPEAROW", 19),
        ],
        prize_money=285,
        intro_text=[
            "👦 [bold]Youngster Kent:[/bold] [yellow]I'm heading to Rock Tunnel — fight me first![/yellow]",
        ],
        defeat_text=["[yellow]Guess I'm not ready for Rock Tunnel either...[/yellow]"],
        victory_text=["[yellow]One more victory before the tunnel![/yellow]"],
    ),
    "hiker_alan_r9": Trainer(
        id="hiker_alan_r9",
        name="Alan",
        trainer_class="Hiker",
        location="Route 9",
        pokemon=[
            TrainerPokemon("GEODUDE", 19),
            TrainerPokemon("ONIX", 18),
        ],
        prize_money=380,
        intro_text=[
            "🥾 [bold]Hiker Alan:[/bold] [orange3]The rocks here are perfect for training![/orange3]",
            "[orange3]   My Geodude and I are inseparable![/orange3]",
        ],
        defeat_text=["[orange3]You rock harder than my Geodude![/orange3]"],
        victory_text=["[orange3]Rock solid! Nothing gets past us![/orange3]"],
    ),
    # ═════════════════════════════════════════════════════════════
    # ROUTE 10 TRAINERS
    # ═════════════════════════════════════════════════════════════
    "youngster_curt": Trainer(
        id="youngster_curt",
        name="Curt",
        trainer_class="Youngster",
        location="Route 10",
        pokemon=[
            TrainerPokemon("VOLTORB", 21),
            TrainerPokemon("MAGNEMITE", 20),
        ],
        prize_money=300,
        intro_text=[
            "👦 [bold]Youngster Curt:[/bold] [yellow]The Power Plant inspires me — Electric-types only![/yellow]",
        ],
        defeat_text=["[yellow]Short-circuited again...[/yellow]"],
        victory_text=["[yellow]BOOM! Voltorb's Selfdestruct![/yellow]"],
    ),
    "hiker_tim": Trainer(
        id="hiker_tim",
        name="Tim",
        trainer_class="Hiker",
        location="Route 10",
        pokemon=[
            TrainerPokemon("GEODUDE", 21),
            TrainerPokemon("GRAVELER", 20),
        ],
        prize_money=420,
        intro_text=[
            "🥾 [bold]Hiker Tim:[/bold] [orange3]Graveler and I have climbed every mountain on this route![/orange3]",
        ],
        defeat_text=["[orange3]You rolled right over my Graveler...[/orange3]"],
        victory_text=["[orange3]Rollout! Unstoppable![/orange3]"],
    ),
    # ═════════════════════════════════════════════════════════════
    # ROUTE 11 TRAINERS
    # ═════════════════════════════════════════════════════════════
    "youngster_sam_r11": Trainer(
        id="youngster_sam_r11",
        name="Sam",
        trainer_class="Youngster",
        location="Route 11",
        pokemon=[
            TrainerPokemon("EKANS", 21),
            TrainerPokemon("SPEAROW", 20),
        ],
        prize_money=300,
        intro_text=[
            "👦 [bold]Youngster Sam:[/bold] [yellow]I've been training east of Vermillion — battle me![/yellow]",
        ],
        defeat_text=["[yellow]My snake and bird couldn't stop you...[/yellow]"],
        victory_text=["[yellow]Wrap and Fury Attack — deadly combo![/yellow]"],
    ),
    "lass_iris": Trainer(
        id="lass_iris",
        name="Iris",
        trainer_class="Lass",
        location="Route 11",
        pokemon=[
            TrainerPokemon("EKANS", 20),
            TrainerPokemon("DROWZEE", 19),
        ],
        prize_money=285,
        intro_text=[
            "👧 [bold]Lass Iris:[/bold] [yellow]Drowzee will put you to sleep before you know it![/yellow]",
        ],
        defeat_text=["[yellow]My sweet dreams turned into a nightmare...[/yellow]"],
        victory_text=["[yellow]Hypnosis worked! Sleep tight![/yellow]"],
    ),
    "youngster_tom_r11": Trainer(
        id="youngster_tom_r11",
        name="Tom",
        trainer_class="Youngster",
        location="Route 11",
        pokemon=[
            TrainerPokemon("KOFFING", 21),
            TrainerPokemon("SPEAROW", 21),
            TrainerPokemon("EKANS", 20),
        ],
        prize_money=315,
        intro_text=[
            "👦 [bold]Youngster Tom:[/bold] [yellow]Koffing's poison cloud will choke you out![/yellow]",
        ],
        defeat_text=["[yellow]The cloud dissipated before I could win...[/yellow]"],
        victory_text=["[yellow]Smokescreen plus Sludge — what a combo![/yellow]"],
    ),
    # ═════════════════════════════════════════════════════════════
    # ROCK TUNNEL TRAINERS
    # ═════════════════════════════════════════════════════════════
    "hiker_allen": Trainer(
        id="hiker_allen",
        name="Allen",
        trainer_class="Hiker",
        location="Rock Tunnel",
        pokemon=[
            TrainerPokemon("GEODUDE", 22),
            TrainerPokemon("MACHOP", 22),
        ],
        prize_money=440,
        intro_text=[
            "🥾 [bold]Hiker Allen:[/bold] [orange3]You dare enter my tunnel without Flash?[/orange3]",
            "[orange3]   You'll regret it![/orange3]",
        ],
        defeat_text=["[orange3]Even in the dark you found a way...[/orange3]"],
        victory_text=["[orange3]Rock Throw! You can't see a thing![/orange3]"],
    ),
    "hiker_jake": Trainer(
        id="hiker_jake",
        name="Jake",
        trainer_class="Hiker",
        location="Rock Tunnel",
        pokemon=[
            TrainerPokemon("ZUBAT", 21),
            TrainerPokemon("GEODUDE", 22),
            TrainerPokemon("ONIX", 20),
        ],
        prize_money=460,
        intro_text=[
            "🥾 [bold]Hiker Jake:[/bold] [orange3]Zubat, Geodude, Onix — I have it all![/orange3]",
            "[orange3]   This tunnel is my domain![/orange3]",
        ],
        defeat_text=["[orange3]Incredible... in the pitch black too![/orange3]"],
        victory_text=["[orange3]Three against one — you never stood a chance![/orange3]"],
    ),
    "hiker_diana": Trainer(
        id="hiker_diana",
        name="Diana",
        trainer_class="Hiker",
        location="Rock Tunnel",
        pokemon=[
            TrainerPokemon("GEODUDE", 23),
            TrainerPokemon("GEODUDE", 23),
            TrainerPokemon("GRAVELER", 22),
        ],
        prize_money=460,
        intro_text=[
            "🥾 [bold]Hiker Diana:[/bold] [orange3]Rock-types rule the tunnel![/orange3]",
            "[orange3]   Three of my best will bury you![/orange3]",
        ],
        defeat_text=["[orange3]You chipped away at all three of my rocks...[/orange3]"],
        victory_text=["[orange3]Magnitude! The whole tunnel shook![/orange3]"],
    ),
    "hiker_rugged": Trainer(
        id="hiker_rugged",
        name="Rugged",
        trainer_class="Hiker",
        location="Rock Tunnel",
        pokemon=[
            TrainerPokemon("MACHOP", 22),
            TrainerPokemon("GEODUDE", 22),
            TrainerPokemon("ONIX", 21),
        ],
        prize_money=460,
        intro_text=[
            "🥾 [bold]Hiker Rugged:[/bold] [orange3]I've lived in this tunnel for years![/orange3]",
            "[orange3]   No one passes without earning it![/orange3]",
        ],
        defeat_text=["[orange3]You've earned your passage through my tunnel.[/orange3]"],
        victory_text=["[orange3]Seismic Toss from Machop! You felt that![/orange3]"],
    ),
    "youngster_josh_rt": Trainer(
        id="youngster_josh_rt",
        name="Josh",
        trainer_class="Youngster",
        location="Rock Tunnel",
        pokemon=[
            TrainerPokemon("ZUBAT", 22),
            TrainerPokemon("EKANS", 21),
        ],
        prize_money=315,
        intro_text=[
            "👦 [bold]Youngster Josh:[/bold] [yellow]Lost in here... might as well battle![/yellow]",
        ],
        defeat_text=["[yellow]Now I'm even more lost...[/yellow]"],
        victory_text=["[yellow]Leech Life in the darkness — spooky![/yellow]"],
    ),
    # ═════════════════════════════════════════════════════════════
    # VERMILLION CITY GYM TRAINERS
    # ═════════════════════════════════════════════════════════════
    "gym_trainer_vermillion_sailor_1": Trainer(
        id="gym_trainer_vermillion_sailor_1",
        name="Dirk",
        trainer_class="Sailor",
        location="Vermillion City",
        pokemon=[
            TrainerPokemon(species="TENTACOOL", level=20),
            TrainerPokemon(species="PIKACHU", level=20),
        ],
        prize_money=500,
        intro_text=[
            "⚓ [bold]Sailor Dirk:[/bold] [yellow]You think you can challenge Lt. Surge?[/yellow]",
            "[yellow]   You'll have to get past me first, landlubber![/yellow]",
        ],
        defeat_text=["[yellow]Man overboard! I've been defeated![/yellow]"],
        victory_text=["[yellow]Shiver me timbers — you weren't ready for this![/yellow]"],
    ),
    "gym_trainer_vermillion_sailor_2": Trainer(
        id="gym_trainer_vermillion_sailor_2",
        name="Huey",
        trainer_class="Sailor",
        location="Vermillion City",
        pokemon=[
            TrainerPokemon(species="VOLTORB", level=19),
            TrainerPokemon(species="VOLTORB", level=19),
            TrainerPokemon(species="PIKACHU", level=21),
        ],
        prize_money=525,
        intro_text=[
            "⚓ [bold]Sailor Huey:[/bold] [yellow]Electric Pokemon saved the Lieutenant during the war![/yellow]",
            "[yellow]   Show some respect and battle me![/yellow]",
        ],
        defeat_text=["[yellow]The circuits are blown... I've been beaten![/yellow]"],
        victory_text=["[yellow]Static shock! You never saw it coming![/yellow]"],
    ),
    # ═════════════════════════════════════════════════════════════
    # ROUTE 7 TRAINERS (Celadon ↔ Saffron)
    # ═════════════════════════════════════════════════════════════
    "lass_ali_r7": Trainer(
        id="lass_ali_r7",
        name="Ali",
        trainer_class="Lass",
        location="Route 7",
        pokemon=[
            TrainerPokemon("PIDGEY", 23),
            TrainerPokemon("PIDGEOTTO", 22),
        ],
        prize_money=330,
        intro_text=[
            "👧 [bold]Lass Ali:[/bold] [yellow]This path is my territory![/yellow]",
            "[yellow]   Try getting past my birds![/yellow]",
        ],
        defeat_text=["[yellow]My Pidgey family lost to you...[/yellow]"],
        victory_text=["[yellow]Wing Attack! You couldn't dodge it![/yellow]"],
    ),
    "youngster_mike_r7": Trainer(
        id="youngster_mike_r7",
        name="Mike",
        trainer_class="Youngster",
        location="Route 7",
        pokemon=[
            TrainerPokemon("DROWZEE", 22),
            TrainerPokemon("SLOWPOKE", 22),
        ],
        prize_money=330,
        intro_text=[
            "👦 [bold]Youngster Mike:[/bold] [yellow]My Drowzee will put you to sleep before you can fight![/yellow]",
        ],
        defeat_text=["[yellow]I couldn't even make you drowsy...[/yellow]"],
        victory_text=["[yellow]Hypnosis! You're out cold![/yellow]"],
    ),
    "gambler_ricky": Trainer(
        id="gambler_ricky",
        name="Ricky",
        trainer_class="Gambler",
        location="Route 7",
        pokemon=[
            TrainerPokemon("SLOWPOKE", 25),
            TrainerPokemon("DROWZEE", 24),
        ],
        prize_money=875,
        intro_text=[
            "🎲 [bold]Gambler Ricky:[/bold] [magenta]I'll bet on my Psychic Pokemon to win![/magenta]",
            "[magenta]   Care to test your luck?[/magenta]",
        ],
        defeat_text=["[magenta]I wagered everything on this battle... and lost![/magenta]"],
        victory_text=["[magenta]The odds were in my favour! Better luck next time![/magenta]"],
    ),
    # ═════════════════════════════════════════════════════════════
    # ROUTE 8 TRAINERS (Saffron ↔ Lavender)
    # ═════════════════════════════════════════════════════════════
    "biker_rudy": Trainer(
        id="biker_rudy",
        name="Rudy",
        trainer_class="Biker",
        location="Route 8",
        pokemon=[
            TrainerPokemon("KOFFING", 24),
            TrainerPokemon("KOFFING", 24),
        ],
        prize_money=480,
        intro_text=[
            "🏍️ [bold]Biker Rudy:[/bold] [purple]Rev it up! Koffing will gas you out![/purple]",
        ],
        defeat_text=["[purple]The exhaust fumes weren't enough![/purple]"],
        victory_text=["[purple]Smog cloud incoming — breathe it in![/purple]"],
    ),
    "biker_alex": Trainer(
        id="biker_alex",
        name="Alex",
        trainer_class="Biker",
        location="Route 8",
        pokemon=[
            TrainerPokemon("GRIMER", 23),
            TrainerPokemon("MUK", 25),
        ],
        prize_money=500,
        intro_text=[
            "🏍️ [bold]Biker Alex:[/bold] [purple]You're blocking the road, kid — battle me![/purple]",
        ],
        defeat_text=["[purple]You smashed right through my Poison-types...[/purple]"],
        victory_text=["[purple]Sludge Bomb! Get covered in gunk![/purple]"],
    ),
    "lass_tina_r8": Trainer(
        id="lass_tina_r8",
        name="Tina",
        trainer_class="Lass",
        location="Route 8",
        pokemon=[
            TrainerPokemon("MEOWTH", 24),
            TrainerPokemon("PERSIAN", 25),
        ],
        prize_money=375,
        intro_text=[
            "👧 [bold]Lass Tina:[/bold] [yellow]Persian is the most elegant Pokemon around![/yellow]",
            "[yellow]   Don't you dare insult it by losing easily![/yellow]",
        ],
        defeat_text=["[yellow]How dare you scratch up my Persian![/yellow]"],
        victory_text=["[yellow]Slash! All finesse, no effort![/yellow]"],
    ),
    # ═════════════════════════════════════════════════════════════
    # ROUTE 12 TRAINERS (South of Lavender Town, Fishing spot)
    # ═════════════════════════════════════════════════════════════
    "fisherman_wade": Trainer(
        id="fisherman_wade",
        name="Wade",
        trainer_class="Fisherman",
        location="Route 12",
        pokemon=[
            TrainerPokemon("MAGIKARP", 20),
            TrainerPokemon("MAGIKARP", 20),
            TrainerPokemon("MAGIKARP", 20),
            TrainerPokemon("MAGIKARP", 20),
        ],
        prize_money=400,
        intro_text=[
            "🎣 [bold]Fisherman Wade:[/bold] [blue]Grr! You interrupted my fishing![/blue]",
            "[blue]   I'll make you pay for that![/blue]",
        ],
        defeat_text=["[blue]My Magikarp... they just flapped around uselessly...[/blue]"],
        victory_text=["[blue]Splash! Splash! The most fearsome attack![/blue]"],
    ),
    "fisherman_henry": Trainer(
        id="fisherman_henry",
        name="Henry",
        trainer_class="Fisherman",
        location="Route 12",
        pokemon=[
            TrainerPokemon("GOLDEEN", 22),
            TrainerPokemon("SEAKING", 23),
        ],
        prize_money=460,
        intro_text=[
            "🎣 [bold]Fisherman Henry:[/bold] [blue]The waters here are full of strong Pokemon![/blue]",
            "[blue]   My fish will shred you with Horn Drill![/blue]",
        ],
        defeat_text=["[blue]The current swept away my strength...[/blue]"],
        victory_text=["[blue]Horn Drill! One hit KO! You're done![/blue]"],
    ),
    "fisherman_dale": Trainer(
        id="fisherman_dale",
        name="Dale",
        trainer_class="Fisherman",
        location="Route 12",
        pokemon=[
            TrainerPokemon("TENTACOOL", 22),
            TrainerPokemon("TENTACRUEL", 24),
        ],
        prize_money=480,
        intro_text=[
            "🎣 [bold]Fisherman Dale:[/bold] [blue]Tentacruel — that's a Pokemon that means business![/blue]",
        ],
        defeat_text=["[blue]The jellyfish got tangled up...[/blue]"],
        victory_text=["[blue]Wrap and Poison — a deadly combo from the deep![/blue]"],
    ),
    # ═════════════════════════════════════════════════════════════
    # POKEMON TOWER TRAINERS (Lavender Town)
    # ═════════════════════════════════════════════════════════════
    "channeler_jody": Trainer(
        id="channeler_jody",
        name="Jody",
        trainer_class="Channeler",
        location="Pokemon Tower",
        pokemon=[
            TrainerPokemon("GASTLY", 22),
        ],
        prize_money=660,
        intro_text=[
            "👻 [bold]Channeler Jody:[/bold] [dim white]The spirits... they cry out![/dim white]",
            "[dim white]   They will not let you pass![/dim white]",
        ],
        defeat_text=["[dim white]The spirits have abandoned me...[/dim white]"],
        victory_text=["[dim white]Lick! A ghostly touch that chills the soul![/dim white]"],
    ),
    "channeler_ruth": Trainer(
        id="channeler_ruth",
        name="Ruth",
        trainer_class="Channeler",
        location="Pokemon Tower",
        pokemon=[
            TrainerPokemon("GASTLY", 23),
            TrainerPokemon("HAUNTER", 22),
        ],
        prize_money=690,
        intro_text=[
            "👻 [bold]Channeler Ruth:[/bold] [dim white]I hear the voices of the departed...[/dim white]",
            "[dim white]   They say: do not disturb this tower![/dim white]",
        ],
        defeat_text=["[dim white]The spirits grow silent around me...[/dim white]"],
        victory_text=["[dim white]Night Shade! The darkness swallows you whole![/dim white]"],
    ),
    "channeler_karina": Trainer(
        id="channeler_karina",
        name="Karina",
        trainer_class="Channeler",
        location="Pokemon Tower",
        pokemon=[
            TrainerPokemon("HAUNTER", 24),
            TrainerPokemon("HAUNTER", 24),
        ],
        prize_money=720,
        intro_text=[
            "👻 [bold]Channeler Karina:[/bold] [dim white]Leave now... while you still can.[/dim white]",
            "[dim white]   The spirits of this tower will curse you![/dim white]",
        ],
        defeat_text=["[dim white]My Haunters... fading back into the shadows...[/dim white]"],
        victory_text=["[dim white]Confuse Ray — your mind shatters in the darkness![/dim white]"],
    ),
    # ═════════════════════════════════════════════════════════════
    # CERULEAN CITY GYM TRAINERS
    # ═════════════════════════════════════════════════════════════
    "gym_trainer_cerulean_swimmer": Trainer(
        id="gym_trainer_cerulean_swimmer",
        name="Grace",
        trainer_class="Swimmer",
        location="Cerulean City",
        pokemon=[
            TrainerPokemon("HORSEA", 18),
            TrainerPokemon("GOLDEEN", 17),
        ],
        prize_money=340,
        intro_text=[
            "🏊 [bold]Swimmer Grace:[/bold] [blue]You'll need to get past me first![/blue]",
            "[blue]   Water Pokemon are nature's perfection![/blue]",
        ],
        defeat_text=["[blue]Washed out...[/blue]"],
        victory_text=["[blue]Sink or swim — and you sank![/blue]"],
    ),
    # ═════════════════════════════════════════════════════════════
    # PEWTER CITY GYM TRAINERS
    # ═════════════════════════════════════════════════════════════
    "gym_trainer_pewter_hiker": Trainer(
        id="gym_trainer_pewter_hiker",
        name="Marc",
        trainer_class="Hiker",
        location="Pewter City",
        pokemon=[
            TrainerPokemon(species="GEODUDE", level=10),
            TrainerPokemon(species="GEODUDE", level=10),
        ],
        prize_money=200,
        intro_text=[
            "🥾 [bold]Hiker Marc:[/bold] [orange3]Hey! You can't just walk past me![/orange3]",
            "[orange3]   Rock-type Pokemon are the toughest![/orange3]",
            "[orange3]   Prove your worth before facing the Gym Leader![/orange3]",
        ],
        defeat_text=[
            "[orange3]My Geodude...[/orange3]",
            "[orange3]   You're stronger than I thought.[/orange3]",
            "[orange3]   Maybe you can handle Brock after all...[/orange3]",
        ],
        victory_text=[
            "[orange3]Rock SMASH! You couldn't break through![/orange3]",
        ],
    ),
    "gym_trainer_pewter_youngster": Trainer(
        id="gym_trainer_pewter_youngster",
        name="Tommy",
        trainer_class="Youngster",
        location="Pewter City",
        pokemon=[
            TrainerPokemon(species="SANDSHREW", level=11),
        ],
        prize_money=165,
        intro_text=[
            "👦 [bold]Youngster Tommy:[/bold] [orange3]Stop right there![/orange3]",
            "[orange3]   I'm training here to beat Brock someday too![/orange3]",
            "[orange3]   But first, let's see what you can do![/orange3]",
        ],
        defeat_text=[
            "[orange3]Aww... my Sandshrew...[/orange3]",
            "[orange3]   You're really good! Brock won't know what hit him![/orange3]",
        ],
        victory_text=[
            "[orange3]Yeah! Sandshrew won![/orange3]",
            "[orange3]   Go train more before you face Brock![/orange3]",
        ],
    ),
    # ═════════════════════════════════════════════════════════════
    # GYM LEADERS
    # ═════════════════════════════════════════════════════════════
    # ===== Pewter City Gym - Brock (Rock-type) =====
    "gym_leader_brock": Trainer(
        id="gym_leader_brock",
        name="Brock",
        trainer_class="Gym Leader",
        location="Pewter City",
        pokemon=[
            TrainerPokemon(species="GEODUDE", level=12),
            TrainerPokemon(species="ONIX", level=14),
        ],
        prize_money=1400,
        intro_text=[
            "⭐ [bold]Gym Leader Brock:[/bold] [orange3]I'm Brock! I'm Pewter's Gym Leader![/orange3]",
            "[orange3]   My rock-hard willpower is evident in my Pokemon![/orange3]",
            "[orange3]   My Pokemon are all rock-hard, and have true grit![/orange3]",
            "[orange3]   Do you still want to challenge me?[/orange3]",
            "",
            "[bold yellow]⚔️  GYM BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=[
            "[orange3]I took you for granted.[/orange3]",
            "[orange3]   As proof of your victory, here's the Boulder Badge![/orange3]",
        ],
        victory_text=[
            "[orange3]My rock-hard Pokemon![/orange3]",
            "[orange3]   You couldn't beat them after all![/orange3]",
        ],
        badge_reward="Boulder Badge",
        badge_id="boulder_badge",
        preferred_types=["Rock", "Ground"],
    ),
    # ===== Cerulean City Gym - Misty (Water-type) =====
    "gym_leader_misty": Trainer(
        id="gym_leader_misty",
        name="Misty",
        trainer_class="Gym Leader",
        location="Cerulean City",
        pokemon=[
            TrainerPokemon(species="STARYU", level=18),
            TrainerPokemon(species="STARMIE", level=21),
        ],
        prize_money=2100,
        intro_text=[
            "⭐ [bold]Gym Leader Misty:[/bold] [blue]Hi, you're a new face![/blue]",
            "[blue]   I'm Misty, the Cerulean City Gym Leader![/blue]",
            "[blue]   I'm a Water Pokemon specialist![/blue]",
            "[blue]   My policy is an all-out offensive with Water Pokemon![/blue]",
            "",
            "[bold yellow]⚔️  GYM BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=[
            "[blue]Wow! You're too much![/blue]",
            "[blue]   All right! You can have the Cascade Badge![/blue]",
        ],
        victory_text=[
            "[blue]That was a close one![/blue]",
            "[blue]   Come back after training more![/blue]",
        ],
        badge_reward="Cascade Badge",
        badge_id="cascade_badge",
        preferred_types=["Water"],
    ),
    # ===== Vermillion City Gym - Lt. Surge (Electric-type) =====
    "gym_leader_lt_surge": Trainer(
        id="gym_leader_lt_surge",
        name="Lt. Surge",
        trainer_class="Gym Leader",
        location="Vermillion City",
        pokemon=[
            TrainerPokemon(species="VOLTORB", level=21),
            TrainerPokemon(species="PIKACHU", level=18),
            TrainerPokemon(species="ELECTRODE", level=23),
            TrainerPokemon(species="RAICHU", level=24),
        ],
        prize_money=2400,
        intro_text=[
            "⭐ [bold]Gym Leader Lt. Surge:[/bold] [yellow]Hey, kid! What do you think you're doing here?[/yellow]",
            "[yellow]   You won't live long in combat![/yellow]",
            "[yellow]   That's for sure![/yellow]",
            "[yellow]   I tell you kid, electric Pokemon saved me during the war![/yellow]",
            "[yellow]   They zapped my enemies into paralysis![/yellow]",
            "",
            "[bold yellow]⚔️  GYM BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=[
            "[yellow]Whoa! You're the real deal, kid![/yellow]",
            "[yellow]   Fine then, take the Thunder Badge![/yellow]",
        ],
        victory_text=[
            "[yellow]Hahaha! That was a shocking development![/yellow]",
            "[yellow]   Come back when you've toughened up![/yellow]",
        ],
        badge_reward="Thunder Badge",
        badge_id="thunder_badge",
        preferred_types=["Electric"],
    ),
    # ===== Celadon City Gym - Erika (Grass-type) =====
    "gym_leader_erika": Trainer(
        id="gym_leader_erika",
        name="Erika",
        trainer_class="Gym Leader",
        location="Celadon City",
        pokemon=[
            TrainerPokemon(species="VICTREEBEL", level=29),
            TrainerPokemon(species="TANGELA", level=24),
            TrainerPokemon(species="VILEPLUME", level=29),
        ],
        prize_money=2900,
        intro_text=[
            "⭐ [bold]Gym Leader Erika:[/bold] [green]Hello...[/green]",
            "[green]   Lovely weather, isn't it?[/green]",
            "[green]   It's so pleasant...[/green]",
            "[green]   ...I'm afraid I may doze off.[/green]",
            "[green]   My Pokemon are all Grass-type.[/green]",
            "",
            "[bold yellow]⚔️  GYM BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=[
            "[green]Oh! I concede defeat.[/green]",
            "[green]   You are remarkably strong.[/green]",
            "[green]   I must confer you the Rainbow Badge.[/green]",
        ],
        victory_text=[
            "[green]That was a foolish move.[/green]",
            "[green]   Come back when you're more prepared.[/green]",
        ],
        badge_reward="Rainbow Badge",
        badge_id="rainbow_badge",
        preferred_types=["Grass", "Poison"],
    ),
    # ===== Fuchsia City Gym - Koga (Poison-type) =====
    "gym_leader_koga": Trainer(
        id="gym_leader_koga",
        name="Koga",
        trainer_class="Gym Leader",
        location="Fuchsia City",
        pokemon=[
            TrainerPokemon(species="KOFFING", level=37),
            TrainerPokemon(species="MUK", level=39),
            TrainerPokemon(species="KOFFING", level=37),
            TrainerPokemon(species="WEEZING", level=43),
        ],
        prize_money=4300,
        intro_text=[
            "⭐ [bold]Gym Leader Koga:[/bold] [purple]Fwahahaha![/purple]",
            "[purple]   A mere child like you dares to challenge me?[/purple]",
            "[purple]   Very well, I shall show you true terror![/purple]",
            "[purple]   You shall learn respect for your elders![/purple]",
            "[purple]   I am the master of Poison-type Pokemon![/purple]",
            "",
            "[bold yellow]⚔️  GYM BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=[
            "[purple]Humph! You have proven your worth![/purple]",
            "[purple]   Here! Take the Soul Badge![/purple]",
        ],
        victory_text=[
            "[purple]Fwahahaha! Poison brings steady doom![/purple]",
            "[purple]   Sleep on it, youngster![/purple]",
        ],
        badge_reward="Soul Badge",
        badge_id="soul_badge",
        preferred_types=["Poison"],
    ),
    # ===== Saffron City Gym - Sabrina (Psychic-type) =====
    "gym_leader_sabrina": Trainer(
        id="gym_leader_sabrina",
        name="Sabrina",
        trainer_class="Gym Leader",
        location="Saffron City",
        pokemon=[
            TrainerPokemon(species="KADABRA", level=38),
            TrainerPokemon(species="MR_MIME", level=37),
            TrainerPokemon(species="VENOMOTH", level=38),
            TrainerPokemon(species="ALAKAZAM", level=43),
        ],
        prize_money=4300,
        intro_text=[
            "⭐ [bold]Gym Leader Sabrina:[/bold] [magenta]I had a vision of your arrival.[/magenta]",
            "[magenta]   I have had Psychic powers since I was a child.[/magenta]",
            "[magenta]   I first learned to bend spoons with my mind.[/magenta]",
            "[magenta]   I dislike fighting, but if you wish...[/magenta]",
            "[magenta]   I will show you my powers![/magenta]",
            "",
            "[bold yellow]⚔️  GYM BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=[
            "[magenta]I'm shocked! But a loss is a loss.[/magenta]",
            "[magenta]   I admit I didn't work hard enough.[/magenta]",
            "[magenta]   You earned the Marsh Badge.[/magenta]",
        ],
        victory_text=[
            "[magenta]I foresaw your loss.[/magenta]",
            "[magenta]   Train your mind and body.[/magenta]",
        ],
        badge_reward="Marsh Badge",
        badge_id="marsh_badge",
        preferred_types=["Psychic"],
    ),
    # ===== Cinnabar Island Gym - Blaine (Fire-type) =====
    "gym_leader_blaine": Trainer(
        id="gym_leader_blaine",
        name="Blaine",
        trainer_class="Gym Leader",
        location="Cinnabar Island",
        pokemon=[
            TrainerPokemon(species="GROWLITHE", level=42),
            TrainerPokemon(species="PONYTA", level=40),
            TrainerPokemon(species="RAPIDASH", level=42),
            TrainerPokemon(species="ARCANINE", level=47),
        ],
        prize_money=4700,
        intro_text=[
            "⭐ [bold]Gym Leader Blaine:[/bold] [red]Hah! I'm Blaine![/red]",
            "[red]   I am the Leader of Cinnabar Gym![/red]",
            "[red]   My fiery Pokemon will incinerate all challengers![/red]",
            "[red]   Hah! You better have Burn Heal![/red]",
            "",
            "[bold yellow]⚔️  GYM BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=[
            "[red]I have burned out![/red]",
            "[red]   You have earned the Volcano Badge![/red]",
        ],
        victory_text=[
            "[red]Hahahaha! Burned![/red]",
            "[red]   Return when you can withstand the heat![/red]",
        ],
        badge_reward="Volcano Badge",
        badge_id="volcano_badge",
        preferred_types=["Fire"],
    ),
    # ===== Viridian City Gym - Giovanni (Ground-type) =====
    "gym_leader_giovanni": Trainer(
        id="gym_leader_giovanni",
        name="Giovanni",
        trainer_class="Gym Leader",
        location="Viridian City",
        pokemon=[
            TrainerPokemon(species="RHYHORN", level=45),
            TrainerPokemon(species="DUGTRIO", level=42),
            TrainerPokemon(species="NIDOQUEEN", level=44),
            TrainerPokemon(species="NIDOKING", level=45),
            TrainerPokemon(species="RHYDON", level=50),
        ],
        prize_money=5000,
        intro_text=[
            "⭐ [bold]Gym Leader Giovanni:[/bold] [brown]Welcome to Viridian Gym.[/brown]",
            "[brown]   I am Giovanni, the Gym Leader![/brown]",
            "[brown]   I have been waiting for a serious challenger![/brown]",
            "[brown]   This will be the ultimate test![/brown]",
            "[brown]   Prove your worth![/brown]",
            "",
            "[bold yellow]⚔️  GYM BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=[
            "[brown]Ha! That was a truly intense fight![/brown]",
            "[brown]   You have proven your mastery.[/brown]",
            "[brown]   Here is the Earth Badge! You've earned it![/brown]",
        ],
        victory_text=[
            "[brown]As I expected.[/brown]",
            "[brown]   Return when you have 7 badges.[/brown]",
        ],
        badge_reward="Earth Badge",
        badge_id="earth_badge",
        preferred_types=["Ground"],
    ),
    # ═════════════════════════════════════════════════════════════
    # S.S. ANNE TRAINERS
    # ═════════════════════════════════════════════════════════════
    "sailor_jeff": Trainer(
        id="sailor_jeff",
        name="Jeff",
        trainer_class="Sailor",
        location="S.S. Anne",
        pokemon=[
            TrainerPokemon("TENTACOOL", 22),
            TrainerPokemon("SHELLDER", 23),
        ],
        prize_money=460,
        intro_text=[
            "⚓ [bold]Sailor Jeff:[/bold] [blue]Ahoy! This is a luxury liner, not a playground![/blue]",
            "[blue]   Prove yourself or walk the plank![/blue]",
        ],
        defeat_text=["[blue]You fight like a real sailor![/blue]"],
        victory_text=["[blue]I've crossed every sea — you won't get past me![/blue]"],
    ),
    "sailor_ron": Trainer(
        id="sailor_ron",
        name="Ron",
        trainer_class="Sailor",
        location="S.S. Anne",
        pokemon=[
            TrainerPokemon("MACHOP", 22),
            TrainerPokemon("TENTACOOL", 21),
        ],
        prize_money=440,
        intro_text=[
            "⚓ [bold]Sailor Ron:[/bold] [blue]I guard this corridor![/blue]",
            "[blue]   No one gets past without a fight![/blue]",
        ],
        defeat_text=["[blue]Knocked overboard by your skill...[/blue]"],
        victory_text=["[blue]Machop muscles win every time![/blue]"],
    ),
    "sailor_huey": Trainer(
        id="sailor_huey",
        name="Huey",
        trainer_class="Sailor",
        location="S.S. Anne",
        pokemon=[
            TrainerPokemon("SHELLDER", 24),
            TrainerPokemon("MACHOP", 23),
            TrainerPokemon("TENTACOOL", 22),
        ],
        prize_money=480,
        intro_text=[
            "⚓ [bold]Sailor Huey:[/bold] [blue]The captain's cabin is off limits![/blue]",
            "[blue]   I'll keep you busy down here![/blue]",
        ],
        defeat_text=["[blue]The captain will hear of this...[/blue]"],
        victory_text=["[blue]Tri-team combo — unbeatable![/blue]"],
    ),
    "jr_trainer_m_jack": Trainer(
        id="jr_trainer_m_jack",
        name="Jack",
        trainer_class="Jr. Trainer♂",
        location="S.S. Anne",
        pokemon=[
            TrainerPokemon("EKANS", 23),
            TrainerPokemon("SANDSHREW", 23),
        ],
        prize_money=414,
        intro_text=[
            "👦 [bold]Jr. Trainer Jack:[/bold] [yellow]I came on this cruise to battle![/yellow]",
            "[yellow]   Let's go![/yellow]",
        ],
        defeat_text=["[yellow]This trip is getting expensive...[/yellow]"],
        victory_text=["[yellow]I'm going pro after this voyage![/yellow]"],
    ),
    "jr_trainer_f_gail": Trainer(
        id="jr_trainer_f_gail",
        name="Gail",
        trainer_class="Jr. Trainer♀",
        location="S.S. Anne",
        pokemon=[
            TrainerPokemon("RATTATA", 22),
            TrainerPokemon("NIDORAN♀", 23),
            TrainerPokemon("PIDGEY", 22),
        ],
        prize_money=414,
        intro_text=[
            "👧 [bold]Jr. Trainer Gail:[/bold] [yellow]I love ocean battles![/yellow]",
            "[yellow]   The rolling waves inspire me![/yellow]",
        ],
        defeat_text=["[yellow]The sea doesn't care about my losses...[/yellow]"],
        victory_text=["[yellow]Seasickness won't slow me down![/yellow]"],
    ),
    "jr_trainer_m_ryan": Trainer(
        id="jr_trainer_m_ryan",
        name="Ryan",
        trainer_class="Jr. Trainer♂",
        location="S.S. Anne",
        pokemon=[
            TrainerPokemon("SPEAROW", 24),
            TrainerPokemon("MACHOP", 23),
        ],
        prize_money=432,
        intro_text=[
            "👦 [bold]Jr. Trainer Ryan:[/bold] [yellow]The captain said to keep order on deck![/yellow]",
            "[yellow]   That means stopping you![/yellow]",
        ],
        defeat_text=["[yellow]So much for keeping order...[/yellow]"],
        victory_text=["[yellow]Deck cleared![/yellow]"],
    ),
    "jr_trainer_f_fiona": Trainer(
        id="jr_trainer_f_fiona",
        name="Fiona",
        trainer_class="Jr. Trainer♀",
        location="S.S. Anne",
        pokemon=[
            TrainerPokemon("JIGGLYPUFF", 24),
            TrainerPokemon("MEOWTH", 24),
        ],
        prize_money=432,
        intro_text=[
            "👧 [bold]Jr. Trainer Fiona:[/bold] [yellow]This ship has the best training rooms![/yellow]",
            "[yellow]   I've been here all voyage![/yellow]",
        ],
        defeat_text=["[yellow]Maybe I need more sea air...[/yellow]"],
        victory_text=["[yellow]Jigglypuff's Sing lulled you right to sleep![/yellow]"],
    ),
    "sailor_dale_ss": Trainer(
        id="sailor_dale_ss",
        name="Dale",
        trainer_class="Sailor",
        location="S.S. Anne",
        pokemon=[
            TrainerPokemon("POLIWAG", 25),
            TrainerPokemon("TENTACRUEL", 24),
        ],
        prize_money=500,
        intro_text=[
            "⚓ [bold]Sailor Dale:[/bold] [blue]This is the last corridor before the captain![/blue]",
            "[blue]   You'll have to go through me![/blue]",
        ],
        defeat_text=["[blue]The captain's on his own now...[/blue]"],
        victory_text=["[blue]Tendrils and tentacles — nowhere to run![/blue]"],
    ),
    # ═════════════════════════════════════════════════════════════
    # ROUTE 10 SOUTH TRAINERS
    # ═════════════════════════════════════════════════════════════
    "hiker_cole": Trainer(
        id="hiker_cole",
        name="Cole",
        trainer_class="Hiker",
        location="Route 10 South",
        pokemon=[
            TrainerPokemon("GEODUDE", 23),
            TrainerPokemon("GRAVELER", 22),
        ],
        prize_money=460,
        intro_text=[
            "🥾 [bold]Hiker Cole:[/bold] [orange3]Just climbed down from Rock Tunnel![/orange3]",
            "[orange3]   Need a good battle to cool off![/orange3]",
        ],
        defeat_text=["[orange3]You handle the downhill better than me...[/orange3]"],
        victory_text=["[orange3]Gravel and grit — unmatched![/orange3]"],
    ),
    "youngster_ned": Trainer(
        id="youngster_ned",
        name="Ned",
        trainer_class="Youngster",
        location="Route 10 South",
        pokemon=[
            TrainerPokemon("VOLTORB", 22),
            TrainerPokemon("DROWZEE", 23),
        ],
        prize_money=345,
        intro_text=[
            "👦 [bold]Youngster Ned:[/bold] [yellow]I can hear Lavender Town from here![/yellow]",
            "[yellow]   Creepy... but first, battle me![/yellow]",
        ],
        defeat_text=["[yellow]Now I'm scared of YOU too...[/yellow]"],
        victory_text=["[yellow]Hypnosis from Drowzee — sweet dreams![/yellow]"],
    ),
    # ═════════════════════════════════════════════════════════════
    # POKEMON TOWER TRAINERS (Channelers)
    # ═════════════════════════════════════════════════════════════
    "channeler_hope": Trainer(
        id="channeler_hope",
        name="Hope",
        trainer_class="Channeler",
        location="Pokemon Tower",
        pokemon=[
            TrainerPokemon("GASTLY", 24),
        ],
        prize_money=480,
        intro_text=[
            "👻 [bold]Channeler Hope:[/bold] [magenta]The spirits speak to me...[/magenta]",
            "[magenta]   They want you to leave![/magenta]",
        ],
        defeat_text=["[magenta]The spirits... have abandoned me...[/magenta]"],
        victory_text=["[magenta]The dead shall rise and overwhelm you![/magenta]"],
    ),
    "channeler_laurel": Trainer(
        id="channeler_laurel",
        name="Laurel",
        trainer_class="Channeler",
        location="Pokemon Tower",
        pokemon=[
            TrainerPokemon("GASTLY", 25),
            TrainerPokemon("GASTLY", 24),
        ],
        prize_money=500,
        intro_text=[
            "👻 [bold]Channeler Laurel:[/bold] [magenta]This tower is sacred ground![/magenta]",
            "[magenta]   Intruders will be cursed![/magenta]",
        ],
        defeat_text=["[magenta]My curse backfired...[/magenta]"],
        victory_text=["[magenta]Lick! Paralysis grips you![/magenta]"],
    ),
    "channeler_ruth_upper": Trainer(
        id="channeler_ruth_upper",
        name="Ruth",
        trainer_class="Channeler",
        location="Pokemon Tower",
        pokemon=[
            TrainerPokemon("HAUNTER", 26),
        ],
        prize_money=520,
        intro_text=[
            "👻 [bold]Channeler Ruth:[/bold] [magenta]You have disturbed the resting place![/magenta]",
            "[magenta]   My Haunter will drag you to the shadow world![/magenta]",
        ],
        defeat_text=["[magenta]It faded... like a dream...[/magenta]"],
        victory_text=["[magenta]Shadow ball engulfs you in darkness![/magenta]"],
    ),
    "channeler_patricia": Trainer(
        id="channeler_patricia",
        name="Patricia",
        trainer_class="Channeler",
        location="Pokemon Tower",
        pokemon=[
            TrainerPokemon("GASTLY", 26),
            TrainerPokemon("HAUNTER", 25),
        ],
        prize_money=520,
        intro_text=[
            "👻 [bold]Channeler Patricia:[/bold] [magenta]The souls here cry out in agony![/magenta]",
            "[magenta]   I will be their voice of vengeance![/magenta]",
        ],
        defeat_text=["[magenta]Their cries... unanswered...[/magenta]"],
        victory_text=["[magenta]Confuse Ray! You can't tell up from down![/magenta]"],
    ),
    "channeler_jody_upper": Trainer(
        id="channeler_jody_upper",
        name="Jody",
        trainer_class="Channeler",
        location="Pokemon Tower",
        pokemon=[
            TrainerPokemon("HAUNTER", 27),
            TrainerPokemon("GASTLY", 26),
        ],
        prize_money=540,
        intro_text=[
            "👻 [bold]Channeler Jody:[/bold] [magenta]Turn back now, or you will never leave![/magenta]",
        ],
        defeat_text=["[magenta]Perhaps the spirits chose you after all...[/magenta]"],
        victory_text=["[magenta]Mean Look! You cannot flee![/magenta]"],
    ),
    "channeler_astrid": Trainer(
        id="channeler_astrid",
        name="Astrid",
        trainer_class="Channeler",
        location="Pokemon Tower",
        pokemon=[
            TrainerPokemon("HAUNTER", 28),
            TrainerPokemon("HAUNTER", 27),
        ],
        prize_money=560,
        intro_text=[
            "👻 [bold]Channeler Astrid:[/bold] [magenta]The top floor is forbidden![/magenta]",
            "[magenta]   Mr. Fuji is ours now![/magenta]",
        ],
        defeat_text=["[magenta]You've broken the circle...[/magenta]"],
        victory_text=["[magenta]Nightmare! Your dreams are not your own![/magenta]"],
    ),
    # ═════════════════════════════════════════════════════════════
    # ROUTE 8 TRAINERS
    # ═════════════════════════════════════════════════════════════
    "jr_trainer_m_miguel": Trainer(
        id="jr_trainer_m_miguel",
        name="Miguel",
        trainer_class="Jr. Trainer♂",
        location="Route 8",
        pokemon=[
            TrainerPokemon("GROWLITHE", 25),
            TrainerPokemon("SPEAROW", 24),
        ],
        prize_money=450,
        intro_text=[
            "👦 [bold]Jr. Trainer Miguel:[/bold] [yellow]Route 8 is my training ground![/yellow]",
            "[yellow]   I've been here for weeks![/yellow]",
        ],
        defeat_text=["[yellow]Back to the drawing board...[/yellow]"],
        victory_text=["[yellow]Growlithe's Ember will scorch you![/yellow]"],
    ),
    "jr_trainer_f_coleen": Trainer(
        id="jr_trainer_f_coleen",
        name="Coleen",
        trainer_class="Jr. Trainer♀",
        location="Route 8",
        pokemon=[
            TrainerPokemon("VULPIX", 25),
            TrainerPokemon("MEOWTH", 24),
        ],
        prize_money=450,
        intro_text=[
            "👧 [bold]Jr. Trainer Coleen:[/bold] [yellow]Vulpix is the cutest AND strongest![/yellow]",
        ],
        defeat_text=["[yellow]My Vulpix's tails drooped...[/yellow]"],
        victory_text=["[yellow]Flamethrower! Too hot to handle![/yellow]"],
    ),
    "youngster_tim_r8": Trainer(
        id="youngster_tim_r8",
        name="Tim",
        trainer_class="Youngster",
        location="Route 8",
        pokemon=[
            TrainerPokemon("DROWZEE", 25),
            TrainerPokemon("MEOWTH", 26),
        ],
        prize_money=390,
        intro_text=[
            "👦 [bold]Youngster Tim:[/bold] [yellow]I was headed to Lavender Town but...[/yellow]",
            "[yellow]   That place is too creepy! Battle me instead![/yellow]",
        ],
        defeat_text=["[yellow]Now I'm scared of YOU too...[/yellow]"],
        victory_text=["[yellow]Hypnosis had you snoozing![/yellow]"],
    ),
    "lass_vera": Trainer(
        id="lass_vera",
        name="Vera",
        trainer_class="Lass",
        location="Route 8",
        pokemon=[
            TrainerPokemon("NIDORAN♀", 25),
            TrainerPokemon("VULPIX", 24),
            TrainerPokemon("MEOWTH", 25),
        ],
        prize_money=375,
        intro_text=[
            "👧 [bold]Lass Vera:[/bold] [yellow]Heading to the Game Corner?[/yellow]",
            "[yellow]   Beat me and I'll give you a tip![/yellow]",
        ],
        defeat_text=["[yellow]Here's the tip: avoid slots![/yellow]"],
        victory_text=["[yellow]I'll keep my tip to myself![/yellow]"],
    ),
    # ═════════════════════════════════════════════════════════════
    # TEAM ROCKET'S HIDEOUT TRAINERS
    # ═════════════════════════════════════════════════════════════
    "rocket_grunt_1": Trainer(
        id="rocket_grunt_1",
        name="Grunt",
        trainer_class="Team Rocket",
        location="Team Rocket's Hideout",
        pokemon=[
            TrainerPokemon("EKANS", 27),
            TrainerPokemon("RATTATA", 26),
        ],
        prize_money=540,
        intro_text=[
            "🚀 [bold]Team Rocket Grunt:[/bold] [red]Prepare for trouble![/red]",
            "[red]   Hand over your Pokemon and your wallet![/red]",
        ],
        defeat_text=["[red]Team Rocket is blasting off again...[/red]"],
        victory_text=["[red]Your Pokemon are ours now![/red]"],
    ),
    "rocket_grunt_2": Trainer(
        id="rocket_grunt_2",
        name="Grunt",
        trainer_class="Team Rocket",
        location="Team Rocket's Hideout",
        pokemon=[
            TrainerPokemon("KOFFING", 27),
            TrainerPokemon("DROWZEE", 26),
        ],
        prize_money=540,
        intro_text=[
            "🚀 [bold]Team Rocket Grunt:[/bold] [red]This floor is restricted![/red]",
            "[red]   Intruders will be eliminated![/red]",
        ],
        defeat_text=["[red]The boss won't be happy...[/red]"],
        victory_text=["[red]Smog everywhere! You can't breathe![/red]"],
    ),
    "rocket_grunt_3": Trainer(
        id="rocket_grunt_3",
        name="Grunt",
        trainer_class="Team Rocket",
        location="Team Rocket's Hideout",
        pokemon=[
            TrainerPokemon("RATTATA", 27),
            TrainerPokemon("ZUBAT", 27),
            TrainerPokemon("EKANS", 26),
        ],
        prize_money=540,
        intro_text=[
            "🚀 [bold]Team Rocket Grunt:[/bold] [red]You've made it this far?[/red]",
            "[red]   Impressive. But your journey ends HERE![/red]",
        ],
        defeat_text=["[red]How did a kid beat me?![/red]"],
        victory_text=["[red]Three-on-one! You can't win![/red]"],
    ),
    "rocket_grunt_4": Trainer(
        id="rocket_grunt_4",
        name="Grunt",
        trainer_class="Team Rocket",
        location="Team Rocket's Hideout",
        pokemon=[
            TrainerPokemon("KOFFING", 28),
            TrainerPokemon("MUK", 27),
        ],
        prize_money=560,
        intro_text=[
            "🚀 [bold]Team Rocket Grunt:[/bold] [red]The Lift Key? You'll never find it![/red]",
            "[red]   I'll make sure of that![/red]",
        ],
        defeat_text=["[red]Check B2F... not that it'll help you...[/red]"],
        victory_text=["[red]Sludge coats everything — you're stuck![/red]"],
    ),
    "rocket_grunt_5": Trainer(
        id="rocket_grunt_5",
        name="Grunt",
        trainer_class="Team Rocket",
        location="Team Rocket's Hideout",
        pokemon=[
            TrainerPokemon("DROWZEE", 29),
            TrainerPokemon("KOFFING", 28),
        ],
        prize_money=580,
        intro_text=[
            "🚀 [bold]Team Rocket Grunt:[/bold] [red]The boss is below — you're not getting through![/red]",
        ],
        defeat_text=["[red]I told the boss this would happen...[/red]"],
        victory_text=["[red]Hypnosis! Sleep until we're done![/red]"],
    ),
    "rocket_grunt_6": Trainer(
        id="rocket_grunt_6",
        name="Grunt",
        trainer_class="Team Rocket",
        location="Team Rocket's Hideout",
        pokemon=[
            TrainerPokemon("RATICATE", 29),
            TrainerPokemon("ZUBAT", 28),
            TrainerPokemon("KOFFING", 28),
        ],
        prize_money=580,
        intro_text=[
            "🚀 [bold]Team Rocket Grunt:[/bold] [red]One step closer to your doom![/red]",
            "[red]   The spinner tiles will break your spirit![/red]",
        ],
        defeat_text=["[red]The spinning tiles betrayed me too...[/red]"],
        victory_text=["[red]Hyper Fang from Raticate! No escaping that![/red]"],
    ),
    "rocket_grunt_7": Trainer(
        id="rocket_grunt_7",
        name="Grunt",
        trainer_class="Team Rocket",
        location="Team Rocket's Hideout",
        pokemon=[
            TrainerPokemon("KOFFING", 30),
            TrainerPokemon("EKANS", 29),
        ],
        prize_money=600,
        intro_text=[
            "🚀 [bold]Team Rocket Grunt:[/bold] [red]Giovanni's personal guard![/red]",
            "[red]   You'll have to kill me to pass![/red]",
        ],
        defeat_text=["[red]Giovanni... forgive me...[/red]"],
        victory_text=["[red]Giovanni will destroy you personally![/red]"],
    ),
    "rocket_grunt_8": Trainer(
        id="rocket_grunt_8",
        name="Grunt",
        trainer_class="Team Rocket",
        location="Team Rocket's Hideout",
        pokemon=[
            TrainerPokemon("MUK", 30),
            TrainerPokemon("KOFFING", 30),
        ],
        prize_money=620,
        intro_text=[
            "🚀 [bold]Team Rocket Grunt:[/bold] [red]Last line of defence![/red]",
            "[red]   If you beat me, Giovanni WILL be waiting![/red]",
        ],
        defeat_text=["[red]The boss... is all that remains...[/red]"],
        victory_text=["[red]Toxic! You'll be poisoned before you reach the boss![/red]"],
    ),
    "rocket_grunt_9": Trainer(
        id="rocket_grunt_9",
        name="Grunt",
        trainer_class="Team Rocket",
        location="Team Rocket's Hideout",
        pokemon=[
            TrainerPokemon("RATTATA", 29),
            TrainerPokemon("RATICATE", 30),
            TrainerPokemon("ZUBAT", 30),
        ],
        prize_money=600,
        intro_text=[
            "🚀 [bold]Team Rocket Grunt:[/bold] [red]You managed the spinner tiles?[/red]",
            "[red]   That was just the warm-up![/red]",
        ],
        defeat_text=["[red]You navigate this maze better than I do...[/red]"],
        victory_text=["[red]Swarm of Zubat! You can't see anything![/red]"],
    ),
    "rocket_grunt_10": Trainer(
        id="rocket_grunt_10",
        name="Grunt",
        trainer_class="Team Rocket",
        location="Team Rocket's Hideout",
        pokemon=[
            TrainerPokemon("DROWZEE", 30),
            TrainerPokemon("MUK", 29),
        ],
        prize_money=600,
        intro_text=[
            "🚀 [bold]Team Rocket Grunt:[/bold] [red]The Silph Scope belongs to Team Rocket![/red]",
            "[red]   Only the boss can let you have it![/red]",
        ],
        defeat_text=["[red]Take it up with the boss then...[/red]"],
        victory_text=["[red]The Silph Scope amplifies our power — not yours![/red]"],
    ),
    # ===== Team Rocket's Hideout - Giovanni (Boss) =====
    "giovanni_rocket_hideout": Trainer(
        id="giovanni_rocket_hideout",
        name="Giovanni",
        trainer_class="Team Rocket",
        location="Team Rocket's Hideout",
        pokemon=[
            TrainerPokemon(species="ONIX", level=25),
            TrainerPokemon(species="RHYHORN", level=24),
            TrainerPokemon(species="KANGASKHAN", level=29),
        ],
        prize_money=2900,
        intro_text=[
            "🚀 [bold]Giovanni:[/bold] [red]So, you have made it this far![/red]",
            "[red]   Impressive for such a young trainer.[/red]",
            "[red]   But here is where your journey ends![/red]",
            "[red]   I am Giovanni, the Boss of Team Rocket![/red]",
            "[red]   My Pokemon are trained to perfection![/red]",
            "",
            "[bold yellow]⚔️  BOSS BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=[
            "[red]Unbelievable...[/red]",
            "[red]   A child has defeated me.[/red]",
            "[red]   ...I shall retreat for now.[/red]",
            "[red]   Here — take the Silph Scope![/red]",
            "[red]   It's useless to us if we cannot hold this base.[/red]",
        ],
        victory_text=[
            "[red]As I expected.[/red]",
            "[red]   Grow stronger and challenge me again.[/red]",
        ],
    ),
    # ===== Celadon City Gym Trainers =====
    "gym_trainer_celadon_beauty": Trainer(
        id="gym_trainer_celadon_beauty",
        name="Beauty Bridget",
        trainer_class="Beauty",
        location="Celadon City",
        pokemon=[
            TrainerPokemon(species="GLOOM", level=26),
            TrainerPokemon(species="WEEPINBELL", level=26),
        ],
        prize_money=1300,
        intro_text=[
            "💄 [bold]Beauty Bridget:[/bold] [green]Oh my, a challenger![/green]",
            "[green]   My Grass Pokemon are so beautiful...[/green]",
            "[green]   ...Don't you dare hurt them![/green]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=[
            "[green]You meanie! My beautiful Pokemon...[/green]",
        ],
        victory_text=[
            "[green]Ha! Beauty and power — what a combination![/green]",
        ],
    ),
    "gym_trainer_celadon_lass": Trainer(
        id="gym_trainer_celadon_lass",
        name="Lass Kay",
        trainer_class="Lass",
        location="Celadon City",
        pokemon=[
            TrainerPokemon(species="ODDISH", level=24),
            TrainerPokemon(species="GLOOM", level=28),
        ],
        prize_money=896,
        intro_text=[
            "🎀 [bold]Lass Kay:[/bold] [green]Erika's the best Gym Leader![/green]",
            "[green]   You'll have to get through me first![/green]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=[
            "[green]Erika will still beat you, just wait![/green]",
        ],
        victory_text=[
            "[green]See? Grass types rule![/green]",
        ],
    ),
    # ===== Fuchsia City Gym Trainers =====
    "gym_trainer_fuchsia_juggler": Trainer(
        id="gym_trainer_fuchsia_juggler",
        name="Juggler Ned",
        trainer_class="Juggler",
        location="Fuchsia City",
        pokemon=[
            TrainerPokemon(species="DROWZEE", level=33),
            TrainerPokemon(species="KOFFING", level=35),
            TrainerPokemon(species="KOFFING", level=35),
        ],
        prize_money=1540,
        intro_text=[
            "🤹 [bold]Juggler Ned:[/bold] [purple]Watch closely![/purple]",
            "[purple]   My Pokemon are as unpredictable as my juggling act![/purple]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=[
            "[purple]You disrupted my concentration![/purple]",
        ],
        victory_text=[
            "[purple]Hah! You couldn't keep up with my tricks![/purple]",
        ],
    ),
    "gym_trainer_fuchsia_lass": Trainer(
        id="gym_trainer_fuchsia_lass",
        name="Lass Cindy",
        trainer_class="Lass",
        location="Fuchsia City",
        pokemon=[
            TrainerPokemon(species="VENONAT", level=32),
            TrainerPokemon(species="VENOMOTH", level=36),
        ],
        prize_money=1152,
        intro_text=[
            "🎀 [bold]Lass Cindy:[/bold] [purple]Koga-sensei taught me everything![/purple]",
            "[purple]   Poison types are totally underrated![/purple]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=[
            "[purple]I'll train harder with Koga-sensei![/purple]",
        ],
        victory_text=[
            "[purple]Hah! Poison always seeps through in the end![/purple]",
        ],
    ),
    # ===== Routes 13-15 Trainers (South Coast) =====
    "trainer_route13_birdkeeper_jose": Trainer(
        id="trainer_route13_birdkeeper_jose",
        name="Bird Keeper Jose",
        trainer_class="Bird Keeper",
        location="Route 13",
        pokemon=[
            TrainerPokemon(species="PIDGEOTTO", level=28),
            TrainerPokemon(species="FEAROW", level=26),
        ],
        prize_money=1008,
        intro_text=[
            "🦅 [bold]Bird Keeper Jose:[/bold] [cyan]The winds are with us![/cyan]",
            "[cyan]   My birds rule the skies of Route 13![/cyan]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=["[cyan]The wind turned against me...[/cyan]"],
        victory_text=["[cyan]Ha! My birds are unbeatable![/cyan]"],
    ),
    "trainer_route13_birdkeeper_donald": Trainer(
        id="trainer_route13_birdkeeper_donald",
        name="Bird Keeper Donald",
        trainer_class="Bird Keeper",
        location="Route 13",
        pokemon=[
            TrainerPokemon(species="FARFETCH'D", level=26),
            TrainerPokemon(species="PIDGEOTTO", level=28),
        ],
        prize_money=1008,
        intro_text=[
            "🦆 [bold]Bird Keeper Donald:[/bold] [cyan]Farfetch'd is a rare sight![/cyan]",
            "[cyan]   My partner and I will defeat you![/cyan]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=["[cyan]Even Farfetch'd couldn't help us...[/cyan]"],
        victory_text=["[cyan]Farfetch'd is worth its weight in gold![/cyan]"],
    ),
    "trainer_route13_birdkeeper_perry": Trainer(
        id="trainer_route13_birdkeeper_perry",
        name="Bird Keeper Perry",
        trainer_class="Bird Keeper",
        location="Route 13",
        pokemon=[
            TrainerPokemon(species="SPEAROW", level=25),
            TrainerPokemon(species="FEAROW", level=30),
        ],
        prize_money=1080,
        intro_text=[
            "🦅 [bold]Bird Keeper Perry:[/bold] [cyan]Fearow swoops from nowhere![/cyan]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=["[cyan]Fearow, return...[/cyan]"],
        victory_text=["[cyan]Fearow's Drill Peck is unstoppable![/cyan]"],
    ),
    "trainer_route14_birdkeeper_wilton": Trainer(
        id="trainer_route14_birdkeeper_wilton",
        name="Bird Keeper Wilton",
        trainer_class="Bird Keeper",
        location="Route 14",
        pokemon=[
            TrainerPokemon(species="PIDGEOTTO", level=27),
            TrainerPokemon(species="PIDGEOTTO", level=29),
        ],
        prize_money=1044,
        intro_text=[
            "🦅 [bold]Bird Keeper Wilton:[/bold] [cyan]Route 14 is my territory![/cyan]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=["[cyan]Swooped and missed...[/cyan]"],
        victory_text=["[cyan]Nobody passes through without a fight![/cyan]"],
    ),
    "trainer_route14_birdkeeper_yoshi": Trainer(
        id="trainer_route14_birdkeeper_yoshi",
        name="Bird Keeper Yoshi",
        trainer_class="Bird Keeper",
        location="Route 14",
        pokemon=[
            TrainerPokemon(species="SPEAROW", level=26),
            TrainerPokemon(species="SPEAROW", level=26),
            TrainerPokemon(species="FEAROW", level=30),
        ],
        prize_money=1080,
        intro_text=[
            "🦅 [bold]Bird Keeper Yoshi:[/bold] [cyan]A flock surrounds you![/cyan]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=["[cyan]The flock scatters...[/cyan]"],
        victory_text=["[cyan]We'll circle around again![/cyan]"],
    ),
    "trainer_route15_pokemaniac_steve": Trainer(
        id="trainer_route15_pokemaniac_steve",
        name="Pokemaniac Steve",
        trainer_class="Pokemaniac",
        location="Route 15",
        pokemon=[
            TrainerPokemon(species="SLOWPOKE", level=30),
            TrainerPokemon(species="SLOWPOKE", level=30),
        ],
        prize_money=1800,
        intro_text=[
            "🧟 [bold]Pokemaniac Steve:[/bold] [magenta]Slowpoke is the most powerful Pokemon![/magenta]",
            "[magenta]   I've been waiting here for hours...[/magenta]",
            "[magenta]   ...or was it days?[/magenta]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=["[magenta]Slow and steady... loses sometimes...[/magenta]"],
        victory_text=["[magenta]Slowpoke always wins eventually![/magenta]"],
    ),
    "trainer_route15_birdkeeper_mitch": Trainer(
        id="trainer_route15_birdkeeper_mitch",
        name="Bird Keeper Mitch",
        trainer_class="Bird Keeper",
        location="Route 15",
        pokemon=[
            TrainerPokemon(species="PIDGEOTTO", level=29),
            TrainerPokemon(species="FEAROW", level=31),
        ],
        prize_money=1116,
        intro_text=[
            "🦅 [bold]Bird Keeper Mitch:[/bold] [cyan]Almost at Fuchsia — but not yet![/cyan]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=["[cyan]So close to the city...[/cyan]"],
        victory_text=["[cyan]Nobody slips past me![/cyan]"],
    ),
    # ===== Routes 16-18 Trainers (Cycling Road) =====
    "trainer_route16_biker_charles": Trainer(
        id="trainer_route16_biker_charles",
        name="Biker Charles",
        trainer_class="Biker",
        location="Route 16",
        pokemon=[
            TrainerPokemon(species="KOFFING", level=30),
            TrainerPokemon(species="KOFFING", level=30),
        ],
        prize_money=780,
        intro_text=[
            "🏍️ [bold]Biker Charles:[/bold] [purple]The Cycling Road is OURS![/purple]",
            "[purple]   No pedestrian challengers allowed![/purple]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=["[purple]You're fast for someone on foot![/purple]"],
        victory_text=["[purple]Nobody outrides the Bikers![/purple]"],
    ),
    "trainer_route17_biker_ruben": Trainer(
        id="trainer_route17_biker_ruben",
        name="Biker Ruben",
        trainer_class="Biker",
        location="Route 17",
        pokemon=[
            TrainerPokemon(species="KOFFING", level=32),
            TrainerPokemon(species="WEEZING", level=34),
        ],
        prize_money=884,
        intro_text=[
            "🏍️ [bold]Biker Ruben:[/bold] [purple]Downhill and full throttle![/purple]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=["[purple]You stopped my momentum![/purple]"],
        victory_text=["[purple]Gas em up! Full speed ahead![/purple]"],
    ),
    "trainer_route17_biker_riley": Trainer(
        id="trainer_route17_biker_riley",
        name="Biker Riley",
        trainer_class="Biker",
        location="Route 17",
        pokemon=[
            TrainerPokemon(species="KOFFING", level=28),
            TrainerPokemon(species="KOFFING", level=28),
            TrainerPokemon(species="KOFFING", level=32),
        ],
        prize_money=832,
        intro_text=[
            "🏍️ [bold]Biker Riley:[/bold] [purple]Three Koffing — that's a cloud of trouble![/purple]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=["[purple]That's some thick smog you cut through![/purple]"],
        victory_text=["[purple]Choke on that poison gas![/purple]"],
    ),
    "trainer_route17_biker_ernest": Trainer(
        id="trainer_route17_biker_ernest",
        name="Biker Ernest",
        trainer_class="Biker",
        location="Route 17",
        pokemon=[
            TrainerPokemon(species="WEEZING", level=35),
        ],
        prize_money=910,
        intro_text=[
            "🏍️ [bold]Biker Ernest:[/bold] [purple]Weezing will flatten your whole team![/purple]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=["[purple]You'll pay for that one...[/purple]"],
        victory_text=["[purple]Nobody beats the Bikers on their home turf![/purple]"],
    ),
    "trainer_route18_biker_glen": Trainer(
        id="trainer_route18_biker_glen",
        name="Biker Glen",
        trainer_class="Biker",
        location="Route 18",
        pokemon=[
            TrainerPokemon(species="KOFFING", level=31),
            TrainerPokemon(species="KOFFING", level=33),
        ],
        prize_money=858,
        intro_text=[
            "🏍️ [bold]Biker Glen:[/bold] [purple]Last checkpoint before Fuchsia![/purple]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=["[purple]The road ends here... for me at least.[/purple]"],
        victory_text=["[purple]Fuchsia City is still a long way off![/purple]"],
    ),
    # ===== Routes 19-20 Trainers (Sea Routes) =====
    "trainer_route19_swimmer_tony": Trainer(
        id="trainer_route19_swimmer_tony",
        name="Swimmer Tony",
        trainer_class="Swimmer",
        location="Route 19",
        pokemon=[
            TrainerPokemon(species="TENTACOOL", level=32),
            TrainerPokemon(species="TENTACOOL", level=34),
        ],
        prize_money=680,
        intro_text=[
            "🏊 [bold]Swimmer Tony:[/bold] [blue]The sea is my battlefield![/blue]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=["[blue]Caught a cramp at the worst moment...[/blue]"],
        victory_text=["[blue]Nobody outraces me in open water![/blue]"],
    ),
    "trainer_route19_swimmer_dawn": Trainer(
        id="trainer_route19_swimmer_dawn",
        name="Swimmer Dawn",
        trainer_class="Swimmer",
        location="Route 19",
        pokemon=[
            TrainerPokemon(species="HORSEA", level=30),
            TrainerPokemon(species="SEADRA", level=35),
        ],
        prize_money=700,
        intro_text=[
            "🏊 [bold]Swimmer Dawn:[/bold] [blue]Seadra will knock you overboard![/blue]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=["[blue]The current swept me away...[/blue]"],
        victory_text=["[blue]Seadra's Dragon Rage is unstoppable![/blue]"],
    ),
    "trainer_route20_swimmer_paul": Trainer(
        id="trainer_route20_swimmer_paul",
        name="Swimmer Paul",
        trainer_class="Swimmer",
        location="Route 20",
        pokemon=[
            TrainerPokemon(species="TENTACOOL", level=33),
            TrainerPokemon(species="TENTACRUEL", level=37),
        ],
        prize_money=740,
        intro_text=[
            "🏊 [bold]Swimmer Paul:[/bold] [blue]These waters belong to Tentacruel![/blue]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=["[blue]Tentacruel's tentacles failed me...[/blue]"],
        victory_text=["[blue]Swim into my trap![/blue]"],
    ),
    "trainer_route20_swimmer_elaine": Trainer(
        id="trainer_route20_swimmer_elaine",
        name="Swimmer Elaine",
        trainer_class="Swimmer",
        location="Route 20",
        pokemon=[
            TrainerPokemon(species="HORSEA", level=32),
            TrainerPokemon(species="HORSEA", level=32),
            TrainerPokemon(species="SEADRA", level=36),
        ],
        prize_money=720,
        intro_text=[
            "🏊 [bold]Swimmer Elaine:[/bold] [blue]The sea route is treacherous — let me show you![/blue]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=["[blue]The waves weren't on my side today...[/blue]"],
        victory_text=["[blue]You'll never reach Cinnabar![/blue]"],
    ),
    # ═════════════════════════════════════════════════════════════
    # SAFFRON CITY GYM TRAINERS (Sabrina — Psychic-type)
    # ═════════════════════════════════════════════════════════════
    "psychic_cameron": Trainer(
        id="psychic_cameron",
        name="Cameron",
        trainer_class="Psychic",
        location="Saffron City",
        pokemon=[
            TrainerPokemon(species="ABRA", level=33),
            TrainerPokemon(species="KADABRA", level=35),
        ],
        prize_money=1120,
        intro_text=[
            "🔮 [bold]Psychic Cameron:[/bold] [magenta]I can already see your defeat...[/magenta]",
            "[magenta]   My psychic bond with my Pokemon is unmatched![/magenta]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=["[magenta]How?! I foresaw everything but this![/magenta]"],
        victory_text=["[magenta]My vision was perfect — as expected.[/magenta]"],
    ),
    "medium_doris": Trainer(
        id="medium_doris",
        name="Doris",
        trainer_class="Medium",
        location="Saffron City",
        pokemon=[
            TrainerPokemon(species="DROWZEE", level=34),
            TrainerPokemon(species="HYPNO", level=36),
        ],
        prize_money=1152,
        intro_text=[
            "🧿 [bold]Medium Doris:[/bold] [magenta]The spirits guide my Hypno...[/magenta]",
            "[magenta]   You cannot resist our power![/magenta]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=["[magenta]The spirits... they misled me...[/magenta]"],
        victory_text=["[magenta]Sleep now and trouble us no more.[/magenta]"],
    ),
    "psychic_brad": Trainer(
        id="psychic_brad",
        name="Brad",
        trainer_class="Psychic",
        location="Saffron City",
        pokemon=[
            TrainerPokemon(species="MR_MIME", level=37),
            TrainerPokemon(species="JYNX", level=36),
        ],
        prize_money=1152,
        intro_text=[
            "🔮 [bold]Psychic Brad:[/bold] [magenta]Mr. Mime will create an invisible wall[/magenta]",
            "[magenta]   around your whole strategy![/magenta]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=["[magenta]Sabrina trains us better than this... I need more work.[/magenta]"],
        victory_text=["[magenta]Mind over matter. Always.[/magenta]"],
    ),
    # ═════════════════════════════════════════════════════════════
    # CINNABAR ISLAND GYM TRAINERS (Blaine — Fire-type)
    # ═════════════════════════════════════════════════════════════
    "super_nerd_ted": Trainer(
        id="super_nerd_ted",
        name="Ted",
        trainer_class="Super Nerd",
        location="Cinnabar Island",
        pokemon=[
            TrainerPokemon(species="MAGMAR", level=38),
            TrainerPokemon(species="RAPIDASH", level=40),
        ],
        prize_money=960,
        intro_text=[
            "🤓 [bold]Super Nerd Ted:[/bold] [red]I've studied the chemistry of fire![/red]",
            "[red]   Magmar's flame is 2200 degrees — fact![/red]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=["[red]My calculations were... slightly off.[/red]"],
        victory_text=["[red]Science AND fire — the ultimate combination![/red]"],
    ),
    "juggler_kaylee": Trainer(
        id="juggler_kaylee",
        name="Kaylee",
        trainer_class="Juggler",
        location="Cinnabar Island",
        pokemon=[
            TrainerPokemon(species="MAGMAR", level=37),
            TrainerPokemon(species="PONYTA", level=37),
            TrainerPokemon(species="RAPIDASH", level=39),
        ],
        prize_money=936,
        intro_text=[
            "🤹 [bold]Juggler Kaylee:[/bold] [red]I juggle fireballs for fun![/red]",
            "[red]   My Pokemon are just as hot![/red]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=["[red]Dropped the ball... literally.[/red]"],
        victory_text=["[red]Hah! You can't handle my heat![/red]"],
    ),
    "blaine_trainee": Trainer(
        id="blaine_trainee",
        name="Ridley",
        trainer_class="Super Nerd",
        location="Cinnabar Island",
        pokemon=[
            TrainerPokemon(species="GROWLITHE", level=40),
            TrainerPokemon(species="ARCANINE", level=42),
        ],
        prize_money=1008,
        intro_text=[
            "🤓 [bold]Super Nerd Ridley:[/bold] [red]I am training directly under Blaine![/red]",
            "[red]   My Arcanine's speed will leave you in ashes![/red]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=["[red]I need to hit the books harder... and the flames hotter.[/red]"],
        victory_text=["[red]Blaine's training is paying off![/red]"],
    ),
    # ═════════════════════════════════════════════════════════════
    # VIRIDIAN CITY GYM TRAINERS (Giovanni — Ground-type)
    # ═════════════════════════════════════════════════════════════
    "cooltrainer_m_tucker": Trainer(
        id="cooltrainer_m_tucker",
        name="Tucker",
        trainer_class="Cool Trainer",
        location="Viridian City",
        pokemon=[
            TrainerPokemon(species="SANDSLASH", level=43),
            TrainerPokemon(species="DUGTRIO", level=45),
        ],
        prize_money=4500,
        intro_text=[
            "😎 [bold]Cool Trainer Tucker:[/bold] [yellow]Only the toughest make it this far.[/yellow]",
            "[yellow]   Dugtrio will bury you alive.[/yellow]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=["[yellow]Impressive. Giovanni is a harder challenge, though.[/yellow]"],
        victory_text=["[yellow]Speed and power — nothing can touch us.[/yellow]"],
    ),
    "tamer_jake": Trainer(
        id="tamer_jake",
        name="Jake",
        trainer_class="Tamer",
        location="Viridian City",
        pokemon=[
            TrainerPokemon(species="RHYHORN", level=44),
            TrainerPokemon(species="RHYDON", level=45),
        ],
        prize_money=1800,
        intro_text=[
            "🦁 [bold]Tamer Jake:[/bold] [orange3]Rhyhorn and Rhydon may look slow...[/orange3]",
            "[orange3]   but Rhydon's Earthquake shakes the whole building![/orange3]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=["[orange3]The earth didn't shake hard enough today.[/orange3]"],
        victory_text=["[orange3]Nothing withstands Rhydon's raw force![/orange3]"],
    ),
    "giovanni_guard": Trainer(
        id="giovanni_guard",
        name="Grunt",
        trainer_class="Rocket Grunt",
        location="Viridian City",
        pokemon=[
            TrainerPokemon(species="NIDORAN♂", level=43),
            TrainerPokemon(species="NIDORINO", level=44),
            TrainerPokemon(species="NIDOKING", level=46),
        ],
        prize_money=1380,
        intro_text=[
            "🚀 [bold]Rocket Grunt:[/bold] [red]Giovanni is the greatest Trainer alive![/red]",
            "[red]   You'll have to get through me first![/red]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=["[red]Team Rocket will rise again![/red]"],
        victory_text=["[red]Giovanni's chosen soldiers are unstoppable![/red]"],
    ),
    # ═════════════════════════════════════════════════════════════
    # SILPH CO. TRAINERS (Saffron City)
    # ═════════════════════════════════════════════════════════════
    "rocket_grunt_silph_1": Trainer(
        id="rocket_grunt_silph_1",
        name="Grunt",
        trainer_class="Rocket Grunt",
        location="Saffron City",
        pokemon=[
            TrainerPokemon(species="EKANS", level=32),
            TrainerPokemon(species="ARBOK", level=34),
        ],
        prize_money=1020,
        intro_text=[
            "🚀 [bold]Rocket Grunt:[/bold] [red]Team Rocket controls Silph Co.![/red]",
            "[red]   No one gets through without a fight![/red]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=["[red]You haven't seen the last of Team Rocket![/red]"],
        victory_text=["[red]Arbok's Glare will paralyse you with fear![/red]"],
    ),
    "rocket_grunt_silph_2": Trainer(
        id="rocket_grunt_silph_2",
        name="Grunt",
        trainer_class="Rocket Grunt",
        location="Saffron City",
        pokemon=[
            TrainerPokemon(species="KOFFING", level=33),
            TrainerPokemon(species="WEEZING", level=35),
        ],
        prize_money=1050,
        intro_text=[
            "🚀 [bold]Rocket Grunt:[/bold] [red]Weezing will fill this floor with poison gas![/red]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=["[red]The gas... it backfired on us...[/red]"],
        victory_text=["[red]Breathe deep — that's Weezing's finest vintage![/red]"],
    ),
    "rocket_grunt_silph_3": Trainer(
        id="rocket_grunt_silph_3",
        name="Grunt",
        trainer_class="Rocket Grunt",
        location="Saffron City",
        pokemon=[
            TrainerPokemon(species="RATICATE", level=34),
            TrainerPokemon(species="PERSIAN", level=36),
        ],
        prize_money=1080,
        intro_text=[
            "🚀 [bold]Rocket Grunt:[/bold] [red]Persian is the boss's favourite,[/red]",
            "[red]   but my Persian is just as deadly![/red]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=["[red]I'll be demoted for this failure...[/red]"],
        victory_text=["[red]Pay Day cuts deep — ask your wallet![/red]"],
    ),
    "silph_executive": Trainer(
        id="silph_executive",
        name="Executive",
        trainer_class="Rocket Executive",
        location="Saffron City",
        pokemon=[
            TrainerPokemon(species="GOLBAT", level=36),
            TrainerPokemon(species="ARBOK", level=36),
            TrainerPokemon(species="WEEZING", level=38),
        ],
        prize_money=1900,
        intro_text=[
            "💼 [bold]Rocket Executive:[/bold] [red]You are meddling with forces beyond your understanding.[/red]",
            "[red]   Silph Co. — and all of Kanto — belongs to Team Rocket![/red]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=[
            "[red]Impossible... I am an Executive of Team Rocket![/red]",
            "[red]   Giovanni will hear of this...[/red]",
        ],
        victory_text=["[red]You cannot stop us. Our plans are already in motion.[/red]"],
    ),
    # ═════════════════════════════════════════════════════════════
    # VICTORY ROAD TRAINERS
    # ═════════════════════════════════════════════════════════════
    "cooltrainer_f_naomi": Trainer(
        id="cooltrainer_f_naomi",
        name="Naomi",
        trainer_class="Cool Trainer",
        location="Victory Road",
        pokemon=[
            TrainerPokemon(species="CLEFABLE", level=44),
            TrainerPokemon(species="CHANSEY", level=46),
        ],
        prize_money=4600,
        intro_text=[
            "😎 [bold]Cool Trainer Naomi:[/bold] [white]You came this far — impressive.[/white]",
            "[white]   But the final stretch belongs to the truly elite.[/white]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=["[white]You have what it takes. Prove it at the League too.[/white]"],
        victory_text=["[white]Chansey's endurance is truly unbreakable.[/white]"],
    ),
    "black_belt_hitoshi": Trainer(
        id="black_belt_hitoshi",
        name="Hitoshi",
        trainer_class="Black Belt",
        location="Victory Road",
        pokemon=[
            TrainerPokemon(species="MACHAMP", level=45),
            TrainerPokemon(species="HITMONLEE", level=44),
            TrainerPokemon(species="HITMONCHAN", level=44),
        ],
        prize_money=1320,
        intro_text=[
            "🥋 [bold]Black Belt Hitoshi:[/bold] [orange3]Victory Road sharpens the mind and body![/orange3]",
            "[orange3]   My three warriors have trained here for years![/orange3]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=["[orange3]Your strength surpasses mine. Train on, warrior.[/orange3]"],
        victory_text=["[orange3]Three Fighting masters — none can withstand us![/orange3]"],
    ),
    "cooltrainer_m_warren": Trainer(
        id="cooltrainer_m_warren",
        name="Warren",
        trainer_class="Cool Trainer",
        location="Victory Road",
        pokemon=[
            TrainerPokemon(species="NIDOKING", level=44),
            TrainerPokemon(species="RHYDON", level=46),
        ],
        prize_money=4600,
        intro_text=[
            "😎 [bold]Cool Trainer Warren:[/bold] [yellow]Ground types rule on this rocky terrain.[/yellow]",
            "[yellow]   Rhydon's Earthquake will flatten everything in your party![/yellow]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=["[yellow]Solid battling. You might just conquer the League.[/yellow]"],
        victory_text=["[yellow]The ground shook — and so did your team.[/yellow]"],
    ),
    "veteran_trainer": Trainer(
        id="veteran_trainer",
        name="Lance",
        trainer_class="Veteran",
        location="Victory Road",
        pokemon=[
            TrainerPokemon(species="GYARADOS", level=44),
            TrainerPokemon(species="DRAGONAIR", level=46),
        ],
        prize_money=4600,
        intro_text=[
            "🎖️ [bold]Veteran Lance:[/bold] [cyan]I have battled in Victory Road for decades.[/cyan]",
            "[cyan]   Dragonair's power is beyond what most trainers ever face.[/cyan]",
            "[cyan]   Are you truly ready for the Pokemon League?[/cyan]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=[
            "[cyan]Remarkable. You have the makings of a true Champion.[/cyan]",
            "[cyan]   Go. The Elite Four await you.[/cyan]",
        ],
        victory_text=["[cyan]Dragonair's grace is beyond your reach today.[/cyan]"],
    ),
    # ═════════════════════════════════════════════════════════════
    # POKEMON MANSION TRAINERS (Cinnabar Island)
    # ═════════════════════════════════════════════════════════════
    "scientist_mansion_1": Trainer(
        id="scientist_mansion_1",
        name="Jerry",
        trainer_class="Super Nerd",
        location="Cinnabar Island",
        pokemon=[
            TrainerPokemon(species="MAGMAR", level=35),
            TrainerPokemon(species="MAGMAR", level=37),
        ],
        prize_money=888,
        intro_text=[
            "🤓 [bold]Super Nerd Jerry:[/bold] [red]This mansion hides the greatest scientific secret![/red]",
            "[red]   The research notes are not for prying eyes![/red]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=["[red]Mewtwo... your creation surpasses your creators...[/red]"],
        victory_text=["[red]Science marches ever forward — and so do I![/red]"],
    ),
    "scientist_mansion_2": Trainer(
        id="scientist_mansion_2",
        name="Marcus",
        trainer_class="Super Nerd",
        location="Cinnabar Island",
        pokemon=[
            TrainerPokemon(species="KOFFING", level=36),
            TrainerPokemon(species="ELECTRODE", level=38),
            TrainerPokemon(species="MAGMAR", level=39),
        ],
        prize_money=936,
        intro_text=[
            "🤓 [bold]Super Nerd Marcus:[/bold] [red]You dare read Dr. Fuji's notes?![/red]",
            "[red]   We sealed this place to protect the world from what's inside![/red]",
            "",
            "[bold yellow]⚔️  TRAINER BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=["[red]The experiment... it has already escaped...[/red]"],
        victory_text=["[red]Our research demanded sacrifices — including yours![/red]"],
    ),
    # ═════════════════════════════════════════════════════════════
    # ELITE FOUR & CHAMPION (Pokemon League)
    # ═════════════════════════════════════════════════════════════
    "elite_lorelei": Trainer(
        id="elite_lorelei",
        name="Lorelei",
        trainer_class="Elite Four",
        location="Pokemon League",
        pokemon=[
            TrainerPokemon(species="DEWGONG", level=54),
            TrainerPokemon(species="CLOYSTER", level=53),
            TrainerPokemon(species="SLOWBRO", level=54),
            TrainerPokemon(species="JYNX", level=56),
            TrainerPokemon(species="LAPRAS", level=60),
        ],
        prize_money=6000,
        intro_text=[
            "❄️ [bold magenta]Elite Four Lorelei:[/bold magenta] [cyan]No one can prevent the冰 freeze that awaits...[/cyan]",
            "[cyan]   My Ice-type Pokemon have never lost to the likes of a child.[/cyan]",
            "[cyan]   Your journey ends here, in the cold.[/cyan]",
            "",
            "[bold yellow]⚔️  ELITE FOUR BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=[
            "[cyan]Incredible... you broke through my ice.[/cyan]",
            "[cyan]   You have earned the right to face Bruno.[/cyan]",
        ],
        victory_text=["[cyan]You are frozen solid — just as I predicted![/cyan]"],
        preferred_types=["Ice", "Water"],
    ),
    "elite_bruno": Trainer(
        id="elite_bruno",
        name="Bruno",
        trainer_class="Elite Four",
        location="Pokemon League",
        pokemon=[
            TrainerPokemon(species="ONIX", level=53),
            TrainerPokemon(species="HITMONCHAN", level=55),
            TrainerPokemon(species="HITMONLEE", level=55),
            TrainerPokemon(species="ONIX", level=56),
            TrainerPokemon(species="MACHAMP", level=58),
        ],
        prize_money=5800,
        intro_text=[
            "💪 [bold red]Elite Four Bruno:[/bold red] [red]I have trained my body and my Pokemon[/red]",
            "[red]   to the absolute limit of human endurance![/red]",
            "[red]   Your spirit may be willing — but your flesh will break![/red]",
            "",
            "[bold yellow]⚔️  ELITE FOUR BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=[
            "[red]You are indeed strong.[/red]",
            "[red]   Face Agatha next. Show her the same fighting spirit.[/red]",
        ],
        victory_text=["[red]Strength of body and mind — and still you falter![/red]"],
        preferred_types=["Fighting", "Rock"],
    ),
    "elite_agatha": Trainer(
        id="elite_agatha",
        name="Agatha",
        trainer_class="Elite Four",
        location="Pokemon League",
        pokemon=[
            TrainerPokemon(species="GENGAR", level=54),
            TrainerPokemon(species="HAUNTER", level=53),
            TrainerPokemon(species="GENGAR", level=58),
            TrainerPokemon(species="ARBOK", level=58),
            TrainerPokemon(species="GENGAR", level=60),
        ],
        prize_money=6000,
        intro_text=[
            "👻 [bold]Elite Four Agatha:[/bold] [dim]Heh heh heh...[/dim]",
            "[dim]   I knew your mentor Oak in his prime. What a waste he became.[/dim]",
            "[dim]   Now his little student stumbles into my parlour of shadows.[/dim]",
            "[dim]   My ghosts will haunt you for eternity![/dim]",
            "",
            "[bold yellow]⚔️  ELITE FOUR BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=[
            "[dim]Hmph! You're not bad... for Oak's pupil.[/dim]",
            "[dim]   Lance is next — good luck. You will need it.[/dim]",
        ],
        victory_text=["[dim]The spirits answer my call — and they claim you![/dim]"],
        preferred_types=["Ghost", "Poison"],
    ),
    "elite_lance": Trainer(
        id="elite_lance",
        name="Lance",
        trainer_class="Elite Four",
        location="Pokemon League",
        pokemon=[
            TrainerPokemon(species="GYARADOS", level=58),
            TrainerPokemon(species="DRAGONAIR", level=56),
            TrainerPokemon(species="DRAGONAIR", level=56),
            TrainerPokemon(species="AERODACTYL", level=60),
            TrainerPokemon(species="DRAGONITE", level=62),
        ],
        prize_money=6200,
        intro_text=[
            "🐉 [bold yellow]Elite Four Lance:[/bold yellow] [yellow]I am Lance — the world's greatest Dragon master![/yellow]",
            "[yellow]   My Dragons have soared above every challenger who dared stand here.[/yellow]",
            "[yellow]   The wind carries your fate. It blows against you today.[/yellow]",
            "",
            "[bold yellow]⚔️  ELITE FOUR BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=[
            "[yellow]Magnificent! You are a true Dragon Tamer![/yellow]",
            "[yellow]   The Champion awaits beyond. Go — prove your destiny.[/yellow]",
        ],
        victory_text=["[yellow]Dragonite's power is legend — and so is your defeat![/yellow]"],
        preferred_types=["Dragon", "Flying"],
    ),
    "champion_gary_bulbasaur": Trainer(
        id="champion_gary_bulbasaur",
        name="Gary",
        trainer_class="Champion",
        location="Pokemon League",
        pokemon=[
            TrainerPokemon(species="PIDGEOT", level=61),
            TrainerPokemon(species="ALAKAZAM", level=59),
            TrainerPokemon(species="RHYDON", level=61),
            TrainerPokemon(species="ARCANINE", level=63),
            TrainerPokemon(species="EXEGGUTOR", level=61),
            TrainerPokemon(species="CHARIZARD", level=65),
        ],
        prize_money=6500,
        intro_text=[
            "🏆 [bold green]Champion Gary:[/bold green] [green]Ha! You actually made it.[/green]",
            "[green]   Remember when we left Pallet Town together? I was always one step ahead.[/green]",
            "[green]   Now I stand as Pokemon League Champion. And you — you're just a challenger.[/green]",
            "[green]   Don't disappoint me. Losing to a weakling would be boring![/green]",
            "",
            "[bold yellow]⚔️  CHAMPION BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=[
            "[green]...[/green]",
            "[green]I... you actually beat me. My Pokemon...[/green]",
            "[green]You really have become stronger than me.[/green]",
            "[green]Congratulations — you are the new Pokemon League Champion![/green]",
            "[green]I was too confident. You humbled me today. Well done.[/green]",
        ],
        victory_text=["[green]Champion Gary remains undefeated! Just as expected![/green]"],
        preferred_types=["Normal", "Psychic"],
    ),
    "champion_gary_charmander": Trainer(
        id="champion_gary_charmander",
        name="Gary",
        trainer_class="Champion",
        location="Pokemon League",
        pokemon=[
            TrainerPokemon(species="PIDGEOT", level=61),
            TrainerPokemon(species="ALAKAZAM", level=59),
            TrainerPokemon(species="RHYDON", level=61),
            TrainerPokemon(species="GYARADOS", level=63),
            TrainerPokemon(species="EXEGGUTOR", level=61),
            TrainerPokemon(species="BLASTOISE", level=65),
        ],
        prize_money=6500,
        intro_text=[
            "🏆 [bold green]Champion Gary:[/bold green] [green]So you made it through the Elite Four.[/green]",
            "[green]   You picked Charmander — and I chose the stronger path.[/green]",
            "[green]   I've been Champion since before you left Pallet Town, practically.[/green]",
            "[green]   Let's end this quickly. I have better things to do![/green]",
            "",
            "[bold yellow]⚔️  CHAMPION BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=[
            "[green]...[/green]",
            "[green]You beat me. I don't believe it.[/green]",
            "[green]You're the new Pokemon League Champion.[/green]",
            "[green]I underestimated you. I won't make that mistake again.[/green]",
            "[green]You've truly grown. Congratulations — for real.[/green]",
        ],
        victory_text=["[green]Champion Gary remains undefeated! Just as expected![/green]"],
        preferred_types=["Normal", "Psychic"],
    ),
    "champion_gary_squirtle": Trainer(
        id="champion_gary_squirtle",
        name="Gary",
        trainer_class="Champion",
        location="Pokemon League",
        pokemon=[
            TrainerPokemon(species="PIDGEOT", level=61),
            TrainerPokemon(species="ALAKAZAM", level=59),
            TrainerPokemon(species="RHYDON", level=61),
            TrainerPokemon(species="ARCANINE", level=63),
            TrainerPokemon(species="EXEGGUTOR", level=61),
            TrainerPokemon(species="VENUSAUR", level=65),
        ],
        prize_money=6500,
        intro_text=[
            "🏆 [bold green]Champion Gary:[/bold green] [green]Well, well. The little Squirtle trainer made it.[/green]",
            "[green]   Do you remember leaving Pallet Town? I was already two towns ahead.[/green]",
            "[green]   I've conquered every trainer in Kanto. You're just the latest.[/green]",
            "[green]   Show me what you've got — and make it interesting![/green]",
            "",
            "[bold yellow]⚔️  CHAMPION BATTLE START! ⚔️[/bold yellow]",
        ],
        defeat_text=[
            "[green]...[/green]",
            "[green]You actually defeated me. The Champion... beaten.[/green]",
            "[green]You are the new Pokemon League Champion.[/green]",
            "[green]All that rivalry, all that training — you surpassed me.[/green]",
            "[green]I'm genuinely proud of you. Champion. It suits you.[/green]",
        ],
        victory_text=["[green]Champion Gary remains undefeated! Just as expected![/green]"],
        preferred_types=["Normal", "Psychic"],
    ),
    # ═════════════════════════════════════════════════════════════
    # REMATCH GYM LEADERS (post-Champion, ~20 levels higher)
    # ═════════════════════════════════════════════════════════════
    "gym_leader_brock_rematch": Trainer(
        id="gym_leader_brock_rematch",
        name="Brock",
        trainer_class="Gym Leader",
        location="Pewter City",
        pokemon=[
            TrainerPokemon(species="GRAVELER", level=54),
            TrainerPokemon(species="RHYHORN", level=56),
            TrainerPokemon(species="ONIX", level=58),
            TrainerPokemon(species="GOLEM", level=62),
        ],
        prize_money=6200,
        intro_text=[
            "⭐ [bold]Gym Leader Brock (Rematch):[/bold] [orange3]I've been training hard since our last battle![/orange3]",
            "[orange3]   My rock-solid resolve has never been stronger![/orange3]",
            "",
            "[bold yellow]⚔️  GYM REMATCH START! ⚔️[/bold yellow]",
        ],
        defeat_text=[
            "[orange3]Impressive! You've truly become a Pokemon Master.[/orange3]",
            "[orange3]   A Champion indeed![/orange3]",
        ],
        victory_text=[
            "[orange3]This time, the rock holds firm![/orange3]",
            "[orange3]   Train harder and come back![/orange3]",
        ],
        badge_reward=None,
        badge_id=None,
        preferred_types=["Rock", "Ground"],
    ),
    "gym_leader_misty_rematch": Trainer(
        id="gym_leader_misty_rematch",
        name="Misty",
        trainer_class="Gym Leader",
        location="Cerulean City",
        pokemon=[
            TrainerPokemon(species="PSYDUCK", level=52),
            TrainerPokemon(species="GOLDUCK", level=54),
            TrainerPokemon(species="STARMIE", level=60),
            TrainerPokemon(species="LAPRAS", level=58),
        ],
        prize_money=6000,
        intro_text=[
            "⭐ [bold]Gym Leader Misty (Rematch):[/bold] [blue]You defeated me once, but I've been training on the open seas![/blue]",
            "[blue]   My Pokemon are stronger than ever![/blue]",
            "",
            "[bold yellow]⚔️  GYM REMATCH START! ⚔️[/bold yellow]",
        ],
        defeat_text=[
            "[blue]Wow! You're the real Champion![/blue]",
            "[blue]   I've got a lot more training to do![/blue]",
        ],
        victory_text=[
            "[blue]My Water Pokemon are unstoppable![/blue]",
            "[blue]   Come back stronger, Champion![/blue]",
        ],
        badge_reward=None,
        badge_id=None,
        preferred_types=["Water"],
    ),
    "gym_leader_lt_surge_rematch": Trainer(
        id="gym_leader_lt_surge_rematch",
        name="Lt. Surge",
        trainer_class="Gym Leader",
        location="Vermillion City",
        pokemon=[
            TrainerPokemon(species="ELECTRODE", level=54),
            TrainerPokemon(species="RAICHU", level=58),
            TrainerPokemon(species="ELECTABUZZ", level=60),
            TrainerPokemon(species="MAGNETON", level=56),
        ],
        prize_money=6000,
        intro_text=[
            "⭐ [bold]Gym Leader Lt. Surge (Rematch):[/bold] [yellow]Soldier! You beat me once — that won't happen again![/yellow]",
            "[yellow]   My Electric Pokemon are battle-hardened![/yellow]",
            "",
            "[bold yellow]⚔️  GYM REMATCH START! ⚔️[/bold yellow]",
        ],
        defeat_text=[
            "[yellow]Mission failed... again! You've earned it, kid![/yellow]",
            "[yellow]   You ARE the real deal![/yellow]",
        ],
        victory_text=[
            "[yellow]Hahahaha! Lightning strikes twice![/yellow]",
            "[yellow]   Come back after more training, Champion![/yellow]",
        ],
        badge_reward=None,
        badge_id=None,
        preferred_types=["Electric"],
    ),
    "gym_leader_erika_rematch": Trainer(
        id="gym_leader_erika_rematch",
        name="Erika",
        trainer_class="Gym Leader",
        location="Celadon City",
        pokemon=[
            TrainerPokemon(species="EXEGGUTOR", level=58),
            TrainerPokemon(species="VICTREEBEL", level=56),
            TrainerPokemon(species="TANGELA", level=54),
            TrainerPokemon(species="VILEPLUME", level=62),
        ],
        prize_money=6200,
        intro_text=[
            "⭐ [bold]Gym Leader Erika (Rematch):[/bold] [green]You caught me napping last time...[/green]",
            "[green]   I won't make that mistake again, Champion.[/green]",
            "",
            "[bold yellow]⚔️  GYM REMATCH START! ⚔️[/bold yellow]",
        ],
        defeat_text=[
            "[green]Oh my... You are remarkable.[/green]",
            "[green]   A true Pokemon Champion.[/green]",
        ],
        victory_text=[
            "[green]Nature's patience outlasts all challengers.[/green]",
            "[green]   Try again, Champion.[/green]",
        ],
        badge_reward=None,
        badge_id=None,
        preferred_types=["Grass", "Poison"],
    ),
    "gym_leader_koga_rematch": Trainer(
        id="gym_leader_koga_rematch",
        name="Koga",
        trainer_class="Gym Leader",
        location="Fuchsia City",
        pokemon=[
            TrainerPokemon(species="WEEZING", level=62),
            TrainerPokemon(species="MUK", level=60),
            TrainerPokemon(species="VENOMOTH", level=58),
            TrainerPokemon(species="ARIADOS", level=65)
            if False
            else TrainerPokemon(species="WEEZING", level=65),
        ],
        prize_money=6500,
        intro_text=[
            "⭐ [bold]Gym Leader Koga (Rematch):[/bold] [purple]Fwahahaha! Champion or not, my poisons know no mercy![/purple]",
            "[purple]   Face the shadows once more![/purple]",
            "",
            "[bold yellow]⚔️  GYM REMATCH START! ⚔️[/bold yellow]",
        ],
        defeat_text=[
            "[purple]Hmph. Even poisons cannot overcome a true Champion.[/purple]",
        ],
        victory_text=[
            "[purple]Fwahahaha! The venom endures![/purple]",
        ],
        badge_reward=None,
        badge_id=None,
        preferred_types=["Poison"],
    ),
    "gym_leader_sabrina_rematch": Trainer(
        id="gym_leader_sabrina_rematch",
        name="Sabrina",
        trainer_class="Gym Leader",
        location="Saffron City",
        pokemon=[
            TrainerPokemon(species="JYNX", level=60),
            TrainerPokemon(species="MR_MIME", level=58),
            TrainerPokemon(species="ALAKAZAM", level=65),
            TrainerPokemon(species="HYPNO", level=62),
        ],
        prize_money=6500,
        intro_text=[
            "⭐ [bold]Gym Leader Sabrina (Rematch):[/bold] [magenta]I foresaw your return, Champion.[/magenta]",
            "[magenta]   My psychic powers have grown since we last met.[/magenta]",
            "",
            "[bold yellow]⚔️  GYM REMATCH START! ⚔️[/bold yellow]",
        ],
        defeat_text=[
            "[magenta]I witnessed this defeat in my visions... yet it still surprises me.[/magenta]",
        ],
        victory_text=[
            "[magenta]The future was clear to me.[/magenta]",
            "[magenta]   Train your mind, Champion.[/magenta]",
        ],
        badge_reward=None,
        badge_id=None,
        preferred_types=["Psychic"],
    ),
    "gym_leader_blaine_rematch": Trainer(
        id="gym_leader_blaine_rematch",
        name="Blaine",
        trainer_class="Gym Leader",
        location="Cinnabar Island",
        pokemon=[
            TrainerPokemon(species="ARCANINE", level=62),
            TrainerPokemon(species="RAPIDASH", level=60),
            TrainerPokemon(species="MAGMAR", level=63),
            TrainerPokemon(species="ARCANINE", level=68),
        ],
        prize_money=6800,
        intro_text=[
            "⭐ [bold]Gym Leader Blaine (Rematch):[/bold] [red]Back again, Champion? My fire burns hotter than ever![/red]",
            "",
            "[bold yellow]⚔️  GYM REMATCH START! ⚔️[/bold yellow]",
        ],
        defeat_text=[
            "[red]Hah! You've burned me out — again![/red]",
            "[red]   The Champion's flame truly is brightest![/red]",
        ],
        victory_text=[
            "[red]Hahahaha! Incinerated![/red]",
            "[red]   Return when you've cooled down, Champion![/red]",
        ],
        badge_reward=None,
        badge_id=None,
        preferred_types=["Fire"],
    ),
    "gym_leader_giovanni_rematch": Trainer(
        id="gym_leader_giovanni_rematch",
        name="Giovanni",
        trainer_class="Gym Leader",
        location="Viridian City",
        pokemon=[
            TrainerPokemon(species="NIDOKING", level=65),
            TrainerPokemon(species="NIDOQUEEN", level=65),
            TrainerPokemon(species="RHYDON", level=67),
            TrainerPokemon(species="PERSIAN", level=62),
            TrainerPokemon(species="DUGTRIO", level=65),
        ],
        prize_money=6700,
        intro_text=[
            "⭐ [bold]Gym Leader Giovanni (Rematch):[/bold] [brown]Champion... I reconsidered my path.[/brown]",
            "[brown]   But I have not forgotten how to battle.[/brown]",
            "[brown]   This will be our finest match yet.[/brown]",
            "",
            "[bold yellow]⚔️  GYM REMATCH START! ⚔️[/bold yellow]",
        ],
        defeat_text=[
            "[brown]Magnificent. You truly are the Champion.[/brown]",
            "[brown]   I have no regrets.[/brown]",
        ],
        victory_text=[
            "[brown]Even a Champion can be defeated.[/brown]",
            "[brown]   Come back when you are ready.[/brown]",
        ],
        badge_reward=None,
        badge_id=None,
        preferred_types=["Ground"],
    ),
}


def get_trainer(trainer_id: str) -> Optional[Trainer]:
    """
    Get trainer data by ID.

    Args:
        trainer_id: Unique trainer identifier

    Returns:
        Trainer object or None
    """
    return TRAINERS.get(trainer_id)


def get_trainers_by_location(location: str) -> List[Trainer]:
    """
    Get all trainers for a specific location.

    Args:
        location: Location name

    Returns:
        List of Trainer objects
    """
    return [trainer for trainer in TRAINERS.values() if trainer.location == location]


def get_trainer_class_info(trainer_class: str) -> Dict[str, Any]:
    """
    Get trainer class information.

    Args:
        trainer_class: Trainer class name

    Returns:
        Trainer class info dict
    """
    return TRAINER_CLASSES.get(trainer_class, {})
