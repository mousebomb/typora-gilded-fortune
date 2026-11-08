#!/usr/bin/env bash
# 把主题装进本机 Typora 主题目录。
#
# 用法：
#   bash install.sh          # 安装/更新
#   bash install.sh --dry-run  # 只打印会做什么
#
# 旧文件用 macOS 自带的 trash 移入废纸篓，可随时恢复；
# 没有 trash 命令时才退回 mv 备份到 .bak 目录。

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
THEMES="$HOME/Library/Application Support/abnerworks.Typora/themes"
FILES=("gilded-fortune.css" "gilded-fortune-light.css" "gilded-fortune")
DRY_RUN=0

[ "${1:-}" = "--dry-run" ] && DRY_RUN=1

if [ ! -d "$THEMES" ]; then
  echo "找不到 Typora 主题目录：$THEMES" >&2
  echo "请先打开 Typora → 偏好设置 → 外观 → 打开主题文件夹，再运行本脚本。" >&2
  exit 1
fi

move_aside() {
  local target="$1"
  [ -e "$target" ] || return 0
  if command -v trash >/dev/null 2>&1; then
    trash "$target"
  else
    mkdir -p "$THEMES/.bak"
    mv "$target" "$THEMES/.bak/$(basename "$target").$(date +%s)"
  fi
}

for item in "${FILES[@]}"; do
  src="$ROOT/$item"
  dst="$THEMES/$item"
  [ -e "$src" ] || { echo "源文件缺失：$src" >&2; exit 1; }
  if [ "$DRY_RUN" = "1" ]; then
    echo "[dry-run] 移走旧文件（若有）：$dst"
    echo "[dry-run] 复制：$src → $dst"
    continue
  fi
  move_aside "$dst"
  cp -R "$src" "$dst"
  echo "已安装：$item"
done

if [ "$DRY_RUN" = "1" ]; then
  echo "[dry-run] 结束，未改动任何文件。"
  exit 0
fi

echo
echo "完成。重启 Typora，在「主题」菜单里选择 Gilded Fortune 或 Gilded Fortune Light。"
echo "（主题文件夹：$THEMES）"
