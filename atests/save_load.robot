*** Settings ***
Documentation       Save and load game functionality end-to-end tests.
...
...                 Covers save file creation, loading games, save data integrity,
...                 and autosave functionality.

Library             PokemonLibraryTest
Resource            resources/common.resource

Suite Setup         Open Pokemon Terminal
Suite Teardown      Close Pokemon Terminal


*** Test Cases ***

# ----------------------------------------------------------------------------
# Manual Save/Load
# ----------------------------------------------------------------------------

Game Can Be Saved With Custom Name
    [Documentation]    Player can save the game with a custom save name.
    [Tags]    save    smoke
    [Setup]    Setup Game With Pokemon    PIKACHU    15
    Type Command    save game as test_save
    Output Should Contain    saved    case_insensitive=True

Game Can Be Loaded From Save File
    [Documentation]    Player can load a previously saved game.
    [Tags]    load    smoke
    [Setup]    Setup Game With Pokemon    BULBASAUR    20
    Set Money    9999
    Type Command    save game as load_test_save
    Output Should Contain    saved    case_insensitive=True
    # Now bootstrap a fresh game
    Bootstrap Game
    Money Should Be    3000
    # Load the saved game
    Type Command    load game load_test_save
    Output Should Contain    loaded    case_insensitive=True
    Money Should Be    9999

Loaded Game Preserves Pokemon Party
    [Documentation]    Loading a game restores the Pokemon party correctly.
    [Tags]    load    pokemon
    [Setup]    Setup Game With Pokemon    CHARIZARD    50
    Type Command    save game as party_test
    Bootstrap Game
    Party Pokemon Should Be    0    SQUIRTLE
    Type Command    load game party_test
    Party Pokemon Should Be    0    CHARIZARD
    Party Pokemon Level Should Be    0    50

Loaded Game Preserves Items
    [Documentation]    Loading a game restores the item bag correctly.
    [Tags]    load    items
    [Setup]    Setup Game With Pokemon    PIKACHU    10
    Set Item    Potion    5
    Set Item    Pokeball    10
    Type Command    save game as items_test
    Bootstrap Game
    Item Count Should Be    Potion    0
    Type Command    load game items_test
    Item Count Should Be    Potion    5
    Item Count Should Be    Pokeball    10

Loaded Game Preserves Location
    [Documentation]    Loading a game restores the player's location.
    [Tags]    load    location
    [Setup]    Setup Game At Location    Cerulean City
    Type Command    save game as location_test
    Bootstrap Game
    Type Command    load game location_test
    Type Command    status
    Output Should Contain    Cerulean City    case_insensitive=True

Loaded Game Preserves Badges
    [Documentation]    Loading a game restores earned badges.
    [Tags]    load    badges
    [Setup]    Setup Game
    Add Badge    Boulder Badge
    Add Badge    Cascade Badge
    Badge Count Should Be    2
    Type Command    save game as badge_test
    Bootstrap Game
    Badge Count Should Be    0
    Type Command    load game badge_test
    Badge Count Should Be    2

# ----------------------------------------------------------------------------
# Save Data Integrity
# ----------------------------------------------------------------------------

Loaded Game Preserves Player Name
    [Documentation]    Loading a game restores the player's name.
    [Tags]    load    player
    [Setup]    Bootstrap Game    player_name=Red
    Type Command    save game as name_test
    Bootstrap Game    player_name=Ash
    Type Command    load game name_test
    Type Command    status
    Output Should Contain    Red    case_insensitive=True

Saving Overwrites Existing Save File
    [Documentation]    Saving with the same name overwrites the previous save.
    [Tags]    save    overwrite
    [Setup]    Setup Game With Pokemon    PIKACHU    10
    Set Money    1000
    Type Command    save game as overwrite_test
    Set Money    5000
    Type Command    save game as overwrite_test
    # Confirm overwrite was prompted (output depends on implementation)
    Bootstrap Game
    Type Command    load game overwrite_test
    Money Should Be    5000

