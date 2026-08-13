RustboroCity_Gym_MapScripts::
	.byte 0

RustboroCity_Gym_EventScript_Roxanne::
	trainerbattle_single TRAINER_ROXANNE_1, RustboroCity_Gym_Text_RoxanneIntro, RustboroCity_Gym_Text_RoxanneDefeat, RustboroCity_Gym_EventScript_RoxanneDefeated, NO_MUSIC
	specialvar VAR_RESULT, ShouldTryRematchBattle
	goto_if_eq VAR_RESULT, TRUE, RustboroCity_Gym_EventScript_RoxanneRematch
	msgbox RustboroCity_Gym_Text_RoxannePostBattle, MSGBOX_DEFAULT
	release
	end

RustboroCity_Gym_EventScript_RoxanneDefeated::
	message RustboroCity_Gym_Text_ReceivedStoneBadge
	waitmessage
	call Common_EventScript_PlayGymBadgeFanfare
	msgbox RustboroCity_Gym_Text_StoneBadgeInfoTakeThis, MSGBOX_DEFAULT
	setflag FLAG_DEFEATED_RUSTBORO_GYM
	setflag FLAG_BADGE01_GET
	setvar VAR_RUSTBORO_CITY_STATE, 1
	addvar VAR_PETALBURG_GYM_STATE, 1
	setvar VAR_0x8008, 1
	call Common_EventScript_SetGymTrainers
	call_if_eq VAR_PETALBURG_GYM_STATE, 6, Common_EventScript_ReadyPetalburgGymForBattle
	@ TM受取処理を削除し、指定のエンディング会話を表示してレベルキャップを50に解放
	msgbox RustboroCity_Gym_Text_RoxanneDemoEnding, MSGBOX_DEFAULT
	setvar VAR_LEVEL_CAP, 50
	release
	end

RustboroCity_Gym_EventScript_RoxanneRematch::
	trainerbattle_rematch_double TRAINER_ROXANNE_1, RustboroCity_Gym_Text_RoxannePreRematch, RustboroCity_Gym_Text_RoxanneRematchDefeat, RustboroCity_Gym_Text_RoxanneRematchNeedTwoMons
	msgbox RustboroCity_Gym_Text_RoxannePostRematch, MSGBOX_AUTOCLOSE
	end

RustboroCity_Gym_EventScript_Josh::
	trainerbattle_single TRAINER_JOSH, RustboroCity_Gym_Text_JoshIntro, RustboroCity_Gym_Text_JoshDefeat
	msgbox RustboroCity_Gym_Text_JoshPostBattle, MSGBOX_AUTOCLOSE
	end

RustboroCity_Gym_EventScript_Tommy::
	trainerbattle_single TRAINER_TOMMY, RustboroCity_Gym_Text_TommyIntro, RustboroCity_Gym_Text_TommyDefeat
	msgbox RustboroCity_Gym_Text_TommyPostBattle, MSGBOX_AUTOCLOSE
	end

RustboroCity_Gym_EventScript_Marc::
	trainerbattle_single TRAINER_MARC, RustboroCity_Gym_Text_MarcIntro, RustboroCity_Gym_Text_MarcDefeat
	msgbox RustboroCity_Gym_Text_MarcPostBattle, MSGBOX_AUTOCLOSE
	end

RustboroCity_Gym_EventScript_GymGuide::
	lock
	faceplayer
	goto_if_set FLAG_DEFEATED_RUSTBORO_GYM, RustboroCity_Gym_EventScript_GymGuidePostVictory
	msgbox RustboroCity_Gym_Text_GymGuideAdvice1, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, RustboroCity_Gym_EventScript_GymGuideNo
	msgbox RustboroCity_Gym_Text_GymGuideAdvice2, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, RustboroCity_Gym_EventScript_GymGuideNo
	msgbox RustboroCity_Gym_Text_GymGuideAdvice3, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, RustboroCity_Gym_EventScript_GymGuideNo
	msgbox RustboroCity_Gym_Text_GymGuideAnswer, MSGBOX_DEFAULT
	release
	end

RustboroCity_Gym_EventScript_GymGuideNo::
	msgbox RustboroCity_Gym_Text_GymGuideNoAnswer, MSGBOX_DEFAULT
	release
	end

RustboroCity_Gym_EventScript_GymGuidePostVictory::
	msgbox RustboroCity_Gym_Text_GymGuidePostVictory, MSGBOX_DEFAULT
	release
	end

RustboroCity_Gym_EventScript_LeftGymStatue::
	lockall
	goto_if_set FLAG_BADGE01_GET, RustboroCity_Gym_EventScript_GymStatueCertified
	goto RustboroCity_Gym_EventScript_GymStatue
	end

