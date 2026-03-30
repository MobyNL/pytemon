"""
Text constants for pytemon/battle/battle_actions.py.
"""

NO_USABLE_POKEMON: list[str] = [
    "[red]❌ All your Pokemon have fainted! Head to a Pokemon Center![/red]",
    "",
]

UNKNOWN_MOVE: list[str] = [
    "[red]❌ Unknown move. Type the name, number, or 'Back'.[/red]",
    "",
]

MOVE_NO_PP: list[str] = [
    "[red]❌ {move_name} has no PP left! Choose another move.[/red]",
    "",
]

PLAYER_USED_MOVE: list[str] = [
    "",
    "[bold]{player_name} used {move_name}![/bold]",
]

OPPONENT_USED_STRUGGLE: list[str] = [
    "[yellow]{opponent_name} has no moves left! It used Struggle![/yellow]",
]

STRUGGLE_DAMAGE: list[str] = [
    "[cyan]{player_name} took {damage} damage![/cyan]",
]

OPPONENT_USED_MOVE: list[str] = [
    "",
    "[yellow]{opponent_name} used {move_name}![/yellow]",
]

TRAINER_FLEE_BLOCKED: list[str] = [
    "",
    "[red]❌ No! There's no running from a trainer battle![/red]",
    "",
]

FLEE_SUCCESS_MESSAGES: list[str] = [
    "[cyan]Got away safely![/cyan]",
    "[cyan]You managed to escape![/cyan]",
    "[cyan]Fled successfully![/cyan]",
    "[cyan]You got away![/cyan]",
]

FLEE_FAILED_MESSAGES: list[str] = [
    "[yellow]Can't escape![/yellow]",
    "[yellow]Couldn't get away![/yellow]",
    "[yellow]Failed to flee![/yellow]",
    "[yellow]No! Can't escape![/yellow]",
]

FLEE_RESULT_WRAPPER: list[str] = [
    "",
    "{message}",
    "",
]

TRAINER_BLOCKED_BALL: list[str] = [
    "",
    "[red]❌ The trainer blocked the Ball![/red]",
    "[yellow]{trainer_name}: Don't be a thief![/yellow]",
    "",
]

NO_POKEBALLS: list[str] = [
    "",
    "[red]❌ You have no Pokeballs![/red]",
    "[dim]Buy Pokeballs at the Pokemart[/dim]",
    "",
]

NO_BALL_TYPE: list[str] = [
    "",
    "[red]❌ You have no {ball_type}s![/red]",
    "[dim]Check your bag for available Pokéballs[/dim]",
    "",
]

THREW_BALL_AT_WILD: list[str] = [
    "",
    "[bold cyan]You threw a {ball_type} at wild {wild_name}![/bold cyan]",
    "",
]

CATCH_SUCCESS: list[str] = [
    "[bold green]★ Gotcha! {wild_name} was caught! ★[/bold green]",
]

CATCH_SUCCESS_PLAIN: list[str] = [
    "[green]★ Gotcha! {wild_name} was caught! ★[/green]",
]

PARTY_FULL_SENT_TO_PC: list[str] = [
    "[yellow]  Your party is full — {wild_name} was sent to {box_name}![/yellow]",
]

PC_RETRIEVE_HINT: list[str] = [
    "[dim]  Access Bill's PC at any Pokemon Center to retrieve it.[/dim]",
]

PARTY_AND_PC_FULL: list[str] = [
    "[red]  Your party and PC are both full! {wild_name} could not be stored.[/red]",
]

POKEDEX_CAUGHT_REGISTERED: list[str] = [
    "[dim]📖 Pokedex: {wild_name} was registered as caught![/dim]",
]

ADDED_TO_PARTY: list[str] = [
    "",
    "[green]✓ {wild_name} was added to your party![/green]",
]

CATCH_FAIL_0: list[str] = [
    "[yellow]Oh no! {wild_name} broke free immediately![/yellow]",
]

CATCH_FAIL_1: list[str] = [
    "[yellow]Aww! It appeared to be caught![/yellow]",
]

CATCH_FAIL_2: list[str] = [
    "[yellow]Aargh! Almost had it![/yellow]",
]

CATCH_FAIL_3: list[str] = [
    "[yellow]Gah! It was so close, too![/yellow]",
]

TRAILING_BLANK: list[str] = [
    "",
]

SAFARI_BAIT: list[str] = [
    "",
    "[cyan]🥩 You tossed some Bait at {wild_name}...[/cyan]",
    "[dim]   {wild_name} is distracted by the food![/dim]",
    "",
]

SAFARI_ROCK: list[str] = [
    "",
    "[red]🪨 You threw a Rock at {wild_name}...[/red]",
    "[dim]   {wild_name} became angry![/dim]",
    "",
]

NO_SAFARI_BALLS: list[str] = [
    "",
    "[red]❌ You have no Safari Balls left![/red]",
    "",
]

