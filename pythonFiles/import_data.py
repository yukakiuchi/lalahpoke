import csv
import io
import os
import requests
from PIL import Image
import warnings

# Pillowの将来の警告（DeprecationWarning）を非表示にする
warnings.filterwarnings("ignore", category=DeprecationWarning)

# ------------------ 設定 ------------------
CSV_FILE_PATH = "/Users/yu/Desktop/sprites.csv"
BASE_OUTPUT_DIR = "/Users/yu/Desktop/expand/graphics/pokemon"

START_ID = 1
END_ID = 300
TARGET_IDS = [49, 88, 90, 246] 

# ------------------ 関数定義 ------------------

def write_jasc_pal(palette_path, palette_list):
    """JASC-PAL形式でパレットを保存"""
    with open(palette_path, "wb") as f:
        f.write(b"JASC-PAL\n0100\n16\n")
        for r, g, b in palette_list:
            f.write(f"{r} {g} {b}\n".encode("ascii"))

def process_and_sync_poke_sprites(img_raw, out_dir, current_id):
    """
    32色インデックス画像の背景色(左上の色)を強制的に0番目に入れ替えて
    背景を透過させる修正版
    """
    if img_raw.mode == 'P':
        palette_data = img_raw.getpalette()
        num_colors = len(palette_data) // 3 if palette_data else 0
    else:
        used_colors = img_raw.getcolors(maxcolors=256)
        num_colors = len(used_colors) if used_colors else 0
    
    if num_colors == 32 and img_raw.mode == 'P':
        process_msg = "32色背景0番補正実行"
        full_pal = img_raw.getpalette() 
        
        # 通常色の背景(0,0)と、色違いの背景(64,0)のインデックスを直接取得
        bg_idx_n = img_raw.getpixel((0, 0))   
        bg_idx_s = img_raw.getpixel((64, 0))  

        # パレットを16色ずつに分割
        pal_n_list = [tuple(full_pal[i:i+3]) for i in range(0, 48, 3)]
        pal_s_list = [tuple(full_pal[i:i+3]) for i in range(48, 96, 3)]

        # --- 重要：通常パレットの背景色を0番に入れ替え ---
        # 0番の色と bg_idx_n の色をスワップする
        actual_bg_n_color = pal_n_list[bg_idx_n]
        original_zero_n_color = pal_n_list[0]
        pal_n_list[0] = actual_bg_n_color
        pal_n_list[bg_idx_n] = original_zero_n_color
        
        # --- 重要：色違いパレットの背景色を0番に入れ替え ---
        bg_s_rel = bg_idx_s - 16
        actual_bg_s_color = pal_s_list[bg_s_rel]
        original_zero_s_color = pal_s_list[0]
        pal_s_list[0] = actual_bg_s_color
        pal_s_list[bg_s_rel] = original_zero_s_color

        parts = []
        for i in range(4):
            part = img_raw.crop((i * 64, 0, (i + 1) * 64, 64))
            is_shiny = (i % 2 == 1)
            
            # 全ピクセルをスキャンしてインデックスを書き換える
            # 背景色(bg_idx)だった場所を0にし、もともと0だった場所を旧背景色の位置へ
            def remap_pixels(p):
                if not is_shiny:
                    if p == bg_idx_n: return 0
                    if p == 0: return bg_idx_n
                    return p
                else:
                    rel_p = p - 16
                    if rel_p == bg_s_rel: return 0
                    if rel_p == 0: return bg_s_rel
                    return rel_p

            # point()を使って高速にインデックスを置換
            part = part.point(remap_pixels)
            
            # 新しいパレットを適用
            current_pal = pal_s_list if is_shiny else pal_n_list
            flat_pal = []
            for rgb in current_pal: flat_pal.extend(rgb)
            part.putpalette(flat_pal + ([0] * (768 - 48)))
            parts.append(part)
        
        f_n_final, b_s_final = parts[0], parts[3]
        pal_n_out, pal_s_out = pal_n_list, pal_s_list

    else:
        # --- パターンB: 通常処理 (ここは信頼性が高いのでそのまま) ---
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

    # --- 共通保存処理 ---
    write_jasc_pal(os.path.join(out_dir, "normal.pal"), pal_n_out)
    write_jasc_pal(os.path.join(out_dir, "shiny.pal"), pal_s_out)
    
    anim_img = Image.new("P", (64, 128))
    anim_img.putpalette(f_n_final.getpalette())
    anim_img.paste(f_n_final, (0, 0))
    anim_img.paste(f_n_final, (0, 64))
    anim_img.save(os.path.join(out_dir, "anim_front.png"))
    
    b_s_final.save(os.path.join(out_dir, "back.png"))
    print(f"✅ ID: {current_id:<4} パレット色数: {num_colors:<3} -> {process_msg}")

# ------------------ メイン処理 ------------------
if __name__ == "__main__":
    if not os.path.exists(BASE_OUTPUT_DIR):
        os.makedirs(BASE_OUTPUT_DIR)

    failed_ids = []

    try:
        with open(CSV_FILE_PATH, newline="", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
            for i, row in enumerate(reader):
                current_id = i + 1
                if TARGET_IDS:
                    if current_id not in TARGET_IDS: continue
                else:
                    if not (START_ID <= current_id <= END_ID): continue

                species = row["speciesName"].lower()
                url = row.get("sprite_url")
                if not url: continue

                out_dir = os.path.join(BASE_OUTPUT_DIR, species)
                os.makedirs(out_dir, exist_ok=True)

                try:
                    resp = requests.get(url, timeout=10)
                    resp.raise_for_status()
                    img_raw = Image.open(io.BytesIO(resp.content))
                    process_and_sync_poke_sprites(img_raw, out_dir, current_id)
                except Exception as e:
                    print(f"❌ ID: {current_id:<4} 処理エラー: {e}")
                    failed_ids.append(current_id)

    except Exception as e:
        print(f"❌ 実行エラー: {e}")

    if failed_ids:
        print("\n" + "!" * 30)
        print(f"処理が完了できなかったid: {', '.join(map(str, failed_ids))}")
        print("!" * 30)