RustboroCity_Gym_EventScript_RightGymStatue::
	lockall
	goto_if_set FLAG_BADGE01_GET, RustboroCity_Gym_EventScript_GymStatueCertified
	goto RustboroCity_Gym_EventScript_GymStatue
	end

RustboroCity_Gym_EventScript_GymStatueCertified::
	msgbox RustboroCity_Gym_Text_GymStatueCertified, MSGBOX_DEFAULT
	releaseall
	end

RustboroCity_Gym_EventScript_GymStatue::
	msgbox RustboroCity_Gym_Text_GymStatue, MSGBOX_DEFAULT
	releaseall
	end

RustboroCity_Gym_EventScript_RegisterRoxanne::
	lockall
	pokenavcall RustboroCity_Gym_Text_RoxanneRegisterCall
	waitmessage
	delay 30
	playfanfare MUS_REGISTER_MATCH_CALL
	msgbox RustboroCity_Gym_Text_RegisteredRoxanne, MSGBOX_DEFAULT
	waitfanfare
	closemessage
	delay 30
	setflag FLAG_ENABLE_ROXANNE_MATCH_CALL
	clearflag FLAG_ENABLE_ROXANNE_FIRST_CALL
	releaseall
	end

RustboroCity_Gym_Text_GymGuideAdvice1::
	.string "Can't beat the Gym Leader?\n"
	.string "Sure, they're tough, but many\p"
	.string "POKéMON can use various tricks\n"
	.string "now, so try different things!\p"
	.string "Do you want me to tell you\n"
	.string "the answer?$"

RustboroCity_Gym_Text_GymGuideAdvice2::
	.string "Are you really sure?$"

RustboroCity_Gym_Text_GymGuideAdvice3::
	.string "Alright, here it comes!\n"
	.string "3, 2, 1... Ready?$"

RustboroCity_Gym_Text_GymGuideAnswer::
	.string "Give a Choice Band to Shiinotic\n"
	.string "and you can sweep the enemy!\p"
	.string "Its Parasite Ability can inflict\n"
	.string "Parasite when using Leech Seed.\p"
	.string "When triggered, it KOs the foe\n"
	.string "and heals your HP! It's a\p"
	.string "super powerful Ability.\p"
	.string "Grass types are immune, and\n"
	.string "Bleed can counter it too.\p"
	.string "However, the Gym Leader has no\n"
	.string "Bleed moves on purpose.\p"
	.string "It's an intentional loophole!\n"
	.string "Now then, good luck!$"

RustboroCity_Gym_Text_GymGuideNoAnswer::
	.string "That's the spirit! I love your\n"
	.string "determination.\p"
	.string "Right now is the most exciting\n"
	.string "part of the journey!\p"
	.string "Give it your absolute best!$"

RustboroCity_Gym_Text_GymGuidePostVictory::
	.string "Whoa! What a breathtaking victory!\n"
	.string "My cheering must've worked!\p"
	.string "Great!\n"
	.string "Check your TRAINER CARD.\p"
	.string "The STONE BADGE you got should be\n"
	.string "properly recorded on it.\p"
	.string "In other words...\p"
	.string "You've climbed the first step on\n"
	.string "the stairs to the CHAMPIONSHIP!\p"
	.string "That's got to feel awesome!$"

RustboroCity_Gym_Text_JoshIntro::
	.string "Don't take us GYM TRAINERS lightly!\n"
	.string "I'll show you why we're better!$"

RustboroCity_Gym_Text_JoshDefeat::
	.string "You were too good for me...$"

RustboroCity_Gym_Text_JoshPostBattle::
	.string "You haven't seen anything of the ROCK\n"
	.string "type's terrifying power!$"

RustboroCity_Gym_Text_TommyIntro::
	.string "If you can't beat me, you won't stand\n"
	.string "a chance against ROXANNE!$"

RustboroCity_Gym_Text_TommyDefeat::
	.string "Wow! You've got some potential!$"

RustboroCity_Gym_Text_TommyPostBattle::
	.string "ROXANNE is stronger than me by\n"
	.string "several times.\p"
	.string "You'd better be on your guard!$"

RustboroCity_Gym_Text_MarcIntro::
	.string "We might be in the middle of town,\n"
	.string "but so what?\p"
	.string "My ROCK POKéMON need room to\n"
	.string "rampage!$"

RustboroCity_Gym_Text_MarcDefeat::
	.string "Oh, man oh man!\n"
	.string "Our challenger is one feisty customer!$"

RustboroCity_Gym_Text_MarcPostBattle::
	.string "I have to hand it to our LEADER.\p"
	.string "It took smarts and sense for her to\n"
	.string "pick the ROCK type at her young age.$"

