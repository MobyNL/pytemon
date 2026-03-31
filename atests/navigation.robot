*** Settings ***
Documentation       Navigation and exploration end-to-end tests.
...
...                 Covers the ``look``, ``status``, ``move to``, ``show party``,
...                 ``show bag``, ``explore`` and ``help`` commands.

Library             PokemonLibraryTest
Resource            resources/common.resource

Suite Setup         Open Pokemon Terminal
Suite Teardown      Close Pokemon Terminal


*** Test Cases ***

# ----------------------------------------------------------------------------
# look around
# ----------------------------------------------------------------------------

Look Around Shows Current Location Name
    [Documentation]    'look around' outputs the name of the current location.
    [Tags]    navigation    look
    [Setup]    Setup Game
    Type Command    look around
    Output Should Contain    Pallet Town

Look Around Shows Available Paths
    [Documentation]    'look around' lists at least one available exit.
    [Tags]    navigation    look
    [Setup]    Setup Game
    Type Command    look around
    Output Should Contain    Available Paths

Look Around Shows Buildings In Town
    [Documentation]    'look around' lists buildings when the player is in a town.
    [Tags]    navigation    look
    [Setup]    Setup Game
    Type Command    look around
    Output Should Contain    Buildings

Look Around In Viridian City Shows That Location
    [Documentation]    'look around' while in Viridian City outputs 'Viridian City'.
    [Tags]    navigation    look
    [Setup]    Setup Game At Location    Viridian City
    Type Command    look around
    Output Should Contain    Viridian City

Look Alias Works Same As Look Around
    [Documentation]    The short alias 'look' is equivalent to 'look around'.
    [Tags]    navigation    look
    [Setup]    Setup Game
    Type Command    look
    Output Should Contain    Pallet Town

# ----------------------------------------------------------------------------
# status
# ----------------------------------------------------------------------------

Status Shows Player Name
    [Documentation]    'status' outputs the player's trainer name.
    [Tags]    navigation    status
    [Setup]    Setup Game
    Type Command    status
    Output Should Contain    Ash

Status Shows Current Location
    [Documentation]    'status' outputs the current location name.
    [Tags]    navigation    status
    [Setup]    Setup Game
    Type Command    status
    Output Should Contain    Pallet Town

Status Shows Money Amount
    [Documentation]    'status' displays the player's money.
    [Tags]    navigation    status
    [Setup]    Setup Game
    Set Money    9999
    Type Command    status
    Output Should Contain    9999

Status Shows Badge Count
    [Documentation]    'status' shows badge count (0/8 initially).
    [Tags]    navigation    status    badges
    [Setup]    Setup Game
    Type Command    status
    Output Should Contain    0/8

# ----------------------------------------------------------------------------
# movement
# ----------------------------------------------------------------------------

Move To Route 1 From Pallet Town Succeeds
    [Documentation]    Player can travel north from Pallet Town to Route 1.
    [Tags]    navigation    move
    [Setup]    Setup Game
    Type Command    move to route 1
    Output Should Contain    Route 1

Move To Invalid Location Shows Error
    [Documentation]    Attempting to move to a non-existent location shows an error.
    [Tags]    navigation    move    error
    [Setup]    Setup Game
    Type Command    move to atlantis
    Output Should Contain    can't go    case_insensitive=True

Status After Moving Shows New Location
    [Documentation]    After teleporting to Viridian City, 'status' reflects the new location.
    [Tags]    navigation    move    status
    [Setup]    Setup Game
    Set Location    Viridian City
    Type Command    status
    Output Should Contain    Viridian City

# ----------------------------------------------------------------------------
# show party
# ----------------------------------------------------------------------------

Show Party Opens Party Panel
    [Documentation]    'show party' opens the party panel.
    [Tags]    navigation    party
    [Setup]    Setup Game
    Type Command    show party
    Widget Should Be Visible    id=party-panel

Party Alias Opens Party Panel
    [Documentation]    The 'party' alias also opens the party panel.
    [Tags]    navigation    party
    [Setup]    Setup Game
    Type Command    party
    Widget Should Be Visible    id=party-panel

Status Shows Party Pokemon
    [Documentation]    'status' shows the Pokemon in the party (in the output log).
    [Tags]    navigation    party    status
    [Setup]    Setup Game
    Type Command    status
    Output Should Contain    Pokemon Party

# ----------------------------------------------------------------------------
# show bag
# ----------------------------------------------------------------------------

Show Bag When Empty Reports Empty
    [Documentation]    'show bag' reports an empty bag when the player has no items.
    [Tags]    navigation    bag
    [Setup]    Setup Game
    Type Command    show bag
    Output Should Contain    empty    case_insensitive=True

Show Bag With Items Lists Item Names
    [Documentation]    'show bag' lists items the player currently holds.
    [Tags]    navigation    bag
    [Setup]    Setup Game With Item    Potion    3
    Type Command    show bag
    Output Should Contain    Potion

Show Bag Lists Item Quantity
    [Documentation]    'show bag' shows the quantity of each item.
    [Tags]    navigation    bag
    [Setup]    Setup Game With Item    Pokeball    5
    Type Command    show bag
    Output Should Contain    5

Bag Alias Works Same As Show Bag
    [Documentation]    The 'bag' alias is equivalent to 'show bag'.
    [Tags]    navigation    bag
    [Setup]    Setup Game With Item    Potion    1
    Type Command    bag
    Output Should Contain    Potion

# ----------------------------------------------------------------------------
# help
# ----------------------------------------------------------------------------

Help Command Shows Command List
    [Documentation]    'help' outputs the list of available commands.
    [Tags]    navigation    help
    [Setup]    Setup Game
    Type Command    help
    Output Should Contain    help    case_insensitive=True