THREW_SAFARI_BALL: list[str] = [
    "",
    "[bold cyan]🎯 You threw a Safari Ball at {wild_name}![/bold cyan]",
    "",
]

SAFARI_FLED_SAFE: list[str] = [
    "",
    "[yellow]You safely fled from the Safari Zone encounter![/yellow]",
    "",
]

WILD_FLED: list[str] = [
    "[yellow]{wild_name} fled![/yellow]",
    "",
]

SWITCH_CANCELLED: list[str] = [
    "[dim]Switch cancelled.[/dim]",
    "",
]

INVALID_SWITCH_SELECTION: list[str] = [
    "[red]❌ Invalid selection: {target}[/red]",
]

ALREADY_IN_BATTLE: list[str] = [
    "[yellow]{pokemon_name} is already in battle![/yellow]",
    "",
]

FAINTED_CANNOT_BATTLE: list[str] = [
    "[red]❌ {pokemon_name} has fainted and can't battle![/red]",
]

SWITCH_PERFORMED: list[str] = [
    "",
    "[bold cyan]{active_name}, come back![/bold cyan]",
    "[bold green]Go, {chosen_name}![/bold green]",
    "",
]

OPPONENT_FAINTED_TRAINER: list[str] = [
    "[bold green]{trainer_name}'s {wild_name} fainted![/bold green]",
]

OPPONENT_FAINTED_WILD: list[str] = [
    "[bold green]Wild {wild_name} fainted![/bold green]",
]

EXP_GAINED: list[str] = [
    "[cyan]{player_name} gained {exp} Exp. Points![/cyan]",
]

LEVEL_UP: list[str] = [
    "",
    "[bold yellow]★ {player_name} grew to Level {new_level}! ★[/bold yellow]",
]

LEARNED_MOVE: list[str] = [
    "[bold cyan]  ✦ {player_name} learned {move_name}![/bold cyan]",
]

FORGOT_AND_LEARNED_MOVE: list[str] = [
    "[bold cyan]  ✦ {player_name} forgot {old_move} and learned {move_name}![/bold cyan]",
]

TRAINER_SENT_NEXT: list[str] = [
    "",
    "[yellow]{trainer_name} sent out {next_name}! (Lv. {next_level})[/yellow]",
    "",
]

TRAINER_DEFEATED_HEADER: list[str] = [
    "",
    "[bold green]═══════════════════════════════════════════[/bold green]",
    "[bold green]🏆 You defeated {trainer_class} {trainer_name}! 🏆[/bold green]",
    "[bold green]═══════════════════════════════════════════[/bold green]",
    "",
]

PRIZE_MONEY: list[str] = [
    "[bold yellow]💰 You received ₽{prize} as prize money![/bold yellow]",
    "",
]

BATTLE_WON: list[str] = [
    "[bold]You won the battle![/bold]",
    "",
]

PLAYER_FAINTED: list[str] = [
    "",
    "[bold red]{player_name} fainted![/bold red]",
    "",
]

OTHER_POKEMON_STILL_STANDING: list[str] = [
    "[yellow]Your other Pokemon are still standing![/yellow]",
]

CHOOSE_NEXT_POKEMON: list[str] = [
    "[dim]Choose your next Pokemon...[/dim]",
    "",
]

NURSE_HEALED_FAINTED: list[str] = [
    "[cyan]Nurse Joy healed your fainted Pokemon at the Pokemon Center.[/cyan]",
    "",
]

NO_MORE_POKEMON: list[str] = [
    "[bold red]You have no more Pokemon that can battle![/bold red]",
    "[dim]You black out...[/dim]",
]

WAKE_UP_CENTER: list[str] = [
    "[cyan]You wake up at the {respawn_location} Pokemon Center.[/cyan]",
]

WAKE_UP_HOME: list[str] = [
    "[cyan]You wake up at home.[/cyan]",
    "[cyan]Mom took care of you and your Pokemon![/cyan]",
]

ALL_HEALED_AFTER_BLACKOUT: list[str] = [
    "[cyan]Nurse Joy has healed all your Pokemon![/cyan]",
]

ALL_HEALED_AT_HOME: list[str] = [
    "[cyan]All your Pokemon have been healed![/cyan]",
]

NO_ITEM_LEFT: list[str] = [
    "",
    "[red]❌ You have no {item_name}s![/red]",
    "",
]

HEAL_ITEM_USED: list[str] = [
    "",
    "[green]💊 {player_name} recovered {heal_amount} HP![/green]",
    "",
]

WRONG_STATUS_CONDITION: list[str] = [
    "",
    "[yellow]⚠ {player_name} doesn't have that condition![/yellow]",
    "",
]

STATUS_CURED: list[str] = [
    "",
    "[green]✓ {player_name} was {cure_msg}![/green]",
    "",
]
