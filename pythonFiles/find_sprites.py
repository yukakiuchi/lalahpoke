import binascii
import os

# --- 設定 ---
rom_path = '/Users/yu/Desktop/expand/pokeemerald.gba'
found_tile_addr = 0x3b0ec0  # 先ほど見つかった確定アドレス

def pinpoint_sprite():
    if not os.path.exists(rom_path):
        print(f"❌ ROMが見つかりません: {rom_path}")
        return

    with open(rom_path, "rb") as rom:
        # 画像サイズ(2048)の前後をカバーするために広めに読み込む
        start_read = max(0, found_tile_addr - 2048)
        rom.seek(start_read)
        data_block = rom.read(4096)

    print(f"🔎 アドレス {hex(found_tile_addr)} 周辺を解析中...")

    # 1. 32バイト(1タイル)ごとに区切って、どこからデータが始まっているか探す
    # ヒットした場所 (found_tile_addr) は data_block 内では offset = (found_tile_addr - start_read)
    target_offset = found_tile_addr - start_read
    real_start = found_tile_addr
    
    # 前方に遡って「00」が続いていないかチェック
    for i in range(target_offset, 0, -32):
        chunk = data_block[i-32 : i]
        if all(b == 0 for b in chunk):
            real_start = start_read + i
            break
    else:
        # 00が見つからない場合、とりあえず2048バイト前から切り出してみる
        real_start = max(0, found_tile_addr - 1024) 

    print(f"🎯 推定される画像の開始地点: {hex(real_start)}")

    # 2. 推定アドレスから 2048バイト (64x64) 分を抽出
    with open(rom_path, "rb") as rom:
        rom.seek(real_start)
        pikachu_data = rom.read(2048)
        
    with open("extracted_pikachu.bin", "wb") as f:
        f.write(pikachu_data)
    
    print(f"💾 抽出完了: extracted_pikachu.bin")
    print(f"このバイナリを以前のPNG化スクリプトで読み込んでみてください。")

if __name__ == "__main__":
    pinpoint_sprite()