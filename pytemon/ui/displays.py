"""
UI display functions for Pokemon Terminal.

This module handles all informational display screens including party, bag,
help, status, badge case, and Pokemon inspection.
"""

from typing import TYPE_CHECKING

from textual.widgets import RichLog

from .formatters import format_experience_bar, format_experience_text, format_hp_bar

if TYPE_CHECKING:
    from ..game_state import GameState


def activate_pikachu_mode(game_state: "GameState", output: RichLog) -> None:
    """
    Activate Pokemon Yellow Easter egg mode.

    Args:
        game_state: The game state
        output: The RichLog widget to write to
    """
    if game_state.game_data.get("pokemon", []):
        # Player already has Pokemon, can't activate
        output.write("")
        output.write("[dim]...Nothing happened.[/dim]")
        output.write("")
        return

    if game_state.pikachu_mode:
        # Already activated
        output.write("")
        output.write("[yellow]You're already running late! Better hurry to the lab![/yellow]")
        output.write("")
        return

    # Activate Pikachu mode
    game_state.pikachu_mode = True
    game_state.game_data["pikachu_mode"] = True

    output.write("")
    output.write("[bold yellow]═══════════════════════════════════════════[/bold yellow]")
    output.write("[bold yellow]⏰ Oh no! You overslept! ⏰[/bold yellow]")
    output.write("[bold yellow]═══════════════════════════════════════════[/bold yellow]")
    output.write("")
    output.write("[yellow]You rush downstairs and run to Professor Oak's Lab![/yellow]")
    output.write(
        "[yellow]By the time you arrive, the other trainers have already chosen their Pokemon![/yellow]"
    )
    output.write("")
    output.write("[dim]A special encounter awaits you...[/dim]")
    output.write("")


def show_party(game_state: "GameState", output: RichLog, ensure_battle_ready_callback) -> None:
    """
    Display the Pokemon party.

    Args:
        game_state: The game state
        output: The RichLog widget to write to
        ensure_battle_ready_callback: Callback to ensure Pokemon has battle stats
    """
    output.write("")
    output.write("[bold cyan]👥 Your Pokemon Party[/bold cyan]")
    output.write("")

    pokemon = game_state.game_data.get("pokemon", [])
    if not pokemon:
        output.write("[dim]You don't have any Pokemon yet![/dim]")
        output.write("")
        return

    for i, p in enumerate(pokemon, 1):
        # Handle both old string format and new dict/PartyPokemon format
        if not isinstance(p, str):
            # Ensure Pokemon has all required fields
            ensure_battle_ready_callback(p)
            name = p["name"]
            level = p.get("level", 5)
            hp = p.get("hp", p.get("max_hp", 0))
            max_hp = p.get("max_hp", 0)
            types = "/".join(p.get("types", []))
            no_evolve = p.get("no_evolve", False)
            status = p.get("status") or ""
            status_str = f" [[red]{status}[/red]]" if status else ""
            evolve_str = " [dim]⚡[/dim]" if no_evolve else ""
            hp_bar = format_hp_bar(hp, max_hp, width=12)
            output.write(f"  {i}. [bold]{name}[/bold] Lv.{level}{status_str}{evolve_str}")
            output.write(f"     {hp_bar} {hp}/{max_hp} HP  [dim]{types}[/dim]")

            # Show experience
            exp = p.get("experience", 0)
            next_level_exp = p.get("next_level_exp", 0)
            exp_text = format_experience_text(exp, next_level_exp)
            output.write(f"     [dim]{exp_text}[/dim]")

            moves = p.get("moves", [])
            if moves:
                move_parts = [f"{m['name']} {m['pp']}/{m['max_pp']}PP" for m in moves]
                output.write(f"     [dim]Moves: {', '.join(move_parts)}[/dim]")
            output.write("")
        else:
            output.write(f"  {i}. {p}")
            output.write("")
    output.write(f"[dim]Party size: {len(pokemon)}/6[/dim]")
    # Show PC tally if anything is stored
    from .. import pc_system

    pc_total = pc_system.get_total_in_pc(game_state)
    if pc_total > 0:
        output.write(f"[dim]💾 Bill's PC: {pc_total} Pokemon stored — type 'pc' to manage[/dim]")
    output.write("")


