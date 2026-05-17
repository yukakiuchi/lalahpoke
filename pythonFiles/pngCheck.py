import os
from PIL import Image

def normalize_sprite_by_groups(file_path):
    target_bg_rgb = (166, 210, 171)
    
    try:
        # RGBAで開いて透明度を正しく判定する
        with Image.open(file_path).convert("RGBA") as img:
            # 1. 背景色の判定ロジック
            r, g, b, a = img.getpixel((0, 0))
            
            # アルファ値が0に近いなら透明とみなす
            if a < 128:
                bg_color = target_bg_rgb
            else:
                bg_color = (r, g, b)
            
            # 再処理用にRGBへ変換
            img_rgb = img.convert("RGB")
            width, height = img.size
            num_blocks = width // 64
            
            # 各グループの使用色抽出
            def get_used_colors(indices):
                colors = {bg_color}
                for i in indices:
                    if i < num_blocks:
                        colors.update(set(img_rgb.crop((i * 64, 0, (i + 1) * 64, 64)).getdata()))
                
                # 背景色をリストの先頭に固定
                color_list = [bg_color] + [c for c in colors if c != bg_color]
                return color_list[:16]

            pal_a_list = get_used_colors([0, 2, 4])
            pal_b_list = get_used_colors([1, 3])
            
            # パレット構築
            full_pal_list = pal_a_list + pal_b_list
            full_pal = [val for rgb in full_pal_list for val in rgb]
            
            # 画像構築
            final_img = Image.new("P", (width, height))
            final_img.putpalette(full_pal)
            
            rgb_to_idx = {rgb: i for i, rgb in enumerate(full_pal_list)}
            
            for i in range(num_blocks):
                block_rgb = img_rgb.crop((i * 64, 0, (i + 1) * 64, 64))
                pixels = list(block_rgb.getdata())
                
                offset = 0 if i in [0, 2, 4] else len(pal_a_list)
                # 使用色以外は必ずグループ内の背景色(オフセット)へ
                remapped = [rgb_to_idx.get(p, offset) for p in pixels]
                
                b_img = Image.new("P", (64, 64))
                b_img.putdata(remapped)
                final_img.paste(b_img, (i * 64, 0))
            
            final_img.save(file_path, "PNG", optimize=False)
            print(f"成功: {os.path.basename(file_path)} (背景設定: {bg_color})")

    except Exception as e:
        print(f"エラー: {file_path} - {e}")

def process_all_images(folder_path):
    files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(".png")])
    for filename in files:
        file_path = os.path.join(folder_path, filename)
        normalize_sprite_by_groups(file_path)

if __name__ == "__main__":
    FOLDER_PATH = "/Users/yu/Downloads/最新ずかん/"
    if os.path.exists(FOLDER_PATH):
        process_all_images(FOLDER_PATH)
        print("--- 全ての画像の処理が完了しました ---")