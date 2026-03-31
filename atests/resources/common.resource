*** Settings ***
Documentation       Shared settings and keywords for PokemonLibrary end-to-end tests.
...
...                 Import this resource in every e2e test suite:
...
...                 | Resource    resources/common.resource |
...
...                 Suite lifecycle:
...                 | Suite Setup     | Open Pokemon Terminal |
...                 | Suite Teardown  | Close Pokemon Terminal |
...
...                 Each test case can use ``[Setup]`` with one of the keywords below
...                 instead of calling ``Bootstrap Game`` directly.

Library             PokemonLibraryTest


*** Keywords ***

# ── Basic game setup ──────────────────────────────────────────────────────

Setup Game
    [Documentation]    Bootstrap a clean game at Pallet Town with default starter.
    ...                Use this as [Setup] for tests that don't need special configuration.
    Bootstrap Game

Setup Game At Location
    [Documentation]    Bootstrap game at a specific location.
    ...                Example: [Setup]    Setup Game At Location    Viridian City
    [Arguments]    ${location}
    Bootstrap Game    location=${location}

# ── Item-focused setups ───────────────────────────────────────────────────

Setup Game With Item
    [Documentation]    Bootstrap game and add one item to the bag.
    ...                Example: [Setup]    Setup Game With Item    Potion    3
    [Arguments]    ${item_name}    ${quantity}=1
    Bootstrap Game
    Set Item    ${item_name}    ${quantity}

Setup Game With Items
    [Documentation]    Bootstrap game and add multiple items.
    ...                Pass item/quantity pairs as arguments.
    ...                Example: [Setup]    Setup Game With Items    Potion    3    Pokeball    5
    [Arguments]    @{items}
    Bootstrap Game
    ${item_count}=    Get Length    ${items}
    FOR    ${i}    IN RANGE    0    ${item_count}    2
        ${item_name}=    Set Variable    ${items}[${i}]
        ${quantity}=    Set Variable    ${items}[${i+1}]
        Set Item    ${item_name}    ${quantity}
    END

# ── Pokemon-focused setups ────────────────────────────────────────────────

Setup Game With Pokemon
    [Documentation]    Bootstrap game and set a specific lead Pokemon at the given level.
    ...                Example: [Setup]    Setup Game With Pokemon    CHARMANDER    15
    [Arguments]    ${species}    ${level}=15
    Bootstrap Game
    Set Lead Pokemon    ${species}    level=${level}

Setup Game With Damaged Pokemon
    [Documentation]    Bootstrap game with a damaged lead Pokemon and a healing item.
    ...                Example: [Setup]    Setup Game With Damaged Pokemon    Potion    1    5
    [Arguments]    ${item_name}    ${item_qty}=1    ${hp}=5
    Bootstrap Game
    Set Item    ${item_name}    ${item_qty}
    Set Pokemon HP    0    ${hp}

# ── Shop setups ───────────────────────────────────────────────────────────

Setup Shop
    [Documentation]    Bootstrap game and enter shop pending-command state with basic catalog.
    ...                Useful for buy/sell tests. Optionally set initial money.
    ...                Example: [Setup]    Setup Shop    money=1000
    [Arguments]    ${money}=3000
    Bootstrap Game
    Set Money    ${money}
    Set Pending Command    shop    _current_shop_catalog=basic

Setup Shop With Items
    [Documentation]    Bootstrap game, set money, add items, and enter shop state.
    ...                Example: [Setup]    Setup Shop With Items    500    Nugget    1
    [Arguments]    ${money}    ${item_name}    ${item_qty}
    Bootstrap Game
    Set Money    ${money}
    Set Item    ${item_name}    ${item_qty}
    Set Pending Command    shop    _current_shop_catalog=basic

# ── Evolution test setups ─────────────────────────────────────────────────

Setup Evolution Test
    [Documentation]    Bootstrap game with a specific Pokemon and evolution stone.
    ...                Example: [Setup]    Setup Evolution Test    GROWLITHE    Fire Stone
    [Arguments]    ${pokemon_species}    ${stone_name}
    Bootstrap Game
    Set Lead Pokemon    ${pokemon_species}
    Set Item    ${stone_name}    1

# ── Badge/gym setups ──────────────────────────────────────────────────────

Setup Game With Badges
    [Documentation]    Bootstrap game and add one or more badges.
    ...                Example: [Setup]    Setup Game With Badges    Boulder Badge    Cascade Badge
    [Arguments]    @{badge_names}
    Bootstrap Game
    FOR    ${badge}    IN    @{badge_names}
        Add Badge    ${badge}
    END

# ── Battle/trainer setups ─────────────────────────────────────────────────

Setup Rival Battle Conditions
    [Documentation]    Bootstrap at location with all nugget trainers defeated.
    ...                Example: [Setup]    Setup Rival Battle Conditions
    [Arguments]    ${location}=Cerulean City
    Bootstrap Game    location=${location}
    Add Defeated Trainer    nugget_trainer_1
    Add Defeated Trainer    nugget_trainer_2
    Add Defeated Trainer    nugget_trainer_3
    Add Defeated Trainer    nugget_trainer_4
    Add Defeated Trainer    nugget_trainer_5

# ── Move learning setups ──────────────────────────────────────────────────

Setup Move Learn Test
    [Documentation]    Bootstrap game with CHARMANDER at level 17 (4 moves) and queue a move prompt.
    ...                Example: [Setup]    Setup Move Learn Test    RAGE
    [Arguments]    ${move_name}    ${remaining}=${EMPTY}
    Bootstrap Game
    Set Lead Pokemon    CHARMANDER    level=17
    IF    '${remaining}' != ''
        Set Learn Move Prompt    ${move_name}    remaining=${remaining}
    ELSE
        Set Learn Move Prompt    ${move_name}
    END
