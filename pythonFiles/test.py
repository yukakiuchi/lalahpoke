import os
import re
from PIL import Image

# ------------------ 設定 ------------------
# 画像が入っているフォルダを指定
INPUT_FOLDER = "/Users/yu/Desktop/cut_result_0"
OUTPUT_FOLDER = "/Users/yu/Desktop/remapped"

# パレット定義（ユーザー様の定義を使用）
PALETTES = {
    0: [(98, 156, 131), (115, 115, 115), (189, 189, 189), (255, 255, 255), (123, 156, 74), (156, 205, 74), (148, 246, 74), (238, 115, 156), (246, 148, 246), (189, 164, 90), (246, 230, 41), (246, 246, 172), (213, 213, 106), (230, 74, 41), (98, 98, 90), (65, 65, 65)],
    1: [(98, 156, 131), (131, 131, 115), (189, 189, 189), (255, 255, 255), (189, 164, 65), (246, 246, 41), (213, 98, 65), (246, 148, 41), (139, 123, 255), (98, 74, 205), (238, 115, 156), (255, 180, 164), (164, 197, 255), (106, 172, 156), (98, 98, 90), (65, 65, 65)],
    2: [(98, 156, 131), (123, 123, 123), (189, 189, 180), (255, 255, 255), (115, 115, 205), (164, 172, 246), (180, 131, 90), (238, 197, 139), (197, 172, 41), (246, 246, 41), (246, 98, 82), (148, 123, 205), (197, 164, 205), (189, 41, 156), (98, 98, 90), (65, 65, 65)],
    3: [(98, 156, 131), (115, 115, 115), (189, 189, 189), (255, 255, 255), (65, 106, 148), (98, 148, 164), (164, 197, 255), (238, 115, 156), (213, 98, 65), (189, 164, 90), (246, 230, 41), (246, 246, 172), (213, 213, 106), (246, 148, 41), (98, 98, 90), (65, 65, 65)],
    4: [(98, 156, 131), (115, 115, 115), (189, 189, 189), (255, 255, 255), (123, 156, 74), (156, 205, 74), (65, 106, 148), (238, 115, 156), (246, 148, 246), (189, 164, 90), (246, 246, 139), (164, 197, 255), (98, 148, 164), (213, 98, 65), (98, 98, 90), (65, 65, 65)],
    5: [(98, 156, 131), (123, 123, 123), (189, 189, 180), (255, 255, 255), (123, 156, 74), (156, 205, 74), (180, 131, 90), (238, 197, 139), (197, 172, 41), (246, 246, 41), (213, 98, 65), (148, 123, 205), (197, 164, 205), (246, 148, 41), (98, 98, 90), (65, 65, 65)]
}
# ------------------------------------------

def get_pil_palette(rgb_list):
    """16色のRGBリストをPillow形式(768個のフラットなリスト)に変換する"""
    flat_palette = []
    for r, g, b in rgb_list:
        flat_palette.extend([r, g, b])
    # 256色分(768個)に満たない場合は黒で埋める
    flat_palette.extend([0] * (768 - len(flat_palette)))
    return flat_palette

def remap_and_save_as_p(input_path, output_path, pal_index):
    try:
        # 画像を開く
        img_raw = Image.open(input_path)
        
        # アルファチャンネル(透過)がある場合は背景色と合成
        if img_raw.mode == 'RGBA':
            bg_color = PALETTES[pal_index][0]
            bg = Image.new("RGB", img_raw.size, bg_color)
            bg.paste(img_raw, mask=img_raw.split()[3])
            img_rgb = bg
        else:
            img_rgb = img_raw.convert("RGB")

        # 対象パレットを取得
        target_rgb_colors = PALETTES.get(pal_index)
        
        # 1. パレット用のダミー画像を作成してパレットを読み込ませる
        # 16色パレットのデータを準備
        flat_palette = []
        for r, g, b in target_rgb_colors:
            flat_palette.extend([r, g, b])
        flat_palette.extend([0] * (768 - len(flat_palette)))
        
        pal_img = Image.new("P", (1, 1))
        pal_img.putpalette(flat_palette)

        # 2. quantizeを実行（エラーが出ていた DITHER.NONE の代わりに）
        # dither を 0 (無効) に設定
        remapped_img = img_rgb.quantize(palette=pal_img, dither=0)

        # 保存
        remapped_img.save(output_path)
        print(f"✅ Saved (P-mode): {output_path}")

    except Exception as e:
        print(f"⚠️ Error processing {input_path}: {e}")

def process_folder():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    print(f"Processing images in: {INPUT_FOLDER}")
    print(f"Saving remapped images to: {OUTPUT_FOLDER}\n")

    # ファイル名をID順にソートして処理（任意）
    filenames = sorted(os.listdir(INPUT_FOLDER))

    processed_count = 0
    for filename in filenames:
        if filename.endswith(".png"):
            # 正規表現でファイル名からIDとパレット指定数字を抽出
            # 例: 001_2_cut.png -> group1='001', group2='2'
            match = re.search(r'(\d+)_(\d+)_.*\.png', filename)
            
            if match:
                try:
                    poke_id = match.group(1)
                    file_pal_num = int(match.group(2))
                    
                    # ユーザー様のルール: ファイル名の数字 - 1 = パレット番号
                    # "001_2_cut.png" -> Palette 1
                    target_pal_idx = file_pal_num - 1
                    
                    input_path = os.path.join(INPUT_FOLDER, filename)
                    # 出力ファイル名を作成
                    output_path = os.path.join(OUTPUT_FOLDER, filename)
                    
                    remap_and_save_as_p(input_path, output_path, target_pal_idx)
                    processed_count += 1
                except ValueError:
                    continue
    
    print(f"\n🏁 Finished. Processed {processed_count} images.")

# 実行
if __name__ == "__main__":
    process_folder()