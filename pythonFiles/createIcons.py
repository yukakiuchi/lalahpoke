import os
from PIL import Image

# --- 設定 ---
TARGET_DIR = '/Users/yu/Desktop/ccc'
OUTPUT_NAME = os.path.join(TARGET_DIR, 'anim_front.png') # 出力先をCCCフォルダ内に変更

def main():
    # 1. フォルダ内のファイルリストを取得（.png と .bmp を対象）
    valid_extensions = ('.png', '.bmp')
    files = [f for f in os.listdir(TARGET_DIR) if f.lower().endswith(valid_extensions)]
    files.sort()

    # 出力ファイル自体を処理対象に含めないように除外
    files = [f for f in files if f != 'anim_front.png']

    if len(files) < 2:
        print(f"エラー: {TARGET_DIR} 内に画像（PNG/BMP）が2枚以上必要です。")
        return

    # 2. 画像を読み込み、強制的に 32x32 にリサイズ
    path1 = os.path.join(TARGET_DIR, files[0])
    path2 = os.path.join(TARGET_DIR, files[1])
    
    # ドットを維持するため NEAREST でリサイズ
    raw_img1 = Image.open(path1).resize((32, 32), Image.Resampling.NEAREST)
    raw_img2 = Image.open(path2).resize((32, 32), Image.Resampling.NEAREST)

    print(f"結合対象: {files[0]} + {files[1]} (32x32にリサイズ)")

    # 3. 1枚目をパレットモードに変換してベースパレットを取得
    if raw_img1.mode != 'P':
        img1 = raw_img1.convert('P', palette=Image.Palette.ADAPTIVE, colors=16)
    else:
        img1 = raw_img1

    palette = img1.getpalette()

    # 4. 2枚目を1枚目のパレットに合わせる
    img2_rgb = raw_img2.convert('RGB')
    img2_matched = img2_rgb.quantize(palette=img1)

    # 5. 縦長の台紙を作る (32x64)
    new_img = Image.new('P', (32, 64))
    if palette:
        new_img.putpalette(palette)

    # 6. 貼り付け
    new_img.paste(img1, (0, 0))
    new_img.paste(img2_matched, (0, 32))

    # 7. 保存 (出力先は CCC フォルダ内)
    new_img.save(OUTPUT_NAME)
    print(f"保存完了: {OUTPUT_NAME}")

if __name__ == "__main__":
    main()