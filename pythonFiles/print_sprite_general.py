import os
import sys
import struct
import subprocess
from PIL import Image
from collections import Counter

# ------------------ 📝 ユーザー設定エリア ------------------
ROM_PATH = '/Users/yu/Downloads/spades&clubs demo 0.2.1.gba'
OUTPUT_BASE_DIR = '/Users/yu/Desktop/extracted_pokemon_syncedaaaa'

HINT_IMG_ADDR = 0xD4183C       # 画像アドレスのヒント
HINT_PAL_ADDR = 0xD41B9C       # 通常パレットアドレスのヒント
HINT_SHINY_ADDR = None         # 色違いパレットアドレス（NoneのままでOK）
SCAN_COUNT = 445               # 抽出したいモンスターの最大数
# -----------------------------------------------------

def gba_pal_to_rgb888(pal_data):
    rgb = []
    for i in range(0, len(pal_data), 2):
        if i+1 < len(pal_data):
            val = pal_data[i] | (pal_data[i+1] << 8)
            rgb.extend([(val & 0x1F) << 3, ((val >> 5) & 0x1F) << 3, ((val >> 10) & 0x1F) << 3])
    while len(rgb) < 768: rgb.extend([0, 0, 0])
    return rgb[:768]

def parse_lz77_header(data, offset):
    if offset + 3 >= len(data) or data[offset] != 0x10: return None
    return data[offset+1] | (data[offset+2] << 8) | (data[offset+3] << 16)

def lz77_decompress_gba(data, offset):
    size = parse_lz77_header(data, offset)
    if size is None or size < 4 or size > 0x10000: return None, 0
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

def extract_only_images(rom_data, start_addr):
    """画像ブロック内から不要なダミーパレットを無視して、大サイズの画像だけを回収"""
    ptr = start_addr
    images = []
    for _ in range(4):
        if ptr >= len(rom_data) or rom_data[ptr] != 0x10: break
        decomp_size = parse_lz77_header(rom_data, ptr)
        dec_data, next_ptr = lz77_decompress_gba(rom_data, ptr)
        if dec_data:
            if decomp_size and decomp_size >= 1000:
                images.append(dec_data)
            ptr = next_ptr
        else:
            ptr += 1
    return images

def fetch_palette_32b(rom_data, addr):
    if addr < len(rom_data) and rom_data[addr] == 0x10:
        dec, _ = lz77_decompress_gba(rom_data, addr)
        if dec and len(dec) >= 32: return dec[:32]
    if addr + 32 <= len(rom_data):
        return rom_data[addr:addr+32]
    return b'\x00' * 32

def save_sprite(img_data, pal_data, path):
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

def analyze_table_structure_flexible(rom_data, target_data_addr):
    """
    ポインタの周辺から12/16バイトなどの周期(ストライド)とID連番法則を動的に学習する。
    失敗した場合はその具体的な理由を文字列で返す。
    """
    gba_pointer = struct.pack("<I", target_data_addr + 0x08000000)
    
    # ROM全体から対象ポインタをすべて検索
    matching_addresses = []
    for addr in range(0, len(rom_data) - 4, 4):
        if rom_data[addr:addr+4] == gba_pointer:
            matching_addresses.append(addr)
            
    if not matching_addresses:
        return None, f"指定アドレス (0x{target_data_addr:X}) を指すGBAポインタが見つかりません。ヒントアドレスが間違っている可能性があります。"

    # ポインタ同士の間隔（ストライド）を計算し、最も頻出する周期を割り出す
    if len(matching_addresses) >= 2:
        intervals = []
        for i in range(len(matching_addresses) - 1):
            diff = matching_addresses[i+1] - matching_addresses[i]
            if diff in [8, 12, 16, 24, 32]:  # 一般的なGBAレコード長
                intervals.append(diff)
        
        if intervals:
            stride = Counter(intervals).most_common(1)[0][0]
        else:
            stride = 8 # デフォルト
    else:
        stride = 8

    # 最初に見つかったポインタの位置を基準にする
    base_match_addr = matching_addresses[0]
    
    # ストライド（周期）の範囲内で、前後で1ずつ増減しているIDフィールド（1バイトまたは2バイト）を自動スキャン
    id_offset = -1
    id_size = 1
    
    # 周期内の各バイトを検査
    for off in range(stride):
        # ポインタ自身がある4バイトはスキップ
        if base_match_addr % stride <= off < (base_match_addr % stride) + 4:
            continue
            
        # 1バイトの連続性確認
        prev_idx = base_match_addr - stride + off
        next_idx = base_match_addr + stride + off
        if 0 <= prev_idx and next_idx < len(rom_data):
            v_prev = rom_data[prev_idx]
            v_curr = rom_data[base_match_addr + off]
            v_next = rom_data[next_idx]
            if v_curr == (v_prev + 1) & 0xFF and v_next == (v_curr + 1) & 0xFF:
                id_offset, id_size = off, 1
                break
                
        # 2バイト（リトルエンディアン）の連続性確認
        if 0 <= prev_idx and next_idx + 1 < len(rom_data):
            v_prev = struct.unpack("<H", rom_data[prev_idx:prev_idx+2])[0]
            v_curr = struct.unpack("<H", rom_data[base_match_addr + off : base_match_addr + off + 2])[0]
            v_next = struct.unpack("<H", rom_data[next_idx:next_idx+2])[0]
            if v_curr == v_prev + 1 and v_next == v_curr + 1:
                id_offset, id_size = off, 2
                break

    if id_offset == -1:
        return None, f"ポインタは特定（ストライド: {stride}B）できましたが、周辺に規則的に1ずつ増加するID（連番）の法則が見つかりません。構造が特殊か、空データで分断されています。"

    # 現在のIDを取得して先頭(ID: 1)のアドレスを逆算
    if id_size == 1:
        current_id = rom_data[base_match_addr + id_offset]
    else:
        current_id = struct.unpack("<H", rom_data[base_match_addr + id_offset : base_match_addr + id_offset + 2])[0]
        
    root_addr = base_match_addr - (current_id - 1) * stride
    
    return {
        'root_addr': root_addr,
        'current_id': current_id,
        'id_offset': id_offset,
        'id_size': id_size,
        'stride': stride
    }, None

