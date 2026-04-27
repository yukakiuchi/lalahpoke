
import csv
import os

# pokeemerald のルートパス
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# CSV ファイル名
csv_file = "generate_poke.csv"

# CSV ファイルの読み込み
with open(csv_file, newline='', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    data = list(reader)


# ------------------画像処理---------------------------------
SRC_IMG = "TREECKO.png"
SPECIES = "treecko"

from PIL import Image
# 出力先ファイル
POKE_PNG_OUT_DIR  = os.path.join(ROOT_DIR, "graphics", "pokemon", SPECIES)

def make_palette_png(front_path, palette_path):
    img = Image.open(front_path)
    if img.mode != "P":
        img = img.convert("P")
    palette = img.getpalette()[:16*3]  # 最初の16色だけ
    pal_img = Image.new("P", (16,1))
    pal_img.putpalette(palette)
    pal_img.putdata(list(range(16)))  # 0~15を割り当て
    pal_img.save(palette_path)
make_palette_png(os.path.join(POKE_PNG_OUT_DIR, "front.png"), os.path.join(POKE_PNG_OUT_DIR, "palette.png"))

img = Image.open(SRC_IMG)
assert img.size == (256, 64)
def cut(x):
    return img.crop((x, 0, x + 64, 64))
cut(0).save(os.path.join(POKE_PNG_OUT_DIR, "front.png"))
cut(64).save(os.path.join(POKE_PNG_OUT_DIR, "shiny_front.png"))
cut(128).save(os.path.join(POKE_PNG_OUT_DIR, "back.png"))
cut(192).save(os.path.join(POKE_PNG_OUT_DIR, "shiny_back.png"))

# ------------------species.h 図鑑定義を生成 ------------------

if False:
    with open("species.h", "w", encoding="utf-8") as f:
        # ヘッダー
        f.write("#ifndef GUARD_CONSTANTS_SPECIES_H\n")
        f.write("#define GUARD_CONSTANTS_SPECIES_H\n\n")

        # species を1行ずつ出力
        for row in data:
            f.write(f"#define SPECIES_{row['internalName']} {row['id']}\n")

        # フッタ
        f.write("\n")
        f.write("#define SPECIES_EGG 412\n\n")
        f.write("#define NUM_SPECIES SPECIES_EGG\n\n")
        f.write("#define SPECIES_UNOWN_B (NUM_SPECIES + 1)\n")
        f.write("#define SPECIES_UNOWN_C (SPECIES_UNOWN_B + 1)\n")
        f.write("#define SPECIES_UNOWN_D (SPECIES_UNOWN_B + 2)\n")
        f.write("#define SPECIES_UNOWN_E (SPECIES_UNOWN_B + 3)\n")
        f.write("#define SPECIES_UNOWN_F (SPECIES_UNOWN_B + 4)\n")
        f.write("#define SPECIES_UNOWN_G (SPECIES_UNOWN_B + 5)\n")
        f.write("#define SPECIES_UNOWN_H (SPECIES_UNOWN_B + 6)\n")
        f.write("#define SPECIES_UNOWN_I (SPECIES_UNOWN_B + 7)\n")
        f.write("#define SPECIES_UNOWN_J (SPECIES_UNOWN_B + 8)\n")
        f.write("#define SPECIES_UNOWN_K (SPECIES_UNOWN_B + 9)\n")
        f.write("#define SPECIES_UNOWN_L (SPECIES_UNOWN_B + 10)\n")
        f.write("#define SPECIES_UNOWN_M (SPECIES_UNOWN_B + 11)\n")
        f.write("#define SPECIES_UNOWN_N (SPECIES_UNOWN_B + 12)\n")
        f.write("#define SPECIES_UNOWN_O (SPECIES_UNOWN_B + 13)\n")
        f.write("#define SPECIES_UNOWN_P (SPECIES_UNOWN_B + 14)\n")
        f.write("#define SPECIES_UNOWN_Q (SPECIES_UNOWN_B + 15)\n")
        f.write("#define SPECIES_UNOWN_R (SPECIES_UNOWN_B + 16)\n")
        f.write("#define SPECIES_UNOWN_S (SPECIES_UNOWN_B + 17)\n")
        f.write("#define SPECIES_UNOWN_T (SPECIES_UNOWN_B + 18)\n")
        f.write("#define SPECIES_UNOWN_U (SPECIES_UNOWN_B + 19)\n")
        f.write("#define SPECIES_UNOWN_V (SPECIES_UNOWN_B + 20)\n")
        f.write("#define SPECIES_UNOWN_W (SPECIES_UNOWN_B + 21)\n")
        f.write("#define SPECIES_UNOWN_X (SPECIES_UNOWN_B + 22)\n")
        f.write("#define SPECIES_UNOWN_Y (SPECIES_UNOWN_B + 23)\n")
        f.write("#define SPECIES_UNOWN_Z (SPECIES_UNOWN_B + 24)\n")
        f.write("#define SPECIES_UNOWN_EMARK (SPECIES_UNOWN_B + 25)\n")
        f.write("#define SPECIES_UNOWN_QMARK (SPECIES_UNOWN_B + 26)\n\n")
        f.write("#endif // GUARD_CONSTANTS_SPECIES_H")


# ------------------species_info.h ポケモン能力情報を生成------------------
# 出力先のフォルダー指定
POKE_DATA_OUT_DIR = os.path.join(ROOT_DIR, "src", "data", "pokemon")  # 例: src/data に生成
# 生成ファイル名
poke_data_output_file = os.path.join(POKE_DATA_OUT_DIR, "species_info.h")

with open(poke_data_output_file, "w", encoding="utf-8") as f:

    # ヘッダー
    f.write("// Maximum value for a female Pokémon is 254 (MON_FEMALE) which is 100% female.\n")
    f.write("// 255 (MON_GENDERLESS) is reserved for genderless Pokémon.\n")
    f.write("#define PERCENT_FEMALE(percent) min(254, ((percent * 255) / 100))\n\n")
    f.write("#define OLD_UNOWN_SPECIES_INFO                                                          \\\n")
    f.write("    {                                                                                   \\\n")
    f.write("        .baseHP = 50,                                                                   \\\n")
    f.write("        .baseAttack = 150,                                                              \\\n")
    f.write("        .baseDefense = 50,                                                              \\\n")
    f.write("        .baseSpeed = 150,                                                               \\\n")
    f.write("        .baseSpAttack = 150,                                                            \\\n")
    f.write("        .baseSpDefense = 50,                                                            \\\n")
    f.write("        .types = { TYPE_NORMAL, TYPE_NORMAL },                                          \\\n")
    f.write("        .catchRate = 3,                                                                 \\\n")
    f.write("        .expYield = 1,                                                                  \\\n")
    f.write("        .evYield_HP = 2,                                                                \\\n")
    f.write("        .evYield_Attack = 2,                                                            \\\n")
    f.write("        .evYield_Defense = 2,                                                           \\\n")
    f.write("        .evYield_Speed = 2,                                                             \\\n")
    f.write("        .evYield_SpAttack = 2,                                                          \\\n")
    f.write("        .evYield_SpDefense = 2,                                                         \\\n")
    f.write("        .itemCommon = ITEM_NONE,                                                        \\\n")
    f.write("        .itemRare   = ITEM_NONE,                                                        \\\n")
    f.write("        .genderRatio = MON_GENDERLESS,                                                  \\\n")
    f.write("        .eggCycles = 120,                                                               \\\n")
    f.write("        .friendship = 0,                                                                \\\n")
    f.write("        .growthRate = GROWTH_MEDIUM_FAST,                                               \\\n")
    f.write("        .eggGroups = { EGG_GROUP_NO_EGGS_DISCOVERED, EGG_GROUP_NO_EGGS_DISCOVERED },    \\\n")
    f.write("        .abilities = { ABILITY_NONE, ABILITY_NONE },                                    \\\n")
    f.write("        .safariZoneFleeRate = 0,                                                        \\\n")
    f.write("        .bodyColor = BODY_COLOR_BLACK,                                                  \\\n")
    f.write("        .noFlip = FALSE,                                                                \\\n")
    f.write("    }\n\n")

    # 中身ベース情報
    f.write("const struct SpeciesInfo gSpeciesInfo[] =\n{\n")
    f.write("    [SPECIES_NONE] = {0},\n\n")


    # 中身
    for i, row in enumerate(data):
        pokemon_id = int(row['id'])

        # システムデータ
        if 252 <= pokemon_id <= 276:
            f.write(f"[SPECIES_{row['internalName']}] = OLD_UNOWN_SPECIES_INFO, \n\n")
    
        # 通常ポケモン
        else:
            f.write(f"    [SPECIES_{row['internalName']}] =\n")
            f.write("    {\n")
            f.write(f"        .baseHP             = {row['baseHP']},\n")
            f.write(f"        .baseAttack         = {row['baseAttack']},\n")
            f.write(f"        .baseDefense        = {row['baseDefense']},\n")
            f.write(f"        .baseSpeed          = {row['baseSpeed']},\n")
            f.write(f"        .baseSpAttack       = {row['baseSpAttack']},\n")
            f.write(f"        .baseSpDefense      = {row['baseSpDefense']},\n")
            f.write(f"        .types              = {{ {row['type1']}, {row['type2']} }},\n")
            f.write(f"        .catchRate          = {row['catchRate']},\n")
            f.write(f"        .expYield           = {row['expYield']},\n")
            f.write(f"        .evYield_HP         = 0,\n")
            f.write(f"        .evYield_Attack     = 0,\n")
            f.write(f"        .evYield_Defense    = 0,\n")
            f.write(f"        .evYield_Speed      = 0,\n")
            f.write(f"        .evYield_SpAttack   = 0,\n")
            f.write(f"        .evYield_SpDefense  = 0,\n")
            f.write(f"        .itemCommon         = {row['itemCommon']},\n")
            f.write(f"        .itemRare           = {row['itemRare']},\n")
            f.write(f"        .genderRatio        = PERCENT_FEMALE(50),\n")
            f.write(f"        .eggCycles          = 20,\n")
            f.write(f"        .friendship         = STANDARD_FRIENDSHIP,\n")
            f.write(f"        .growthRate         = GROWTH_MEDIUM_FAST,\n")
            f.write("        .eggGroups          = { EGG_GROUP_NO_EGGS_DISCOVERED, EGG_GROUP_NO_EGGS_DISCOVERED },\n")
            f.write(f"        .abilities          = {{ {row['ability1']}, {row['ability2']} }},\n")
            f.write(f"        .safariZoneFleeRate = 0,\n")
            f.write(f"        .bodyColor          = BODY_COLOR_GREEN,\n")
            f.write(f"        .noFlip             = FALSE,\n")
            f.write("    }")

            # 最後の要素かでカンマを制御
            is_last = (i == len(data) - 1)  # 最後の要素かどうか
            if not is_last:
                f.write(",\n\n")
            else:
                f.write("\n\n")
        # 閉じる
    f.write("};\n\n")


# 完了通知
print('ファイルをを生成しました！')