/**
 * 主题契约测试（node:test，零第三方依赖）
 *
 * 守住四类问题：
 *   1. Typora 变量 / 主题内部变量缺失，导致某块界面回落到浅色默认值；
 *   2. 对比度不达标（正文、次要文字、选中行、代码、选区、语法高亮）；
 *   3. body 背景亮度不对，Typora 会把暗色主题判成亮色（侧栏菜单翻白）；
 *   4. 引用了外部字体或远程资源，离线/墙内会挂。
 *
 * 运行：node --test test/theme.test.mjs
 */

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, existsSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const THEMES = [
  { file: "gilded-fortune.css", name: "暗色", dark: true },
  { file: "gilded-fortune-light.css", name: "亮色", dark: false },
];

/** 读取主题 CSS 里的变量表（先剥掉注释，避免变量被注释块挡在行首） */
function readVars(file) {
  const css = readFileSync(join(ROOT, file), "utf8");
  assert.match(css, /:root\s*\{/, `${file} 里没有 :root 变量块`);

  const vars = {};
  for (const m of css.replace(/\/\*[\s\S]*?\*\//g, "").matchAll(/(--[\w-]+)\s*:\s*([^;]+);/g)) {
    vars[m[1]] = m[2].trim();
  }
  assert.ok(Object.keys(vars).length > 0, `${file} 里没有解析到任何变量`);
  return { css, vars };
}

function hexToRgb(hex) {
  const h = hex.trim().replace("#", "");
  assert.match(h, /^[0-9a-fA-F]{6}$/, `不是合法的六位十六进制色值: ${hex}`);
  return [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16));
}

/** 相对亮度（WCAG 2.1） */
function luminance([r, g, b]) {
  const f = (c) => {
    const s = c / 255;
    return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
  };
  return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
}

function contrast(a, b) {
  const [l1, l2] = [luminance(hexToRgb(a)), luminance(hexToRgb(b))].sort((x, y) => y - x);
  return (l1 + 0.05) / (l2 + 0.05);
}

/** Typora 判断主题明暗用的算法：body 背景亮度 < 0.5 即暗色 */
function brightness(hex) {
  const [r, g, b] = hexToRgb(hex);
  return (299 * r + 587 * g + 114 * b) / 256000;
}

const TYPORA_VARS = [
  "--bg-color",
  "--text-color",
  "--side-bar-bg-color",
  "--window-border",
  "--active-file-bg-color",
  "--active-file-text-color",
  "--active-file-border-color",
  "--item-hover-bg-color",
  "--item-hover-text-color",
  "--control-text-color",
  "--control-text-hover-color",
  "--primary-color",
  "--primary-btn-border-color",
  "--primary-btn-text-color",
  "--md-char-color",
  "--meta-content-color",
  "--select-text-bg-color",
  "--select-text-font-color",
  "--search-select-bg-color",
  "--table-border-color",
  "--rawblock-edit-panel-bd",
  "--panel-border-color",
  "--focus-ring-color",
  "--blur-text-color",
  "--active-toggle-btn-color",
  "--heading-char-color",
  "--drag-placeholder-color",
  "--monospace",
];

const GF_VARS = [
  "--gf-bg",
  "--gf-bg-deep",
  "--gf-surface",
  "--gf-control",
  "--gf-line",
  "--gf-line-strong",
  "--gf-fg",
  "--gf-muted",
  "--gf-faint",
  "--gf-accent",
  "--gf-accent-bright",
  "--gf-accent-dim",
  "--gf-accent-soft",
  "--gf-link",
  "--gf-active-bg",
  "--gf-hover-bg",
  "--gf-code-bg",
  "--gf-icode-bg",
  "--gf-icode-fg",
  "--gf-thead-bg",
  "--gf-zebra",
  "--gf-quote-bg",
  "--gf-sel-bg",
  "--gf-sel-fg",
  "--gf-mark-bg",
  "--gf-mark-fg",
  "--gf-hit",
  "--gf-shadow",
  "--gf-alert-note",
  "--gf-alert-tip",
  "--gf-alert-important",
  "--gf-alert-warning",
  "--gf-alert-caution",
  "--gf-syn-keyword",
  "--gf-syn-string",
  "--gf-syn-number",
  "--gf-syn-def",
  "--gf-syn-variable",
  "--gf-syn-type",
  "--gf-syn-tag",
  "--gf-syn-operator",
  "--gf-syn-meta",
  "--gf-syn-link",
  "--gf-syn-comment",
  "--gf-syn-error",
  "--mermaid-theme",
];

/** 对比度要求：[前景, 背景, 最低比值, 说明] */
const CONTRAST_RULES = [
  ["--gf-fg", "--gf-bg", 7, "正文 / 页面底"],
  ["--gf-muted", "--gf-bg", 4.5, "次要文字 / 页面底"],
  ["--gf-faint", "--gf-bg", 3, "语法符号 / 页面底"],
  ["--gf-accent", "--gf-bg", 4.5, "强调金 / 页面底"],
  ["--gf-accent-bright", "--gf-bg", 4.5, "高亮金 / 页面底"],
  ["--gf-link", "--gf-bg", 4.5, "链接 / 页面底"],
  ["--gf-fg", "--gf-surface", 7, "正文 / 卡片层"],
  ["--gf-fg", "--gf-control", 7, "正文 / 控件层"],
  ["--gf-fg", "--gf-bg-deep", 7, "正文 / 侧栏底"],
  ["--gf-fg", "--gf-thead-bg", 7, "正文 / 表头"],
  ["--gf-fg", "--gf-code-bg", 7, "正文 / 代码底"],
  ["--gf-fg", "--gf-active-bg", 4.5, "正文 / 选中行"],
  ["--gf-fg", "--gf-hover-bg", 4.5, "正文 / 悬停行"],
  ["--gf-fg", "--gf-hit", 4.5, "正文 / 搜索高亮"],
  ["--gf-icode-fg", "--gf-icode-bg", 4.5, "行内代码文字 / 底色"],
  ["--gf-sel-fg", "--gf-sel-bg", 4.5, "选区文字 / 选区底"],
  ["--gf-mark-fg", "--gf-mark-bg", 4.5, "高亮文字 / 高亮底"],
  ["--gf-syn-comment", "--gf-code-bg", 3.5, "代码注释 / 代码底"],
  ["--gf-syn-keyword", "--gf-code-bg", 4.5, "代码关键字 / 代码底"],
  ["--gf-syn-string", "--gf-code-bg", 4.5, "代码字符串 / 代码底"],
  ["--gf-syn-number", "--gf-code-bg", 4.5, "代码数字 / 代码底"],
  ["--gf-syn-def", "--gf-code-bg", 4.5, "代码函数 / 代码底"],
  ["--gf-syn-variable", "--gf-code-bg", 4.5, "代码变量 / 代码底"],
  ["--gf-syn-type", "--gf-code-bg", 4.5, "代码类型 / 代码底"],
  ["--gf-syn-tag", "--gf-code-bg", 4.5, "代码标签 / 代码底"],
  ["--gf-syn-operator", "--gf-code-bg", 4.5, "代码运算符 / 代码底"],
  ["--gf-syn-meta", "--gf-code-bg", 4.5, "代码元信息 / 代码底"],
  ["--gf-syn-link", "--gf-code-bg", 4.5, "代码链接 / 代码底"],
  ["--text-color", "--active-file-bg-color", 4.5, "选中文件行文字 / 选中底"],
  ["--primary-color", "--active-file-bg-color", 4.5, "选中态强调色 / 选中底"],
  ["--primary-color", "--bg-color", 4.5, "选中态强调色 / 页面底"],
  ["--item-hover-text-color", "--item-hover-bg-color", 4.5, "悬停文字 / 悬停底"],
  ["--primary-btn-text-color", "--gf-accent", 4.5, "主按钮文字 / 主按钮底"],
  ["--search-select-text-color", "--search-select-bg-color", 4.5, "搜索选中文字 / 底"],
];

for (const theme of THEMES) {
  const { css, vars } = readVars(theme.file);

  test(`${theme.name}：Typora 变量齐全`, () => {
    const missing = TYPORA_VARS.filter((v) => !vars[v]);
    assert.deepEqual(missing, [], `缺少变量: ${missing.join(", ")}`);
  });

  test(`${theme.name}：主题色阶变量齐全`, () => {
    const missing = GF_VARS.filter((v) => !vars[v]);
    assert.deepEqual(missing, [], `缺少变量: ${missing.join(", ")}`);
  });

  test(`${theme.name}：body 背景亮度让 Typora 判对明暗`, () => {
    const value = brightness(vars["--gf-bg"]);
    if (theme.dark) {
      assert.ok(value < 0.5, `暗色主题背景亮度 ${value.toFixed(3)}，会被判成亮色`);
    } else {
      assert.ok(value > 0.5, `亮色主题背景亮度 ${value.toFixed(3)}，会被判成暗色`);
    }
    assert.equal(vars["--bg-color"], vars["--gf-bg"], "--bg-color 必须与 --gf-bg 一致");
  });

  for (const [fg, bg, min, label] of CONTRAST_RULES) {
    test(`${theme.name}：${label} ≥ ${min}:1`, () => {
      const ratio = contrast(vars[fg], vars[bg]);
      assert.ok(ratio >= min, `${ratio.toFixed(2)}:1（${fg} on ${bg}），要求 ≥ ${min}:1`);
    });
  }

  test(`${theme.name}：不引用远程资源与外部字体`, () => {
    assert.ok(!/@import\s+url\(\s*["']?https?:/i.test(css), "存在远程 @import");
    assert.ok(!/url\(\s*["']?https?:/i.test(css), "存在远程 url()");
    assert.ok(!/@font-face/i.test(css), "不应自带 @font-face，字体走系统栈");
  });

  test(`${theme.name}：@import 指向的文件都存在`, () => {
    const imports = [...css.matchAll(/@import\s+["']([^"']+)["']/g)].map((m) => m[1]);
    assert.ok(imports.length > 0, "主题没有 import 结构层");
    for (const path of imports) {
      assert.ok(existsSync(join(ROOT, path)), `@import 目标不存在: ${path}`);
    }
  });
}

test("两套主题的色阶变量集合一致", () => {
  const { vars: a } = readVars(THEMES[0].file);
  const { vars: b } = readVars(THEMES[1].file);
  const keysA = Object.keys(a).filter((k) => k.startsWith("--gf-")).sort();
  const keysB = Object.keys(b).filter((k) => k.startsWith("--gf-")).sort();
  assert.deepEqual(keysA, keysB, "暗色与亮色主题的 --gf-* 变量应一一对应");
});

test("结构层不碰会破坏编辑行为的属性", () => {
  const base = readFileSync(join(ROOT, "gilded-fortune/base.css"), "utf8");
  // 官方文档明确提醒：给 #write 加 white-space: pre-wrap 会导致 Tab 键失效
  assert.ok(!/white-space\s*:\s*pre-wrap/i.test(base), "结构层不应设置 white-space: pre-wrap");
  assert.ok(!/text-indent\s*:/i.test(base), "首行缩进交给 Typora 偏好面板，结构层不应写死");
  assert.ok(!/\btab-size\s*:/i.test(base), "不应覆盖 tab-size");
});
