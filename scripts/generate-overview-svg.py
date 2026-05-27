#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import importlib.util
import math
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "sources" / "Inconsolata.glyphs"
DEFAULT_FONT = Path("/tmp/ligconsolata-next-smoke/LigconsolataNext[wdth,wght].ttf")
DEFAULT_SAMPLES = ROOT / "documentation" / "overview-samples.txt"
DEFAULT_OUTPUT = ROOT / "documentation" / "img" / "ligconsolata-next-overview.svg"

WIDTH = 1760
SCALE = 0.019
PANEL_X = 80
PANEL_Y = 222
PANEL_WIDTH = 1600
TABLE_LEFT = PANEL_X + 40
LABEL_COLUMN_WIDTH = 220
LABEL_X = TABLE_LEFT + 28
LEFT_X = TABLE_LEFT + LABEL_COLUMN_WIDTH + 30
RIGHT_X = PANEL_X + 960
GRID_RIGHT = PANEL_X + PANEL_WIDTH - 40
COLUMN_WIDTH = 600
GRID_COLUMNS = 4
GRID_CELL_WIDTH = COLUMN_WIDTH / GRID_COLUMNS
LINE_GAP = 36
CATEGORY_TO_CONTENT = 48
GROUP_BOTTOM_PAD = 30
FIRST_GROUP_Y = 342

CATEGORY_TRANSLATIONS = {
    "Equality": "相等",
    "Arrows": "箭头",
    "Long arrows": "长箭头",
    "Pipes and brackets": "管道与括号",
    "Fira Code inspired": "Fira Code 灵感",
    "Calt-inspired": "calt 灵感",
    "Punctuation": "标点",
    "Separators": "分隔线",
}


@dataclass(frozen=True)
class Sample:
    category: str
    text: str
    number: int


@dataclass(frozen=True)
class PreparedItem:
    sample: Sample
    raw_glyphs: list[str]
    shaped_glyphs: list[str]
    item_width: float
    column: int
    span: int


