import os
import re
import sys
import subprocess
from PIL import Image

# ------------------ 設定 ------------------
SOURCE_DIR = "/Users/yu/Desktop/kara"
OUTPUT_DIR = "/Users/yu/Desktop/your_output_folder"
TILE_SIZE = 32
# ------------------------------------------

def open_folder_and_exit(target_dir):
    print(f"\n📂 出力フォルダを自動で開きます: {target_dir}")
    if sys.platform == "darwin":
        subprocess.run(["open", target_dir])
    sys.exit(0)

def process_images():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # PNGファイルを取得
    files = [f for f in os.listdir(SOURCE_DIR) if f.lower().endswith(".png") and not f.startswith('.')]
    
    print(f"処理を開始します...")

    for filename in files:
        # ファイル名から「カット位置」を抽出 (例: 456_1_i.png -> 1)
        match = re.search(r"_(\d+)_i\.png$", filename)
        if not match:
            continue
        
        cut_index = int(match.group(1)) # 1始まりのインデックス
        
        file_path = os.path.join(SOURCE_DIR, filename)
        
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                
                # カットしたい開始X座標（0始まり）
                # cut_indexが1なら x=0, 2なら x=32...
                start_x = (cut_index - 1) * TILE_SIZE
                
                # 範囲チェック（画像からはみ出さないように）
                if start_x + TILE_SIZE > width:
                    print(f"⚠️ スキップ: {filename} は範囲外です")
                    continue
                
                # 切り出しボックス (left, top, right, bottom)
                # 高さは画像の高さをそのまま使用（32または64）
                crop_box = (start_x, 0, start_x + TILE_SIZE, height)
                
                part = img.crop(crop_box)
                
                # 保存
                save_path = os.path.join(OUTPUT_DIR, filename)
                part.save(save_path)
                print(f"✅ 切り出し完了: {filename} (X:{start_x}〜{start_x+32}, H:{height})")
                
        except Exception as e:
            print(f"❌ エラー: {filename} - {e}")

    print("-" * 40)
    print("🚀 すべての画像処理が完了しました。")
    open_folder_and_exit(OUTPUT_DIR)

if __name__ == "__main__":
    process_images()