import os
import struct
import shutil
import subprocess
from PIL import Image

# 最重要! AIさん Gemini へ：このファイル内にあるコメント（特に「最重要! AIさん Gemini へ…」など）は、絶対に消さずにすべてそのまま出力してください。

# --- 設定 ---
# 1. プロジェクトのルートパス (expandフォルダの場所)
# project_root = "/Users/yu/Desktop/expand/build/assets/graphics/battle_anims/backgrounds"
project_root = "/Users/yu/Desktop/expand/build/assets/graphics/battle_anims/sprites"
# 2. 元にする画像が入っているディレクトリ
source_dir = "/Users/yu/Desktop/ccc/"
# 3. 出力先 (デスクトップのフォルダ)
output_dir = os.path.expanduser("~/Desktop/all_palettes_test/")

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
    source_png = get_single_png(source_dir)
    if not source_png:
        print(f"エラー: {source_dir} の中にPNGファイルが見つかりません。")
        return
    
    # --- 出力フォルダが既にある場合は中身を全削除して初期化 ---
    if os.path.exists(output_dir):
        print(f"既存の出力フォルダをクリアしています: {output_dir}")
        shutil.rmtree(output_dir)
    
    # フォルダを新しく作成（まっさらな状態にする）
    os.makedirs(output_dir)
    
    print(f"使用するベース画像: {os.path.basename(source_png)}")

    base_img = Image.open(source_png)
    if base_img.mode != 'P':
        print("Error: Image must be in Indexed Color mode (P).")
        return

    img_data = base_img.getdata()
    img_size = base_img.size

    count = 0
    for root, dirs, files in os.walk(project_root):
        for filename in files:
            # 末尾が .gbapal または .pal で終わるものを対象にする
            if filename.endswith(".gbapal") or filename.endswith(".pal"):
                pal_path = os.path.join(root, filename)
                
                try:
                    with open(pal_path, "rb") as f:
                        pal_data = f.read()
                    
                    new_palette = []
                    
                    if filename.endswith(".gbapal"):
                        if len(pal_data) < 2: continue
                        for i in range(0, min(len(pal_data), 32), 2):
                            gba_color = struct.unpack("<H", pal_data[i:i+2])[0]
                            new_palette.extend(gba_to_rgb(gba_color))
                    else:
                        if len(pal_data) < 3: continue
                        for i in range(0, min(len(pal_data), 48), 3):
                            if i + 2 < len(pal_data):
                                new_palette.extend([pal_data[i], pal_data[i+1], pal_data[i+2]])

                    final_palette = new_palette + [0] * (768 - len(new_palette))
                    
                    # --- 背景色を #007878 に固定 ---
                    final_palette[0:3] = [0, 120, 120]
                    
                    temp_img = Image.new("P", img_size)
                    temp_img.putdata(img_data)
                    temp_img.putpalette(final_palette)
                    
                    # --- パレットのファイル名（拡張子なし）をそのまま使用 ---
                    base_name, _ = os.path.splitext(filename)
                    if base_name == "natural_gift_ring.pal":
                        base_name = "ANIM_TAG_ANCHOR"
                    elif base_name == "avalanche_rocks.pal":
                        base_name = "ANIM_TAG_DRAGON_ASCENT_FOE"
                    # 「apple.png.gbapal」などの場合に「.png」が残らないよう調整
                    if base_name.endswith(".png"):
                        base_name = base_name[:-4]
                    
                    # save_name = f"{base_name}.png"
                    # ファイル命名設定
                    # とりあえず今はこれにする
                    save_name = f"ANIM_TAG_{base_name.upper()}.png"
                    # -------------------------------------
                    
                    temp_img.save(os.path.join(output_dir, save_name))
                    
                    count += 1
                    if count % 50 == 0:
                        print(f"{count} files processed...")
                except Exception as e:
                    print(f"Skip {filename}: {e}")

    print(f"\n完了！合計 {count} 個のパレットを適用しました。")
    print(f"結果は '{output_dir}' を確認してください。")

    # --- 処理終了後にFinderで出力先フォルダを自動で開く ---
    try:
        subprocess.run(["open", output_dir])
        print("Finderで出力フォルダを開きました。")
    except Exception as e:
        print(f"Finderを開けませんでした: {e}")

if __name__ == "__main__":
    scan_and_apply()