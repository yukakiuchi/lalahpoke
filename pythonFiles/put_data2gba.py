# =======================================================================================
# 💡
# 最重要! AIさんへ: このファイルの中のコメントは消さないこと
# スペースや改行もインデントのためや見やすいようにしてるから消さないで
# コードを書くときは変数名はlとか省略せずしっかり言葉で書く
# エラーがある場合は確信がある場合はそのまま説明して確信でない場合は原因となりそうな箇所にデバッグコードを
# 書くようにお願いします。もし変更箇所が1~2箇所だけならピンポイントでその箇所を教えてこう書くと教える
# もし3~4箇所以上必要な場合はまとまった処理ごとにコピペできるように修正を表示する
# 【機能追加・コード修正時の厳格ルール】
# 例外処理・サイレントエラーの完全防止:
# コードの追加・変更を行う際は、正常系だけでなく「対象データや記述が存在しなかった場合」「フォーマットが想定と異なる場合」の例外処理（エラー検知・警告ログ出力・スキップ処理）が既存コードと同等に備わっているか必ず事前に検証すること。
# 事前の不確実性・エッジケースの提示:
# ユーザーから指示された処理に対し、データが存在しない場合や失敗するリスクのあるパターン（エッジケース）が懸念される場合は、コードを出す前に必ず質問・提案を行うこと。
# ・コードは特に指示がない場合は
# ピンポイントで変更箇所を下記の形式で伝える
# ```
# (既存のコード3行分)
# // ここから
# ... 変更処理 ...
# // ここまで
# (既存のコード3行分)
# ```
# ・変数名は省略せずしっかりとした単語にすること
# =======================================================================================
import csv
import io
import os
import sys
import json
import requests
import re
import time
from PIL import Image
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
warnings.filterwarnings("ignore", category=DeprecationWarning)

########################### 設定 ###############################
SPECIS_CSV_FILE_PATH                 = "/Users/yu/Desktop/sprites.csv"
MOVES_CSV_FILE_PATH                  = "/Users/yu/Desktop/moves.csv"
LEARNSET_CSV_FILE_PATH               = "/Users/yu/Desktop/learnset.csv"
ORIGINAL_SPECIES_INFO_DIR            = "/Users/yu/Desktop/Original_expantion_data/PokeData/species_info"
ORIGINAL_SPECIES_IDS_FILE_PATH       = "/Users/yu/Desktop/Original_expantion_data/PokeData/id_setting/species.h"
ORIGINAL_ANIM_FRONT_FILE_PATH        = "/Users/yu/Desktop/Original_expantion_data/PokeData/anim_sprite_setting/pokemon.h"
ORIGINAL_POKEMON_PNG_DIR             = "/Users/yu/Desktop/Original_expantion_data/PokeGraphics"
ORIGINAL_NATIONAL_POKEDEX_FILE_PATH  = "/Users/yu/Desktop/Original_expantion_data/NationalPokedex/pokedex.h"
ORIGINAL_LEARNSET_FILE_PATH          = "/Users/yu/Desktop/expand/src/data/pokemon/all_learnables.json"
ORIGINAL_MOVES_FILE_PATH             = "/Users/yu/Desktop/Original_expantion_data/Moves/gen_9_moves.h"
CURRENT_POKEMON_PNG_DIR              = "/Users/yu/Desktop/expand/graphics/pokemon"
CURRENT_SPECIES_INFO_DIR             = "/Users/yu/Desktop/expand/src/data/pokemon/species_info"
CURRENT_SPECIES_ID_FILE_PATH         = "/Users/yu/Desktop/expand/include/constants/species.h"
CURRENT_ANIM_FRONT_SETTING_FILE_PATH = "/Users/yu/Desktop/expand/src/data/graphics/pokemon.h"
CURRENT_NATIONAL_DEX_FILE_PATH       = "/Users/yu/Desktop/expand/include/constants/pokedex.h"
CURRENT_MOVES_FILE_PATH              = "/Users/yu/Desktop/expand/src/data/pokemon/level_up_learnsets/gen_9.h"
CURRENT_LEARNSET_FILE_PATH           = "/Users/yu/Desktop/expand/src/data/pokemon/all_learnables.json"

START_ID = 1
END_ID = 272

CONFIG_VARS = [
    "UPDATE_SPRITES",
    "UPDATE_ICONS",
    "UPDATE_ICON_PALS",
    "UPDATE_TYPE",
    "UPDATE_HOLDITEMS",
    "UPDATE_ABILITIES",
    "UPDATE_STATUS",
    "UPDATE_DESCRIPTIONS",
    "UPDATE_EVOLUTIONS",
    "UPDATE_MOVES",
    "UPDATE_LEARNSET",
    "UPDATE_ANIM_FRONT",
    "UPDATE_ID_SORT",
    "UPDATE_B_SPRITE_OFFSET",
    "UPDATE_DISPLAY_NAME",
    "UPDATE_NATIONAL_DEX",
]


UPDATE_PNG                = False
UPDATE_ALL_SPECIES_INFO   = True
UPDATE_ID_SORT            = True
UPDATE_ANIM_FRONT         = True
UPDATE_NATIONAL_DEX       = True


if UPDATE_ALL_SPECIES_INFO == True:
    UPDATE_ICON_PALS       = True
    UPDATE_TYPE            = True
    UPDATE_HOLDITEMS       = True
    UPDATE_ABILITIES       = True
    UPDATE_STATUS          = True
    UPDATE_DESCRIPTIONS    = True
    UPDATE_EVOLUTIONS      = True
    UPDATE_B_SPRITE_OFFSET = True
    UPDATE_DISPLAY_NAME    = True
    UPDATE_MOVES           = True
    UPDATE_LEARNSET     = True

if UPDATE_PNG         == True:
    UPDATE_SPRITES        = True
    UPDATE_ICONS          = True


ALLOWED_TYPES =[
    "NORMAL", "FIGHTING", "FLYING", "ROCK", "BUG", "FIRE", 
    "WATER", "GRASS", "ELECTRIC", "ICE", "DARK", "FAIRY", "RAINBOW"]

REQUIRED_CSV_HEADERS = [
    "id","original_name_code","display_name", "sprite_url","icon_url", "pal", "dex_description", 
    "type", "itemCommon", "itemRare", "abilities", "evo_requirements", "backPicYOffset","frontPicYOffset","enemyMonElevation","Shadow"]

# 画像処理の時の特殊なフォルダ分け設定（SPECIES名: フォルダ名）
# 指定がない場合は既存の自動ルールが適用されます
CUSTOM_FOLDER_MAP = {
    'SPECIES_HO_OH': 'ho_oh',
    'SPECIES_TERAPAGOS_NORMAL': 'terapagos',
    'SPECIES_SQUAWKABILLY_GREEN' : 'squawkabilly',
    'SPECIES_BASCULEGION_M' : 'basculegion',
    'SPECIES_DUDUNSPARCE_TWO_SEGMENT' : 'dudunsparce',
    'SPECIES_HOOPA_CONFINED':'hoopa',
    'SPECIES_WO_CHIEN' : 'wo_chien',
}

NATIONAL_DEX_MAPPING = {
    'SPECIES_WO_CHIEN'                : 'NATIONAL_DEX_WO_CHIEN',
    'SPECIES_SQUAWKABILLY_GREEN'      : 'NATIONAL_DEX_SQUAWKABILLY',
    'SPECIES_KYUREM_BLACK'            : 'NATIONAL_DEX_KYUREM',
    'SPECIES_BASCULEGION_M'           : 'NATIONAL_DEX_BASCULEGION',
    'SPECIES_DUDUNSPARCE_TWO_SEGMENT' : 'NATIONAL_DEX_DUDUNSPARCE',
    'SPECIES_HOOPA_CONFINED'          : 'NATIONAL_DEX_HOOPA',
    'SPECIES_ZORUA_HISUI'             : 'NATIONAL_DEX_ZORUA',
    'SPECIES_ZOROARK_HISUI'           : 'NATIONAL_DEX_ZOROARK',
    'SPECIES_TERAPAGOS_NORMAL'        : 'NATIONAL_DEX_TERAPAGOS',
    'SPECIES_HO_OH'                   : 'NATIONAL_DEX_HO_OH',
}

MAX_WORKERS = 30
MAX_PICS_DOWNLOAD_RETRIES = 3
##########################################################
# --- 画像キャッシュ用変数と関数 ---
task_dict = {}
moves_task_dictionary = {}
cache_moves_file_content = ""
learnset_task_dictionary = {}
cache_learnset_json_dict = {}
poke_graphics_cache = {}
cache_gen_x_families_h_files = {}
cache_species_h = {}
cache_pokemon_h = {}
icon_pal_num = []


def init():
    for var in CONFIG_VARS:
        if var not in globals():
            globals()[var] = False

def check_csv_n_create_tasks():
    
    # -------- 1. CSVのヘッダーチェック -------
    # コード数を減らすためCSVのカラムの中身が空っぽかどうかのチェックは行わないから自分で確認して
    try:
        with open(SPECIS_CSV_FILE_PATH, newline="", encoding="utf-8") as f:
            csv_reader = csv.DictReader(f)     # header情報を取得するため、中身は文字コードであまり読めない
            csv_header = csv_reader.fieldnames # ヘッダーをパイソンで読めるような形にする
            csv_data = list(csv_reader)

        missing = [col for col in REQUIRED_CSV_HEADERS if col not in (csv_header or [])]
        if missing:
            print(f"❌ エラー: 不足しているカラム: {missing}があるため、処理を開始できません。")
            sys.exit(1)

    except FileNotFoundError:
        print(f"❌ エラー: 指定されたファイルが見つかりません: {SPECIS_CSV_FILE_PATH}")
        sys.exit(1)
    # --------- 2. 指定したidの行データのみを抜き取る -------
    for row in csv_data:
        poke_id = int(row["id"])
        if START_ID <= poke_id <= END_ID:
            task_dict[poke_id] = row
    return
    # ------------------------------------------------

