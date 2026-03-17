"""Tests for PokemonLibrary/data/pokemon_data.py — verifying newly-implemented species data."""

import pytest

from pytemon.data.pokemon_data import (
    FLYING,
    GRASS,
    GROUND,
    NORMAL,
    POISON,
    POKEMON,
    PSYCHIC,
    WATER,
    ItemEvolution,
    LevelEvolution,
)

# ===========================================================================
# Phase 1: Critical Wild Encounters
# ===========================================================================


class TestPhase1WildEncounters:
    """Tests for Phase 1: Critical wild encounter Pokemon."""

    def test_zubat_exists_and_not_stub(self):
        """Zubat (#41) has full data (not stub)."""
        assert 41 in POKEMON
        zubat = POKEMON[41]
        assert zubat.name == "ZUBAT"
        assert zubat.number == 41
        # Verify not stub (stubs have 50 in all stats)
        assert zubat.stats.hp != 50 or zubat.stats.attack != 50

    def test_zubat_dual_type(self):
        """Zubat is Poison/Flying."""
        zubat = POKEMON[41]
        assert len(zubat.types) == 2
        assert POISON in zubat.types
        assert FLYING in zubat.types

    def test_zubat_evolution(self):
        """Zubat evolves to Golbat at level 22."""
        zubat = POKEMON[41]
        assert zubat.evolution is not None
        assert isinstance(zubat.evolution, LevelEvolution)
        assert zubat.evolution.level == 22
        assert zubat.evolution.into_species == "GOLBAT"

    def test_zubat_learnset_valid(self):
        """Zubat has a valid learnset."""
        zubat = POKEMON[41]
        assert len(zubat.learnset) >= 3
        assert 1 in zubat.learnset
        assert len(zubat.learnset[1]) >= 1

    def test_clefairy_exists_and_not_stub(self):
        """Clefairy (#35) has full data (not stub)."""
        assert 35 in POKEMON
        clefairy = POKEMON[35]
        assert clefairy.name == "CLEFAIRY"
        assert clefairy.number == 35
        assert clefairy.stats.hp != 50 or clefairy.stats.attack != 50

    def test_clefairy_type(self):
        """Clefairy is Normal."""
        clefairy = POKEMON[35]
        assert clefairy.types == [NORMAL]

    def test_clefairy_evolution(self):
        """Clefairy evolves with Moon Stone to Clefable."""
        clefairy = POKEMON[35]
        assert clefairy.evolution is not None
        assert isinstance(clefairy.evolution, ItemEvolution)
        assert clefairy.evolution.item == "MOON STONE"
        assert clefairy.evolution.into_species == "CLEFABLE"

    def test_clefairy_learnset_valid(self):
        """Clefairy has a valid learnset."""
        clefairy = POKEMON[35]
        assert len(clefairy.learnset) >= 3
        assert 1 in clefairy.learnset

    def test_jigglypuff_exists_and_not_stub(self):
        """Jigglypuff (#39) has full data (not stub)."""
        assert 39 in POKEMON
        jiggly = POKEMON[39]
        assert jiggly.name == "JIGGLYPUFF"
        assert jiggly.number == 39
        assert jiggly.stats.hp != 50 or jiggly.stats.attack != 50

    def test_jigglypuff_type(self):
        """Jigglypuff is Normal."""
        jiggly = POKEMON[39]
        assert jiggly.types == [NORMAL]

    def test_jigglypuff_evolution(self):
        """Jigglypuff evolves with Moon Stone to Wigglytuff."""
        jiggly = POKEMON[39]
        assert jiggly.evolution is not None
        assert isinstance(jiggly.evolution, ItemEvolution)
        assert jiggly.evolution.item == "MOON STONE"
        assert jiggly.evolution.into_species == "WIGGLYTUFF"

    def test_jigglypuff_high_hp(self):
        """Jigglypuff has famously high HP."""
        jiggly = POKEMON[39]
        assert jiggly.stats.hp == 115

    def test_meowth_exists_and_not_stub(self):
        """Meowth (#52) has full data (not stub)."""
        assert 52 in POKEMON
        meowth = POKEMON[52]
        assert meowth.name == "MEOWTH"
        assert meowth.number == 52
        assert meowth.stats.hp != 50 or meowth.stats.attack != 50

    def test_meowth_type(self):
        """Meowth is Normal."""
        meowth = POKEMON[52]
        assert meowth.types == [NORMAL]

    def test_meowth_evolution(self):
        """Meowth evolves to Persian at level 28."""
        meowth = POKEMON[52]
        assert meowth.evolution is not None
        assert isinstance(meowth.evolution, LevelEvolution)
        assert meowth.evolution.level == 28
        assert meowth.evolution.into_species == "PERSIAN"

    def test_meowth_learnset_valid(self):
        """Meowth has a valid learnset."""
        meowth = POKEMON[52]
        assert len(meowth.learnset) >= 3
        assert 1 in meowth.learnset