def load_ligatures() -> list[tuple[str, str]]:
    script = ROOT / "scripts" / "update-ligature-glyphs.py"
    spec = importlib.util.spec_from_file_location("ligconsolata_update_ligatures", script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {script}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return [(ligature.source, ligature.glyph) for ligature in module.LIGATURES]


LIGATURES = load_ligatures()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the Ligconsolata Next README overview SVG.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="Glyphs source used when --build is set.")
    parser.add_argument("--font", type=Path, default=DEFAULT_FONT, help="Built font to read outlines from.")
    parser.add_argument("--samples", type=Path, default=DEFAULT_SAMPLES, help="Text file with grouped ASCII samples.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="SVG output path.")
    parser.add_argument("--build", action="store_true", help="Build a fresh temporary variable font before generating SVG.")
    return parser.parse_args()


def build_font(source: Path, font_path: Path) -> None:
    font_path.parent.mkdir(parents=True, exist_ok=True)
    fontmake = Path(sys.executable).with_name("fontmake")
    fontmake_command = str(fontmake if fontmake.exists() else "fontmake")
    subprocess.run(
        [
            fontmake_command,
            "-g",
            str(source),
            "-o",
            "variable",
            "--master-dir",
            "{tmp}",
            "--output-path",
            str(font_path),
        ],
        cwd=ROOT,
        check=True,
    )


def read_samples(path: Path) -> list[Sample]:
    samples: list[Sample] = []
    category = "Core"
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip("\n")
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("## "):
            category = stripped.removeprefix("## ").strip()
            continue
        if stripped.startswith("#"):
            continue
        samples.append(Sample(category=category, text=line, number=len(samples) + 1))
    if not samples:
        raise ValueError(f"No samples found in {path}")
    return samples


def glyphs_for_text(text: str, cmap: dict[int, str]) -> list[str]:
    glyphs = []
    for char in text:
        glyph_name = cmap.get(ord(char))
        if glyph_name is None:
            raise KeyError(f"Missing glyph for character {char!r}")
        glyphs.append(glyph_name)
    return glyphs


def glyphs_for_liga_text(text: str, cmap: dict[int, str]) -> list[str]:
    glyphs = []
    index = 0
    while index < len(text):
        match = next(((source, glyph_name) for source, glyph_name in LIGATURES if text.startswith(source, index)), None)
        if match is not None:
            source, glyph_name = match
            glyphs.append(glyph_name)
            index += len(source)
            continue
        glyph_name = cmap.get(ord(text[index]))
        if glyph_name is None:
            raise KeyError(f"Missing glyph for character {text[index]!r}")
        glyphs.append(glyph_name)
        index += 1
    return glyphs


def glyphs_for_shaped_text(text: str, cmap: dict[int, str], font_path: Path) -> list[str]:
    hb_shape = "/opt/homebrew/bin/hb-shape"
    if not Path(hb_shape).exists():
        return glyphs_for_liga_text(text, cmap)
    result = subprocess.run(
        [hb_shape, str(font_path), text, "--features=liga=1,dlig=1,calt=1"],
        check=True,
        text=True,
        capture_output=True,
    )
    output = result.stdout.strip()
    if not output.startswith("[") or not output.endswith("]"):
        raise ValueError(f"Unexpected hb-shape output for {text!r}: {output}")
    body = output[1:-1]
    if not body:
        return []
    return [part.split("=", 1)[0] for part in body.split("|")]


def advance_width(glyphs: list[str], hmtx) -> int:
    return sum(hmtx[glyph_name][0] for glyph_name in glyphs)


def safe_comment(text: str) -> str:
    comment = html.escape(text, quote=False)
    while "--" in comment:
        comment = comment.replace("--", "- -")
    if comment.endswith("-"):
        comment += " "
    return comment


def path_element(
    glyph_set,
    glyph_name: str,
    x: float,
    baseline: float,
    fill: str,
    opacity: float = 1,
) -> str:
    pen = SVGPathPen(glyph_set)
    glyph_set[glyph_name].draw(pen)
    commands = pen.getCommands()
    if not commands:
        return ""
    escaped_commands = html.escape(commands)
    return (
        f'<path d="{escaped_commands}" fill="{fill}" opacity="{opacity:.2f}" '
        f'transform="translate({x:.2f} {baseline:.2f}) scale({SCALE:.5f} {-SCALE:.5f})"/>'
    )


def draw_run(
    glyph_set,
    hmtx,
    glyphs: list[str],
    x: float,
    baseline: float,
    fill: str,
    opacity: float = 1,
) -> tuple[str, float]:
    parts = []
    cursor = x
    for glyph_name in glyphs:
        parts.append(path_element(glyph_set, glyph_name, cursor, baseline, fill, opacity))
        cursor += hmtx[glyph_name][0] * SCALE
    return "\n".join(part for part in parts if part), cursor


def grouped_samples(samples: list[Sample]) -> list[tuple[str, list[Sample]]]:
    groups: list[tuple[str, list[Sample]]] = []
    for sample in samples:
        if not groups or groups[-1][0] != sample.category:
            groups.append((sample.category, []))
        groups[-1][1].append(sample)
    return groups


def wrap_group_items(font: TTFont, font_path: Path, samples: list[Sample], cmap, hmtx) -> list[list[PreparedItem]]:
    lines: list[list[PreparedItem]] = [[]]
    column = 0
    for sample in samples:
        raw_glyphs = glyphs_for_text(sample.text, cmap)
        shaped_glyphs = glyphs_for_shaped_text(sample.text, cmap, font_path)
        raw_width = advance_width(raw_glyphs, hmtx)
        shaped_width = advance_width(shaped_glyphs, hmtx)
        if raw_width != shaped_width:
            raise ValueError(f"Width mismatch for {sample.text!r}: raw={raw_width}, shaped={shaped_width}")
        item_width = raw_width * SCALE
        span = max(1, min(GRID_COLUMNS, math.ceil(item_width / GRID_CELL_WIDTH - 0.0001)))
        if lines[-1] and column + span > GRID_COLUMNS:
            lines.append([])
            column = 0
        lines[-1].append(
            PreparedItem(
                sample=sample,
                raw_glyphs=raw_glyphs,
                shaped_glyphs=shaped_glyphs,
                item_width=item_width,
                column=column,
                span=span,
            )
        )
        column += span
    return lines


def draw_items(
    glyph_set,
    hmtx,
    items: list[PreparedItem],
    x: float,
    baseline: float,
    shaped: bool,
) -> str:
    parts = []
    for item in items:
        glyphs = item.shaped_glyphs if shaped else item.raw_glyphs
        fill = "#f6f8fb" if shaped else "#8793a1"
        opacity = 1 if shaped else 0.62
        cursor = x + item.column * GRID_CELL_WIDTH
        drawn, _ = draw_run(glyph_set, hmtx, glyphs, cursor, baseline, fill, opacity)
        parts.append(f"  <!-- {safe_comment(item.sample.text)} {'shaped' if shaped else 'raw'} -->\n  {drawn}")
    return "\n".join(parts)


def panel_rows(font: TTFont, font_path: Path, samples: list[Sample]) -> tuple[str, float]:
    glyph_set = font.getGlyphSet()
    hmtx = font["hmtx"].metrics
    cmap = font.getBestCmap()
    rows = []
    cursor_y = FIRST_GROUP_Y
    for category, category_samples in grouped_samples(samples):
        rule_y = cursor_y
        first_baseline = rule_y + CATEGORY_TO_CONTENT
        item_lines = wrap_group_items(font, font_path, category_samples, cmap, hmtx)
        last_baseline = first_baseline + (len(item_lines) - 1) * LINE_GAP
        label_y = (rule_y + last_baseline + GROUP_BOTTOM_PAD) / 2
        category_translation = CATEGORY_TRANSLATIONS.get(category, "")
        rows.append(
            f'''  <line x1="{TABLE_LEFT}" y1="{rule_y}" x2="{GRID_RIGHT}" y2="{rule_y}" class="rule"/>\n'''
            f'''  <text x="{LABEL_X}" y="{label_y - 7:.1f}" class="sans category" font-size="13" font-weight="800">{html.escape(category)}</text>\n'''
            f'''  <text x="{LABEL_X}" y="{label_y + 13:.1f}" class="sans categoryCn" font-size="11">{html.escape(category_translation)}</text>'''
        )
        for line_index, items in enumerate(item_lines):
            baseline = first_baseline + line_index * LINE_GAP
            rows.append(draw_items(glyph_set, hmtx, items, LEFT_X, baseline, shaped=True))
            rows.append(draw_items(glyph_set, hmtx, items, RIGHT_X, baseline, shaped=False))
        cursor_y = last_baseline + GROUP_BOTTOM_PAD
    return "\n".join(rows), cursor_y


def render_svg(rows: str, sample_count: int, end_y: float) -> str:
    panel_height = end_y - PANEL_Y + 22
    height = int(PANEL_Y + panel_height + 120)
    chips_y = int(PANEL_Y + panel_height + 42)
    shadow_width = WIDTH - 108
    wave_c1 = WIDTH * 0.16
    wave_c2 = WIDTH * 0.33
    wave_c3 = WIDTH * 0.47
    wave_c4 = WIDTH * 0.63
    wave_c5 = WIDTH * 0.76
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" role="img" aria-labelledby="title desc">
  <title id="title">Ligconsolata Next overview</title>
  <desc id="desc">A left-right comparison graphic showing {sample_count} Ligconsolata Next samples. The left side is shaped from a smoke-built font with liga, dlig, and calt enabled, and the right side is the same raw ASCII source with ligatures disabled.</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#111318"/>
      <stop offset="1" stop-color="#20252c"/>
    </linearGradient>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#52d0a4"/>
      <stop offset="1" stop-color="#8fb8ff"/>
    </linearGradient>
    <filter id="softShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="14" stdDeviation="18" flood-color="#000000" flood-opacity=".35"/>
    </filter>
    <style>
      .sans {{ font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
      .muted {{ fill: #9aa7b5; }}
      .soft {{ fill: #cdd6df; }}
      .bright {{ fill: #f5f7fa; }}
      .accent {{ fill: #5ed6af; }}
      .category {{ fill: #70dec0; letter-spacing: .08em; text-transform: uppercase; }}
      .categoryCn {{ fill: #6a7787; }}
      .cn {{ fill: #6f7c8d; }}
      .rowIndex {{ fill: #708094; }}
      .arrow {{ fill: #506070; letter-spacing: .06em; }}
      .panel {{ fill: #171b21; stroke: #313945; stroke-width: 1; }}
      .chip {{ fill: #222832; stroke: #3b4553; stroke-width: 1; }}
      .rule {{ stroke: #2e3743; stroke-width: 1; }}
      .measure {{ stroke-width: 1; stroke-dasharray: 4 5; opacity: .45; }}
      .beforeMeasure {{ stroke: #455161; }}
      .afterMeasure {{ stroke: #708298; }}
    </style>
  </defs>

  <rect width="{WIDTH}" height="{height}" rx="30" fill="url(#bg)"/>
  <path d="M0 {height - 170} C{wave_c1:.0f} {height - 234} {wave_c2:.0f} {height - 116} {wave_c3:.0f} {height - 198} C{wave_c4:.0f} {height - 280} {wave_c5:.0f} {height - 230} {WIDTH} {height - 326} L{WIDTH} {height} L0 {height} Z" fill="#15191f" opacity=".72"/>
  <rect x="54" y="42" width="{shadow_width}" height="{height - 84}" rx="24" fill="#11151b" opacity=".78" filter="url(#softShadow)"/>

  <text x="96" y="96" class="sans bright" font-size="42" font-weight="760">Ligconsolata Next</text>
  <text x="98" y="128" class="sans muted" font-size="17">Left: Ligconsolata Next shaping. Right: raw ASCII. Representative samples, not the full Fira Code feature set.</text>
  <text x="98" y="150" class="sans cn" font-size="13">左侧为 Ligconsolata Next 连字渲染，右侧为原始 ASCII；这里只展示代表性样例，不是完整 Fira Code 特性集。</text>
  <rect x="98" y="170" width="348" height="34" rx="17" fill="url(#accent)" opacity=".95"/>
  <text x="118" y="192" class="sans" font-size="14" font-weight="800" fill="#0c1217">Actual font shaping / 真实字体渲染</text>

  <rect x="{PANEL_X}" y="{PANEL_Y}" width="{PANEL_WIDTH}" height="{panel_height:.0f}" rx="16" class="panel"/>
  <text x="{LEFT_X}" y="{PANEL_Y + 38}" class="sans accent" font-size="20" font-weight="800">Ligconsolata Next</text>
  <text x="{LEFT_X}" y="{PANEL_Y + 62}" class="sans cn" font-size="12">连字渲染结果</text>
  <text x="{LEFT_X}" y="{PANEL_Y + 84}" class="sans muted" font-size="15">ligatures ON / 连字开启</text>
  <rect x="{LEFT_X + 198}" y="{PANEL_Y + 68}" width="38" height="20" rx="10" fill="#5ed6af"/>
  <circle cx="{LEFT_X + 226}" cy="{PANEL_Y + 78}" r="7" fill="#11151b"/>
  <text x="{RIGHT_X}" y="{PANEL_Y + 38}" class="sans soft" font-size="20" font-weight="800">Raw ASCII</text>
  <text x="{RIGHT_X}" y="{PANEL_Y + 62}" class="sans cn" font-size="12">原始 ASCII</text>
  <text x="{RIGHT_X}" y="{PANEL_Y + 84}" class="sans muted" font-size="15">ligatures OFF / 连字关闭</text>
  <rect x="{RIGHT_X + 200}" y="{PANEL_Y + 68}" width="38" height="20" rx="10" fill="#586170"/>
  <circle cx="{RIGHT_X + 210}" cy="{PANEL_Y + 78}" r="7" fill="#11151b"/>

{rows}

  <g transform="translate(96 {chips_y})">
    <rect class="chip" width="276" height="32" rx="16"/>
    <text x="18" y="21" class="sans soft" font-size="13">{len(LIGATURES)} ligature rules / {len(LIGATURES)} 条规则</text>
    <rect x="294" class="chip" width="260" height="32" rx="16"/>
    <text x="312" y="21" class="sans soft" font-size="13">Samples file / 样例配置</text>
    <rect x="572" class="chip" width="304" height="32" rx="16"/>
    <text x="590" y="21" class="sans soft" font-size="13">Advance width preserved / 保持等宽</text>
    <rect x="894" class="chip" width="318" height="32" rx="16"/>
    <text x="912" y="21" class="sans soft" font-size="13">liga + dlig + calt verified / 特性已验证</text>
  </g>
</svg>
'''


def main() -> None:
    args = parse_args()
    if args.build or not args.font.exists():
        build_font(args.source, args.font)
    if not args.font.exists():
        raise FileNotFoundError(f"Font not found: {args.font}")
    samples = read_samples(args.samples)
    font = TTFont(args.font)
    rows, end_y = panel_rows(font, args.font, samples)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_svg(rows, len(samples), end_y), encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