# 1. 修得技CSVの検証とデータ読み込み
def check_moves_csv_and_validate():
    print("\n" + "✨" * 40)
    print("     修得技CSV (moves.csv) の検証と読み込みを開始します")
    print("✨" * 40 + "\n")

    if not os.path.exists(MOVES_CSV_FILE_PATH):
        print(f"❌ エラー: 指定された修得技ファイルが見つかりません: {MOVES_CSV_FILE_PATH}")
        sys.exit(1)

    invalid_entries = []

    try:
        with open(MOVES_CSV_FILE_PATH, newline="", encoding="utf-8") as moves_file_object:
            csv_reader = csv.DictReader(moves_file_object)
            for row in csv_reader:
                poke_id = int(row["id"])
                if START_ID <= poke_id <= END_ID:
                    original_name_code = row.get("original_name_code", "").strip()
                    
                    # moves_1 から moves_16 までのカラムの妥当性をチェック
                    for move_index in range(1, 17):
                        column_name = f"moves_{move_index}"
                        raw_move_value = row.get(column_name, "").strip()
                        
                        if not raw_move_value:
                            continue

                        # カンマが含まれていない場合（レベル表記がない場合）
                        if "," not in raw_move_value:
                            invalid_entries.append({
                                "id": poke_id,
                                "original_name_code": original_name_code,
                                "column": column_name,
                                "value": raw_move_value,
                                "reason": "レベル指定（カンマ）が含まれていません"
                            })
                            continue

                        # カンマ前後のパースチェック
                        move_data_parts = raw_move_value.split(",", 1)
                        level_string = move_data_parts[0].strip()
                        move_name = move_data_parts[1].strip()

                        if not level_string.isdigit():
                            invalid_entries.append({
                                "id": poke_id,
                                "original_name_code": original_name_code,
                                "column": column_name,
                                "value": raw_move_value,
                                "reason": f"レベル数値 '{level_string}' が正しくありません"
                            })
                            continue

                        if not move_name:
                            invalid_entries.append({
                                "id": poke_id,
                                "original_name_code": original_name_code,
                                "column": column_name,
                                "value": raw_move_value,
                                "reason": "技名が指定されていません"
                            })
                            continue

                    moves_task_dictionary[poke_id] = row

    except Exception as error_message:
        print(f"❌ 修得技CSVの読み込み中にエラーが発生しました: {error_message}")
        sys.exit(1)

    if invalid_entries:
        print("❌ 以下の修得技CSVデータ内に不正なフォーマットが発見されたため処理を停止します:\n")
        for entry in invalid_entries:
            print(f"   - [ID: {entry['id']}] {entry['original_name_code']} | カラム: {entry['column']} | 値: '{entry['value']}' | 原因: {entry['reason']}")
        print("\n修得技CSVデータを確認・修正の上、再度実行してください。")
        sys.exit(1)

    print(f"✅ 修得技CSVの検証完了: 対象 {len(moves_task_dictionary)} 件のデータを正常に取得しました。")


# 2. 修得技（gen_9_moves.h）ファイルのメモリキャッシュ化
def cache_moves_file():
    global cache_moves_file_content
    if os.path.exists(ORIGINAL_MOVES_FILE_PATH):
        print(f"📦 ORIGINAL_MOVES_FILEをメモリにキャッシュ中...\n📁({ORIGINAL_MOVES_FILE_PATH})")
        with open(ORIGINAL_MOVES_FILE_PATH, "r", encoding="utf-8", errors="ignore") as moves_file_object:
            cache_moves_file_content = moves_file_object.read()
        print("✅ キャッシュ完了: 修得技ファイル")
    else:
        print(f"⚠️ {ORIGINAL_MOVES_FILE_PATH} が見つからないため、修得技ファイルのキャッシュに失敗しました。")


# 3. キャッシュに対する修得技上書きおよび実ファイル適用
def update_pokemon_moves():
    global cache_moves_file_content
    print("\n" + "✨" * 40)
    print("     修得技 (gen_9.h) の上書き処理を開始します")
    print("✨" * 40 + "\n")

    if not cache_moves_file_content:
        print("⚠️ 修得技のキャッシュデータが存在しないため、処理をスキップします。")
        return

    working_content = cache_moves_file_content
    changed_pokemon_logs = []
    failed_species_list = []

    for pokemon_id, row_data in moves_task_dictionary.items():
        original_name_code = row_data.get("original_name_code", "").strip()
        
        # SPECIES_WO_CHIEN -> wochien（アンダースコア消去・小文字化）
        clean_species_name = original_name_code.replace("SPECIES_", "").replace("_", "")

        # 大文字小文字を区別しない正規表現パターンを作成
        search_pattern = re.compile(
            rf"(static\s+const\s+struct\s+LevelUpMove\s+s{clean_species_name}LevelUpLearnset\s*\[\s*\]\s*=\s*\{{)(.*?)(\}};\n?)",
            re.DOTALL | re.IGNORECASE
        )

        match_result = search_pattern.search(working_content)
        if not match_result:
            failed_species_list.append(f"ID:{pokemon_id} ({original_name_code} -> s{clean_species_name}LevelUpLearnset[])")
            continue

        # 新しい修得技ブロックの行を生成
        move_entry_lines = []
        for move_index in range(1, 17):
            column_name = f"moves_{move_index}"
            raw_move_value = row_data.get(column_name, "").strip()
            if not raw_move_value:
                continue

            move_data_parts = raw_move_value.split(",", 1)
            level_number = move_data_parts[0].strip()
            move_name = move_data_parts[1].strip()
            formatted_level_number = f"{int(level_number):>2}"
            move_entry_lines.append(f"    LEVEL_UP_MOVE({formatted_level_number}, {move_name}),")

        move_entry_lines.append("    LEVEL_UP_END")

        new_block_content = "\n" + "\n".join(move_entry_lines) + "\n"
        
        # ブロック全体の置き換え処理
        header_text = match_result.group(1)
        footer_text = match_result.group(3)
        replaced_full_block = f"{header_text}{new_block_content}{footer_text}"

        working_content = working_content[:match_result.start()] + replaced_full_block + working_content[match_result.end():]
        changed_pokemon_logs.append(f"ID:{pokemon_id} ({original_name_code}) の修得技を上書き更新")

    # 全ポケモンの置換完了後、キャッシュを最新に更新
    cache_moves_file_content = working_content

    # 完成したキャッシュ内容と実ファイル（CURRENT_MOVES_FILE_PATH）の比較・適用
    needs_write = True
    if os.path.exists(CURRENT_MOVES_FILE_PATH):
        with open(CURRENT_MOVES_FILE_PATH, "r", encoding="utf-8", errors="ignore") as current_moves_file_object:
            if current_moves_file_object.read() == cache_moves_file_content:
                needs_write = False

    if needs_write:
        destination_directory = os.path.dirname(CURRENT_MOVES_FILE_PATH)
        if destination_directory and not os.path.exists(destination_directory):
            os.makedirs(destination_directory, exist_ok=True)

        with open(CURRENT_MOVES_FILE_PATH, "w", encoding="utf-8") as current_moves_file_object:
            current_moves_file_object.write(cache_moves_file_content)
        
        print("📝 修得技データを適用しました:")
        for log_message in changed_pokemon_logs:
            print(f"   - {log_message}")
        print(f"\n💾 変更を適用しました: {os.path.basename(CURRENT_MOVES_FILE_PATH)}")
    else:
        print("💾 変更はありません (すでに最新の状態です)")

    if failed_species_list:
        print(f"\n❌ 以下の修得技データブロックが見つからずスキップされました:\n" + "\n".join(failed_species_list))
# ------------------------------------------------------------------------------------------------------------------------------------------------ #

def check_learnset_csv_and_validate():
    print("\n" + "✨" * 40)
    print("     修得技CSV (learnset.csv) の検証と読み込みを開始します")
    print("✨" * 40 + "\n")

    if not os.path.exists(LEARNSET_CSV_FILE_PATH):
        print(f"❌ エラー: 指定された修得技ファイルが見つかりません: {LEARNSET_CSV_FILE_PATH}")
        sys.exit(1)

    invalid_entries = []

    try:
        with open(LEARNSET_CSV_FILE_PATH, newline="", encoding="utf-8") as learnset_file_object:
            csv_reader = csv.DictReader(learnset_file_object)
            field_names = csv_reader.fieldnames or []

            # moves_ で始まるカラムを抽出し、数値順（1, 2, 3...）にソート
            moves_columns = [column for column in field_names if column.startswith("moves_")]
            def get_column_index(column_name):
                number_part = column_name.replace("moves_", "")
                return int(number_part) if number_part.isdigit() else 9999

            moves_columns.sort(key=get_column_index)

            for line_number, row in enumerate(csv_reader, start=2):
                raw_poke_id = row.get("id", "").strip()

                # id カラムが数値でない場合、行番号と詳細を出力してエラー停止
                if not raw_poke_id.isdigit():
                    original_name_code = row.get("original_name_code", "不明")
                    print(f"❌ エラー: CSV {line_number} 行目の 'id' カラムの値が不正です。")
                    print(f"   - 取得された id の値 : '{raw_poke_id}'")
                    print(f"   - 対象の種族コード    : '{original_name_code}'")
                    print(f"   - 原因: CSVのカンマの数が多すぎる/少なすぎるため、列がズレている可能性があります。")
                    sys.exit(1)

                poke_id = int(raw_poke_id)

                if START_ID <= poke_id <= END_ID:
                    original_name_code = row.get("original_name_code", "").strip()

                    for column_name in moves_columns:
                        raw_move_value = row.get(column_name, "").strip()

                        if not raw_move_value:
                            continue

                        # カンマが含まれている場合（レベル指定などが誤混入している場合）
                        if "," in raw_move_value:
                            invalid_entries.append({
                                "id": poke_id,
                                "original_name_code": original_name_code,
                                "column": column_name,
                                "value": raw_move_value,
                                "reason": "カンマが含まれています（技名のみ指定してください）"
                            })
                            continue

                        # MOVE_ から始まっていない場合
                        if not raw_move_value.startswith("MOVE_"):
                            invalid_entries.append({
                                "id": poke_id,
                                "original_name_code": original_name_code,
                                "column": column_name,
                                "value": raw_move_value,
                                "reason": "'MOVE_' から始まっていません"
                            })
                            continue

                    learnset_task_dictionary[poke_id] = row

    except Exception as error_message:
        print(f"❌ 修得技CSVの読み込み中にエラーが発生しました: {error_message}")
        sys.exit(1)

    if invalid_entries:
        print("❌ 以下の修得技CSVデータ内に不正なフォーマットが発見されたため処理を停止します:\n")
        for entry in invalid_entries:
            print(f"   - [ID: {entry['id']}] {entry['original_name_code']} | カラム: {entry['column']} | 値: '{entry['value']}' | 原因: {entry['reason']}")
        print("\n修得技CSVデータを確認・修正の上、再度実行してください。")
        sys.exit(1)

    print(f"✅ 修得技CSVの検証完了: 対象 {len(learnset_task_dictionary)} 件のデータを正常に取得しました。")