# ===========================================================================
# Phase 2: Gym Leaders
# ===========================================================================


class TestPhase2GymLeaders:
    """Tests for Phase 2: Gym leader Pokemon."""

    def test_staryu_exists_and_not_stub(self):
        """Staryu (#120) has full data (not stub)."""
        assert 120 in POKEMON
        staryu = POKEMON[120]
        assert staryu.name == "STARYU"
        assert staryu.number == 120
        assert staryu.stats.hp != 50 or staryu.stats.attack != 50

    def test_staryu_type(self):
        """Staryu is Water."""
        staryu = POKEMON[120]
        assert staryu.types == [WATER]

    def test_staryu_evolution(self):
        """Staryu evolves with Water Stone to Starmie."""
        staryu = POKEMON[120]
        assert staryu.evolution is not None
        assert isinstance(staryu.evolution, ItemEvolution)
        assert staryu.evolution.item == "WATER STONE"
        assert staryu.evolution.into_species == "STARMIE"

    def test_starmie_exists_and_not_stub(self):
        """Starmie (#121) has full data (not stub)."""
        assert 121 in POKEMON
        starmie = POKEMON[121]
        assert starmie.name == "STARMIE"
        assert starmie.number == 121
        assert starmie.stats.hp != 50 or starmie.stats.attack != 50

    def test_starmie_dual_type(self):
        """Starmie is Water/Psychic."""
        starmie = POKEMON[121]
        assert len(starmie.types) == 2
        assert WATER in starmie.types
        assert PSYCHIC in starmie.types

    def test_starmie_no_evolution(self):
        """Starmie does not evolve."""
        starmie = POKEMON[121]
        assert starmie.evolution is None

    def test_horsea_exists_and_not_stub(self):
        """Horsea (#116) has full data (not stub)."""
        assert 116 in POKEMON
        horsea = POKEMON[116]
        assert horsea.name == "HORSEA"
        assert horsea.number == 116
        assert horsea.stats.hp != 50 or horsea.stats.attack != 50

    def test_horsea_type(self):
        """Horsea is Water."""
        horsea = POKEMON[116]
        assert horsea.types == [WATER]

    def test_horsea_evolution(self):
        """Horsea evolves to Seadra at level 32."""
        horsea = POKEMON[116]
        assert horsea.evolution is not None
        assert isinstance(horsea.evolution, LevelEvolution)
        assert horsea.evolution.level == 32
        assert horsea.evolution.into_species == "SEADRA"

    def test_goldeen_exists_and_not_stub(self):
        """Goldeen (#118) has full data (not stub)."""
        assert 118 in POKEMON
        goldeen = POKEMON[118]
        assert goldeen.name == "GOLDEEN"
        assert goldeen.number == 118
        assert goldeen.stats.hp != 50 or goldeen.stats.attack != 50

    def test_goldeen_type(self):
        """Goldeen is Water."""
        goldeen = POKEMON[118]
        assert goldeen.types == [WATER]

    def test_goldeen_evolution(self):
        """Goldeen evolves to Seaking at level 33."""
        goldeen = POKEMON[118]
        assert goldeen.evolution is not None
        assert isinstance(goldeen.evolution, LevelEvolution)
        assert goldeen.evolution.level == 33
        assert goldeen.evolution.into_species == "SEAKING"


# ===========================================================================
# Phase 3: Trainer Battles
# ===========================================================================


