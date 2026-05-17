import os
import sys
import struct
import subprocess
from PIL import Image

# ==========================================
# ★ 設定エリア ★
# ==========================================
ROM_PATH = '/Users/yu/Desktop/sprites_roms/pisces/pisces v1.5.4.gba'
SAMPLE_IMAGE_PATH = '/Users/yu/Desktop/iconss/starter.png'
BASE_OUTPUT_DIR = '/Users/yu/Desktop/search_icon_result'

ID_RANGE = (1350, 1550)
SPECIFIC_IDS = []


# 6つのパレット定義
PALETTES = {
    0: [(98, 156, 131), (131, 131, 115), (189, 189, 189), (255, 255, 255), (189, 164, 65), (246, 246, 41), (213, 98, 65), (246, 148, 41), (139, 123, 255), (98, 74, 205), (238, 115, 156), (255, 180, 164), (164, 197, 255), (106, 172, 156), (98, 98, 90), (65, 65, 65)],
    1: [(98, 156, 131), (115, 115, 115), (189, 189, 189), (255, 255, 255), (123, 156, 74), (156, 205, 74), (148, 246, 74), (238, 115, 156), (246, 148, 246), (189, 164, 90), (246, 230, 41), (246, 246, 172), (213, 213, 106), (230, 74, 41), (98, 98, 90), (65, 65, 65)],
    2: [(98, 156, 131), (123, 123, 123), (189, 189, 180), (255, 255, 255), (115, 115, 205), (164, 172, 246), (180, 131, 90), (238, 197, 139), (197, 172, 41), (246, 246, 41), (246, 98, 82), (148, 123, 205), (197, 164, 205), (189, 41, 156), (98, 98, 90), (65, 65, 65)],
    3: [(98, 156, 131), (115, 115, 115), (189, 189, 189), (255, 255, 255), (65, 106, 148), (98, 148, 164), (164, 197, 255), (238, 115, 156), (213, 98, 65), (189, 164, 90), (246, 230, 41), (246, 246, 172), (213, 213, 106), (246, 148, 41), (98, 98, 90), (65, 65, 65)],
    4: [(98, 156, 131), (115, 115, 115), (189, 189, 189), (255, 255, 255), (123, 156, 74), (156, 205, 74), (65, 106, 148), (238, 115, 156), (246, 148, 246), (189, 164, 90), (246, 246, 139), (164, 197, 255), (98, 148, 164), (213, 98, 65), (98, 98, 90), (65, 65, 65)],
    5: [(98, 156, 131), (123, 123, 123), (189, 189, 180), (255, 255, 255), (123, 156, 74), (156, 205, 74), (180, 131, 90), (238, 197, 139), (197, 172, 41), (246, 246, 41), (213, 98, 65), (148, 123, 205), (197, 164, 205), (246, 148, 41), (98, 98, 90), (65, 65, 65)]
}
# ==========================================

def get_unique_dir(base_dir):
    if not os.path.exists(base_dir):
        return base_dir
    counter = 1
    while True:
        new_dir = f"{base_dir}_{counter}"
        if not os.path.exists(new_dir):
            return new_dir
        counter += 1

def open_folder_and_exit(target_dir):
    print(f"\n📂 出力フォルダを自動で開きます: {target_dir}")
    if sys.platform == "darwin":
        subprocess.run(["open", target_dir])
    elif sys.platform == "win32":
        os.startfile(target_dir)
    else:
        subprocess.run(["xdg-open", target_dir])
    sys.exit(0)

def convert_png_chunk_to_gba_4bpp(img, start_y):
    pixels = list(img.getdata())
    img_w, _ = img.size
    gba_data = bytearray(512)
    byte_ptr = 0

    for tile_y in range(4):
        for tile_x in range(4):
            for y in range(8):
                pixel_y = (start_y + tile_y * 8) + y
                for x in range(0, 8, 2):
                    pixel_x = tile_x * 8 + x
                    p1 = pixels[pixel_y * img_w + pixel_x] & 0x0F
                    p2 = pixels[pixel_y * img_w + (pixel_x + 1)] & 0x0F
                    gba_data[byte_ptr] = p1 | (p2 << 4)
                    byte_ptr += 1
    return bytes(gba_data)

def extract_search_bytes(img_path):
    try:
        img = Image.open(img_path).convert('P')
    except Exception as e:
        print(f"❌ 画像ファイルの読み込みに失敗しました: {e}")
        return None
    w, h = img.size
    if w != 32 or (h != 32 and h != 64):
        print(f"❌ 警告: 画像サイズが {w}x{h} です。32x32 または 32x64 である必要があります。")
        return None
    return convert_png_chunk_to_gba_4bpp(img, start_y=0)

def get_indexed_pixels(data):
    if len(data) < 512: return [0] * (32 * 32)
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

def make_palette_list(rgb_list):
    flat = []
    for r, g, b in rgb_list: flat.extend([r, g, b])
    return flat + [0] * (768 - len(flat))

