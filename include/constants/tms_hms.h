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
    F(CHILLY_RECEPTION)/* TM15: さむいギャグ */ \
    F(GRASSY_TERRAIN)  /* TM16: グラスフィールド */ \
    F(ELECTRIC_TERRAIN)/* TM17: エレキフィールド */ \
    F(PSYCHIC_TERRAIN) /* TM18: サイコフィールド */ \
    F(MISTY_TERRAIN)   /* TM19: ミストフィールド */ \
    F(REST)            /* TM20: ねむる */ \
    F(RECOVER)         /* TM21: じこさいせい */ \
    F(MORNING_SUN)     /* TM22: あさのひざし */ \
    F(SYNTHESIS)       /* TM23: こうごうせい */ \
    F(MOONLIGHT)       /* TM24: つきのひかり */ \
    F(SOFT_BOILED)     /* TM25: タマゴうみ */ \
    F(MILK_DRINK)      /* TM26: ミルクのみ */ \
    F(SLACK_OFF)       /* TM27: なまける */ \
    F(ROOST)           /* TM28: はねやすめ */ \
    F(STRENGTH_SAP)    /* TM29: ちからをすいとる */ \
    F(WISH)            /* TM30: ねがいごと */ \
    F(HEAL_BELL)       /* TM31: いやしのすず */ \
    F(AROMATHERAPY)    /* TM32: アロマセラピー */ \
    F(PAIN_SPLIT)      /* TM33: いたみわけ */ \
    F(AQUA_RING)       /* TM34: アクアリング */ \
    F(INGRAIN)         /* TM35: ねっこをはる */ \
    F(LEECH_SEED)      /* TM36: やどりぎのたね */ \
    F(SALT_CURE)       /* TM37: しおづけ */ \
    F(FIRE_SPIN)       /* TM38: ほのおのうず */ \
    F(INFESTATION)     /* TM39: まとわりつく */ \
    F(WHIRLPOOL)       /* TM40: うずしお */ \
    F(SAND_TOMB)       /* TM41: すなじごく */ \
    F(SPIKES)          /* TM42: まきびし */ \
    F(TOXIC_SPIKES)    /* TM43: どくびし */ \
    F(STEALTH_ROCK)    /* TM44: ステルスロック */ \
    F(STICKY_WEB)      /* TM45: ねばねばネット */ \
    F(ELECTROWEB)      /* TM46: エレキネット */ \
    F(CURSE)           /* TM47: のろい */ \
    F(NIGHTMARE)       /* TM48: あくむ */ \
    F(YAWN)            /* TM49: あくび */ \
    F(SPORE)           /* TM50: キノコのほうし */ \
    F(THUNDER_WAVE)    /* TM51: でんじは */ \
    F(WILL_O_WISP)     /* TM52: おにび */ \
    F(TOXIC)           /* TM53: どくどく */ \
    F(TEETER_DANCE)    /* TM54: フラフラダンス */ \
    F(ATTRACT)         /* TM55: メロメロ */ \
    F(REFLECT)         /* TM56: リフレクター */ \
    F(LIGHT_SCREEN)    /* TM57: ひかりのかべ */ \
    F(AURORA_VEIL)     /* TM58: オーロラベール */ \
    F(COUNTER)         /* TM59: カウンター */ \
    F(MIRROR_COAT)     /* TM60: ミラーコート */ \
    F(METAL_BURST)     /* TM61: メタルバースト */ \
    F(COMEUPPANCE)     /* TM62: ほうふく */ \
    F(REVENGE)         /* TM63: リベンジ */ \
    F(PROTECT)         /* TM64: まもる */ \
    F(KINGS_SHIELD)    /* TM65: キングシールド */ \
    F(BANEFUL_BUNKER)  /* TM66: トーチカ */ \
    F(SPIKY_SHIELD)    /* TM67: ニードルガード */ \
    F(SILK_TRAP)       /* TM68: スレッドトラップ */ \
    F(OBSTRUCT)        /* TM69: ブロッキング */ \
    F(TOPSY_TURVY)     /* TM70: ひっくりかえし */ \
    F(SNATCH)          /* TM71: よこどり */ \
    F(PSYCH_UP)        /* TM72: じこあんじ */ \
    F(TRICK)           /* TM73: トリック */ \
    F(SWITCHEROO)      /* TM74: すりかえ */ \
    F(PARTING_SHOT)    /* TM75: すてぜりふ */ \
    F(CLEAR_SMOG)      /* TM76: クリアスモッグ */ \
    F(SPEED_SWAP)      /* TM77: スピードスワップ */ \
    F(GUARD_SPLIT)     /* TM78: ガードシェア */ \
    F(POWER_SPLIT)     /* TM79: パワーシェア */ \
    F(SPECTRAL_THIEF)  /* TM80: シャドースチール */ \
    F(DEFOG)           /* TM81: きりばらい */ \
    F(COURT_CHANGE)    /* TM82: コートチェンジ */ \
    F(TIDY_UP)         /* TM83: おかたづけ */ \
    F(HAZE)            /* TM84: くろいきり */ \
    F(MIST)            /* TM85: しろいきり */ \
    F(SAFEGUARD)       /* TM86: しんぴのまもり */ \
    F(TAILWIND)        /* TM87: おいかぜ */ \
    F(TRICK_ROOM)      /* TM88: トリックルーム */ \
    F(WONDER_ROOM)     /* TM89: ワンダールーム */ \
    F(MAGIC_ROOM)      /* TM90: マジックルーム */ \
    F(MEAN_LOOK)       /* TM91: くろいまなざし */ \
    F(BLOCK)           /* TM92: とうせんぼう */ \
    F(SPIDER_WEB)      /* TM93: クモのす */ \
    F(SPIRIT_SHACKLE)  /* TM94: かげぬい */ \
    F(ROAR)            /* TM95: ほえる */ \
    F(WHIRLWIND)       /* TM96: ふきとばし */ \
    F(SOAK)            /* TM97: みずびたし */ \
    F(MAGIC_POWDER)    /* TM98: まほうのこな */ \
    F(TRICK_OR_TREAT)  /* TM99: ハロウィン */ \
    F(FORESTS_CURSE)   /* TM100: もりののろい */ \
    F(SKILL_SWAP)      /* TM101: スキルスワップ */ \
    F(WORRY_SEED)      /* TM102: なやみのタネ */ \
    F(GASTRO_ACID)     /* TM103: いえき */ \
    F(SIMPLE_BEAM)     /* TM104: シンプルビーム */ \
    F(ENTRAINMENT)     /* TM105: なかまずくり */ \
    F(SPLASH)          /* TM106: はねる */ \
    F(DOUBLE_TEAM)     /* TM107: かげぶんしん */ \
    F(MINIMIZE)        /* TM108: ちいさくなる */ \
    F(GROWTH)          /* TM109: せいちょう */ \
    F(WORK_UP)         /* TM110: ふるいたてる */ \
    F(FAKE_TEARS)      /* TM111: うそなき */ \
    F(HONE_CLAWS)      /* TM112: つめとぎ */ \
    F(COVET)           /* TM113: ほしがる */ \
    F(MIND_READER)     /* TM114: こころのめ */ \
    F(LOCK_ON)         /* TM115: ロックオン */ \
    F(SHARPEN)         /* TM116: みがく */ \
    F(CALM_MIND)       /* TM117: めいそう */ \
    F(SHELL_SMASH)     /* TM118: からやぶる */ \
    F(BELLY_DRUM)      /* TM119: はらだいこ */ \
    F(FILLET_AWAY)     /* TM120: みをけずる */ \
    F(TICKLE)          /* TM121: くすぐる */ \
    F(THIEF)           /* TM122: どろぼう */ \
    F(KNOCK_OFF)       /* TM123: はたきおとす */ \
    F(SNORE)           /* TM124: いびき */ \
    F(LICK)            /* TM125: したでなめる */ \
    F(BULK_UP)         /* TM126: ビルドアップ */ \
    F(NUZZLE)          /* TM127: ほっぺスリスリ */ \
    F(LOVELY_KISS)     /* TM128: あくまのキッス */ \
    F(SWEET_KISS)      /* TM129: てんしのキッス */ \
    F(DRAINING_KISS)   /* TM130: ドレインキッス */ \
    F(U_TURN)          /* TM131: とんぼがえり */ \
    F(VOLT_SWITCH)     /* TM132: ボルトチェンジ */ \
    F(FLIP_TURN)       /* TM133: クイックターン */ \
    F(MACH_PUNCH)      /* TM134: マッハパンチ */ \
    F(POWER_UP_PUNCH)  /* TM135: パワーアップパンチ */ \
    F(NEEDLE_ARM)      /* TM136: ニードルアーム */ \
    F(FIRE_PUNCH)      /* TM137: ほのおのパンチ */ \
    F(JET_PUNCH)       /* TM138: ジェットパンチ */ \
    F(THUNDER_PUNCH)   /* TM139: かみなりパンチ */ \
    F(ICE_PUNCH)       /* TM140: れいとうパンチ */ \
    F(SHADOW_PUNCH)    /* TM141: シャドーパンチ */ \
    F(SKY_UPPERCUT)    /* TM142: スカイアッパー */ \
    F(DRAIN_PUNCH)     /* TM143: ドレインパンチ */ \
    F(RAGE_FIST)       /* TM144: ふんどのこぶし */ \
    F(COMET_PUNCH)     /* TM145: れんぞくパンチ */ \
    F(SURGING_STRIKES) /* TM146: すいりゅうれんだ */ \
    F(MISTY_FOG)       /* TM147: ふしぎなきり */ \
    F(SING)            /* TM147: うたう */




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