class TestPhase3TrainerBattles:
    """Tests for Phase 3: Trainer battle Pokemon."""

    def test_ekans_exists_and_not_stub(self):
        """Ekans (#23) has full data (not stub)."""
        assert 23 in POKEMON
        ekans = POKEMON[23]
        assert ekans.name == "EKANS"
        assert ekans.number == 23
        assert ekans.stats.hp != 50 or ekans.stats.attack != 50

    def test_ekans_type(self):
        """Ekans is Poison."""
        ekans = POKEMON[23]
        assert ekans.types == [POISON]

    def test_ekans_evolution(self):
        """Ekans evolves to Arbok at level 22."""
        ekans = POKEMON[23]
        assert ekans.evolution is not None
        assert isinstance(ekans.evolution, LevelEvolution)
        assert ekans.evolution.level == 22
        assert ekans.evolution.into_species == "ARBOK"

    def test_sandshrew_exists_and_not_stub(self):
        """Sandshrew (#27) has full data (not stub)."""
        assert 27 in POKEMON
        sandshrew = POKEMON[27]
        assert sandshrew.name == "SANDSHREW"
        assert sandshrew.number == 27
        assert sandshrew.stats.hp != 50 or sandshrew.stats.attack != 50

    def test_sandshrew_type(self):
        """Sandshrew is Ground."""
        sandshrew = POKEMON[27]
        assert sandshrew.types == [GROUND]

    def test_sandshrew_evolution(self):
        """Sandshrew evolves to Sandslash at level 22."""
        sandshrew = POKEMON[27]
        assert sandshrew.evolution is not None
        assert isinstance(sandshrew.evolution, LevelEvolution)
        assert sandshrew.evolution.level == 22
        assert sandshrew.evolution.into_species == "SANDSLASH"

    def test_abra_exists_and_not_stub(self):
        """Abra (#63) has full data (not stub)."""
        assert 63 in POKEMON
        abra = POKEMON[63]
        assert abra.name == "ABRA"
        assert abra.number == 63
        assert abra.stats.hp != 50 or abra.stats.attack != 50

    def test_abra_type(self):
        """Abra is Psychic."""
        abra = POKEMON[63]
        assert abra.types == [PSYCHIC]

    def test_abra_evolution(self):
        """Abra evolves to Kadabra at level 16."""
        abra = POKEMON[63]
        assert abra.evolution is not None
        assert isinstance(abra.evolution, LevelEvolution)
        assert abra.evolution.level == 16
        assert abra.evolution.into_species == "KADABRA"

    def test_abra_teleport_only(self):
        """Abra only knows Teleport at level 1."""
        abra = POKEMON[63]
        assert 1 in abra.learnset
        assert "TELEPORT" in abra.learnset[1]

    def test_oddish_exists_and_not_stub(self):
        """Oddish (#43) has full data (not stub)."""
        assert 43 in POKEMON
        oddish = POKEMON[43]
        assert oddish.name == "ODDISH"
        assert oddish.number == 43
        assert oddish.stats.hp != 50 or oddish.stats.attack != 50

    def test_oddish_dual_type(self):
        """Oddish is Grass/Poison."""
        oddish = POKEMON[43]
        assert len(oddish.types) == 2
        assert GRASS in oddish.types
        assert POISON in oddish.types

    def test_oddish_evolution(self):
        """Oddish evolves to Gloom at level 21."""
        oddish = POKEMON[43]
        assert oddish.evolution is not None
        assert isinstance(oddish.evolution, LevelEvolution)
        assert oddish.evolution.level == 21
        assert oddish.evolution.into_species == "GLOOM"

    def test_bellsprout_exists_and_not_stub(self):
        """Bellsprout (#69) has full data (not stub)."""
        assert 69 in POKEMON
        bellsprout = POKEMON[69]
        assert bellsprout.name == "BELLSPROUT"
        assert bellsprout.number == 69
        assert bellsprout.stats.hp != 50 or bellsprout.stats.attack != 50

    def test_bellsprout_dual_type(self):
        """Bellsprout is Grass/Poison."""
        bellsprout = POKEMON[69]
        assert len(bellsprout.types) == 2
        assert GRASS in bellsprout.types
        assert POISON in bellsprout.types

    def test_bellsprout_evolution(self):
        """Bellsprout evolves to Weepinbell at level 21."""
        bellsprout = POKEMON[69]
        assert bellsprout.evolution is not None
        assert isinstance(bellsprout.evolution, LevelEvolution)
        assert bellsprout.evolution.level == 21
        assert bellsprout.evolution.into_species == "WEEPINBELL"


