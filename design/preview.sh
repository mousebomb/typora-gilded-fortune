#!/usr/bin/env bash
# 用 Typora 官方预览工具链（typora-theme-toolkit）把主题渲染成 PNG。
#
# 用法：
#   bash design/preview.sh              # 两套主题都出图
#   bash design/preview.sh dark         # 只出暗色
#   bash design/preview.sh light        # 只出亮色
#
# 产物：design/preview-<theme>-<page>.png
# 工具链克隆在 .cache/（已 gitignore，不入库），避免把 GPL 代码带进本仓库。

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CACHE="$ROOT/.cache/toolkit"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
REPO="https://github.com/typora/typora-theme-toolkit.git"

# 官方提供的页面：正文排版 / 源码模式 / 组件与侧栏
PAGES=(lorem source-mode ui-controls2)

if [ ! -d "$CACHE" ]; then
  echo "==> 克隆 Typora 官方预览工具链"
  git clone --depth 1 "$REPO" "$CACHE"
fi

if [ ! -x "$CHROME" ]; then
  echo "找不到 Chrome：$CHROME（可用 CHROME=... 指定）" >&2
  exit 1
fi

render() {
  local theme="$1" css="$2" size="$3"
  local preview="$CACHE/html-preview"

  # 主题 CSS 与资源夹一起放进工具链，保证 @import 的相对路径可用
  cp "$ROOT/$css" "$preview/theme/test.css"
  rm -rf "$preview/theme/gilded-fortune"
  cp -R "$ROOT/gilded-fortune" "$preview/theme/gilded-fortune"

  for page in "${PAGES[@]}"; do
    local out="$ROOT/design/preview-$theme-$page.png"
    "$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
      --window-size="$size" --default-background-color=00000000 \
      --screenshot="$out" "file://$preview/html/$page.html" >/dev/null 2>&1
    echo "    design/preview-$theme-$page.png"
  done
}

case "${1:-both}" in
  dark) render dark gilded-fortune.css 1200,1500 ;;
  light) render light gilded-fortune-light.css 1200,1500 ;;
  both)
    echo "==> 暗色"
    render dark gilded-fortune.css 1200,1500
    echo "==> 亮色"
    render light gilded-fortune-light.css 1200,1500
    ;;
  *)
    echo "用法：bash design/preview.sh [dark|light|both]" >&2
    exit 1
    ;;
esac
