#include "global.h"
#include "pokemon.h"
#include "constants/pokemon.h"
#include "constants/species.h"
#include "daycare.h"
#include "constants/items.h"
#include "constants/region_map_sections.h"
#include "random.h"                       // Random()を使うため
#include "constants/songs.h"
#include "event_data.h"                   // フラグ操作で使う Flagset(), FlagClear()
#include "constants/flags.h"              // フラグを参照する FLAG_SHOW_DELIBIRD_OUTSIDE_NPC
#include "constants/delibirdShop.h"
#include "delibirdShop_C.h"

static const struct EggGachaEntry sNormalEggEntries[] =
{
    { SPECIES_UNOWN,          200 }, // 調整枠
    { SPECIES_CLEFAIRY,       350 },
    { SPECIES_WEEDLE,         350 },
    { SPECIES_PIDGEY,         350 },
    { SPECIES_RATICATE,       350 },
    { SPECIES_SANDSHREW,      350 },
    { SPECIES_NIDORAN_F,      350 },
    { SPECIES_NIDORAN_M,      350 },
    { SPECIES_NINETALES,      350 },
    { SPECIES_GOLBAT,         350 },
    { SPECIES_VILEPLUME,      350 },
    { SPECIES_VENONAT,        350 },
    { SPECIES_DIGLETT,        350 },
    { SPECIES_MANKEY,         350 },
    { SPECIES_POLIWAG,        350 },
    { SPECIES_KADABRA,        350 },
    { SPECIES_MACHOKE,        350 },
    { SPECIES_TENTACOOL,      350 },
    { SPECIES_GOLEM,          350 },
    { SPECIES_SLOWPOKE,       350 },
    { SPECIES_DODUO,          350 },
    { SPECIES_GRIMER,         350 },
    { SPECIES_GASTLY,         350 },
    { SPECIES_HYPNO,          350 },
    { SPECIES_KINGLER,        350 },
    { SPECIES_EXEGGCUTE,      350 },
    { SPECIES_MAROWAK,        350 },
    { SPECIES_LICKITUNG,      350 },
    { SPECIES_KANGASKHAN,     350 },
};

static const struct EggGachaEntry sSpecialEggEntries[] =
{
    { SPECIES_UNOWN,        120 }, //調整枠
    { SPECIES_YANMA,        380 },
    { SPECIES_BAYLEEF,      380 },
    { SPECIES_DITTO,        380 },
    { SPECIES_MAGMAR,       380 },
    { SPECIES_GYARADOS,     380 },
    { SPECIES_MR_MIME,      380 },
    { SPECIES_SEAKING,      380 },
    { SPECIES_WEEZING,      380 },
    { SPECIES_GENGAR,       380 },
    { SPECIES_ARBOK,        380 },
    { SPECIES_ARTICUNO,     380 },
    { SPECIES_MEWTWO,       380 },
    { SPECIES_QUILAVA,      380 },
    { SPECIES_FERALIGATR,   380 },
    { SPECIES_NOCTOWL,      380 },
    { SPECIES_AMPHAROS,     380 },
    { SPECIES_HOPPIP,       380 },
    { SPECIES_JUMPLUFF,     380 },
    { SPECIES_SUNKERN,      380 },
    { SPECIES_SLOWKING,     380 },
    { SPECIES_QWILFISH,     380 },
    { SPECIES_SHUCKLE,      380 },
    { SPECIES_OCTILLERY,    380 },
    { SPECIES_MANTINE,      380 },
    { SPECIES_HOUNDOUR,     380 },
    { SPECIES_TYROGUE,      380 },
};

static const struct EggGachaEntry sRareEggEntries[] =
{
    { SPECIES_UNOWN,         100 }, // 調整枠
    { SPECIES_FLAREON,       900 }, 
    { SPECIES_SNEASEL,       900 },
    { SPECIES_SNUBBULL,      900 },
    { SPECIES_DUNSPARCE,     900 },
    { SPECIES_GIRAFARIG,     900 },
    { SPECIES_NATU,          900 },
    { SPECIES_CLEFFA,        900 },
    { SPECIES_CHINCHOU,      900 },
    { SPECIES_SPINARAK,      900 },
    { SPECIES_DRAGONAIR,     900 },
    { SPECIES_MOLTRES,       900 },

};

