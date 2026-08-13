import csv
import io
import os
import sys
import requests
from PIL import Image
import warnings

# Pillowの将来の警告（DeprecationWarning）を非表示にする
warnings.filterwarnings("ignore", category=DeprecationWarning)

# ------------------ 設定 ------------------
SEARCH_IMAGE_PATH = "/Users/yu/Desktop/aaa.png"
ROM_PATH = '/Users/yu/Downloads/hodgepodge.gba'
OUTPUT_DIR = '/Users/yu/Desktop/extracted_results'
# -----------------------------------------

def rgb_to_gba_bgr555(r, g, b):
    """RGB888をGBA内部のBGR555形式（2バイト）に変換"""
    r5, g5, b5 = r >> 3, g >> 3, b >> 3
    val = r5 | (g5 << 5) | (b5 << 10)
    return bytes([val & 0xFF, (val >> 8) & 0xFF])

def gba_pal_to_rgb888(pal_data):
    """GBAのBGR555パレットデータをPILで扱えるRGB888形式に変換"""
    rgb_palette = []
    for i in range(0, len(pal_data), 2):
        val = pal_data[i] | (pal_data[i+1] << 8)
        r = (val & 0x1F) << 3
        g = ((val >> 5) & 0x1F) << 3
        b = ((val >> 10) & 0x1F) << 3
        rgb_palette.extend([r, g, b])
    while len(rgb_palette) < 768:
        rgb_palette.extend([0, 0, 0])
    return rgb_palette

def lz77_decompress_image(data, offset):
    """画像用：4096バイト(64x128)の連結ストリームを限界まで解凍する関数"""
    ptr = offset
    if ptr + 4 > len(data) or data[ptr] != 0x10: return None
    max_size = 4096
    ptr += 4
    out = bytearray()
    try:
        while ptr < len(data) and len(out) < max_size:
            flags = data[ptr]; ptr += 1
            for i in range(8):
                if len(out) >= max_size: break
                if flags & (0x80 >> i):
                    info = (data[ptr] << 8) | data[ptr+1]; ptr += 2
                    length = (info >> 12) + 3
                    disp = (info & 0x0FFF) + 1
                    back = len(out) - disp
                    for _ in range(length):
                        if len(out) >= max_size: break
                        out.append(out[back]); back += 1
                else:
                    out.append(data[ptr]); ptr += 1
        return bytes(out)
    except:
        return bytes(out) if len(out) >= 512 else None

def lz77_decompress_palette(data, offset):
    """パレット用：ヘッダー記載のサイズ(32Bなど)通りにキッチリ解凍する関数"""
    ptr = offset
    if ptr + 4 > len(data) or data[ptr] != 0x10: return None
    decomp_size = data[ptr+1] | (data[ptr+2] << 8) | (data[ptr+3] << 16)
    if decomp_size == 0 or decomp_size > 500: return None 
    ptr += 4
    out = bytearray()
    try:
        while len(out) < decomp_size:
            flags = data[ptr]; ptr += 1
            for i in range(8):
                if len(out) >= decomp_size: break
                if flags & (0x80 >> i):
                    info = (data[ptr] << 8) | data[ptr+1]; ptr += 2
                    length = (info >> 12) + 3
                    disp = (info & 0x0FFF) + 1
                    back = len(out) - disp
                    for _ in range(length):
                        out.append(out[back]); back += 1
                else:
                    out.append(data[ptr]); ptr += 1
        return bytes(out)
    except:
        return None

