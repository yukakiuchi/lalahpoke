import os
import sys
import subprocess
from PIL import Image

# ------------------ 設定 ------------------
SOURCE_DIR = "/Users/yu/Desktop/please_cut"
OUTPUT_DIR = "/Users/yu/Desktop/please_cut_done"
TILE_SIZE = 64

# 【手動指定CUT】
SIMPLE_CUT = []
CUSTOM_CUT = []
# ------------------------------------------

def open_folder_and_exit(target_dir):
    """ 処理完了後にフォルダをUIで開き、スクリプトを終了する """
    print(f"\n📂 出力フォルダを自動で開きます: {target_dir}")
    if sys.platform == "darwin": subprocess.run(["open", target_dir])
    elif sys.platform == "win32": os.startfile(target_dir)
    else: subprocess.run(["xdg-open", target_dir])
    sys.exit(0)

def get_palette_count(img):
    if img.mode == 'P':
        if hasattr(img, 'palette') and img.palette and img.palette.palette:
            return len(img.palette.palette) // 3
        try: return max(img.getdata()) + 1
        except: return 256
    else:
        colors = img.getcolors(maxcolors=10000)
        return len(colors) if colors else 256

def process_images():
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    files = sorted([f for f in os.listdir(SOURCE_DIR) if f.lower().endswith(".png") and not f.startswith('.')])
    
    print(f"取得元: {SOURCE_DIR}")
    print(f"出力先: {OUTPUT_DIR}")
    print("-" * 40)

    for filename in files:
        file_path = os.path.join(SOURCE_DIR, filename)
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                base_name = os.path.splitext(filename.replace("_combined", ""))[0]
                palette_count = get_palette_count(img)
                
                # モード判定
                if filename in SIMPLE_CUT: cut_mode = "SIMPLE"
                elif filename in CUSTOM_CUT: cut_mode = "CUSTOM"
                elif 31 <= palette_count <= 33: cut_mode = "CUSTOM"
                else: cut_mode = "SIMPLE"

                if cut_mode == "CUSTOM":
                    print(f"🎨 [CUSTOM] {filename} (色数: {palette_count}) -> 16色ずつに減色・カットします")
                    img_p = img.convert('P')
                    full_pal = img_p.getpalette()
                    pal_norm_data = full_pal[0:48]
                    pal_shiny_data = full_pal[48:96]
                    cols = width // TILE_SIZE
                    for c in range(cols):
                        part = img_p.crop((c * TILE_SIZE, 0, (c + 1) * TILE_SIZE, TILE_SIZE))
                        if c % 2 == 1:
                            part = part.point(lambda p: p - 16 if p >= 16 else 0)
                            current_pal_data = pal_shiny_data
                        else:
                            current_pal_data = pal_norm_data
                        part.putpalette(list(current_pal_data) + ([0] * (768 - 48)))
                        part.palette.palette = bytes(current_pal_data)
                        part.save(os.path.join(OUTPUT_DIR, f"{base_name}_{c + 1}.png"), transparency=0)

                else:
                    print(f"🔄 [SIMPLE/SYNC] {filename} (色数: {palette_count}) -> パレット同期カット")
                    img_rgba = img.convert("RGBA")
                    f_n = img_rgba.crop((0, 0, 64, 64)); f_s = img_rgba.crop((64, 0, 128, 64))
                    b_n = img_rgba.crop((128, 0, 192, 64)); b_s = img_rgba.crop((192, 0, 256, 64))
                    
                    bg_n, bg_s = (0, 120, 120), (0, 120, 120)
                    pal_n, pal_s = [bg_n], [bg_s]
                    color_to_idx = {}
                    
                    def build_indices(img_n, img_s):
                        indices = []
                        for p_n, p_s in zip(list(img_n.getdata()), list(img_s.getdata())):
                            if p_n[3] == 0 or p_n[:3] == bg_n: indices.append(0); continue
                            combo = (p_n[:3], p_s[:3])
                            if combo not in color_to_idx:
                                if len(pal_n) < 16:
                                    color_to_idx[combo] = len(pal_n)
                                    pal_n.append(p_n[:3]); pal_s.append(p_s[:3])
                                    indices.append(color_to_idx[combo])
                                else: indices.append(0)
                            else: indices.append(color_to_idx[combo])
                        return indices

                    idx_f = build_indices(f_n, f_s)
                    idx_b = build_indices(b_n, b_s)
                    while len(pal_n) < 16: pal_n.append((0, 0, 0)); pal_s.append((0, 0, 0))
                    
                    def save_p(idx, pal, num):
                        p = Image.new("P", (64, 64))
                        p.putpalette([c for rgb in pal for c in rgb])
                        p.putdata(idx)
                        p.save(os.path.join(OUTPUT_DIR, f"{base_name}_{num}.png"))

                    save_p(idx_f, pal_n, "1"); save_p(idx_f, pal_s, "2")
                    save_p(idx_b, pal_n, "3"); save_p(idx_b, pal_s, "4")
        
        except Exception as e:
            print(f"❌ エラー発生: {filename} - {e}")

    print("-" * 40 + "\n🚀 すべての画像処理が完了しました。")
    open_folder_and_exit(OUTPUT_DIR)

if __name__ == "__main__":
    process_images()