static const struct EggGachaEntry sSuperRareEggEntries[] =
{
    // 調整枠オニスズメ
    { SPECIES_WINGULL,       1600 }, 

    { SPECIES_MILTANK,       1400 },
    { SPECIES_LARVITAR,      1400 },
    { SPECIES_LUGIA,         1400 },
    { SPECIES_GROVYLE,       1400 },
    { SPECIES_KINGDRA,       1400 },
    { SPECIES_URSARING,      1400 },
};

static const struct EggGachaEntry sEpicEggEntries[] =
{
    // 調整枠人形たち
    { SPECIES_NUZLEAF,        1400 },
    { SPECIES_LUDICOLO,       1400 },

    { SPECIES_PSYDUCK,         600 },
    { SPECIES_MARILL,          600 },
    { SPECIES_UMBREON,         600 },
    { SPECIES_SMOOCHUM,        600 },
    { SPECIES_MUDKIP,          600 },
    { SPECIES_POOCHYENA,       600 },
    { SPECIES_LINOONE,         600 },
    { SPECIES_BEAUTIFLY,       600 },
    { SPECIES_LOTAD,           600 },
    { SPECIES_SUICUNE,         600 },
    { SPECIES_TAILLOW,         600 },
    { SPECIES_PILOSWINE,       600 },
};

