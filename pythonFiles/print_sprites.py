import os
from PIL import Image

# ------------------ 設定 ------------------
ROM_PATH = '/Users/yu/Downloads/Redux v2.65 Beta 2 Debug.gba'
OUTPUT_DIR = '/Users/yu/Desktop/pokemon_custom_extract'

# --- 基準 A (ID 1 ～ 1103) ---
START_ID_A = 1
ADDR_IMG_FRONT_A = 0x592DA0
ADDR_IMG_BACK_A  = 0x7DB04C
ADDR_PAL_NORM_A  = 0x55F14C
ADDR_PAL_SHINY_A = 0x570644

# --- 基準 B (ID 1104 ～ 1260) ---
START_ID_B = 1104
ADDR_IMG_FRONT_B = 0x6FFE4C
ADDR_IMG_BACK_B  = 0x8B4B24
ADDR_PAL_NORM_B  = 0x569AFC
ADDR_PAL_SHINY_B = 0x57AFD0

# --- 基準 C (ID 1261 ～ ) ---
START_ID_C = 1261
ADDR_IMG_FRONT_C = 0x727B74
ADDR_IMG_BACK_C  = 0x8D3F34
ADDR_PAL_NORM_C  = 0x56AF18
ADDR_PAL_SHINY_C = 0x57C3EC

# --- モード設定 ---
MODE = "RANGE"
TARGET_RANGE = (1000, 1500)


# MODE = "SELECT"
# TARGET_LIST = [1, 4, 1884, 1885]  # SELECTモード用
# -----------------------------------------

def lz77_decompress_gba(data, offset):
    if offset >= len(data) or data[offset] != 0x10:
        return None, 4
    try:
        size = data[offset+1] | (data[offset+2] << 8) | (data[offset+3] << 16)
        if size == 0 or size > 0x10000: return None, 4
        ptr, out = offset + 4, bytearray()
        while len(out) < size:
            flags = data[ptr]; ptr += 1
            for i in range(8):
                if len(out) >= size: break
                if flags & (0x80 >> i):
                    info = (data[ptr] << 8) | data[ptr+1]; ptr += 2
                    length, disp = (info >> 12) + 3, (info & 0x0FFF) + 1
                    back = len(out) - disp
                    for _ in range(length): out.append(out[back]); back += 1
                else:
                    out.append(data[ptr]); ptr += 1
        return bytes(out), (ptr - offset + 3) & ~3
    except: return None, 4

def save_indexed_img(img_data, pal_data, path):
    if not img_data or not pal_data: return
    rgb = []
    for i in range(0, min(len(pal_data), 32), 2):
        v = pal_data[i] | (pal_data[i+1] << 8)
        rgb.extend([(v & 0x1F) << 3, ((v >> 5) & 0x1F) << 3, ((v >> 10) & 0x1F) << 3])
    rgb += [0] * (768 - len(rgb))
    img = Image.new('P', (64, 64))
    img.putpalette(rgb)
    ptr = 0
    for ty in range(0, 64, 8):
        for tx in range(0, 64, 8):
            for y in range(ty, ty+8):
                for x in range(tx, tx+8, 2):
                    if ptr < len(img_data):
                        b = img_data[ptr]; ptr += 1
                        img.putpixel((x, y), b & 0x0F); img.putpixel((x+1, y), (b >> 4) & 0x0F)
    img.save(path)

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(ROM_PATH, 'rb') as f: rom = f.read()

    if MODE == "RANGE":
        targets = list(range(TARGET_RANGE[0], TARGET_RANGE[1] + 1))
    else:
        targets = sorted(list(set(TARGET_LIST)))
    
    max_target = max(targets)

    # 初期ポインタ（基準Aから開始）
    pf, pb, pn, ps = ADDR_IMG_FRONT_A, ADDR_IMG_BACK_A, ADDR_PAL_NORM_A, ADDR_PAL_SHINY_A

    print(f"--- スキャン開始 (最大ID: {max_target}) ---")

    for tid in range(1, max_target + 1):
        # バンクリセット判定
        if tid == START_ID_B:
            print(f"🔄 ID {tid}: 基準Bへワープします")
            pf, pb, pn, ps = ADDR_IMG_FRONT_B, ADDR_IMG_BACK_B, ADDR_PAL_NORM_B, ADDR_PAL_SHINY_B
        
        elif tid == START_ID_C:
            print(f"🔄 ID {tid}: 基準Cへワープします")
            pf, pb, pn, ps = ADDR_IMG_FRONT_C, ADDR_IMG_BACK_C, ADDR_PAL_NORM_C, ADDR_PAL_SHINY_C

        # 1. 解凍とサイズ計測
        f_raw, f_c = lz77_decompress_gba(rom, pf)
        b_raw, b_c = lz77_decompress_gba(rom, pb)
        pn_raw, pn_c = lz77_decompress_gba(rom, pn)
        ps_raw, ps_c = lz77_decompress_gba(rom, ps)

        # 2. 対象ID保存
        if tid in targets:
            addr_info = f"{hex(pf)}_{hex(pn)}"
            # 正面通常
            if f_raw and pn_raw:
                save_indexed_img(f_raw[0:2048], pn_raw, os.path.join(OUTPUT_DIR, f"{tid}_1_{addr_info}.png"))
                f2 = f_raw[2048:4096] if len(f_raw) >= 4096 else f_raw[0:2048]
                save_indexed_img(f2, pn_raw, os.path.join(OUTPUT_DIR, f"{tid}_2_{addr_info}.png"))
            # 正面色違い
            if f_raw and ps_raw:
                save_indexed_img(f_raw[0:2048], ps_raw, os.path.join(OUTPUT_DIR, f"{tid}_3_{addr_info}.png"))
            # 背面通常/色違い
            if b_raw and pn_raw:
                save_indexed_img(b_raw[0:2048], pn_raw, os.path.join(OUTPUT_DIR, f"{tid}_4_{addr_info}.png"))
            if b_raw and ps_raw:
                save_indexed_img(b_raw[0:2048], ps_raw, os.path.join(OUTPUT_DIR, f"{tid}_5_{addr_info}.png"))
            print(f"✨ ID {tid}: 出力完了")

        # 3. ポインタ更新
        pf += f_c
        pb += b_c
        pn += pn_c
        ps += ps_c

    print(f"\n✅ 完了しました！")

if __name__ == "__main__":
    main()