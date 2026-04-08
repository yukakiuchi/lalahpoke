import os
from PIL import Image
import struct

# --- 設定 ---
# 処理したい【画像ファイル】のフルパスをここに入れる
TARGET_FILE = "/Users/yu/Desktop/expand/graphics/battle_environment/cave/night_tiles.png"
# 出力ファイル名（固定）
OUTPUT_NAME = "nightPalette.gbapal"
# -----------

def color_to_gba_binary(r, g, b):
    """RGB888をGBA用の16bitバイナリに変換"""
    r_5bit = r // 8
    g_5bit = g // 8
    b_5bit = b // 8
    gba_color = (r_5bit) | (g_5bit << 5) | (b_5bit << 10)
    return struct.pack('<H', gba_color)

def png_to_gbapal(file_path):
    try:
        if not os.path.exists(file_path):
            print(f"エラー: ファイルが見つかりません -> {file_path}")
            return

        img = Image.open(file_path)
        
        # パレットモードでない場合は変換
        if img.mode != 'P':
            img = img.convert('P', palette=Image.ADAPTIVE, colors=256)
        
        palette_data = img.getpalette()
        if not palette_data:
            print(f"スキップ: パレット情報がありません -> {file_path}")
            return

        # 色数を取得し、GBAの16色スロット単位(16の倍数)に切り上げる
        total_colors = len(palette_data) // 3
        output_color_count = ((total_colors + 15) // 16) * 16

        # --- 修正箇所：出力先ディレクトリを取得し、固定ファイル名を結合 ---
        target_dir = os.path.dirname(file_path)
        output_path = os.path.join(target_dir, OUTPUT_NAME)
        # -----------------------------------------------------------

        with open(output_path, "wb") as f:
            for i in range(output_color_count):
                idx = i * 3
                if idx + 2 < len(palette_data):
                    r, g, b = palette_data[idx], palette_data[idx+1], palette_data[idx+2]
                    f.write(color_to_gba_binary(r, g, b))
                else:
                    f.write(struct.pack('<H', 0x0000))

        print("-" * 30)
        print(f"生成完了: {OUTPUT_NAME}")
        print(f"保存場所: {target_dir}")
        print(f"色数: {output_color_count} colors")
        print("-" * 30)

    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    png_to_gbapal(TARGET_FILE)