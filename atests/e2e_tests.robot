*** Settings ***
Documentation       End-to-end tests for PokemonLibrary using the PokemonLibraryTest keyword library.
...
...                 Runs the full PokemonTerminal Textual app in headless mode.
...                 Each test bootstraps its own game state and exercises real TUI code paths.

Library             PokemonLibraryTest
Resource            resources/common.resource

Suite Setup         Open Pokemon Terminal
Suite Teardown      Close Pokemon Terminal


*** Test Cases ***

# ----------------------------------------------------------------------------
# Main Menu
# ----------------------------------------------------------------------------

App Shows Main Menu On Startup
    [Documentation]    The app renders the main-menu panel on launch.
    [Tags]    smoke    menu
    Widget Should Be Visible    id=main-menu-actions
    Output Should Contain       MAIN MENU

Clicking New Game Opens Name Selection
    [Documentation]    Clicking the New Game button shows the name-selection panel.
    [Tags]    smoke    menu
    Click Widget    id=btn-new-game
    Widget Should Be Visible    id=name-selection

# ----------------------------------------------------------------------------
# Sell items at Pokemart
# ----------------------------------------------------------------------------

Sell Nugget Increases Money
    [Documentation]    Selling a Nugget from the shop adds ₽5000 to the player's wallet.
    [Tags]    shop    sell
    [Setup]    Setup Shop With Items    500    Nugget    1
    Type Command    sell nugget
    Output Should Contain    Sold 1x Nugget
    Money Should Be          5500
    Item Count Should Be     Nugget    0

Sell Multiple Potions At Once
    [Documentation]    'sell 3 potion' deducts all three and awards 3 × 150 = 450.
    [Tags]    shop    sell
    [Setup]    Setup Shop With Items    0    Potion    3
    Type Command    sell 3 potion
    Output Should Contain    Sold 3x Potion
    Money Should Be          450
    Item Count Should Be     Potion    0

Selling Item Not Owned Shows Error
    [Documentation]    Attempting to sell an item the player doesn't own shows an error.
    [Tags]    shop    sell    error
    [Setup]    Setup Shop    money=500
    Type Command    sell nugget
    Output Should Contain    don't have    case_insensitive=True
    Money Should Be          500

Sell Qty Clamped To Stock
    [Documentation]    Requesting more than owned quantity sells only what is available.
    [Tags]    shop    sell
    [Setup]    Setup Shop With Items    0    Potion    2
    Type Command    sell 10 potion
    Money Should Be          300
    Item Count Should Be     Potion    0

Buy Still Works After Sell Feature Added
    [Documentation]    Regression: the existing buy command still works.
    [Tags]    shop    buy    regression
    [Setup]    Setup Shop    money=1000
    Type Command    buy potion
    Output Should Contain    Bought

Player Can Buy Potion From Shop
    [Documentation]    Buying a Potion from the shop costs ₽200 and adds the item to bag.
    [Tags]    shop    buy
    [Setup]    Setup Shop    money=1000
    Type Command    buy potion
    Output Should Contain    Bought
    Item Count Should Be     Potion    1
    Money Should Be          800

Player Can Buy Multiple Items At Once
    [Documentation]    'buy 5 pokeball' purchases 5 Pokeballs at once.
    [Tags]    shop    buy
    [Setup]    Setup Shop    money=1000
    Type Command    buy 5 pokeball
    Output Should Contain    Bought
    Item Count Should Be     Pokeball    5
    Money Should Be          0

Player Cannot Buy Without Enough Money
    [Documentation]    Attempting to buy an item without enough money shows error and does not add item.
    [Tags]    shop    buy    error
    [Setup]    Setup Shop    money=50
    Type Command    buy potion
    Output Should Contain    not enough    case_insensitive=True
    Item Count Should Be     Potion    0
    Money Should Be          50

Buying Item Not In Catalog Shows Error
    [Documentation]    Attempting to buy an item not in the shop shows error.
    [Tags]    shop    buy    error
    [Setup]    Setup Shop    money=10000
    Type Command    buy master ball
    Output Should Contain    not found    case_insensitive=True
    Money Should Be          10000

