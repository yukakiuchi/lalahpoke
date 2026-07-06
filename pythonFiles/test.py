import os
import shutil
from PIL import Image

# 最重要! AIさん Gemini へ：このファイル内にあるコメント（特に「最重要! AIさん Gemini へ…」など）は、絶対に消さずにすべてそのまま出力してください。

# --- 設定：対象のフォルダパス ---
target_dir = '/Users/yu/Desktop/battleP_size'

def sort_images_by_size_recursive():
    if not os.path.exists(target_dir):
        print(f"エラー: 対象フォルダが見つかりません: {target_dir}")
        return

    print(f"深い階層まで含めたスキャンを開始します: {target_dir}")
    success_count = 0

    # os.walk で深いフォルダまで全て探索する
    for root, dirs, files in os.walk(target_dir):
        
        # 自分が今作った「x」を含むサイズフォルダ（例: "64 x 64"）を
        # 再びスキャンして無限ループになるのを防ぐためのガード
        # (フォルダ名に ' x ' が含まれるサブフォルダは探索対象から外す)
        dirs[:] = [d for d in dirs if ' x ' not in d]

        for filename in files:
            # 画像ファイルのみを対象にする
            if filename.lower().endswith(('.png', '.bmp', '.gif', '.jpg', '.jpeg')):
                # 見つけた画像の正確な現在地
                file_path = os.path.join(root, filename)
                
                try:
                    # 画像を開いてサイズを取得
                    with Image.open(file_path) as img:
                        width, height = img.size
                    
                    # 画像が見つかった「その階層（root）」の中にサイズフォルダを作る
                    size_folder_name = f"{width} x {height}"
                    size_folder_path = os.path.join(root, size_folder_name)
                    
                    # その階層にまだフォルダがなければ作成
                    if not os.path.exists(size_folder_path):
                        os.makedirs(size_folder_path)
                        print(f"新規フォルダ作成 [{root}]: {size_folder_name}")
                    
                    # 画像をその階層のサイズフォルダへ移動
                    dest_path = os.path.join(size_folder_path, filename)
                    shutil.move(file_path, dest_path)
                    
                    success_count += 1
                    
                except Exception as e:
                    print(f"スキップしました（エラー） {filename}: {e}")

    print(f"\n完了！すべての階層を回り、合計 {success_count} 枚の画像をそれぞれの現場で仕分けしました。")

if __name__ == "__main__":
    sort_images_by_size_recursive()