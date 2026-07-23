@@ README @@
@ C側のパス src/delibirdEgg_gacha.c
@ ata/scripts/delibirdShop.inc と defineをシェアしてるから

@ ------------------------ 屋外で隠れてるデリバードに話しかけた時 -------------------------- @
EventScript_DelibirdShop_Outside::
	lock
	faceplayer

	@ 購入数最大25個 制限に引っかかってるか確認
	goto_if_ge VAR_DELIBIRD_EGG_PURCHASE_COUNT, DELIBIRDSHOP_OUTSIDE_MAX_PURCHASE_NUM, DelibirdShop_After_Sould_Out

	@ 購入しますか？と聞かれる
	@ いいえを選択するとデリバード販売員怒る表現へ
	playmoncry SPECIES_DELIBIRD, CRY_MODE_NORMAL
	msgbox Text_Delibird_Outside_WouldYouLikeToBuy, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, DelibirdShop_Outside_Angry_Delibird

	@ ランダムエッグ購入のメニュー表示
	@ ユーザーは選択 or Bで戻る操作可能
	showmoneybox 0, 0, 0
	DelibirdShop_Outside_MenuLoop:
	dynmultipush Text_DelibirdShop_Outside_RandomEgg_1,    0
	dynmultipush Text_DelibirdShop_Outside_RandomEgg_5,    1
	dynmultipush Text_DelibirdShop_Outside_RandomEgg_25,   2
	dynmultipush Text_DelibirdShop_Outside_Cancel,         3
	dynmultistack 13, 0, FALSE, 4, FALSE, 0, 0
	copyvar VAR_0x8004, VAR_RESULT                                      @ 選択した項目を0x8004に収納

	@ Bボタンやキャンセル押した時
	switch VAR_RESULT
	case 3, DelibirdShop_Outside_Finish                                              @ 項目3のCANCEL選択時
	case MULTI_B_PRESSED, DelibirdShop_Outside_Finish                                @ Bボタン操作時

	msgbox Text_Delibird_Outside_YouSureWantToBuyThis, MSGBOX_YESNO     @ 本当にこれにする？ 確認
	switch VAR_RESULT                                                   @ 結果をVAR_RESULTに収納し比較対象にする
	case NO,  DelibirdShop_Outside_MenuLoop                             @ Noを選んだ場合メニューに戻る
	case YES, DelibirdShop_Outside_ProcessPurchase                      @ 購入準備

@ 購入しますか？"はい"を選択した後
DelibirdShop_Outside_ProcessPurchase:
	@ 25個以上買ったら在庫切れ
	goto_if_ge VAR_DELIBIRD_EGG_PURCHASE_COUNT, DELIBIRDSHOP_OUTSIDE_MAX_PURCHASE_NUM, DelibirdShop_Outside_Sould_Out

	@ 選択された商品の購入処理へ
	switch VAR_0x8004                                      
	case 0, DelibirdShop_BuyRandomEgg_1
	case 1, DelibirdShop_BuyRandomEgg_5
	case 2, DelibirdShop_BuyRandomEgg_25

@ ---------------------- 各種メニュデータの設定 ------------------------- @
@ 購入処理に必要が情報を変数にセットし購入処理へ
DelibirdShop_BuyRandomEgg_1:
	setvar VAR_0x8005, 1                      @ 購入数(C側で参照してる)をセット
	setvar VAR_0x8006, 1000                   @ 価格をセット
	setvar VAR_0x8007, EGG_TYPE_RANDOM_1      @ ランダムエッグのタイプをセット
	goto DelibirdShop_Outside_DoPurchase      @ 購入実行処理へ

@ ランダムエッグ5個購入時の値設定
DelibirdShop_BuyRandomEgg_5:
	setvar VAR_0x8005, 5
	setvar VAR_0x8006, 4500
	setvar VAR_0x8007, EGG_TYPE_RANDOM_5
	goto DelibirdShop_Outside_DoPurchase

@ ランダムエッグ25個購入時の値設定
DelibirdShop_BuyRandomEgg_25:
	setvar VAR_0x8005, 25
	setvar VAR_0x8006, 2
	setvar VAR_0x8007, EGG_TYPE_RANDOM_25
	goto DelibirdShop_Outside_DoPurchase