Player Can Buy Antidote From Shop
    [Documentation]    Buying an Antidote costs ₽100.
    [Tags]    shop    buy
    [Setup]    Setup Shop    money=500
    Type Command    buy antidote
    Output Should Contain    Bought
    Item Count Should Be     Antidote    1
    Money Should Be          400

Player Can Buy Escape Rope From Shop
    [Documentation]    Buying an Escape Rope costs ₽550.
    [Tags]    shop    buy
    [Setup]    Setup Shop    money=600
    Type Command    buy escape rope
    Output Should Contain    Bought
    Item Count Should Be     Escape Rope    1
    Money Should Be          50

# ----------------------------------------------------------------------------
# Stone-based evolution
# ----------------------------------------------------------------------------

Fire Stone Evolves Growlithe To Arcanine
    [Documentation]    Using a Fire Stone on GROWLITHE produces ARCANINE and consumes the stone.
    [Tags]    evolution    stone
    [Setup]    Setup Evolution Test    GROWLITHE    Fire Stone
    Type Command    use fire stone on growlithe
    Output Should Contain       ARCANINE
    Party Pokemon Should Be     0    ARCANINE
    Item Count Should Be        Fire Stone    0

Moon Stone Evolves Clefairy To Clefable
    [Documentation]    Using a Moon Stone on CLEFAIRY produces CLEFABLE.
    [Tags]    evolution    stone
    [Setup]    Setup Evolution Test    CLEFAIRY    Moon Stone
    Type Command    use moon stone on clefairy
    Output Should Contain    CLEFABLE
    Party Pokemon Should Be     0    CLEFABLE
    Item Count Should Be        Moon Stone    0

Wrong Stone Has No Effect And Is Not Consumed
    [Documentation]    Using a Fire Stone on SQUIRTLE has no effect and keeps the stone.
    [Tags]    evolution    stone    error
    [Setup]    Setup Game With Item    Fire Stone    1
    Type Command    use fire stone on squirtle
    Output Should Contain       no effect    case_insensitive=True
    Party Pokemon Should Be     0    SQUIRTLE
    Item Count Should Be        Fire Stone    1

Thunder Stone Evolves Pikachu To Raichu
    [Documentation]    Using a Thunder Stone on PIKACHU produces RAICHU.
    [Tags]    evolution    stone
    [Setup]    Setup Evolution Test    PIKACHU    Thunder Stone
    Type Command    use thunder stone on pikachu
    Output Should Contain    RAICHU
    Party Pokemon Should Be     0    RAICHU
    Item Count Should Be        Thunder Stone    0

# ----------------------------------------------------------------------------
# Rival battle at Cerulean / Nugget Bridge
# ----------------------------------------------------------------------------

Rival Battle Triggers After All Nugget Trainers Beaten
    [Documentation]    Entering Nugget Bridge with all 5 trainers defeated triggers the rival.
    [Tags]    rival    battle
    [Setup]    Setup Rival Battle Conditions
    Type Command    enter nugget bridge
    Output Should Contain    familiar voice    case_insensitive=True
    Should Be In Battle
    Pending Command Should Be    battle

Rival Battle Not Triggered If Already Beaten
    [Documentation]    If the rival_cerulean_beaten flag is set no second battle fires.
    [Tags]    rival    battle    flag
    [Setup]    Setup Rival Battle Conditions
    Set Story Flag    rival_cerulean_beaten
    Type Command    enter nugget bridge
    Should Not Be In Battle

# ----------------------------------------------------------------------------
# Battle tests with newly implemented Pokemon
# ----------------------------------------------------------------------------

# TODO: Enable when Set Wild Encounter keyword is implemented
#Zubat Can Battle Against Wild Pokemon
#    [Documentation]    ZUBAT can engage in wild Pokemon battles successfully.
#    [Tags]    battle    phase1    zubat
#    [Setup]    Setup Game With Pokemon    ZUBAT    15
#    Set Wild Encounter    RATTATA    level=10
#    Type Command    explore
#    Should Be In Battle
#    Output Should Contain    ZUBAT

