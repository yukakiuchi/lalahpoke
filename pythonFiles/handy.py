import os
import subprocess
from PIL import Image

# ==========================================
# ★ USER SETTINGS ★
# ==========================================
# アイコンデータの開始地点 (見つかったアドレス)
REF_ADDR = 0xD5910C 
# 基準となるID (0xD5910C が No.1 のデータなら 1)
REF_ID = 1 
ROM_PATH = "/Users/yu/Desktop/sprites_roms/adventure_red/U_FR_Adventure_Red_Beta_15_Expansion_Fix_Patch_C.gba"
OUTPUT_DIR = "/Users/yu/Desktop/pokemon_icons_final"

# --- モード設定 ---
# "RANGE" なら START_ID から END_ID まで
# "EACH" なら EACH_IDS に書いたIDのみ
MODE = "RANGE" 
START_ID = 1
END_ID   = 1000
# EACH_IDS = [493]

# 生成したいパレット番号のリスト
TARGET_PALETTES = [0]

# アイコン1つあたりのデータサイズ (32x64 4bpp = 1024 bytes)
BYTE_PER_POKE = 1024

# --- パレット定義 ---
PALETTES = {
    0: [(98, 156, 131), (131, 131, 115), (189, 189, 189), (255, 255, 255), (189, 164, 65), (246, 246, 41), (213, 98, 65), (246, 148, 41), (139, 123, 255), (98, 74, 205), (238, 115, 156), (255, 180, 164), (164, 197, 255), (106, 172, 156), (98, 98, 90), (65, 65, 65)],
    1: [(98, 156, 131), (115, 115, 115), (189, 189, 189), (255, 255, 255), (123, 156, 74), (156, 205, 74), (148, 246, 74), (238, 115, 156), (246, 148, 246), (189, 164, 90), (246, 230, 41), (246, 246, 172), (213, 213, 106), (230, 74, 41), (98, 98, 90), (65, 65, 65)],
    2: [(98, 156, 131), (123, 123, 123), (189, 189, 180), (255, 255, 255), (115, 115, 205), (164, 172, 246), (180, 131, 90), (238, 197, 139), (197, 172, 41), (246, 246, 41), (246, 98, 82), (148, 123, 205), (197, 164, 205), (189, 41, 156), (98, 98, 90), (65, 65, 65)],
    3: [(98, 156, 131), (115, 115, 115), (189, 189, 189), (255, 255, 255), (65, 106, 148), (98, 148, 164), (164, 197, 255), (238, 115, 156), (213, 98, 65), (189, 164, 90), (246, 230, 41), (246, 246, 172), (213, 213, 106), (246, 148, 41), (98, 98, 90), (65, 65, 65)],
    4: [(98, 156, 131), (115, 115, 115), (189, 189, 189), (255, 255, 255), (123, 156, 74), (156, 205, 74), (65, 106, 148), (238, 115, 156), (246, 148, 246), (189, 164, 90), (246, 246, 139), (164, 197, 255), (98, 148, 164), (213, 98, 65), (98, 98, 90), (65, 65, 65)],
    5: [(98, 156, 131), (123, 123, 123), (189, 189, 180), (255, 255, 255), (123, 156, 74), (156, 205, 74), (180, 131, 90), (238, 197, 139), (197, 172, 41), (246, 246, 41), (213, 98, 65), (148, 123, 205), (197, 164, 205), (246, 148, 41), (98, 98, 90), (65, 65, 65)]
}

def get_indexed_pixels(data):
    """GBAのタイル形式(4bpp)をピクセルインデックスに変換"""
    raw_indices = []
    for tile_idx in range(len(data) // 32):
        for i in range(32):
            b = data[tile_idx * 32 + i]
            raw_indices.append(b & 0x0F)
            raw_indices.append(b >> 4)
    
    # 32x32ピクセルに並べ替え
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
    """RAWデータから32x64の画像を作成"""
    # 上半分と下半分をそれぞれタイル変換
    f1_idx = get_indexed_pixels(rom_data[target_addr : target_addr + 512])
    f2_idx = get_indexed_pixels(rom_data[target_addr + 512 : target_addr + 1024])
    
    img = Image.new('P', (32, 64))
    
    # パレットをフラット化(RGBタプル -> リスト)
    flat_palette = [val for rgb in palette_rgb for val in rgb]
    # Pillow用に768バイト(256色分)に拡張
    img.putpalette(flat_palette + [0] * (768 - len(flat_palette)))
    
    # ピクセルデータを流し込む
    img.putdata(f1_idx + f2_idx)
    return img

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    else:
        # 既存ファイルをクリア（必要なら）
        for f in os.listdir(OUTPUT_DIR):
            if f.endswith(".png"): os.unlink(os.path.join(OUTPUT_DIR, f))

    target_ids = list(range(START_ID, END_ID + 1)) if MODE == "RANGE" else EACH_IDS
    count = 0

    try:
        with open(ROM_PATH, "rb") as f:
            rom_data = f.read()

        print(f"🚀 アイコン抽出開始 (モード: {MODE})")

        for current_id in target_ids:
            # 基準アドレスからの位置を計算
            target_addr = REF_ADDR + ((current_id - REF_ID) * BYTE_PER_POKE)
            
            if target_addr < 0 or target_addr + BYTE_PER_POKE > len(rom_data):
                continue

            for p_num in TARGET_PALETTES:
                active_pal = PALETTES.get(p_num, PALETTES[0])
                img = create_indexed_image(rom_data, target_addr, active_pal)
                
                save_path = os.path.join(OUTPUT_DIR, f"icon_{current_id:04d}_pal{p_num}.png")
                
                # インデックス0を透明に設定して保存
                img.save(save_path, "PNG", transparency=0)
                count += 1

        print("-" * 40)
        print(f"✅ 生成完了: {count} 個のアイコンを保存しました")
        print(f"出力先: {OUTPUT_DIR}")
        print("-" * 40)
        subprocess.run(["open", OUTPUT_DIR])

    except Exception as e:
        print(f"⚠️ エラーが発生しました: {e}")

if __name__ == "__main__":
    main()