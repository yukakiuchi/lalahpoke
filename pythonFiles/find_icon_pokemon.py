import os
from PIL import Image

# Yuさんが見つけた「完璧な開始地点」
START_ADDR = 0xCF1FA0 
rom_path = "/Users/yu/Downloads/redux.gba"
output_dir = "/Users/yu/Downloads/final_verification"
os.makedirs(output_dir, exist_ok=True)

def raw_4bpp_to_pixels(data):
    pixels = [0] * (32 * 32)
    for tile_idx in range(16):
        tx, ty = (tile_idx % 4) * 8, (tile_idx // 4) * 8
        for i in range(32):
            b = data[tile_idx * 32 + i]
            p1, p2 = (b & 0x0F) * 17, (b >> 4) * 17
            lx, ly = (i * 2) % 8, (i * 2) // 8
            pixels[(ty + ly) * 32 + (tx + lx)] = p1
            pixels[(ty + ly) * 32 + (tx + lx + 1)] = p2
    return pixels

with open(rom_path, "rb") as f:
    rom_data = f.read()

print(f"📡 {hex(START_ADDR)} から1024バイト刻みで500匹スキャンします...")

for i in range(500):
    current = START_ADDR + (i * 1024)
    if current + 1024 > len(rom_data): break
    
    # 2フレーム結合
    combined = Image.new('L', (64, 32))
    for f_idx in range(2):
        chunk = rom_data[current + (f_idx * 512) : current + (f_idx * 512) + 512]
        img = Image.new('L', (32, 32))
        img.putdata(raw_4bpp_to_pixels(chunk))
        combined.paste(img, (f_idx * 32, 0))
    
    # 保存名にアドレスを入れる
    combined.save(f"{output_dir}/poke_{i:03d}_addr_{hex(current)}.png")
    
    # もし 0xCFFF28 に近づいたら教えてくれるフラグ
    if abs(current - 0xCFFF28) < 1024:
        print(f"💡 注目！ 0xCFFF28 付近の個体（No.{i}）を書き出しました: {hex(current)}")

print(f"✅ 完了！ 0xCFFF28 が『どのポケモンの、どのフレームか』がこれで判明します。")