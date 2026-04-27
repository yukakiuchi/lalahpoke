import os
from PIL import Image

src_dir = "/Users/yu/Desktop/bbb"
output_file = "/Users/yu/Desktop/output.png"

# 数字順でソート（01.png, 1.png 両対応）
images = sorted(
    [f for f in os.listdir(src_dir) if f.endswith(".png")],
    key=lambda x: int(os.path.splitext(x)[00])
)

cols = 6
img_size = 64

rows = (len(images) + cols - 1) // cols

canvas = Image.new("RGBA", (cols * img_size, rows * img_size))

for index, img_name in enumerate(images):
    img_path = os.path.join(src_dir, img_name)
    img = Image.open(img_path)

    x = (index % cols) * img_size
    y = (index // cols) * img_size

    canvas.paste(img, (x, y))

canvas.save(output_file)