# 2. 修得技（all_learnables.json）ファイルのメモリキャッシュ化
def cache_learnset_file():
    global cache_learnset_json_dict
    if os.path.exists(ORIGINAL_LEARNSET_FILE_PATH):
        print(f"📦 ORIGINAL_LEARNSET_FILEをメモリにキャッシュ中...\n📁({ORIGINAL_LEARNSET_FILE_PATH})")
        with open(ORIGINAL_LEARNSET_FILE_PATH, "r", encoding="utf-8", errors="ignore") as learnset_file_object:
            cache_learnset_json_dict = json.load(learnset_file_object)
        print("✅ キャッシュ完了: 修得技JSONファイル")
    else:
        print(f"⚠️ {ORIGINAL_LEARNSET_FILE_PATH} が見つからないため、修得技JSONファイルのキャッシュに失敗しました。")


# 3. キャッシュに対する修得技上書きおよび実ファイル適用
def update_pokemon_learnset():
    global cache_learnset_json_dict
    print("\n" + "✨" * 40)
    print("     修得技 (all_learnables.json) の上書き処理を開始します")
    print("✨" * 40 + "\n")

    if not cache_learnset_json_dict:
        print("⚠️ 修得技のJSONキャッシュデータが存在しないため、処理をスキップします。")
        return

    changed_pokemon_logs = []
    failed_species_list = []

    for pokemon_id, row_data in learnset_task_dictionary.items():
        original_name_code = row_data.get("original_name_code", "").strip()

        # SPECIES_HO_OH -> HO_OH （SPECIES_ 以降の文字列を取得してキー検索）
        search_key_name = original_name_code.replace("SPECIES_", "")

        # moves_ で始まるカラムから有効な技名を動的に抽出
        move_name_list = []
        moves_columns = [column for column in row_data.keys() if column.startswith("moves_")]
        def get_column_index(column_name):
            number_part = column_name.replace("moves_", "")
            return int(number_part) if number_part.isdigit() else 9999

        moves_columns.sort(key=get_column_index)

        for column_name in moves_columns:
            raw_move_value = row_data.get(column_name, "").strip()
            if raw_move_value:
                move_name_list.append(raw_move_value)

        # 技が1つも指定されていない場合は完全にスキップして次へ進む
        if not move_name_list:
            continue

        # 対象のキー（例: "HO_OH"）がJSONデータ内に存在するかチェック
        if search_key_name not in cache_learnset_json_dict:
            failed_species_list.append(f"ID:{pokemon_id} ({original_name_code} -> \"{search_key_name}\")")
            continue

        # JSONの該当キーの配列データを完全上書き
        cache_learnset_json_dict[search_key_name] = move_name_list
        changed_pokemon_logs.append(f"ID:{pokemon_id} ({original_name_code} / キー:\"{search_key_name}\") の修得技を上書き更新")

    # JSON文字列に整形（インデント2スペース）
    formatted_json_content = json.dumps(cache_learnset_json_dict, indent=2, ensure_ascii=False) + "\n"

    # 実ファイル（CURRENT_LEARNSET_FILE_PATH）と比較して書き込み
    needs_write = True
    if os.path.exists(CURRENT_LEARNSET_FILE_PATH):
        with open(CURRENT_LEARNSET_FILE_PATH, "r", encoding="utf-8", errors="ignore") as current_file_object:
            if current_file_object.read() == formatted_json_content:
                needs_write = False

    if needs_write:
        destination_directory = os.path.dirname(CURRENT_LEARNSET_FILE_PATH)
        if destination_directory and not os.path.exists(destination_directory):
            os.makedirs(destination_directory, exist_ok=True)

        with open(CURRENT_LEARNSET_FILE_PATH, "w", encoding="utf-8") as current_file_object:
            current_file_object.write(formatted_json_content)

        print("📝 修得技(JSON)データを適用しました:")
        for log_message in changed_pokemon_logs:
            print(f"   - {log_message}")
        print(f"\n💾 変更を適用しました: {os.path.basename(CURRENT_LEARNSET_FILE_PATH)}")
    else:
        print("💾 変更はありません (すでに最新の状態です)")

    if failed_species_list:
        print(f"\n❌ 以下の修得技(JSON)キーが見つからずスキップされました:\n" + "\n".join(failed_species_list))
# ------------------------------------------------------------------------------------------------------------------------------------------------ #






def load_poke_graphics_cache():
    """PokeGraphicsフォルダの全ファイルをメモリに一括読み込み"""
    src_dir = ORIGINAL_POKEMON_PNG_DIR
    print(f"📦 PokeGraphicsをメモリにキャッシュ中...\n📁({src_dir})")
    if not os.path.exists(src_dir):
        print(f"⚠️ 警告: PokeGraphicsフォルダが見つかりません。")
        return

    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(('.png', '.pal')):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, src_dir)
                with open(file_path, 'rb') as f:
                    poke_graphics_cache[rel_path] = f.read()
    print(f"✅ キャッシュ完了: {len(poke_graphics_cache)} ファイル")

def apply_poke_graphics_cache():
    """キャッシュの内容をCURRENT_POKEMON_PNG_DIRへ適用（差分比較）"""
    print(f"\n💾 キャッシュから {CURRENT_POKEMON_PNG_DIR} へ変更を適用中...")
    if not os.path.exists(CURRENT_POKEMON_PNG_DIR):
        os.makedirs(CURRENT_POKEMON_PNG_DIR, exist_ok=True)
        
    updated_count = 0
    for rel_path, cache_data in poke_graphics_cache.items():
        out_path = os.path.join(CURRENT_POKEMON_PNG_DIR, rel_path)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        
        # バイナリレベルでの完全一致比較
        needs_update = True
        if os.path.exists(out_path):
            with open(out_path, 'rb') as f:
                if f.read() == cache_data:
                    needs_update = False
                    
        if needs_update:
            with open(out_path, 'wb') as f:
                f.write(cache_data)
            updated_count += 1
            
    print(f"✅ 適用完了: {updated_count} ファイル更新しました。\n")
    print("\n🌈 すべて of の画像処理が正常に完了しました。")

def download_n_process_graphics():
    print("\n\n✨✨✨✨✨ 画像処理を開始します ✨✨✨✨✨")

    # 1. 【キャッシュ】画像の事前読み込み
    load_poke_graphics_cache()

    # 処理が必要なidたち
    download_required_ids = sorted(list(task_dict.keys()))
    retry_counts = {poke_id: 0 for poke_id in download_required_ids}

    retry_times = 1
    while download_required_ids:
        print(f"\n🔄 処理開始 ({retry_times}回目:残り {len(download_required_ids)}件)\n" + "-" * 40)

        next_incomplete_ids = []
        current_tasks = [(task_dict[poke_id], poke_id) for poke_id in download_required_ids]
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # futureオブジェクトを「並列処理のタスク」という分かりやすい名前に変更
            task_futures = {executor.submit(do_download, row, poke_id): poke_id for row, poke_id in current_tasks}
            
            for completed_task in as_completed(task_futures):
                poke_id, success_download_sprite, success_download_icon, target_pokemon_folder, sprite_bytes, icon_bytes = completed_task.result()
                print(f"ID: {poke_id}")

                # スプライトの処理、またはアイコンの処理のどちらか片方でも失敗（False）なら
                if not success_download_sprite or not success_download_icon:
                    retry_counts[poke_id] += 1
                    if retry_counts[poke_id] < MAX_PICS_DOWNLOAD_RETRIES:
                        next_incomplete_ids.append(poke_id)                
                        print(f"❌❌ ダウンロード失敗!! ❌❌")
                        print("-" * 40)
                    else:
                        print(f"❌ ID {poke_id} は最大リトライ回数を超えたためスキップします。")
                else:
                    if sprite_bytes:
                        print(f"SPRITE  : ダウンロード完了")
                        # スプライトのデータをスプライト専用キャッシュ（または処理関数）に安全に保存
                        process_and_sync_poke_sprites(Image.open(io.BytesIO(sprite_bytes)), target_pokemon_folder, poke_id)

                    if icon_bytes:
                        print(f"ICON    : ダウンロード完了")
                        print(f"-" * 40)
                        # アイコンのデータをアイコン専用キャッシュ（poke_graphics_cache）に安全に保存
                        relative_path = os.path.join(target_pokemon_folder, "icon.png")
                        poke_graphics_cache[relative_path] = icon_bytes

        download_required_ids = sorted(list(set(next_incomplete_ids)))

        if download_required_ids:
            print(f"\n⚠️  通信エラーがあったため3秒後に再試行します... ⚠️")
            print(f"残りID: {download_required_ids}")
            retry_times += 1
            time.sleep(3)
        else:
            failed_ids = [pid for pid, count in retry_counts.items() if count >= MAX_PICS_DOWNLOAD_RETRIES]
            
            if failed_ids:
                print(f"\n❌ 更新できなかったIDがあります: {failed_ids}")
                print("   ※これらは最大リトライ回数を超えたためスキップされました。")
            else:
                print("\n✨✨✨✨✨ すべてのIDの更新が完了しました ✨✨✨✨✨")

            # 画像書き込み処理
            apply_poke_graphics_cache()