@ ----------------------------- 購入処理 -------------------------------- @
DelibirdShop_Outside_DoPurchase:

	@ 1. ポケモンボックスに空きがないか
    specialvar VAR_RESULT, HasEmptySlotsInBoxes @ チェックの値はC側で読み取り済み
    goto_if_eq VAR_RESULT, FALSE DelibirdShop_Outside_PokemonBox_NotEnoughSpace

	@ 2. お金チェック
    special CheckMoneyFromVar                 @C側でVAR_0x8006を参照してる
    goto_if_eq VAR_RESULT, FALSE, DelibirdShop_Outside_NotEnoughMoney

    @ 3. 購入処理
    playse SE_SHOP
    special RemoveMoneyFromVar                @C側でVAR_0x8006を参照してる
    updatemoneybox

	@ 4. タマゴを渡す
    special GiveDelibirdEggFromVar            @C側でVAR_0x8007を参照してる

    @ 5. 購入数加算(在庫管理用)
    special AddPurchaseCount                  @C側でVAR_0x8005を参照してる

    @ 6. メニュー表示に戻る
    goto DelibirdShop_Outside_MenuLoop

@ ------------------------ 例外処理 ----------------------- @
@ 冒頭で買わないと答えた時
DelibirdShop_Outside_Angry_Delibird:
	applymovement VAR_LAST_TALKED, Common_Movement_FaceAwayPlayer
	waitmovement 0
	msgbox Text_Outside_Delibird_Sad MSGBOX_DEFAULT
	release
	end

@ 屋外でお金が足りなかった時の処理
DelibirdShop_Outside_NotEnoughMoney:
	msgbox Text_Delibird_Outside_NotEnoughMoney
	goto DelibirdShop_Outside_MenuLoop

@ ポケモンボックスが満帆な時の処理
DelibirdShop_Outside_PokemonBox_NotEnoughSpace:
	playmoncry SPECIES_DELIBIRD, CRY_MODE_WEAK_DOUBLES
	msgbox Text_DelibirdShop_Outside_NotEnough_Space
	goto DelibirdShop_Outside_MenuLoop

@ メニューを閉じた時の処理
DelibirdShop_Outside_Finish:
	playmoncry SPECIES_DELIBIRD, CRY_MODE_NORMAL
	msgbox Text_Delibird_Outside_Thanks, MSGBOX_DEFAULT
	waitmoncry
	hidemoneybox
	release
	end

@ 屋外での購入時に在庫切れになった時
DelibirdShop_Outside_Sould_Out:
	playmoncry SPECIES_DELIBIRD, CRY_MODE_ENCOUNTER
	msgbox Text_Delibird_Outside_Sold_Out, MSGBOX_DEFAULT
	waitmoncry
	hidemoneybox
	release
	end

@ 在庫切れになった後に再度デリバードに話しかけた時
DelibirdShop_After_Sould_Out:
	playmoncry SPECIES_DELIBIRD, CRY_MODE_ENCOUNTER
	msgbox Text_Delibird_Outside_Sold_Out, MSGBOX_DEFAULT
	waitmoncry
	hidemoneybox
	release
	end

@ --------- 屋外で堂々としてるデリバードに話しかけた時 ---------- @
EventScript_Delibird_Seems_Busy::
	lock
	faceplayer
	playmoncry SPECIES_DELIBIRD, CRY_MODE_NORMAL
	msgbox Text_Delibird_Normal_Greet, MSGBOX_DEFAULT
	waitmoncry
	applymovement VAR_LAST_TALKED, Common_Movement_FaceOriginalDirection
	delay 40
	msgbox Text_Delibird_Seems_Busy, MSGBOX_DEFAULT
	release
	end

@ ------------------------ セリフ一覧 ------------------------- @
Text_Delibird_Outside_WouldYouLikeToBuy:
	.string "Biri Biri?\p"
	.string "(He is showing me Random Egg)\p"
	.string "(Should I buy them?)$"
Text_Delibird_Outside_YouSureWantToBuyThis:
	.string "Biri Biri?$"
Text_Delibird_Outside_Thanks:
	.string "Biri Biri!$"
Text_Delibird_Outside_NotEnoughMoney:
	.string "Biri Biri...\p"
	.string "(Oh I don't have enough money)$"
Text_DelibirdShop_Outside_NotEnough_Space:
	.string "Biri Biri...\p"
	.string "(Oh the PokemonBox is full...)$"
Text_Outside_Delibird_Sad:
	.string "Biri...$"
Text_Delibird_Outside_Sold_Out:
	.string "Biri! Biri!! Biri!!!\p"
	.string "(Delibird looks so happy)\p"
	.string "(I guess he sold out!)$"
Text_Delibird_Normal_Greet:
	.string "Biri Biri!$"
Text_Delibird_Seems_Busy:
	.string "(Delibird seems busy...)$"

@ ------------------------ 屋外メニュー --------------------- @
Text_DelibirdShop_Outside_RandomEgg_1:
	.string "Random Egg x1     ¥1000$"
Text_DelibirdShop_Outside_RandomEgg_5:
	.string "Random Egg x5     ¥4500$"
Text_DelibirdShop_Outside_RandomEgg_25:
	.string "Random Egg x25 ¥20000$"
Text_DelibirdShop_Outside_Cancel:
	.string "CANSEL$"
