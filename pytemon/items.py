"""
Item system for the Pokemon game.

Handles out-of-battle item usage: healing, stat boosters, Rare Candy, and
evolution stones.  Battle-specific item use (Potion during a fight, Pokeball
catch attempts) stays in battle_actions.py.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from textual.widgets import RichLog

from . import evolution as _evo
from . import hm_tm_system as _hm_tm
from .engine import BattleState as _BattleState
from .locations import get_location
from .models import PartyPokemon as _PartyPokemon

if TYPE_CHECKING:
    from .game_state import GameState
    from .models import PartyPokemon


# ---------------------------------------------------------------------------
# Item catalogue
# ---------------------------------------------------------------------------

# Category values used by show_bag and the use-item dispatcher.
CAT_HEAL = "heal"  # Restores HP
CAT_CURE = "cure"  # Cures status condition
CAT_REVIVE = "revive"  # Revives fainted Pokemon
CAT_STAT = "stat"  # Permanent stat boost
CAT_CANDY = "candy"  # Rare Candy — gain one level
CAT_STONE = "stone"  # Evolution stone
CAT_REPEL = "repel"  # Reduces wild encounters
CAT_BALL = "ball"  # Pokeball (battle only)
CAT_ESCAPE = "escape"  # Escape Rope
CAT_HM = "hm"  # Hidden Machine — teaches a move; never consumed
CAT_TM = "tm"  # Technical Machine — teaches a move; consumed on use
CAT_ROD = "rod"  # Fishing rod — used to fish for water Pokemon


@dataclass
class ItemData:
    """An item definition from the item catalogue."""

    desc: str
    emoji: str
    cat: str
    heal: int = 0
    cures_all: bool = False
    cures: Optional[str] = None
    full: bool = False
    stat: str = ""
    amount: int = 0
    steps: int = 0
    move: str = ""  # Move taught by HM/TM (e.g. "SURF")
    badge: str = ""  # Badge required for HM field use (badge ID, e.g. "cascade_badge")

    def __getitem__(self, key: str):
        return getattr(self, key)

    def get(self, key: str, default=None):
        try:
            return getattr(self, key)
        except AttributeError:
            return default


# Each entry: description, emoji, category, extra data used by use_item()
ITEM_DATA: dict[str, ItemData] = {
    # ── Healing ────────────────────────────────────────────────────────────
    "Potion": ItemData(desc="Restores 20 HP", emoji="💊", cat=CAT_HEAL, heal=20),
    "Super Potion": ItemData(desc="Restores 50 HP", emoji="💊", cat=CAT_HEAL, heal=50),
    "Hyper Potion": ItemData(desc="Restores 200 HP", emoji="💊", cat=CAT_HEAL, heal=200),
    "Max Potion": ItemData(desc="Fully restores HP", emoji="💊", cat=CAT_HEAL, heal=9999),
    "Full Restore": ItemData(
        desc="Fully restores HP and cures status",
        emoji="✨",
        cat=CAT_HEAL,
        heal=9999,
        cures_all=True,
    ),
    # ── Revive ─────────────────────────────────────────────────────────────
    "Revive": ItemData(desc="Revives a fainted Pokemon to half HP", emoji="💫", cat=CAT_REVIVE),
    "Max Revive": ItemData(
        desc="Revives a fainted Pokemon to full HP", emoji="💫", cat=CAT_REVIVE, full=True
    ),
    # ── Status cures ───────────────────────────────────────────────────────
    "Antidote": ItemData(desc="Cures poison", emoji="🧪", cat=CAT_CURE, cures="POISON"),
    "Paralyze Heal": ItemData(desc="Cures paralysis", emoji="⚡", cat=CAT_CURE, cures="PARALYSIS"),
    "Awakening": ItemData(desc="Wakes a sleeping Pokemon", emoji="☀️", cat=CAT_CURE, cures="SLEEP"),
    "Burn Heal": ItemData(desc="Cures burn", emoji="🧊", cat=CAT_CURE, cures="BURN"),
    "Ice Heal": ItemData(desc="Cures freeze", emoji="🔥", cat=CAT_CURE, cures="FREEZE"),
    "Full Heal": ItemData(desc="Cures any status condition", emoji="🌟", cat=CAT_CURE, cures=None),
    # ── Stat boosters (permanent) ──────────────────────────────────────────
    "HP Up": ItemData(desc="Raises max HP by 10", emoji="❤️", cat=CAT_STAT, stat="hp", amount=10),
    "Protein": ItemData(
        desc="Raises Attack by 5", emoji="💪", cat=CAT_STAT, stat="attack", amount=5
    ),
    "Iron": ItemData(desc="Raises Defense by 5", emoji="🛡️", cat=CAT_STAT, stat="defense", amount=5),
    "Calcium": ItemData(
        desc="Raises Special by 5", emoji="🔹", cat=CAT_STAT, stat="special", amount=5
    ),
    "Carbos": ItemData(desc="Raises Speed by 5", emoji="⚡", cat=CAT_STAT, stat="speed", amount=5),
    # ── Level-up ───────────────────────────────────────────────────────────
    "Rare Candy": ItemData(desc="Raises a Pokemon's level by 1", emoji="🍬", cat=CAT_CANDY),
    # ── Evolution stones ───────────────────────────────────────────────────
    "Fire Stone": ItemData(desc="Evolves certain Fire-type Pokemon", emoji="🔥", cat=CAT_STONE),
    "Water Stone": ItemData(desc="Evolves certain Water-type Pokemon", emoji="💧", cat=CAT_STONE),
    "Thunder Stone": ItemData(
        desc="Evolves certain Electric-type Pokemon", emoji="⚡", cat=CAT_STONE
    ),
    "Leaf Stone": ItemData(desc="Evolves certain Grass-type Pokemon", emoji="🍃", cat=CAT_STONE),
    "Moon Stone": ItemData(desc="Evolves certain Pokemon at night", emoji="🌙", cat=CAT_STONE),
    # ── Field / misc ───────────────────────────────────────────────────────
    "Repel": ItemData(
        desc="Reduces wild encounters for 10 explores", emoji="🪢", cat=CAT_REPEL, steps=10
    ),
    "Super Repel": ItemData(
        desc="Reduces wild encounters for 20 explores", emoji="🪢", cat=CAT_REPEL, steps=20
    ),
    "Escape Rope": ItemData(desc="Escape from routes and forests", emoji="🪢", cat=CAT_ESCAPE),
    "Pokeball": ItemData(desc="Catch wild Pokemon (battle only)", emoji="🔴", cat=CAT_BALL),
    "Great Ball": ItemData(desc="Better catch rate (battle only)", emoji="🔵", cat=CAT_BALL),
    "Ultra Ball": ItemData(desc="High catch rate (battle only)", emoji="⚫", cat=CAT_BALL),
    "Master Ball": ItemData(
        desc="Catches any wild Pokemon without fail (battle only)", emoji="🟣", cat=CAT_BALL
    ),
    # ── Hidden Machines (HM) ───────────────────────────────────────────────
    "HM01 Cut": ItemData(
        desc="Teaches Cut; clears obstacles (needs Boulder Badge)",
        emoji="✂️",
        cat=CAT_HM,
        move="CUT",
        badge="boulder_badge",
    ),
    "HM02 Fly": ItemData(
        desc="Teaches Fly; fast travel to visited cities (needs Thunder Badge)",
        emoji="🦅",
        cat=CAT_HM,
        move="FLY",
        badge="thunder_badge",
    ),
    "HM03 Surf": ItemData(
        desc="Teaches Surf; cross water routes (needs Cascade Badge)",
        emoji="🌊",
        cat=CAT_HM,
        move="SURF",
        badge="cascade_badge",
    ),
    "HM04 Strength": ItemData(
        desc="Teaches Strength; move heavy boulders (needs Soul Badge)",
        emoji="💪",
        cat=CAT_HM,
        move="STRENGTH",
        badge="soul_badge",
    ),
    "HM05 Flash": ItemData(
        desc="Teaches Flash; lowers accuracy (needs Boulder Badge)",
        emoji="💡",
        cat=CAT_HM,
        move="FLASH",
        badge="boulder_badge",
    ),
    # ── Technical Machines (TM) — all 50 Gen 1 TMs ────────────────────────
    "TM01 Mega Punch": ItemData(
        desc="Teaches Mega Punch (one-time use)", emoji="👊", cat=CAT_TM, move="MEGA PUNCH"
    ),
    "TM02 Razor Wind": ItemData(
        desc="Teaches Razor Wind (one-time use)", emoji="🌪️", cat=CAT_TM, move="RAZOR WIND"
    ),
    "TM03 Swords Dance": ItemData(
        desc="Teaches Swords Dance (one-time use)", emoji="⚔️", cat=CAT_TM, move="SWORDS DANCE"
    ),
    "TM04 Whirlwind": ItemData(
        desc="Teaches Whirlwind (one-time use)", emoji="🌀", cat=CAT_TM, move="WHIRLWIND"
    ),
    "TM05 Mega Kick": ItemData(
        desc="Teaches Mega Kick (one-time use)", emoji="🦵", cat=CAT_TM, move="MEGA KICK"
    ),
    "TM06 Toxic": ItemData(
        desc="Teaches Toxic (one-time use)", emoji="☠️", cat=CAT_TM, move="TOXIC"
    ),
    "TM07 Horn Drill": ItemData(
        desc="Teaches Horn Drill (one-time use)", emoji="🦏", cat=CAT_TM, move="HORN DRILL"
    ),
    "TM08 Body Slam": ItemData(
        desc="Teaches Body Slam (one-time use)", emoji="💥", cat=CAT_TM, move="BODY SLAM"
    ),
    "TM09 Take Down": ItemData(
        desc="Teaches Take Down (one-time use)", emoji="🐂", cat=CAT_TM, move="TAKE DOWN"
    ),
    "TM10 Double-Edge": ItemData(
        desc="Teaches Double-Edge (one-time use)", emoji="⚡", cat=CAT_TM, move="DOUBLE-EDGE"
    ),
    "TM11 BubbleBeam": ItemData(
        desc="Teaches BubbleBeam (one-time use)", emoji="🫧", cat=CAT_TM, move="BUBBLE BEAM"
    ),
    "TM12 Water Gun": ItemData(
        desc="Teaches Water Gun (one-time use)", emoji="💧", cat=CAT_TM, move="WATER GUN"
    ),
    "TM13 Ice Beam": ItemData(
        desc="Teaches Ice Beam (one-time use)", emoji="🧊", cat=CAT_TM, move="ICE BEAM"
    ),
    "TM14 Blizzard": ItemData(
        desc="Teaches Blizzard (one-time use)", emoji="❄️", cat=CAT_TM, move="BLIZZARD"
    ),
    "TM15 Hyper Beam": ItemData(
        desc="Teaches Hyper Beam (one-time use)", emoji="🔫", cat=CAT_TM, move="HYPER BEAM"
    ),
    "TM16 Pay Day": ItemData(
        desc="Teaches Pay Day (one-time use)", emoji="💰", cat=CAT_TM, move="PAY DAY"
    ),
    "TM17 Submission": ItemData(
        desc="Teaches Submission (one-time use)", emoji="🤼", cat=CAT_TM, move="SUBMISSION"
    ),
    "TM18 Counter": ItemData(
        desc="Teaches Counter (one-time use)", emoji="🥊", cat=CAT_TM, move="COUNTER"
    ),
    "TM19 Seismic Toss": ItemData(
        desc="Teaches Seismic Toss (one-time use)", emoji="🌋", cat=CAT_TM, move="SEISMIC TOSS"
    ),
    "TM20 Rage": ItemData(desc="Teaches Rage (one-time use)", emoji="😡", cat=CAT_TM, move="RAGE"),
    "TM21 Mega Drain": ItemData(
        desc="Teaches Mega Drain (one-time use)", emoji="🌿", cat=CAT_TM, move="MEGA DRAIN"
    ),
    "TM22 SolarBeam": ItemData(
        desc="Teaches SolarBeam (one-time use)", emoji="☀️", cat=CAT_TM, move="SOLARBEAM"
    ),
    "TM23 Dragon Rage": ItemData(
        desc="Teaches Dragon Rage (one-time use)", emoji="🐉", cat=CAT_TM, move="DRAGON RAGE"
    ),
    "TM24 Thunderbolt": ItemData(
        desc="Teaches Thunderbolt (one-time use)", emoji="⚡", cat=CAT_TM, move="THUNDERBOLT"
    ),
    "TM25 Thunder": ItemData(
        desc="Teaches Thunder (one-time use)", emoji="🌩️", cat=CAT_TM, move="THUNDER"
    ),
    "TM26 Earthquake": ItemData(
        desc="Teaches Earthquake (one-time use)", emoji="🌍", cat=CAT_TM, move="EARTHQUAKE"
    ),
    "TM27 Fissure": ItemData(
        desc="Teaches Fissure (one-time use)", emoji="🕳️", cat=CAT_TM, move="FISSURE"
    ),
    "TM28 Dig": ItemData(desc="Teaches Dig (one-time use)", emoji="⛏️", cat=CAT_TM, move="DIG"),
    "TM29 Psychic": ItemData(
        desc="Teaches Psychic (one-time use)", emoji="🔮", cat=CAT_TM, move="PSYCHIC"
    ),
    "TM30 Teleport": ItemData(
        desc="Teaches Teleport (one-time use)", emoji="✨", cat=CAT_TM, move="TELEPORT"
    ),
    "TM31 Mimic": ItemData(
        desc="Teaches Mimic (one-time use)", emoji="🪞", cat=CAT_TM, move="MIMIC"
    ),
    "TM32 Double Team": ItemData(
        desc="Teaches Double Team (one-time use)", emoji="👥", cat=CAT_TM, move="DOUBLE TEAM"
    ),
    "TM33 Reflect": ItemData(
        desc="Teaches Reflect (one-time use)", emoji="🛡️", cat=CAT_TM, move="REFLECT"
    ),
    "TM34 Bide": ItemData(desc="Teaches Bide (one-time use)", emoji="⏳", cat=CAT_TM, move="BIDE"),
    "TM35 Metronome": ItemData(
        desc="Teaches Metronome (one-time use)", emoji="🎵", cat=CAT_TM, move="METRONOME"
    ),
    "TM36 Self-Destruct": ItemData(
        desc="Teaches Self-Destruct (one-time use)", emoji="💣", cat=CAT_TM, move="SELFDESTRUCT"
    ),
    "TM37 Egg Bomb": ItemData(
        desc="Teaches Egg Bomb (one-time use)", emoji="🥚", cat=CAT_TM, move="EGG BOMB"
    ),
    "TM38 Fire Blast": ItemData(
        desc="Teaches Fire Blast (one-time use)", emoji="🔥", cat=CAT_TM, move="FIRE BLAST"
    ),
    "TM39 Swift": ItemData(
        desc="Teaches Swift (one-time use)", emoji="⭐", cat=CAT_TM, move="SWIFT"
    ),
    "TM40 Skull Bash": ItemData(
        desc="Teaches Skull Bash (one-time use)", emoji="💀", cat=CAT_TM, move="SKULL BASH"
    ),
    "TM41 Softboiled": ItemData(
        desc="Teaches Softboiled (one-time use)", emoji="🥚", cat=CAT_TM, move="SOFT-BOILED"
    ),
    "TM42 Dream Eater": ItemData(
        desc="Teaches Dream Eater (one-time use)", emoji="😴", cat=CAT_TM, move="DREAM EATER"
    ),
    "TM43 Sky Attack": ItemData(
        desc="Teaches Sky Attack (one-time use)", emoji="🦅", cat=CAT_TM, move="SKY ATTACK"
    ),
    "TM44 Rest": ItemData(desc="Teaches Rest (one-time use)", emoji="💤", cat=CAT_TM, move="REST"),
    "TM45 Thunder Wave": ItemData(
        desc="Teaches Thunder Wave (one-time use)", emoji="⚡", cat=CAT_TM, move="THUNDER WAVE"
    ),
    "TM46 Psywave": ItemData(
        desc="Teaches Psywave (one-time use)", emoji="🌀", cat=CAT_TM, move="PSYWAVE"
    ),
    "TM47 Explosion": ItemData(
        desc="Teaches Explosion (one-time use)", emoji="💥", cat=CAT_TM, move="EXPLOSION"
    ),
    "TM48 Rock Slide": ItemData(
        desc="Teaches Rock Slide (one-time use)", emoji="🪨", cat=CAT_TM, move="ROCK SLIDE"
    ),
    "TM49 Tri Attack": ItemData(
        desc="Teaches Tri Attack (one-time use)", emoji="🔺", cat=CAT_TM, move="TRI ATTACK"
    ),
    "TM50 Substitute": ItemData(
        desc="Teaches Substitute (one-time use)", emoji="🪆", cat=CAT_TM, move="SUBSTITUTE"
    ),
    # ── Fishing Rods ──────────────────────────────────────────────────────
    "Old Rod": ItemData(
        desc="A basic fishing rod — mostly catches Magikarp",
        emoji="🎣",
        cat=CAT_ROD,
    ),
    "Good Rod": ItemData(
        desc="A better fishing rod — catches a wider variety",
        emoji="🎣",
        cat=CAT_ROD,
    ),
    "Super Rod": ItemData(
        desc="The best fishing rod — finds rare water Pokemon",
        emoji="🎣",
        cat=CAT_ROD,
    ),
}


def get_item(name: str) -> Optional[ItemData]:
    """Return item data for ``name`` (case-insensitive), or None."""
    for k, v in ITEM_DATA.items():
        if k.lower() == name.lower():
            return v
    return None


def get_item_canonical_name(name: str) -> Optional[str]:
    """Return the canonical (correctly capitalised) name for an item, or None."""
    for k in ITEM_DATA:
        if k.lower() == name.lower():
            return k
    return None


# ---------------------------------------------------------------------------
# Out-of-battle item use
# ---------------------------------------------------------------------------


def use_item_outside_battle(
    game_state: GameState,
    item_name: str,
    target: Optional[str],
    output: RichLog,
) -> bool:
    """
    Use an item outside of battle.

    Args:
        game_state: Current game state.
        item_name:  Canonical item name (e.g. ``"Rare Candy"``).
        target:     Optional Pokemon name or slot number (e.g. ``"Charmander"``
                    or ``"1"``).  Required for stones, stat boosters, Rare
                    Candy, and Revive.  For plain healing items the active
                    (first non-fainted) Pokemon is used when target is None.
        output:     RichLog widget to write results to.

    Returns:
        True if the item was consumed successfully.
    """
    data = get_item(item_name)
    if not data:
        output.write(f"[red]❌ Unknown item: {item_name}[/red]")
        return False

    canonical = get_item_canonical_name(item_name)
    if canonical is None:
        return False  # guard: keeps canonical as str below
    items = game_state.game_data.get("items", {})
    if items.get(canonical, 0) <= 0:
        output.write(f"[red]❌ You have no {canonical}![/red]")
        return False

    cat = data["cat"]

    # ── Escape Rope ──────────────────────────────────────────────────────
    if cat == CAT_ESCAPE:
        return _use_escape_rope(game_state, canonical, output)

    # ── Repel ────────────────────────────────────────────────────────────
    if cat == CAT_REPEL:
        return _use_repel(game_state, canonical, data, output)

    # ── Battle-only items ────────────────────────────────────────────────
    if cat == CAT_BALL:
        output.write("")
        output.write(f"[yellow]⚠ {canonical} can only be used in battle.[/yellow]")
        output.write("")
        return False

    # ── HM / TM — teach move to Pokemon ─────────────────────────────────
    if cat in (CAT_HM, CAT_TM):
        return _use_hm_tm(game_state, canonical, data, target, output)

    # ── Fishing Rod ──────────────────────────────────────────────────────
    if cat == CAT_ROD:
        output.write("")
        output.write(f"[yellow]⚠ Use 'fish' to go fishing with your {canonical}![/yellow]")
        output.write("[dim]Example: 'fish'  or  'fish with old rod'[/dim]")
        output.write("")
        return False

    # ── Resolve target Pokemon ────────────────────────────────────────────
    if cat in (CAT_STAT, CAT_STONE, CAT_CANDY):
        # These always require an explicit target
        if not target:
            output.write("")
            output.write(f"[yellow]⚠ Usage: Use {canonical} on <Pokemon name or slot>[/yellow]")
            output.write(
                "[dim]Example: 'Use Rare Candy on Charmander' or 'Use Fire Stone on Growlithe'[/dim]"
            )
            output.write("")
            return False
        pokemon, _ = game_state.find_pokemon(target)
        if not pokemon:
            output.write(f"[red]❌ Pokemon not found: {target}[/red]")
            return False
    elif cat == CAT_REVIVE:
        # Revive targets a fainted Pokemon; optional target defaults to first fainted
        if target:
            pokemon, _ = game_state.find_pokemon(target)
            if not pokemon:
                output.write(f"[red]❌ Pokemon not found: {target}[/red]")
                return False
            if pokemon.get("hp", 0) > 0:
                output.write(f"[yellow]⚠ {pokemon['name']} is not fainted![/yellow]")
                return False
        else:
            pokemon = _first_fainted(game_state)
            if not pokemon:
                output.write("")
                output.write("[yellow]⚠ None of your Pokemon have fainted![/yellow]")
                output.write("")
                return False
    elif cat in (CAT_HEAL, CAT_CURE):
        if target:
            pokemon, _ = game_state.find_pokemon(target)
            if not pokemon:
                output.write(f"[red]❌ Pokemon not found: {target}[/red]")
                return False
        else:
            pokemon = game_state.get_active_pokemon()
            if not pokemon:
                output.write("[red]❌ No active Pokemon to heal![/red]")
                return False
    else:
        pokemon = None

    # ── Dispatch ─────────────────────────────────────────────────────────
    # All dispatch branches that call helpers require a non-None pokemon;
    # the branches above return early if the resolved pokemon is None.
    # If somehow pokemon is None here (unrecognised cat), bail out.
    if pokemon is None:
        output.write(f"[yellow]⚠ {canonical} has no out-of-battle effect.[/yellow]")
        return False

    if cat == CAT_HEAL:
        return _use_heal(game_state, canonical, data, pokemon, output)

    if cat == CAT_CURE:
        return _use_cure(game_state, canonical, data, pokemon, output)

    if cat == CAT_REVIVE:
        return _use_revive(game_state, canonical, data, pokemon, output)

    if cat == CAT_STAT:
        return _use_stat_booster(game_state, canonical, data, pokemon, output)

    if cat == CAT_CANDY:
        return _use_rare_candy(game_state, canonical, pokemon, output)

    if cat == CAT_STONE:
        return _use_stone(game_state, canonical, pokemon, output)

    output.write(f"[yellow]⚠ {canonical} has no out-of-battle effect.[/yellow]")
    return False


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _consume(game_state: GameState, item_name: str) -> None:
    """Remove one unit of item_name from the bag."""
    items = game_state.game_data.get("items", {})
    if item_name in items:
        items[item_name] -= 1
        if items[item_name] <= 0:
            del items[item_name]


def _first_fainted(game_state: GameState) -> Optional[PartyPokemon]:
    for p in game_state.game_data.get("pokemon", []):
        if isinstance(p, _PartyPokemon) and p.hp <= 0:
            return p
        elif isinstance(p, dict) and p.get("hp", 1) <= 0:
            return p  # type: ignore[return-value]
    return None


def _use_heal(
    game_state: GameState, name: str, data: ItemData, pokemon: PartyPokemon, output: RichLog
) -> bool:
    max_hp = pokemon.get("max_hp", pokemon["hp"])
    if pokemon["hp"] >= max_hp:
        output.write("")
        output.write(f"[yellow]⚠ {pokemon['name']}'s HP is already full![/yellow]")
        output.write("")
        return False

    heal_amount = data.get("heal", 0)
    restored = min(heal_amount, max_hp - pokemon["hp"])
    pokemon["hp"] = min(pokemon["hp"] + heal_amount, max_hp)

    if data.get("cures_all"):
        pokemon["status"] = None

    _consume(game_state, name)
    output.write("")
    output.write(f"[green]{data['emoji']} {pokemon['name']} recovered {restored} HP![/green]")
    output.write(f"[dim]  HP: {pokemon['hp']}/{max_hp}[/dim]")
    output.write("")
    return True


def _use_cure(
    game_state: GameState, name: str, data: ItemData, pokemon: PartyPokemon, output: RichLog
) -> bool:
    cures = data.get("cures")  # None means "any status"
    current_status = pokemon.get("status")

    if not current_status:
        output.write("")
        output.write(f"[yellow]⚠ {pokemon['name']} has no status condition.[/yellow]")
        output.write("")
        return False

    if cures and current_status != cures:
        output.write("")
        output.write(f"[yellow]⚠ {name} doesn't cure {current_status.lower()}.[/yellow]")
        output.write("")
        return False

    pokemon["status"] = None
    _consume(game_state, name)
    output.write("")
    output.write(
        f"[green]{data['emoji']} {pokemon['name']} was cured of {current_status.lower()}![/green]"
    )
    output.write("")
    return True


def _use_revive(
    game_state: GameState, name: str, data: ItemData, pokemon: PartyPokemon, output: RichLog
) -> bool:
    max_hp = pokemon.get("max_hp", 50)
    if data.get("full"):
        restore_to = max_hp
    else:
        restore_to = max(1, max_hp // 2)

    pokemon["hp"] = restore_to
    pokemon["status"] = None
    _consume(game_state, name)
    output.write("")
    output.write(f"[green]{data['emoji']} {pokemon['name']} was revived![/green]")
    output.write(f"[dim]  HP: {pokemon['hp']}/{max_hp}[/dim]")
    output.write("")
    return True


def _use_stat_booster(
    game_state: GameState, name: str, data: ItemData, pokemon: PartyPokemon, output: RichLog
) -> bool:
    stat = data.get("stat", "")
    amount = data.get("amount", 0)

    # Store bonuses permanently on the pokemon dict
    bonus_key = f"{stat}_bonus"
    pokemon[bonus_key] = pokemon.get(bonus_key, 0) + amount

    # Also update the actual stat
    if stat == "hp":
        old_max = pokemon.get("max_hp", 50)
        pokemon["max_hp"] = old_max + amount
        pokemon["hp"] = min(pokemon.get("hp", old_max), pokemon["max_hp"])
        stat_display = "max HP"
        new_val = pokemon["max_hp"]
    else:
        pokemon["stats"] = pokemon.get("stats", {})  # type: ignore[assignment]
        new_stat_val = (pokemon["stats"].get(stat, 50) or 50) + amount  # type: ignore[misc]
        pokemon["stats"][stat] = new_stat_val  # type: ignore[literal-required]
        stat_display = stat.capitalize()
        new_val: int = new_stat_val

    _consume(game_state, name)
    output.write("")
    output.write(
        f"[green]{data['emoji']} {pokemon['name']}'s {stat_display} rose to {new_val}! (+{amount})[/green]"
    )
    output.write("")
    return True


def _use_rare_candy(
    game_state: GameState, name: str, pokemon: PartyPokemon, output: RichLog
) -> bool:
    old_level = pokemon.get("level", 1)
    if old_level >= 100:
        output.write("")
        output.write(f"[yellow]⚠ {pokemon['name']} is already at level 100![/yellow]")
        output.write("")
        return False

    new_level = old_level + 1
    pokemon["level"] = new_level

    # Apply the stat gains for this level-up
    engine = _BattleState()
    engine.apply_level_up_stats(pokemon)

    _consume(game_state, name)
    output.write("")
    output.write(f"[bold yellow]🍬 {pokemon['name']} grew to Level {new_level}![/bold yellow]")

    # Check for natural level-up evolution
    evo_target = _evo.get_level_evolution(pokemon)
    if evo_target:
        output.write(f"[dim]  → {pokemon['name']} can evolve into {evo_target}![/dim]")
        output.write(f"[dim]    Type 'evolve {pokemon['name']}' to trigger evolution.[/dim]")

    output.write("")
    return True


def _use_stone(game_state: GameState, name: str, pokemon: PartyPokemon, output: RichLog) -> bool:
    pokemon_name = pokemon.get("name", "POKÉMON")
    evo_target = _evo.get_stone_evolution(pokemon, name)
    if not evo_target:
        output.write("")
        output.write(f"[yellow]⚠ The {name} has no effect on {pokemon_name}.[/yellow]")
        output.write("")
        return False

    _consume(game_state, name)
    success = _evo.force_evolve(game_state, pokemon, evo_target, output)
    if not success:
        # Refund if force_evolve failed (shouldn't normally happen)
        items = game_state.game_data.setdefault("items", {})
        items[name] = items.get(name, 0) + 1
    return success


def _find_nearest_town(start_name: str) -> str | None:
    """BFS through the location graph to find the name of the nearest reachable town."""
    visited: set[str] = {start_name}
    queue: deque[str] = deque([start_name])
    while queue:
        loc_name = queue.popleft()
        loc = get_location(loc_name)
        if loc is None:
            continue
        for exit_name in loc.exits:
            if exit_name in visited:
                continue
            visited.add(exit_name)
            dest = get_location(exit_name)
            if dest and dest.type == "town":
                return exit_name
            queue.append(exit_name)
    return None


def _use_escape_rope(game_state: GameState, name: str, output: RichLog) -> bool:
    location = game_state.current_location
    if not location:
        output.write("[red]❌ No current location![/red]")
        return False

    if location.type == "town":
        output.write("")
        output.write("[yellow]⚠ You're already in a town — no need for an Escape Rope![/yellow]")
        output.write("")
        return False

    # BFS to find the nearest town (works even when no town is a direct exit)
    town_name = _find_nearest_town(location.name)
    if town_name:
        dest = get_location(town_name)
        if dest:
            _consume(game_state, name)
            game_state.game_data["previous_location"] = location.name
            game_state.current_location = dest
            game_state.game_data["location"] = dest.name
            game_state.game_data.setdefault("route_progress", {})[dest.name] = 0
            output.write("")
            output.write("[bold cyan]🪢 You used the Escape Rope![/bold cyan]")
            output.write(f"[cyan]You were whisked back to {dest.name}![/cyan]")
            output.write("")
            return True

    output.write("")
    output.write("[yellow]⚠ The Escape Rope can't be used here.[/yellow]")
    output.write("")
    return False


def _use_repel(game_state: GameState, name: str, data: ItemData, output: RichLog) -> bool:
    steps = data.get("steps", 10)
    current = game_state.game_data.get("repel_steps", 0)
    game_state.game_data["repel_steps"] = current + steps
    _consume(game_state, name)
    output.write("")
    output.write(
        f"[green]🪢 {name} used! Wild Pokemon will be less likely to appear for {steps} explores.[/green]"
    )
    if current > 0:
        output.write(f"[dim]  (Repel now active for {current + steps} more explores)[/dim]")
    output.write("")
    return True


def _use_hm_tm(
    game_state: GameState,
    name: str,
    data: ItemData,
    target: Optional[str],
    output: RichLog,
) -> bool:
    """Teach the move from an HM or TM to a target Pokemon.

    HMs are never consumed; TMs are consumed on successful use.

    Args:
        game_state: Current game state.
        name:       Canonical item name (e.g. ``"HM03 Surf"``).
        data:       ItemData for this item.
        target:     Pokemon name or slot to teach the move to.
        output:     RichLog widget.

    Returns:
        True if the move was successfully taught.
    """
    move_name = data.get("move", "")
    if not move_name:
        output.write(f"[red]❌ {name} has no move data.[/red]")
        return False

    is_hm = data["cat"] == CAT_HM

    if not target:
        party = game_state.game_data.get("pokemon", [])
        example_name = party[0].get("name", "Pikachu") if party else "Pikachu"
        output.write("")
        output.write(f"[yellow]⚠ Usage: use {name} on <Pokemon name or slot>[/yellow]")
        output.write(f"[dim]Example: 'use {name} on {example_name}'[/dim]")
        output.write("")
        return False

    pokemon, _ = game_state.find_pokemon(target)
    if not pokemon:
        output.write(f"[red]❌ Pokemon not found: {target}[/red]")
        return False

    success = _hm_tm.teach_move(game_state, move_name, pokemon, name, is_hm, output)
    if success and not is_hm:
        _consume(game_state, name)
    return success
