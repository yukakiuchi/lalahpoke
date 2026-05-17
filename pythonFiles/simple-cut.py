import os
from PIL import Image

# ------------------ 設定 ------------------
SOURCE_DIR = "/Users/yu/Desktop/edit_png"
OUTPUT_DIR = "/Users/yu/Desktop/cut"
TILE_SIZE = 64
# ------------------------------------------

def split_images():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 隠しファイル（.DS_Store等）を除外してPNGのみ取得
    files = sorted([f for f in os.listdir(SOURCE_DIR) if f.lower().endswith(".png") and not f.startswith('.')])
    
    print(f"取得元フォルダー: {SOURCE_DIR}")
    print(f"出力先フォルダー: {OUTPUT_DIR}")
    print("-" * 30)

    for filename in files:
        file_path = os.path.join(SOURCE_DIR, filename)
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                
                # 横と縦に何個のタイルが並んでいるか計算
                cols = width // TILE_SIZE
                rows = height // TILE_SIZE
                
                base_name = os.path.splitext(filename)[0]
                
                count = 1
                for r in range(rows):
                    for c in range(cols):
                        # 切り出し範囲計算 (左, 上, 右, 下)
                        left = c * TILE_SIZE
                        top = r * TILE_SIZE
                        right = left + TILE_SIZE
                        bottom = top + TILE_SIZE
                        
                        part = img.crop((left, top, right, bottom))
                        
                        # 保存名の作成 (元のファイル名_1, _2...)
                        new_filename = f"{base_name}_{count}.png"
                        save_path = os.path.join(OUTPUT_DIR, new_filename)
                        
                        # そのままのモード(PやRGBA)で保存
                        part.save(save_path)
                        
                        print(f"分割出力: {new_filename}")
                        count += 1
                        
        except Exception as e:
            print(f"エラー発生: {filename} - {e}")

    print("-" * 30)
    print("🚀 64x64のシンプル分割処理が完了しました。")

if __name__ == "__main__":
    split_images()