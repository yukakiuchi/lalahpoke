@ ==========================================
@ ポケモンタクシー スクリプト（現在地除外バグ修正版）
@ ==========================================
EventScript_PokemonTaxiNPC::
	lock
	faceplayer
	msgbox Text_PokemonTaxi_Intro, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, EventScript_PokemonTaxi_Cancel

	@ トウカシティ未訪問（冒険序盤）ならまだ利用不可
	goto_if_unset FLAG_VISITED_PETALBURG_CITY, EventScript_PokemonTaxi_NoTowns

	@ 現在地のマップ番号を取得 (VAR_TEMP_2 に格納される)
	callnative GetCurrentMapScript

	@ 訪問カウンターのリセット
	setvar VAR_TEMP_1, 0

	@ 訪れたことがある街＆「現在地以外」の場所を選択肢に追加
	call_if_set FLAG_VISITED_OLDALE_TOWN, EventScript_PokemonTaxi_AddOldale
	call_if_set FLAG_VISITED_PETALBURG_CITY, EventScript_PokemonTaxi_AddPetalburg
	call_if_set FLAG_VISITED_PETALBURG_CITY, EventScript_PokemonTaxi_AddRoute104
	call_if_set FLAG_VISITED_RUSTBORO_CITY, EventScript_PokemonTaxi_AddRustboro

	@ 移動できる場所が1つもない場合
	goto_if_eq VAR_TEMP_1, 0, EventScript_PokemonTaxi_NoTowns

	msgbox Text_PokemonTaxi_Where, MSGBOX_DEFAULT
	
	@ 選択肢メニューを表示
	dynmultistack 0, 0, FALSE, 4, FALSE, 0, NULL

	goto_if_eq VAR_RESULT, 0, EventScript_PokemonTaxi_Oldale
	goto_if_eq VAR_RESULT, 1, EventScript_PokemonTaxi_Petalburg
	goto_if_eq VAR_RESULT, 2, EventScript_PokemonTaxi_Route104
	goto_if_eq VAR_RESULT, 3, EventScript_PokemonTaxi_Rustboro
	goto EventScript_PokemonTaxi_Cancel
	end

@ --- 選択肢追加用（VAR_TEMP_2 と一致する場合は追加しない） ---
EventScript_PokemonTaxi_AddOldale::
	goto_if_eq VAR_TEMP_2, MAP_OLDALE_TOWN, EventScript_TaxiReturn
	dynmultipush Text_Oldale, 0
	addvar VAR_TEMP_1, 1
	return

EventScript_PokemonTaxi_AddPetalburg::
	goto_if_eq VAR_TEMP_2, MAP_PETALBURG_CITY, EventScript_TaxiReturn
	dynmultipush Text_Petalburg, 1
	addvar VAR_TEMP_1, 1
	return

EventScript_PokemonTaxi_AddRoute104::
	goto_if_eq VAR_TEMP_2, MAP_ROUTE104, EventScript_TaxiReturn
	dynmultipush Text_Route104, 2
	addvar VAR_TEMP_1, 1
	return

EventScript_PokemonTaxi_AddRustboro::
	goto_if_eq VAR_TEMP_2, MAP_RUSTBORO_CITY, EventScript_TaxiReturn
	dynmultipush Text_Rustboro, 3
	addvar VAR_TEMP_1, 1
	return

EventScript_TaxiReturn::
	return

@ --- 飛ぶ演出 ---
EventScript_PokemonTaxi_FlySequence::
	msgbox Text_PokemonTaxi_Depart, MSGBOX_DEFAULT
	closemessage
	playmoncry SPECIES_PIDGEOT, CRY_MODE_NORMAL
	waitmoncry
	fadescreen FADE_TO_BLACK
	playse SE_M_FLY
	waitse
	return

@ --- 各街・道路への移動 ---
EventScript_PokemonTaxi_Oldale::
	call EventScript_PokemonTaxi_FlySequence
	setvar VAR_0x8004, MAP_OLDALE_TOWN
	setvar VAR_0x8005, 10
	setvar VAR_0x8006, 9
	callnative DoPokemonTaxiWarp
	waitstate
	end

EventScript_PokemonTaxi_Petalburg::
	call EventScript_PokemonTaxi_FlySequence
	setvar VAR_0x8004, MAP_PETALBURG_CITY
	setvar VAR_0x8005, 20
	setvar VAR_0x8006, 17
	callnative DoPokemonTaxiWarp
	waitstate
	end

EventScript_PokemonTaxi_Route104::
	call EventScript_PokemonTaxi_FlySequence
	setvar VAR_0x8004, MAP_ROUTE104
	setvar VAR_0x8005, 21
	setvar VAR_0x8006, 48
	callnative DoPokemonTaxiWarp
	waitstate
	end

EventScript_PokemonTaxi_Rustboro::
	call EventScript_PokemonTaxi_FlySequence
	setvar VAR_0x8004, MAP_RUSTBORO_CITY
	setvar VAR_0x8005, 16
	setvar VAR_0x8006, 28
	callnative DoPokemonTaxiWarp
	waitstate
	end

@ --- キャンセル・エラー時 ---
EventScript_PokemonTaxi_NoTowns::
	msgbox Text_PokemonTaxi_NoTownsYet, MSGBOX_DEFAULT
	release
	end

EventScript_PokemonTaxi_Cancel::
	msgbox Text_PokemonTaxi_Cancel, MSGBOX_DEFAULT
	release
	end

@ --- テキストデータ ---
Text_PokemonTaxi_Intro:
	.string "My Pidgeot can carry you to any\n"
	.string "town you've visited before!\p"
	.string "Would you like a ride?$"

Text_PokemonTaxi_Where:
	.string "Where would you like to go?$"

Text_PokemonTaxi_NoTownsYet:
	.string "Hummm it looks like you've only\n"
	.string "just started your journey!\p"
	.string "Come back once you've explored\n"
	.string "a bit more!$"

Text_PokemonTaxi_Depart:
	.string "Alright, hold tight!\n"
	.string "Here we go!$"

Text_PokemonTaxi_Cancel:
	.string "Alright. Let me know if you\n"
	.string "change your mind!$"

Text_Oldale:
	.string "Oldale Town$"

Text_Petalburg:
	.string "Petalburg City$"

Text_Route104:
	.string "Route 104$"

Text_Rustboro:
	.string "Rustboro City$"


@ ==========================================
@ ピジョットの鳴き声 スクリプト
@ ==========================================
EventScript_PidgeotCry::
	lock
	faceplayer
	playmoncry SPECIES_PIDGEOT, CRY_MODE_NORMAL
	msgbox Text_PidgeotCry, MSGBOX_DEFAULT
	waitmoncry
	release
	end

Text_PidgeotCry:
	.string "Pidgeot: Shaaoooh!$"
