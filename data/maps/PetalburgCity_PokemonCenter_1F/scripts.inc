PetalburgCity_PokemonCenter_1F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PetalburgCity_PokemonCenter_1F_OnTransition
	map_script MAP_SCRIPT_ON_RESUME, CableClub_OnResume
	.byte 0

PetalburgCity_PokemonCenter_1F_OnTransition:
	setrespawn HEAL_LOCATION_PETALBURG_CITY
	call Common_EventScript_UpdateBrineyLocation
	end

PetalburgCity_PokemonCenter_1F_EventScript_Nurse::
	setvar VAR_0x800B, LOCALID_PETALBURG_NURSE
	call Common_EventScript_PkmnCenterNurse
	waitmessage
	waitbuttonpress
	release
	end

PetalburgCity_PokemonCenter_1F_EventScript_FatMan::
	msgbox PetalburgCity_PokemonCenter_1F_Text_PCStorageSystem, MSGBOX_NPC
	end

PetalburgCity_PokemonCenter_1F_EventScript_Youngster::
	msgbox PetalburgCity_PokemonCenter_1F_Text_OranBerryRegainedHP, MSGBOX_NPC
	end

PetalburgCity_PokemonCenter_1F_EventScript_Woman::
	lock
	faceplayer
	msgbox PetalburgCity_PokemonCenter_1F_Text_ManyTypesOfPokemon, MSGBOX_DEFAULT
	specialvar VAR_RESULT, IsStarterInParty
	goto_if_eq VAR_RESULT, TRUE, PetalburgCity_PokemonCenter_1F_EventScript_SayStarterTypeInfo
	release
	end

PetalburgCity_PokemonCenter_1F_EventScript_SayStarterTypeInfo::
	call_if_eq VAR_STARTER_MON, 0, PetalburgCity_PokemonCenter_1F_EventScript_SayTreeckoType
	call_if_eq VAR_STARTER_MON, 1, PetalburgCity_PokemonCenter_1F_EventScript_SayTorchicType
	call_if_eq VAR_STARTER_MON, 2, PetalburgCity_PokemonCenter_1F_EventScript_SayMudkipType
	release
	end

PetalburgCity_PokemonCenter_1F_EventScript_SayTreeckoType::
	msgbox PetalburgCity_PokemonCenter_1F_Text_TreeckoIsGrassType, MSGBOX_DEFAULT
	return

PetalburgCity_PokemonCenter_1F_EventScript_SayTorchicType::
	msgbox PetalburgCity_PokemonCenter_1F_Text_TorchicIsFireType, MSGBOX_DEFAULT
	return

PetalburgCity_PokemonCenter_1F_EventScript_SayMudkipType::
	msgbox PetalburgCity_PokemonCenter_1F_Text_MudkipIsWaterType, MSGBOX_DEFAULT
	return

PetalburgCity_PokemonCenter_1F_Text_PCStorageSystem:
	.string "Select a POKéMON in your party,\n"
	.string "then choose LEARN MOVES!\p"
	.string "That way, you can relearn past\n"
	.string "level-up moves anytime you want!\p"
	.string "However, an evolved POKéMON counts\n"
	.string "as having a brand-new body...\p"
	.string "So it can't relearn moves from\n"
	.string "before it evolved!$"

PetalburgCity_PokemonCenter_1F_Text_OranBerryRegainedHP:
	.string "Dark and Fairy types deal super-\n"
	.string "effective damage to each other,\p"
	.string "and deal normal damage to all\n"
	.string "other types. Simple and easy!$"

PetalburgCity_PokemonCenter_1F_Text_ManyTypesOfPokemon:
	.string "Actually, there are way more moves\n"
	.string "you can learn from TMs!\p"
	.string "Most POKéMON can learn over 30\n"
	.string "different TM moves.\p"
	.string "Most are status moves, but ones\n"
	.string "like Belly Drum make them super\p"
	.string "strong! You can get TMs as drops\n"
	.string "or steal them from wild POKéMON!$"

PetalburgCity_PokemonCenter_1F_Text_TreeckoIsGrassType:
	.string "To get a lot of TMs, aim for the\n"
	.string "TM for Thief dropped by Delibird!\p"
	.string "That should make the game much\n"
	.string "easier for you to clear!\p"
	.string "There are plenty of Delibird in\n"
	.string "the forest, so go find them!$"

PetalburgCity_PokemonCenter_1F_Text_TorchicIsFireType:
	.string "To get a lot of TMs, aim for the\n"
	.string "TM for Thief dropped by Delibird!\p"
	.string "That should make the game much\n"
	.string "easier for you to clear!\p"
	.string "There are plenty of Delibird in\n"
	.string "the forest, so go find them!$"

PetalburgCity_PokemonCenter_1F_Text_MudkipIsWaterType:
	.string "To get a lot of TMs, aim for the\n"
	.string "TM for Thief dropped by Delibird!\p"
	.string "That should make the game much\n"
	.string "easier for you to clear!\p"
	.string "There are plenty of Delibird in\n"
	.string "the forest, so go find them!$"

