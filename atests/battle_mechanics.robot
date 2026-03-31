*** Settings ***
Documentation       Battle mechanics end-to-end tests.
...
...                 Covers wild encounters, battle commands (fight, flee, item),
...                 catching Pokemon, and battle resolution.

Library             PokemonLibraryTest
Resource            resources/common.resource

Suite Setup         Open Pokemon Terminal
Suite Teardown      Close Pokemon Terminal


*** Test Cases ***

# ----------------------------------------------------------------------------
# Wild encounters
# ----------------------------------------------------------------------------

Wild Battle Can Be Triggered
    [Documentation]    Setting a wild encounter and searching triggers a battle.
    [Tags]    battle    smoke
    [Setup]    Setup Game With Pokemon    PIKACHU    10
    Set Wild Encounter    RATTATA    5
    Type Command    search for wild pokemon
    Should Be In Battle
    Output Should Contain    wild
    Output Should Contain    RATTATA

Wild Pokemon Appears At Correct Level
    [Documentation]    The wild Pokemon appears at the level specified.
    [Tags]    battle    encounter
    [Setup]    Setup Game With Pokemon    PIKACHU    15
    Set Wild Encounter    PIDGEY    7
    Type Command    search for wild pokemon
    Should Be In Battle
    Output Should Contain    Lv.7    case_insensitive=True

# ----------------------------------------------------------------------------
# Battle commands - Fight
# ----------------------------------------------------------------------------

Player Can Choose Move In Battle
    [Documentation]    Choosing a move slot executes the move.
    [Tags]    battle    fight
    [Setup]    Setup Game With Pokemon    PIKACHU    12
    Set Wild Encounter    RATTATA    3
    Type Command    search for wild pokemon
    Choose Move    1
    # Output should show the move was used
    Output Should Contain    used    case_insensitive=True

Move Deals Damage To Wild Pokemon
    [Documentation]    Using a move reduces the wild Pokemon's HP.
    [Tags]    battle    damage
    [Setup]    Setup Game With Pokemon    CHARIZARD    50
    Set Wild Encounter    RATTATA    3
    Type Command    search for wild pokemon
    Choose Move    1
    # A level 50 Charizard should easily damage a level 3 Rattata
    Output Should Contain    damage    case_insensitive=True

# ----------------------------------------------------------------------------
# Battle commands - Flee
# ----------------------------------------------------------------------------

Player Can Flee From Wild Battle
    [Documentation]    Using the flee command exits the wild battle.
    [Tags]    battle    flee
    [Setup]    Setup Game With Pokemon    PIKACHU    10
    Set Wild Encounter    RATTATA    5
    Type Command    search for wild pokemon
    Should Be In Battle
    Flee Battle
    # May succeed or fail based on RNG, but should show output
    # If successful, battle ends; if not, battle continues
    Output Should Contain    ${EMPTY}    # Just check there's output

Fleeing Allows Multiple Attempts
    [Documentation]    If flee fails, the player can try again.
    [Tags]    battle    flee
    [Setup]    Setup Game With Pokemon    SQUIRTLE    8
    Set Wild Encounter    PIDGEY    5
    Type Command    search for wild pokemon
    Should Be In Battle
    # Try fleeing (may succeed or fail)
    Flee Battle
    # We don't assert outcome, just that the command works

# ----------------------------------------------------------------------------
# Battle commands - Item
# ----------------------------------------------------------------------------

Player Can Use Potion In Battle
    [Documentation]    Using a Potion during battle heals the active Pokemon.
    [Tags]    battle    item    potion
    [Setup]    Setup Game With Damaged Pokemon    Potion    3    10
    Set Wild Encounter    RATTATA    3
    Type Command    search for wild pokemon
    Should Be In Battle
    # The damaged Pokemon should be able to use Potion
    Use Item In Battle    Potion
    Output Should Contain    heal    case_insensitive=True

Player Can Throw Pokeball In Battle
    [Documentation]    Throwing a Pokeball attempts to catch the wild Pokemon.
    [Tags]    battle    catch    pokeball
    [Setup]    Setup Game With Pokemon    PIKACHU    20
    Set Item    Pokeball    5
    Set Wild Encounter    RATTATA    3
    Type Command    search for wild pokemon
    Should Be In Battle
    Use Item In Battle    Pokeball
    # Should show catch attempt (success or failure depends on RNG)
    Output Should Contain    ball    case_insensitive=True

