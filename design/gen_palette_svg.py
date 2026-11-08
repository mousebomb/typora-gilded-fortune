#!/usr/bin/env python3
"""生成 README 用的配色卡 SVG：只呈现最终采用的暗/亮两套色板。

改色后重新执行本脚本，不要手改 SVG：
    python3 design/gen_palette_svg.py
"""

import pathlib

W, H = 1240, 820
PAD = 40
PANEL_W = 560
PANEL_H = 700

FONT = "'PingFang SC','Hiragino Sans GB','Noto Sans SC',-apple-system,sans-serif"
MONO = "'SF Mono',Menlo,monospace"

DARK = dict(
    bg="#17150f", deep="#131109", surface="#1e1b13", control="#221f15",
    line="#322c1c", fg="#f5efe0", muted="#c9bfa5", faint="#8a8068",
    accent="#c8a63f", link="#d9c06b", code="#1c1912", sel="#4a3d18",
    name="Gilded Fortune", sub="暗色 · 近黑褐底 + 压一档的鎏金",
)
LIGHT = dict(
    bg="#f2ebda", deep="#ebe2cf", surface="#f8f3e6", control="#ece4d0",
    line="#ded1b5", fg="#1b1813", muted="#5f5745", faint="#8a7f65",
    accent="#7a5f1a", link="#6b5316", code="#ece3cd", sel="#ddd0a8",
    name="Gilded Fortune Light", sub="亮色 · 同源推导的羊皮纸",
)

ROLES = [
    ("bg", "页面底"),
    ("deep", "侧栏底"),
    ("surface", "卡片 / 弹窗"),
    ("control", "控件 / 输入框"),
    ("line", "边框"),
    ("code", "代码底"),
    ("fg", "正文"),
    ("muted", "次要文字"),
    ("faint", "语法符号"),
    ("accent", "强调金"),
    ("link", "链接"),
    ("sel", "选区底"),
]


def lum(hexv):
    h = hexv.lstrip("#")
    r, g, b = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def ratio(a, b):
    l1, l2 = sorted([lum(a), lum(b)], reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def chip_text_color(hexv):
    """在色块上放深字还是浅字，按亮度挑对比更高的一边。"""
    return "#14110b" if lum(hexv) > 0.35 else "#f7f1e2"


def panel(x, y, c):
    p = [f'<rect x="{x}" y="{y}" width="{PANEL_W}" height="{PANEL_H}" rx="18" '
         f'fill="{c["bg"]}" stroke="#000" stroke-opacity="0.35"/>']

    # 标题区
    p.append(f'<text x="{x+32}" y="{y+50}" font-family="{FONT}" font-size="22" '
             f'font-weight="700" fill="{c["accent"]}">{c["name"]}</text>')
    p.append(f'<text x="{x+32}" y="{y+74}" font-family="{FONT}" font-size="12.5" '
             f'fill="{c["muted"]}">{c["sub"]}</text>')

    # 迷你排版示意：标题 + 正文 + 行内代码 + 引用
    tx = x + 32
    p.append(f'<text x="{tx}" y="{y+118}" font-family="{FONT}" font-size="17" '
             f'font-weight="600" fill="{c["fg"]}">金运亨通</text>')
    p.append(f'<rect x="{tx}" y="{y+128}" width="88" height="3" rx="1.5" fill="{c["accent"]}"/>')
    p.append(f'<text x="{tx}" y="{y+156}" font-family="{FONT}" font-size="12" '
             f'fill="{c["fg"]}">近黑褐底压一档鎏金，长时间读写不刺眼。</text>')
    p.append(f'<text x="{tx}" y="{y+178}" font-family="{FONT}" font-size="12" '
             f'fill="{c["muted"]}">次要文字与语法符号拉开层次。</text>')
    # 行内代码
    p.append(f'<rect x="{tx}" y="{y+192}" width="118" height="22" rx="4" fill="{c["code"]}"/>')
    p.append(f'<text x="{tx+10}" y="{y+207}" font-family="{MONO}" font-size="11" '
             f'fill="{c["accent"]}">gilded-fortune</text>')
    # 引用块
    p.append(f'<rect x="{tx}" y="{y+228}" width="{PANEL_W-64}" height="66" rx="6" '
             f'fill="{c["surface"]}"/>')
    p.append(f'<rect x="{tx}" y="{y+228}" width="3" height="66" fill="{c["accent"]}"/>')
    p.append(f'<text x="{tx+16}" y="{y+252}" font-family="{FONT}" font-size="11.5" '
             f'fill="{c["muted"]}">同一套色板推导明暗两版，</text>')
    p.append(f'<text x="{tx+16}" y="{y+272}" font-family="{FONT}" font-size="11.5" '
             f'fill="{c["muted"]}">暗端暖、亮端像羊皮纸。</text>')

    # 12 个色块：三行四列
    top = y + 322
    cw, ch, gap = 120, 40, 10
    for i, (key, cn) in enumerate(ROLES):
        col, row = i % 4, i // 4
        cx = tx + col * (cw + gap)
        cy = top + row * (ch + 30)
        hexv = c[key]
        p.append(f'<text x="{cx}" y="{cy-7}" font-family="{FONT}" font-size="10.5" '
                 f'fill="{c["muted"]}">{cn}</text>')
        p.append(f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="6" '
                 f'fill="{hexv}" stroke="{c["fg"]}" stroke-opacity="0.12"/>')
        p.append(f'<text x="{cx+cw/2}" y="{cy+25}" text-anchor="middle" '
                 f'font-family="{MONO}" font-size="11" fill="{chip_text_color(hexv)}">'
                 f'{hexv.upper()}</text>')

    # 对比度摘要
    p.append(f'<text x="{tx}" y="{y+PANEL_H-26}" font-family="{MONO}" font-size="10.5" '
             f'fill="{c["muted"]}">正文 {ratio(c["fg"], c["bg"]):.1f}:1　'
             f'次文 {ratio(c["muted"], c["bg"]):.1f}:1　'
             f'强调 {ratio(c["accent"], c["bg"]):.1f}:1</text>')
    return "".join(p)


parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}" role="img" aria-label="Gilded Fortune 配色卡">']
parts.append(f'<rect width="{W}" height="{H}" fill="#0b0a07"/>')
parts.append(f'<text x="{PAD}" y="34" font-family="{FONT}" font-size="11" '
             f'letter-spacing="4" fill="#8a6d1f">GILDED FORTUNE · 金运亨通</text>')
parts.append(f'<text x="{W-PAD}" y="34" text-anchor="end" font-family="{FONT}" '
             f'font-size="11" fill="#6f6656">Typora 主题 · 明暗双版</text>')
parts.append(panel(PAD, 64, DARK))
parts.append(panel(PAD + PANEL_W + 40, 64, LIGHT))
parts.append(f'<text x="{PAD}" y="{H-22}" font-family="{FONT}" font-size="11" '
             f'fill="#6f6656">色块内文字为十六进制值；亮色端强调金已压深，以满足浅底上的可读性。</text>')
parts.append(f'<text x="{W-PAD}" y="{H-22}" text-anchor="end" font-family="{MONO}" '
             f'font-size="10.5" fill="#4a4335">design/palette.svg</text>')
parts.append("</svg>")

out = pathlib.Path(__file__).with_name("palette.svg")
out.write_text("\n".join(parts), encoding="utf-8")
print(out, len(out.read_text(encoding="utf-8")), "chars")
