import os
import sys
import struct
import subprocess
from PIL import Image

# ------------------ 📝 ユーザー設定エリア ------------------
ROM_PATH = '/Users/yu/Desktop/sprites_roms/weird type fun/weird type fun v1.93.gba'
OUTPUT_BASE_DIR = '/Users/yu/Desktop/extracted_pokemon_syncedaaaa'

HINT_IMG_ADDR = 0xEC0480       # 画像アドレス
HINT_PAL_ADDR = 0xD343DC       # 通常パレットアドレス
HINT_SHINY_ADDR = None     # 色違いパレットアドレス（わからない場合は None または 0 に設定）
SCAN_COUNT = 445               # 抽出したいモンスターの数（352匹〜445匹など調整可能）
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

def analyze_table_structure(rom_data, target_data_addr):
    """
    指定されたアドレスを指すポインタを検索し、
    周辺バイナリの連続性から「IDが格納されている位置」と「現在のID」を自動で学習・記憶する
    """
    gba_pointer = struct.pack("<I", target_data_addr + 0x08000000)
    for addr in range(0, len(rom_data) - 8, 4):
        if rom_data[addr:addr+4] == gba_pointer:
            # レコード長8バイトと仮定し、後半4バイト（オフセット4〜7）で1ずつ増える場所を探す
            id_offset = -1
            id_size = 1
            for off in range(4, 8):
                prev_val = rom_data[addr - 8 + off] if addr >= 8 else None
                curr_val = rom_data[addr + off]
                next_val = rom_data[addr + 8 + off] if addr + 8 < len(rom_data) else None
                if prev_val is not None and next_val is not None:
                    if curr_val == (prev_val + 1) & 0xFF and next_val == (curr_val + 1) & 0xFF:
                        id_offset = off
                        id_size = 1
                        break
            
            # 1バイトで判定できない場合、2バイト（リトルエンディアン）の連続性を検証
            if id_offset == -1:
                for off in range(4, 7):
                    prev_val = struct.unpack("<H", rom_data[addr - 8 + off : addr - 8 + off + 2])[0] if addr >= 8 else None
                    curr_val = struct.unpack("<H", rom_data[addr + off : addr + off + 2])[0] # 🛠️ 変数名の間違い(offset -> off)を修正
                    next_val = struct.unpack("<H", rom_data[addr + 8 + off : addr + 8 + off + 2])[0] if addr + 8 < len(rom_data) else None
                    if prev_val is not None and next_val is not None:
                        if curr_val == prev_val + 1 and next_val == curr_val + 1:
                            id_offset = off
                            id_size = 2
                            break

            # 法則が見つかった場合、IDを解析してテーブルの「先頭（ID 1）」のアドレスを算出して返す
            if id_offset != -1:
                if id_size == 1:
                    current_id = rom_data[addr + id_offset]
                else:
                    current_id = struct.unpack("<H", rom_data[addr + id_offset : addr + id_offset + 2])[0]
                
                root_addr = addr - (current_id - 1) * 8
                return root_addr, current_id, id_offset, id_size
            
            # フォールバック（自動検出に失敗した場合、後半2バイトを暫定IDとする）
            current_id = struct.unpack("<H", rom_data[addr+4:addr+6])[0]
            if 0 < current_id < 2000:
                return addr - (current_id - 1) * 8, current_id, 4, 2
                
    return None, None, None, None

def count_total_images(rom_data, root_addr, id_offset, id_size):
    """画像テーブルの下限を走査し、このROMに格納されている最大画像（ポケモン）数を自動で割り出す"""
    count = 0
    addr = root_addr
    expected_id = 1
    while addr + 8 <= len(rom_data):
        ptr_val = struct.unpack("<I", rom_data[addr:addr+4])[0]
        if ptr_val < 0x08000000 or ptr_val > 0x09FFFFFF: break
        
        if id_size == 1: curr_id = rom_data[addr + id_offset]
        else: curr_id = struct.unpack("<H", rom_data[addr + id_offset : addr + id_offset + 2])[0]
            
        if curr_id != expected_id: break
        count += 1
        expected_id += 1
        addr += 8
    return count

