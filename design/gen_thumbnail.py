#!/usr/bin/env python3
"""生成画廊投稿用的 500×400 缩略图（先出 2 倍尺寸 SVG，再光栅化缩放）。

    python3 design/gen_thumbnail.py

产物：
    design/thumbnail.svg   矢量源
    design/thumbnail.png   1000×800 位图（投稿前用 sips 缩到 500×400）
"""

import pathlib

W, H = 1000, 800
SPLIT = 330  # 上半亮色带高度

FONT = "'PingFang SC','Hiragino Sans GB','Noto Sans SC',-apple-system,sans-serif"
MONO = "'SF Mono',Menlo,monospace"

DARK = dict(bg="#17150f", fg="#f5efe0", muted="#c9bfa5", faint="#8a8068",
            accent="#c8a63f", link="#d9c06b", surface="#1e1b13", line="#322c1c",
            code="#1c1912")
LIGHT = dict(bg="#f2ebda", fg="#1b1813", muted="#5f5745", faint="#8a7f65",
             accent="#7a5f1a", link="#6b5316", surface="#f8f3e6", line="#ded1b5",
             code="#ece3cd")

parts = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
         f'width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="Gilded Fortune 金运亨通 Typora 主题">']

# 上半：亮色品牌带
parts.append(f'<rect width="{W}" height="{SPLIT}" fill="{LIGHT["bg"]}"/>')
# 图标（沿用 Paseo 版「金」字图标）
parts.append(f'<image x="56" y="62" width="104" height="104" xlink:href="../assets/icon.png"/>')
parts.append(f'<text x="192" y="118" font-family="{FONT}" font-size="44" font-weight="700" '
             f'fill="{LIGHT["fg"]}">金运亨通</text>')
parts.append(f'<text x="194" y="152" font-family="{FONT}" font-size="17" '
             f'fill="{LIGHT["muted"]}">Gilded Fortune · Typora 明暗双主题</text>')
parts.append(f'<text x="56" y="236" font-family="{FONT}" font-size="19" '
             f'fill="{LIGHT["fg"]}">近黑褐底压一档鎏金，配同源推导的羊皮纸亮色版。</text>')
parts.append(f'<text x="56" y="272" font-family="{FONT}" font-size="17" '
             f'fill="{LIGHT["muted"]}">正文 / 次文 / 链接 / 代码，全套对比度过 WCAG AA。</text>')
parts.append(f'<rect x="56" y="292" width="72" height="3" rx="1.5" fill="{LIGHT["accent"]}"/>')

# 下半：暗色排版特写
parts.append(f'<rect y="{SPLIT}" width="{W}" height="{H-SPLIT}" fill="{DARK["bg"]}"/>')
by = SPLIT + 58
parts.append(f'<text x="56" y="{by}" font-family="{FONT}" font-size="30" font-weight="600" '
             f'fill="{DARK["fg"]}">阅读与写作的底色</text>')
parts.append(f'<rect x="40" y="{by-24}" width="4" height="30" rx="2" fill="{DARK["accent"]}"/>')

parts.append(f'<text x="56" y="{by+46}" font-family="{FONT}" font-size="18" '
             f'fill="{DARK["fg"]}">金色只留给强调与层级，不铺满界面；</text>')
parts.append(f'<text x="56" y="{by+76}" font-family="{FONT}" font-size="18" '
             f'fill="{DARK["fg"]}">代码高亮限定在金 / 橄榄 / 赤陶 / 米白四色系。</text>')

# 行内代码
parts.append(f'<rect x="56" y="{by+96}" width="196" height="30" rx="5" fill="{DARK["code"]}"/>')
parts.append(f'<text x="70" y="{by+117}" font-family="{MONO}" font-size="15" '
             f'fill="{DARK["accent"]}">gilded-fortune.css</text>')

# 引用块
qy = by + 148
parts.append(f'<rect x="56" y="{qy}" width="{W-112}" height="86" rx="6" fill="{DARK["surface"]}"/>')
parts.append(f'<rect x="56" y="{qy}" width="3" height="86" fill="{DARK["accent"]}"/>')
parts.append(f'<text x="78" y="{qy+32}" font-family="{FONT}" font-size="16" '
             f'fill="{DARK["muted"]}">Typora 只读主题 CSS，所以两版共用同一份结构层，</text>')
parts.append(f'<text x="78" y="{qy+58}" font-family="{FONT}" font-size="16" '
             f'fill="{DARK["muted"]}">改版式只改一处，换色只换变量表。</text>')

# 页脚
parts.append(f'<text x="56" y="{H-26}" font-family="{MONO}" font-size="13" '
             f'fill="{DARK["faint"]}">github.com/mousebomb/typora-gilded-fortune</text>')

# 色板条：缩到 500×400 后仍能一眼看到主色
chips = ["#f5efe0", "#c8a63f", "#d9c06b", "#a9b878", "#cf8b5a", "#322c1c"]
for i, hexv in enumerate(chips):
    parts.append(f'<rect x="{56 + i * 120}" y="{H-152}" width="110" height="44" rx="8" '
                 f'fill="{hexv}" stroke="{DARK["fg"]}" stroke-opacity="0.14"/>')
parts.append("</svg>")

out = pathlib.Path(__file__).with_name("thumbnail.svg")
out.write_text("\n".join(parts), encoding="utf-8")
print(out, len(out.read_text(encoding="utf-8")), "chars")
