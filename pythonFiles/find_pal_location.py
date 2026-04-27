import os
import struct
from PIL import Image

# ==========================================
# 設定エリア (ここを変更してください)
# ==========================================
# あなたが持っている、色が完璧なターゲット画像のパス
INPUT_PNG_PATH = '/Users/yu/Downloads/GLIMMORA_SHINY.png' 
# 対象とするGBA ROMのパス
ROM_PATH = '/Users/yu/Downloads/Z (v1.2.0).gba'
# 出力ファイル名の接頭辞
OUTPUT_PREFIX = 'extracted_pokemon'
# ==========================================

def lz77_decompress_gba(data, offset):
    """GBA BIOS形式のLZ77を解凍 (展開後のサイズ制限付きで高速化)"""
    try:
        ptr = offset
        if data[ptr] != 0x10: return None
        decomp_size = data[ptr+1] | (data[ptr+2] << 8) | (data[ptr+3] << 16)
        
        # 今回の対象(64x64 4bpp)は2048byte。
        # パレットは32byte以上。極端に大きいデータは無視して高速化。
        if decomp_size == 0 or decomp_size > 4096: return None
        
        ptr += 4
        out = bytearray()
        while len(out) < decomp_size:
            if ptr >= len(data): break
            flags = data[ptr]
            ptr += 1
            for i in range(8):
                if len(out) >= decomp_size: break
                if flags & (0x80 >> i):
                    if ptr + 1 >= len(data): break
                    info = (data[ptr] << 8) | data[ptr+1]
                    ptr += 2
                    length = (info >> 12) + 3
                    disp = (info & 0x0FFF) + 1
                    back = len(out) - disp
                    if back < 0: return None # 解凍エラー
                    for _ in range(length):
                        out.append(out[back])
                        back += 1
                else:
                    if ptr >= len(data): break
                    out.append(data[ptr])
                    ptr += 1
        return out
    except:
        return None

def png_to_gba_palette(image_path):
    """PNGからGBA用BGR555パレット(32byte)を抽出"""
    img = Image.open(image_path).convert('P')
    palette = img.getpalette()
    gba_pal = bytearray()
    for i in range(16):
        r, g, b = palette[i*3 : i*3+3]
        r5, g5, b5 = r >> 3, g >> 3, b >> 3
        color = (b5 << 10) | (g5 << 5) | r5
        gba_pal.append(color & 0xFF)
        gba_pal.append((color >> 8) & 0xFF)
    return gba_pal

def png_to_gba_pixels(image_path):
    """PNGからGBA用4bppタイル画素データを抽出"""
    img = Image.open(image_path).convert('P')
    width, height = img.size
    if width != 64 or height != 64:
        raise ValueError("画像サイズは64x64ピクセルである必要があります。")
    pixels = list(img.getdata())
    gba_data = bytearray()
    for tile_y in range(0, 64, 8):
        for tile_x in range(0, 64, 8):
            for y in range(tile_y, tile_y + 8):
                for x in range(tile_x, tile_x + 8, 2):
                    p1 = pixels[y * 64 + x] & 0x0F
                    p2 = pixels[y * 64 + (x + 1)] & 0x0F
                    gba_data.append((p2 << 4) | p1)
    return gba_data

def gba_pal_to_rgb(pal_bytes):
    """BGR555をPIL用RGBパレットに変換"""
    colors = []
    for i in range(0, len(pal_bytes), 2):
        if i + 1 >= len(pal_bytes): break
        val = pal_bytes[i] | (pal_bytes[i+1] << 8)
        r = (val & 0x1F) << 3
        g = ((val >> 5) & 0x1F) << 3
        b = ((val >> 10) & 0x1F) << 3
        colors.extend([r, g, b])
    return colors