def main():
    if not os.path.exists(ROM_PATH):
        print(f"❌ ROMファイルが見つかりません: {ROM_PATH}")
        return
    with open(ROM_PATH, 'rb') as f: rom_data = f.read()
    if not os.path.exists(OUTPUT_BASE_DIR): os.makedirs(OUTPUT_BASE_DIR)

    print("🕵️‍♂️ 【自律型バイナリ・ラーニングシステム稼働】")
    print("=" * 80)

    # 1. 画像と通常パレットの構造・現在IDをROMから自動学習
    img_root, img_id, img_ioff, img_isize = analyze_table_structure(rom_data, HINT_IMG_ADDR)
    pal_root, pal_id, pal_ioff, pal_isize = analyze_table_structure(rom_data, HINT_PAL_ADDR)

    if not img_root or not pal_root:
        print("❌ 必須テーブル（画像または通常パレット）の構造解析に失敗しました。")
        return

    print(f"📸 [画像解析完了]    Root: 0x{img_root:X} | 検出ID: {img_id} (格納オフセット: +{img_ioff}B)")
    print(f"🎨 [通常色パレ完了] Root: 0x{pal_root:X} | 検出ID: {pal_id} (格納オフセット: +{pal_ioff}B)")

    # 画像テーブルの限界値を自動スキャンして総数を記憶
    total_images = count_total_images(rom_data, img_root, img_ioff, img_isize)
    print(f"📊 [ROM内総数推測]  このROMの有効な登録画像数は【 {total_images} 匹 】と判明しました。")

    # 2. 色違いパレットの自動位置割り出し
    shiny_table_root = None
    s_ioff, s_isize = 4, 2  # デフォルトの構造定義フォールバック用
    
    if HINT_SHINY_ADDR and HINT_SHINY_ADDR != 0:
        # アドレスが手動指定されている場合はそこからIDを学習
        s_root, s_id, s_ioff_loaded, s_isize_loaded = analyze_table_structure(rom_data, HINT_SHINY_ADDR)
        if s_root is not None:
            shiny_table_root = s_root
            s_ioff, s_isize = s_ioff_loaded, s_isize_loaded
            print(f"✨ [色違い位置確定] ユーザー指定アドレスの解析により特定 ➔ Root: 0x{shiny_table_root:X} (内部ID: {s_id})")
    else:
        # アドレスが空欄(Noneや0)の場合、学習データ（総画像数）を元に、通常色の後ろに合体していると仮定して境界を自動計算
        if total_images > 0:
            shiny_table_root = pal_root + (total_images * 8)
            s_ioff, s_isize = pal_ioff, pal_isize  # 通常パレットの構造をコピー
            print(f"🧠 [色違い自動推測] アドレス未指定のため、通常色の最大数({total_images}個)を境に自動決定 ➔ 推定Root: 0x{shiny_table_root:X}")
        else:
            print("⚠️ [色違いスキップ] 画像総数が不明なため、色違いの自動推測を断念しました。通常色のみ抽出します。")

    print("=" * 80)
    print(f"🚀 【同期抽出開始】ターゲット数: {SCAN_COUNT} 匹")
    print("-" * 80)

    success_count = 0
    for idx in range(SCAN_COUNT):
        display_id = idx + 1
        
        # 各エントリのアドレス計算
        img_entry = img_root + (idx * 8)
        pal_entry = pal_root + (idx * 8)
        
        if img_entry + 8 > len(rom_data) or pal_entry + 8 > len(rom_data): break

        # 通常パレットテーブルのエントリから、このポケモンの「本来の内部ID」を読み取る
        if pal_isize == 1:
            target_internal_id = rom_data[pal_entry + pal_ioff]
        else:
            target_internal_id = struct.unpack("<H", rom_data[pal_entry + pal_ioff : pal_entry + pal_ioff + 2])[0]

        # ポインタからROM実アドレスへ変換
        img_data_addr = struct.unpack("<I", rom_data[img_entry:img_entry+4])[0] - 0x08000000
        pal_data_addr = struct.unpack("<I", rom_data[pal_entry:pal_entry+4])[0] - 0x08000000

        # 画像データの分離抽出 (ダミーパレットは無視して画像のみ回収)
        images = extract_only_images(rom_data, img_data_addr)
        if not images: continue

        # 通常パレットデータの取得
        normal_pal = fetch_palette_32b(rom_data, pal_data_addr)
        
        # 🛠️ 【色違いズレ対策：ID同期型自動スキャンロジック】
        # 単純に idx*8 でアクセスせず、通常パレットと「同じ内部ID」を持つエントリを色違いテーブルから動的に探す
