OldaleTown_PokemonCenter_1F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, OldaleTown_PokemonCenter_1F_OnTransition
	map_script MAP_SCRIPT_ON_RESUME, CableClub_OnResume
	.byte 0

OldaleTown_PokemonCenter_1F_OnTransition:
	setrespawn HEAL_LOCATION_OLDALE_TOWN
	call Common_EventScript_UpdateBrineyLocation
	end

OldaleTown_PokemonCenter_1F_EventScript_Nurse::
	setvar VAR_0x800B, LOCALID_OLDALE_NURSE
	call Common_EventScript_PkmnCenterNurse
	waitmessage
	waitbuttonpress
	release
	end

OldaleTown_PokemonCenter_1F_EventScript_Gentleman::
	msgbox OldaleTown_PokemonCenter_1F_Text_TrainersCanUsePC, MSGBOX_NPC
	end

OldaleTown_PokemonCenter_1F_EventScript_Boy::
	msgbox OldaleTown_PokemonCenter_1F_Text_PokemonCentersAreGreat, MSGBOX_NPC
	end

OldaleTown_PokemonCenter_1F_EventScript_Girl::
	lock
	faceplayer
	goto_if_set FLAG_SYS_POKEDEX_GET, OldaleTown_PokemonCenter_1F_EventScript_WirelessClubAvailable
	msgbox OldaleTown_PokemonCenter_1F_Text_WirelessClubNotAvailable, MSGBOX_DEFAULT
	release
	end

OldaleTown_PokemonCenter_1F_EventScript_WirelessClubAvailable::
	msgbox OldaleTown_PokemonCenter_1F_Text_TradedInWirelessClub, MSGBOX_DEFAULT
	release
	end

OldaleTown_PokemonCenter_1F_Text_TrainersCanUsePC:
	.string "Rainbow-type moves deal super-\n"
	.string "effective damage to all types.\p"
	.string "In return, it also takes super-\n"
	.string "effective damage from all types!\p"
	.string "It's a very unique type, but\n"
	.string "dealing 4x damage to almost any\p"
	.string "opponent is a huge advantage!$"

OldaleTown_PokemonCenter_1F_Text_PokemonCentersAreGreat:
	.string "Type matchups are a bit different\n"
	.string "here than in the original games.\p"
	.string "Fairly speaking, each type has\n"
	.string "only 2 strengths and 2 weaknesses.\p"
	.string "Only Normal, Rainbow, Fairy, and\n"
	.string "Dark are a little special, though.\p"
	.string "For details, check the docs or\n"
	.string "ask the developer!$"

OldaleTown_PokemonCenter_1F_Text_WirelessClubNotAvailable:
	.string "The POKéMON WIRELESS CLUB on\n"
	.string "the second floor was built recently.\p"
	.string "But they say they're still making\n"
	.string "adjustments.$"

OldaleTown_PokemonCenter_1F_Text_TradedInWirelessClub:
	.string "Oh, you have a Normal-type\n"
	.string "POKéMON!\p"
	.string "In this world, Normal types take\n"
	.string "half damage from all attacks,\p"
	.string "except for Rainbow-type ones!\p"
	.string "It's a divine protection to shield\n"
	.string "fragile starter POKéMON.\p"
	.string "You'll find more Normal types\n"
	.string "later for specific reasons.\p"
	.string "It might be interesting to keep\n"
	.string "that in mind on your journey!$"