static const struct EggGachaEntry sRandomEggEntries[] =
{
    // ハズレ枠
    // パーセンテージ調整枠
    { SPECIES_UNOWN,        120 },

    //【普通率】30体
    { SPECIES_TOTODILE,     100 },
    { SPECIES_WEEDLE,       100 },
    { SPECIES_PIDGEY,       100 },
    { SPECIES_RATICATE,     100 },
    { SPECIES_SANDSHREW,    100 },
    { SPECIES_NIDORAN_F,    100 },
    { SPECIES_NIDORAN_M,    100 },
    { SPECIES_CLEFAIRY,     100 },
    { SPECIES_NINETALES,    100 },
    { SPECIES_GOLBAT,       100 },
    { SPECIES_VILEPLUME,    100 },
    { SPECIES_VENONAT,      100 },
    { SPECIES_DIGLETT,      100 },
    { SPECIES_MANKEY,       100 },
    { SPECIES_POLIWAG,      100 },
    { SPECIES_KADABRA,      100 },
    { SPECIES_MACHOKE,      100 },
    { SPECIES_TENTACOOL,    100 },
    { SPECIES_GOLEM,        100 },
    { SPECIES_SLOWPOKE,     100 },
    { SPECIES_DODUO,        100 },
    { SPECIES_GRIMER,       100 },
    { SPECIES_GASTLY,       100 },
    { SPECIES_HYPNO,        100 },
    { SPECIES_KINGLER,      100 },
    { SPECIES_EXEGGCUTE,    100 },
    { SPECIES_MAROWAK,      100 },
    { SPECIES_LICKITUNG,    100 },
    { SPECIES_KANGASKHAN,   100 },
    { SPECIES_SEADRA,       100 },

    // 【スペシャルエッグ】26体
    { SPECIES_MAGMAR,       150 },
    { SPECIES_GYARADOS,     150 },
    { SPECIES_DITTO,        150 },
    { SPECIES_MR_MIME,      150 },
    { SPECIES_SEAKING,      150 },
    { SPECIES_WEEZING,      150 },
    { SPECIES_GENGAR,       150 },
    { SPECIES_ARBOK,        150 },
    { SPECIES_ARTICUNO,     150 },
    { SPECIES_MEWTWO,       150 },
    { SPECIES_BAYLEEF,      150 },
    { SPECIES_QUILAVA,      150 },
    { SPECIES_FERALIGATR,   150 },
    { SPECIES_NOCTOWL,      150 },
    { SPECIES_AMPHAROS,     150 },
    { SPECIES_HOPPIP,       150 },
    { SPECIES_JUMPLUFF,     150 },
    { SPECIES_SUNKERN,      150 },
    { SPECIES_YANMA,        150 },
    { SPECIES_SLOWKING,     150 },
    { SPECIES_QWILFISH,     150 },
    { SPECIES_SHUCKLE,      160 },
    { SPECIES_OCTILLERY,    160 },
    { SPECIES_MANTINE,      160 },
    { SPECIES_HOUNDOUR,     160 },
    { SPECIES_TYROGUE,      160 },

    // 【レア】11体
    // 物語中盤
    { SPECIES_SNEASEL,      130 },
    { SPECIES_SNUBBULL,     130 },
    { SPECIES_DUNSPARCE,    130 },
    { SPECIES_GIRAFARIG,    130 },
    { SPECIES_NATU,         130 },
    { SPECIES_CLEFFA,       130 },
    { SPECIES_CHINCHOU,     130 },
    { SPECIES_SPINARAK,     130 },
    { SPECIES_DRAGONAIR,    130 },
    { SPECIES_MOLTRES,      130 },
    { SPECIES_FLAREON,      130 },

    // 【sレア】7体
    // 物語終盤に出てくるポケモン
    { SPECIES_MILTANK,      100 },
    { SPECIES_LARVITAR,     100 },
    { SPECIES_LUGIA,        100 },
    { SPECIES_GROVYLE,      100 },
    { SPECIES_KINGDRA,      100 },
    { SPECIES_URSARING,     100 },
    { SPECIES_WINGULL,      100 },

    // 【エピック】14体
    // 異世界ポケモン
    { SPECIES_PSYDUCK,      50 },
    { SPECIES_MARILL,       50 },
    { SPECIES_UMBREON,      50 },
    { SPECIES_SMOOCHUM,     50 },
    { SPECIES_MUDKIP,       50 },
    { SPECIES_POOCHYENA,    50 }, 
    { SPECIES_LINOONE,      50 },
    { SPECIES_BEAUTIFLY,    50 },
    { SPECIES_LOTAD,        50 },
    { SPECIES_SUICUNE,      50 },
    { SPECIES_TAILLOW,      50 },
    { SPECIES_NUZLEAF,      50 },
    { SPECIES_LUDICOLO,     50 },
    { SPECIES_PILOSWINE,    50 },

    // 【激レア】8体
    // 御三家とパートナーポケモンのみ
    { SPECIES_BULBASAUR,    20 },
    { SPECIES_CHARMANDER,   20 },
    { SPECIES_SQUIRTLE,     20 },
    { SPECIES_CATERPIE,     10 },
    { SPECIES_SHEDINJA,     10 },
    { SPECIES_DELCATTY,     10 },
    { SPECIES_EXPLOUD,      10 },
    { SPECIES_AZURILL,      10 },
};

// 全グループのテーブル
static const struct EggGachaTable sGachaTables[] = {
    [EGG_TYPE_NORMAL]   = { sNormalEggEntries,    ARRAY_COUNT(sNormalEggEntries) },
    [EGG_TYPE_SPECIAL]  = { sSpecialEggEntries,   ARRAY_COUNT(sSpecialEggEntries) },
    [EGG_TYPE_RARE]     = { sRareEggEntries,      ARRAY_COUNT(sRareEggEntries) },
    [EGG_TYPE_SRARE]    = { sSuperRareEggEntries, ARRAY_COUNT(sSuperRareEggEntries) },
    [EGG_TYPE_EPIC]     = { sEpicEggEntries,      ARRAY_COUNT(sNormalEggEntries) },
    [EGG_TYPE_RANDOM]   = { sRandomEggEntries,    ARRAY_COUNT(sRandomEggEntries) },
};