def fallback_serial_scan(rom_data, normal_pal):
    """
    【セーフティネット】テーブル解析が破綻した場合、
    64x64ピクセルの解凍サイズ(2048バイト=0x0800)を持つLZ77シグネチャ『10 00 08 00』を直接全スキャンする
    """
    print("\n🚨 【緊急発動: シリアル・バイナリスキャンモード】")
    print("➔ テーブル構造を無視し、64x64画像(LZ77サイズ:2048B)のヘッダ『10 00 08 00』を直接全走査します。")
    print("-" * 80)
    
    target_signature = b'\x10\x00\x08\x00'
    success_count = 0
    ptr = 0
    
    while True:
        ptr = rom_data.find(target_signature, ptr)
        if ptr == -1: break
        if success_count >= SCAN_COUNT: break
        
        # 見つかった場所から画像をデコンプレス
        images = extract_only_images(rom_data, ptr)
        if images:
            display_id = success_count + 1
            base_name = f"fallback_{display_id:03d}_addr_{ptr:06X}"
            
            # フロント画像
            save_sprite(images[0], normal_pal, os.path.join(OUTPUT_BASE_DIR, f"{base_name}.png"))
            
            # バック画像（あれば）
            if len(images) >= 2:
                save_sprite(images[1], normal_pal, os.path.join(OUTPUT_BASE_DIR, f"{base_name}_back.png"))
                
            print(f"📸 [シリアル検出 ID {display_id:03d}] アドレス: 0x{ptr:X} からの画像化に成功！")
            success_count += 1
            
        ptr += 4 # 次の検索へ進める
        
    return success_count

