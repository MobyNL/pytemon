"""
Text constants for pytemon/buildings.py.
"""

# ── enter_pokemon_center ──────────────────────────────────────────────────────

POKEMON_CENTER_HEADER: list[str] = [
    "",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "[bold cyan]           🏥 POKEMON CENTER 🏥            [/bold cyan]",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "",
    "[bold]Nurse Joy:[/bold] [magenta]Welcome to the Pokemon Center![/magenta]",
    "",
]

POKEMON_CENTER_NO_POKEMON: list[str] = [
    "[magenta]Oh my... you don't have any Pokemon![/magenta]",
    "[magenta]Please obtain a Pokemon before coming here.[/magenta]",
    "",
]

POKEMON_CENTER_NO_POKEMON_LEAVE: list[str] = [
    "[magenta]   But it seems you don't have any Pokemon yet![/magenta]",
    "",
    "[dim]You leave the Pokemon Center[/dim]",
    "",
]

POKEMON_CENTER_LOBBY_PROMPT: list[str] = [
    "[bold]Nurse Joy:[/bold] [magenta]How can I help you today?[/magenta]",
    "",
]

# ── enter_pokemart ────────────────────────────────────────────────────────────

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

SHOP_COMMANDS_HINT: list[str] = [
    "[dim]Commands: 'buy <item>'  or  'buy <qty> <item>'  (e.g. 'buy 5 pokeball')[/dim]",
    "[dim]          'leave' to exit the shop[/dim]",
    "",
]

SHOP_LEAVE: list[str] = [
    "",
    "[yellow]Clerk: Come back anytime![/yellow]",
    "",
]