const struct EggGachaEntry* RunDelibirdEggGacha(u8 groupId)
{
    u32 i;
    u16 random = (Random() % 10000) + 1; // 1〜10000の乱数
    u16 cumulative = 0;

    const struct EggGachaTable *table = &sGachaTables[groupId];

    for (i = 0; i < table->count; i++) {
        cumulative += table->entries[i].weight;
        if (random <= cumulative) {
            return &table->entries[i];
        }
    }
    return &table->entries[0]; // 万が一数字が合わなかった場合
}

void ClearDelibirdEgg(void)
{
    gSaveBlock1Ptr->delibirdEgg.stepCounter = 0;
    FlagSet(FLAG_HIDE_DELIBIRD_OUTSIDE_NPC);
}

static u16 RandomRange(u16 min, u16 max)
{
    return (Random() % (max - min + 1)) + min;
}


u8 giveDelibirdRareRankEggs(u16 delibirdEggGroupId)
{
    struct Pokemon mon;
    const struct EggGachaEntry *result = RunDelibirdEggGacha(delibirdEggGroupId);
    
    u8 eggCycles = RandomRange(2, 10);
    metloc_u8_t metLocation; 
    bool8 isShiny;
    u8 isEgg;

    // 1. ベースとなる卵を生成
    // 第三引数のフラグはセットするとMetLocationが温泉になってしまう
    CreateEgg(&mon, result->species, FALSE);

    // 2. タマゴのMet_Locationの設定
    metLocation = METLOC_DELIBIRD_SHOP;
    SetMonData(&mon, MON_DATA_MET_LOCATION, &metLocation);
    
    // 3. 既存の便利な関数を使ってIVをすべてMAXにする
    SetBoxMonIVs(&mon.box, MAX_PER_STAT_IVS);
    
    // 4. 20%の確率で色違いにする
    isShiny = (Random() % 100 < 20);
    SetMonData(&mon, MON_DATA_IS_SHINY, &isShiny);
    
    // 5. 孵化までの歩数を設定
    SetMonData(&mon, MON_DATA_FRIENDSHIP, &eggCycles);
    
    // 6. 卵フラグを念のため再設定
    isEgg = TRUE;
    SetMonData(&mon, MON_DATA_IS_EGG, &isEgg);

    // 7. プレイヤーに渡す
    return GiveCapturedMonToPlayer(&mon);
}

u8 giveDelibirdRandomEggs(u16 delibirdEggGroupId)
{
    metloc_u8_t metLocation = METLOC_DELIBIRD_OUTSIDE;
    bool8 isShiny;
    u8 isEgg = TRUE;
    u8 i;
    u8 count;

    if (delibirdEggGroupId == EGG_TYPE_RANDOM_1)
        count = 1;
    if (delibirdEggGroupId == EGG_TYPE_RANDOM_5)
        count = 5;
    if (delibirdEggGroupId == EGG_TYPE_RANDOM_25)
        count = 25;

    for (i = 0; i < count; i++)
    {
        struct Pokemon mon;
        const struct EggGachaEntry *result = RunDelibirdEggGacha(EGG_TYPE_RANDOM);
        isShiny = (Random() % 100 < 20);
        u8 eggCycles = RandomRange(5, 15);

        CreateEgg(&mon, result->species, FALSE);
        SetBoxMonIVs(&mon.box, MAX_PER_STAT_IVS);
        SetMonData(&mon, MON_DATA_IS_EGG, &isEgg);
        SetMonData(&mon, MON_DATA_IS_SHINY, &isShiny);
        SetMonData(&mon, MON_DATA_FRIENDSHIP, &eggCycles);
        SetMonData(&mon, MON_DATA_MET_LOCATION, &metLocation);
        GiveCapturedMonToPlayer(&mon);
    }
    return 0;
}

u8 giveDelibirdEgg(u16 delibirdEggGroupId)
{
    if (delibirdEggGroupId == EGG_TYPE_RANDOM_1 ||
        delibirdEggGroupId == EGG_TYPE_RANDOM_5 ||
        delibirdEggGroupId == EGG_TYPE_RANDOM_25)
    {
        return giveDelibirdRandomEggs(delibirdEggGroupId);
    } else
    {
        return giveDelibirdRareRankEggs(delibirdEggGroupId);
    }
}
