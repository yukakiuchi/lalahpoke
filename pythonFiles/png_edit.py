import csv
import os
import requests
from PIL import Image

# ------------------ 設定 ------------------
CSV_FILE = "sprites.csv"  # CSVに species, url がある想定
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
POKE_PNG_OUT_DIR_BASE = os.path.join(ROOT_DIR, "graphics", "pokemon")

# ------------------ CSV 読み込み ------------------
with open(CSV_FILE, newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        species = row["internalName"].lower()  # treecko, pikachu など
        url = row["png_url"]

        # 出力ディレクトリ
        out_dir = os.path.join(POKE_PNG_OUT_DIR_BASE, species)
        os.makedirs(out_dir, exist_ok=True)

        # ------------------ URL から PNG をダウンロード ------------------
        src_img_path = os.path.join(out_dir, f"{species}_sheet.png")
        resp = requests.get(url)
        resp.raise_for_status()  # ダウンロード失敗時に例外
        with open(src_img_path, "wb") as img_file:
            img_file.write(resp.content)

        # ------------------ 画像処理 ------------------
        img = Image.open(src_img_path)
        assert img.size == (256, 64), f"{species} の画像サイズが256x64ではありません"

        # 元画像を P モードにして palette 固定
        if img.mode != "P":
            img = img.convert("P")
        sprite_palette = img.getpalette()

        # --- crop + 保存 ---
        def cut_and_save(x, filename):
            part = img.crop((x, 0, x + 64, 64))
            part = part.copy()
            part.putpalette(sprite_palette)
            path = os.path.join(out_dir, filename)
            part.save(path)
            return part

        front_img = cut_and_save(0, "front.png")
        back_img  = cut_and_save(128, "back.png")

        # --- anim_front ---
        anim_img = Image.new("P", (64, 128))
        anim_img.putpalette(front_img.getpalette())
        anim_img.paste(front_img, (0, 0))
        anim_img.paste(front_img, (0, 64))
        anim_img.save(os.path.join(out_dir, "anim_front.png"))

        # --- パレット生成 ---
        def write_jasc_pal(palette_path, rgb_list):
            with open(palette_path, "w") as f:
                f.write("JASC-PAL\n0100\n16\n")
                for r, g, b in rgb_list:
                    f.write(f"{r} {g} {b}\n")

        def make_pal_from_image(img_obj, pal_path):
            palette_data = img_obj.getpalette()[:16*3]
            rgb_list = [tuple(palette_data[i:i+3]) for i in range(0, 16*3, 3)]
            write_jasc_pal(pal_path, rgb_list)

        make_pal_from_image(front_img, os.path.join(out_dir, "normal.pal"))
        make_pal_from_image(anim_img, os.path.join(out_dir, "shiny.pal"))

        print(f"{species} sprites and palettes generated in {out_dir}")