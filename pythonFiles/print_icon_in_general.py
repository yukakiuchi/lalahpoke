import os
import struct
from PIL import Image

# ==========================================
# ★ SETTINGS ★
# ==========================================
# まずはアイコンを呼び出してるポインターアドレスを見つける
# そこからそのポインターを元にアイコンを出力していくスタイル
ROM_PATH = "/Users/yu/Desktop/sprites_roms/adventure_red/U_FR_Adventure_Red_Beta_15_Expansion_Fix_Patch_C.gba"
OUTPUT_DIR = "/Users/yu/Desktop/pokemon_icons_top_only"

# 開始ポインタテーブルのアドレス
TABLE_START = 0x161E5C4 

# 出力枚数
NUM_POKEMON = 5000

PALETTES = {
    0: [(98, 156, 131), (131, 131, 115), (189, 189, 189), (255, 255, 255), (189, 164, 65), (246, 246, 41), (213, 98, 65), (246, 148, 41), (139, 123, 255), (98, 74, 205), (238, 115, 156), (255, 180, 164), (164, 197, 255), (106, 172, 156), (98, 98, 90), (65, 65, 65)],
    1: [(98, 156, 131), (115, 115, 115), (189, 189, 189), (255, 255, 255), (123, 156, 74), (156, 205, 74), (148, 246, 74), (238, 115, 156), (246, 148, 246), (189, 164, 90), (246, 230, 41), (246, 246, 172), (213, 213, 106), (230, 74, 41), (98, 98, 90), (65, 65, 65)],
    2: [(98, 156, 131), (123, 123, 123), (189, 189, 180), (255, 255, 255), (115, 115, 205), (164, 172, 246), (180, 131, 90), (238, 197, 139), (197, 172, 41), (246, 246, 41), (246, 98, 82), (148, 123, 205), (197, 164, 205), (189, 41, 156), (98, 98, 90), (65, 65, 65)],
    3: [(98, 156, 131), (115, 115, 115), (189, 189, 189), (255, 255, 255), (65, 106, 148), (98, 148, 164), (164, 197, 255), (238, 115, 156), (213, 98, 65), (189, 164, 90), (246, 230, 41), (246, 246, 172), (213, 213, 106), (246, 148, 41), (98, 98, 90), (65, 65, 65)],
    4: [(98, 156, 131), (115, 115, 115), (189, 189, 189), (255, 255, 255), (123, 156, 74), (156, 205, 74), (65, 106, 148), (238, 115, 156), (246, 148, 246), (189, 164, 90), (246, 246, 139), (164, 197, 255), (98, 148, 164), (213, 98, 65), (98, 98, 90), (65, 65, 65)],
    5: [(98, 156, 131), (123, 123, 123), (189, 189, 180), (255, 255, 255), (123, 156, 74), (156, 205, 74), (180, 131, 90), (238, 197, 139), (197, 172, 41), (246, 246, 41), (213, 98, 65), (148, 123, 205), (197, 164, 205), (246, 148, 41), (98, 98, 90), (65, 65, 65)]
}

def get_pil_palette(rgb_list):
    p = []
    for r, g, b in rgb_list: p.extend([r, g, b])
    p += [0] * (768 - len(p))
    return p

def get_tiles_32x32(data):
    """512バイトのデータから32x32ピクセルを生成"""
    width, height = 32, 32
    pixels = [0] * (width * height)
    ptr = 0
    for ty in range(0, height, 8):
        for tx in range(0, width, 8):
            for y in range(ty, ty + 8):
                for x in range(tx, tx + 8, 2):
                    if ptr < len(data):
                        b = data[ptr]; ptr += 1
                        pixels[y * width + x] = b & 0x0F
                        pixels[y * width + x + 1] = b >> 4
    return pixels

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    with open(ROM_PATH, "rb") as f:
        rom_data = f.read()

        for i in range(NUM_POKEMON):
            ptr_pos = TABLE_START + (i * 4)
            # ポインタがROMの末尾を超えないかチェック
            if ptr_pos + 4 > len(rom_data): break
            
            ptr_val = struct.unpack('<I', rom_data[ptr_pos : ptr_pos + 4])[0]
            
            # GBAポインタ（0x08XXXXXX）の妥当性チェック
            if not (0x08000000 <= ptr_val <= 0x09FFFFFF): continue
            
            addr = ptr_val - 0x08000000

            # 32x32に必要なのは512バイト
            if addr < 0 or addr > len(rom_data) - 512:
                continue

            # 512バイト分だけ取得
            raw_data = rom_data[addr : addr + 512]
            pixels = get_tiles_32x32(raw_data)

            # 横長のキャンバス (32px * 6枚 = 192px幅, 32px高)
            combined_img = Image.new('RGBA', (192, 32))

            for p_id in range(6):
                temp_img = Image.new('P', (32, 32))
                temp_img.putpalette(get_pil_palette(PALETTES[p_id]))
                temp_img.putdata(pixels)
                
                temp_rgba = temp_img.convert('RGBA')
                datas = temp_rgba.getdata()
                new_data = []
                for item in datas:
                    # 背景色(98, 156, 131)を透明に
                    if item[0] == 98 and item[1] == 156 and item[2] == 131:
                        new_data.append((0, 0, 0, 0))
                    else:
                        new_data.append(item)
                temp_rgba.putdata(new_data)
                
                combined_img.paste(temp_rgba, (p_id * 32, 0))

            save_path = os.path.join(OUTPUT_DIR, f"{hex(addr)}.png")
            combined_img.save(save_path)

            if i % 100 == 0:
                print(f"進捗: {i} 体完了...")

    print(f"✨ 完了！ {OUTPUT_DIR} を確認してください。")

if __name__ == "__main__":
    main()