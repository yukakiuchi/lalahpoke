import os
from PIL import Image

# --- 設定 ---
TARGET_FILE = "/Users/yu/Desktop/pokemon_icons/022.png"
OUTPUT_NAME = "icon6.pal" # .pal に変更！
# -----------

def png_to_jasc_pal(file_path):
    try:
        img = Image.open(file_path)
        if img.mode != 'P':
            img = img.convert('P', palette=Image.ADAPTIVE, colors=256)
        
        palette = img.getpalette()
        if not palette:
            print("パレット情報がありません")
            return

        # ターゲットディレクトリを取得
        target_dir = os.path.dirname(file_path)
        output_path = os.path.join(target_dir, OUTPUT_NAME)

        with open(output_path, "w", newline='\n') as f:
            # JASC-PAL ヘッダー
            f.write("JASC-PAL\n")
            f.write("0100\n")
            
            # 色数 (16の倍数に切り上げ)
            total_colors = len(palette) // 3
            output_color_count = ((total_colors + 15) // 16) * 16
            f.write(f"{output_color_count}\n")
            
            # 各色を出力
            for i in range(output_color_count):
                if i < total_colors:
                    r, g, b = palette[i*3], palette[i*3+1], palette[i*3+2]
                    f.write(f"{r} {g} {b}\n")
                else:
                    # 埋め草用の黒色
                    f.write("0 0 0\n")

        print(f"生成完了: {output_path}")

    except Exception as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    png_to_jasc_pal(TARGET_FILE)