def save_indexed_png(pixel_data, pal_bytes, output_path):
    """画素データとパレットを組み合わせてPNGを保存"""
    img = Image.new('P', (64, 64))
    rgb_palette = gba_pal_to_rgb(pal_bytes)
    img.putpalette(rgb_palette + [0] * (768 - len(rgb_palette)))
    ptr = 0
    for tile_y in range(0, 64, 8):
        for tile_x in range(0, 64, 8):
            for y in range(tile_y, tile_y + 8):
                for x in range(tile_x, tile_x + 8, 2):
                    if ptr >= len(pixel_data): break
                    byte = pixel_data[ptr]; ptr += 1
                    # タイル形式をピクセル座標に変換
                    # リトルエンディアン: 下位4bitが左、上位4bitが右
                    img.putpixel((tile_x + (x % 8), tile_y + (y % 8)), byte & 0x0F)
                    img.putpixel((tile_x + (x % 8) + 1, tile_y + (y % 8)), byte >> 4)
    img.save(output_path)
    print(f"  -> PNG保存完了: {output_path}")

# ==========================================
# メイン処理
# ==========================================
def main():
    if not os.path.exists(INPUT_PNG_PATH) or not os.path.exists(ROM_PATH):
        print("エラー: 入力画像またはROMファイルが見つかりません。パスを確認してください。")
        return

    print(f"--- GBA ROM 圧縮データ自動解析ツール ---")
    print(f"入力画像: {INPUT_PNG_PATH}")
    print(f"対象ROM: {ROM_PATH}")

    # 1. 入力PNGから検索ターゲットを抽出
    print("\n[1/3] 入力画像を解析中...")
    target_pixels = png_to_gba_pixels(INPUT_PNG_PATH)
    target_palette = png_to_gba_palette(INPUT_PNG_PATH)
    
    # 比較用の一部（透明な余白を避ける）
    pixel_match_part = target_pixels[800:1000] # 画像中央付近の200バイト
    pal_match_part = target_palette[4:20]      # パレットの3〜10色目付近

    # 2. ROM内を総当たりスキャン
    print("\n[2/3] ROM内の圧縮データをスキャン中... (時間がかかります)")
    with open(ROM_PATH, 'rb') as f:
        rom_data = f.read()

    found_img_addr = None
    found_pal_addr = None
    decoded_pixel_data = None
    decoded_pal_data_full = None

    # 4バイト境界ごとにLZ77ヘッダー(10)を探す
    for offset in range(0, len(rom_data) - 4, 4):
        if rom_data[offset] == 0x10:
            decoded = lz77_decompress_gba(rom_data, offset)
            if not decoded: continue

            # 画像の特定 (解凍後2048バイト)
            if not found_img_addr and len(decoded) == 2048:
                if pixel_match_part in decoded:
                    print(f"  >> 【画像発見！】アドレス: 0x{offset:X}")
                    found_img_addr = offset
                    decoded_pixel_data = decoded

            # パレットの特定 (解凍後32バイト以上)
            if not found_pal_addr and len(decoded) >= 32:
                if pal_match_part in decoded:
                    print(f"  >> 【パレット発見！】アドレス: 0x{offset:X}")
                    found_pal_addr = offset
                    decoded_pal_data_full = decoded

            # 両方見つかったらスキャン終了
            if found_img_addr and found_pal_addr:
                break

    # 3. 最終出力
    print("\n[3/3] 解析結果を出力中...")
    if not found_img_addr or not found_pal_addr:
        print("エラー: 画像またはパレットをROM内から特定できませんでした。")
        print("理由: パレットが非圧縮であるか、画像がLZ77以外の方式で圧縮されている可能性があります。")
        return

    # 通常色パレット (最初の32バイト)
    normal_pal = decoded_pal_data_full[0:32]
    save_indexed_png(decoded_pixel_data, normal_pal, f"{OUTPUT_PREFIX}_normal.png")
    
    # 色違いパレット (次の32バイト)
    if len(decoded_pal_data_full) >= 64:
        shiny_pal = decoded_pal_data_full[32:64]
        save_indexed_png(decoded_pixel_data, shiny_pal, f"{OUTPUT_PREFIX}_shiny.png")
    else:
        print("  -> 色違いパレットはこのブロックに含まれていません。")

    print(f"\nすべての処理が完了しました。")
    print(f"画像アドレス: 0x{found_img_addr:X}")
    print(f"パレットアドレス: 0x{found_pal_addr:X}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n実行中にエラーが発生しました: {e}")