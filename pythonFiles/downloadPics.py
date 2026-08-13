import os
import sys
import csv
import time
import shutil
import subprocess
import requests
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

# ==========================================
# 1. 設定部分
# ==========================================
DOWNLOAD_SPRITES = False
DOWNLOAD_ICON    = True

CSV_FILE_PATH = "/Users/yu/Desktop/sprites.csv"
OUTPUT_DIR = "/Users/yu/Desktop/DREAM_newDEXX"
SOURCE_DIR = os.path.join(OUTPUT_DIR, "raw")
TILE_SIZE = 64
MAX_WORKERS = 50

SIMPLE_CUT = [] 
CUSTOM_CUT = [] 

# ==========================================
# 2. 共通タスク作成・ダウンロード処理
# ==========================================
def load_tasks(url_column):
    """
    CSVファイルを読み込み、指定されたURLカラムからダウンロードタスクを作成します。
    """
    tasks = []
    if not os.path.exists(CSV_FILE_PATH):
        print(f"❌ CSVファイルが見つかりません: {CSV_FILE_PATH}")
        return tasks

    with open(CSV_FILE_PATH, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                poke_id_str = row.get("id", "").strip()
                if not poke_id_str:
                    continue
                poke_id = int(poke_id_str)
                url = row.get(url_column, "").strip()
                if url:
                    tasks.append({
                        "id": poke_id_str,
                        "original_name_code": row.get("original_name_code", "").strip() or "N/A",
                        "url": url,
                        "filename": f"{poke_id:03d}.png"
                    })
            except ValueError:
                continue
    return tasks

def download_single_image(task, target_dir):
    """
    単一ファイルのダウンロードを行い、開始ログをリアルタイムに出力します。
    """
    poke_id = task["id"]
    code = task["original_name_code"]
    
    # 表示用IDを3桁に整形
    try:
        formatted_id = f"{int(poke_id):03d}"
    except ValueError:
        formatted_id = poke_id

    # ダウンロード開始をリアルタイムで報告
    print(f"📥 [ダウンロード開始] ID: {formatted_id} ({code})")

    url = task["url"]
    filename = task["filename"]
    filepath = os.path.join(target_dir, filename)
    
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        with open(filepath, 'wb') as f:
            f.write(resp.content)
        return True, None
    except Exception as e:
        return False, str(e)

def execute_download_loop(tasks, target_dir):
    """
    ダウンロード処理を実行し、失敗したタスクを記憶して最大4回までリトライします。
    """
    current_tasks = list(tasks)
    
    for attempt in range(1, 5):
        print(f"\n🔄 ダウンロード試行 {attempt}/4 回目 (対象: {len(current_tasks)} 件)")
        failed_tasks = []
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # タスクをスレッドプールに投入
            futures = {executor.submit(download_single_image, task, target_dir): task for task in current_tasks}
            
            for future in futures:
                task = futures[future]
                try:
                    success, err_msg = future.result()
                except Exception as e:
                    success, err_msg = False, str(e)
                
                if not success:
                    print(f"⚠️ [失敗] ID: {task['id']}, Code: {task['original_name_code']} - {err_msg}")
                    failed_tasks.append(task)
        
        if not failed_tasks:
            print("✨ すべてのダウンロードが完了しました。")
            return True
            
        print(f"⚠️ 試行 {attempt} 終了。失敗した件数: {len(failed_tasks)} 件")
        current_tasks = failed_tasks
        
        if attempt < 4:
            print("1秒後に失敗したファイルの再ダウンロードを開始します...")
            time.sleep(1)
            
    # 4回リトライしても失敗したものが残った場合
    print(f"\n❌ 一部のファイルがダウンロードできませんでした (未完了: {len(current_tasks)} 件)。")
    for task in current_tasks:
        print(f" - 未完了 ID: {task['id']}, Code: {task['original_name_code']}")
    return False

# ==========================================
# 3. カット・パレット同期処理
# ==========================================
def get_palette_count(img):
    if img.mode == 'P':
        if hasattr(img, 'palette') and img.palette and img.palette.palette:
            return len(img.palette.palette) // 3
        try: return max(img.getdata()) + 1
        except: return 256
    else:
        colors = img.getcolors(maxcolors=10000)
        return len(colors) if colors else 256

def open_folder_and_exit(target_dir):
    print(f"\n📂 出力フォルダを開きます: {target_dir}")
    if sys.platform == "darwin": subprocess.run(["open", target_dir])
    elif sys.platform == "win32": os.startfile(target_dir)
    sys.exit(0)

def process_images():
    if not os.path.exists(SOURCE_DIR):
        print("❌ 処理対象の raw フォルダが見つかりません。")
        return

    files = sorted([f for f in os.listdir(SOURCE_DIR) if f.lower().endswith(".png")])
    print(f"\n✂️ カット処理を開始します (対象: {len(files)} 件)")
    
    for filename in files:
        file_path = os.path.join(SOURCE_DIR, filename)
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                base_name = os.path.splitext(filename.replace("_combined", ""))[0]
                palette_count = get_palette_count(img)
                
                # モード判定
                if filename in SIMPLE_CUT: cut_mode = "SIMPLE"
                elif filename in CUSTOM_CUT: cut_mode = "CUSTOM"
                elif 31 <= palette_count <= 33: cut_mode = "CUSTOM"
                else: cut_mode = "SIMPLE"

                if cut_mode == "CUSTOM":
                    img_p = img.convert('P')
                    full_pal = img_p.getpalette()
                    pal_norm_data = full_pal[0:48]
                    pal_shiny_data = full_pal[48:96]
                    cols = width // TILE_SIZE
                    for c in range(cols):
                        part = img_p.crop((c * TILE_SIZE, 0, (c + 1) * TILE_SIZE, TILE_SIZE))
                        if c % 2 == 1:
                            part = part.point(lambda p: p - 16 if p >= 16 else 0)
                            current_pal_data = pal_shiny_data
                        else:
                            current_pal_data = pal_norm_data
                        part.putpalette(list(current_pal_data) + ([0] * (768 - 48)))
                        part.save(os.path.join(OUTPUT_DIR, f"{base_name}_{c + 1}.png"), transparency=0)
                else:
                    img_rgba = img.convert("RGBA")
                    width = img_rgba.width
                    num_tiles = width // 64
                    
                    tiles = [img_rgba.crop((i * 64, 0, (i + 1) * 64, 64)) for i in range(num_tiles)]
                    
                    bg_n, bg_s = (0, 120, 120), (0, 120, 120)
                    pal_n, pal_s = [bg_n], [bg_s]
                    
                    def build_indices_flexible(tiles):
                        indices_list = [[] for _ in range(num_tiles)]
                        for i in range(num_tiles):
                            for p in list(tiles[i].getdata()):
                                if p[3] == 0 or p[:3] == bg_n:
                                    indices_list[i].append(0)
                                    continue
                                
                                if i % 2 == 0:
                                    if p[:3] not in pal_n:
                                        if len(pal_n) < 16: pal_n.append(p[:3])
                                        else: indices_list[i].append(0); continue
                                    indices_list[i].append(pal_n.index(p[:3]))
                                else:
                                    if p[:3] not in pal_s:
                                        if len(pal_s) < 16: pal_s.append(p[:3])
                                        else: indices_list[i].append(0); continue
                                    indices_list[i].append(pal_s.index(p[:3]))
                        return indices_list

                    all_indices = build_indices_flexible(tiles)
                    
                    while len(pal_n) < 16: pal_n.append((0, 0, 0))
                    while len(pal_s) < 16: pal_s.append((0, 0, 0))
                    
                    for i in range(num_tiles):
                        p = Image.new("P", (64, 64))
                        current_pal = pal_n if i % 2 == 0 else pal_s
                        p.putpalette([c for rgb in current_pal for c in rgb])
                        p.putdata(all_indices[i])
                        p.save(os.path.join(OUTPUT_DIR, f"{base_name}_{i + 1}.png"))
        
        except Exception as e:
            print(f"❌ エラー発生: {filename} - {e}")

    print("-" * 40 + "\n🎉 すべての画像処理が完了しました。")
    print("🧹 rawフォルダを削除します...")
    if os.path.exists(SOURCE_DIR):
        shutil.rmtree(SOURCE_DIR)
    open_folder_and_exit(OUTPUT_DIR)

# ==========================================
# 4. メイン実行ブロック
# ==========================================
def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    if DOWNLOAD_SPRITES:
        print("====== SPRITES ダウンロード＆カット処理を開始します ======")
        if os.path.exists(SOURCE_DIR):
            shutil.rmtree(SOURCE_DIR)
        os.makedirs(SOURCE_DIR)
        
        tasks = load_tasks("sprite_url")
        if not tasks:
            print("❌ スプライトのダウンロード対象データが見つかりませんでした。")
            return
            
        print(f"🚀 全 {len(tasks)} 件のダウンロードを開始します。")
        execute_download_loop(tasks, SOURCE_DIR)
        
        # 部分的であってもダウンロードされた画像があれば、カット処理に進みます
        process_images()

    elif DOWNLOAD_ICON:
        print("====== ICON ダウンロード処理を開始します ======")
        tasks = load_tasks("icon_url")
        if not tasks:
            print("❌ アイコンのダウンロード対象データが見つかりませんでした。")
            return
            
        print(f"🚀 全 {len(tasks)} 件のダウンロードを開始します。")
        execute_download_loop(tasks, OUTPUT_DIR)
        
        # 完了後にフォルダを開いて終了します
        open_folder_and_exit(OUTPUT_DIR)
        
    else:
        print("⚠️ DOWNLOAD_SPRITES または DOWNLOAD_ICON のいずれかを True に設定してください。")

if __name__ == "__main__":
    main()