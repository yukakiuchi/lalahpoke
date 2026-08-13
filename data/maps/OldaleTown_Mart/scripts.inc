OldaleTown_Mart_MapScripts::
	.byte 0

OldaleTown_Mart_EventScript_Clerk::
	lock
	faceplayer
	message gText_HowMayIServeYou
	waitmessage
	goto_if_set FLAG_ADVENTURE_STARTED, OldaleTown_Mart_ExpandedItems
	pokemart OldaleTown_Mart_Pokemart_Basic
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
OldaleTown_Mart_Pokemart_Basic:
	.2byte ITEM_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_TM01
	.2byte ITEM_TM03
	.2byte ITEM_TM05
	.2byte ITEM_TM11
	.2byte ITEM_TM12
	.2byte ITEM_TM13
	.2byte ITEM_TM14
	.2byte ITEM_TM21
	.2byte ITEM_TM28
	.2byte ITEM_TM56
	.2byte ITEM_TM66
	.2byte ITEM_TM97
	.2byte ITEM_TM98
	.2byte ITEM_TM108
	pokemartlistend

OldaleTown_Mart_ExpandedItems::
	pokemart OldaleTown_Mart_Pokemart_Expanded
	msgbox gText_PleaseComeAgain, MSGBOX_DEFAULT
	release
	end

	.align 2
OldaleTown_Mart_Pokemart_Expanded:
	.2byte ITEM_POKE_BALL
	.2byte ITEM_POTION
	.2byte ITEM_ANTIDOTE
	.2byte ITEM_PARALYZE_HEAL
	.2byte ITEM_AWAKENING
	.2byte ITEM_TM01
	.2byte ITEM_TM03
	.2byte ITEM_TM05
	.2byte ITEM_TM11
	.2byte ITEM_TM12
	.2byte ITEM_TM13
	.2byte ITEM_TM14
	.2byte ITEM_TM21
	.2byte ITEM_TM28
	.2byte ITEM_TM56
	.2byte ITEM_TM66
	.2byte ITEM_TM97
	.2byte ITEM_TM98
	.2byte ITEM_TM108
	pokemartlistend

OldaleTown_Mart_EventScript_Woman::
	lock
	faceplayer
	goto_if_set FLAG_ADVENTURE_STARTED, OldaleTown_Mart_EventScript_PokeBallsInStock
	msgbox OldaleTown_Mart_Text_PokeBallsAreSoldOut, MSGBOX_DEFAULT
	release
	end

OldaleTown_Mart_EventScript_PokeBallsInStock::
	msgbox OldaleTown_Mart_Text_ImGoingToBuyPokeBalls, MSGBOX_DEFAULT
	release
	end

OldaleTown_Mart_EventScript_Boy::
	msgbox OldaleTown_Mart_Text_RestoreHPWithPotion, MSGBOX_NPC
	end

OldaleTown_Mart_Text_PokeBallsAreSoldOut:
	.string "The clerk says they're all sold out.\n"
	.string "I can't buy any POKé BALLS.$"

OldaleTown_Mart_Text_ImGoingToBuyPokeBalls:
	.string "Shops don't sell very good items\n"
	.string "in this world.\p"
	.string "Instead, you mostly rely on item\n"
	.string "drops from POKéMON!\p"
	.string "It's a bit different from usual,\n"
	.string "but interesting, isn't it?\p"
	.string "It gives more reason to battle\n"
	.string "killing two birds with one stone!$"

OldaleTown_Mart_Text_RestoreHPWithPotion:
	.string "Wild POKéMON drop common items\n"
	.string "20 percent of the time, and\p"
	.string "rare items 10 percent of the time.\p"
	.string "That might be rebalanced later,\n"
	.string "but that's the rate for now.\p"
	.string "By the way, held items are at\n"
	.string "30 percent for both types!\p"
	.string "So catching POKéMON or stealing\n"
	.string "their held items is a much better\p"
	.string "way to get rare items!$"

