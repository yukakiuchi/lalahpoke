import os
import sys
import struct
import subprocess
from PIL import Image

# ==========================================
# ★ 設定エリア ★
# ==========================================
ROM_PATH = '/Users/yu/Desktop/sprites_roms/adventure_red/Adventure_Red_Beta_15_Expansion.gba'
SAMPLE_IMAGE_PATH = '/Users/yu/Desktop/bbb.png'
BASE_OUTPUT_DIR = '/Users/yu/Desktop/search_icon_result'

# コメントアウトされている、または空の場合は「発見アドレスから20枚出力モード」になります
# ID_RANGE = (1350, 1550)
# SPECIFIC_IDS = []

# 6つのパレット定義
PALETTES = {
    0: [(98, 156, 131), (131, 131, 115), (189, 189, 189), (255, 255, 255), (189, 164, 65), (246, 246, 41), (213, 98, 65), (246, 148, 41), (139, 123, 255), (98, 74, 205), (238, 115, 156), (255, 180, 164), (164, 197, 255), (106, 172, 156), (98, 98, 90), (65, 65, 65)],
    1: [(98, 156, 131), (115, 115, 115), (189, 189, 189), (255, 255, 255), (123, 156, 74), (156, 205, 74), (148, 246, 74), (238, 115, 156), (246, 148, 246), (189, 164, 90), (246, 230, 41), (246, 246, 172), (213, 213, 106), (230, 74, 41), (98, 98, 90), (65, 65, 65)],
    2: [(98, 156, 131), (123, 123, 123), (189, 189, 180), (255, 255, 255), (115, 115, 205), (164, 172, 246), (180, 131, 90), (238, 197, 139), (197, 172, 41), (246, 246, 41), (246, 98, 82), (148, 123, 205), (197, 164, 205), (189, 41, 156), (98, 98, 90), (65, 65, 65)],
    3: [(98, 156, 131), (115, 115, 115), (189, 189, 189), (255, 255, 255), (65, 106, 148), (98, 148, 164), (164, 197, 255), (238, 115, 156), (213, 98, 65), (189, 164, 90), (246, 230, 41), (246, 246, 172), (213, 213, 106), (246, 148, 41), (98, 98, 90), (65, 65, 65)],
    4: [(98, 156, 131), (115, 115, 115), (189, 189, 189), (255, 255, 255), (123, 156, 74), (156, 205, 74), (65, 106, 148), (238, 115, 156), (246, 148, 246), (189, 164, 90), (246, 246, 139), (164, 197, 255), (98, 148, 164), (213, 98, 65), (98, 98, 90), (65, 65, 65)],
    5: [(98, 156, 131), (123, 123, 123), (189, 180, 180), (255, 255, 255), (123, 156, 74), (156, 205, 74), (180, 131, 90), (238, 197, 139), (197, 172, 41), (246, 246, 41), (213, 98, 65), (148, 123, 205), (197, 164, 205), (246, 148, 41), (98, 98, 90), (65, 65, 65)]
}
# ==========================================

def get_unique_dir(base_dir):
    if not os.path.exists(base_dir): return base_dir
    counter = 1
    while True:
        new_dir = f"{base_dir}_{counter}"
        if not os.path.exists(new_dir): return new_dir
        counter += 1

def hex_dump_around(data, addr, window=32, title="バイナリダンプ"):
    start = max(0, addr - window)
    end = min(len(data), addr + window + 16)
    print(f"\n--- 🔍 {title} (0x{start:X} 〜 0x{end:X}) ---")
    for i in range(start, end, 16):
        chunk = data[i:i+16]
        hex_str = " ".join(f"{b:02X}" for b in chunk)
        prefix = "👉" if i <= addr < i+16 else "  "
        print(f"{prefix} 0x{i:07X}: {hex_str:<48}")
    print("-" * 50)

def apply_palette_mapping(pixels):
    """
    パレットのインデックス並びを反転させて変換する
    0x0 ↔ 0xF, 0x1 ↔ 0xE, 0x2 ↔ 0xD, 0x3 ↔ 0xC ... という全反転ルール
    """
    # 0〜Fの値を反転させる（0->F, 1->E, 2->D, ..., F->0）
    # ただし、透明色などの扱いを考慮して「1〜F」の範囲のみ反転させる場合は 0x10 - p とします
    # ここでは完全な反転 (p = 0x0F - p) を適用します
    return [(0x0F - p) & 0x0F for p in pixels]

