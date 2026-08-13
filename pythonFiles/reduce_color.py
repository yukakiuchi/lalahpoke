import os
import subprocess
from PIL import Image

FILE_PATH = "/Users/yu/Desktop/DREAM_DEXXXggggg"
OUTPUT_PATH = "/Users/yu/Desktop/DREAM_DEXXX_fffresult"

def main():
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    
    files = [f for f in os.listdir(FILE_PATH) if f.lower().endswith('.png')]
    
    for filename in files:
        filepath = os.path.join(FILE_PATH, filename)
        outpath = os.path.join(OUTPUT_PATH, filename)
        
        try:
            with Image.open(filepath) as img:
                # 1. 画像をパレットモード(P)に変換
                # パレットが16色以下になるように減色処理を適用
                img_p = img.convert("P", palette=Image.ADAPTIVE, colors=16)
                
                # 2. パレットを先頭16色に整理（念のため）
                palette = img_p.getpalette()
                new_palette = palette[:48] + [0] * (768 - 48)
                img_p.putpalette(new_palette)
                
                # 3. 透過色の処理がある場合はインデックスを補正
                # (bits=4にするため、インデックス16以上は全て強制的にインデックス0に変換)
                pixels = list(img_p.getdata())
                new_pixels = [p if p < 16 else 0 for p in pixels]
                img_p.putdata(new_pixels)
                
                # 4. ここが最重要：bits=4で保存
                # Pillowはこのオプションを指定すると、PLTEチャンクを適切なサイズにし、
                # ピクセルデータも4ビットパッキングで生成します。
                img_p.save(outpath, format="PNG", bits=4, optimize=False)
                
                print(f"✅ 成功: {filename}")
                
        except Exception as e:
            print(f"❌ エラー ({filename}): {e}")

    # 処理終了後にFinderを開く
    subprocess.call(["open", OUTPUT_PATH])

if __name__ == "__main__":
    main()