# TODO: Enable when Set Wild Encounter keyword is implemented
#Clefairy Learns Moves And Can Use Them
#    [Documentation]    CLEFAIRY has proper moves and can use them in battle.
#    [Tags]    battle    phase1    clefairy
#    [Setup]    Setup Game With Pokemon    CLEFAIRY    20
#    Set Wild Encounter    RATTATA    level=10
#    Type Command    explore
#    Should Be In Battle
#    Type Command    moves
#    # Should show at least one move other than just Tackle

# TODO: Enable when Set Wild Encounter keyword is implemented
#Jigglypuff Has High HP In Battle
#    [Documentation]    JIGGLYPUFF displays its signature high HP during battles.
#    [Tags]    battle    phase1    jigglypuff
#    [Setup]    Setup Game With Pokemon    JIGGLYPUFF    20
#    Set Wild Encounter    RATTATA    level=10
#    Type Command    explore
#    Should Be In Battle
#    # HP bar should show Jigglypuff has more HP than typical Pokemon

Staryu Can Battle In Gym
    [Documentation]    STARYU functions properly in gym battles (Misty's team).
    [Tags]    battle    phase2    gym    staryu
    [Setup]    Setup Game At Location    Cerulean City
    Add Badge    Boulder Badge
    Set Lead Pokemon    PIKACHU    25
    Type Command    enter gym
    Click Widget    id=btn-gym-challenge
    Should Be In Battle
    Output Should Contain    Misty

# TODO: Enable when Set Wild Encounter keyword is implemented
#Abra Teleport Move Works In Battle
#    [Documentation]    ABRA's signature TELEPORT move functions in battle (flee mechanic).
#    [Tags]    battle    phase3    abra
#    [Setup]    Setup Game With Pokemon    ABRA    10
#    Set Wild Encounter    RATTATA    level=5
#    Type Command    explore
#    Should Be In Battle
#    Type Command    moves
#    Output Should Contain    TELEPORT

# TODO: Enable when Set Wild Encounter keyword is implemented
#Ekans Poison Type Advantage Works
#    [Documentation]    EKANS (Poison type) gets proper type matchups in battle.
#    [Tags]    battle    phase3    ekans
#    [Setup]    Setup Game With Pokemon    EKANS    20
#    Set Wild Encounter    ODDISH    level=15
#    Type Command    explore
#    Should Be In Battle
#    # Poison vs Grass should have type effectiveness

# TODO: Enable when Set Wild Encounter keyword is implemented
#Alakazam High Special Stat Affects Damage
#    [Documentation]    ALAKAZAM with high Special stat deals appropriate damage.
#    [Tags]    battle    phase4    alakazam
#    [Setup]    Setup Game With Pokemon    ALAKAZAM    50
#    Set Wild Encounter    RATTATA    level=10
#    Type Command    explore
#    Should Be In Battle
#    # Alakazam should have very high special stat visible

# TODO: Enable when Set Wild Encounter keyword is implemented
#Water Stone Evolution Creates Battle Ready Starmie
#    [Documentation]    STARMIE evolved via Water Stone is immediately battle-ready.
#    [Tags]    battle    phase2    evolution    starmie
#    [Setup]    Setup Evolution Test    STARYU    Water Stone
#    Type Command    use water stone on staryu
#    Party Pokemon Should Be    0    STARMIE
#    Set Wild Encounter    RATTATA    level=10
#    Type Command    explore
#    Should Be In Battle
#    Output Should Contain    STARMIE

# TODO: Enable when Set Wild Encounter keyword is implemented
#Dual Type Pokemon Show Both Types In Battle
#    [Documentation]    Dual-type Pokemon (like Oddish: Grass/Poison) display both types.
#    [Tags]    battle    phase3    oddish
#    [Setup]    Setup Game With Pokemon    ODDISH    15
#    Set Wild Encounter    RATTATA    level=10
#    Type Command    explore
#    Should Be In Battle
#    Type Command    inspect oddish
#    Output Should Contain    Grass
