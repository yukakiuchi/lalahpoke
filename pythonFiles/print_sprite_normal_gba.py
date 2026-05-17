import os
import sys
import struct
import subprocess
from PIL import Image

# ------------------ 📝 汎用設定エリア ------------------
ROM_PATH = '/Users/yu/Downloads/Super Mariomon (v1.5.1-Anniversary).gba'

# 1. 🔍 調べたい「最初の正面画像」のアドレス
TARGET_START_ADDR = 0x11E66E8  

# 2. 🎨【任意】精度を上げるためのパレット開始アドレス（分からなければ None でOK）
OPTIONAL_PAL_ADDR = 0x11E6AA0  

OUTPUT_BASE_DIR = '/Users/yu/Desktop/extracted_pokemon'
SCAN_COUNT = 350  # 🏎️ 抽出したいモンスターの数（20体分なら王道で計80枚出力）
# -----------------------------------------------------

def gba_pal_to_rgb888(pal_data):
    rgb = []
    for i in range(0, min(len(pal_data), 32), 2):
        if i+1 < len(pal_data):
            val = pal_data[i] | (pal_data[i+1] << 8)
            rgb.extend([(val & 0x1F) << 3, ((val >> 5) & 0x1F) << 3, ((val >> 10) & 0x1F) << 3])
    while len(rgb) < 768:
        rgb.extend([0, 0, 0])
    return rgb[:768]

def lz77_decompress_gba(data, offset):
    if offset >= len(data) or data[offset] != 0x10: return None, 0
    size = data[offset+1] | (data[offset+2] << 8) | (data[offset+3] << 16)
    if size < 20 or size > 0x10000: return None, 0
    ptr, out = offset + 4, bytearray()
    try:
        while len(out) < size and ptr < len(data):
            flags = data[ptr]; ptr += 1
            for i in range(8):
                if len(out) >= size: break
                if flags & (0x80 >> i):
                    if ptr + 1 >= len(data): break
                    info = (data[ptr] << 8) | data[ptr+1]; ptr += 2
                    length, disp = (info >> 12) + 3, (info & 0x0FFF) + 1
                    back = len(out) - disp
                    if back < 0: break
                    for _ in range(length): 
                        if len(out) >= size: break
                        out.append(out[back]); back += 1
                else: 
                    if ptr >= len(data): break
                    out.append(data[ptr]); ptr += 1
        return bytes(out), (ptr + 3) & ~3
    except: 
        return bytes(out) if len(out) >= 32 else None, 0

def save_sprite_64x64(img_data, pal_data, path):
    img = Image.new('P', (64, 64))
    img.putpalette(gba_pal_to_rgb888(pal_data))
    ptr = 0
    for ty in range(0, 64, 8):
        for tx in range(0, 64, 8):
            for y in range(ty, ty + 8):
                for x in range(tx, tx + 8, 2):
                    if ptr < len(img_data):
                        b = img_data[ptr]; ptr += 1
                        img.putpixel((x, y), b & 0x0F)
                        img.putpixel((x+1, y), (b >> 4) & 0x0F)
    img.save(path, transparency=0)

def get_unique_dir_name(base_dir):
    if not os.path.exists(base_dir): return base_dir
    counter = 1
    while True:
        new_dir = f"{base_dir}_{counter}"
        if not os.path.exists(new_dir): return new_dir
        counter += 1

def scan_area(rom_data, start_addr, max_elements=100):
    current_ptr = start_addr
    elements = []
    while current_ptr < len(rom_data) and len(elements) < max_elements:
        if rom_data[current_ptr] == 0x10:
            dec, next_ptr = lz77_decompress_gba(rom_data, current_ptr)
            if dec:
                size = len(dec)
                elem_type = "🖼️ IMG" if size == 2048 else ("🎨 PAL" if 32 <= size <= 64 else "📦 OTHER")
                elements.append({'addr': current_ptr, 'data': dec, 'type': elem_type, 'size': size})
                current_ptr = next_ptr
                continue
        current_ptr += 4
    return elements

