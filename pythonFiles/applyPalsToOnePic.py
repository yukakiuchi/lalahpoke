import os
import struct
from PIL import Image

# --- 設定 ---
# 1. プロジェクトのルートパス (expandフォルダの場所)
project_root = "/Users/yu/Desktop/expand/graphics/battle_anims" 
# 2. 元にする画像が入っているディレクトリ (この中のPNGを自動取得)
source_dir = "/Users/yu/Desktop/ccc/"
# 3. 出力先 (デスクトップのフォルダ)
output_dir = os.path.expanduser("~/Desktop/all_palettes_test/")

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def gba_to_rgb(gba_color):
    r = (gba_color & 0x1F) << 3
    g = ((gba_color >> 5) & 0x1F) << 3
    b = ((gba_color >> 10) & 0x1F) << 3
    return (r, g, b)

def get_single_png(directory):
    """ディレクトリ内の最初のPNGファイルパスを返す"""
    for f in os.listdir(directory):
        if f.lower().endswith(".png"):
            return os.path.join(directory, f)
    return None

def scan_and_apply():
    # --- 修正箇所：CCCフォルダから画像を探す ---
    source_png = get_single_png(source_dir)
    if not source_png:
        print(f"エラー: {source_dir} の中にPNGファイルが見つかりません。")
        return
    
    print(f"使用するベース画像: {os.path.basename(source_png)}")
    # ---------------------------------------

    base_img = Image.open(source_png)
    if base_img.mode != 'P':
        print("Error: Image must be in Indexed Color mode (P).")
        return

    count = 0
    # os.walk で全フォルダを自動探索
    for root, dirs, files in os.walk(project_root):
        for filename in files:
            if filename.endswith(".gbapal"):
                pal_path = os.path.join(root, filename)
                
                try:
                    with open(pal_path, "rb") as f:
                        pal_data = f.read()
                    
                    if len(pal_data) < 2: continue
                    
                    new_palette = []
                    # 最大16色分取得
                    for i in range(0, min(len(pal_data), 32), 2):
                        gba_color = struct.unpack("<H", pal_data[i:i+2])[0]
                        new_palette.extend(gba_to_rgb(gba_color))

                    final_palette = new_palette + [0] * (768 - len(new_palette))
                    
                    temp_img = base_img.copy()
                    temp_img.putpalette(final_palette)
                    
                    # 保存名は「フォルダ名_ファイル名.png」にして重複を避ける
                    rel_path = os.path.relpath(root, project_root).replace("/", "_")
                    save_name = f"{rel_path}_{filename.replace('.gbapal', '.png')}"
                    temp_img.save(os.path.join(output_dir, save_name))
                    
                    count += 1
                    if count % 50 == 0:
                        print(f"{count} files processed...")
                except Exception as e:
                    print(f"Skip {filename}: {e}")

    print(f"\n完了！合計 {count} 個のパレットを適用しました。")
    print(f"結果は '{output_dir}' を確認してください。")

if __name__ == "__main__":
    scan_and_apply()