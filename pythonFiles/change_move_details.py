import os
import re

TARGET_FILE_PATH = "/Users/yu/Desktop/expand/src/data/moves_info.h"

def flatten_line(line, param_name):
    """
    .power または .accuracy の行に三項演算子 (? ... :) が含まれている場合、
    演算子部分だけを小さい方の数値文字列に置換する。（改行・カンマ等はそのまま残す）
    """
    match = re.search(r'\.' + param_name + r'\s*=\s*(.*?\?\s*(\d+)\s*:\s*(\d+))', line)
    if match:
        full_expr = match.group(1) # "B_UPDATED_MOVE_DATA >= GEN_3 ? 100 : 75"
        val1 = int(match.group(2))
        val2 = int(match.group(3))
        min_val = min(val1, val2)
        # 式の部分だけを数値文字列に置換
        line = line.replace(full_expr, str(min_val))
    return line

def modify_line_val(line, param_name):
    """
    .power = 80 や .accuracy = 75 の数値部分を判定し、
    条件を満たせば数値部分のみを -10 して置換する。（改行・カンマ等はそのまま残す）
    """
    match = re.search(r'(\.' + param_name + r'\s*=\s*)(\d+)', line)
    if match:
        prefix = match.group(1)
        val = int(match.group(2))

        should_modify = False
        if param_name == 'power' and val >= 40:
            should_modify = True
        elif param_name == 'accuracy' and val > 50:
            should_modify = True

        if should_modify:
            new_val = val - 10
            # 該当する ".power = 80" の部分だけを置き換え、前後の文字列（改行等）は一切触らない
            line = line[:match.start()] + f"{prefix}{new_val}" + line[match.end():]

    return line

def process_move_block(block_text):
    # 特殊技（DAMAGE_CATEGORY_SPECIAL）以外は何も変更しない
    if not re.search(r'\.category\s*=\s*DAMAGE_CATEGORY_SPECIAL\b', block_text):
        return block_text

    lines = block_text.splitlines(keepends=True) # 改行コードを保持して行分割
    new_lines = []

    for line in lines:
        if '.power' in line:
            line = flatten_line(line, 'power')
            line = modify_line_val(line, 'power')
        elif '.accuracy' in line:
            line = flatten_line(line, 'accuracy')
            line = modify_line_val(line, 'accuracy')

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

    print(f"処理完了: {modified_count} 個の特殊技ブロックを更新しました。")

if __name__ == "__main__":
    main()