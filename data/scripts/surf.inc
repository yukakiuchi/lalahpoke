EventScript_UseSurf::
	lockall
	msgbox gText_WantToUseSurf, MSGBOX_YESNO
	goto_if_eq VAR_RESULT, NO, EventScript_ReleaseUseSurf
	goto_if_unset FLAG_BADGE01_GET, EventScript_NoBadge05
	setvar 0x8007, 1 @臨時変数にフラグとして代入 フィールド上からかどうか(パーティメニューのなみのりからではない)
	dofieldeffect FLDEFF_USE_SURF

EventScript_ReleaseUseSurf::
	releaseall
	end

EventScript_CurrentTooFast::
	lockall
	checkfieldmove FIELD_MOVE_SURF
	goto_if_eq VAR_RESULT, FALSE, EventScript_CurrentTooFastEndMsg
	playse SE_SELECT
	msgbox Text_CurrentTooFast
EventScript_CurrentTooFastEndMsg::
	releaseall
	end


@ -------------------- Can't Surf Message ---------------------------
EventScript_NoBadge05::
	msgbox Text_NoBadge05, MSGBOX_DEFAULT
	releaseall
	end

Text_NoBadge05:
    .string "Balance Badge required\p"
    .string "Beat the 5th gym leader to get it!$"