# --- 既存の shiny_pal 取得ロジックを以下に差し替え ---
        shiny_pal = None
        shiny_data_addr = None
        
        if False:
            # 💡 修正：IDが一致しない場合でも、通常パレットからの「物理的な距離(オフセット)」が
            # 一定であると仮定し、そのオフセットを強制的に適用する
            # idx * 8 はテーブルの物理的な位置を指すので、最も確実です
            shiny_entry = shiny_table_root + (idx * 8) 

            if shiny_entry + 8 <= len(rom_data):
                # 念のため、shiny_entryの内容がポインタとして妥当か（0x08...）だけチェック
                s_ptr_val = struct.unpack("<I", rom_data[shiny_entry:shiny_entry+4])[0]
                if 0x08000000 <= s_ptr_val < 0x0A000000:
                    shiny_data_addr = s_ptr_val - 0x08000000
                    shiny_pal = fetch_palette_32b(rom_data, shiny_data_addr)
            
            # 見つからなかった場合のセーフティフォールバック
            if not shiny_entry:
                shiny_entry = shiny_table_root + (idx * 8)

            if shiny_entry and shiny_entry + 8 <= len(rom_data):
                s_ptr_val = struct.unpack("<I", rom_data[shiny_entry:shiny_entry+4])[0]
                if 0x08000000 <= s_ptr_val < 0x0A000000:
                    shiny_data_addr = s_ptr_val - 0x08000000
                    shiny_pal = fetch_palette_32b(rom_data, shiny_data_addr)

        # ファイル出力処理
        base_name = f"{display_id:03d}_{img_data_addr:06X}_{pal_data_addr:06X}"
        
        # フロントグラフィック出力
        save_sprite(images[0], normal_pal, os.path.join(OUTPUT_BASE_DIR, f"{base_name}.png"))
        # if shiny_pal and shiny_data_addr is not None:
        #     shiny_name = f"{display_id:03d}_{img_data_addr:06X}_{shiny_data_addr:06X}_shiny"
        #     save_sprite(images[0], shiny_pal, os.path.join(OUTPUT_BASE_DIR, f"{shiny_name}.png")) # 🛠️ "+"の除去と構文修正

        # バックグラフィック（存在すれば）
        if len(images) >= 2:
            save_sprite(images[1], normal_pal, os.path.join(OUTPUT_BASE_DIR, f"{base_name}_back.png"))
            # if shiny_pal and shiny_data_addr is not None:
            #     save_sprite(images[1], shiny_pal, os.path.join(OUTPUT_BASE_DIR, f"{shiny_name}_back_shiny.png")) # 🛠️ out_prefixを修正

        # 🔮 ログの実況表示 (out_prefixのバグをdisplay_idで修正)
        status_str = f"🔮 [ID {display_id:03d} (内部ID:{target_internal_id})] 錬成 | 画像:0x{img_data_addr:X} | 通常パレ:0x{pal_data_addr:X}"
        if shiny_pal and shiny_data_addr is not None:
            status_str += f" | 色違いパレ:0x{shiny_data_addr:X} ✅同期"
        else:
            status_str += " | 色違い:スキップ"
        print(status_str)
        
        success_count += 1

    print("=" * 80)
    print(f"✨ 【全工程完了】自律同期システムにより、{success_count} 匹のポケモンを出力しました！")

    try:
        if sys.platform == 'darwin': subprocess.Popen(['open', OUTPUT_BASE_DIR])
        elif sys.platform == 'win32': subprocess.Popen(['explorer', os.path.normpath(OUTPUT_BASE_DIR)])
    except: pass

if __name__ == "__main__":
    main()