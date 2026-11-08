# Typora Gilded Fortune 技术约束

本文件沉淀 Typora 主题的机制与踩坑记录，避免以后重复翻源码。

## 环境

- 开发机：macOS，Typora 1.14.15
- 主题目录：`~/Library/Application Support/abnerworks.Typora/themes/`
- Typora 源码位置（本地安装包内）：`/Applications/Typora.app/Contents/Resources/TypeMark/`
  - `style/base.css`、`window.css`、`base-control.css`、`megamenu.css`：编辑器与界面基础样式
  - `appsrc/main.js`：主题加载与明暗判型逻辑
  - `Docs/Write Custom Theme.md`：官方主题文档的离线版

## 明暗判型（最容易翻车的一条）

Typora 不看任何元数据，直接把 `document.body` 的计算背景色换算成亮度：

```
(299*R + 587*G + 114*B) / 256000 < 0.5  →  当作暗色主题
```

源码：`appsrc/main.js` 的 `setTheme()`。后果：

- 暗色主题的 `body` 必须是**实底背景**，写 `transparent` 或让它继承会导致侧栏、菜单、弹窗按亮色渲染
- 换主题后 Typora 会重新计算，所以两套主题各自定义 `--bg-color` 与 `body` 背景即可
- 偏好设置里「自定义字号」是给 `<html>` 写内联 `style.fontSize`，会正常覆盖主题的 `html{font-size:16px}`

## CSS 变量契约

Typora 通过约 30 个 `:root` 变量驱动界面。本主题用到的关键项：

| 变量 | 实际用途 | 我们踩过的点 |
|---|---|---|
| `--bg-color` | 全窗口背景 | 必须与主题底色一致，参与明暗判型 |
| `--side-bar-bg-color` | 侧栏背景 | 亮色端要比正文底略深 |
| `--active-file-bg-color` / `--active-file-text-color` | 文件树/搜索结果的选中行 | 必须成对校验对比度，别留深底深字 |
| `--primary-color` | 选中态描边、排序按钮文字 | 也会压在 `--active-file-bg-color` 上，两处都要够亮/够深 |
| `--item-hover-bg-color` / `--item-hover-text-color` | 菜单与列表悬停 | 同上 |
| `--select-text-bg-color` / `--select-text-font-color` | 正文选区 | 用不透明底，避免与背景混出低对比 |
| `--search-select-bg-color` | 搜索命中项 | 文字颜色另有 `--search-select-text-color` |
| `--active-toggle-btn-color` | 搜索面板开关按钮激活底 | 源码里固定配 `color:#000`，所以亮色端必须给浅金 |
| `--blur-text-color` | 聚焦模式淡出文字 | 暗色端别用太亮的值，否则"淡出"没效果 |
| `--monospace` | 代码字体 | 只走系统栈，不打包字体 |

## 选择器要点

- **代码围栏**用 CodeMirror，主题类名 `.cm-s-inner`；**源码模式**类名是 `.cm-s-typora-default`，两套要分别写
- 正文区域选择器尽量写成 `#write h2` 这种形式，避免影响弹窗里同样用 `<h4>` 的控件
- 文件树选中态：`.file-tree-node.active > .file-node-background`；列表态：`.file-list-item.active`
- 大纲选中态两套类名并存：`outline-active`（新）与 `outline-item-active`（旧），都要覆盖
- Windows/Linux 的 unibody 界面用 `#megamenu-menu` / `.megamenu-menu-sidebar` / `.megamenu-menu-list`，macOS 用不到但别删

## 不要做的事

- 不要给 `#write` 设 `white-space: pre-wrap`：官方文档点名，会让 Tab 键插不进制表符
- 不要写死 `text-indent`：首行缩进是 Typora 偏好面板的开关，类名 `#write.first-line-indent`
- 不要在主题里 `@font-face` 引远程字体：离线或墙内会挂，且增加体积
- 不要改 Typora 安装包内的文件：升级即被覆盖
- 文件名必须全小写、无空格，Typora 会把 `-` 转成菜单里的空格与首字母大写

## 结构层与配色层的分工

- `gilded-fortune/base.css`：所有结构样式，只引用 `--gf-*` 变量，**不含任何具体色值**
- `gilded-fortune.css` / `gilded-fortune-light.css`：只定义变量（Typora 契约 + `--gf-*` 色阶 + 语法色 + `--mermaid-theme`）
- 这样两套主题的差异只有变量表，改版式只需改一处

## 测试

`test/theme.test.mjs`（node:test，零依赖）守住：

1. Typora 变量与 `--gf-*` 变量齐全
2. 正文 7:1、次文/链接/代码/选中行/选区 4.5:1 等对比度阈值
3. `body` 背景亮度落在正确一侧（暗色 < 0.5，亮色 > 0.5）
4. 无远程 `@import` / `url()` / `@font-face`，且 `@import` 目标存在
5. 结构层不出现 `white-space: pre-wrap`、`text-indent`、`tab-size`

改色后 `npm test` 必须全绿。确需放宽阈值时，先改测试并在 devlog 写明理由。

## 预览与截图

`design/preview.sh` 克隆 Typora 官方调试工具链 `typora/typora-theme-toolkit` 到 `.cache/`（已 gitignore，**不把 GPL 代码带进本仓库**），把主题 CSS 与资源夹灌进去，再用 Chrome headless 截图：

```bash
npm run preview            # 两套主题，各 3 张
bash design/preview.sh dark
```

页面来源：`lorem.html`（正文排版）、`source-mode.html`（源码模式）、`ui-controls2.html`（侧栏与文件列表）。

## 主题画廊（以后要投稿再看）

- 仓库：`typora/theme.typora.io`，分支 `gh-pages`（文档里写的 `typora-theme-gallery` 是旧名）
- 新增 `_posts/theme/YYYY-MM-DD-<slug>.md`，YAML 字段（以近期条目为准）：
  `layout: theme`、`category: theme`、`title`、`homepage`、`download`、`builtin: false`、
  `author`、`author_url`、`thumbnail`、`preview`、`description`、`tags`，
  以及 `typora-root-url: ../../`、`typora-copy-images-to: ../../media/theme/<slug>`
- 缩略图放 `media/thumbnails/<slug>.png`，250×200 或 500×400；`thumbnail` 与 `preview` 常指向同一张
- 详情页截图放 `media/theme/<slug>/`，在正文里用相对路径引用
- 只在 macOS 测过就要在正文里声明未逐项验证 Windows/Linux

## 开发日志

每次修改后更新 `devlog/`（统一日志仓库：`~/MyWork/devlog/typora-gilded-fortune/`），记录需求、问题定位、最终方案。