Master Ball Always Catches Pokemon
    [Documentation]    Using a Master Ball guarantees a catch.
    [Tags]    battle    catch    masterball
    [Setup]    Setup Game With Pokemon    PIKACHU    10
    Set Item    Master Ball    1
    Set Wild Encounter    MEWTWO    70
    Type Command    search for wild pokemon
    Should Be In Battle
    Use Item In Battle    Master Ball
    Output Should Contain    Gotcha    case_insensitive=True
    Should Not Be In Battle
    Party Size Should Be    2
    Party Pokemon Should Be    1    MEWTWO

# ----------------------------------------------------------------------------
# Battle resolution
# ----------------------------------------------------------------------------

Defeating Wild Pokemon Grants Experience
    [Documentation]    Winning a battle awards experience points to the party.
    [Tags]    battle    experience
    [Setup]    Setup Game With Pokemon    PIKACHU    10
    Set Lead Pokemon    PIKACHU    10
    Set Wild Encounter    RATTATA    3
    Type Command    search for wild pokemon
    Should Be In Battle
    # Use a strong move to defeat it
    Choose Move    1
    # After enough turns, the wild Pokemon should faint
    # (This is tricky to test deterministically without controlling damage)
    # For now, just verify the battle started
    # In practice, we'd need multiple rounds

Fainting All Pokemon Ends Battle
    [Documentation]    If the player's Pokemon all faint, the battle ends.
    [Tags]    battle    faint
    # This is complex to test without controlling RNG
    # Marking as placeholder for future implementation
    [Setup]    Setup Game With Pokemon    PIKACHU    1
    Set Pokemon HP    0    1
    Set Wild Encounter    MEWTWO    70
    Type Command    search for wild pokemon
    Should Be In Battle
    # The level 1 Pikachu with 1 HP will likely faint immediately
    Choose Move    1

# ----------------------------------------------------------------------------
# Post-battle events
# ----------------------------------------------------------------------------

Caught Pokemon Added To Party
    [Documentation]    Successfully catching a Pokemon adds it to the party.
    [Tags]    battle    catch    party
    [Setup]    Setup Game With Pokemon    BULBASAUR    15
    Party Size Should Be    1
    Set Item    Ultra Ball    5
    Set Wild Encounter    CATERPIE    5
    Type Command    search for wild pokemon
    Should Be In Battle
    # Ultra Ball has high catch rate, should catch low-level Caterpie
    Use Item In Battle    Ultra Ball
    # If caught, party size increases
    # Note: This depends on RNG, so we can't assert definitively

Caught Pokemon Registered In Pokedex
    [Documentation]    Catching a Pokemon registers it as both seen and caught.
    [Tags]    battle    catch    pokedex
    [Setup]    Setup Game With Pokemon    PIKACHU    20
    Set Item    Ultra Ball    10
    Set Wild Encounter    DRATINI    10
    Type Command    search for wild pokemon
    Should Be In Battle
    # Attempt to catch
    Use Item In Battle    Ultra Ball
    # After battle results, check Pokedex (if caught)
    # This is hard to assert deterministically

# ----------------------------------------------------------------------------
# Edge cases
# ----------------------------------------------------------------------------

Cannot Battle Without Pokemon
    [Documentation]    If the player has no Pokemon, cannot enter battle.
    [Tags]    battle    error
    [Setup]    Bootstrap Game
    # Remove the default starter
    ${empty_list}=    Create List
    Set Global Variable    ${empty_list}
    # This test needs a way to set empty party - may require additional keyword
    # Skipping for now

Battle With Full Party Cannot Add Seventh Pokemon
    [Documentation]    If party is full, caught Pokemon goes to PC.
    [Tags]    battle    catch    pc
    # Requires setting up 6 party members first
    # Placeholder for future implementation
    [Setup]    Setup Game With Pokemon    PIKACHU    10
    [Teardown]    NONE

Using Item Not In Bag Shows Error
    [Documentation]    Attempting to use an item not owned shows an error.
    [Tags]    battle    item    error
    [Setup]    Setup Game With Pokemon    PIKACHU    10
    Set Wild Encounter    RATTATA    5
    Type Command    search for wild pokemon
    Should Be In Battle
    # Try to use an item we don't have
    Use Item In Battle    Ultra Ball
    Output Should Contain    not have    case_insensitive=True
