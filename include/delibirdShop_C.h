#ifndef GUARD_DELIBIRDSHOP_C_H
#define GUARD_DELIBIRDSHOP_C_H

#define EGG_TYPE_NORMAL      0
#define EGG_TYPE_SPECIAL     1
#define EGG_TYPE_RARE        2
#define EGG_TYPE_SRARE       3
#define EGG_TYPE_EPIC        4
#define EGG_TYPE_RANDOM      5
#define EGG_TYPE_RANDOM_1    6
#define EGG_TYPE_RANDOM_5    7
#define EGG_TYPE_RANDOM_25   8
#define DELIBIRDSHOP_OUTSIDE_ENCOUNT_STEPS   1
#define DELIBIRDSHOP_OUTSIDE_DISSAPEAR_STEPS 10000


struct EggGachaEntry {
    u16 species;    // ポケモンの種類
    u16 weight;     // 当選確率
};


struct EggGachaTable {
    const struct EggGachaEntry *entries;
    u8 count;
};

void ClearDelibirdEgg(void);
u8 giveDelibirdEgg(u16 delibirdEggGroupId);

#endif //GUARD_DELIBIRDSHOP_C_H
