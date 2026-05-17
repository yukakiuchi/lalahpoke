import os
import sys
import subprocess
from PIL import Image
from collections import defaultdict

# ------------------ 設定 ------------------
INPUT_DIR = "/Users/yu/Desktop/edit_png"
OUTPUT_DIR = "/Users/yu/Desktop/combined"
# ------------------------------------------

def open_folder_and_exit(target_dir):
    """ 処理完了後にフォルダをUIで開き、スクリプトを終了する """
    print(f"\n📂 出力フォルダを自動で開きます: {target_dir}")
    if sys.platform == "darwin":  # Mac
        subprocess.run(["open", target_dir])
    elif sys.platform == "win32":  # Windows
        os.startfile(target_dir)
    else:  # Linux等
        subprocess.run(["xdg-open", target_dir])
    sys.exit(0)

def pad_palette_to_16(palette_list):
    """ 16色(48要素)に満たない場合はマゼンタ(255,0,255)で埋める """
    target_len = 48
    if len(palette_list) < target_len:
        missing_colors = (target_len - len(palette_list)) // 3
        for _ in range(missing_colors):
            palette_list.extend([255, 0, 255]) 
    return palette_list[:48]

def process_and_sanitize_image(img_path, filename):
    """ 
    画像の色数を確認し、GBA互換（最大16色、0番透過）になるよう調整する関数
    """
    img = Image.open(img_path).convert('P')
    
    # getcolors()で実際にピクセルとして使われている色数を取得
    unique_colors = img.getcolors()
    actual_color_count = len(unique_colors) if unique_colors else 0
    
    # パレットリストを取得 (RGBのフラットリスト)
    raw_palette = img.getpalette()
    if not raw_palette:
        raw_palette = [0] * 768

    # 1. 16色ぴったりなら何もしない
    if actual_color_count == 16:
        return img

    # 2. 15色以下の場合はマゼンタ補完（ログ表示用）
    elif actual_color_count <= 15:
        print(f" ⚠️  [警告] {filename} (色数: {actual_color_count}) ➔ マゼンタで16色に補完しました。")
        return img

    # 3. 17色ぴったりの場合（(0,0)の背景色を0番に持ってくるリマップ処理）
    elif actual_color_count == 17:
        # 左上 (0,0) のピクセルが指すパレットインデックスを取得
        bg_index = img.getpixel((0, 0))
        
        if bg_index != 0:
            # ピクセルデータをリマップ（入れ替え）する
            # 元のbg_indexだった場所は0に、元々0だった場所（不使用）はbg_indexに変換
            remap_table = list(range(256))
            remap_table[bg_index] = 0
            remap_table[0] = bg_index
            img = img.point(remap_table)
            
            # パレット（色見本）側もインデックス0番とbg_index番を入れ替える
            # RGBが3要素ずつ並んでいるので、3倍してスライスを入れ替え
            p_copy = list(raw_palette)
            idx0_rgb = p_copy[0:3]
            bg_rgb = p_copy[bg_index*3 : bg_index*3+3]
            
            p_copy[0:3] = bg_rgb
            p_copy[bg_index*3 : bg_index*3+3] = idx0_rgb
            img.putpalette(p_copy)
            
            print(f" 🛠️  [調整] {filename} (色数: 17) ➔ (0,0)の背景色(元Index:{bg_index})をIndex:0番にリマップ調整しました。")
        else:
            print(f" ⚠️  [警告] {filename} (色数: 17) ➔ すでに(0,0)がIndex:0でした。17色目は強制カットされます。")
        
        return img

    # 4. 18色以上の場合（17色目以降のインデックスを強制的に削ぎ落とす）
    else:
        # ピクセル値が15（16色目）を超えるものは、強制的に15に丸める（減色）
        sanitized_img = img.point(lambda p: min(p, 15))
        print(f" 🚨 [削減] {filename} (色数: {actual_color_count}) ➔ 17色目以降を強制削除（最大16色へ減色）しました。")
        return sanitized_img

def combine_images():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    groups = defaultdict(list)
    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".png")]

    if not files:
        print(f"取得元フォルダー: {INPUT_DIR} に画像が見つかりません。")
        return

    print(f"📂 取得元フォルダー: {INPUT_DIR}")
    print(f"📂 出力先フォルダー: {OUTPUT_DIR}")
    print("-" * 50)

    for f in files:
        if "_" in f:
            prefix = f.split("_")[0]
            groups[prefix].append(f)

    for prefix, member_files in groups.items():
        member_files.sort()
        
        raw_images = []
        for f in member_files:
            # 🎨 ここで各画像の色数チェック＆バリデーション・リマップを実行
            img = process_and_sanitize_image(os.path.join(INPUT_DIR, f), f)
            raw_images.append(img)

        # 2枚しかない場合は 0101 の順に並べる
        if len(raw_images) == 2:
            images = [raw_images[0], raw_images[1], raw_images[0], raw_images[1]]
        else:
            images = raw_images

        # 各パレットを取得し、必ず16色(48bytes)になるように補完
        p1 = pad_palette_to_16(images[0].getpalette()[:48])
        p2 = pad_palette_to_16(images[1].getpalette()[:48])
        
        # 結合パレット (32色 / 96bytes)
        combined_palette_data = p1 + p2

        total_width = sum(img.width for img in images)
        max_height = max(img.height for img in images)

        combined_img = Image.new("P", (total_width, max_height))
        full_palette = combined_palette_data + ([0] * (768 - len(combined_palette_data)))
        combined_img.putpalette(full_palette)

        current_x = 0
        for i, img in enumerate(images):
            # インデックスが奇数の画像（Shiny等）はパレット番号を+16シフト
            if i % 2 == 1:
                # 0(背景/透過)は維持し、1〜15の範囲をシフト
                # 18色以上だった場合でも、前段で15以下に丸められているので安全
                shifted_img = img.point(lambda p: p + 16 if 0 < p <= 15 else 0)
                combined_img.paste(shifted_img, (current_x, 0))
            else:
                combined_img.paste(img, (current_x, 0))
            current_x += img.width

        # ファイル保存時にパレットデータを32色(96bytes)に強制カット
        combined_img.palette.palette = bytes(combined_palette_data)
        
        save_name = f"{prefix}_combined.png"
        # 0番を透明として扱う
        combined_img.save(os.path.join(OUTPUT_DIR, save_name), transparency=0)
        print(f" ✅ 結合出力成功 ➔ {save_name}\n")

    print("-" * 50)
    print("✨ すべての結合処理が正常に完了しました。")
    
    # 📂 【追加】出力したフォルダをUIで開き、プログラムを終了する
    open_folder_and_exit(OUTPUT_DIR)

if __name__ == "__main__":
    combine_images()