def do_download(row, current_id):
    species = row.get("original_name_code")
    
    # 1. カスタム設定があるか確認
    if species in CUSTOM_FOLDER_MAP:
        target_pokemon_folder = CUSTOM_FOLDER_MAP[species]
    else:
        # 2. 通常の自動フォルダ分けロジック
        name_stripped = species.removeprefix("SPECIES_").lower()
        name_parts = name_stripped.split('_')
        
        if len(name_parts) >= 2:
            # 「treecko_mega_x」だと"treecko/mega_x"になるらしい
            target_pokemon_folder = os.path.join(name_parts[0], "_".join(name_parts[1:]))
        else:
            # 「treecko」のように単語が1つだけならそのままフォルダ名にする
            target_pokemon_folder = name_stripped

    # ----------- 画像ダウンロード処理の中身 ---------
    success_download_sprite = True
    success_download_icon   = True

    # 【重要な仕様変更の理由】
    # この関数はマルチスレッド（ThreadPoolExecutor）で同時に何件も並列処理されます。
    # 各スレッドから同時に「poke_graphics_cache」や実ファイルへ書き込み（追加）を行うと、
    # データの衝突が起きてキャッシュが壊れたり、保存が失敗したりするリスク（スレッドセーフではない問題）があります。
    # そのため、この関数の中では書き込みを一切行わず、「ダウンロードした生データ（バイナリ）」を
    # そのまま親関数（メインスレッド）へ持ち帰り、外側で安全にキャッシュへ書き込む仕様にしています。
    sprite_bytes = None
    icon_bytes   = None

    # --- スプライト処理 ---
    if UPDATE_SPRITES:
        sprite_url = row.get("sprite_url")
        if not sprite_url:
            print(f"⚠️ [ID: {current_id}] スプライトURLが空です。")
            success_download_sprite = False
        else:
            try:
                response = requests.get(sprite_url, timeout=10)
                response.raise_for_status()
                sprite_bytes = response.content
                
                # 画像データとして正常に開けるか事前に検証します
                with Image.open(io.BytesIO(sprite_bytes)) as img:
                    img.verify()
            except requests.exceptions.RequestException as e:
                print(f"❌ [ID: {current_id}] スプライトの通信エラーが発生しました。\n   URL: {sprite_url}\n   エラー: {e}")
                success_download_sprite = False
            except Exception as e:
                # HTTPは成功したものの、データが壊れているか、画像以外のデータ（HTMLなど）が混入している場合
                preview = sprite_bytes[:100] if sprite_bytes else b""
                print(f"❌ [ID: {current_id}] スプライトの画像データが不正です。画像として解釈できません。\n   URL: {sprite_url}\n   エラー詳細: {e}\n   データ冒頭(100bytes): {preview}")
                success_download_sprite = False

    # --- アイコン処理 ---
    if UPDATE_ICONS:
        icon_url = row.get("icon_url")
        if not icon_url:
            print(f"⚠️ [ID: {current_id}] アイコンURLが空です。")
            success_download_icon = False
        else:
            try:
                response = requests.get(icon_url, timeout=10)
                response.raise_for_status()
                icon_bytes = response.content
                
                # 画像データとして正常に開けるか事前に検証します
                with Image.open(io.BytesIO(icon_bytes)) as img:
                    img.verify()
            except requests.exceptions.RequestException as e:
                print(f"❌ [ID: {current_id}] アイコンの通信エラーが発生しました。\n   URL: {icon_url}\n   エラー: {e}")
                success_download_icon = False
            except Exception as e:
                # HTTPは成功したものの、データが壊れているか、画像以外のデータ（HTMLなど）が混入している場合
                preview = icon_bytes[:100] if icon_bytes else b""
                print(f"❌ [ID: {current_id}] アイコンの画像データが不正です。画像として解釈できません。\n   URL: {icon_url}\n   エラー詳細: {e}\n   データ冒頭(100bytes): {preview}")
                success_download_icon = False
    
    return current_id, success_download_sprite, success_download_icon, target_pokemon_folder, sprite_bytes, icon_bytes

def write_jasc_pal(rel_dir, filename, palette_list):
    rel_path = os.path.join(rel_dir, filename)
    buf = io.BytesIO()
    buf.write(b"JASC-PAL\n0100\n16\n")
    for r, g, b in palette_list:
        buf.write(f"{r} {g} {b}\n".encode("ascii"))
    poke_graphics_cache[rel_path] = buf.getvalue()

