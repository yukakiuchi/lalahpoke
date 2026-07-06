import os
import sys
import subprocess
from PIL import Image
from collections import defaultdict

# ------------------ 設定 ------------------
INPUT_DIR = "/Users/yu/Desktop/please_cut"
OUTPUT_DIR = "/Users/yu/Desktop/DreamDexCombined"
# ------------------------------------------

def open_folder_and_exit(target_dir):
    """ 処理完了後にフォルダをUIで開き、スクリプトを終了する """
    print(f"\n📂 出力フォルダを自動で開きます: {target_dir}")
    if sys.platform == "darwin":      # Mac
        subprocess.run(["open", target_dir])
    elif sys.platform == "win32":    # Windows
        os.startfile(target_dir)
    else:                            # Linux等
        subprocess.run(["xdg-open", target_dir])
    sys.exit(0)

def get_clean_rgba_and_bg(img_path):
    """ 画像をRGBAに変換し、(0,0)のピクセルから背景色を取得 """
    img_rgba = Image.open(img_path).convert("RGBA")
    px_00 = img_rgba.getpixel((0, 0))
    bg_rgb = px_00[:3] if px_00[3] > 0 else (0, 120, 120)
    return img_rgba, bg_rgb

def get_actual_used_colors(img_rgba, bg_rgb):
    """ 画像内で「実際にピクセルとして描かれている」透明以外のユニークな色数を数える """
    pixels = img_rgba.getdata()
    used_colors = set()
    for p in pixels:
        rgb = p[:3]
        alpha = p[3]
        if alpha == 0 or rgb == bg_rgb:
            continue
        used_colors.add(rgb)
    return len(used_colors)

def build_synced_indices_and_palettes(front_n_rgba, front_s_rgba, back_n_rgba, back_s_rgba, anim_n_rgba, bg_n, bg_s):
    """ 5枚（anim含む）の画像を同時にスキャンし、パレットを完全同期。検出された総ペア数と減色フラグを返す """
    pal_n = [bg_n]
    pal_s = [bg_s]
    color_to_idx = {}
    reduction_triggered = False

    def process_pair(img_n, img_s, bg_normal, bg_shiny, is_anim_mode=False):
        nonlocal reduction_triggered
        data_n = img_n.getdata()
        local_indices = []

        # アニメーション用(_5)の場合は、色違いの相方がいない（単色判定）
        if is_anim_mode:
            for p_n in data_n:
                rgb_n = p_n[:3]
                alpha_n = p_n[3]

                if alpha_n == 0 or rgb_n == bg_normal:
                    local_indices.append(0)
                    continue

                # _5はノーマルパレットに属するので、過去のどのペアかのrgb_nと一致するか、新規追加
                # 対になる色違いは、仮に同じ色(rgb_n)として登録を試みる
                combo = (rgb_n, rgb_n)
                
                # すでに別のペアとして登録済みの色か探す
                found = False
                for existing_combo, idx in color_to_idx.items():
                    if existing_combo[0] == rgb_n:
                        local_indices.append(idx)
                        found = True
                        break
                
                if not found:
                    if len(pal_n) < 16:
                        idx = len(pal_n)
                        color_to_idx[combo] = idx
                        pal_n.append(rgb_n)
                        pal_s.append(rgb_n) # 色違い側にも仮置き
                        local_indices.append(idx)
                    else:
                        local_indices.append(0)
                        reduction_triggered = True
            return local_indices

        # 通常の _1〜_4 用のペアスキャン
        data_s = img_s.getdata()
        for p_n, p_s in zip(data_n, data_s):
            rgb_n, rgb_s = p_n[:3], p_s[:3]
            alpha_n, alpha_s = p_n[3], p_s[3]

            if alpha_n == 0 or rgb_n == bg_normal or alpha_s == 0 or rgb_s == bg_shiny:
                local_indices.append(0)
                continue

            combo = (rgb_n, rgb_s)
            if combo not in color_to_idx:
                if len(pal_n) < 16:
                    idx = len(pal_n)
                    color_to_idx[combo] = idx
                    pal_n.append(rgb_n)
                    pal_s.append(rgb_s)
                    local_indices.append(idx)
                else:
                    local_indices.append(0)
                    reduction_triggered = True
            else:
                local_indices.append(color_to_idx[combo])
        return local_indices

    indices_fn = process_pair(front_n_rgba, front_s_rgba, bg_n, bg_s)
    indices_bs = process_pair(back_n_rgba, back_s_rgba, bg_n, bg_s)
    
    indices_an = []
    if anim_n_rgba is not None:
        indices_an = process_pair(anim_n_rgba, None, bg_n, bg_s, is_anim_mode=True)

    total_detected_combos = len(color_to_idx) + 1

    while len(pal_n) < 16: pal_n.append((0, 0, 0))
    while len(pal_s) < 16: pal_s.append((0, 0, 0))

    return indices_fn, indices_bs, indices_an, pal_n, pal_s, reduction_triggered, total_detected_combos

