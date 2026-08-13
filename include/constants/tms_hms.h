#ifndef GUARD_CONSTANTS_TMS_HMS_H
#define GUARD_CONSTANTS_TMS_HMS_H

#define FOREACH_TM(F) \
    F(ENCORE)          /* TM01: アンコール */ \
    F(TAUNT)           /* TM02: ちょうはつ */ \
    F(SUBSTITUTE)      /* TM03: みがわり */ \
    F(SHED_TAIL)       /* TM04: しっぽぎり */ \
    F(BATON_PASS)      /* TM05: バトンタッチ */ \
    F(DISABLE)         /* TM06: かなしばり */ \
    F(THROAT_CHOP)     /* TM07: じごくづき */ \
    F(IMPRISON)        /* TM08: ふういん */ \
    F(DESTINY_BOND)    /* TM09: みちづれ */ \
    F(PERISH_SONG)     /* TM10: ほろびのうた */ \
    F(SUNNY_DAY)       /* TM11: にほんばれ */ \
    F(RAIN_DANCE)      /* TM12: あまごい */ \
    F(SANDSTORM)       /* TM13: すなあらし */ \
    F(HAIL)            /* TM14: あられ */ \
    F(MISTY_FOG)       /* TM15: ふしぎなきり */ \
    F(CHILLY_RECEPTION)/* TM16: さむいギャグ */ \
    F(GRASSY_TERRAIN)  /* TM17: グラスフィールド */ \
    F(ELECTRIC_TERRAIN)/* TM18: エレキフィールド */ \
    F(PSYCHIC_TERRAIN) /* TM19: サイコフィールド */ \
    F(MISTY_TERRAIN)   /* TM20: ミストフィールド */ \
    F(REST)            /* TM21: ねむる */ \
    F(RECOVER)         /* TM22: じこさいせい */ \
    F(MORNING_SUN)     /* TM23: あさのひざし */ \
    F(SYNTHESIS)       /* TM24: こうごうせい */ \
    F(MOONLIGHT)       /* TM25: つきのひかり */ \
    F(SOFT_BOILED)     /* TM26: タマゴうみ */ \
    F(MILK_DRINK)      /* TM27: ミルクのみ */ \
    F(SLACK_OFF)       /* TM28: なまける */ \
    F(ROOST)           /* TM29: はねやすめ */ \
    F(STRENGTH_SAP)    /* TM30: ちからをすいとる */ \
    F(WISH)            /* TM31: ねがいごと */ \
    F(HEAL_BELL)       /* TM32: いやしのすず */ \
    F(AROMATHERAPY)    /* TM33: アロマセラピー */ \
    F(PAIN_SPLIT)      /* TM34: いたみわけ */ \
    F(AQUA_RING)       /* TM35: アクアリング */ \
    F(INGRAIN)         /* TM36: ねっこをはる */ \
    F(LEECH_SEED)      /* TM37: やどりぎのたね */ \
    F(SALT_CURE)       /* TM38: しおづけ */ \
    F(FIRE_SPIN)       /* TM39: ほのおのうず */ \
    F(INFESTATION)     /* TM40: まとわりつく */ \
    F(WHIRLPOOL)       /* TM41: うずしお */ \
    F(SAND_TOMB)       /* TM42: すなじごく */ \
    F(SPIKES)          /* TM43: まきびし */ \
    F(TOXIC_SPIKES)    /* TM44: どくびし */ \
    F(STEALTH_ROCK)    /* TM45: ステルスロック */ \
    F(STICKY_WEB)      /* TM46: ねばねばネット */ \
    F(ELECTROWEB)      /* TM47: エレキネット */ \
    F(CURSE)           /* TM48: のろい */ \
    F(NIGHTMARE)       /* TM49: あくむ */ \
    F(YAWN)            /* TM50: あくび */ \
    F(SPORE)           /* TM51: キノコのほうし */ \
    F(THUNDER_WAVE)    /* TM52: でんじは */ \
    F(WILL_O_WISP)     /* TM53: おにび */ \
    F(TOXIC)           /* TM54: どくどく */ \
    F(TEETER_DANCE)    /* TM55: フラフラダンス */ \
    F(ATTRACT)         /* TM56: メロメロ */ \
    F(SING)            /* TM57: うたう */ \
    F(REFLECT)         /* TM58: リフレクター */ \
    F(LIGHT_SCREEN)    /* TM59: ひかりのかべ */ \
    F(AURORA_VEIL)     /* TM60: オーロラベール */ \
    F(COUNTER)         /* TM61: カウンター */ \
    F(MIRROR_COAT)     /* TM62: ミラーコート */ \
    F(METAL_BURST)     /* TM63: メタルバースト */ \
    F(COMEUPPANCE)     /* TM64: ほうふく */ \
    F(REVENGE)         /* TM65: リベンジ */ \
    F(PROTECT)         /* TM66: まもる */ \
    F(KINGS_SHIELD)    /* TM67: キングシールド */ \
    F(BANEFUL_BUNKER)  /* TM68: トーチカ */ \
    F(SPIKY_SHIELD)    /* TM69: ニードルガード */ \
    F(SILK_TRAP)       /* TM70: スレッドトラップ */ \
    F(OBSTRUCT)        /* TM71: ブロッキング */ \
    F(TOPSY_TURVY)     /* TM72: ひっくりかえし */ \
    F(SNATCH)          /* TM73: よこどり */ \
    F(PSYCH_UP)        /* TM74: じこあんじ */ \
    F(TRICK)           /* TM75: トリック */ \
    F(SWITCHEROO)      /* TM76: すりかえ */ \
    F(PARTING_SHOT)    /* TM77: すてぜりふ */ \
    F(CLEAR_SMOG)      /* TM78: クリアスモッグ */ \
    F(SPEED_SWAP)      /* TM79: スピードスワップ */ \
    F(GUARD_SPLIT)     /* TM80: ガードシェア */ \
    F(POWER_SPLIT)     /* TM81: パワーシェア */ \
    F(SPECTRAL_THIEF)  /* TM82: シャドースチール */ \
    F(DEFOG)           /* TM83: きりばらい */ \
    F(COURT_CHANGE)    /* TM84: コートチェンジ */ \
    F(TIDY_UP)         /* TM85: おかたづけ */ \
    F(HAZE)            /* TM86: くろいきり */ \
    F(MIST)            /* TM87: しろいきり */ \
    F(SAFEGUARD)       /* TM88: しんぴのまもり */ \
    F(TAILWIND)        /* TM89: おいかぜ */ \
    F(TRICK_ROOM)      /* TM90: トリックルーム */ \
    F(WONDER_ROOM)     /* TM91: ワンダールーム */ \
    F(MAGIC_ROOM)      /* TM92: マジックルーム */ \
    F(MEAN_LOOK)       /* TM93: くろいまなざし */ \
    F(BLOCK)           /* TM94: とうせんぼう */ \
    F(SPIDER_WEB)      /* TM95: クモのす */ \
    F(SPIRIT_SHACKLE)  /* TM96: かげぬい */ \
    F(ROAR)            /* TM97: ほえる */ \
    F(WHIRLWIND)       /* TM98: ふきとばし */ \
    F(SOAK)            /* TM99: みずびたし */ \
    F(MAGIC_POWDER)    /* TM100: まほうのこな */ \
    F(TRICK_OR_TREAT)  /* TM101: ハロウィン */ \
    F(FORESTS_CURSE)   /* TM102: もりののろい */ \
    F(SKILL_SWAP)      /* TM103: スキルスワップ */ \
    F(WORRY_SEED)      /* TM104: なやみのタネ */ \
    F(GASTRO_ACID)     /* TM105: いえき */ \
    F(SIMPLE_BEAM)     /* TM106: シンプルビーム */ \
    F(ENTRAINMENT)     /* TM107: なかまずくり */ \
    F(SPLASH)          /* TM108: はねる */ \
    F(DOUBLE_TEAM)     /* TM109: かげぶんしん */ \
    F(MINIMIZE)        /* TM110: ちいさくなる */ \
    F(GROWTH)          /* TM111: せいちょう */ \
    F(WORK_UP)         /* TM112: ふるいたてる */ \
    F(FAKE_TEARS)      /* TM113: うそなき */ \
    F(HONE_CLAWS)      /* TM114: つめとぎ */ \
    F(COVET)           /* TM115: ほしがる */ \
    F(MIND_READER)     /* TM116: こころのめ */ \
    F(LOCK_ON)         /* TM117: ロックオン */ \
    F(SHARPEN)         /* TM118: みがく */ \
    F(CALM_MIND)       /* TM119: めいそう */ \
    F(SHELL_SMASH)     /* TM120: からやぶる */ \
    F(BELLY_DRUM)      /* TM121: はらだいこ */ \
    F(FILLET_AWAY)     /* TM122: みをけずる */ \
    F(TICKLE)          /* TM123: くすぐる */ \
    F(THIEF)           /* TM124: どろぼう */ \
    F(KNOCK_OFF)       /* TM125: はたきおとす */ \
    F(SNORE)           /* TM126: いびき */ \
    F(LICK)            /* TM127: したでなめる */ \
    F(BULK_UP)         /* TM128: ビルドアップ */ \
    F(NUZZLE)          /* TM129: ほっぺスリスリ */ \
    F(LOVELY_KISS)     /* TM130: あくまのキッス */ \
    F(SWEET_KISS)      /* TM131: てんしのキッス */ \
    F(DRAINING_KISS)   /* TM132: ドレインキッス */ \
    F(U_TURN)          /* TM133: とんぼがえり */ \
    F(VOLT_SWITCH)     /* TM134: ボルトチェンジ */ \
    F(FLIP_TURN)       /* TM135: クイックターン */ \
    F(MACH_PUNCH)      /* TM136: マッハパンチ */ \
    F(POWER_UP_PUNCH)  /* TM137: パワーアップパンチ */ \
    F(NEEDLE_ARM)      /* TM138: ニードルアーム */ \
    F(FIRE_PUNCH)      /* TM139: ほのおのパンチ */ \
    F(JET_PUNCH)       /* TM140: ジェットパンチ */ \
    F(THUNDER_PUNCH)   /* TM141: かみなりパンチ */ \
    F(ICE_PUNCH)       /* TM142: れいとうパンチ */ \
    F(SHADOW_PUNCH)    /* TM143: シャドーパンチ */ \
    F(SKY_UPPERCUT)    /* TM144: スカイアッパー */ \
    F(DRAIN_PUNCH)     /* TM145: ドレインパンチ */ \
    F(RAGE_FIST)       /* TM146: ふんどのこぶし */ \
    F(COMET_PUNCH)     /* TM147: れんぞくパンチ */ \
    F(SURGING_STRIKES) /* TM148: すいりゅうれんだ */

#define FOREACH_HM(F) \
    F(CUT) \
    F(FLY) \
    F(SURF) \
    F(STRENGTH) \
    F(FLASH) \
    F(ROCK_SMASH) \
    F(WATERFALL) \
    F(DIVE)

#define FOREACH_TMHM(F) \
    FOREACH_TM(F) \
    FOREACH_HM(F)

#endif