@ 初回対戦前のセリフ（Demo最終戦テキストへ置き換え）
RustboroCity_Gym_Text_RoxanneIntro::
	.string "This is the last serious battle\n"
	.string "in this Demo version.\p"
	.string "Don't you think it was much tougher\n"
	.string "and more challenging than the main game?\p"
	.string "But once you figure out how it works,\n"
	.string "it becomes very easy--that's the charm!\p"
	.string "Mindlessly leveling up to brute-force\n"
	.string "your way through is for the main game.\p"
	.string "Now, fully savor my beloved\n"
	.string "Purple Team!$"

RustboroCity_Gym_Text_RoxanneDefeat::
	.string "So...\n"
	.string "I lost...\p"
	.string "It seems that I still have much more\n"
	.string "to learn...\p"
	.string "I understand.\p"
	.string "The POKéMON LEAGUE's rules state\n"
	.string "that TRAINERS are to be given this\l"
	.string "if they defeat a GYM LEADER.\p"
	.string "Please accept the official POKéMON\n"
	.string "LEAGUE STONE BADGE.$"

RustboroCity_Gym_Text_ReceivedStoneBadge::
	.string "{PLAYER} received the STONE BADGE\n"
	.string "from ROXANNE.$"

RustboroCity_Gym_Text_StoneBadgeInfoTakeThis::
	.string "The STONE BADGE heightens the ATTACK\n"
	.string "power of your POKéMON.\p"
	.string "It also enables them to use the HM move\n"
	.string "CUT outside of battle.$"

@ バトル勝利後のフィールドでの会話セリフ
RustboroCity_Gym_Text_RoxanneDemoEnding::
	.string "That was a fantastic battle, truly\n"
	.string "worthy of being the finale!\p"
	.string "I'm so glad you played this far.\n"
	.string "You are a truly wonderful POKéMON TRAINER!\p"
	.string "If you enjoyed this game, I'll do my\n"
	.string "best to release a sequel.\p"
	.string "Now then, I'll raise the level cap to 50!\p"
	.string "All available POKéMON can now reach\n"
	.string "their final evolution stage!\p"
	.string "Please enjoy it as post-game content!$"

@ クリア後に再度話しかけた際のセリフ
RustboroCity_Gym_Text_RoxannePostBattle::
	.string "I've raised the level cap to 50!\p"
	.string "All available POKéMON can now reach\n"
	.string "their final evolution stage!\p"
	.string "Please enjoy it as post-game content!$"

RustboroCity_Gym_Text_GymStatue::
	.string "RUSTBORO CITY POKéMON GYM$"

RustboroCity_Gym_Text_GymStatueCertified::
	.string "RUSTBORO CITY POKéMON GYM\p"
	.string "ROXANNE'S CERTIFIED TRAINERS:\n"
	.string "{PLAYER}$"

RustboroCity_Gym_Text_RoxanneRegisterCall::
	.string "... ... ... ... ... ...\n"
	.string "... ... ... ... ... Beep!\p"
	.string "ROXANNE: Oh, hello, {PLAYER}?\n"
	.string "This is ROXANNE of RUSTBORO CITY.\p"
	.string "I heard from BRAWLY that you're\n"
	.string "moving up through the ranks of\l"
	.string "TRAINERS at an incredible clip.\p"
	.string "Well, I'd rather not think that\n"
	.string "I can't beat you.\p"
	.string "I promise, I will shape up my GYM\n"
	.string "so that you may challenge us again.\p"
	.string "I hope you'll be looking forward to\n"
	.string "that occasion as much as me!\p"
	.string "... ... ... ... ... ...\n"
	.string "... ... ... ... ... Click!$"

RustboroCity_Gym_Text_RegisteredRoxanne::
	.string "Registered GYM LEADER ROXANNE\n"
	.string "in the POKéNAV.$"

RustboroCity_Gym_Text_RoxannePreRematch::
	.string "ROXANNE: I'm so glad to see you again.\n"
	.string "I'm ROXANNE, the GYM LEADER here.\p"
	.string "I'm sure we've both experienced many\n"
	.string "battles since we last met.\p"
	.string "I would like to see how much better\n"
	.string "we've become. Let us battle!$"

RustboroCity_Gym_Text_RoxanneRematchDefeat::
	.string "Grr...\n"
	.string "Again, I have lost...$"

RustboroCity_Gym_Text_RoxannePostRematch::
	.string "ROXANNE: I still have much to learn\n"
	.string "when it comes to battling POKéMON.\p"
	.string "That awareness makes me love battling\n"
	.string "all that much more!$"

RustboroCity_Gym_Text_RoxanneRematchNeedTwoMons::
	.string "ROXANNE: I'm so glad to see you again.\n"
	.string "I'm ROXANNE, the GYM LEADER here.\p"
	.string "I'm sure we've both experienced many\n"
	.string "battles since we last met.\p"
	.string "I would like to see how much better\n"
	.string "we've become...\p"
	.string "Oh, no...\n"
	.string "You only have one POKéMON with you?\p"
	.string "Please return with at least one more\n"
	.string "POKéMON.$"