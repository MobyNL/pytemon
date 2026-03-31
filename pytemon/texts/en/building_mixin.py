"""
Text constants for pytemon/ui/building_mixin.py.
"""

HEAL_CENTER_DECLINED: list[str] = [
    "",
    "[bold]Nurse Joy:[/bold] [magenta]Please come back if you need us![/magenta]",
    "",
    "[dim]You leave the Pokemon Center[/dim]",
    "",
]

HEAL_MOM_DECLINED: list[str] = [
    "",
    "[bold]Mom:[/bold] [magenta]Okay! Come back anytime you need to rest![/magenta]",
    "",
    "[dim]You leave the house[/dim]",
    "",
]

INVALID_RESPONSE_YES_NO: list[str] = [
    "",
    "[red]❌ Invalid response[/red]",
    "[dim]Please type: Yes or No[/dim]",
    "",
]

POKEMON_CENTER_LEAVE: list[str] = [
    "[dim]You leave the Pokemon Center. Come back if your Pokemon need healing![/dim]",
    "",
]

POKEMON_CENTER_UNKNOWN_COMMAND: list[str] = [
    "[bold]Nurse Joy:[/bold] [magenta]I'm not sure I understand.[/magenta]",
    "[magenta]   Would you like to heal your Pokemon, use the PC, or leave?[/magenta]",
    "",
]

POKEMART_HEADER: list[str] = [
    "",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "[bold cyan]            🏪 POKEMART 🏪                [/bold cyan]",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "",
    "[bold]Clerk:[/bold] [yellow]Welcome to the Pokemart![/yellow]",
    "[yellow]   What can I get for you?[/yellow]",
    "",
]

POKEMART_LEAVE: list[str] = [
    "",
    "[bold]Clerk:[/bold] [yellow]Thank you! Come again![/yellow]",
    "",
    "[dim]You leave the Pokemart[/dim]",
    "",
]

SHOP_NO_RESALE_VALUE: list[str] = [
    "",
    "[red]❌ That item has no resale value[/red]",
    "",
]

SHOP_DO_NOT_HAVE_ITEM: list[str] = [
    "",
    "[red]❌ You don't have any {item_name}![/red]",
    "",
]

SHOP_SELL_SUCCESS: list[str] = [
    "",
    "[bold green]✓ Sold {qty}x {item_name} for ₽{total_earned}![/bold green]",
    "   [dim]Money: ₽{money}[/dim]",
    "",
]

SHOP_UNKNOWN_COMMAND: list[str] = [
    "",
    "[yellow]?[/yellow] [dim]I don't understand that.[/dim]",
    "[dim]Type 'buy <item>', 'sell <item>' or 'leave'[/dim]",
    "",
]

SHOP_ITEM_NOT_SOLD: list[str] = [
    "",
    "[red]❌ '{item_name}' is not sold here[/red]",
    "[dim]Check the item list above[/dim]",
    "",
]

SHOP_NOT_ENOUGH_MONEY: list[str] = [
    "",
    "[red]❌ Not enough money! Need ₽{total_cost}, have ₽{money}[/red]",
    "",
]

SHOP_BUY_SUCCESS: list[str] = [
    "",
    "[bold green]✓ Bought {qty}x {item_name} for ₽{total_cost}![/bold green]",
    "   [dim]Remaining money: ₽{money}[/dim]",
    "",
]

GYM_HEADER: list[str] = [
    "",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "[bold cyan]           ⚔️  POKEMON GYM ⚔️             [/bold cyan]",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "",
]

GYM_PEWTER_DIALOGUE: list[str] = [
    "[bold]Brock:[/bold] [yellow]I'm Brock! I'm Pewter's Gym Leader![/yellow]",
    "[yellow]   My rock-hard willpower is evident in my Pokemon![/yellow]",
    "",
    "[dim]Gym battles will be implemented soon...[/dim]",
]

GYM_VIRIDIAN_DIALOGUE: list[str] = [
    "[bold]???:[/bold] [yellow]The Gym Leader is not here...[/yellow]",
    "",
    "[dim]You need 7 badges to challenge this gym[/dim]",
]

GYM_CLOSED: list[str] = [
    "[yellow]The gym is currently closed[/yellow]",
]

GYM_EXIT: list[str] = [
    "",
    "[dim]You leave the Gym[/dim]",
    "",
]

PLAYER_HOUSE_VISIT: list[str] = [
    "",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "[bold cyan]          🏠 PLAYER'S HOUSE 🏠            [/bold cyan]",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "",
    "[bold]Mom:[/bold] [magenta]Welcome home! Did you come back to rest?[/magenta]",
    "",
    "[magenta]   Your room is upstairs if you need anything.[/magenta]",
    "[magenta]   There's a TV in the living room if you want to watch.[/magenta]",
    "",
    "[dim]Your room has a bed and a PC for storing Pokemon[/dim]",
    "",
    "[bold]Mom:[/bold] [magenta]Take care on your journey![/magenta]",
    "",
    "[dim]You leave the house[/dim]",
    "",
]

RIVALS_HOUSE_HEADER: list[str] = [
    "",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "[bold cyan]          🏠 RIVAL'S HOUSE 🏠             [/bold cyan]",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "",
]

RIVALS_HOUSE_NO_POKEMON: list[str] = [
    "[bold]Rival's Sister:[/bold] [yellow]Oh! You're going to see Professor Oak?[/yellow]",
    "[yellow]   My brother already left. He's always so impatient![/yellow]",
]

RIVALS_HOUSE_WITH_POKEMON: list[str] = [
    "[bold]Rival's Sister:[/bold] [yellow]My brother is on his Pokemon journey too![/yellow]",
    "[yellow]   I hope you two can be good rivals and help each other grow![/yellow]",
]

RIVALS_HOUSE_EXIT: list[str] = [
    "",
    "[dim]You leave the house[/dim]",
    "",
]

NAME_REQUIRED_PLAYER: list[str] = [
    "",
    "[red]❌ Please enter your name![/red]",
    "",
]

NAME_REQUIRED_RIVAL: list[str] = [
    "",
    "[red]❌ Please enter your rival's name![/red]",
    "",
]

NAMES_SET: list[str] = [
    "",
    "[bold green]✓ Names set![/bold green]",
    "  👤 Your name: [cyan]{player_name}[/cyan]",
    "  👤 Rival's name: [yellow]{rival_name}[/yellow]",
    "",
]

RANDOM_NAMES_GENERATED: list[str] = [
    "",
    "[dim]Generated random names:[/dim]",
    "  👤 Your name: [cyan]{player_name}[/cyan]",
    "  👤 Rival's name: [yellow]{rival_name}[/yellow]",
    "",
    "[dim]Click 'Confirm Names' or edit them if you'd like![/dim]",
    "",
]