def populate_party_overview(log: RichLog, pokemon: list, ensure_battle_ready_callback) -> None:
    """
    Populate a RichLog with the party overview: 2 columns, up to 3 rows of 2 Pokémon each.

    Args:
        log: The RichLog widget to write into
        pokemon: List of party Pokémon dicts
        ensure_battle_ready_callback: Callback to fill in missing battle fields
    """
    from rich.table import Table as RichTable

    real_pokemon = [p for p in pokemon if not isinstance(p, str)]
    if not real_pokemon:
        log.write("[dim]Your party is empty![/dim]")
        return

    log.write("[bold cyan]👥 Party Overview[/bold cyan]")
    log.write("")

    # Build a 2-column table, up to 3 rows
    table = RichTable.grid(padding=(0, 2))
    table.add_column(ratio=1)
    table.add_column(ratio=1)

    def _card(p: dict) -> str:
        """Build a Rich markup card string for one Pokémon."""
        ensure_battle_ready_callback(p)
        name = p.get("name", "???")
        level = p.get("level", 1)
        hp = p.get("hp", 0)
        max_hp = p.get("max_hp", 1)
        types = "/".join(p.get("types", []))
        status = p.get("status") or ""
        exp = p.get("experience", 0)
        nxt = p.get("next_level_exp", 0)
        no_evolve = p.get("no_evolve", False)

        hp_bar = format_hp_bar(hp, max_hp, width=16)
        ratio = max(0.0, hp / max_hp) if max_hp > 0 else 0
        hp_color = "green" if ratio > 0.5 else ("yellow" if ratio > 0.25 else "red")

        exp_bar = ""
        if nxt > 0:
            exp_filled = int((exp / nxt) * 16)
            exp_bar = "[cyan]" + "█" * exp_filled + "[/cyan]" + "░" * (16 - exp_filled)

        status_str = f"  [[red]{status}[/red]]" if status else ""
        evolve_str = "  [dim]⚡ No Evolve[/dim]" if no_evolve else ""

        lines = [
            f"[bold]{name}[/bold]  Lv.[bold]{level}[/bold]{status_str}{evolve_str}",
            f"[dim]{types}[/dim]",
            f"{hp_bar}",
            f"  [{hp_color}]{hp}[/{hp_color}] / {max_hp} HP",
        ]
        if nxt > 0:
            lines.append(f"{exp_bar}")
            lines.append(f"  [dim]{exp} / {nxt} EXP[/dim]")
        else:
            lines.append(f"  [dim]{exp} EXP[/dim]")
        return "\n".join(lines)

    # Fill up to 6 slots, padding with None for empty
    slots: list = list(real_pokemon) + [None] * (6 - len(real_pokemon))

    for row_idx in range(3):
        left = slots[row_idx * 2]
        right = slots[row_idx * 2 + 1]
        if left is None and right is None:
            break
        left_cell = _card(left) if left else "[dim]  — empty —[/dim]"
        right_cell = _card(right) if right else "[dim]  — empty —[/dim]"
        table.add_row(left_cell, right_cell)
        if row_idx < 2 and (
            slots[(row_idx + 1) * 2] is not None or slots[(row_idx + 1) * 2 + 1] is not None
        ):
            table.add_row("", "")  # spacer row

    log.write(table)
    log.write("")
    log.write(
        f"[dim]Party: {len(real_pokemon)}/6  ·  type 'party' to refresh  ·  use tabs for details[/dim]"
    )


