*** Settings ***
Documentation       Interactive move-learn prompt end-to-end tests using Robot Framework.
...
...                 Covers the ``learn_move_choice`` pending-command flow:
...                 choosing a slot to replace, typing 'no' to skip, out-of-range
...                 input re-prompting, and queued multiple moves.

Library             PokemonLibraryTest
Resource            resources/common.resource

Suite Setup         Open Pokemon Terminal
Suite Teardown      Close Pokemon Terminal


*** Variables ***
${CHARMANDER_LEVEL}    17


*** Test Cases ***

# ----------------------------------------------------------------------------
# Slot replacement
# ----------------------------------------------------------------------------

Choosing Slot 1 Replaces First Move
    [Documentation]    When the lead Pokemon has a full moveset and a new move is queued,
    ...                typing '1' replaces the first move slot with the new move.
    [Tags]    move_learn    slot
    [Setup]    Setup Move Learn Test    RAGE
    Type Command    1
    Output Should Contain    RAGE
    Pending Command Should Be Empty

Choosing Slot 4 Replaces Last Move
    [Documentation]    Typing '4' replaces the fourth (last) move slot.
    [Tags]    move_learn    slot
    [Setup]    Setup Move Learn Test    SLASH
    Type Command    4
    Output Should Contain    SLASH
    Pending Command Should Be Empty

# ----------------------------------------------------------------------------
# Skip learning
# ----------------------------------------------------------------------------

Typing No Skips Learning New Move
    [Documentation]    Typing 'no' declines the new move without modifying the moveset.
    [Tags]    move_learn    skip
    [Setup]    Setup Move Learn Test    RAGE
    Type Command    no
    Output Should Contain    did not learn    case_insensitive=True
    Pending Command Should Be Empty

# ----------------------------------------------------------------------------
# Input validation
# ----------------------------------------------------------------------------

Out Of Range Slot Number Re-Prompts
    [Documentation]    Entering '9' (out of range 1–4) keeps the prompt active.
    [Tags]    move_learn    validation
    [Setup]    Setup Move Learn Test    RAGE
    Type Command    9
    Pending Command Should Be    learn_move_choice

# ----------------------------------------------------------------------------
# Queued moves
# ----------------------------------------------------------------------------

Second Queued Move Shows Next Prompt After First Is Resolved
    [Documentation]    When two moves are queued, resolving the first advances to the second.
    [Tags]    move_learn    queue
    [Setup]    Setup Move Learn Test    RAGE    SLASH
    Type Command    1
    Pending Command Should Be    learn_move_choice
