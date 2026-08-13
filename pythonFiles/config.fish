# ==============================================================================
# 🐠 config.fish - 完全同期・最適化版（GBAビルド＆Macツール両対応）
# ==============================================================================

# --- 1. PATH / ccache 設定 ---
# Homebrew大元（/opt/homebrew/bin）を先頭に追加し、pkg-configや各種ツールが自動で動くように最適化
set -gx PATH /opt/homebrew/bin /opt/homebrew/opt/ccache/libexec /opt/devkitpro/devkitARM/bin $PATH

# --- 2. devkitPro 環境変数 ---
set -gx DEVKITPRO /opt/devkitpro
set -gx DEVKITARM $DEVKITPRO/devkitARM

# --- 3. プロンプト設定 ---
if status is-interactive
    function fish_prompt
        echo -n (basename (pwd)) ' ->: '
    end
end

# --- 5. save コマンド設定 ---
function save --description 'fish設定を一括同期し、干渉する古い残骸ファイルを自動消去する'
    set -l fish_dir "$HOME/.config/fish"

    if not test -d $fish_dir
        echo "❌ fishの設定ディレクトリが見つかりません: $fish_dir"
        return
    end

    set -l residue_file "$fish_dir/functions/op.fish"
    if test -f $residue_file
        rm $residue_file
        echo "🧹 干渉する古い関数ファイルを自動消去しました: functions/op.fish"
    end

    set -l target_files (find $fish_dir -type f -name "*.fish" 2>/dev/null)

    if test (count $target_files) -eq 0
        echo "⚠️ .fish ファイルが見つかりませんでした。"
        return
    end

    echo "📂 次の設定ファイルを同期します:"
    for file in $target_files
        source $file
        set -l display_path (string replace "$HOME" "~" $file)
        echo "  🔹 $display_path"
    end

    echo "--------------------------------------------------"
    echo "🔄 以上の全 .fish ファイル（計 "(count $target_files)" 個）を一括同期しました！"
end

# --- 6. エイリアス設定（すべて通常の python3 指定） ---
alias py-put-data=              '/Users/yu/Desktop/venv/bin/python3 /Users/yu/Desktop/expand/pythonFiles/put_data2gba.py'
alias py-cut-sprites=                                      'python3 /Users/yu/Desktop/expand/pythonFiles/cut-sprites.py'
alias py-cut-simple=                                       'python3 /Users/yu/Desktop/expand/pythonFiles/cut-simple.py'
alias py-check-png='python3 /Users/yu/Desktop/expand/pythonFiles/pngCheck.py'
alias py-combine='python3 /Users/yu/Desktop/expand/pythonFiles/combinePNG.py'
alias py-create-anim-icon='python3 /Users/yu/Desktop/expand/pythonFiles/createIcons.py'
alias py-find-icon='python3 /Users/yu/Desktop/expand/pythonFiles/find_icons.py'
alias py-generate-pal='python3 /Users/yu/Desktop/expand/pythonFiles/png2gbapal.py'
alias py-handy='python3 /Users/yu/Desktop/expand/pythonFiles/handy.py'
alias py-print-sprites='/Users/yu/Desktop/venv/bin/python3 /Users/yu/Desktop/expand/pythonFiles/print_sprite_general.py'
alias py-search-icons='python3 /Users/yu/Desktop/expand/pythonFiles/search_icons_general.py'
alias py-search-sprite='/Users/yu/Desktop/venv/bin/python3 /Users/yu/Desktop/expand/pythonFiles/search_sprites.py'
alias py-test='python3 /Users/yu/Desktop/expand/pythonFiles/test.py'
alias py-generate-redux-icon='python3 /Users/yu/Desktop/expand/pythonFiles/getPkIconsFromRedux.py'
alias py-putSprite2Game='python3 /Users/yu/Desktop/expand/pythonFiles/putSprite2Game.py'
alias config='open ~/.config/fish/config.fish'

# --- 7. Tabキー：自作フォルダ・スクリプト候補のトグル巡回機能（最適化版） ---
set -g my_tab_last_cmd ""
set -g my_tab_candidates
set -g my_tab_index 1
set -g my_tab_base_word ""

function __op_tab_complete
    set -l current_cmd (commandline)

    if not string match -q "op*" "$current_cmd"
        commandline -f complete
        return
    end

    if test "$current_cmd" = "$my_tab_last_cmd"; and test (count $my_tab_candidates) -gt 0
        set my_tab_index (math $my_tab_index + 1)
        if test $my_tab_index -gt (count $my_tab_candidates)
            set my_tab_index 1
        end
    else
        set -g my_tab_candidates
        set -g my_tab_base_word (string replace -r "^op\s*" "" "$current_cmd")
        
        set -l p_files (ls /Users/yu/Desktop/expand/pythonFiles 2>/dev/null)
        set -l d_folders
        for dir in /Users/yu/Desktop/*/
            set -l name (basename $dir)
            if not string match -q ".*" $name
                set d_folders $d_folders $name
            end
        end
        
        set -l all_list $p_files $d_folders
        for item in $all_list
            if string match -r "^"(string escape --style=regex $my_tab_base_word) $item >/dev/null
                set -g my_tab_candidates $my_tab_candidates $item
            end
        end
        set -g my_tab_index 1
    end

    if test (count $my_tab_candidates) -gt 0
        set -l selected $my_tab_candidates[$my_tab_index]
        commandline ""
        commandline -i "op $selected"
        commandline -C (string length (commandline))
        set -g my_tab_last_cmd (commandline)
    else
        commandline -f complete
    end
end

if status is-interactive
    bind \t __op_tab_complete
end

# --- 8. op コマンド本体 ---
function op --description '指定されたフォルダ、またはスクリプトをMacのUIで開く'
    set -l target $argv[1]
    set -l option $argv[2]

    if test -z "$target"
        commandline ""
        return
    end

    if test -d "/Users/yu/Desktop/$target"
        if test "$option" = "-icon"
            echo "🎬 [Option: -icon] Desktop/$target を112pxで開きます..."
            osascript -e "
                tell application \"Finder\"
                    activate
                    set targetFolder to (POSIX file \"/Users/yu/Desktop/$target\") as alias
                    open targetFolder
                    delay 0.3
                    set bounds of front Finder window to {0, 50, 1700, 550}
                    set current view of front Finder window to icon view
                    delay 0.1
                    set icon size of icon view options of front Finder window to 112
                end tell
            "
        else
            echo "📂 Desktop/$target を通常のFinderで開きます..."
            open "/Users/yu/Desktop/$target"
        end
        commandline ""
        return
    end

    if test -f "/Users/yu/Desktop/expand/pythonFiles/$target"
        echo "📄 $target をUIで開きます..."
        open "/Users/yu/Desktop/expand/pythonFiles/$target"
        commandline ""
        return
    end

    echo "❌ ファイルまたはフォルダが見つかりません: $target"
    commandline ""
end