# ===========================================================================
# Phase 4: Evolutions
# ===========================================================================


class TestPhase4Evolutions:
    """Tests for Phase 4: Evolution line completion."""

    def test_arbok_exists_and_not_stub(self):
        """Arbok (#24) has full data (not stub)."""
        assert 24 in POKEMON
        arbok = POKEMON[24]
        assert arbok.name == "ARBOK"
        assert arbok.number == 24
        assert arbok.stats.hp != 50 or arbok.stats.attack != 50

    def test_arbok_no_evolution(self):
        """Arbok does not evolve."""
        arbok = POKEMON[24]
        assert arbok.evolution is None

    def test_sandslash_exists_and_not_stub(self):
        """Sandslash (#28) has full data (not stub)."""
        assert 28 in POKEMON
        sandslash = POKEMON[28]
        assert sandslash.name == "SANDSLASH"
        assert sandslash.number == 28
        assert sandslash.stats.hp != 50 or sandslash.stats.attack != 50

    def test_sandslash_no_evolution(self):
        """Sandslash does not evolve."""
        sandslash = POKEMON[28]
        assert sandslash.evolution is None

    def test_clefable_exists_and_not_stub(self):
        """Clefable (#36) has full data (not stub)."""
        assert 36 in POKEMON
        clefable = POKEMON[36]
        assert clefable.name == "CLEFABLE"
        assert clefable.number == 36
        assert clefable.stats.hp != 50 or clefable.stats.attack != 50

    def test_clefable_no_evolution(self):
        """Clefable does not evolve."""
        clefable = POKEMON[36]
        assert clefable.evolution is None

    def test_wigglytuff_exists_and_not_stub(self):
        """Wigglytuff (#40) has full data (not stub)."""
        assert 40 in POKEMON
        wigglytuff = POKEMON[40]
        assert wigglytuff.name == "WIGGLYTUFF"
        assert wigglytuff.number == 40
        assert wigglytuff.stats.hp != 50 or wigglytuff.stats.attack != 50

    def test_wigglytuff_no_evolution(self):
        """Wigglytuff does not evolve."""
        wigglytuff = POKEMON[40]
        assert wigglytuff.evolution is None

    def test_wigglytuff_even_higher_hp(self):
        """Wigglytuff has even higher HP than Jigglypuff."""
        wigglytuff = POKEMON[40]
        assert wigglytuff.stats.hp == 140

    def test_persian_exists_and_not_stub(self):
        """Persian (#53) has full data (not stub)."""
        assert 53 in POKEMON
        persian = POKEMON[53]
        assert persian.name == "PERSIAN"
        assert persian.number == 53
        assert persian.stats.hp != 50 or persian.stats.attack != 50

    def test_persian_no_evolution(self):
        """Persian does not evolve."""
        persian = POKEMON[53]
        assert persian.evolution is None

    def test_golbat_exists_and_not_stub(self):
        """Golbat (#42) has full data (not stub)."""
        assert 42 in POKEMON
        golbat = POKEMON[42]
        assert golbat.name == "GOLBAT"
        assert golbat.number == 42
        assert golbat.stats.hp != 50 or golbat.stats.attack != 50

    def test_golbat_dual_type(self):
        """Golbat is Poison/Flying."""
        golbat = POKEMON[42]
        assert len(golbat.types) == 2
        assert POISON in golbat.types
        assert FLYING in golbat.types

    def test_golbat_no_evolution(self):
        """Golbat does not evolve (in Gen 1)."""
        golbat = POKEMON[42]
        assert golbat.evolution is None

    def test_golem_exists_and_not_stub(self):
        """Golem (#76) has full data (not stub)."""
        assert 76 in POKEMON
        golem = POKEMON[76]
        assert golem.name == "GOLEM"
        assert golem.number == 76
        assert golem.stats.hp != 50 or golem.stats.attack != 50

    def test_golem_no_evolution(self):
        """Golem does not evolve."""
        golem = POKEMON[76]
        assert golem.evolution is None

    def test_seadra_exists_and_not_stub(self):
        """Seadra (#117) has full data (not stub)."""
        assert 117 in POKEMON
        seadra = POKEMON[117]
        assert seadra.name == "SEADRA"
        assert seadra.number == 117
        assert seadra.stats.hp != 50 or seadra.stats.attack != 50

    def test_seadra_no_evolution(self):
        """Seadra does not evolve (in Gen 1)."""
        seadra = POKEMON[117]
        assert seadra.evolution is None

    def test_seaking_exists_and_not_stub(self):
        """Seaking (#119) has full data (not stub)."""
        assert 119 in POKEMON
        seaking = POKEMON[119]
        assert seaking.name == "SEAKING"
        assert seaking.number == 119
        assert seaking.stats.hp != 50 or seaking.stats.attack != 50

    def test_seaking_no_evolution(self):
        """Seaking does not evolve."""
        seaking = POKEMON[119]
        assert seaking.evolution is None

    def test_kadabra_exists_and_not_stub(self):
        """Kadabra (#64) has full data (not stub)."""
        assert 64 in POKEMON
        kadabra = POKEMON[64]
        assert kadabra.name == "KADABRA"
        assert kadabra.number == 64
        assert kadabra.stats.hp != 50 or kadabra.stats.attack != 50

    def test_kadabra_type(self):
        """Kadabra is Psychic."""
        kadabra = POKEMON[64]
        assert kadabra.types == [PSYCHIC]

    def test_kadabra_evolution(self):
        """Kadabra evolves to Alakazam via Link Cable (trade-evolver converted to item)."""
        kadabra = POKEMON[64]
        assert kadabra.evolution is not None
        assert isinstance(kadabra.evolution, ItemEvolution)
        assert kadabra.evolution.item.upper() == "LINK CABLE"
        assert kadabra.evolution.into_species == "ALAKAZAM"

    def test_alakazam_exists_and_not_stub(self):
        """Alakazam (#65) has full data (not stub)."""
        assert 65 in POKEMON
        alakazam = POKEMON[65]
        assert alakazam.name == "ALAKAZAM"
        assert alakazam.number == 65
        assert alakazam.stats.hp != 50 or alakazam.stats.attack != 50

    def test_alakazam_type(self):
        """Alakazam is Psychic."""
        alakazam = POKEMON[65]
        assert alakazam.types == [PSYCHIC]

    def test_alakazam_no_evolution(self):
        """Alakazam does not evolve."""
        alakazam = POKEMON[65]
        assert alakazam.evolution is None

    def test_alakazam_high_special(self):
        """Alakazam has very high Special stat."""
        alakazam = POKEMON[65]
        assert alakazam.stats.special >= 120

    def test_gloom_exists_and_not_stub(self):
        """Gloom (#44) has full data (not stub)."""
        assert 44 in POKEMON
        gloom = POKEMON[44]
        assert gloom.name == "GLOOM"
        assert gloom.number == 44
        assert gloom.stats.hp != 50 or gloom.stats.attack != 50

    def test_gloom_dual_type(self):
        """Gloom is Grass/Poison."""
        gloom = POKEMON[44]
        assert len(gloom.types) == 2
        assert GRASS in gloom.types
        assert POISON in gloom.types

    def test_gloom_evolution(self):
        """Gloom evolves with Leaf Stone to Vileplume."""
        gloom = POKEMON[44]
        assert gloom.evolution is not None
        assert isinstance(gloom.evolution, ItemEvolution)
        assert gloom.evolution.item == "LEAF STONE"
        assert gloom.evolution.into_species == "VILEPLUME"

    def test_vileplume_exists_and_not_stub(self):
        """Vileplume (#45) has full data (not stub)."""
        assert 45 in POKEMON
        vileplume = POKEMON[45]
        assert vileplume.name == "VILEPLUME"
        assert vileplume.number == 45
        assert vileplume.stats.hp != 50 or vileplume.stats.attack != 50

    def test_vileplume_dual_type(self):
        """Vileplume is Grass/Poison."""
        vileplume = POKEMON[45]
        assert len(vileplume.types) == 2
        assert GRASS in vileplume.types
        assert POISON in vileplume.types

    def test_vileplume_no_evolution(self):
        """Vileplume does not evolve."""
        vileplume = POKEMON[45]
        assert vileplume.evolution is None

    def test_weepinbell_exists_and_not_stub(self):
        """Weepinbell (#70) has full data (not stub)."""
        assert 70 in POKEMON
        weepinbell = POKEMON[70]
        assert weepinbell.name == "WEEPINBELL"
        assert weepinbell.number == 70
        assert weepinbell.stats.hp != 50 or weepinbell.stats.attack != 50

    def test_weepinbell_dual_type(self):
        """Weepinbell is Grass/Poison."""
        weepinbell = POKEMON[70]
        assert len(weepinbell.types) == 2
        assert GRASS in weepinbell.types
        assert POISON in weepinbell.types

    def test_weepinbell_evolution(self):
        """Weepinbell evolves with Leaf Stone to Victreebel."""
        weepinbell = POKEMON[70]
        assert weepinbell.evolution is not None
        assert isinstance(weepinbell.evolution, ItemEvolution)
        assert weepinbell.evolution.item == "LEAF STONE"
        assert weepinbell.evolution.into_species == "VICTREEBEL"

    def test_victreebel_exists_and_not_stub(self):
        """Victreebel (#71) has full data (not stub)."""
        assert 71 in POKEMON
        victreebel = POKEMON[71]
        assert victreebel.name == "VICTREEBEL"
        assert victreebel.number == 71
        assert victreebel.stats.hp != 50 or victreebel.stats.attack != 50

    def test_victreebel_dual_type(self):
        """Victreebel is Grass/Poison."""
        victreebel = POKEMON[71]
        assert len(victreebel.types) == 2
        assert GRASS in victreebel.types
        assert POISON in victreebel.types

    def test_victreebel_no_evolution(self):
        """Victreebel does not evolve."""
        victreebel = POKEMON[71]
        assert victreebel.evolution is None


