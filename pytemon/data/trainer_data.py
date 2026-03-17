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
