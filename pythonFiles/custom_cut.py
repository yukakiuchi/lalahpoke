import os
from PIL import Image

# ------------------ 設定 ------------------
SOURCE_DIR = "/Users/yu/Desktop/edit_png"
OUTPUT_DIR = "/Users/yu/Desktop/cut"
# ------------------------------------------

def split_images():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    files = sorted([f for f in os.listdir(SOURCE_DIR) if f.lower().endswith(".png")])
    
    print(f"取得元フォルダー: {SOURCE_DIR}")
    print(f"出力先フォルダー: {OUTPUT_DIR}")
    print("-" * 30)

    for filename in files:
        file_path = os.path.join(SOURCE_DIR, filename)
        try:
            with Image.open(file_path) as img:
                img = img.convert('P')
                full_pal = img.getpalette()
                
                # パレット分離（各16色=48bytes）
                pal_norm_data = full_pal[0:48]
                pal_shiny_data = full_pal[48:96]
                
                cols = img.width // 64
                base_name = os.path.splitext(filename.replace("_combined", ""))[0]

                for c in range(cols):
                    part = img.crop((c * 64, 0, (c + 1) * 64, 64))
                    
                    if c % 2 == 1:
                        part = part.point(lambda p: p - 16 if p >= 16 else 0)
                        current_pal_data = pal_shiny_data
                    else:
                        current_pal_data = pal_norm_data
                    
                    # 16色パレットを適用
                    part.putpalette(list(current_pal_data) + ([0] * (768 - 48)))
                    
                    # 【重要】パレットの登録数を16色(48bytes)に強制カット
                    part.palette.palette = bytes(current_pal_data)
                    
                    new_filename = f"{base_name}_{c+1}.png"
                    part.save(os.path.join(OUTPUT_DIR, new_filename), transparency=0)
                    print(f"分割出力: {new_filename} (16色パレット限定済)")
                    
        except Exception as e:
            print(f"エラー発生: {filename} - {e}")

    print("-" * 30)
    print("🚀 16色に限定した分割処理が完了しました。")

if __name__ == "__main__":
    split_images()