import os
import sys
import subprocess
from PIL import Image

# ------------------ 設定 ------------------
SOURCE_DIR = "/Users/yu/Desktop/edit"
OUTPUT_DIR = "/Users/yu/Desktop/edit_png"
TILE_SIZE = 64
# ------------------------------------------

def open_folder_and_exit(target_dir):
    """ 処理完了後にフォルダをUIで開き、スクリプトを終了する """
    print(f"\n📂 出力フォルダを自動で開きます: {target_dir}")
    if sys.platform == "darwin":      # Mac
        subprocess.run(["open", target_dir])
    elif sys.platform == "win32":    # Windows
        os.startfile(target_dir)
    else:                            # Linux等
        subprocess.run(["xdg-open", target_dir])
    sys.exit(0)

def get_palette_count(img):
    """
    画像の定義上のパレット数（または実際のユニーク色数）を取得する
    """
    if img.mode == 'P':
        if hasattr(img, 'palette') and img.palette and img.palette.palette:
            actual_bytes = len(img.palette.palette)
            if actual_bytes > 0:
                return actual_bytes // 3
                
        try:
            max_pixel_value = max(img.getdata())
            return max_pixel_value + 1
        except:
            return 256
    else:
        colors = img.getcolors(maxcolors=10000)
        if colors:
            return len(colors)
        return 256

def process_images():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 隠しファイル（.DS_Store等）を除外してPNGのみ取得
    files = sorted([f for f in os.listdir(SOURCE_DIR) if f.lower().endswith(".png") and not f.startswith('.')])
    
    print(f"取得元フォルダー: {SOURCE_DIR}")
    print(f"出力先フォルダー: {OUTPUT_DIR}")
    print("-" * 40)

    for filename in files:
        file_path = os.path.join(SOURCE_DIR, filename)
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                base_name = os.path.splitext(filename.replace("_combined", ""))[0]
                
                palette_count = get_palette_count(img)
                
                # ------------------------------------------------------------
                # 👑 判定基準: 28色以上の場合はCUSTOM (通常/色違い統合)
                # ------------------------------------------------------------
                if palette_count >= 31:
                    print(f"🎨 [CUSTOM] {filename} (色数: {palette_count}) -> 16色ずつに減色・カットします")
                    
                    img_p = img.convert('P')
                    full_pal = img_p.getpalette()
                    
                    # パレット分離（各16色 = 48bytes）
                    pal_norm_data = full_pal[0:48]
                    pal_shiny_data = full_pal[48:96]
                    
                    cols = width // TILE_SIZE
                    
                    for c in range(cols):
                        part = img_p.crop((c * TILE_SIZE, 0, (c + 1) * TILE_SIZE, TILE_SIZE))
                        
                        # 奇数番目は色違いスプライトとして処理
                        if c % 2 == 1:
                            part = part.point(lambda p: p - 16 if p >= 16 else 0)
                            current_pal_data = pal_shiny_data
                        else:
                            current_pal_data = pal_norm_data
                        
                        # 16色パレットの適用と、パレット構造の16色(48bytes)強制カット
                        part.putpalette(list(current_pal_data) + ([0] * (768 - 48)))
                        part.palette.palette = bytes(current_pal_data)
                        
                        new_filename = f"{base_name}_{c + 1}.png"
                        part.save(os.path.join(OUTPUT_DIR, new_filename), transparency=0)
                        print(f"  └ 出力: {new_filename} (16色パレット限定済)")

                # ------------------------------------------------------------
                # 👑 判定基準: それ以下（27色以下、実質17色以下想定）はSIMPLE
                # ------------------------------------------------------------
                else:
                    print(f"📐 [SIMPLE] {filename} (色数: {palette_count}) -> そのままシンプル分割します")
                    cols = width // TILE_SIZE
                    rows = height // TILE_SIZE
                    
                    count = 1
                    for r in range(rows):
                        for c in range(cols):
                            left = c * TILE_SIZE
                            top = r * TILE_SIZE
                            right = left + TILE_SIZE
                            bottom = top + TILE_SIZE
                            
                            part = img.crop((left, top, right, bottom))
                            
                            new_filename = f"{base_name}_{count}.png"
                            save_path = os.path.join(OUTPUT_DIR, new_filename)
                            
                            part.save(save_path)
                            print(f"  └ 出力: {new_filename}")
                            count += 1
                        
        except Exception as e:
            print(f"❌ エラー発生: {filename} - {e}")

    print("-" * 40)
    print("🚀 すべての画像処理が完了しました。")
    
    open_folder_and_exit(OUTPUT_DIR)

if __name__ == "__main__":
    process_images()