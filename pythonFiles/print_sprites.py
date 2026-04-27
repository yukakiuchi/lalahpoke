import os
from PIL import Image

def lz77_decompress_gba(data, offset):
    """GBA BIOS形式のLZ77を解凍する"""
    ptr = offset
    
    # LZ77ヘッダーの確認 (0x10)
    if data[ptr] != 0x10:
        print(f"エラー: アドレス 0x{offset:X} はLZ77ヘッダー (10) から始まっていません。")
        return None
    
    # 解凍後のサイズを取得 (24ビット)
    decompressed_size = data[ptr+1] | (data[ptr+2] << 8) | (data[ptr+3] << 16)
    print(f"解凍後のサイズ: {decompressed_size} バイト")
    
    # 解凍処理
    ptr += 4
    out = bytearray()
    
    while len(out) < decompressed_size:
        if ptr >= len(data): break # バッファオーバーフロー防止
        flags = data[ptr]
        ptr += 1
        
        for i in range(8):
            if len(out) >= decompressed_size: break
            if flags & (0x80 >> i):
                # 圧縮ブロック（一致）
                if ptr + 1 >= len(data): break
                info = (data[ptr] << 8) | data[ptr+1]
                ptr += 2
                length = (info >> 12) + 3 # 3〜18バイトの一致
                disp = (info & 0x0FFF) + 1 # 1〜4096バイト前の相対位置
                
                back = len(out) - disp
                if back < 0:
                    # 希にあるエラーケースの回避
                    print(f"Warning: 無効なdisp値 {disp} がアドレス 0x{ptr-3:X} 付近で発生しました。")
                    for _ in range(length):
                        out.append(0)
                else:
                    for _ in range(length):
                        out.append(out[back])
                        back += 1
            else:
                # 非圧縮ブロック（生データ）
                if ptr >= len(data): break
                out.append(data[ptr])
                ptr += 1
    
    return out

def save_gba_4bpp_as_png(raw_data, width, height, output_path):
    """4bppタイルデータをPNG画像として保存"""
    # インデックス（パレット）モードで画像を作成
    img = Image.new('P', (width, height))
    
    # グレースケールのパレットを設定 (0=黒, 15=白 に徐々に変化)
    palette = []
    for i in range(16):
        # 16色を均等にグレースケールに割り当てる (i*17 で 0〜255)
        palette.extend([i*17, i*17, i*17])
    # パレットを適用
    img.putpalette(palette + [0]*(768-len(palette)))

    # タイルデータをピクセルに書き戻し
    ptr = 0
    # 64x64ピクセルを8x8タイルの集合として処理
    for tile_y in range(0, height, 8):
        for tile_x in range(0, width, 8):
            # タイル内の各行
            for y in range(tile_y, tile_y + 8):
                # 2ピクセル(4bit+4bit)で1バイト
                for x in range(tile_x, tile_x + 8, 2):
                    if ptr >= len(raw_data): break
                    byte = raw_data[ptr]
                    ptr += 1
                    
                    # リトルエンディアン形式: 
                    # 最初のピクセル(x)は下位4bit、
                    # 2番目のピクセル(x+1)は上位4bit
                    p1 = byte & 0x0F
                    p2 = (byte >> 4) & 0x0F
                    
                    img.putpixel((x, y), p1)
                    img.putpixel((x+1, y), p2)
    
    # 保存
    img.save(output_path)
    print(f"解凍・PNG化が完了しました: {output_path}")

# 設定
ROM_PATH = '/Users/yu/Downloads/Z (v1.2.0).gba'
TARGET_ADDR = 0x4AAAF4 # 特定したアドレス
OUTPUT_NAME = 'awkw_extracted.png'

if __name__ == "__main__":
    if not os.path.exists(ROM_PATH):
        print(f"Error: ROMファイルが見つかりません: {ROM_PATH}")
    else:
        print(f"ROM読み込み中: {ROM_PATH}")
        with open(ROM_PATH, 'rb') as f:
            rom_data = f.read()

        print(f"アドレス 0x{TARGET_ADDR:X} から解凍中...")
        decoded = lz77_decompress_gba(rom_data, TARGET_ADDR)
        
        if decoded:
            # $64 \times 64$ ピクセルの4bpp画像に変換して保存
            save_gba_4bpp_as_png(decoded, 64, 64, OUTPUT_NAME)
        else:
            print("解凍に失敗しました。")