SHOP_LEAVE_THANK_YOU: list[str] = [
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

# ── enter_museum (Pewter City) ─────────────────────────────────────────────

MUSEUM_HEADER: list[str] = [
    "",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "[bold cyan]       🏛️  PEWTER CITY MUSEUM 🏛️         [/bold cyan]",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "",
    "[bold]Museum Guide:[/bold] [green]Welcome to the Pewter City Natural Science Museum![/green]",
    "[green]   We showcase rare Pokemon fossils and space artifacts![/green]",
    "",
]

MUSEUM_FOSSIL_EXHIBIT: list[str] = [
    "[bold yellow]🦕 FOSSIL EXHIBIT[/bold yellow]",
    "   [dim]Ancient Pokemon fossils recovered from nearby Mt. Moon:[/dim]",
    "",
    "   🦴 [cyan]Old Amber[/cyan]    — Prehistoric remains of an ancient flying Pokemon",
    "   🪨 [cyan]Dome Fossil[/cyan]  — Said to contain a prehistoric Water-type Pokemon",
    "   🪨 [cyan]Helix Fossil[/cyan] — Holds the DNA of a curiously spiralled Pokemon",
    "",
]

MUSEUM_MOON_STONE_EXHIBIT: list[str] = [
    "[bold yellow]🌑 MOON STONE EXHIBIT[/bold yellow]",
    "   🌙 [magenta]Moon Stone[/magenta] — A mysterious stone from space; causes certain Pokemon to evolve",
    "   [dim]Tip: Full Moon Stones can sometimes be found in Mt. Moon![/dim]",
    "",
]

MUSEUM_SPACE_EXHIBIT: list[str] = [
    "[bold yellow]🗿 SPACE EXHIBIT[/bold yellow]",
    "   ⭐ [yellow]Meteorite Fragment[/yellow] — A chunk of rock from outer space",
    "   🌌 [blue]Star Charts[/blue]         — Ancient navigation maps used by Pokemon sailors",
    "",
]

MUSEUM_FOOTER: list[str] = [
    "[bold]Museum Guide:[/bold] [green]Admission is free for Pokemon trainers![/green]",
    "[green]   Come back if you find any fossils on your journey![/green]",
    "",
    "[dim]Type 'leave' or 'exit' to head back outside.[/dim]",
    "",
]

MUSEUM_LEAVE: list[str] = [
    "",
    "[dim]You leave the museum, inspired by the ancient history.[/dim]",
    "",
]

# ── enter_bills_house ─────────────────────────────────────────────────────────

BILLS_HOUSE_HEADER: list[str] = [
    "",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "[bold cyan]           💻 BILL'S HOUSE 💻              [/bold cyan]",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "",
]

# ── enter_ss_anne ─────────────────────────────────────────────────────────────

SS_ANNE_HEADER: list[str] = [
    "",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "[bold cyan]          🚢 S.S. ANNE DOCK 🚢              [/bold cyan]",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "",
]

SS_ANNE_ALREADY_DEPARTED: list[str] = [
    "[dim]The dock is empty — the S.S. Anne has already set sail.[/dim]",
    "[dim]You watch the faint outline of the ship disappear over the horizon.[/dim]",
    "",
]

SS_ANNE_NO_TICKET: list[str] = [
    "[bold]Guard:[/bold] [yellow]Hey! You can't board without an S.S. Anne Ticket![/yellow]",
    "[yellow]   Talk to Bill on Route 24 — he might be able to help.[/yellow]",
    "",
    "[dim]The guard blocks your path to the gangplank.[/dim]",
    "",
]

SS_ANNE_DEPARTING_AFTER_VISIT: list[str] = [
    "[bold]Guard:[/bold] [yellow]The Captain thanks you for visiting![/yellow]",
    "[yellow]   The S.S. Anne is preparing to depart now.[/yellow]",
    "",
    "[dim]The crew cast off the moorings and the great ship slowly pulls away.[/dim]",
    "[dim]The S.S. Anne has departed from Vermillion City.[/dim]",
    "",
]

SS_ANNE_FIRST_VISIT_STORY: list[str] = [
    "[bold]Guard:[/bold] [yellow]Welcome aboard the S.S. Anne![/yellow]",
    "[yellow]   Present your ticket — step right this way![/yellow]",
    "",
    "[dim]You step onto the luxurious ocean liner. The polished decks gleam,[/dim]",
    "[dim]and trainers from all over the world have gathered here.[/dim]",
    "",
    "[cyan]After exploring the cabins and battling a few trainers...[/cyan]",
    "",
    "[bold]Sailor:[/bold] [yellow]The Captain's cabin is at the bow of the ship![/yellow]",
    "[yellow]   He's been a bit seasick, but he loves meeting trainers.[/yellow]",
    "",
    "[italic]You find the Captain slumped over his charts...[/italic]",
    "",
    "[bold]Captain:[/bold] [green]Ugh... I'm not feeling well.[/green]",
    "[green]   But you remind me of a trainer from my youth![/green]",
    "[green]   Take this HM — you've earned it just by making the trip![/green]",
    "",
]

SS_ANNE_RECEIVED_HM01_CUT: list[str] = [
    "[bold yellow]★ Received HM01 Cut! ★[/bold yellow]",
    "",
]

SS_ANNE_HM01_EXPLANATION: list[str] = [
    "[bold]Captain:[/bold] [green]Cut can be used to clear small trees blocking your path.[/green]",
    "[green]   You'll need a Pokemon that can learn it,[/green]",
    "[green]   and the [bold]Cascade Badge[/bold] to use it outside of battle.[/green]",
    "",
    "[dim]You bid the Captain farewell and make your way back to the dock.[/dim]",
    "",
]

# ── enter_pokemon_tower ───────────────────────────────────────────────────────

POKEMON_TOWER_HEADER: list[str] = [
    "",
    "[bold purple]═══════════════════════════════════════════[/bold purple]",
    "[bold purple]          👻 POKEMON TOWER 👻              [/bold purple]",
    "[bold purple]═══════════════════════════════════════════[/bold purple]",
    "",
]

POKEMON_TOWER_AMBIENCE: list[str] = [
    "[dim]An eerie chill passes over you as you push open the heavy doors.[/dim]",
    "[dim]The air inside smells of incense and old stone. Flowers line the walls[/dim]",
    "[dim]beside small placards bearing the names of beloved Pokemon.[/dim]",
    "",
]

POKEMON_TOWER_RESCUED_DIALOGUE: list[str] = [
    "[bold]Mr. Fuji:[/bold] [cyan]Ah, my young friend! Thank you again.[/cyan]",
    "[cyan]   The spirits of this tower have grown calmer since you helped.[/cyan]",
    "[cyan]   Please, take this — a small token of my gratitude.[/cyan]",
    "",
]

POKEMON_TOWER_RESCUED_REWARD: list[str] = [
    "[bold yellow]★ Received the Poke Flute! ★[/bold yellow]",
    "[dim]   Use the Poke Flute to wake sleeping Pokemon — including Snorlax![/dim]",
    "",
]

POKEMON_TOWER_RESCUED_ALREADY_REWARDED: list[str] = [
    "[cyan]   You've already received everything I can give.[/cyan]",
    "[cyan]   Safe travels on your journey.[/cyan]",
    "",
]

POKEMON_TOWER_GHOST_APPEARED_DIALOGUE: list[str] = [
    "[bold]Mr. Fuji:[/bold] [cyan]The ghost on the third floor...[/cyan]",
    "[cyan]   It is a Marowak — the mother of a Cubone who lives here.[/cyan]",
    "[cyan]   She cannot rest until those who wronged her are punished.[/cyan]",
    "",
    "[dim]You feel a presence on the upper floors — something is waiting for you.[/dim]",
    "[dim]Type 'explore' to climb deeper into the tower.[/dim]",
    "",
]

POKEMON_TOWER_FIRST_VISIT_DIALOGUE: list[str] = [
    "[bold]Mr. Fuji:[/bold] [cyan]Welcome to the Pokemon Tower.[/cyan]",
    "[cyan]   This is a place of rest for Pokemon who have passed on.[/cyan]",
    "[cyan]   Trainers come here to pay their respects.[/cyan]",
    "",
    "[bold]Mr. Fuji:[/bold] [cyan]But something is wrong...[/cyan]",
    "[cyan]   A spirit on the upper floors has grown restless.[/cyan]",
    "[cyan]   It fills the trainers here with sorrow and unease.[/cyan]",
    "[cyan]   I pray someone brave will help calm it.[/cyan]",
    "",
    "[dim]Channelers wander the upper floors, their eyes glazed over with grief.[/dim]",
    "[dim]Type 'explore' to climb the tower and face what awaits.[/dim]",
    "",
]

# ── enter_bike_shop ───────────────────────────────────────────────────────────

BIKE_SHOP_HEADER: list[str] = [
    "",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "[bold cyan]          🚲 CERULEAN BIKE SHOP 🚲        [/bold cyan]",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "",
]

BIKE_SHOP_WELCOME: list[str] = [
    "[bold]Owner:[/bold] [yellow]Welcome to the Cerulean Bike Shop![/yellow]",
    "[yellow]   We carry the finest bikes in Kanto![/yellow]",
    "",
]

BIKE_SHOP_FIRST_VISIT_DIALOGUE: list[str] = [
    "[bold]Owner:[/bold] [yellow]Hey! You look like a real trainer on the go![/yellow]",
    "",
    "[yellow]   As a one-time promotional gift, I'd like to give you[/yellow]",
    "[yellow]   a [bold]Bicycle[/bold] — absolutely free![/yellow]",
    "[yellow]   Just spread the word and tell your friends about us![/yellow]",
    "",
    "[yellow]   With a Bicycle you can zip through routes at high speed[/yellow]",
    "[yellow]   and encounter fewer wild Pokemon while riding![/yellow]",
    "",
]

BIKE_SHOP_RECEIVED_BICYCLE: list[str] = [
    "[bold green]✓ Received a Bicycle![/bold green]",
    "   [dim]Use 'ride bike' or 'use bicycle' on a route to cycle faster![/dim]",
    "   [dim](Halves wild encounter rate while cycling)[/dim]",
    "",
]

BIKE_SHOP_REPEAT_DIALOGUE: list[str] = [
    "[bold]Owner:[/bold] [yellow]Still enjoying that bike we gave you?[/yellow]",
    "[yellow]   Great! Nothing beats a Cerulean Bike![/yellow]",
    "",
    "[bold yellow]🚲 Premium models on display (definitely not affordable):[/bold yellow]",
    "   • [cyan]Mach Bike[/cyan]  ₽1,000,000 — Blazing fast",
    "   • [cyan]Acro Bike[/cyan]  ₽1,000,000 — Perfect for stunts",
    "   [dim](One bike is definitely enough for your journey...)[/dim]",
    "",
]

BIKE_SHOP_EXIT: list[str] = [
    "[dim]You leave the Bike Shop[/dim]",
    "",
]

# ── enter_nugget_bridge ─────────────────────────────────────────────────────

NUGGET_BRIDGE_HEADER: list[str] = [
    "",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "[bold cyan]          🌉 NUGGET BRIDGE 🌉              [/bold cyan]",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "",
]

NUGGET_BRIDGE_ALREADY_COMPLETE: list[str] = [
    "[bold]Bridge Patron:[/bold] [yellow]You're the champ who beat all five![/yellow]",
    "[yellow]   The bridge is open to you whenever you like![/yellow]",
    "",
    "[dim]You stroll across Nugget Bridge[/dim]",
    "",
]

NUGGET_BRIDGE_ALL_TRAINERS_BEATEN: list[str] = [
    "[bold yellow]🏆 You defeated all five Nugget Bridge trainers![/bold yellow]",
    "",
    "[bold]Bridge Patron:[/bold] [yellow]Astounding! You beat every single one![/yellow]",
    "[yellow]   As promised — here's your Nugget![/yellow]",
    "[yellow]   You can sell it at any Pokemart for a whopping ₽5000![/yellow]",
    "",
    "[bold green]✓ Received a Nugget![/bold green]",
    "   [dim](Worth ₽5000 — sell at any Pokemart)[/dim]",
    "",
    "[dim]You cross Nugget Bridge triumphantly![/dim]",
    "",
]

NUGGET_BRIDGE_RIVAL_CALL_OUT: list[str] = [
    "",
    "[dim]As you claim the Nugget, a familiar voice calls out...[/dim]",
    "",
]

NUGGET_BRIDGE_FIRST_CHALLENGE: list[str] = [
    "[dim]A long bridge stretches north over the river...[/dim]",
    "[dim]Five trainers line the path, staring you down![/dim]",
    "",
    "[bold]Trainer:[/bold] [yellow]Welcome to Nugget Bridge![/yellow]",
    "[yellow]   Defeat all five of us to claim the legendary Nugget prize![/yellow]",
    "",
]

NUGGET_BRIDGE_PROGRESS: list[str] = [
    "[dim]Progress: {defeated_count}/5 bridge trainers defeated[/dim]",
    "[dim]{remaining} trainer(s) remain on the bridge![/dim]",
    "",
]

NUGGET_BRIDGE_WAITING_PROMPT: list[str] = [
    "[yellow]   Prepare your team, then step onto the bridge![/yellow]",
    "[dim]You hesitate at the bridge entrance[/dim]",
    "",
]

# ── enter_game_corner ───────────────────────────────────────────────────────

GAME_CORNER_HEADER: list[str] = [
    "",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "[bold cyan]         🎰 CELADON GAME CORNER 🎰        [/bold cyan]",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "",
]

# ── enter_department_store ────────────────────────────────────────────────────

DEPARTMENT_STORE_HEADER: list[str] = [
    "",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "[bold cyan]     🏬 CELADON DEPARTMENT STORE 🏬        [/bold cyan]",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "",
]

# ── enter_safari_zone ─────────────────────────────────────────────────────────

SAFARI_ZONE_HEADER: list[str] = [
    "",
    "[bold green]═══════════════════════════════════════════[/bold green]",
    "[bold green]          🦁 SAFARI ZONE ENTRANCE 🦁       [/bold green]",
    "[bold green]═══════════════════════════════════════════[/bold green]",
    "",
]

# ── enter_mr_fujis_house ──────────────────────────────────────────────────────

MR_FUJIS_HOUSE_HEADER: list[str] = [
    "",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "[bold cyan]        🏠 MR. FUJI'S HOUSE 🏠            [/bold cyan]",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "",
]

# ── enter_building (error states) ─────────────────────────────────────────────

NO_BUILDINGS_HERE: list[str] = [
    "",
    "[yellow]⚠ There are no buildings here to enter[/yellow]",
    "[dim]You can only enter buildings in towns and cities[/dim]",
    "",
]

NOT_A_TOWN: list[str] = [
    "",
    "[yellow]⚠ There are no buildings here[/yellow]",
    "[dim]Buildings are only found in towns and cities[/dim]",
    "",
]

CHEAT_BYPASS_BUILDING_LOCK: list[str] = [
    "",
    "[bold yellow]🎮 [CHEAT MODE] Bypassing restriction...[/bold yellow]",
]

BUILDING_BLOCKED_REASON: list[str] = [
    "",
    "[yellow]⚠ {reason}[/yellow]",
    "",
]

BUILDING_NOT_HERE: list[str] = [
    "",
    "[red]❌ '{building_name}' is not a building here[/red]",
    "[dim]Type 'Look Around' to see available buildings[/dim]",
    "",
]

GYM_NOT_AVAILABLE_CONTEXT: list[str] = [
    "",
    "[yellow]⚠ Gym battles are not available in this context[/yellow]",
    "",
]

BUILDING_NOT_IMPLEMENTED: list[str] = [
    "",
    "[yellow]You entered {building_name}[/yellow]",
    "[dim]This building is not yet implemented[/dim]",
    "",
]

# ── perform_pokemon_center_heal ───────────────────────────────────────────────

HEAL_SUCCESS: list[str] = [
    "",
    "[bold green]✓ Your Pokemon have been healed![/bold green]",
    "",
]

# ── perform_mom_heal ──────────────────────────────────────────────────────────

MOM_HEAL_HEADER: list[str] = [
    "",
    "[bold]Mom:[/bold] [magenta]Let me take care of your Pokemon![/magenta]",
    "",
    "[cyan]   ♪ Mom's cooking and care ♪[/cyan]",
    "",
]

MOM_HEAL_SUCCESS: list[str] = [
    "",
    "[bold]Mom:[/bold] [magenta]There! All better! ❤️[/magenta]",
    "[magenta]   Your Pokemon look so happy now![/magenta]",
    "[magenta]   Come back anytime you need to rest![/magenta]",
    "",
    "[dim]You leave the house feeling grateful[/dim]",
    "",
]

# ── enter_rivals_house ───────────────────────────────────────────────────────

RIVALS_HOUSE_HEADER: list[str] = [
    "",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "[bold cyan]          🏠 {rival_name_upper}'S HOUSE 🏠             [/bold cyan]",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "",
]

RIVALS_HOUSE_NO_POKEMON: list[str] = [
    "[bold]{rival_name}'s Sister:[/bold] [yellow]Oh! You're going to see Professor Oak?[/yellow]",
    "[yellow]   {rival_name} already left. He's always so impatient![/yellow]",
]

RIVALS_HOUSE_WITH_POKEMON: list[str] = [
    "[bold]{rival_name}'s Sister:[/bold] [yellow]{rival_name} is on his Pokemon journey too![/yellow]",
    "[yellow]   I hope you two can be good rivals and help each other grow![/yellow]",
]

RIVALS_HOUSE_EXIT: list[str] = [
    "",
    "[dim]You leave the house[/dim]",
    "",
]

# ── enter_oaks_lab ───────────────────────────────────────────────────────────

OAKS_LAB_HEADER: list[str] = [
    "",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "[bold cyan]      🔬 PROFESSOR OAK'S LAB 🔬          [/bold cyan]",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "",
]

OAKS_LAB_PIKACHU_INTRO: list[str] = [
    "[bold]Professor Oak:[/bold] [cyan]Oh! You're finally here![/cyan]",
    "",
    "[cyan]   I was about to head out looking for you![/cyan]",
    "[cyan]   I have a special Pokemon that's been waiting for a trainer...[/cyan]",
    "",
    "[bold yellow]The last remaining Pokemon:[/bold yellow]",
    "",
    "  ⚡ [yellow]Pikachu[/yellow] - Electric type",
    "     [dim]An energetic Pokemon that refuses to stay in its Pokeball![/dim]",
    "",
]

OAKS_LAB_PIKACHU_PROMPT_PANEL: list[str] = [
    "[dim]Click the button or type 'Choose Pikachu' to begin your journey:[/dim]",
]

OAKS_LAB_PIKACHU_PROMPT_TEXT: list[str] = [
    "[yellow]Type 'Choose Pikachu' to begin your journey:[/yellow]",
]

OAKS_LAB_STARTER_INTRO: list[str] = [
    "[bold]Professor Oak:[/bold] [cyan]Ah! Welcome to my laboratory![/cyan]",
    "",
    "[cyan]   I study Pokemon as my life's work![/cyan]",
    "[cyan]   Now, it's time for you to choose your first Pokemon![/cyan]",
    "",
    "[bold yellow]Choose your starter Pokemon:[/bold yellow]",
    "",
    "  🌿 [green]Bulbasaur[/green] - Grass/Poison type",
    "     [dim]A tough Pokemon with great defensive abilities[/dim]",
    "",
    "  🔥 [red]Charmander[/red] - Fire type",
    "     [dim]A fiery Pokemon that will become a powerful dragon[/dim]",
    "",
    "  💧 [blue]Squirtle[/blue] - Water type",
    "     [dim]A cool Pokemon with strong water attacks[/dim]",
    "",
]

OAKS_LAB_STARTER_PROMPT_PANEL: list[str] = [
    "[dim]Click a button or type 'Choose' followed by the Pokemon name:[/dim]",
    "[dim]Example: Choose Bulbasaur[/dim]",
]

OAKS_LAB_STARTER_PROMPT_TEXT: list[str] = [
    "[yellow]Type 'Choose' followed by the Pokemon name:[/yellow]",
    "[dim]Example: Choose Bulbasaur[/dim]",
]

OAKS_LAB_PROGRESS_DIALOGUE: list[str] = [
    "[bold]Professor Oak:[/bold] [cyan]Hello! How is your Pokedex coming along?[/cyan]",
    "",
    "[cyan]   Remember, to make a complete guide of all Pokemon[/cyan]",
    "[cyan]   in the world... That is my dream![/cyan]",
    "",
    "[bold]Research Data:[/bold]",
    "   • Pokemon seen: [dim]Coming soon[/dim]",
]

OAKS_LAB_CAUGHT_COUNT: list[str] = [
    "   • Pokemon caught: [green]{caught_count}[/green]",
    "",
]

OAKS_LAB_EXIT: list[str] = [
    "[dim]You leave the laboratory[/dim]",
    "",
]

# ── choose_starter_pokemon ───────────────────────────────────────────────────

STARTER_INVALID_NOT_AVAILABLE: list[str] = [
    "",
    "[red]❌ Pikachu is not an available starter Pokemon![/red]",
    "[dim]Please choose: Bulbasaur, Charmander, or Squirtle[/dim]",
    "",
]

STARTER_PIKACHU_SELECTED: list[str] = [
    "",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "[bold yellow]⚡ You chose Pikachu! ⚡[/bold yellow]",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "",
    "[bold]Professor Oak:[/bold] [cyan]Wonderful![/cyan]",
    "",
    "[cyan]   Pikachu is very special - it loves to stay outside its Pokeball![/cyan]",
    "[cyan]   I'm sure you two will become great friends![/cyan]",
    "",
    "[green]✓ Pikachu (Lv. 5) was added to your party![/green]",
    "[dim]   (This Pikachu refuses to evolve)[/dim]",
    "",
    "[green]✓ Received 5 Potions![/green]",
    "",
    "[bold]Professor Oak:[/bold] [cyan]By the way, your rival already took Eevee![/cyan]",
    "",
]

STARTER_SELECTION_INVALID_PIKACHU_MODE: list[str] = [
    "",
    "[red]❌ That's not the right Pokemon![/red]",
    "[dim]Please choose: Pikachu[/dim]",
    "",
]

STARTER_SELECTION_INVALID_NORMAL_MODE: list[str] = [
    "",
    "[red]❌ That's not one of the starter Pokemon![/red]",
    "[dim]Please choose: Bulbasaur, Charmander, or Squirtle[/dim]",
    "",
]

STARTER_SELECTION_PIKACHU_ONLY: list[str] = [
    "",
    "[red]❌ That Pokemon is not available![/red]",
    "[dim]Please choose: Pikachu[/dim]",
    "",
]

STARTER_SELECTION_CONFIRMED: list[str] = [
    "",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "[bold green]{emoji} You chose {starter_name}! {emoji}[/bold green]",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "",
    "[bold]Professor Oak:[/bold] [cyan]Excellent choice![/cyan]",
    "",
    "[cyan]   {starter_name} is a wonderful Pokemon![/cyan]",
    "[cyan]   Treat it with love and kindness, and it will grow strong![/cyan]",
    "",
    "[green]✓ {starter_name} (Lv. 5) was added to your party![/green]",
    "",
    "[green]✓ Received 5 Potions![/green]",
    "",
    "[bold]Professor Oak:[/bold] [cyan]Oh! Your rival already chose {rival_pokemon}![/cyan]",
    "[cyan]   It seems he wanted to have an advantage over you![/cyan]",
    "",
]

STARTER_TURN_TO_LEAVE: list[str] = [
    "[dim]As you turn to leave...[/dim]",
    "",
]

STARTER_JOURNEY_READY_PIKACHU: list[str] = [
    "",
    "[bold]Professor Oak:[/bold] [cyan]Now you're ready to begin your Pokemon journey![/cyan]",
    "[cyan]   Be sure to visit the Pokemon Center if your Pokemon get hurt![/cyan]",
    "",
    "[dim]You leave the laboratory with your electric companion![/dim]",
    "",
]

STARTER_JOURNEY_READY: list[str] = [
    "",
    "[bold]Professor Oak:[/bold] [cyan]Now you're ready to begin your Pokemon journey![/cyan]",
    "[cyan]   Be sure to visit the Pokemon Center if your Pokemon get hurt![/cyan]",
    "",
    "[dim]You leave the laboratory with your new partner![/dim]",
    "",
]

# ── enter_ss_anne_dock ───────────────────────────────────────────────────────

SS_ANNE_DOCK_HEADER: list[str] = [
    "",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "[bold cyan]           ⚓ S.S. ANNE DOCK ⚓            [/bold cyan]",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "",
]

SS_ANNE_DOCK_WELCOME: list[str] = [
    "[bold]Dock Worker:[/bold] [cyan]Welcome to the Vermillion Harbour S.S. Anne Dock![/cyan]",
    "",
]

SS_ANNE_DOCK_HAS_TICKET: list[str] = [
    "[cyan]   I can see you have a ticket — the ship is ready to board![/cyan]",
    "[cyan]   Head around to the gangplank and use 'Move to S.S. Anne'.[/cyan]",
    "",
    "[dim]   The S.S. Anne is filled with trainers from around the world.[/dim]",
    "[dim]   The captain's cabin is somewhere aboard — he may have a reward for you.[/dim]",
]

SS_ANNE_DOCK_NO_TICKET: list[str] = [
    "[cyan]   Sorry, I can't let you through without an S.S. Anne Ticket.[/cyan]",
    "[cyan]   Have you spoken to Bill north of Cerulean City?[/cyan]",
    "",
    "[dim]   Bill hands out tickets to trainers he trusts.[/dim]",
    "[dim]   Visit Bill's House on Route 24 to obtain an S.S. Anne Ticket.[/dim]",
]

SS_ANNE_DOCK_FOOTER: list[str] = [
    "",
]

# ── enter_mr_fujis_house ─────────────────────────────────────────────────────

MR_FUJIS_RESCUED_DIALOGUE: list[str] = [
    "[bold]Mr. Fuji:[/bold] [cyan]Ah, my young rescuer! Welcome back.[/cyan]",
    "[cyan]   I hope the Poke Flute serves you well on your journey.[/cyan]",
    "[cyan]   The Pokemon laid to rest in the tower deserve peace.[/cyan]",
    "[cyan]   Thank you for driving out Team Rocket.[/cyan]",
]

MR_FUJIS_REWARD: list[str] = [
    "",
    "[bold yellow]★ Received Poke Flute! ★[/bold yellow]",
]

MR_FUJIS_NOT_HOME_DIALOGUE: list[str] = [
    "[bold]Old Woman:[/bold] [cyan]Mr. Fuji isn't here...[/cyan]",
    "[cyan]   He went up to Pokemon Tower as always, but he hasn't returned.[/cyan]",
    "[cyan]   We're all very worried.[/cyan]",
    "",
    "[dim]   The Pokemon Tower looms just east of town.[/dim]",
    "[dim]   If you're headed there, please see if Mr. Fuji is all right.[/dim]",
]

MR_FUJIS_HOUSE_FOOTER: list[str] = [
    "",
]

# ── enter_game_corner ────────────────────────────────────────────────────────

GAME_CORNER_ATTENDANT: list[str] = [
    "[bold]Attendant:[/bold] [yellow]Welcome to the Celadon Game Corner![/yellow]",
    "[yellow]   Try your luck on the slot machines![/yellow]",
    "",
]

GAME_CORNER_AFTER_HIDEOUT: list[str] = [
    "[dim]   The suspicious poster on the back wall has been removed.[/dim]",
    "[dim]   Team Rocket's presence here seems to have faded.[/dim]",
]

GAME_CORNER_HIDEOUT_HINT: list[str] = [
    "[dim]   The machines chime and flash all around you.[/dim]",
    "[dim]   A suspicious-looking poster adorns the back wall...[/dim]",
    "[dim]   Something feels off about this place — those men in black uniforms are everywhere.[/dim]",
    "",
    "[yellow]💡 Tip:[/yellow] [dim]Team Rocket's Hideout is accessible from Celadon City.[/dim]",
    "[dim]   Use 'Move to Team Rocket's Hideout' to investigate.[/dim]",
]

GAME_CORNER_FOOTER: list[str] = [
    "",
]

# ── enter_department_store ───────────────────────────────────────────────────

DEPARTMENT_STORE_WELCOME: list[str] = [
    "[bold]Clerk:[/bold] [yellow]Welcome to the Celadon Department Store![/yellow]",
    "[yellow]   We have six floors of Pokemon goods![/yellow]",
    "",
    "[bold green]Available items (selection):[/bold green]",
]

DEPARTMENT_STORE_MONEY: list[str] = [
    "   [bold]Your money:[/bold] [cyan]₽{money}[/cyan]",
    "",
]

DEPARTMENT_STORE_FOOTER: list[str] = [
    "",
    "[dim]   This is a display only — use the Pokemart for purchases.[/dim]",
    "[dim]   Tip: The Pokemart in Celadon stocks the full advanced catalogue.[/dim]",
    "",
]

# ── enter_safari_zone ────────────────────────────────────────────────────────

SAFARI_START_GAME_FIRST: list[str] = [
    "[red]❌ Start a game first![/red]",
]

SAFARI_WARDEN_INTRO: list[str] = [
    "[bold]Warden:[/bold] [green]Welcome, Trainer![/green]",
    "[green]   The Safari Zone is home to rare Pokemon found nowhere else![/green]",
    "[green]   The admission fee is ₽500 for 30 Safari Balls.[/green]",
    "",
]

SAFARI_NOT_ENOUGH_MONEY: list[str] = [
    "[red]Warden: You don't have enough money for admission (₽500 required).[/red]",
    "",
]

SAFARI_ENTRY_SUCCESS: list[str] = [
    "[green]   You paid ₽500 and received [bold]30 Safari Balls[/bold]![/green]",
    "",
]

SAFARI_RULES: list[str] = [
    "[bold]Safari Zone Rules:[/bold]",
    "   🎯 [cyan]safari ball[/cyan] — throw a Safari Ball to catch",
    "   🥩 [cyan]bait[/cyan]        — toss bait to make Pokemon easier to catch",
    "   🪨 [cyan]rock[/cyan]        — throw a rock to anger Pokemon (boosts catch rate briefly)",
    "   🏃 [cyan]run[/cyan]         — flee from the wild Pokemon",
    "",
    "[yellow]⚠️  You cannot battle wild Pokemon in the Safari Zone![/yellow]",
    "[dim]   Explore to encounter wild Pokemon. You have 30 Safari Balls.[/dim]",
    "",
]

SAFARI_BALLS_REMAINING: list[str] = [
    "[dim]Safari Balls remaining: {remaining}[/dim]",
    "",
]