def convert_pixels_to_gba_4bpp(pixels, img_w, start_y):
    """ピクセルリストを受け取り、GBAの4bppタイル形式(bytearray)に変換する"""
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
        
    with open(ROM_PATH, "rb") as f: 
        rom_data = f.read()

    print("🖼️  【1】手がかり画像のバイナリ変換中...")
    try:
        img = Image.open(SAMPLE_IMAGE_PATH).convert('P')
    except Exception as e:
        print(f"❌ 画像ファイルの読み込みに失敗しました: {e}")
        return

    pixels = list(img.getdata() if hasattr(img, 'getdata') else img.get_flattened_data())
    img_w, _ = img.size

    # 🌟 2パターンのバイナリを生成する
    # パターン1: そのまま (画像ソフト上のパレット順)
    target_original = convert_pixels_to_gba_4bpp(pixels, img_w, start_y=0)
    
    # パターン2: ROM仕様に合わせたパレット補正版
    mapped_pixels = apply_palette_mapping(pixels)
    target_mapped = convert_pixels_to_gba_4bpp(mapped_pixels, img_w, start_y=0)

    print("🔍 【2】32x32マス（512バイト）丸ごと完全一致でROM内をスキャン中...")
    
    # まずそのままの形式で検索
    idx = rom_data.find(target_original)
    if idx != -1:
        found_addr = idx
        print(f"🎯 そのままの形式で完全一致しました！ ➔ アドレス: 0x{found_addr:X}")
    else:
        print(" ➔ そのままの形式で見つからず、ROM変換形式(パレット補正版)で再検索...")
        # 次に変換形式で検索
        idx = rom_data.find(target_mapped)
        if idx != -1:
            found_addr = idx
            print(f"🎯 ROM変換形式で完全一致しました！ ➔ アドレス: 0x{found_addr:X}")
        else:
            print("❌ 32x32の完全一致バイナリが両方のパターンでROM内に見つかりませんでした。")
            print(" ➔ 原因の可能性: 未知のパレットズレがあるか、画像自体が間違っている可能性があります。")
            return

    # ヒットした周辺バイナリをダンプ表示
    hex_dump_around(rom_data, found_addr, window=32, title="特定画像アドレス周辺のバイナリ")

    print("\n🔮 【3】ROM仕様に合わせた次のアイコン画像候補アドレスを算出中...")
    next_candidates = []
    for offset in [512, 1024, 1536, 2048, 3072, 4096]:
        c_addr = found_addr + offset
        if c_addr < len(rom_data):
            next_candidates.append(c_addr)
            print(f" ➔ 次のアイコン画像候補アドレス案: 0x{c_addr:X} (起点 + {offset}バイト)")

    print("\n🛰️  【4】特定アドレスを指す「ポインタ目次」を非アライメント(1B刻み)で全検索中...")
    ptr_08 = struct.pack("<I", (found_addr & 0x00FFFFFF) | 0x08000000)
    ptr_09 = struct.pack("<I", found_addr + 0x08000000)
    
    table_entry_addr = -1
    for gba_pointer in [ptr_08, ptr_09]:
        p_idx = 0
        while True:
            p_idx = rom_data.find(gba_pointer, p_idx)
            if p_idx == -1: break
            table_entry_addr = p_idx
            print(f"🎯 ポインタ発見！位置: 0x{table_entry_addr:X} (データ: {gba_pointer.hex().upper()})")
            break
        if table_entry_addr != -1: break

    if table_entry_addr == -1:
        print("❌ アドレスに対する目次ポインタがROM内から一切見つかりませんでした。解析を終了します。")
        return

    hex_dump_around(rom_data, table_entry_addr, window=32, title="ポインタテーブル周辺のバイナリ")

    print("\n📊 【5】ポインタテーブル構造の法則性・自動分析")
    print("=" * 80)
    
    pointer_step = 4
    detected_step = False
    
    for offset in range(1, 32, 1):
        check_ptr = table_entry_addr + offset
        if check_ptr + 4 > len(rom_data): break
        
        val = struct.unpack("<I", rom_data[check_ptr:check_ptr+4])[0]
        if (val & 0xFF000000) == 0x08000000:
            potential_real_addr = val - 0x08000000
            
            for cand in next_candidates:
                if abs(potential_real_addr - cand) < 64:
                    pointer_step = offset
                    detected_step = True
                    print(f"🔥 法則を看破しました！")
                    print(f" ➔ ポインタは 【 {pointer_step} バイト周期 】 で並んでいます。")
                    break
        if detected_step: break

    if not detected_step:
        print("⚠️ 次のポインタとの明確な連動法則が見つかりませんでした。デフォルトの4バイト直列として処理を続行します。")

    # モード判定
    globals_dict = globals()
    has_range = "ID_RANGE" in globals_dict and isinstance(globals_dict["ID_RANGE"], tuple)
    has_specific = "SPECIFIC_IDS" in globals_dict and isinstance(globals_dict["SPECIFIC_IDS"], list) and len(globals_dict["SPECIFIC_IDS"]) > 0

    if not has_range and not has_specific:
        print("\n🎯 【モード検出】ID指定がコメントアウトされているため、【検索出力フォーカスモード】で起動します。")
        print(f" ➔ 見つかったポインタ(0x{table_entry_addr:X})を起点に、下流へ20枚連続で抽出します。")
        start_table_ptr = table_entry_addr
        scan_limit = 5000
        mode_focus = True
        max_limit_id = 999999
    else:
        print("\n📊 【モード検出】ID指定が有効なため、【インデックス範囲抽出モード】で起動します。")
        start_table_ptr = table_entry_addr
        while start_table_ptr >= pointer_step:
            val = struct.unpack("<I", rom_data[start_table_ptr - pointer_step : start_table_ptr - pointer_step + 4])[0]
            if 0x08000000 <= val <= 0x0A000000:
                start_table_ptr -= pointer_step
            else:
                break
        scan_limit = 999999
        mode_focus = False
        max_limit_id = max(SPECIFIC_IDS) if has_specific else ID_RANGE[1]

    print(f"📍 処理を開始するテーブル位置: 0x{start_table_ptr:X}")

    output_dir = get_unique_dir(BASE_OUTPUT_DIR)
    os.makedirs(output_dir, exist_ok=True)

    print("\n🚀 【6】看破した法則に従って画像を抽出・生成中...")
    print("-" * 80)

    current_table_ptr = start_table_ptr
    poke_id = 1
    extracted_count = 0
    
    while current_table_ptr < len(rom_data):
        val = struct.unpack("<I", rom_data[current_table_ptr : current_table_ptr + 4])[0]
        if not (0x08000000 <= val <= 0x0A000000): break
        
        should_extract = False
        if mode_focus:
            should_extract = True
        else:
            if has_specific:
                if poke_id in SPECIFIC_IDS: should_extract = True
            else:
                if ID_RANGE[0] <= poke_id <= ID_RANGE[1]: should_extract = True

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
                
                extracted_count += 1
                out_name = f"{extracted_count:03d}_0x{actual_img_addr:X}.png"
                combined_canvas.save(os.path.join(output_dir, out_name), "PNG")
                
                mark = "⭐ (手がかり元)" if actual_img_addr == found_addr else ""
                print(f" 📦 [{extracted_count:03d}] {out_name} を出力しました。 {mark}")

                if mode_focus and extracted_count >= scan_limit:
                    break

        current_table_ptr += pointer_step
        poke_id += 1
        if not mode_focus and poke_id > max_limit_id: break

    print("-" * 80)
    print(f"✨ 【抽出完了】 計 {extracted_count} 枚の画像を出力しました。")
    print(f" ➔ 保存先: {output_dir}")
    
    if sys.platform == "darwin": subprocess.run(["open", output_dir])
    elif sys.platform == "win32": os.startfile(output_dir)
    sys.exit(0)

if __name__ == "__main__":
    main()