def make_p_image(indices, palette_rgb_list, size):
    """ インデックスデータとRGBリストからPモード画像を生成 """
    img = Image.new("P", size)
    flat_pal = []
    for rgb in palette_rgb_list: flat_pal.extend(rgb)
    img.putpalette(flat_pal + [0] * (768 - len(flat_pal)))
    img.putdata(indices)
    return img

def combine_images():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    groups = defaultdict(list)
    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".png")]

    if not files:
        print(f"取得元フォルダー: {INPUT_DIR} に画像が見つかりません。")
        return

    print(f"📂 取得元フォルダー: {INPUT_DIR}")
    print(f"📂 出力先フォルダー: {OUTPUT_DIR}")
    print("-" * 80)

    for f in files:
        if "_" in f:
            prefix = f.split("_")[0]
            groups[prefix].append(f)

    for prefix, member_files in groups.items():
        member_files.sort()

        slots = {}
        for f in member_files:
            sub_id_str = f.split("_")[1].split(".")[0]
            if sub_id_str.isdigit():
                slots[int(sub_id_str)] = os.path.join(INPUT_DIR, f)

        if 1 not in slots:
            print(f"❌ 処理不可: グループ {prefix} (_1画像不足)")
            continue

        is_two_sheet_mode = False
        has_anim_sheet = (5 in slots)
        
        if 2 in slots and 3 not in slots and 4 not in slots and 5 not in slots:
            is_two_sheet_mode = True
            
            f_n_rgba, bg_n = get_clean_rgba_and_bg(slots[1])
            f_s_rgba = f_n_rgba.copy()
            bg_s = bg_n
            
            b_n_rgba, _ = get_clean_rgba_and_bg(slots[2])
            b_s_rgba = b_n_rgba.copy()
            anim_n_rgba = None
            
            c1 = get_actual_used_colors(f_n_rgba, bg_n) + 1
            c2 = get_actual_used_colors(b_n_rgba, bg_n) + 1
            colors_inline_str = f"_1(正面): {c1}色 | _2(背面): {c2}色"
            
        else:
            if 2 not in slots:
                print(f"❌ 処理不可: グループ {prefix} (_2画像不足)")
                continue
                
            f_n_rgba, bg_n = get_clean_rgba_and_bg(slots[1])
            f_s_rgba, bg_s = get_clean_rgba_and_bg(slots[2])

            if 3 in slots:   b_n_rgba, _ = get_clean_rgba_and_bg(slots[3])
            else:            b_n_rgba = f_n_rgba.copy()

            if 4 in slots:   b_s_rgba, _ = get_clean_rgba_and_bg(slots[4])
            else:            b_s_rgba = f_s_rgba.copy()
            
            if 5 in slots:   anim_n_rgba, _ = get_clean_rgba_and_bg(slots[5])
            else:            anim_n_rgba = None

            color_info_list = []
            for s_id in sorted(slots.keys()):
                if s_id == 1: img_obj, bg_obj = f_n_rgba, bg_n
                elif s_id == 2: img_obj, bg_obj = f_s_rgba, bg_s
                elif s_id == 3: img_obj, bg_obj = b_n_rgba, bg_n
                elif s_id == 4: img_obj, bg_obj = b_s_rgba, bg_s
                elif s_id == 5: img_obj, bg_obj = anim_n_rgba, bg_n
                
                real_colors = get_actual_used_colors(img_obj, bg_obj)
                color_info_list.append(f"_{s_id}: {real_colors + 1}色")
            colors_inline_str = " | ".join(color_info_list)

        # パレット同期処理の実行
        indices_fn, indices_bs, indices_an, pal_n_out, pal_s_out, reduction, total_combos = build_synced_indices_and_palettes(
            f_n_rgba, f_s_rgba, b_n_rgba, b_s_rgba, anim_n_rgba, bg_n, bg_s
        )

        actions = ["背景色0番入れ替え"]
        if is_two_sheet_mode:
            actions.append("正面/背面パレット単純統合")
        else:
            if has_anim_sheet:
                actions.append("通常/色違い/正面アニメ共通同期")
            else:
                actions.append("通常/色違いパレット同期")
            
        if reduction:
            actions.append(f"16色制限超過分の自動減色（統合: {total_combos}色）")

        action_line = " ＋ ".join(actions)

        # 個別Pモード画像生成
        f_n_final = make_p_image(indices_fn, pal_n_out, (64, 64))
        b_s_final = make_p_image(indices_bs, pal_s_out, (64, 64))

        img_fn = f_n_final
        img_fs = make_p_image(indices_fn, pal_s_out, (64, 64))
        img_bn = make_p_image(indices_bs, pal_n_out, (64, 64))
        img_bs = b_s_final
        
        final_images = [img_fn, img_fs, img_bn, img_bs]
        
        # _5 がある場合は5枚目の画像リストに加える
        if has_anim_sheet:
            img_an = make_p_image(indices_an, pal_n_out, (64, 64))
            final_images.append(img_an)

        # 32色パレット結合
        flat_pal_n = []
        for rgb in pal_n_out: flat_pal_n.extend(rgb)
        flat_pal_s = []
        for rgb in pal_s_out: flat_pal_s.extend(rgb)
        combined_palette_data = flat_pal_n + flat_pal_s

        # 横結合のサイズ決定
        total_width = sum(img.width for img in final_images)
        max_height = max(img.height for img in final_images)

        combined_img = Image.new("P", (total_width, max_height))
        full_palette = combined_palette_data + ([0] * (768 - len(combined_palette_data)))
        combined_img.putpalette(full_palette)

        current_x = 0
        for i, img in enumerate(final_images):
            # i が 1(正面色違い) または 3(背面色違い) のときだけパレット番号を+16シフトする
            if i in (1, 3):
                shifted_img = img.point(lambda p: p + 16 if 0 < p <= 15 else 0)
                combined_img.paste(shifted_img, (current_x, 0))
            else:
                # 0(正面通常), 2(背面通常), 4(正面アニメ_5) はそのまま結合
                combined_img.paste(img, (current_x, 0))
            current_x += img.width

        combined_img.palette.palette = bytes(combined_palette_data)
        save_name = f"{prefix}_combined.png"
        combined_img.save(os.path.join(OUTPUT_DIR, save_name), transparency=0)

        print(f"=========================[{prefix}]==========================")
        print(f"[使用色数] {colors_inline_str}")
        print(f"[処理内容] {action_line}\n")

    print("-" * 80)
    print("✨ すべての同期・結合処理が完了しました。")
    open_folder_and_exit(OUTPUT_DIR)

if __name__ == "__main__":
    combine_images()