def populate_party_detail(log: RichLog, p: dict, slot: int, ensure_battle_ready_callback) -> None:
    """
    Populate a RichLog with a detailed view of a single party Pokémon.

    Args:
        log: The RichLog widget to write into
        p: The Pokémon dict
        slot: 1-based slot index
        ensure_battle_ready_callback: Callback to fill in missing battle fields
    """
    from ..data import POKEMON, get_move

    # Human-readable descriptions for move effect keys
    EFFECT_DESC = {
        "absorb": "Restores ½ dmg dealt as HP",
        "bad_poison": "Badly poisons the target",
        "burn": "May burn the target",
        "confuse": "May confuse the target",
        "conversion": "Changes user type to move type",
        "counter": "Returns double physical damage",
        "disable": "Disables targets last move",
        "double_hit": "Hits twice",
        "fixed_damage": "Deals fixed damage",
        "flinch": "May cause flinch",
        "focus_energy": "Raises critical-hit ratio",
        "freeze": "May freeze the target",
        "half_hp": "Deals damage equal to ½ user HP",
        "high_crit": "High critical-hit ratio",
        "leech_seed": "Drains HP each turn",
        "level_damage": "Damage equals user level",
        "light_screen": "Halves special damage for 5 turns",
        "lock_on": "Next move always hits",
        "lower_accuracy": "Lowers target accuracy",
        "lower_attack": "Lowers target attack",
        "lower_defense": "Lowers target defense",
        "lower_defense_2": "Sharply lowers target defense",
        "lower_special": "Lowers target special",
        "lower_speed": "Lowers target speed",
        "metronome": "Uses a random move",
        "mimic": "Copies targets last move",
        "mirror_move": "Uses the same move as target",
        "mist": "Prevents stat reduction for 5 turns",
        "multi_hit": "Hits 2–5 times",
        "ohko": "One-hit KO",
        "paralysis": "May paralyze the target",
        "payday": "Scatters coins on hit",
        "poison": "May poison the target",
        "priority": "Always strikes first",
        "rage": "Attack rises each time user is hit",
        "raise_attack": "Raises user attack",
        "raise_attack_2": "Sharply raises user attack",
        "raise_defense": "Raises user defense",
        "raise_defense_2": "Sharply raises user defense",
        "raise_evasion": "Raises user evasion",
        "raise_evasion_2": "Sharply raises user evasion",
        "raise_special": "Raises user special",
        "raise_special_2": "Sharply raises user special",
        "raise_speed_2": "Sharply raises user speed",
        "recharge": "User must recharge next turn",
        "recoil": "User takes ¼ damage as recoil",
        "recover": "Restores up to ½ max HP",
        "reflect": "Halves physical damage for 5 turns",
        "rest": "Sleeps to fully restore HP & status",
        "roar": "Ends wild battles; forces switch",
        "safeguard": "Protects from status for 5 turns",
        "selfdestruct": "User faints after attacking",
        "sleep": "Puts target to sleep",
        "substitute": "Creates a decoy using ¼ HP",
        "teleport": "Escapes from wild battles",
        "transform": "Copies targets moves and stats",
        "trap": "Traps target for 2–5 turns",
        "whirlwind": "Ends wild battles; forces switch",
    }

    ensure_battle_ready_callback(p)

    name = p.get("name", "???")
    level = p.get("level", 1)
    types = p.get("types", [])
    hp = p.get("hp", 0)
    max_hp = p.get("max_hp", 1)
    # Stats live in the nested 'stats' dict
    stats = p.get("stats", {})
    atk = stats.get("attack", "?")
    defense = stats.get("defense", "?")
    spa = stats.get("special", "?")
    spd = stats.get("speed", "?")
    exp = p.get("experience", 0)
    nxt = p.get("next_level_exp", 0)
    status = p.get("status") or "None"
    no_evolve = p.get("no_evolve", False)
    nickname = p.get("nickname", "")

    # Look up dex number
    dex_num = "???"
    for num, species in POKEMON.items():
        if species.get("name", "").lower() == name.lower():
            dex_num = str(num)
            break

    hp_bar = format_hp_bar(hp, max_hp, width=22)
    ratio = max(0.0, hp / max_hp) if max_hp > 0 else 0
    hp_color = "green" if ratio > 0.5 else ("yellow" if ratio > 0.25 else "red")

    # Type colour mapping (simple)
    type_colors = {
        "Fire": "red",
        "Water": "blue",
        "Grass": "green",
        "Electric": "yellow",
        "Psychic": "magenta",
        "Ice": "cyan",
        "Fighting": "red3",
        "Poison": "purple",
        "Ground": "dark_goldenrod",
        "Flying": "sky_blue1",
        "Bug": "chartreuse3",
        "Rock": "tan",
        "Ghost": "medium_purple",
        "Dragon": "dark_violet",
        "Normal": "white",
        "Steel": "steel_blue",
    }
    type_badges = " ".join(
        f"[bold {type_colors.get(t, 'white')}]{t}[/bold {type_colors.get(t, 'white')}]"
        for t in types
    )

    display_name = f"{name}" + (f' "{nickname}"' if nickname else "")

    log.write("")
    log.write(f"[bold cyan]{'━' * 38}[/bold cyan]")
    log.write(f"  [bold white]#{dex_num:>3}  {display_name}[/bold white]  {type_badges}")
    log.write(f"  [bold]Level {level}[/bold]")
    log.write(f"[bold cyan]{'━' * 38}[/bold cyan]")
    log.write("")

    # HP
    log.write(f"  HP   {hp_bar}")
    log.write(f"       [{hp_color}]{hp}[/{hp_color}] / {max_hp}")
    log.write("")

    # Stats in two-column layout
    log.write(
        f"  [bold]ATK[/bold] [yellow]{atk:>3}[/yellow]      [bold]DEF[/bold] [yellow]{defense:>3}[/yellow]"
    )
    log.write(
        f"  [bold]SPC[/bold] [yellow]{spa:>3}[/yellow]      [bold]SPD[/bold] [yellow]{spd:>3}[/yellow]"
    )
    log.write("")

    # Experience
    if nxt > 0:
        exp_pct = int((exp / nxt) * 22)
        exp_bar = "[cyan]" + "█" * exp_pct + "[/cyan]" + "░" * (22 - exp_pct)
        log.write(f"  EXP  {exp_bar}")
        log.write(f"       [dim]{exp} / {nxt} to Level {level + 1}[/dim]")
    else:
        log.write(f"  EXP  [cyan]{'█' * 22}[/cyan]")
        log.write(f"       [dim]{exp} EXP  (Max Level)[/dim]")
    log.write("")

    # Status & flags
    status_markup = f"[red]{status}[/red]" if status != "None" else "[dim]None[/dim]"
    log.write(f"  Status: {status_markup}  " + ("[dim]⚡ No Evolve[/dim]" if no_evolve else ""))
    log.write("")

    # Moves
    moves = p.get("moves", [])
    if moves:
        log.write("  [bold yellow]Moves[/bold yellow]")
        log.write(f"  {'━' * 34}")
        for m in moves:
            m_name = m.get("name", "???")
            m_pp = m.get("pp", 0)
            m_max_pp = m.get("max_pp", m_pp)
            # Look up move data
            try:
                md = get_move(m_name)
                m_type = md.type if md else "?"
                m_cat = md.category if md else "?"
                m_pow = md.power if md else 0
                m_acc = md.accuracy if md else 0
            except Exception:
                m_type, m_cat, m_pow, m_acc = "?", "?", 0, 0

            t_color = type_colors.get(m_type, "white")
            pp_color = (
                "green" if m_pp == m_max_pp else ("yellow" if m_pp > m_max_pp // 3 else "red")
            )
            pow_str = f"Pow {m_pow:>3}" if m_pow else "  Status  "
            acc_str = f"Acc {m_acc}%" if m_acc > 0 else "  ─────  "
            # Effect description
            effect_key = getattr(md, "effect", None) if md else None
            effect_chance = getattr(md, "effect_chance", None) if md else None
            desc = EFFECT_DESC.get(effect_key, "") if effect_key else ""
            if desc and effect_chance and effect_chance < 100:
                desc = f"{desc} ({effect_chance}%)"
            log.write(f"  [bold]{m_name:<16}[/bold]  [{pp_color}]{m_pp}/{m_max_pp} PP[/{pp_color}]")
            log.write(
                f"    [bold {t_color}]{m_type:<10}[/bold {t_color}]"
                f"[dim]{m_cat:<10}[/dim]"
                f"  {pow_str}  {acc_str}"
            )
            if desc:
                log.write(f"    [dim italic]{desc}[/dim italic]")
        log.write("")
    else:
        log.write("  [dim]No moves learned yet.[/dim]")
        log.write("")


def show_bag(game_state: "GameState", output: RichLog) -> None:
    """
    Display the items in the bag, grouped by category with descriptions.

    Args:
        game_state: The game state
        output: The RichLog widget to write to
    """
    from .. import items as _items

    output.write("")
    output.write("[bold cyan]🎒 Your Bag[/bold cyan]")
    output.write("")

    bag = game_state.game_data.get("items", {})
    if not bag:
        output.write("[dim]Your bag is empty![/dim]")
        output.write("[dim]Buy items at the Pokemart, or find them while exploring.[/dim]")
        output.write("")
        return

    # ── Build category buckets ──────────────────────────────────────────────
    CATEGORY_LABELS = {
        _items.CAT_HEAL: ("💊 Healing Items", "use <item>  or  use <item> on <pokemon>"),
        _items.CAT_REVIVE: ("💫 Revival Items", "use <item>  or  use <item> on <pokemon>"),
        _items.CAT_CURE: ("🧪 Status Cures", "use <item>  or  use <item> on <pokemon>"),
        _items.CAT_STAT: ("💪 Vitamins", "use <item> on <pokemon>"),
        _items.CAT_CANDY: ("🍬 Rare Candy", "use Rare Candy on <pokemon>"),
        _items.CAT_STONE: ("💎 Evolution Stones", "use <stone> on <pokemon>"),
        _items.CAT_REPEL: ("🪢 Repels", "use <item>  (works immediately)"),
        _items.CAT_ESCAPE: ("🪢 Field Items", "use Escape Rope"),
        _items.CAT_BALL: ("🔴 Pokéballs", "used automatically in battle"),
        _items.CAT_HM: (
            "📀 Hidden Machines (HM)",
            "use <hm> on <pokemon>  or  use surf / fly / cut",
        ),
        _items.CAT_TM: ("💿 Technical Machines (TM)", "use <tm> on <pokemon>  (one-time use)"),
        _items.CAT_ROD: ("🎣 Fishing Rods", "fish  or  fish with <rod>"),
        "unknown": ("📦 Other Items", "use <item>"),
    }
    CATEGORY_ORDER = [
        _items.CAT_HEAL,
        _items.CAT_REVIVE,
        _items.CAT_CURE,
        _items.CAT_STAT,
        _items.CAT_CANDY,
        _items.CAT_STONE,
        _items.CAT_REPEL,
        _items.CAT_ESCAPE,
        _items.CAT_BALL,
        _items.CAT_HM,
        _items.CAT_TM,
        _items.CAT_ROD,
        "unknown",
    ]

    buckets: dict[str, list[tuple[str, int, dict]]] = {cat: [] for cat in CATEGORY_ORDER}

    for item_name, quantity in bag.items():
        data = _items.get_item(item_name)
        cat = data["cat"] if data else "unknown"
        if cat not in buckets:
            cat = "unknown"
        buckets[cat].append((item_name, quantity, data or {}))

    # ── Print each non-empty category ──────────────────────────────────────
    for cat in CATEGORY_ORDER:
        entries = buckets[cat]
        if not entries:
            continue
        label, hint = CATEGORY_LABELS[cat]
        output.write(f"  [bold]{label}[/bold]")
        for item_name, quantity, data in entries:
            emoji = data.get("emoji", "•")
            desc = data.get("desc", "")
            qty_s = f"[cyan]x{quantity}[/cyan]"
            output.write(f"    {emoji} [green]{item_name}[/green] {qty_s}  [dim]{desc}[/dim]")
        output.write(f"  [dim]  ↳ {hint}[/dim]")
        output.write("")

    # ── Repel counter ──────────────────────────────────────────────────────
    repel_steps = game_state.game_data.get("repel_steps", 0)
    if repel_steps > 0:
        output.write(f"  [yellow]🪢 Repel active — {repel_steps} explore(s) remaining[/yellow]")
        output.write("")


def show_badge_case(game_state: "GameState", output: RichLog) -> None:
    """
    Display the player's badge case.

    Args:
        game_state: The game state
        output: The RichLog widget to write to
    """
    # Import here to avoid circular import
    from ..gym_system import show_badge_case as show_badges

    show_badges(game_state, output)


def inspect_pokemon(
    game_state: "GameState", output: RichLog, target: str, ensure_battle_ready_callback
) -> None:
    """
    Display detailed information about a specific Pokemon.

    Args:
        game_state: The game state
        output: The RichLog widget to write to
        target: Pokemon name or party position (1-6)
        ensure_battle_ready_callback: Callback to ensure Pokemon has battle stats
    """
    pokemon_list = game_state.game_data.get("pokemon", [])
    if not pokemon_list:
        output.write("")
        output.write("[yellow]⚠ You don't have any Pokemon yet![/yellow]")
        output.write("")
        return

    selected_pokemon, _ = game_state.find_pokemon(target)

    if not selected_pokemon:
        output.write("")
        output.write(f"[yellow]⚠ Could not find Pokemon: {target}[/yellow]")
        output.write("[dim]Use 'Show Party' to see your Pokemon list[/dim]")
        output.write("")
        return

    # Ensure Pokemon has all required fields
    ensure_battle_ready_callback(selected_pokemon)

    # Display detailed information
    output.write("")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("[bold cyan]       🔍 POKEMON INSPECTION 🔍            [/bold cyan]")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("")

    name = selected_pokemon["name"]
    level = selected_pokemon.get("level", 5)
    types = "/".join(selected_pokemon.get("types", []))
    hp = selected_pokemon.get("hp", selected_pokemon.get("max_hp", 0))
    max_hp = selected_pokemon.get("max_hp", 0)
    status = selected_pokemon.get("status") or "OK"
    no_evolve = selected_pokemon.get("no_evolve", False)

    output.write(f"  [bold yellow]Name:[/bold yellow] {name}")
    output.write(f"  [bold yellow]Level:[/bold yellow] {level}")
    output.write(f"  [bold yellow]Type:[/bold yellow] {types}")
    if no_evolve:
        output.write("  [bold yellow]Evolution:[/bold yellow] [dim]Blocked (Easter Egg)[/dim]")
    output.write("")

    # HP Bar
    hp_bar = format_hp_bar(hp, max_hp, width=20)
    output.write("  [bold yellow]HP:[/bold yellow]")
    output.write(f"    {hp_bar}")
    output.write(f"    {hp}/{max_hp} HP")
    output.write(f"  [bold yellow]Status:[/bold yellow] {status}")
    output.write("")

    # Stats
    stats = selected_pokemon.get("stats", {})
    if stats:
        output.write("  [bold yellow]Stats:[/bold yellow]")
        output.write(
            f"    Attack:  {stats.get('attack', '?'):<4}  Defense: {stats.get('defense', '?')}"
        )
        output.write(
            f"    Special: {stats.get('special', '?'):<4}  Speed:   {stats.get('speed', '?')}"
        )
        output.write("")

    # Experience
    exp = selected_pokemon.get("experience", 0)
    next_level_exp = selected_pokemon.get("next_level_exp", 0)
    output.write("  [bold yellow]Experience:[/bold yellow]")
    exp_bar, exp_text = format_experience_bar(exp, next_level_exp, level, width=20)
    output.write(f"    [{exp_bar}]")
    output.write(f"    {exp_text}")
    output.write("")

    # Moves
    moves = selected_pokemon.get("moves", [])
    output.write("  [bold yellow]Moves:[/bold yellow]")
    if moves:
        for move in moves:
            move_name = move.get("name", "Unknown")
            pp = move.get("pp", 0)
            max_pp = move.get("max_pp", 0)
            output.write(f"    • {move_name:<15} {pp}/{max_pp} PP")
    else:
        output.write("    [dim]No moves learned[/dim]")

    output.write("")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("")


def show_help(game_state: "GameState", output: RichLog) -> None:
    """
    Display context-aware help information based on current game state and location.

    Shows only the commands relevant to the current context:
    - In battle → battle commands only
    - In a town → building and general commands
    - On a route/forest → exploration and general commands
    - No active game → general/menu commands only

    Args:
        game_state: The game state
        output: The RichLog widget to write to
    """
    output.write("")
    output.write("[bold cyan]╔══════════════════════════════════════════════════╗[/bold cyan]")
    output.write("[bold cyan]║              📖  COMMAND REFERENCE               ║[/bold cyan]")
    output.write("[bold cyan]╚══════════════════════════════════════════════════╝[/bold cyan]")
    output.write("")

    if game_state.in_game:
        in_battle = game_state.battle_state is not None
        loc = game_state.current_location
        loc_type = loc.type if loc else None  # "town", "route", "forest", "dungeon"

        if in_battle:
            # ── Battle Commands (battle context only) ────────────────────────
            output.write("[bold red]⚔️   Battle Commands[/bold red]")
            output.write("  [cyan]Fight[/cyan]                           Open move selection")
            output.write(
                "  [cyan]<move name>[/cyan]                     Use a specific move  "
                "[dim]e.g. 'Tackle'[/dim]"
            )
            output.write(
                "  [cyan]Switch[/cyan]                          Switch your active Pokémon"
            )
            output.write("  [cyan]Bag[/cyan]                             Open battle bag")
            output.write("  [cyan]Use Potion[/cyan]                      Restore 20 HP")
            output.write("  [cyan]Use Super Potion[/cyan]                Restore 50 HP")
            output.write("  [cyan]Use Antidote[/cyan]                    Cure poison")
            output.write("  [cyan]Use Paralyze Heal[/cyan]               Cure paralysis")
            output.write(
                "  [cyan]Use Awakening[/cyan]                   Wake up a sleeping Pokémon"
            )
            output.write(
                "  [cyan]Pokeball[/cyan]                        Throw a Pokéball  "
                "[dim](wild battles only)[/dim]"
            )
            output.write(
                "  [cyan]Run[/cyan]                             Attempt to flee  "
                "[dim](wild battles only)[/dim]"
            )
            output.write("")
            output.write(
                "[dim]Status conditions: 🔥BRN=1/8 HP/turn  ☠PSN=1/16 HP/turn  ⚡PAR=may skip turn[/dim]"
            )
            output.write("")

        elif loc_type == "town":
            # ── Town Commands ─────────────────────────────────────────────────
            output.write("[bold yellow]🏙  Town Commands[/bold yellow]")
            output.write(
                "  [green]Enter <building>[/green]                Enter a building  "
                "[dim]e.g. 'Enter Pokemon Center'[/dim]"
            )
            output.write(
                "  [green]Enter[/green]                           Show available buildings (button menu)"
            )
            output.write(
                "  [green]Look Around[/green]                     Show exits and buildings"
            )
            output.write(
                "  [green]Move To <location>[/green]              Travel to a connected location"
            )
            output.write(
                "  [green]Move To[/green]                         Show available destinations (button menu)"
            )
            output.write(
                "  [green]Map[/green]                             Show the Kanto region map"
            )
            output.write("")

            # ── Party & Items ─────────────────────────────────────────────────
            output.write("[bold yellow]🎒  Party & Items[/bold yellow]")
            output.write("  [green]Show Party[/green]                      View your Pokémon party")
            output.write("  [green]Show Bag[/green]                        View items in your bag")
            output.write(
                "  [green]Use <item>[/green]                      Use an item outside battle"
            )
            output.write("  [green]Show Badges[/green]                     View your badge case")
            output.write(
                "  [green]Inspect <name|#>[/green]                View a Pokémon's details"
            )
            output.write("  [green]Show Status[/green]                     Trainer info summary")
            output.write("  [green]Show Pokedex[/green]                    Open Pokédex")
            output.write("  [green]Stats[/green]                           Adventure statistics")
            output.write("")

            # ── Game Management ───────────────────────────────────────────────
            output.write("[bold yellow]💾  Game Management[/bold yellow]")
            output.write("  [green]Save Game[/green]                       Save your game")
            output.write("  [green]Go To Main Menu[/green]                 Return to the main menu")
            output.write("")

        else:
            # Route / forest / dungeon ─────────────────────────────────────────
            output.write("[bold yellow]🗺  Exploration Commands[/bold yellow]")
            output.write(
                "  [green]Explore Area[/green]                    Search for wild Pokémon or trainers"
            )
            output.write(
                "  [green]Look Around[/green]                     Show exits and area description"
            )
            output.write(
                "  [green]Move To <location>[/green]              Travel to a connected location"
            )
            output.write(
                "  [green]Move To[/green]                         Show available destinations (button menu)"
            )
            output.write(
                "  [green]Map[/green]                             Show the Kanto region map"
            )
            output.write("")

            # ── Party & Items ─────────────────────────────────────────────────
            output.write("[bold yellow]🎒  Party & Items[/bold yellow]")
            output.write("  [green]Show Party[/green]                      View your Pokémon party")
            output.write("  [green]Show Bag[/green]                        View items in your bag")
            output.write(
                "  [green]Use <item>[/green]                      Use an item outside battle"
            )
            output.write(
                "  [green]Inspect <name|#>[/green]                View a Pokémon's details"
            )
            output.write("  [green]Show Status[/green]                     Trainer info summary")
            output.write("  [green]Show Pokedex[/green]                    Open Pokédex")
            output.write("")

            # ── Game Management ───────────────────────────────────────────────
            output.write("[bold yellow]💾  Game Management[/bold yellow]")
            output.write("  [green]Save Game[/green]                       Save your game")
            output.write("  [green]Go To Main Menu[/green]                 Return to the main menu")
            output.write("")

    # ── General / Menu Commands (always shown) ───────────────────────────────
    output.write("[bold yellow]🖥  General[/bold yellow]")
    output.write("  [green]Show Help[/green]                       Show this command reference")
    output.write("  [green]Show About[/green]                      About this application")
    output.write("  [green]Clear Output[/green]                    Clear the output log")
    output.write(
        "  [green]Quit Game[/green]                       Exit the game  [dim](also: Quit, Exit)[/dim]"
    )
    output.write("")

    output.write("[bold yellow]⌨️   Keyboard Shortcuts[/bold yellow]")
    output.write("  [dim]h          Open help[/dim]")
    output.write("  [dim]q          Quit[/dim]")
    output.write("  [dim]Ctrl+C     Quit[/dim]")
    output.write("")


def show_map(game_state: "GameState", output: RichLog) -> None:
    """
    Display a Rich-formatted ASCII map of the Kanto region.

    Shows current position, visited locations, and locked paths.
    Purely cosmetic but helps with orientation.

    Args:
        game_state: The game state
        output: The RichLog widget to write to
    """
    current = game_state.current_location
    current_name = current.name if current else ""
    route_progress = game_state.game_data.get("route_progress", {})
    previous = game_state.game_data.get("previous_location", "") or ""
    badges = set(game_state.game_data.get("badges", []))

    # Build the set of visited locations
    visited: set[str] = set()
    if current_name:
        visited.add(current_name)
    if previous:
        visited.add(previous)
    for loc_name, progress in route_progress.items():
        if isinstance(progress, int) and progress > 0:
            visited.add(loc_name)
    # Infer town visits from gym badges
    if "boulder_badge" in badges:
        visited.add("Pewter City")
    if "cascade_badge" in badges:
        visited.add("Cerulean City")
    if "thunder_badge" in badges:
        visited.add("Vermillion City")

    def _fmt(name: str, label: str) -> str:
        """Return a Rich-styled label for the given location."""
        locked = (name == "Pokemon League Gate" and len(badges) < 8) or (
            name == "Route 24" and "cascade_badge" not in badges
        )
        if name == current_name:
            return f"[bold yellow on blue] ★{label} [/bold yellow on blue]"
        elif locked:
            return f"[dim red]🔒{label}[/dim red]"
        elif name in visited:
            return f"[bold green]{label}[/bold green]"
        else:
            return f"[dim]{label}[/dim]"

    c = "[dim]│[/dim]"  # vertical connector

    output.write("")
    output.write("[bold cyan]╔══════════════════════════════════════════════════════╗[/bold cyan]")
    output.write("[bold cyan]║               🗺  KANTO REGION MAP                  ║[/bold cyan]")
    output.write("[bold cyan]╚══════════════════════════════════════════════════════╝[/bold cyan]")
    output.write(
        "  [bold yellow]★[/bold yellow] = here  "
        "[bold green]green[/bold green] = visited  "
        "[dim]dim[/dim] = unvisited  "
        "[dim red]🔒[/dim red] = locked"
    )
    output.write("")

    # ── Map layout: north at top, flowing south then east ──────────────────
    #
    # Pokemon League Gate ─── Route 22 ─── VIRIDIAN CITY
    #                                            │
    #                                        Route 1
    #                                            │
    #                                       PALLET TOWN
    #
    # VIRIDIAN CITY ─── Route 2 South ─── Viridian Forest ─── Route 2 North ─── Diglett's Cave
    #                                                                │                   │
    #                                                          PEWTER CITY ─── Route 3   │
    #                                                                             │       │
    #                                                                          Mt. Moon   │ (shortcut)
    #                                                                             │       │
    #                                                                          Route 4    │
    #                                                                             │       │
    #                                                                     CERULEAN CITY   │
    #                                                                       │      │      │
    #                                                                   Route 5  Route 9  │
    #                                                                       │      │      │
    #                                                                   UG Path  Route 10 │
    #                                                                       │      │      │
    #                                                                   Route 6  Rock Tunnel
    #                                                                       │
    #                                                              VERMILLION CITY ─── Route 11 ─── (Diglett's Cave)
    #
    #                                                 Route 24 (Nugget Bridge, north of Cerulean — locked until Cascade Badge)

    league = _fmt("Pokemon League Gate", "🏆 Pokémon League")
    r22 = _fmt("Route 22", "Route 22")
    viridian = _fmt("Viridian City", "VIRIDIAN CITY")
    r1 = _fmt("Route 1", "Route 1")
    pallet = _fmt("Pallet Town", "PALLET TOWN")
    r2s = _fmt("Route 2 South", "Route 2 South")
    virfor = _fmt("Viridian Forest", "Viridian Forest")
    r2n = _fmt("Route 2 North", "Route 2 North")
    pewter = _fmt("Pewter City", "PEWTER CITY")
    r3 = _fmt("Route 3", "Route 3")
    moon = _fmt("Mt. Moon", "Mt. Moon")
    r4 = _fmt("Route 4", "Route 4")
    cerulean = _fmt("Cerulean City", "CERULEAN CITY")
    r24 = _fmt("Route 24", "Route 24 (Nugget Bridge 🔒)")
    r9 = _fmt("Route 9", "Route 9")
    r10 = _fmt("Route 10", "Route 10")
    rock = _fmt("Rock Tunnel", "Rock Tunnel")
    r5 = _fmt("Route 5", "Route 5")
    ugn = _fmt("Underground Path (North)", "UG Path N")
    ugs = _fmt("Underground Path (South)", "UG Path S")
    r6 = _fmt("Route 6", "Route 6")
    vermillion = _fmt("Vermillion City", "VERMILLION CITY")
    r11 = _fmt("Route 11", "Route 11")
    diglett = _fmt("Diglett's Cave", "Diglett's Cave")

    h = "[dim]──[/dim]"  # horizontal connector

    # ── North block ────────────────────────────────────────────────────────
    output.write(f"  {league} {h} {r22} {h} {viridian}")
    output.write(f"                                {c}")
    output.write(f"                            {r1}")
    output.write(f"                                {c}")
    output.write(f"                           {pallet}")
    output.write("")
    # ── Main east-west spine ────────────────────────────────────────────────
    output.write(f"  {viridian} {h} {r2s} {h} {virfor} {h} {r2n} {h} {diglett}")
    output.write(f"                                                    {c}              {c}")
    output.write(
        f"                                               {pewter} {h} {r3} {h} {moon} {h} {r4} {h} {cerulean}"
    )
    output.write(
        f"                                                                                          {c}       {c}"
    )
    output.write(
        f"                                                                                       {r5}     {r9}"
    )
    output.write(
        f"                                                                                          {c}       {c}"
    )
    output.write(
        f"                                                                                      {ugn}   {r10}"
    )
    output.write(
        f"                                                                                          {c}       {c}"
    )
    output.write(
        f"                                                                                      {ugs}  {rock}"
    )
    output.write(
        f"                                                                                          {c}"
    )
    output.write(
        f"                                                                               {vermillion} {h} {r11} {h} {diglett}"
    )
    output.write("")
    output.write(f"  [dim](north of CERULEAN CITY, locked until Cascade Badge → {r24})[/dim]")
    output.write("")


def show_game_status(game_state: "GameState", output: RichLog, show_status_callback) -> None:
    """
    Display current game status.

    Args:
        game_state: The game state
        output: The RichLog widget to write to
        show_status_callback: Callback to show terminal status (fallback)
    """
    if not game_state.in_game:
        show_status_callback(output)
        return

    output.write("")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("[bold cyan]           🎮 GAME STATUS 🎮               [/bold cyan]")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("")

    data = game_state.game_data

    output.write(f"  [bold]Trainer:[/bold] [yellow]{data.get('player_name', 'Unknown')}[/yellow]")

    if game_state.current_location:
        output.write(f"  [bold]Location:[/bold] [green]{game_state.current_location.name}[/green]")
        output.write(f"  [dim]{game_state.current_location.description}[/dim]")
    else:
        output.write(f"  [bold]Location:[/bold] [green]{data.get('location', 'Unknown')}[/green]")

    output.write("")
    output.write(f"  [bold]Money:[/bold] [cyan]₽{data.get('money', 0)}[/cyan]")

    # Display badges
    badges = data.get("badges", [])
    badge_count = len(badges) if isinstance(badges, list) else badges
    output.write(f"  [bold]Badges:[/bold] [yellow]{'🏆' * badge_count} {badge_count}/8[/yellow]")
    output.write("")

    pokemon = data.get("pokemon", [])
    if pokemon:
        output.write(f"  [bold]Pokemon Party:[/bold] [green]{len(pokemon)}/6[/green]")
        for p in pokemon:
            output.write(f"    • {p}")
    else:
        output.write("  [bold]Pokemon Party:[/bold] [dim]Empty[/dim]")

    output.write("")

    items = data.get("items", {})
    if items:
        output.write(f"  [bold]Items:[/bold] {len(items)} type(s)")

    output.write("")

    if game_state.current_save:
        output.write(f"  [dim]Save file: {game_state.current_save.name}[/dim]")
    else:
        output.write("  [dim]No save file (use 'save' to save your progress)[/dim]")


def show_status(
    game_state: "GameState", output: RichLog, command_count: int, title: str, sub_title: str
) -> None:
    """
    Display application status.

    Args:
        game_state: The game state
        output: The RichLog widget to write to
        command_count: Number of commands executed
        title: Terminal title
        sub_title: Terminal sub-title
    """
    output.write("")
    output.write("[bold cyan]📊 Terminal Status:[/bold cyan]")
    output.write("")
    output.write(f"  Commands executed: [green]{command_count}[/green]")
    output.write(f"  Terminal title: [cyan]{title}[/cyan]")
    output.write(f"  Sub-title: [cyan]{sub_title}[/cyan]")
    output.write(
        f"  Game state: [yellow]{'In Game' if game_state.in_game else 'Main Menu'}[/yellow]"
    )

    # Show cheat mode status
    if game_state.cheat_mode:
        output.write("  Cheat mode: [bold yellow]ENABLED 🎮[/bold yellow]")

    output.write(f"  Saves directory: [dim]{game_state.saves_dir}[/dim]")
    output.write("")


def show_about(output: RichLog) -> None:
    """
    Display about information.

    Args:
        output: The RichLog widget to write to
    """
    output.write("")
    output.write("[bold cyan]🎮 About Pokemon Terminal[/bold cyan]")
    output.write("")
    output.write("  [bold]Robot Framework Pokemon Library[/bold]")
    output.write("  Version: [green]0.1.0[/green]")
    output.write("")
    output.write("  A modern terminal-based Pokemon game built with:")
    output.write("    • [cyan]Robot Framework[/cyan] - Test automation framework")
    output.write("    • [cyan]Textual[/cyan] - Modern Python TUI framework")
    output.write("    • [cyan]Rich[/cyan] - Beautiful terminal formatting")
    output.write("")
    output.write("  [dim]This is an April Fools project - QA engineers[/dim]")
    output.write("  [dim]expect tests, but get a Pokemon game instead! 🎉[/dim]")
