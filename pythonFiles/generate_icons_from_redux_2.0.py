import os
import subprocess
from PIL import Image

# ==========================================
# ★ 設定エリア ★
# ==========================================
ROM_PATH = "/Users/yu/Downloads/redux2.0.gba"
OUTPUT_DIR = "/Users/yu/Downloads/pokemon_icon_extraction"

BASE_REF_ID   = 1648
BASE_REF_ADDR = 0x1CA912C
BYTE_PER_POKE = 1024

MODE = "RANGE"
TARGET_PALETTES = [3]
START_ID = 1648
END_ID   = 1700

# パレットをグローバルスコープで定義
PALETTES = {
    0: [(98, 156, 131), (131, 131, 115), (189, 189, 189), (255, 255, 255), (189, 164, 65), (246, 246, 41), (213, 98, 65), (246, 148, 41), (139, 123, 255), (98, 74, 205), (238, 115, 156), (255, 180, 164), (164, 197, 255), (106, 172, 156), (98, 98, 90), (65, 65, 65)],
    1: [(98, 156, 131), (115, 115, 115), (189, 189, 189), (255, 255, 255), (123, 156, 74), (156, 205, 74), (148, 246, 74), (238, 115, 156), (246, 148, 246), (189, 164, 90), (246, 230, 41), (246, 246, 172), (213, 213, 106), (230, 74, 41), (98, 98, 90), (65, 65, 65)],
    2: [(98, 156, 131), (123, 123, 123), (189, 189, 180), (255, 255, 255), (115, 115, 205), (164, 172, 246), (180, 131, 90), (238, 197, 139), (197, 172, 41), (246, 246, 41), (246, 98, 82), (148, 123, 205), (197, 164, 205), (189, 41, 156), (98, 98, 90), (65, 65, 65)],
    3: [(98, 156, 131), (115, 115, 115), (189, 189, 189), (255, 255, 255), (65, 106, 148), (98, 148, 164), (164, 197, 255), (238, 115, 156), (213, 98, 65), (189, 164, 90), (246, 230, 41), (246, 246, 172), (213, 213, 106), (246, 148, 41), (98, 98, 90), (65, 65, 65)],
    4: [(98, 156, 131), (115, 115, 115), (189, 189, 189), (255, 255, 255), (123, 156, 74), (156, 205, 74), (65, 106, 148), (238, 115, 156), (246, 148, 246), (189, 164, 90), (246, 246, 139), (164, 197, 255), (98, 148, 164), (213, 98, 65), (98, 98, 90), (65, 65, 65)],
    5: [(98, 156, 131), (123, 123, 123), (189, 189, 180), (255, 255, 255), (123, 156, 74), (156, 205, 74), (180, 131, 90), (238, 197, 139), (197, 172, 41), (246, 246, 41), (213, 98, 65), (148, 123, 205), (197, 164, 205), (246, 148, 41), (98, 98, 90), (65, 65, 65)]
}

def get_indexed_pixels(data):
    raw_indices = []
    for tile_idx in range(16):
        for i in range(32):
            b = data[tile_idx * 32 + i]
            raw_indices.append(b & 0x0F)
            raw_indices.append(b >> 4)
    final_indices = [0] * (32 * 32)
    for t in range(16):
        tx, ty = (t % 4) * 8, (t // 4) * 8
        for ly in range(8):
            for lx in range(8):
                src = (t * 64) + (ly * 8) + lx
                if src < len(raw_indices):
                    final_indices[(ty + ly) * 32 + (tx + lx)] = raw_indices[src]
    return final_indices

def create_indexed_image(rom_data, target_addr, palette_rgb):
    f1_idx = get_indexed_pixels(rom_data[target_addr : target_addr + 512])
    f2_idx = get_indexed_pixels(rom_data[target_addr + 512 : target_addr + 1024])
    img = Image.new('P', (32, 64))
    palette_16 = [val for rgb in palette_rgb for val in rgb]
    img.putpalette(palette_16 + [0]*(768-len(palette_16)))
    img.putdata(f1_idx + f2_idx)
    return img

def main():
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    with open(ROM_PATH, "rb") as f: rom_data = f.read()
    
    target_ids = list(range(START_ID, END_ID + 1)) if MODE == "RANGE" else EACH_IDS
    
    for current_id in target_ids:
        offset_diff = (current_id - BASE_REF_ID) * BYTE_PER_POKE
        target_addr = BASE_REF_ADDR + offset_diff
        
        if target_addr < 0 or target_addr + 1024 > len(rom_data): continue
        
        for p_num in TARGET_PALETTES:
            active_pal = PALETTES.get(p_num, PALETTES[0])
            img = create_indexed_image(rom_data, target_addr, active_pal)
            img.save(f"{OUTPUT_DIR}/id_{current_id:04d}_pal{p_num}.png", "PNG")
    
    print(f"✅ 生成完了: {OUTPUT_DIR}")
    subprocess.run(["open", OUTPUT_DIR])

if __name__ == "__main__":
    main()