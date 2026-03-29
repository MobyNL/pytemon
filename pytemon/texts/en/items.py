"""
Text constants for pytemon/items.py.
"""

# ── show_bag ─────────────────────────────────────────────────────────────────

BAG_HEADER: list[str] = [
    "",
    "[bold cyan]🎒 Your Bag[/bold cyan]",
    "",
]

BAG_EMPTY: list[str] = [
    "[dim]Your bag is empty![/dim]",
    "[dim]Buy items at the Pokemart, or find them while exploring.[/dim]",
    "",
]

BAG_COMMANDS_HINT: list[str] = [
    "[dim]Commands: 'use <item>' · 'use <item> on <pokemon>'[/dim]",
    "",
]

# ── use_item (generic errors) ─────────────────────────────────────────────────

ITEM_NO_POKEMON: list[str] = [
    "",
    "[yellow]⚠ You don't have any Pokemon to use items on![/yellow]",
    "",
]

ITEM_NOT_OWNED: list[str] = [
    "",
    # dynamic: "[red]❌ You don't have any {item_name}![/red]"
    "",
]

ITEM_BALLS_BATTLE_ONLY: list[str] = [
    "",
    "[yellow]⚠ Pokeballs can only be used during battle![/yellow]",
    "",
]

ITEM_HM_USE_HINT: list[str] = [
    # dynamic: "[dim]{hm_name} teaches a move. Select a Pokemon with 'use {hm_name} on <pokemon>'[/dim]"
]

# ── use_item (escape rope) ────────────────────────────────────────────────────

ESCAPE_ROPE_NOT_HERE: list[str] = [
    "",
    "[yellow]⚠ Can't use Escape Rope here — you're in a town or city![/yellow]",
    "",
]

# Dynamic: "[bold green]You used the Escape Rope and escaped to {destination}![/bold green]"

# ── use_item (repel) ──────────────────────────────────────────────────────────

# Dynamic: "[bold green]✓ {repel_name} activated! Wild encounters reduced for {steps} explores.[/bold green]"

# ── use_item (stat booster) ───────────────────────────────────────────────────

# Dynamic: "[bold green]✓ {item_name} raised {pokemon_name}'s {stat} by {amount}![/bold green]"

# ── use_item (rare candy) ─────────────────────────────────────────────────────

# Dynamic: "[bold green]✓ {pokemon_name} grew to Level {new_level}![/bold green]"

RARE_CANDY_MAX_LEVEL: list[str] = [
    "",
    "[yellow]⚠ That Pokemon is already at the maximum level![/yellow]",
    "",
]

# ── use_item (revive) ─────────────────────────────────────────────────────────

REVIVE_NOT_FAINTED: list[str] = [
    "",
    "[yellow]⚠ That Pokemon hasn't fainted![/yellow]",
    "",
]

# Dynamic: "[bold green]✓ {pokemon_name} was revived![/bold green]"

# ── use_item (evolution stone) ────────────────────────────────────────────────

STONE_NO_EFFECT: list[str] = [
    "",
    "[yellow]⚠ Nothing happened. That Pokemon can't evolve with this stone.[/yellow]",
    "",
]