def process_and_sync_poke_sprites(img_raw, rel_dir, current_id):
    if img_raw.mode == 'P':
        palette_data = img_raw.getpalette()
        num_colors = len(palette_data) // 3 if palette_data else 0
    else:
        used_colors = img_raw.getcolors(maxcolors=256)
        num_colors = len(used_colors) if used_colors else 0
    
    if num_colors == 32 and img_raw.mode == 'P':
        print("PALETTE : 32色背景0番補正実行")
        full_pal = img_raw.getpalette() 
        bg_idx_n = img_raw.getpixel((0, 0))   
        bg_idx_s = img_raw.getpixel((64, 0))  
        pal_n_list = [tuple(full_pal[i:i+3]) for i in range(0, 48, 3)]
        pal_s_list = [tuple(full_pal[i:i+3]) for i in range(48, 96, 3)]
        actual_bg_n_color = pal_n_list[bg_idx_n]
        original_zero_n_color = pal_n_list[0]
        pal_n_list[0] = actual_bg_n_color
        pal_n_list[bg_idx_n] = original_zero_n_color
        bg_s_rel = bg_idx_s - 16
        actual_bg_s_color = pal_s_list[bg_s_rel]
        original_zero_s_color = pal_s_list[0]
        pal_s_list[0] = actual_bg_s_color
        pal_s_list[bg_s_rel] = original_zero_s_color
        parts = []
        for i in range(min(5, (img_raw.width // 64))):
            part = img_raw.crop((i * 64, 0, (i + 1) * 64, 64))
            is_shiny = (i % 2 == 1)
            lut = list(range(256))
            if not is_shiny:
                lut[bg_idx_n] = 0
                lut[0] = bg_idx_n
            else:
                for p in range(16, 32):
                    rel_p = p - 16
                    if rel_p == bg_s_rel: lut[p] = 0
                    elif rel_p == 0: lut[p] = bg_s_rel
                    else: lut[p] = rel_p
            part = part.point(lut)
            current_pal = pal_s_list if is_shiny else pal_n_list
            flat_pal = []
            for rgb in current_pal: flat_pal.extend(rgb)
            part.putpalette(flat_pal + ([0] * (768 - 48)))
            parts.append(part)
        if len(parts) >= 5:
            f_n_final = parts[0]
            f_anim_final = parts[4]  # 5枚目があるならアニメ用パーツを使う
            b_s_final = parts[3]
        else:
            f_n_final = parts[0]
            f_anim_final = parts[0]  # ないなら通常パーツを複製して使う（既存の挙動）
            b_s_final = parts[3]
        pal_n_out, pal_s_out = pal_n_list, pal_s_list
    else:
        process_msg = "通常ペアリング処理"
        img_rgba = img_raw.convert("RGBA")
        f_n = img_rgba.crop((0, 0, 64, 64)); f_s = img_rgba.crop((64, 0, 128, 64))
        b_n = img_rgba.crop((128, 0, 192, 64)); b_s = img_rgba.crop((192, 0, 256, 64))
        def get_bg(img):
            px = img.getpixel((0, 0))
            return px[:3] if px[3] > 0 else (0, 120, 120)
        bg_n, bg_s = get_bg(f_n), get_bg(f_s)
        pal_n, pal_s = [bg_n], [bg_s]
        color_to_idx = {}
        def build_indices(img_n, img_s):
            data_n, data_s = list(img_n.getdata()), list(img_s.getdata())
            local_indices = []
            for p_n, p_s in zip(data_n, data_s):
                rgb_n, rgb_s = p_n[:3], p_s[:3]
                if p_n[3] == 0 or rgb_n == bg_n:
                    local_indices.append(0); continue
                combo = (rgb_n, rgb_s)
                if combo not in color_to_idx:
                    if len(pal_n) < 16:
                        idx = len(pal_n); color_to_idx[combo] = idx
                        pal_n.append(rgb_n); pal_s.append(rgb_s)
                        local_indices.append(idx)
                    else: local_indices.append(0)
                else: local_indices.append(color_to_idx[combo])
            return local_indices
        indices_f = build_indices(f_n, f_s)
        indices_b = build_indices(b_n, b_s)
        while len(pal_n) < 16: pal_n.append((0, 0, 0))
        while len(pal_s) < 16: pal_s.append((0, 0, 0))
        def make_p_img(indices, palette, size):
            img = Image.new("P", size)
            flat_pal = []
            for rgb in palette: flat_pal.extend(rgb)
            img.putpalette(flat_pal)
            img.putdata(indices)
            return img
        f_n_final = make_p_img(indices_f, pal_n, (64, 64))
        b_s_final = make_p_img(indices_b, pal_s, (64, 64))
        pal_n_out, pal_s_out = pal_n, pal_s
    write_jasc_pal(rel_dir, "normal.pal", pal_n_out)
    write_jasc_pal(rel_dir, "shiny.pal", pal_s_out)

    if 'f_anim_final' not in locals():
        f_anim_final = f_n_final
    anim_img = Image.new("P", (64, 128))
    anim_img.putpalette(f_n_final.getpalette())
    anim_img.paste(f_n_final, (0, 0))
    anim_img.paste(f_anim_final, (0, 64))
    
    # BytesIOを使ってキャッシュに保存
    buf_anim = io.BytesIO()
    anim_img.save(buf_anim, format="PNG")
    poke_graphics_cache[os.path.join(rel_dir, "anim_front.png")] = buf_anim.getvalue()
    
    buf_back = io.BytesIO()
    b_s_final.save(buf_back, format="PNG")
    poke_graphics_cache[os.path.join(rel_dir, "back.png")] = buf_back.getvalue()

def cache_species_info_files():
    # オリジナルデータフォルダのspecies_info内の全ファイルを一括（キャッシュ化）
    if os.path.exists(ORIGINAL_SPECIES_INFO_DIR):
        print(f"📦 ORIGINAL_POKEDATAのspecies_infoをメモリにキャッシュ中...\n📁({ORIGINAL_SPECIES_INFO_DIR})")
        for root, _, files in os.walk(ORIGINAL_SPECIES_INFO_DIR):
            for file_name in files:
                if file_name.endswith('.h'):
                    # rootには/Users/yu/Desktop/Original_expantion_data/PokeData/species_info/までが入ってる
                    file_full_path = os.path.join(root, file_name)

                    with open(file_full_path, "r", encoding="utf-8", errors="ignore") as cache_file_gen_x_families_h:
                        cache_gen_x_families_h_files[file_name] = cache_file_gen_x_families_h.read()
        print(f"✅ キャッシュ完了: {len(cache_gen_x_families_h_files)} ファイル")
    else:
        print(f"⚠️ {ORIGINAL_SPECIES_INFO_DIR} が見つからないため、種族情報の編集処理は開始できませんでした。")
    return

def cache_moves_file():
    global cache_moves_file_content
    if os.path.exists(ORIGINAL_MOVES_FILE_PATH):
        print(f"📦 ORIGINAL_MOVES_FILEをメモリにキャッシュ中...\n📁({ORIGINAL_MOVES_FILE_PATH})")
        with open(ORIGINAL_MOVES_FILE_PATH, "r", encoding="utf-8", errors="ignore") as moves_file_object:
            cache_moves_file_content = moves_file_object.read()
        print("✅ キャッシュ完了: 修得技ファイル")
    else:
        print(f"⚠️ {ORIGINAL_MOVES_FILE_PATH} が見つからないため、修得技ファイルのキャッシュに失敗しました。")

def stop_task():
    print(f"❌ 問題が発生したため処理を中止しました。")
    sys.exit(1)


# ------------ 種族情報を上書きする処理ここから ---------------
def update_species_info():

    target_files_path = set()
    changed_pokemon_logs = {}
    failed_types = []

    print("\n" + "✨" * 40)
    if UPDATE_DISPLAY_NAME:
        print("     表示名の上書き処理を開始します")
    if UPDATE_ICON_PALS:
        print("     pal番号の上書き処理を開始します")
    if UPDATE_TYPE:
        print("     typeの上書き処理を開始します")
    if UPDATE_HOLDITEMS:
        print("     所持アイテム（itemCommon/itemRare）の上書き処理を開始します")
    if UPDATE_ABILITIES:
        print("     abilitiesの上書き処理を開始します")
    if UPDATE_STATUS:
        print("     種族値（ステータス）の上書き処理を開始します")
    if UPDATE_DESCRIPTIONS:
        print("     dex_descriptionの上書き処理を開始します")
    if UPDATE_EVOLUTIONS:
        print("     evolutionsの上書き処理を開始します")
    if UPDATE_B_SPRITE_OFFSET:
        print("     戦闘画面のポケモン画像の位置の値の上書き処理を開始します")
    print("✨" * 40 + "\n")

    for poke_id, row in task_dict.items():
        pal                         = row["pal"]
        raw_species_name            = row["original_name_code"]
        type_raw                    = row["type"].strip()
        csv_item_common             = row["itemCommon"].strip()
        csv_item_rare               = row["itemRare"].strip()
        csv_display_name            = row["display_name"].strip()
        csv_abilities               = row["abilities"].strip()
        csv_dex_description         = row["dex_description"].strip()
        csv_evolution_requirements  = row["evo_requirements"].strip()
        csv_hp_status               = row["HP"].strip()
        csv_atk_status              = row["ATK"].strip()
        csv_def_status              = row["DEF"].strip()
        csv_satk_status             = row["SATK"].strip()
        csv_sdef_status             = row["SDEF"].strip()
        csv_spd_status              = row["SPD"].strip()

        # 空のカラム名を特定してリスト化
        missing_status_columns = []
        if not csv_hp_status:   missing_status_columns.append("HP")
        if not csv_atk_status:  missing_status_columns.append("ATK")
        if not csv_def_status:  missing_status_columns.append("DEF")
        if not csv_satk_status: missing_status_columns.append("SATK")
        if not csv_sdef_status: missing_status_columns.append("SDEF")
        if not csv_spd_status:  missing_status_columns.append("SPD")

        has_all_status_values = len(missing_status_columns) == 0

        # 値が空でスキップされた場合、どの項目の値が無かったかを警告ログに記録
        if UPDATE_STATUS and not has_all_status_values:
            failed_types.append(f"⚠️ ID:{poke_id} ({raw_species_name}) 種族値更新スキップ: 空のカラムがあります -> [{', '.join(missing_status_columns)}]")

        if UPDATE_TYPE:
            types = [t.strip().upper() for t in type_raw.split(",")] # pythonが読み取れる形にする。配列形式にする
            if not all(t in ALLOWED_TYPES for t in types):           # csvの中身のタイプを小分けにしてALLOWED_TYPESで文字確認してる
                failed_types.append(f"ID:{poke_id} → ({type_raw}) 許可せれてないタイプです。誤字がないか確認してください")        # バリデートして引っかかったやつログに書き出し
                stop_task()

            if len(types) == 1:
                output_type = f"MON_TYPES(TYPE_{types[0]})"
            else:
                output_type = f"MON_TYPES(TYPE_{types[0]}, TYPE_{types[1]})"

        if UPDATE_B_SPRITE_OFFSET:
            backPicOffset    = row["backPicYOffset"].strip()
            frontPicOffset   = row["frontPicYOffset"].strip()
            elevation        = row["enemyMonElevation"].strip()
            shadow_raw       = row["Shadow"].strip()   # "0, 0, SHADOW_SIZE_NONE"
            fixed_shadow_raw = shadow_raw.replace("SHADOW_SIZE_XL", "SHADOW_SIZE_XL_BATTLE_ONLY")
            shadow_parts     = fixed_shadow_raw.split(",")   # ['0', ' 0', ' SHADOW_SIZE_NONE']
            shadow_size      = shadow_parts[2].strip() # SHADOW_SIZE_NONE

                
        found = False
        start_marker = f"[{raw_species_name}]" # 検索対象のブロック開始文字列

        # ファイル単位でgen_1_families.h単位で回してる
        for cache_gen_x_file_name, cache_gen_x_content in cache_gen_x_families_h_files.items():
            if start_marker not in cache_gen_x_content: continue # そのポケモンがファイルの中に書かれてるか
            
            # 1. まず該当種族のブロック範囲を特定する
            # 行ベースで分割し、[SPECIES_...] から } までを範囲とする
            lines = cache_gen_x_content.splitlines()

            # 事前にこのポケモンのブロック内に .evolutions = が存在するかチェック
            has_evolution_in_species_block = False
            species_block_start_line_index = -1

            for line_index, line_content in enumerate(lines):
                if start_marker in line_content:
                    species_block_start_line_index = line_index
                    break

            if species_block_start_line_index != -1:
                for line_content in lines[species_block_start_line_index:]:
                    if line_content.strip().startswith("},"):
                        break
                    if ".evolutions =" in line_content:
                        has_evolution_in_species_block = True
                        break

            new_lines                         = []
            in_block                          = False
            replaced_type                     = False
            replaced_hold_items               = False
            found_types_for_items             = False
            old_item_common                   = "(なし)"
            old_item_rare                     = "(なし)"
            replaced_pal                      = False
            replaced_abilities                = False
            found_abilities_in_block          = False
            replaced_status                   = False
            found_hp_status                   = False
            found_atk_status                  = False
            found_def_status                  = False
            found_spd_status                  = False
            found_satk_status                 = False
            found_sdef_status                 = False
            has_replaced_evolution            = False
            replaced_description              = False
            is_inside_description_block       = False
            is_inside_evolution_block         = False
            evolution_parenthesis_depth       = 0
            evolution_preprocessor_depth      = 0
            replaced_offset                   = False
            found_back_pic_for_elevation      = False
            elevation_handled                 = False
            cleaned_description               = csv_dex_description.replace('""', '').strip()
            has_compound_string_description   = False
            
            for line in lines:

                # lstrip() で左側の空白を削除した文字列の長さを元と比較して、インデントの長さを特定
                indent = line[:len(line) - len(line.lstrip())]
                
                if start_marker in line:
                    in_block = True
                    elevation_handled = False

                    # 対象種族ブロック内に存在する既存のアイテム値（旧値）を事前に取得
                    if species_block_start_line_index != -1:
                        for check_line in lines[species_block_start_line_index:]:
                            if check_line.strip().startswith("},"):
                                break
                            if ".itemCommon" in check_line and "=" in check_line:
                                match_result = re.search(r"=\s*(.*?)\s*,", check_line)
                                if match_result:
                                    old_item_common = match_result.group(1).strip()
                            if ".itemRare" in check_line and "=" in check_line:
                                match_result = re.search(r"=\s*(.*?)\s*,", check_line)
                                if match_result:
                                    old_item_rare = match_result.group(1).strip()

                    # この種族ブロック内に .description = COMPOUND_STRING( が存在するか事前に確認
                    has_compound_string_description = False
                    if species_block_start_line_index != -1:
                        for check_line in lines[species_block_start_line_index:]:
                            if check_line.strip().startswith("},"):
                                break
                            if ".description = COMPOUND_STRING(" in check_line:
                                has_compound_string_description = True
                                break

                if in_block:
                    old_value = "(空白)"
                    # ログ出力
                    if raw_species_name not in changed_pokemon_logs:
                        changed_pokemon_logs[raw_species_name] = []
                        changed_pokemon_logs[raw_species_name].append(f"ID           : {poke_id}")

                    # --- 進化（.evolutions）ブロック削除・通過の処理 (パターンB対応) ---
                    if is_inside_evolution_block:
                        if line.strip().startswith(".") or line.strip().startswith("},"):
                            is_inside_evolution_block = False
                        else:
                            stripped_line = line.strip()
                            if stripped_line.startswith("#if"):
                                evolution_preprocessor_depth += 1
                            elif stripped_line.startswith("#endif"):
                                evolution_preprocessor_depth = max(0, evolution_preprocessor_depth - 1)

                            evolution_parenthesis_depth += line.count("(") - line.count(")")

                            if evolution_parenthesis_depth <= 0 and evolution_preprocessor_depth == 0:
                                is_inside_evolution_block = False
                            continue

                     # --- 説明文（.description）ブロック削除・通過の処理 ---
                    if is_inside_description_block:
                        stripped_line = line.strip()
                        # 安全装置: 次のプロパティ(.)や構造体の終わり(})に到達した場合は強制的にブロックを抜ける
                        if stripped_line.startswith(".") or stripped_line.startswith("}"):
                            is_inside_description_block = False
                        elif ")" in stripped_line:
                            is_inside_description_block = False
                            continue
                        else:
                            continue

                    # 種族名の変更
                    if UPDATE_DISPLAY_NAME and ".speciesName" in line:
                        search_result = re.search(r"=\s*(.*?)\s*,", line)
                        old_value = search_result.group(1)
                        line = f'{indent}.speciesName = _("{csv_display_name}"),'
                        new_lines.append(line)
                        changed_pokemon_logs[raw_species_name].append(f"DISPLAY_NAME : {old_value} →  {csv_display_name}")
                        replaced_pal = True
                        continue

                    # iconパレット番号の変更
                    if UPDATE_ICON_PALS and ".iconPalIndex" in line:
                        search_result = re.search(r"=\s*(.*?)\s*,", line)
                        old_value = search_result.group(1)
                        line = f"{indent}.iconPalIndex = {pal},"
                        new_lines.append(line)
                        changed_pokemon_logs[raw_species_name].append(f"ICON_PAL     : {old_value} →  {pal}")
                        replaced_pal = True
                        continue

                    # タイプの変更とアイテム変更
                    if ".types" in line:
                        if UPDATE_TYPE:
                            search_result = re.search(r"MON_TYPES\((.*?)\)", line)
                            old_value = search_result.group(1)
                            line = f"{indent}.types = {output_type},"
                            new_lines.append(line)
                            changed_pokemon_logs[raw_species_name].append(f"TYPE         : {old_value} →  {type_raw}")
                            replaced_type = True
                        else:
                            new_lines.append(line)

                        # 所持アイテム（itemCommon / itemRare）を .types の直下に追加
                        if UPDATE_HOLDITEMS and (csv_item_common or csv_item_rare):
                            found_types_for_items = True
                            if csv_item_common:
                                new_lines.append(f"{indent}.itemCommon = {csv_item_common},")
                                changed_pokemon_logs[raw_species_name].append(f"ITEM_COMMON  : {old_item_common} →  {csv_item_common}")
                            if csv_item_rare:
                                new_lines.append(f"{indent}.itemRare = {csv_item_rare},")
                                changed_pokemon_logs[raw_species_name].append(f"ITEM_RARE    : {old_item_rare} →  {csv_item_rare}")
                            replaced_hold_items = True
                        continue

                    # 既存の所持アイテム行（.itemCommon / .itemRare）を削除（スキップ）
                    if UPDATE_HOLDITEMS and (csv_item_common or csv_item_rare):
                        if ".itemCommon" in line and "=" in line:
                            continue
                        if ".itemRare" in line and "=" in line:
                            continue

                    # 特性変更
                    # If文で世代によってabilitiesが何個もパターンがあるがそういうパターンは全部csvに上書きさせる
                    # だからログでABILITYが二回以上表示されるが想定内の挙動である
                    if UPDATE_ABILITIES and ".abilities" in line:
                        search_result = re.search(r"=\s*(.*?)$", line)
                        old_value = search_result.group(1) if search_result else line.strip()
                        line = f"{indent}{csv_abilities}"
                        new_lines.append(line)
                        changed_pokemon_logs[raw_species_name].append(f"ABILITIES    : {old_value} →  {csv_abilities}")
                        replaced_abilities = True
                        found_abilities_in_block = True
                        continue

                     # ステータス（種族値）の変更
                    if UPDATE_STATUS and has_all_status_values:
                        if ".baseHP" in line and "=" in line:
                            search_result = re.search(r"=\s*(.*?)\s*,", line)
                            old_value = search_result.group(1) if search_result else ""
                            line = f"{indent}.baseHP        = {csv_hp_status},"
                            new_lines.append(line)
                            changed_pokemon_logs[raw_species_name].append(f"HP           : {old_value} →  {csv_hp_status}")
                            found_hp_status = True
                            replaced_status = True
                            continue

                        if ".baseAttack" in line and "=" in line:
                            search_result = re.search(r"=\s*(.*?)\s*,", line)
                            old_value = search_result.group(1) if search_result else ""
                            line = f"{indent}.baseAttack    = {csv_atk_status},"
                            new_lines.append(line)
                            changed_pokemon_logs[raw_species_name].append(f"ATK          : {old_value} →  {csv_atk_status}")
                            found_atk_status = True
                            replaced_status = True
                            continue

                        if ".baseDefense" in line and "=" in line:
                            search_result = re.search(r"=\s*(.*?)\s*,", line)
                            old_value = search_result.group(1) if search_result else ""
                            line = f"{indent}.baseDefense   = {csv_def_status},"
                            new_lines.append(line)
                            changed_pokemon_logs[raw_species_name].append(f"DEF          : {old_value} →  {csv_def_status}")
                            found_def_status = True
                            replaced_status = True
                            continue

                        if ".baseSpeed" in line and "=" in line:
                            search_result = re.search(r"=\s*(.*?)\s*,", line)
                            old_value = search_result.group(1) if search_result else ""
                            line = f"{indent}.baseSpeed     = {csv_spd_status},"
                            new_lines.append(line)
                            changed_pokemon_logs[raw_species_name].append(f"SPD          : {old_value} →  {csv_spd_status}")
                            found_spd_status = True
                            replaced_status = True
                            continue

                        if ".baseSpAttack" in line and "=" in line:
                            search_result = re.search(r"=\s*(.*?)\s*,", line)
                            old_value = search_result.group(1) if search_result else ""
                            line = f"{indent}.baseSpAttack  = {csv_satk_status},"
                            new_lines.append(line)
                            changed_pokemon_logs[raw_species_name].append(f"SATK         : {old_value} →  {csv_satk_status}")
                            found_satk_status = True
                            replaced_status = True
                            continue

                        if ".baseSpDefense" in line and "=" in line:
                            search_result = re.search(r"=\s*(.*?)\s*,", line)
                            old_value = search_result.group(1) if search_result else ""
                            line = f"{indent}.baseSpDefense = {csv_sdef_status},"
                            new_lines.append(line)
                            changed_pokemon_logs[raw_species_name].append(f"SDEF         : {old_value} →  {csv_sdef_status}")
                            found_sdef_status = True
                            replaced_status = True
                            continue

                    # 説明文（.description）の変更
                    if UPDATE_DESCRIPTIONS and cleaned_description:
                        # 優先順位1: .description = COMPOUND_STRING( 形式が存在する場合はそれを最優先で上書き（複数行置換）
                        if has_compound_string_description and ".description = COMPOUND_STRING(" in line:
                            replaced_description = True
                            is_inside_description_block = True
                            
                            split_description_lines = re.split(r'\\n|\n', cleaned_description)
                            formatted_description_lines = [l.strip(' "') for l in split_description_lines if l.strip(' "')]
                            
                            new_lines.append(f"{indent}.description = COMPOUND_STRING(")
                            for line_index, description_line_text in enumerate(formatted_description_lines):
                                if line_index < len(formatted_description_lines) - 1:
                                    new_lines.append(f'{indent}    "{description_line_text}\\n"')
                                else:
                                    new_lines.append(f'{indent}    "{description_line_text}"),')
                            
                            changed_pokemon_logs[raw_species_name].append(f"DESCRIPTION  : 更新")
                            
                            if ")" in line:
                                is_inside_description_block = False
                            continue

                        # 優先順位2: COMPOUND_STRING( が無い場合のみ、.description = (gPichuPokedexText等の単一行) を上書き
                        elif not has_compound_string_description and ".description =" in line:
                            replaced_description = True
                            
                            split_description_lines = re.split(r'\\n|\n', cleaned_description)
                            formatted_description_lines = [l.strip(' "') for l in split_description_lines if l.strip(' "')]
                            
                            new_lines.append(f"{indent}.description = COMPOUND_STRING(")
                            for line_index, description_line_text in enumerate(formatted_description_lines):
                                if line_index < len(formatted_description_lines) - 1:
                                    new_lines.append(f'{indent}    "{description_line_text}\\n"')
                                else:
                                    new_lines.append(f'{indent}    "{description_line_text}"),')
                            
                            changed_pokemon_logs[raw_species_name].append(f"DESCRIPTION  : 更新")
                            continue

                    # 進化（.evolutions）の変更・置換処理
                    if UPDATE_EVOLUTIONS and ".evolutions =" in line:
                        has_replaced_evolution = True
                        is_inside_evolution_block = True
                        evolution_parenthesis_depth = line.count("(") - line.count(")")
                        evolution_preprocessor_depth = 0

                        if line.strip().startswith("#if"):
                            evolution_preprocessor_depth += 1

                        if csv_evolution_requirements == "NO_EVOLUTION":
                            changed_pokemon_logs[raw_species_name].append(f"EVOLUTIONS   : 既存の進化データを削除")
                            if evolution_parenthesis_depth <= 0 and evolution_preprocessor_depth == 0:
                                is_inside_evolution_block = False
                            continue
                        else:
                            line = f"{indent}.evolutions = EVOLUTION({{{csv_evolution_requirements}}}),"
                            new_lines.append(line)
                            changed_pokemon_logs[raw_species_name].append(f"EVOLUTIONS   : 更新")
                            if evolution_parenthesis_depth <= 0 and evolution_preprocessor_depth == 0:
                                is_inside_evolution_block = False
                            continue

                    # .evolutions が元から存在しない場合、.levelUpLearnset の直下に追加する処理
                    elif UPDATE_EVOLUTIONS and not has_evolution_in_species_block and csv_evolution_requirements != "NO_EVOLUTION" and ".levelUpLearnset" in line:
                        new_lines.append(line)
                        new_lines.append(f"{indent}.evolutions = EVOLUTION({{{csv_evolution_requirements}}}),")
                        changed_pokemon_logs[raw_species_name].append(f"EVOLUTIONS   : .levelUpLearnset の下に新規追加")
                        has_replaced_evolution = True
                        has_evolution_in_species_block = True
                        continue

                    # 戦闘画面の画像の位置の変更
                    if UPDATE_B_SPRITE_OFFSET:
                        if ".backPicYOffset" in line and "=" in line:
                            search_result = re.search(r"=\s*(.*?)\s*,", line)
                            old_value = search_result.group(1)
                            line = f"{indent}.backPicYOffset = {backPicOffset},"
                            new_lines.append(line)
                            changed_pokemon_logs[raw_species_name].append(f"BACK_Y       : {old_value} →  {backPicOffset}")
                            continue
                        if ".frontPicYOffset" in line and "=" in line:
                            search_result = re.search(r"=\s*(.*?)\s*,", line)
                            old_value = search_result.group(1)
                            line = f"{indent}.frontPicYOffset = {frontPicOffset},"
                            new_lines.append(line)
                            changed_pokemon_logs[raw_species_name].append(f"FRONT_Y      : {old_value} →  {frontPicOffset}")
                            continue
                        # まず既存のenemyMonElevationの処理をまっさらの状態にする
                        if ".enemyMonElevation" in line:
                            search_result = re.search(r"=\s*(.*?)\s*,", line)
                            old_value = search_result.group(1)
                            continue
                        if ".backPic =" in line: #.backPicの下の行に追加する
                            if elevation != "0":
                                new_lines.append(f"{indent}.enemyMonElevation = {elevation},")
                                new_lines.append(line)
                                changed_pokemon_logs[raw_species_name].append(f"ELEV         : {old_value} →  {elevation}")
                            else:
                                new_lines.append(line)
                                changed_pokemon_logs[raw_species_name].append(f"ELEV         : {old_value} →  (空白)")
                            continue
                        
                        # まずは既存のSHADOWの処理をまっさらの状態にする
                        if "NO_SHADOW" in line:
                            continue
                        if "SHADOW" in line and "(" in line:
                            continue
                        if ".pokemonJumpType" in line:
                            new_lines.append(line) # まず .pokemonJumpType の行を追加
                            if shadow_size == "SHADOW_SIZE_NONE":
                                new_lines.append(f"{indent}NO_SHADOW")
                            else:
                                new_lines.append(f"{indent}SHADOW({fixed_shadow_raw})")
                            replaced_offset = True
                            continue

                    # ブロック終了条件 (行末が },)
                    if line.strip().startswith("},"):
                        in_block = False

                new_lines.append(line)

            replaced_in_this_file = replaced_type or replaced_pal or replaced_offset or replaced_abilities or has_replaced_evolution or replaced_description or replaced_status or replaced_hold_items

            if replaced_in_this_file:
                cache_gen_x_families_h_files[cache_gen_x_file_name] = "\n".join(new_lines)
                file_full_path = os.path.join(CURRENT_SPECIES_INFO_DIR, cache_gen_x_file_name)
                target_files_path.add(file_full_path)
                
                changed_pokemon_logs[raw_species_name].append("-" * 40)

                if UPDATE_HOLDITEMS and (csv_item_common or csv_item_rare) and not found_types_for_items:
                    failed_types.append(f"⚠️ ID:{poke_id} ({raw_species_name}) 対象ブロック内に `.types =` の行が見つからなかったため所持アイテムを更新できませんでした。")
                if UPDATE_ABILITIES and not found_abilities_in_block:
                    failed_types.append(f"⚠️ ID:{poke_id} ({raw_species_name}) 対象ブロック内に `.abilities =` の行が見つかりませんでした。")
                if UPDATE_STATUS and has_all_status_values:
                    if not (found_hp_status and found_atk_status and found_def_status and found_spd_status and found_satk_status and found_sdef_status):
                        failed_types.append(f"⚠️ ID:{poke_id} ({raw_species_name}) 対象ブロック内に一部のステータス項目 (.baseHP 等) が見つかりませんでした。")
                if UPDATE_EVOLUTIONS and csv_evolution_requirements != "NO_EVOLUTION" and not has_replaced_evolution:
                    failed_types.append(f"⚠️ ID:{poke_id} ({raw_species_name}) 進化情報を追加しようとしましたが `.evolutions =` も `.levelUpLearnset` も見つかりませんでした。")
                if UPDATE_DESCRIPTIONS and cleaned_description and not replaced_description:
                    failed_types.append(f"⚠️ ID:{poke_id} ({raw_species_name}) 対象ブロック内に `.description = COMPOUND_STRING(` の行が見つかりませんでした。")

                found = True
                break
                
        if not found:
            failed_types.append(f"ID:{poke_id} ({raw_species_name} のデータ行が見つかりませんでした)")
# ------------ 種族値を上書きする処理ここまで ---------------

# ------------------------------------------------------------------ ルート処理終了 ------------------------------------------------------------------ #

    # 書き戻し（差分のみ、または変更があったものを現行プロジェクトフォルダーへ適用）
    if target_files_path:
        print(f"\n💾 変更を適用中...")
        updated_files_count = 0
        
        for target_file_path in target_files_path:
            file_name = os.path.basename(target_file_path)
            
            # 辞書を順番にチェックして、該当するデータを見つける
            new_content = None
            if file_name in cache_gen_x_families_h_files:
                new_content = cache_gen_x_families_h_files[file_name]

            if new_content is None:
                continue # データが見つからなければスキップ

            # 差分チェックと書き込み
            needs_write = True
            if os.path.exists(target_file_path):
                with open(target_file_path, "r", encoding="utf-8", errors="ignore") as current_file:
                    if current_file.read() == new_content:
                        needs_write = False
            
            if needs_write:
                with open(target_file_path, "w", encoding="utf-8") as current_file:
                    current_file.write(new_content)
                updated_files_count += 1
                print(f"  📝 適用: {file_name}")

        if changed_pokemon_logs:
            print(f"\n✨ 変更されたポケモン一覧:")
            for pokemon, logs in changed_pokemon_logs.items():
                print(f"[{pokemon}]")
                for log in logs:
                    print(f"  - {log}")
                
        print(f"✅ テキストデータの適用完了: {updated_files_count} ファイルを更新しました。\n")
    
    # 最終報告セクション
    if failed_types:
        print(f"\n❌ 以下のTYPE指定が不正または見つからずスキップされました:\n" + "\n".join(failed_types))

# ------------ 種族値を上書きする処理ここまで ---------------


# ------------ 新機能: ANIM_FRONT 独立処理（pokemon.hパス書き換え） ------------
def update_sprite_file_path():
    if not UPDATE_ANIM_FRONT:
        return

    # 1. ORIGINAL_ANIM_FRONT_FILE_PATH をメモリに読み込む
    if not os.path.exists(ORIGINAL_ANIM_FRONT_FILE_PATH):
        print(f"⚠️ {ORIGINAL_ANIM_FRONT_FILE_PATH} が見つからないため、ANIM_FRONTの編集処理は開始できませんでした。")
        return

    with open(ORIGINAL_ANIM_FRONT_FILE_PATH, "r", encoding="utf-8", errors="ignore") as file_obj:
        content = file_obj.read()

    lines = content.splitlines()
    changed_logs = []
    failed_logs = []

    # 2. task_dict をループしてキャッシュ（lines）の対象行を書き換える
    for poke_id, row in task_dict.items():
        raw_species_name = row["original_name_code"]
        
        # SPECIES_XXX を PascalCase に整形
        base_name = raw_species_name.replace("SPECIES_", "")
        if base_name.startswith("SQUAWKABILLY_"):
            formatted_name = "Squawkabilly"
        else:
            formatted_name = "".join(word.capitalize() for word in base_name.split("_"))
        
        target_string = f"gMonFrontPic_{formatted_name}[]"
        
        # ファイル内に記述があるかチェック
        if target_string not in content:
            failed_logs.append(f"ID:{poke_id} ({target_string} の記述自体が見つかりませんでした)")
            continue

        replaced = False
        # 行ごとに走査して置換
        for idx, line in enumerate(lines):
            if target_string in line:
                new_line = line
                # 通常定義とGBA定義（front.png / front_gba.png）の双方に対応して置換を行う
                if "anim_front" in line:
                    pass
                elif "front.png" in line:
                    new_line = line.replace("front.png", "anim_front.png")
                
                if new_line != line:
                    lines[idx] = new_line
                    replaced = True

        if replaced:
            changed_logs.append(f"ANIM_FRONT : {formatted_name} (front.png -> anim_front.png に変更)")

    # すべて置換し終わったテキストを結合
    updated_content = "\n".join(lines) + "\n"

    # 3. CURRENT_ANIM_FRONT_SETTING_FILE_PATH と差分チェックして書き込む
    needs_write = True
    if os.path.exists(CURRENT_ANIM_FRONT_SETTING_FILE_PATH):
        with open(CURRENT_ANIM_FRONT_SETTING_FILE_PATH, "r", encoding="utf-8", errors="ignore") as current_file:
            if current_file.read() == updated_content:
                needs_write = False

    if needs_write:
        os.makedirs(os.path.dirname(CURRENT_ANIM_FRONT_SETTING_FILE_PATH), exist_ok=True)
        with open(CURRENT_ANIM_FRONT_SETTING_FILE_PATH, "w", encoding="utf-8") as current_file:
            current_file.write(updated_content)
        
        # 実際に変更（置換）があった場合のみ完了ログを出力
        if changed_logs:
            print("\n" + "✨" * 40)
            print("     anim_front.pngの適用完了ログ")
            print("✨" * 40 + "\n")
            for log in changed_logs:
                print(f"   {log}")
            print(f"\n💾 変更を適用しました: {os.path.basename(CURRENT_ANIM_FRONT_SETTING_FILE_PATH)}")
    else:
        print("\n💾 変更はありません (すでに最新の状態です)")

    if failed_logs:
        print(f"\n❌ 以下のANIM_FRONT指定で対象が見つからずスキップされました:\n" + "\n".join(failed_logs))

# ------------ ANIM_FRONT 独立処理ここまで ------------


# ------------------ 新機能: ID並び替え (species.h) ------------------
def sort_species_id():
    # 処理を実行するかどうかはUPDATE_ID_SORTがTrueの時のみ
    if not UPDATE_ID_SORT:
        return

    print("\n" + "✨" * 40)
    print("     種族ID (species.h) の並び替え処理を開始します")
    print("✨" * 40 + "\n")

    if not os.path.exists(CURRENT_SPECIES_ID_FILE_PATH):
        print(f"⚠️ {CURRENT_SPECIES_ID_FILE_PATH} が見つからないため、ID並び替え処理はスキップされます。")
        return

    # 1. species.h を直接読み込む
    with open(CURRENT_SPECIES_ID_FILE_PATH, "r", encoding="utf-8", errors="ignore") as file_obj:
        lines = file_obj.read().splitlines()

    # CSVのタスクIDを昇順にソートして処理する
    sorted_poke_ids = sorted(task_dict.keys())
    failed_sort_ids = []

    # フォーマットを整える内部関数
    def format_line(line_content):
        parts = line_content.split()
        if len(parts) < 3:
            return line_content
        # 既存のフォーマット規則に従い、インデント幅47で整える
        return f"{parts[0]} {parts[1]:<47} {parts[2]}"

    for poke_id in sorted_poke_ids:
        row = task_dict[poke_id]
        raw_species_name = row["original_name_code"] # targetとなる種族名

        # 毎ループで現在の lines からマッピング情報を再構築する（玉突きでインデックスや値が変わるため）
        poke_name_to_value_map = {}
        poke_name_to_line_index_map = {}
        
        for line_number, line_content in enumerate(lines):
            if line_content is None:
                continue
            # #define SPECIES_XXXX 値 のパターンにマッチさせる
            # SPECIES_PACHIRISU の部分を poke_name_code、417 などの値を poke_value とする
            match = re.match(r"^#define\s+(SPECIES_[A-Z0-9_]+)\s+([A-Z0-9_()+\s]+)", line_content)
            if match:
                poke_name_code, poke_value = match.groups()
                poke_value = poke_value.strip()
                poke_name_to_value_map[poke_name_code] = poke_value
                poke_name_to_line_index_map[poke_name_code] = line_number

        # グループ情報を取得する内部関数 (1段階エイリアスまで対応)
        # 変数名は省略せず、分かりやすく記述する
        def get_group_info(target_poke_name):
            poke_value = poke_name_to_value_map.get(target_poke_name)
            if not poke_value:
                return None

            # poke_valueが数字（ID）であれば、これが本体
            if re.match(r"^\d+$", poke_value):
                main_poke_name = target_poke_name
                main_poke_value = poke_value
            else:
                # poke_valueが文字列（エイリアス参照先）の場合、1段階先を探す
                main_poke_name = poke_value
                main_poke_value = poke_name_to_value_map.get(main_poke_name)
                # 1段階先が存在しない、または数字でない場合は非対応として弾く
                if not main_poke_value or not re.match(r"^\d+$", main_poke_value):
                    return None
            
            # 本体（main_poke_name）を参照しているエイリアスを全て取得してグループ化
            group_poke_names = [main_poke_name]
            for temp_poke_name, temp_poke_value in poke_name_to_value_map.items():
                if temp_poke_value == main_poke_name and temp_poke_name != main_poke_name:
                    group_poke_names.append(temp_poke_name)
            
            return group_poke_names, main_poke_name, main_poke_value

        # 2. 検索対象 (raw_species_name) の情報を取得
        target_info = get_group_info(raw_species_name)

        # poke_idに現在住んでいる人 (current_resident) の情報を取得
        current_resident_poke_name = None
        for temp_poke_name, temp_poke_value in poke_name_to_value_map.items():
            if temp_poke_value == str(poke_id):
                current_resident_poke_name = temp_poke_name
                break
        
        resident_info = get_group_info(current_resident_poke_name) if current_resident_poke_name else None

        # どちらかが見つからない、または2段階以上のエイリアスで None が返った場合はスキップ
        if not target_info or not resident_info:
            failed_sort_ids.append(poke_id)
            continue

        target_poke_names, target_main_name, target_main_value = target_info
        resident_poke_names, resident_main_name, resident_main_value = resident_info

        # 3. 入れ替え実行（スワップ）
        # 両グループとも「1行のみ」の場合は、既存のシンプルな名前入れ替えロジックを実行
        if len(target_poke_names) == 1 and len(resident_poke_names) == 1:
            line_index_1 = poke_name_to_line_index_map[resident_main_name]
            line_index_2 = poke_name_to_line_index_map[target_main_name]

            def swap_name(line_content, old_name, new_name):
                return re.sub(rf"(#define\s+){old_name}(\s+)", rf"\g<1>{new_name}\g<2>", line_content)

            lines[line_index_1] = swap_name(lines[line_index_1], resident_main_name, target_main_name)
            lines[line_index_2] = swap_name(lines[line_index_2], target_main_name, resident_main_name)

            lines[line_index_1] = format_line(lines[line_index_1])
            lines[line_index_2] = format_line(lines[line_index_2])

            print(f"   ID SORT  : {resident_main_name} <-> {target_main_name} を入れ替え")
        
        # グループ共有パターンが含まれる場合（行ごと入れ替えるロジック）
        else:
            # グループ内の元の行番号を昇順にソート（エイリアスと本元の並び順を崩さないため）
            resident_line_indices = sorted([poke_name_to_line_index_map[name] for name in resident_poke_names])
            target_line_indices = sorted([poke_name_to_line_index_map[name] for name in target_poke_names])

            # target_poke_names (raw_species_name側) は resident の場所へ移動。IDの数値は resident_main_value (poke_id) に更新。
            new_resident_block = []
            for name in sorted(target_poke_names, key=lambda x: poke_name_to_line_index_map[x]):
                line_content = lines[poke_name_to_line_index_map[name]]
                if name == target_main_name:
                    # 本体の行のみ、末尾の数値を置換する
                    line_content = re.sub(r"\s+\d+$", f" {resident_main_value}", line_content)
                new_resident_block.append(format_line(line_content))

            # resident_poke_names (poke_idの元の住人側) は target の場所へ移動。IDの数値は target_main_value に更新。
            new_target_block = []
            for name in sorted(resident_poke_names, key=lambda x: poke_name_to_line_index_map[x]):
                line_content = lines[poke_name_to_line_index_map[name]]
                if name == resident_main_name:
                    # 本体の行のみ、末尾の数値を置換する
                    line_content = re.sub(r"\s+\d+$", f" {target_main_value}", line_content)
                new_target_block.append(format_line(line_content))

            # 最も上の行にブロック（複数行まとめた文字列）を挿入
            lines[resident_line_indices[0]] = "\n".join(new_resident_block)
            lines[target_line_indices[0]] = "\n".join(new_target_block)

            # 残りの使わなくなった行は None にして後で詰める
            for line_index in resident_line_indices[1:] + target_line_indices[1:]:
                lines[line_index] = None

            # None の行を削除してリストをきれいに再構築
            temp_lines = []
            for line_content in lines:
                if line_content is None:
                    continue
                if "\n" in line_content:
                    temp_lines.extend(line_content.splitlines())
                else:
                    temp_lines.append(line_content)
            lines = temp_lines

            print(f"   ID SORT  : グループ {resident_main_name} <-> {target_main_name} を入れ替え")

    # 全てのソートが終わった後、1回のみ SPECIES_EGG の更新を行う
    egg_line_index = -1
    for line_number, line_content in enumerate(lines):
        if "#define SPECIES_EGG" in line_content:
            egg_line_index = line_number
            break

    if egg_line_index != -1:
        last_poke_id = 0
        # 5行前まで戻って数字を定義している直前の種族IDを探す
        for line_number in range(egg_line_index - 1, egg_line_index - 6, -1):
            if line_number < 0:
                break
            line_content = lines[line_number]
            match = re.match(r"^#define\s+SPECIES_[A-Z0-9_]+\s+(\d+)", line_content)
            if match:
                last_poke_id = int(match.group(1))
                break
        
        if last_poke_id > 0:
            # SPECIES_EGG の横はスペースを十分に確保してバグを防ぐ
            lines[egg_line_index] = f"#define SPECIES_EGG                                     ({last_poke_id} + 1)"
            print(f"✨ SPECIES_H: SPECIES_EGGを自動更新しました ({last_poke_id} + 1)")

    # 実ファイルに直接書き込む
    with open(CURRENT_SPECIES_ID_FILE_PATH, "w", encoding="utf-8") as file_obj:
        file_obj.write("\n".join(lines) + "\n")

    print("✅ species.h の並び替えと書き込みが完了しました。")

    if failed_sort_ids:
        print(f"\n❌ species.h 内に見つからずスキップされたID一覧:")
        print(f"FAILED_SORT_IDS = {sorted(list(set(failed_sort_ids)))}")


def update_national_dex_order():
    national_poke_code_names = []
    
    # 1. task_dict から対象データを取得・整形して配列に順次格納
    for poke_id, row in task_dict.items():
        original_name_code = row.get("original_name_code", "").strip()

        # 1. 例外マッピングに合致する場合はその値を使用して終了
        if original_name_code in NATIONAL_DEX_MAPPING:
            code_name = NATIONAL_DEX_MAPPING[original_name_code]
            
        # 2. 例外マッピングにない場合の処理
        else:
            # アンダースコアが2つ以上、または SWANNA ならスキップ
            if original_name_code.count("_") >= 2 or original_name_code == "SPECIES_SWANNA":
                continue

            # 通常のコード名生成（※elseのインデント内に記述します）
            if original_name_code.startswith("SPECIES_"):
                real_pokemon_name = original_name_code[len("SPECIES_"):]
            else:
                print(f"\n❌ {original_name_code} は SPECIES_ から始まっていません。")
                real_pokemon_name = original_name_code
                
            code_name = f"NATIONAL_DEX_{real_pokemon_name}"
            
        national_poke_code_names.append(code_name)

    if not national_poke_code_names:
        print("⚠️ 更新対象となるコード名がタスク内に存在しませんでした。")
        return

    # 2. 元の national pokedex ファイルを読み込む
    if not os.path.exists(ORIGINAL_NATIONAL_POKEDEX_FILE_PATH):
        print(f"❌ エラー: 元ファイルが見つかりません: {ORIGINAL_NATIONAL_POKEDEX_FILE_PATH}")
        return

    try:
        with open(ORIGINAL_NATIONAL_POKEDEX_FILE_PATH, "r", encoding="utf-8", errors="ignore") as f:
            original_lines = f.readlines()
    except Exception as e:
        print(f"❌ 元ファイルの読み込み中にエラーが発生しました: {e}")
        return

    # 3. 既存の行を走査し、追加対象（national_poke_code_names）と一致する行を除外
    cleaned_lines = []
    remove_set = set(national_poke_code_names)  # 検索の高速化

    for line in original_lines:
        # 行前後の余分な空白や、末尾のカンマを取り除いて比較
        cleaned_line_content = line.strip().rstrip(",")
        if cleaned_line_content in remove_set:
            continue  # 見つけたらappendせず次の行へ(実質削除)
        cleaned_lines.append(line)

    # 4. 「NATIONAL_DEX_NONE,」の行を探し、その直下に新しい並び順で挿入
    new_lines = []
    inserted = False

    for line in cleaned_lines:
        new_lines.append(line)
        
        # NATIONAL_DEX_NONE の行を検知し、まだ挿入していない場合に処理を実行
        if "NATIONAL_DEX_NONE" in line and not inserted:
            # 動的に行頭のインデント（スペースなどの空白）を取得
            indent = line[:len(line) - len(line.lstrip())]
            if not indent:
                indent = "    "  # 取得できない場合のデフォルト値
                
            # national_poke_code_names の順番通りに挿入
            for name in national_poke_code_names:
                new_lines.append(f"{indent}{name},\n")
            inserted = True

    new_content = "".join(new_lines)

    # 5. 現在のファイル（CURRENT_NATIONAL_DEX_FILE_PATH）と比較し、差分があれば書き出し
    needs_write = True
    if os.path.exists(CURRENT_NATIONAL_DEX_FILE_PATH):
        try:
            with open(CURRENT_NATIONAL_DEX_FILE_PATH, "r", encoding="utf-8", errors="ignore") as f:
                current_content = f.read()
            if current_content == new_content:
                needs_write = False
        except Exception as e:
            print(f"⚠️ 現在ファイルの読み込み中にエラーが発生したため、書き込みを継続します: {e}")

    if needs_write:
        try:
            # 保存先ディレクトリが存在しない場合は作成
            dest_dir = os.path.dirname(CURRENT_NATIONAL_DEX_FILE_PATH)
            if dest_dir and not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)

            with open(CURRENT_NATIONAL_DEX_FILE_PATH, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"📝 正常に {CURRENT_NATIONAL_DEX_FILE_PATH} を更新しました。")
        except Exception as e:
            print(f"❌ ファイルの更新に失敗しました: {e}")
    else:
        print("🔄 差分が存在しないため、ファイルの更新はスキップされました。")


# =======================================================================================
# プログラム起動口（メインブロック）
# =======================================================================================
if __name__ == "__main__":
    init()

    # 1. CSVを検証し、処理に必要な指定されたid of 行のみが入ったCSVのデータを抜き取る
    check_csv_n_create_tasks()
    cache_species_info_files()
    
    if UPDATE_MOVES:
        check_moves_csv_and_validate()
        cache_moves_file()

    if UPDATE_LEARNSET:
        check_learnset_csv_and_validate()
        cache_learnset_file()

    # 2. 準備したデータを使って、画像処理を行なっていく
    if UPDATE_SPRITES or UPDATE_ICONS:
        download_n_process_graphics()

    # 3. 種族情報更新ブロック
    if UPDATE_ICON_PALS or UPDATE_TYPE or UPDATE_B_SPRITE_OFFSET or UPDATE_DISPLAY_NAME or UPDATE_ABILITIES or UPDATE_EVOLUTIONS or UPDATE_DESCRIPTIONS or UPDATE_HOLDITEMS:
        update_species_info()

    if UPDATE_MOVES:
        update_pokemon_moves()

    if UPDATE_LEARNSET:
        update_pokemon_learnset()

    if UPDATE_ID_SORT:
        sort_species_id()

    if UPDATE_ANIM_FRONT:
        update_sprite_file_path()

    if UPDATE_NATIONAL_DEX:
        update_national_dex_order()

    print("\n🏁 プログラムを終了します。")