def main():
    if not os.path.exists(ROM_PATH):
        print(f"❌ ROMファイルが見つかりません: {ROM_PATH}")
        return
    with open(ROM_PATH, 'rb') as f: rom_data = f.read()
    if not os.path.exists(OUTPUT_BASE_DIR): os.makedirs(OUTPUT_BASE_DIR)

    print("🕵️‍♂️ 【超適応型バイナリ・インテリジェンスシステムアプデ版】稼働")
    print("=" * 80)

    # パレットを確保しておく（フォールバックでも共通で使用するため）
    normal_pal = fetch_palette_32b(rom_data, HINT_PAL_ADDR)

    # 1. 画像構造を動的・臨機応変に学習
    img_info, img_err = analyze_table_structure_flexible(rom_data, HINT_IMG_ADDR)
    pal_info, pal_err = analyze_table_structure_flexible(rom_data, HINT_PAL_ADDR)

    # どちらかのテーブル解析が失敗した、あるいは矛盾がある場合は即座にフォールバックへ
    if not img_info or not pal_info:
        print("⚠️ 【警告】通常のテーブル解析を中断します。")
        if img_err: print(f" ➔ 画像テーブルの失敗理由: {img_err}")
        if pal_err: print(f" ➔ パレットテーブルの失敗理由: {pal_err}")
        
        # あなたの提案した10 00 08 00 直接スキャンモードへ
        scanned = fallback_serial_scan(rom_data, normal_pal)
        print("=" * 80)
        print(f"✨ 【全工程完了】シリアルスキャンにより、{scanned} 匹を出力しました！")
        if scanned > 0:
            try:
                if sys.platform == 'darwin': subprocess.Popen(['open', OUTPUT_BASE_DIR])
                elif sys.platform == 'win32': subprocess.Popen(['explorer', os.path.normpath(OUTPUT_BASE_DIR)])
            except: pass
        return

    # 解析に成功した場合のパラメータ表示（12Bや16Bなど自動適応された結果）
    print(f"📸 [画像解析適応]  Root: 0x{img_info['root_addr']:X} | 検出周期: {img_info['stride']}バイト | 内部ID: {img_info['current_id']}")
    print(f"🎨 [パレット適応]  Root: 0x{pal_info['root_addr']:X} | 検出周期: {pal_info['stride']}バイト | 内部ID: {pal_info['current_id']}")
    print("=" * 80)
    print(f"🚀 【同期標準スキャン開始】ターゲット数: {SCAN_COUNT} 匹")
    print("-" * 80)

    success_count = 0
    img_root = img_info['root_addr']
    pal_root = pal_info['root_addr']
    img_stride = img_info['stride']
    pal_stride = pal_info['stride']

    for idx in range(SCAN_COUNT):
        display_id = idx + 1
        
        img_entry = img_root + (idx * img_stride)
        pal_entry = pal_root + (idx * pal_stride)
        
        if img_entry + 4 > len(rom_data) or pal_entry + 4 > len(rom_data): 
            print(f"⚠️ ROMデータの終端に達したため終了します。")
            break

        # 空データ（00 00 00 00）や不正ポインタのスキップ処理
        img_ptr_val = struct.unpack("<I", rom_data[img_entry:img_entry+4])[0]
        pal_ptr_val = struct.unpack("<I", rom_data[pal_entry:pal_entry+4])[0]
        
        if img_ptr_val == 0 or pal_ptr_val == 0 or not (0x08000000 <= img_ptr_val < 0x0A000000):
            print(f"🕳️ [ID {display_id:03d}] 空データ（穴）または不正ポインタを検知。次の有効な地点へスキップします。")
            continue

        # 実アドレス変換
        img_data_addr = img_ptr_val - 0x08000000
        pal_data_addr = pal_ptr_val - 0x08000000

        # 画像データの分離抽出
        images = extract_only_images(rom_data, img_data_addr)
        if not images:
            print(f"⚠️ [ID {display_id:03d}] アドレス 0x{img_data_addr:X} からの画像デコンプレスに失敗。")
            continue

        # パレットデータの取得
        current_pal = fetch_palette_32b(rom_data, pal_data_addr)
        
        # 内部IDの取得
        if pal_info['id_size'] == 1:
            target_internal_id = rom_data[pal_entry + pal_info['id_offset']]
        else:
            target_internal_id = struct.unpack("<H", rom_data[pal_entry + pal_info['id_offset'] : pal_entry + pal_info['id_offset'] + 2])[0]

        # ファイル出力処理
        base_name = f"{display_id:03d}_{img_data_addr:06X}_{pal_data_addr:06X}"
        save_sprite(images[0], current_pal, os.path.join(OUTPUT_BASE_DIR, f"{base_name}.png"))

        if len(images) >= 2:
            save_sprite(images[1], current_pal, os.path.join(OUTPUT_BASE_DIR, f"{base_name}_back.png"))

        print(f"🔮 [ID {display_id:03d} (内部ID:{target_internal_id})] 抽出成功 | 画像:0x{img_data_addr:X} | パレ:0x{pal_data_addr:X} (周期:{img_stride}B)")
        success_count += 1

    print("=" * 80)
    print(f"✨ 【全工程完了】適応型同期システムにより、{success_count} 匹のポケモンを出力しました！")

    # もし標準スキャンが一件も抜けなかった場合は最終手段としてシリアルスキャンを実行
    if success_count == 0:
        print("\n⚠️ 標準スキャンによる出力が0件だったため、フォールバック（シリアルスキャン）を自動起動します。")
        success_count = fallback_serial_scan(rom_data, normal_pal)

    try:
        if sys.platform == 'darwin': subprocess.Popen(['open', OUTPUT_BASE_DIR])
        elif sys.platform == 'win32': subprocess.Popen(['explorer', os.path.normpath(OUTPUT_BASE_DIR)])
    except: pass

if __name__ == "__main__":
    main()