def main():
    if not os.path.exists(ROM_PATH):
        print("❌ ROMファイルが見つかりません。パスを確認してください。")
        return
        
    output_dir = get_unique_dir(BASE_OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)
    
    with open(ROM_PATH, "rb") as f: 
        rom_data = f.read()

    print("🖼️  【1】手がかり画像のバイナリ変換中...")
    target_bytes = extract_search_bytes(SAMPLE_IMAGE_PATH)
    if not target_bytes: return

    print("🔍 【2】ROM内から該当アイコンの位置をスキャンしています...")
    found_addr = -1
    
    idx = rom_data.find(target_bytes)
    if idx != -1:
        print(f"🎯 完璧に一致するデータを発見しました！ ➔ アドレス: 0x{idx:X}")
        found_addr = idx
    else:
        print("⚠️ 完全一致が見つかりませんでした。下半分での部分一致に切り替えます。")
        half_bytes = target_bytes[256:]
        idx = rom_data.find(half_bytes)
        if idx != -1:
            found_addr = idx - 256
            print(f"🎯 部分一致から先頭を逆算特定しました！ ➔ 予測アドレス: 0x{found_addr:X}")
        else:
            print("❌ 画像バイナリがROM内に見つかりませんでした。解析を終了します。")
            return

    print("\n🛰️  【3】特定したアドレスを読み込んでいる「ポインタ目次」を捜索中...")
    ptr_08 = struct.pack("<I", (found_addr & 0x00FFFFFF) | 0x08000000)
    ptr_09 = struct.pack("<I", found_addr + 0x08000000)
    
    table_entry_addr = -1
    for gba_pointer in [ptr_08, ptr_09]:
        p_idx = 0
        while True:
            p_idx = rom_data.find(gba_pointer, p_idx)
            if p_idx == -1: break
            if p_idx % 4 == 0:
                table_entry_addr = p_idx
                print(f"🎯 目次テーブルを特定！位置: 0x{table_entry_addr:X} (ポインタ: {gba_pointer.hex().upper()})")
                break
            p_idx += 4
        if table_entry_addr != -1: break

    if table_entry_addr == -1:
        print("❌ アドレスに対する目次ポインタが見つかりませんでした。解析を終了します。")
        return

    start_table_ptr = table_entry_addr
    while start_table_ptr >= 4:
        val = struct.unpack("<I", rom_data[start_table_ptr - 4 : start_table_ptr])[0]
        if 0x08000000 <= val <= 0x0A000000:
            start_table_ptr -= 4
        else:
            break

    print("\n🚀 【4】条件に一致するIDの画像を抽出・生成中...")
    print("-" * 80)

    # 🛠️ 優先度判定のロジック
    use_specific = len(SPECIFIC_IDS) > 0
    if use_specific:
        print(f"🔥 【優先モード】個別指定されたIDリストのみを出力します: {SPECIFIC_IDS}")
        max_limit_id = max(SPECIFIC_IDS)
    else:
        start_id, end_id = ID_RANGE
        print(f"📊 【範囲モード】ID: {start_id} から {end_id} までを出力します。")
        max_limit_id = end_id

    current_table_ptr = start_table_ptr
    poke_id = 1
    extracted_count = 0
    
    while current_table_ptr < len(rom_data):
        val = struct.unpack("<I", rom_data[current_table_ptr : current_table_ptr + 4])[0]
        if not (0x08000000 <= val <= 0x0A000000): break
        
        # 🛠️ 現在の ID が出力条件にマッチするか判定
        should_extract = False
        if use_specific:
            if poke_id in SPECIFIC_IDS:
                should_extract = True
        else:
            if start_id <= poke_id <= end_id:
                should_extract = True

        if should_extract:
            actual_img_addr = val & 0x01FFFFFF
            if 0x100000 <= actual_img_addr < len(rom_data):
                raw_poke_data = rom_data[actual_img_addr : actual_img_addr + 1024]
                f1_idx = get_indexed_pixels(raw_poke_data[0:512])
                f2_idx = get_indexed_pixels(raw_poke_data[512:1024])
                
                combined_canvas = Image.new('RGB', (192, 64))
                
                for p_num in range(6):
                    pal_rgb = PALETTES[p_num]
                    single_img = Image.new('P', (32, 64))
                    single_img.putpalette(make_palette_list(pal_rgb))
                    single_img.putdata(f1_idx + f2_idx)
                    combined_canvas.paste(single_img.convert('RGB'), (p_num * 32, 0))
                    
                out_name = f"{poke_id:03d}_0x{actual_img_addr:X}.png"
                combined_canvas.save(os.path.join(output_dir, out_name), "PNG")
                
                mark = "⭐ (手がかり元)" if actual_img_addr == found_addr else ""
                print(f" 📦 [{poke_id:03d}] {out_name} を出力しました。 {mark}")
                extracted_count += 1

        current_table_ptr += 4
        poke_id += 1
        
        # 処理の最大上限を超えたらループを抜ける（無駄なスキャン防止）
        if poke_id > max_limit_id: break

    print("-" * 80)
    print(f"✨ 【条件付き一括出力完了】 計 {extracted_count} 枚の画像を出力しました。")
    print(f" ➔ 保存先: {output_dir}")
    
    open_folder_and_exit(output_dir)

if __name__ == "__main__":
    main()