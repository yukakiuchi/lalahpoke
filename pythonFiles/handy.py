import os
from PIL import Image

# ==========================================
# 設定エリア
# ==========================================
ROM_PATH = '/Users/yu/Downloads/Z (v1.2.0).gba'
FIXED_IMG_OFFSET = 0x4BFA88  # ここが 0x10 で始まっていない可能性を考慮
OUTPUT_DIR = 'palette_search_results'
SCAN_START_OFFSET = 0x600000 
MAX_RESULTS = 1000
# ==========================================

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def lz77_decompress_gba(data, offset):
    try:
        if offset >= len(data) or data[offset] != 0x10: 
            return None, None
        
        decomp_size = data[offset+1] | (data[offset+2] << 8) | (data[offset+3] << 16)
        if decomp_size == 0 or decomp_size > 0x10000: return None, None
        
        ptr = offset + 4
        out = bytearray()
        while len(out) < decomp_size:
            if ptr >= len(data): break
            flags = data[ptr]; ptr += 1
            for i in range(8):
                if len(out) >= decomp_size: break
                if flags & (0x80 >> i):
                    if ptr + 1 >= len(data): break
                    info = (data[ptr] << 8) | data[ptr+1]; ptr += 2
                    length, disp = (info >> 12) + 3, (info & 0x0FFF) + 1
                    back = len(out) - disp
                    if back < 0: return None, None
                    for _ in range(length):
                        out.append(out[back]); back += 1
                else:
                    if ptr >= len(data): break
                    out.append(data[ptr]); ptr += 1
        return out, ptr
    except:
        return None, None

def gba_pal_to_rgb(pal_bytes):
    colors = []
    for i in range(0, 32, 2):
        if i + 1 >= len(pal_bytes): break
        val = pal_bytes[i] | (pal_bytes[i+1] << 8)
        r, g, b = (val & 0x1F) << 3, ((val >> 5) & 0x1F) << 3, ((val >> 10) & 0x1F) << 3
        colors.extend([r, g, b])
    return colors

def create_sprite_image(pixel_data, pal_bytes):
    # ポケモンのグラフィックは通常 64x64
    img = Image.new('P', (64, 64))
    rgb_pal = gba_pal_to_rgb(pal_bytes)
    img.putpalette(rgb_pal + [0] * (768 - len(rgb_pal)))
    
    ptr = 0
    for tile_y in range(0, 64, 8):
        for tile_x in range(0, 64, 8):
            for y in range(tile_y, tile_y + 8):
                for x in range(tile_x, tile_x + 8, 2):
                    if ptr >= len(pixel_data): break
                    byte = pixel_data[ptr]; ptr += 1
                    img.putpixel((tile_x + (x % 8), tile_y + (y % 8)), byte & 0x0F)
                    img.putpixel((tile_x + (x % 8) + 1, tile_y + (y % 8)), (byte >> 4) & 0x0F)
    return img

def main():
    if not os.path.exists(ROM_PATH):
        print(f"Error: ROMが見つかりません {ROM_PATH}")
        return

    with open(ROM_PATH, 'rb') as f:
        rom_data = f.read()

    # 画像の検出 (指定アドレスの前後32バイトをスキャン)
    pixel_data = None
    actual_img_addr = 0
    print(f"画像検索中 (Target: 0x{FIXED_IMG_OFFSET:X})...")
    
    for search_off in range(max(0, FIXED_IMG_OFFSET - 32), FIXED_IMG_OFFSET + 32):
        if rom_data[search_off] == 0x10:
            dec, _ = lz77_decompress_gba(rom_data, search_off)
            if dec and len(dec) == 2048:
                pixel_data = dec
                actual_img_addr = search_off
                print(f"[*] 画像を 0x{actual_img_addr:X} で発見しました。")
                break

    if not pixel_data:
        print("!! エラー: 指定アドレス付近に有効なLZ77画像(2048bytes)が見つかりません。")
        print(f"0x{FIXED_IMG_OFFSET:X} のバイト値: {rom_data[FIXED_IMG_OFFSET:FIXED_IMG_OFFSET+4].hex()}")
        return

    # パレットスキャン
    found_count = 0
    offset = SCAN_START_OFFSET
    print(f"パレットスキャン開始 (0x{offset:X}〜)...")

    while offset < len(rom_data) - 4 and found_count < MAX_RESULTS:
        if rom_data[offset] == 0x10:
            pal_dec, next_ptr = lz77_decompress_gba(rom_data, offset)
            if pal_dec and len(pal_dec) == 32:
                found_count += 1
                filename = f"pal_0x{offset:X}.png"
                img = create_sprite_image(pixel_data, pal_dec)
                img.save(os.path.join(OUTPUT_DIR, filename))
                print(f"[{found_count}] Found: 0x{offset:X}")
                offset = next_ptr if next_ptr else offset + 1
                continue
        offset += 1

    print("\n完了しました。")

if __name__ == "__main__":
    main()