# ===========================================================================
# Cross-Phase Validation Tests
# ===========================================================================


class TestStatsValidation:
    """Validate that stats are realistic (not all 50s)."""

    @pytest.mark.parametrize(
        "number",
        [
            23,
            24,
            27,
            28,
            35,
            36,
            39,
            40,
            41,
            42,
            43,
            44,
            45,
            52,
            53,
            63,
            64,
            65,
            69,
            70,
            71,
            76,
            116,
            117,
            118,
            119,
            120,
            121,
        ],
    )
    def test_hp_in_realistic_range(self, number):
        """All newly-implemented Pokemon have HP between 20-255."""
        pokemon = POKEMON[number]
        assert 20 <= pokemon.stats.hp <= 255

    @pytest.mark.parametrize(
        "number",
        [
            23,
            24,
            27,
            28,
            35,
            36,
            39,
            40,
            41,
            42,
            43,
            44,
            45,
            52,
            53,
            63,
            64,
            65,
            69,
            70,
            71,
            76,
            116,
            117,
            118,
            119,
            120,
            121,
        ],
    )
    def test_attack_in_realistic_range(self, number):
        """All newly-implemented Pokemon have Attack between 5-255."""
        pokemon = POKEMON[number]
        assert 5 <= pokemon.stats.attack <= 255

    @pytest.mark.parametrize(
        "number",
        [
            23,
            24,
            27,
            28,
            35,
            36,
            39,
            40,
            41,
            42,
            43,
            44,
            45,
            52,
            53,
            63,
            64,
            65,
            69,
            70,
            71,
            76,
            116,
            117,
            118,
            119,
            120,
            121,
        ],
    )
    def test_not_all_stats_are_50(self, number):
        """Newly-implemented Pokemon are not stubs (not all stats = 50)."""
        pokemon = POKEMON[number]
        stats = [
            pokemon.stats.hp,
            pokemon.stats.attack,
            pokemon.stats.defense,
            pokemon.stats.special,
            pokemon.stats.speed,
        ]
        # At least one stat must differ from 50
        assert not all(s == 50 for s in stats)


