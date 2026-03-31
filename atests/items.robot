*** Settings ***
Documentation       Item usage outside of battle end-to-end tests.
...
...                 Covers the ``use <item>``, ``use <item> on <pokemon>`` commands
...                 for healing, stat boosters, Rare Candy, Repel, and Escape Rope.

Library             PokemonLibraryTest
Resource            resources/common.resource

Suite Setup         Open Pokemon Terminal
Suite Teardown      Close Pokemon Terminal


*** Test Cases ***

# ----------------------------------------------------------------------------
# Rare Candy
# ----------------------------------------------------------------------------

Rare Candy Increases Lead Pokemon Level
    [Documentation]    Using a Rare Candy on the lead Pokemon increases its level by 1.
    [Tags]    items    rare_candy
    [Setup]    Setup Game With Item    Rare Candy    1
    Type Command    use rare candy on squirtle
    Output Should Contain    grew to Level    case_insensitive=True
    Item Count Should Be    Rare Candy    0

Rare Candy On Named Pokemon Works
    [Documentation]    'use rare candy on squirtle' targets SQUIRTLE specifically.
    [Tags]    items    rare_candy
    [Setup]    Setup Game With Item    Rare Candy    1
    Party Pokemon Level Should Be    0    10
    Type Command    use rare candy on squirtle
    Output Should Contain    grew to Level    case_insensitive=True
    Party Pokemon Level Should Be    0    11

Rare Candy Consumed After Use
    [Documentation]    The Rare Candy is removed from the bag after use.
    [Tags]    items    rare_candy
    [Setup]    Setup Game With Item    Rare Candy    3
    Type Command    use rare candy on squirtle
    Item Count Should Be    Rare Candy    2

# ----------------------------------------------------------------------------
# Potion / healing items
# ----------------------------------------------------------------------------

Potion Heals Damaged Pokemon
    [Documentation]    Using a Potion on a damaged Pokemon restores some HP.
    [Tags]    items    heal
    [Setup]    Setup Game With Damaged Pokemon    Potion    1    5
    Type Command    use potion
    Output Should Contain    recovered    case_insensitive=True
    Item Count Should Be    Potion    0

Potion On Full HP Shows Warning
    [Documentation]    Using a Potion when the Pokemon is at full HP shows a message.
    [Tags]    items    heal    edge_case
    [Setup]    Setup Game With Item    Potion    1
    Type Command    use potion
    Output Should Contain    already full    case_insensitive=True

Potion Heals Specific Named Pokemon
    [Documentation]    'use potion on squirtle' heals SQUIRTLE specifically.
    [Tags]    items    heal
    [Setup]    Setup Game With Damaged Pokemon    Potion    1    5
    Type Command    use potion on squirtle
    Output Should Contain    recovered    case_insensitive=True

# ----------------------------------------------------------------------------
# Repel
# ----------------------------------------------------------------------------

Repel Activates And Is Consumed
    [Documentation]    Using a Repel activates the repel effect and removes it from the bag.
    [Tags]    items    repel
    [Setup]    Setup Game With Item    Repel    1
    Type Command    use repel
    Output Should Contain    Repel used    case_insensitive=True
    Item Count Should Be    Repel    0

Super Repel Provides More Explores Than Repel
    [Documentation]    Super Repel covers more explores than a standard Repel.
    [Tags]    items    repel
    [Setup]    Setup Game With Item    Super Repel    1
    Type Command    use super repel
    Output Should Contain    20 explores    case_insensitive=True
    Item Count Should Be    Super Repel    0

# ----------------------------------------------------------------------------
# Escape Rope
# ----------------------------------------------------------------------------

Escape Rope In Town Shows Already In Town Message
    [Documentation]    Using an Escape Rope while already in a town shows a message.
    [Tags]    items    escape_rope
    [Setup]    Setup Game With Item    Escape Rope    1
    Type Command    use escape rope
    Output Should Contain    already in a town    case_insensitive=True

# ----------------------------------------------------------------------------
# Error cases
# ----------------------------------------------------------------------------

Use Item Not In Bag Shows Error
    [Documentation]    Using an item the player does not own shows an error.
    [Tags]    items    error
    [Setup]    Setup Game
    Type Command    use hyper potion
    Output Should Contain    don't have any    case_insensitive=True

Use Unknown Item Shows Error
    [Documentation]    Using a completely unknown item name shows an error.
    [Tags]    items    error
    [Setup]    Setup Game
    Type Command    use unobtainium
    Output Should Contain    Unknown item    case_insensitive=True

Pokeball Cannot Be Used Outside Battle
    [Documentation]    Pokeballs have no out-of-battle effect.
    [Tags]    items    error    ball
    [Setup]    Setup Game With Item    Pokeball    1
    Type Command    use pokeball
    Output Should Contain    can only be used in battle    case_insensitive=True
