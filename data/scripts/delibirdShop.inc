@ ------------------- 店内購入時の処理 -------------------- @
EventScript_DelibirdShop::
	lock
	faceplayer

	@ ショップ開始あいさつ
	playmoncry SPECIES_DELIBIRD, CRY_MODE_NORMAL
	showmoneybox 0, 0, 0
	msgbox Text_Delibird_Hello, MSGBOX_DEFAULT
	waitmoncry

@ ------------------ メニューを表示 ---------------------- @
DelibirdShop_MenuLoop:
	dynmultipush Text_DelibirdShop_Normal_Egg,  0
	dynmultipush Text_DelibirdShop_Special_Egg, 1
	dynmultipush Text_DelibirdShop_Rare_Egg,    2
	dynmultipush Text_DelibirdShop_SRare_Egg,	3
	dynmultipush Text_DelibirdShop_Epic_Egg,    4
	dynmultipush Text_DelibirdShop_Cancel,      5
	dynmultistack 13, 0, FALSE, 6, FALSE, 0, 0

	copyvar VAR_0x8004, VAR_RESULT

	@ Bボタンやキャンセル押した時
	switch VAR_RESULT
	case 5, DelibirdFinish
	case MULTI_B_PRESSED, DelibirdFinish

	@買いますか？
	msgbox Text_Delibird_WouldYouLikeToBuy, MSGBOX_YESNO
	switch VAR_RESULT
	case NO, DelibirdShop_MenuLoop
	case YES, DelibirdShop_ProcessPurchase

@ 購入しますか？"はい"を選択した後
DelibirdShop_ProcessPurchase:
	switch VAR_0x8004
	case 0, DelibirdShop_BuyNormalEgg
	case 1, DelibirdShop_BuySpecialEgg
	case 2, DelibirdShop_BuyRareEgg
	case 3, DelibirdShop_BuyRareEgg
	case 4, DelibirdShop_BuyEpicEgg

@ ---------------------- 各種メニュデータの設定 ------------------------- @
@ 購入処理に必要が情報を変数にセットし購入処理へ
DelibirdShop_BuyNormalEgg:
	setvar VAR_0x8006, 1000                   @ 価格をセット
	setvar VAR_0x8007, EGG_TYPE_NORMAL                      @ タマゴグループをセット
	goto DelibirdShop_DoPurchase              @ 購入実行処理へ

DelibirdShop_BuySpecialEgg:
	setvar VAR_0x8006, 3000
	setvar VAR_0x8007, EGG_TYPE_SPECIAL
	goto DelibirdShop_DoPurchase

DelibirdShop_BuyRareEgg:
	setvar VAR_0x8006, 5000
	setvar VAR_0x8007, EGG_TYPE_RARE
	goto DelibirdShop_DoPurchase

DelibirdShop_BuySRareEgg:
	setvar VAR_0x8006, 7000
	setvar VAR_0x8007, EGG_TYPE_SRARE
	goto DelibirdShop_DoPurchase

DelibirdShop_BuyEpicEgg:
	setvar VAR_0x8006, 9999
	setvar VAR_0x8007, EGG_TYPE_EPIC
	goto DelibirdShop_DoPurchase

@ ----------------------------- 購入処理 -------------------------------- @
DelibirdShop_DoPurchase:
	@ 1. ポケモンボックスに1個空きがないか確認
	setvar VAR_0x8005, 1                        @ 購入個数(ポケモンボックス必要空き数)
    specialvar VAR_RESULT, HasEmptySlotsInBoxes @ チェックの値はC側で読み取り済み
    goto_if_eq VAR_RESULT, FALSE DelibirdShop_PokemonBox_NotEnoughSpace

	@ 2. お金チェック
    special CheckMoneyFromVar                   @C側でVAR_0x8006を参照してる
    goto_if_eq VAR_RESULT, FALSE, DelibirdShop_NotEnoughMoney

    @ 3. 購入処理
    playse SE_SHOP
    special RemoveMoneyFromVar                @C側でVAR_0x8006を参照してる
    updatemoneybox

	@ 4. タマゴを渡す
    special GiveDelibirdEggFromVar            @C側でVAR_0x8007を参照してる

    @ 6. メニュー表示に戻る
    goto DelibirdShop_MenuLoop

@ ------------------------ 例外処理 ----------------------- @
DelibirdShop_PokemonBox_NotEnoughSpace:
	msgbox Text_DelibirdShop_NotEnough_Space
	goto DelibirdShop_MenuLoop

DelibirdShop_NotEnoughMoney:
	msgbox Text_Delibird_NotEnoughMoney
	goto DelibirdShop_MenuLoop

DelibirdFinish:
	playmoncry SPECIES_DELIBIRD, CRY_MODE_NORMAL
	msgbox Text_Delibird_Thanks, MSGBOX_DEFAULT
	waitmoncry
	hidemoneybox
	release
	end

@ ------------------------ セリフ一覧 --------------------- @
Text_Delibird_Hello:
	.string "Biri Biri$"
Text_Delibird_WouldYouLikeToBuy:
	.string "Biri Biri?$"
Text_Delibird_Thanks:
	.string "Biri Biri!$"
Text_Delibird_NotEnoughMoney:
	.string "Biri Biri...(not enough money)$"
Text_DelibirdShop_NotEnough_Space:
	.string "Biri Biri...\p"
	.string "(Oh the PokemonBox is full...)$"

@ ------------------------ 店内メニューテキスト --------------------- @
Text_DelibirdShop_Normal_Egg:
	.string "Normal Egg        ¥1000$"
Text_DelibirdShop_Special_Egg:
	.string "Special Egg      ¥3000$"
Text_DelibirdShop_Rare_Egg:
	.string "Rare Egg           ¥5000$"
Text_DelibirdShop_SRare_Egg:
	.string "SRare Egg         ¥7000$"
Text_DelibirdShop_Epic_Egg:
	.string "Epic Egg           ¥9999$"
Text_DelibirdShop_Cancel:
	.string "CANSEL$"