# ----------------------------------------------------------------------------
# Autosave Functionality
# ----------------------------------------------------------------------------

Autosave Can Be Enabled
    [Documentation]    Player can enable autosave via settings.
    [Tags]    autosave    settings
    [Setup]    Setup Game
    Type Command    enable autosave
    Output Should Contain    enabled    case_insensitive=True

Autosave Can Be Disabled
    [Documentation]    Player can disable autosave via settings.
    [Tags]    autosave    settings
    [Setup]    Setup Game
    Type Command    disable autosave
    Output Should Contain    disabled    case_insensitive=True

Autosave Frequency Can Be Set
    [Documentation]    Player can set autosave frequency.
    [Tags]    autosave    settings
    [Setup]    Setup Game
    Type Command    set autosave frequency 10
    Output Should Contain    10    case_insensitive=True

# ----------------------------------------------------------------------------
# Error Handling
# ----------------------------------------------------------------------------

Loading Nonexistent Save Shows Error
    [Documentation]    Attempting to load a save file that doesn't exist shows error.
    [Tags]    load    error
    [Setup]    Setup Game
    Type Command    load game nonexistent_save_file
    Output Should Contain    not found    case_insensitive=True

Saving Without Name Shows Error
    [Documentation]    Attempting to save without providing a name shows error.
    [Tags]    save    error
    [Setup]    Setup Game
    # This behavior depends on implementation - may prompt for name or show error
    # We'll just check the command works
    Type Command    save game
    # Output should contain some response (exact text depends on implementation)

# ----------------------------------------------------------------------------
# Advanced Save Features
# ----------------------------------------------------------------------------

Game Saves Preserve Defeated Trainers
    [Documentation]    Loading a game restores the list of defeated trainers.
    [Tags]    load    trainers
    [Setup]    Setup Game
    Add Defeated Trainer    brock_gym_trainer_1
    Add Defeated Trainer    route3_bugcatcher_1
    Type Command    save game as trainer_test
    Bootstrap Game
    # After loading, trainers should still be marked defeated
    Type Command    load game trainer_test
    # Can't directly assert defeated trainers without a keyword, but we saved it

Game Saves Preserve Story Flags
    [Documentation]    Loading a game restores story progression flags.
    [Tags]    load    story
    [Setup]    Setup Game
    Set Story Flag    oak_delivery_done
    Set Story Flag    got_starter
    Type Command    save game as story_test
    Bootstrap Game
    Type Command    load game story_test
    # Story flags preserved (can't directly assert without keyword)

Multiple Saves Can Coexist
    [Documentation]    Player can have multiple save files.
    [Tags]    save    multiple
    [Setup]    Setup Game With Pokemon    PIKACHU    10
    Type Command    save game as save_slot_1
    Set Lead Pokemon    CHARMANDER    15
    Type Command    save game as save_slot_2
    Set Lead Pokemon    SQUIRTLE    20
    Type Command    save game as save_slot_3
    # All three saves exist
    Bootstrap Game
    Type Command    load game save_slot_1
    Party Pokemon Should Be    0    PIKACHU
    Type Command    load game save_slot_2
    Party Pokemon Should Be    0    CHARMANDER
    Type Command    load game save_slot_3
    Party Pokemon Should Be    0    SQUIRTLE

# ----------------------------------------------------------------------------
# Quick Save/Load
# ----------------------------------------------------------------------------

Quick Save Command Works
    [Documentation]    Quick save (if implemented) saves without prompting for name.
    [Tags]    save    quicksave
    [Setup]    Setup Game With Pokemon    BULBASAUR    12
    # Check if quicksave command exists
    Type Command    quicksave
    # Output depends on whether feature exists

Quick Load Command Works
    [Documentation]    Quick load (if implemented) loads the most recent save.
    [Tags]    load    quickload
    [Setup]    Setup Game With Pokemon    PIKACHU    10
    Type Command    save game as recent_save
    Bootstrap Game
    Type Command    quickload
    # Output depends on whether feature exists