def main():
    if not os.path.exists(ROM_PATH):
        print(f"❌ ROMが見つかりません: {ROM_PATH}")
        return
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("--- ステップ1: 検索データ（下半分・完全一致用）の準備 ---")
    img_orig = Image.open(SEARCH_IMAGE_PATH).convert('P')
    
    # 画像の「真ん中半分から下（Y: 32〜63）」だけをGBAのタイル順バイナリに変換
    target_tile_bin = bytearray()
    for ty in range(32, 64, 8):  # Y座標32から開始（下半分32行分）
        for tx in range(0, 64, 8):
            for y in range(ty, ty + 8):
                for x in range(tx, tx + 8, 2):
                    target_tile_bin.append((img_orig.getpixel((x, y)) & 0x0F) | (img_orig.getpixel((x+1, y)) & 0x0F) << 4)
    target_tile_bin = bytes(target_tile_bin)
    
    print(f"🔑 生成された下半分検索キーのサイズ: {len(target_tile_bin)} バイト")

    raw_pal = img_orig.getpalette()
    target_pal_bin = b""
    for i in range(16):
        target_pal_bin += rgb_to_gba_bgr555(raw_pal[i*3], raw_pal[i*3+1], raw_pal[i*3+2])

    with open(ROM_PATH, 'rb') as f:
        rom_data = f.read()

    print("--- ステップ2: 条件指定・厳密アドレススキャン ---")
    img_addr = None
    decoded_img_data = None
    
    # 32x32ピクセル（512バイト）を境界とし、これより小さいサイズは対象外
    MIN_SIZE = 512 

    for addr in range(0, len(rom_data) - 4, 4):
        if rom_data[addr] == 0x10:
            decoded = lz77_decompress_image(rom_data, addr)
            
            if decoded:
                # 512B未満のデータサイズは一律でスキップ
                if len(decoded) < MIN_SIZE:
                    continue
                
                # 切り出した下半分バイナリが、解凍データ内に完全一致で含まれるか
                if target_tile_bin in decoded:
                    img_addr = addr
                    decoded_img_data = decoded
                    print(f"✨ 条件完全一致で画像アドレスを特定！: 0x{img_addr:X} (解凍サイズ: {len(decoded_img_data)}バイト)")
                    break

    if img_addr is None:
        print("❌ 条件に一致する画像アドレスがROM内から見つかりませんでした。")
        return

    print("--- ステップ3: パレットアドレスをスキャン中 ---")
    pal_addr = None
    decoded_pal_data = None
    search_pal_key = target_pal_bin[2:10] 

    for addr in range(0, len(rom_data) - 4, 4):
        if rom_data[addr] == 0x10:
            decoded = lz77_decompress_palette(rom_data, addr)
            if decoded and search_pal_key in decoded:
                pal_addr = addr
                decoded_pal_data = decoded
                print(f"🎨 パレットヒット！ アドレス: 0x{pal_addr:X}")
                break

    if decoded_pal_data is None:
        print("❌ パレットがROM内に見つかりませんでした。")
        return

    print("--- ステップ4: 特定したアドレスから【前半（通常画像）】を生成中 ---")
    final_pal = gba_pal_to_rgb888(decoded_pal_data)
    img = Image.new('P', (64, 64))
    img.putpalette(final_pal)

    # 🌟修正：前半（通常正面画像）を抽出するため、データ先頭（0）から読み込みを開始する
    print("💡 先頭（0バイト目）から読み込み、前半の【通常正面画像】を切り出します。")
    ptr = 0

    for ty in range(0, 64, 8):
        for tx in range(0, 64, 8):
            for y in range(ty, ty + 8):
                for x in range(tx, tx + 8, 2):
                    if ptr < len(decoded_img_data):
                        byte = decoded_img_data[ptr]; ptr += 1
                        img.putpixel((x, y), byte & 0x0F)
                        img.putpixel((x+1, y), (byte >> 4) & 0x0F)

    # 保存ファイル名とログを通常正面画像（normal）として出力
    out_path = os.path.join(OUTPUT_DIR, f"normal_color_0x{img_addr:X}.png")
    img.save(out_path, transparency=0)
    
    print("\n" + "="*30)
    print(f"  結果確定画像アドレス: 0x{img_addr:X}")
    print(f"  結果確定パレットアドレス: 0x{pal_addr:X}")
    print(f"  保存先: {out_path}")
    print("="*30)

if __name__ == "__main__":
    main()