class TestLearnsetValidation:
    """Validate that all Pokemon have valid learnsets."""

    @pytest.mark.parametrize(
        "number",
        [
            23,
            24,
            27,
            28,
            35,
            36,
            39,
            40,
            41,
            42,
            43,
            44,
            45,
            52,
            53,
            63,
            64,
            65,
            69,
            70,
            71,
            76,
            116,
            117,
            118,
            119,
            120,
            121,
        ],
    )
    def test_has_level_1_move(self, number):
        """All newly-implemented Pokemon have at least one move at level 1."""
        pokemon = POKEMON[number]
        assert 1 in pokemon.learnset
        assert len(pokemon.learnset[1]) >= 1

    @pytest.mark.parametrize(
        "number",
        [
            23,
            24,
            27,
            28,
            35,
            36,
            39,
            40,
            41,
            42,
            43,
            44,
            45,
            52,
            53,
            63,
            64,
            65,
            69,
            70,
            71,
            76,
            116,
            117,
            118,
            119,
            120,
            121,
        ],
    )
    def test_has_minimum_moves(self, number):
        """All newly-implemented Pokemon have at least 1 level in learnset."""
        pokemon = POKEMON[number]
        assert len(pokemon.learnset) >= 1


class TestEvolutionChains:
    """Validate complete evolution chains."""

    def test_ekans_to_arbok_chain(self):
        """Ekans → Arbok chain is complete."""
        ekans = POKEMON[23]
        arbok = POKEMON[24]
        assert ekans.evolution.into_species == "ARBOK"
        assert arbok.evolution is None

    def test_sandshrew_to_sandslash_chain(self):
        """Sandshrew → Sandslash chain is complete."""
        sandshrew = POKEMON[27]
        sandslash = POKEMON[28]
        assert sandshrew.evolution.into_species == "SANDSLASH"
        assert sandslash.evolution is None

    def test_clefairy_to_clefable_chain(self):
        """Clefairy → Clefable chain is complete."""
        clefairy = POKEMON[35]
        clefable = POKEMON[36]
        assert clefairy.evolution.into_species == "CLEFABLE"
        assert clefable.evolution is None

    def test_jigglypuff_to_wigglytuff_chain(self):
        """Jigglypuff → Wigglytuff chain is complete."""
        jiggly = POKEMON[39]
        wiggly = POKEMON[40]
        assert jiggly.evolution.into_species == "WIGGLYTUFF"
        assert wiggly.evolution is None

    def test_meowth_to_persian_chain(self):
        """Meowth → Persian chain is complete."""
        meowth = POKEMON[52]
        persian = POKEMON[53]
        assert meowth.evolution.into_species == "PERSIAN"
        assert persian.evolution is None

    def test_zubat_to_golbat_chain(self):
        """Zubat → Golbat chain is complete."""
        zubat = POKEMON[41]
        golbat = POKEMON[42]
        assert zubat.evolution.into_species == "GOLBAT"
        assert golbat.evolution is None

    def test_abra_kadabra_alakazam_chain(self):
        """Abra → Kadabra → Alakazam chain is complete."""
        abra = POKEMON[63]
        kadabra = POKEMON[64]
        alakazam = POKEMON[65]
        assert abra.evolution.into_species == "KADABRA"
        assert kadabra.evolution.into_species == "ALAKAZAM"
        assert alakazam.evolution is None

    def test_oddish_gloom_vileplume_chain(self):
        """Oddish → Gloom → Vileplume chain is complete."""
        oddish = POKEMON[43]
        gloom = POKEMON[44]
        vileplume = POKEMON[45]
        assert oddish.evolution.into_species == "GLOOM"
        assert gloom.evolution.into_species == "VILEPLUME"
        assert vileplume.evolution is None

    def test_bellsprout_weepinbell_victreebel_chain(self):
        """Bellsprout → Weepinbell → Victreebel chain is complete."""
        bellsprout = POKEMON[69]
        weepinbell = POKEMON[70]
        victreebel = POKEMON[71]
        assert bellsprout.evolution.into_species == "WEEPINBELL"
        assert weepinbell.evolution.into_species == "VICTREEBEL"
        assert victreebel.evolution is None

    def test_horsea_to_seadra_chain(self):
        """Horsea → Seadra chain is complete."""
        horsea = POKEMON[116]
        seadra = POKEMON[117]
        assert horsea.evolution.into_species == "SEADRA"
        assert seadra.evolution is None

    def test_goldeen_to_seaking_chain(self):
        """Goldeen → Seaking chain is complete."""
        goldeen = POKEMON[118]
        seaking = POKEMON[119]
        assert goldeen.evolution.into_species == "SEAKING"
        assert seaking.evolution is None

    def test_staryu_to_starmie_chain(self):
        """Staryu → Starmie chain is complete."""
        staryu = POKEMON[120]
        starmie = POKEMON[121]
        assert staryu.evolution.into_species == "STARMIE"
        assert starmie.evolution is None
