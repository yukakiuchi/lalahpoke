import os
from PIL import Image

TARGET_DIR = "/Users/yu/Desktop/rrr"

def force_save_16color_png(file_path):
    try:
        with Image.open(file_path) as img:
            # 1. 確実にPモードにする
            pixels = img.convert("P")
            
            # 2. 現在のパレット（最大256色分）を取得
            full_palette = pixels.getpalette()
            
            # 3. 先頭16色分だけを抽出（16 * 3 = 48）
            base_16_palette = full_palette[:48]
            
            # 4. 元のインデックスデータを取得（リストに変換）
            # get_flattened_dataは環境により未実装の場合があるため、list(img.getdata())が現在最も安全です
            pixel_data = list(pixels.getdata())
            
            # 5. 画像を再構築する際、パレットを先に定義する
            # Pillowの現在の仕様で「パレットサイズを物理的に16色にする」には、
            # palette引数を渡して初期化する必要があります
            new_img = Image.new("P", img.size)
            
            # 6. パレットを強制的に16色にするための工夫
            # Pモード画像に対し、パレットを明示的にセット
            new_img.putpalette(base_16_palette)
            
            # 7. ピクセルデータを流し込む
            new_img.putdata(pixel_data)
            
            # 8. 保存（ここでパレットを最適化）
            new_img.save(file_path, "PNG", palette=base_16_palette)
            return True
    except Exception as e:
        print(f"⚠️ エラー: {file_path} - {e}")
        return False

# 実行部分
for f in os.listdir(TARGET_DIR):
    if f.lower().endswith(".png"):
        force_save_16color_png(os.path.join(TARGET_DIR, f))