def main():
    if not os.path.exists(ROM_PATH):
        print(f"❌ ROMファイルが見つかりませんッ！: {ROM_PATH}")
        return

    with open(ROM_PATH, 'rb') as f:
        rom_data = f.read()

    print("✨✨✨ 🔍 【1. 画像エリアの超加速スキャン】 ✨✨✨")
    print("=" * 75)
    img_elements = scan_area(rom_data, TARGET_START_ADDR, max_elements=SCAN_COUNT * 5)
    for e in img_elements[:8]:
        print(f" 🖼️  画像側ポインタ ➔ 0x{e['addr']:07X} | ✨ 解凍後: {e['size']:4d}B ➔ 予想: {e['type']}")
    print("...🚀 さらに奥深くへスキャン中...")

    rom_pattern = "UNKNOWN"
    pal_elements = []

    if OPTIONAL_PAL_ADDR is not None:
        print(f"\n🎨【2. パレット入力欄のディープ解析（位置: 0x{OPTIONAL_PAL_ADDR:X}）】 🎨")
        print("=" * 75)
        pal_elements = scan_area(rom_data, OPTIONAL_PAL_ADDR, max_elements=SCAN_COUNT * 5)
        for e in pal_elements[:8]:
            print(f" パレット側ポインタ ➔ 0x{e['addr']:07X} | 解凍後: {e['size']:4d}B ➔ 予想: {e['type']}")
        print("...🚀 パレットデータ並びを追跡中...")

        distance = abs(TARGET_START_ADDR - OPTIONAL_PAL_ADDR)
        print(f"\n📏 画像とパレットの物理的キョリ: {distance} バイト (0x{distance:X})")

        if distance < 0x2000:
            print("💖 【分析完了】画像とパレットが超ご近所さんです！「王道数珠つなぎパターン」と判定します！")
            rom_pattern = "STANDARD"
        else:
            # 遠距離かつ、第二アドレス側も「IMG, PAL」が混在している場合の高度な判定
            pal_types = [e['type'] for e in pal_elements[:4]]
            if '🖼️ IMG' in pal_types:
                print("⚡ 【分析完了】離れた位置に、もう一つの『画像＋パレットの塊』を発見しました！「前後エリア分離型構造」と判定します！")
                rom_pattern = "DOUBLE_CLUSTER"
            else:
                print("⚡ 【分析完了】画像とパレットが離れ離れです！「画像・パレット完全分離構造」と判定します！")
                rom_pattern = "SEPARATED"
    else:
        img_types = [e['type'] for e in img_elements[:6]]
        if len(img_types) >= 4 and img_types[0:4] == ['🖼️ IMG', '🎨 PAL', '🖼️ IMG', '🎨 PAL']:
            rom_pattern = "STANDARD"
        elif img_types.count("🖼️ IMG") == len(img_types):
            rom_pattern = "IMG_ONLY_CLUSTER"

    print("\n📊【3. ROM構造の最終ジャッジ＆シミュレーション】 📊")
    print("=" * 75)

    if rom_pattern == "STANDARD":
        print("👑 確定 ➔ 【パターン1：王道直列ループ構造】")
        print("   📂 [正面画像 ➔ 通常パ ➔ 背後画像 ➔ 色違パ] の神パック編成です。")
        print(f"   🎉 予定出荷枚数: {SCAN_COUNT}匹 × 4バリエーション ＝ 【計 {SCAN_COUNT * 4} 枚】")
    elif rom_pattern == "DOUBLE_CLUSTER":
        print("🏢 確定 ➔ 【パターン2変形：正面・背後エリア完全独立構造】")
        print("   📂 画像側アドレスに[正面データ群]、パレット側アドレスに[背後データ群]がそれぞれ王道配置されています。")
        print(f"   🎉 予定出荷枚数: {SCAN_COUNT}匹 × 4バリエーション ＝ 【計 {SCAN_COUNT * 4} 枚】")
    elif rom_pattern == "SEPARATED" or rom_pattern == "IMG_ONLY_CLUSTER":
        print("🏢 確定 ➔ 【パターン2：画像・パレット完全分離マンション構造】")
        print("   📂 グラフィックはグラフィック、色は色で別々のセクターに隔離されています。")
        if OPTIONAL_PAL_ADDR is None:
            print("\n🚨🚨🚨 【エラー：手がかりが足りません！】 🚨🚨🚨")
            print("画像だけの密集地帯を見つけましたが、対応するカラーパレットの迷宮の入り口がわかりません。")
            print("精度を100%にするため、上部の 'OPTIONAL_PAL_ADDR' にパレットアドレスを教えてください！")
            return
        print(f"   🎉 予定出荷枚数: {SCAN_COUNT}匹 × 2バリエーション ＝ 【計 {SCAN_COUNT * 2} 枚】")
    else:
        print("❓ 確定 ➔ 【パターン3：カオス型変則構造】")
        print("   📂 規則性が掴めないため、見つかったグラフィックをそのまま1枚ずつ引っこ抜きます。")
        print(f"   🎉 予定出荷枚数: 【最大 {SCAN_COUNT} 枚】")
    print("=" * 75)

    final_output_dir = get_unique_dir_name(OUTPUT_BASE_DIR)
    os.makedirs(final_output_dir)
    print(f"\n🖼️ 🛠️  【4. PNG画像ジェネレーター起動】 ➔ 出発地: {final_output_dir}")
    print("-" * 75)

    generated_files = []

    if rom_pattern == "STANDARD":
        pokemon_idx = 1
        i = 0
        while i < len(img_elements) - 3 and pokemon_idx <= SCAN_COUNT:
            e1, e2, e3, e4 = img_elements[i], img_elements[i+1], img_elements[i+2], img_elements[i+3]
            if e1['type'] == '🖼️ IMG' and e2['type'] == '🎨 PAL' and e3['type'] == '🖼️ IMG' and e4['type'] == '🎨 PAL':
                prefix = f"Poke_{pokemon_idx:03d}"
                save_sprite_64x64(e1['data'], e2['data'], os.path.join(final_output_dir, f"{prefix}_1_front_normal.png"))
                save_sprite_64x64(e1['data'], e4['data'], os.path.join(final_output_dir, f"{prefix}_2_front_shiny.png"))
                save_sprite_64x64(e3['data'], e2['data'], os.path.join(final_output_dir, f"{prefix}_3_back_normal.png"))
                save_sprite_64x64(e3['data'], e4['data'], os.path.join(final_output_dir, f"{prefix}_4_back_shiny.png"))
                generated_files.extend([f"{prefix}_1_front_normal.png", f"{prefix}_2_front_shiny.png", f"{prefix}_3_back_normal.png", f"{prefix}_4_back_shiny.png"])
                
                print(f"🌈 [No.{pokemon_idx:03d}] 4枚セット錬成完了！ (正面:0x{e1['addr']:X})")
                pokemon_idx += 1
                i += 4
            else:
                i += 1

    elif rom_pattern == "DOUBLE_CLUSTER":
        # 正面エリアと背後エリアがそれぞれ [IMG, PAL, IMG, PAL] で同期している場合の特別結合処理
        pokemon_idx = 1
        f_idx = 0  # 正面側(img_elements)のポインタ
        b_idx = 0  # 背後側(pal_elements)のポインタ

        while f_idx < len(img_elements) - 3 and b_idx < len(pal_elements) - 3 and pokemon_idx <= SCAN_COUNT:
            f1, f2, f3, f4 = img_elements[f_idx], img_elements[f_idx+1], img_elements[f_idx+2], img_elements[f_idx+3]
            b1, b2, b3, b4 = pal_elements[b_idx], pal_elements[b_idx+1], pal_elements[b_idx+2], pal_elements[b_idx+3]

            # 両方のエリアが想定通りの構造かチェック
            f_ok = (f1['type'] == '🖼️ IMG' and f2['type'] == '🎨 PAL' and f3['type'] == '🖼️ IMG' and f4['type'] == '🎨 PAL')
            b_ok = (b1['type'] == '🖼️ IMG' and b2['type'] == '🎨 PAL' and b3['type'] == '🖼️ IMG' and b4['type'] == '🎨 PAL')

            if f_ok and b_ok:
                prefix = f"Poke_{pokemon_idx:03d}"
                # 正面側から正面グラフィック(f1, f3)とパレット(f2, f4)を使って生成
                save_sprite_64x64(f1['data'], f2['data'], os.path.join(final_output_dir, f"{prefix}_1_front_normal.png"))
                save_sprite_64x64(f1['data'], f4['data'], os.path.join(final_output_dir, f"{prefix}_2_front_shiny.png"))
                # 背後側から背後グラフィック(b1, b3)とパレット(b2, b4)を使って生成
                save_sprite_64x64(b1['data'], b2['data'], os.path.join(final_output_dir, f"{prefix}_3_back_normal.png"))
                save_sprite_64x64(b1['data'], b4['data'], os.path.join(final_output_dir, f"{prefix}_4_back_shiny.png"))
                
                generated_files.extend([f"{prefix}_1_front_normal.png", f"{prefix}_2_front_shiny.png", f"{prefix}_3_back_normal.png", f"{prefix}_4_back_shiny.png"])
                print(f"🌈 [No.{pokemon_idx:03d}] 前後独立エリアから4枚セット完全錬成！ (正面:0x{f1['addr']:X} / 背後:0x{b1['addr']:X})")
                
                pokemon_idx += 1
                f_idx += 4
                b_idx += 4
            else:
                if not f_ok: f_idx += 1
                if not b_ok: b_idx += 1

    elif rom_pattern == "SEPARATED":
        pokemon_idx = 1
        img_idx = 0
        pal_idx = 0
        
        while img_idx < len(img_elements) and pal_idx < len(pal_elements) - 1 and pokemon_idx <= SCAN_COUNT:
            e_img = img_elements[img_idx]
            e_npal = pal_elements[pal_idx]
            e_spal = pal_elements[pal_idx+1]
            
            if e_img['type'] == '🖼️ IMG' and e_npal['type'] == '🎨 PAL' and e_spal['type'] == '🎨 PAL':
                prefix = f"SepPoke_{pokemon_idx:03d}"
                
                save_sprite_64x64(e_img['data'], e_npal['data'], os.path.join(final_output_dir, f"{prefix}_1_front_normal.png"))
                save_sprite_64x64(e_img['data'], e_spal['data'], os.path.join(final_output_dir, f"{prefix}_2_front_shiny.png"))
                generated_files.extend([f"{prefix}_1_front_normal.png", f"{prefix}_2_front_shiny.png"])
                
                print(f"🔗 [分離型 No.{pokemon_idx:03d}] 遠隔結合に成功！ (画像:0x{e_img['addr']:X} ➔ パレット:0x{e_npal['addr']:X})")
                pokemon_idx += 1
                img_idx += 1
                pal_idx += 2
            else:
                if e_img['type'] != '🖼️ IMG': img_idx += 1
                if e_npal['type'] != '🎨 PAL': pal_idx += 1

    else:
        for idx, e in enumerate(img_elements[:SCAN_COUNT]):
            if e['type'] == '🖼️ IMG':
                fname = f"Unknown_Img_{idx+1:03d}_0x{e['addr']:X}.png"
                dummy_pal = pal_elements[0]['data'] if pal_elements else bytes([0]*64)
                save_sprite_64x64(e['data'], dummy_pal, os.path.join(final_output_dir, fname))
                generated_files.append(fname)

    print("-" * 75)
    print("📋 【📄 生成されたファイル（一部抜粋）】")
    for name in generated_files[:8]:
        print(f"  🎁 {name}")
    if len(generated_files) > 8:
        print(f"  ...他 {len(generated_files) - 8} 個のファイルを爆誕させました。")
        
    print(f"\n✨✨ 完 全 終 了 ッッ！！ ✨✨")
    print(f"📂 格納場所はこちら ➔ {final_output_dir}")
    print("🚀 フォルダを自動でシュパッと開きます！")

    try:
        if sys.platform == 'darwin': 
            subprocess.Popen(['open', final_output_dir])
        elif sys.platform == 'win32': 
            subprocess.Popen(['explorer', os.path.normpath(final_output_dir)])
    except Exception as e:
        pass

if __name__ == "__main__":
    main()