import os
from PIL import Image

# --- 設定 ---
TARGET_DIR = '/Users/yu/Desktop/ccc'
OUTPUT_NAME = 'anim_front.png'

def main():
    # 1. フォルダ内のファイルリストを取得（.png のみ）
    files = [f for f in os.listdir(TARGET_DIR) if f.lower().endswith('.png')]
    files.sort()  # 名前順に並び替え

    if len(files) < 2:
        print(f"エラー: {TARGET_DIR} 内に画像が2枚以上必要です。")
        return

    # 2. 画像を読み込む（リストの最初から2つを使用）
    path1 = os.path.join(TARGET_DIR, files[0])
    path2 = os.path.join(TARGET_DIR, files[1])
    
    img1 = Image.open(path1)
    img2 = Image.open(path2)

    print(f"結合対象: {files[0]} + {files[1]}")

    # 3. 1枚目のパレット情報を取得
    palette = img1.getpalette()

    # 4. 縦長の「パレットモード(P)」の台紙を作る
    # 64x64が2枚なので 64x128
    new_img = Image.new('P', (64, 128))
    if palette:
        new_img.putpalette(palette)

    # 5. 貼り付け
    new_img.paste(img1, (0, 0))
    new_img.paste(img2, (0, 64))

    # 6. 保存
    new_img.save(OUTPUT_NAME)
    print(f"保存完了: {OUTPUT_NAME}")

if __name__ == "__main__":
    main()