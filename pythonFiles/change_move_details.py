import os
import re

TARGET_FILE_PATH = "/Users/yu/Desktop/expand/src/data/moves_info.h"

def flatten_line(line, param_name):
    """
    .power または .accuracy の行に三項演算子 (? ... :) が含まれている場合、
    小さい方の数値を取り出して固定値表記に置換する。
    """
    pattern = re.compile(r'(\s*\.' + param_name + r'\s*=\s*).*?\?\s*(\d+)\s*:\s*(\d+)\s*(,.*)')
    match = pattern.search(line)
    if match:
        prefix = match.group(1)
        val1 = int(match.group(2))
        val2 = int(match.group(3))
        suffix = match.group(4)
        min_val = min(val1, val2)
        return f"{prefix}{min_val}{suffix}"
    return line

def process_move_block(block_text):
    # 特殊技（DAMAGE_CATEGORY_SPECIAL）以外は対象外
    if not re.search(r'\.category\s*=\s*DAMAGE_CATEGORY_SPECIAL\b', block_text):
        return block_text

    lines = block_text.splitlines(keepends=True)
    new_lines = []

    for line in lines:
        # --- .power 行の独立処理 ---
        if '.power' in line:
            # 1. 演算子の平坦化（三項演算子があれば小さい方に上書き）
            line = flatten_line(line, 'power')
            # 2. 数値を取得して独立判定 (威力40以上なら -10)
            m = re.search(r'(\s*\.power\s*=\s*)(\d+)(,.*)', line)
            if m:
                prefix, power_val, suffix = m.group(1), int(m.group(2)), m.group(3)
                if power_val >= 40:
                    new_power = power_val - 10
                    line = f"{prefix}{new_power}{suffix}"

        # --- .accuracy 行の独立処理 ---
        elif '.accuracy' in line:
            # 1. 演算子の平坦化（三項演算子があれば小さい方に上書き）
            line = flatten_line(line, 'accuracy')
            # 2. 数値を取得して独立判定 (命中51以上なら -10)
            m = re.search(r'(\s*\.accuracy\s*=\s*)(\d+)(,.*)', line)
            if m:
                prefix, acc_val, suffix = m.group(1), int(m.group(2)), m.group(3)
                if acc_val > 50:
                    new_acc = acc_val - 10
                    line = f"{prefix}{new_acc}{suffix}"

        new_lines.append(line)

    return "".join(new_lines)

def main():
    if not os.path.exists(TARGET_FILE_PATH):
        print(f"エラー: 指定されたファイルが存在しません: {TARGET_FILE_PATH}")
        return

    with open(TARGET_FILE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # [MOVE_XXXX] = { ... }, の技定義ブロックを抽出
    pattern = re.compile(r'(\[\s*MOVE_[A-Z0-9_]+\s*\]\s*=\s*\n?\s*\{.*?\n    \},)', re.DOTALL)

    modified_count = 0

    def replace_callback(match):
        nonlocal modified_count
        original_block = match.group(1)
        processed_block = process_move_block(original_block)
        if processed_block != original_block:
            modified_count += 1
        return processed_block

    new_content = pattern.sub(replace_callback, content)

    # 上書き保存
    with open(TARGET_FILE_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"処理完了: {modified_count} 個の特殊技ブロックを調整・更新しました。")

if __name__ == "__main__":
    main()