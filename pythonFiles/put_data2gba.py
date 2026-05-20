import csv
import io
import os
import sys
import requests
import re
from PIL import Image
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed

warnings.filterwarnings("ignore", category=DeprecationWarning)

# ------------------ 設定 ------------------
CSV_FILE_PATH = "/Users/yu/Desktop/sprites.csv"
BASE_OUTPUT_DIR = "/Users/yu/Desktop/expand/graphics/pokemon"
SPECIES_INFO_DIR = "/Users/yu/Desktop/expand/src/data/pokemon/species_info"

START_ID = 1
END_ID = 320

TARGET_SPRITE_IDS = []
TARGET_ICON_IDS = []

ENABLE_SPRITES = "OFF"
ENABLE_ICONS = "ON"
ENABLE_ICON_PAL_UPDATE = "ON"

MAX_WORKERS = 50
# ------------------------------------------

def write_jasc_pal(palette_path, palette_list):
    with open(palette_path, "wb") as f:
        f.write(b"JASC-PAL\n0100\n16\n")
        for r, g, b in palette_list:
            f.write(f"{r} {g} {b}\n".encode("ascii"))

def process_and_sync_poke_sprites(img_raw, out_dir, current_id):
    if img_raw.mode == 'P':
        palette_data = img_raw.getpalette()
        num_colors = len(palette_data) // 3 if palette_data else 0
    else:
        used_colors = img_raw.getcolors(maxcolors=256)
        num_colors = len(used_colors) if used_colors else 0
    
    if num_colors == 32 and img_raw.mode == 'P':
        process_msg = "32色背景0番補正実行"
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
        for i in range(4):
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
        f_n_final, b_s_final = parts[0], parts[3]
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
    write_jasc_pal(os.path.join(out_dir, "normal.pal"), pal_n_out)
    write_jasc_pal(os.path.join(out_dir, "shiny.pal"), pal_s_out)
    anim_img = Image.new("P", (64, 128))
    anim_img.putpalette(f_n_final.getpalette())
    anim_img.paste(f_n_final, (0, 0))
    anim_img.paste(f_n_final, (0, 64))
    anim_img.save(os.path.join(out_dir, "anim_front.png"))
    b_s_final.save(os.path.join(out_dir, "back.png"))
    print(f"✅ ID: {current_id:<4} -> {process_msg}")

def download_and_process_task(row, current_id):
    species = row.get("speciesName", f"unknown_id_{current_id}").lower()
    out_dir = os.path.join(BASE_OUTPUT_DIR, species)
    
    s_ok, s_empty = True, False
    i_ok, i_empty = True, False
    err_msgs = []

    if ENABLE_SPRITES == "ON":
        if not TARGET_SPRITE_IDS or current_id in TARGET_SPRITE_IDS:
            url = row.get("sprite_url")
            if not url:
                s_empty = True
                s_ok = False
            else:
                try:
                    os.makedirs(out_dir, exist_ok=True)
                    resp = requests.get(url, timeout=10)
                    resp.raise_for_status()
                    process_and_sync_poke_sprites(Image.open(io.BytesIO(resp.content)), out_dir, current_id)
                except Exception as e:
                    err_msgs.append(f"Spriteエラー({current_id}): {e}")
                    s_ok = False

    if ENABLE_ICONS == "ON":
        if not TARGET_ICON_IDS or current_id in TARGET_ICON_IDS:
            icon_url = row.get("icon_url")
            if not icon_url:
                i_empty = True
                i_ok = False
            else:
                try:
                    os.makedirs(out_dir, exist_ok=True)
                    resp = requests.get(icon_url, timeout=10)
                    resp.raise_for_status()
                    img = Image.open(io.BytesIO(resp.content))
                    if img.mode != 'P':
                        if img.mode == 'RGBA':
                            bg = Image.new("RGB", img.size, (0, 120, 120))
                            bg.paste(img, mask=img.split()[3])
                            img = bg
                        img = img.convert("P", palette=Image.Palette.ADAPTIVE, colors=16)
                    img.save(os.path.join(out_dir, "icon.png"), "PNG")
                    print(f"📸 ID: {current_id:<4} -> icon.png 保存完了")
                except Exception as e:
                    err_msgs.append(f"Iconエラー({current_id}): {e}")
                    i_ok = False

    return current_id, s_ok, s_empty, i_ok, i_empty, " | ".join(err_msgs) if err_msgs else None

def update_icon_palettes(tasks):
    print("\n📝 [iconPalIndex 更新処理] を開始します...")
    if not os.path.exists(SPECIES_INFO_DIR): return
    file_cache = {}
    for root, _, files in os.walk(SPECIES_INFO_DIR):
        for f in files:
            if f.endswith(('.h', '.c', '.txt')):
                path = os.path.join(root, f)
                with open(path, "r", encoding="utf-8", errors="ignore") as file_obj:
                    file_cache[path] = file_obj.read()
    modified = set()
    for row, cid in tasks:
        species_name = row.get("speciesName")
        pal = row.get("pal")
        if not species_name or not pal: continue
        name = re.sub(r'[^a-zA-Z0-9_]', '_', species_name).upper()
        name = re.sub(r'_+', '_', name).strip('_')
        pattern = rf"(\[SPECIES_{name}\]\s*=\s*\{{.*?\.iconPalIndex\s*=\s*)(.*?)(,)"
        for path, content in file_cache.items():
            new_content, count = re.subn(pattern, rf"\g<1>{pal}\g<3>", content, flags=re.DOTALL)
            if count > 0:
                file_cache[path] = new_content
                modified.add(path)
                break
    for path in modified:
        with open(path, "w", encoding="utf-8") as f: f.write(file_cache[path])

if __name__ == "__main__":
    combined = TARGET_SPRITE_IDS + TARGET_ICON_IDS
    with open(CSV_FILE_PATH, newline="", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    tasks = [(row, i+1) for i, row in enumerate(reader) if (combined and i+1 in combined) or (not combined and START_ID <= i+1 <= END_ID)]
    
    failed_s, empty_s = [], []
    failed_i, empty_i = [], []

    if tasks:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(download_and_process_task, row, cid): cid for row, cid in tasks}
            for f in as_completed(futures):
                cid, s_ok, s_empty, i_ok, i_empty, err = f.result()
                if not s_ok:
                    if s_empty: empty_s.append(cid)
                    else: failed_s.append(cid)
                if not i_ok:
                    if i_empty: empty_i.append(cid)
                    else: failed_i.append(cid)
                if err: print(f"⚠️ {err}")

    # 4. 結果の表示ロジック
    has_failed = failed_s or failed_i
    has_empty = empty_s or empty_i

    if has_failed:
        print("\n❌ 失敗ID一覧 (エラー発生)")
        print(f"TARGET_SPRITE_IDS = {sorted(list(set(failed_s)))}")
        print(f"TARGET_ICON_IDS = {sorted(list(set(failed_i)))}")
    
    if has_empty:
        print("\nℹ️ データなしID一覧 (URLが空)")
        print(f"EMPTY_SPRITE_IDS = {sorted(list(set(empty_s)))}")
        print(f"EMPTY_ICON_IDS = {sorted(list(set(empty_i)))}")

    if not has_failed and not has_empty:
        print("\n✅ すべての処理が正常に完了しました。エラーや空のデータはありません。")

    # パレット更新処理
    if ENABLE_ICON_PAL_UPDATE == "ON":
        update_icon_palettes(tasks)
        
    print("\n🏁 プログラムを終了します。")