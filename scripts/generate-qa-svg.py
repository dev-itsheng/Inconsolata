#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import subprocess
from dataclasses import dataclass
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont


ROOT = Path(__file__).resolve().parents[1]
SMOKE_FONT = Path("/tmp/ligconsolata-next-smoke/LigconsolataNext[wdth,wght].ttf")
DEMO_FONT = ROOT / "documentation" / "demo" / "fonts" / "LigconsolataNext[wdth,wght].ttf"
CONFUSABLE_SAMPLES = ROOT / "documentation" / "qa" / "confusable-samples.txt"
MATRIX_SAMPLES = ROOT / "documentation" / "qa" / "matrix-samples.txt"
CONFUSABLE_OUTPUT = ROOT / "documentation" / "img" / "ligconsolata-next-confusables-qa.svg"
MATRIX_OUTPUT = ROOT / "documentation" / "img" / "ligconsolata-next-size-weight-matrix.svg"


@dataclass(frozen=True)
class Sample:
    category: str
    category_cn: str
    text: str


@dataclass(frozen=True)
class SvgTheme:
    name: str
    name_cn: str
    panel_fill: str
    text_fill: str
    muted_fill: str
    rule: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Ligconsolata Next QA SVG specimens.")
    parser.add_argument("--font", type=Path, default=None, help="Built Ligconsolata Next variable font.")
    parser.add_argument("--confusable-samples", type=Path, default=CONFUSABLE_SAMPLES)
    parser.add_argument("--matrix-samples", type=Path, default=MATRIX_SAMPLES)
    parser.add_argument("--confusable-output", type=Path, default=CONFUSABLE_OUTPUT)
    parser.add_argument("--matrix-output", type=Path, default=MATRIX_OUTPUT)
    return parser.parse_args()


def resolve_font(path: Path | None) -> Path:
    if path is not None:
        return path
    for candidate in (SMOKE_FONT, DEMO_FONT):
        if candidate.exists():
            return candidate
    raise FileNotFoundError("No built Ligconsolata Next font found. Run a smoke build or pass --font.")


def split_label(label: str) -> tuple[str, str]:
    if " / " not in label:
        return label, ""
    left, right = label.split(" / ", 1)
    return left.strip(), right.strip()


def read_grouped_samples(path: Path) -> list[Sample]:
    samples: list[Sample] = []
    category = "Samples"
    category_cn = "样例"
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        if line.startswith("## ") and " / " in line:
            category, category_cn = split_label(line.removeprefix("## ").strip())
            continue
        samples.append(Sample(category=category, category_cn=category_cn, text=line))
    if not samples:
        raise ValueError(f"No samples found in {path}")
    return samples


def read_plain_samples(path: Path) -> list[str]:
    samples = [line.rstrip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not samples:
        raise ValueError(f"No samples found in {path}")
    return samples


def shape_text(font_path: Path, text: str, *, enabled: bool) -> list[str]:
    hb_shape = Path("/opt/homebrew/bin/hb-shape")
    if not hb_shape.exists():
        return []
    features = "liga=1,dlig=1,calt=1" if enabled else "liga=0,dlig=0,calt=0"
    result = subprocess.run(
        [str(hb_shape), str(font_path), text, f"--features={features}"],
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


def glyphs_for_text(font: TTFont, font_path: Path, text: str, *, enabled: bool) -> list[str]:
    shaped = shape_text(font_path, text, enabled=enabled)
    if shaped:
        return shaped
    cmap = font.getBestCmap()
    glyphs = []
    for char in text:
        glyph_name = cmap.get(ord(char))
        if glyph_name is None:
            raise KeyError(f"Missing glyph for character {char!r}")
        glyphs.append(glyph_name)
    return glyphs


def instance_font(font: TTFont, weight: float) -> TTFont:
    if "fvar" not in font:
        return font
    axes = {axis.axisTag: axis.defaultValue for axis in font["fvar"].axes}
    axes["wght"] = weight
    if "wdth" in axes:
        axes["wdth"] = 100
    return instantiateVariableFont(font, axes, inplace=False)


def weight_values(font: TTFont) -> list[int]:
    if "fvar" not in font:
        return [400]
    axis = next((axis for axis in font["fvar"].axes if axis.axisTag == "wght"), None)
    if axis is None:
        return [400]
    values = [int(axis.minValue), int(axis.defaultValue), 700, int(axis.maxValue)]
    bounded = [max(int(axis.minValue), min(int(axis.maxValue), value)) for value in values]
    return sorted(set(bounded), key=bounded.index)


def path_element(glyph_set, glyph_name: str, x: float, baseline: float, scale: float, fill: str, opacity: float = 1) -> str:
    pen = SVGPathPen(glyph_set)
    glyph_set[glyph_name].draw(pen)
    commands = pen.getCommands()
    if not commands:
        return ""
    return (
        f'<path d="{html.escape(commands)}" fill="{fill}" opacity="{opacity:.2f}" '
        f'transform="translate({x:.2f} {baseline:.2f}) scale({scale:.5f} {-scale:.5f})"/>'
    )


def draw_run(font: TTFont, glyphs: list[str], x: float, baseline: float, size: float, fill: str, opacity: float = 1) -> str:
    glyph_set = font.getGlyphSet()
    hmtx = font["hmtx"].metrics
    scale = size / 1000
    cursor = x
    parts = []
    for glyph_name in glyphs:
        if glyph_name not in hmtx:
            continue
        parts.append(path_element(glyph_set, glyph_name, cursor, baseline, scale, fill, opacity))
        cursor += hmtx[glyph_name][0] * scale
    return "\n".join(part for part in parts if part)


def render_confusables(font: TTFont, font_path: Path, samples: list[Sample]) -> str:
    width = 1760
    row_h = 58
    group_gap = 28
    y = 330
    body = []
    active_group = None
    grouped_count = 0
    inst = instance_font(font, 400)

    for sample in samples:
        if sample.category != active_group:
            if active_group is not None:
                y += group_gap
            active_group = sample.category
            body.append(f'<line x1="96" y1="{y - 34}" x2="1664" y2="{y - 34}" class="rule"/>')
            body.append(f'<text x="116" y="{y - 8}" class="sans category">{html.escape(sample.category)}</text>')
            body.append(f'<text x="116" y="{y + 12}" class="sans categoryCn">{html.escape(sample.category_cn)}</text>')
            y += 28
        shaped = glyphs_for_text(font, font_path, sample.text, enabled=True)
        raw = glyphs_for_text(font, font_path, sample.text, enabled=False)
        body.append(f'<text x="136" y="{y}" class="sans label">{html.escape(sample.text)}</text>')
        body.append(draw_run(inst, shaped, 430, y + 6, 31, "#f7f9fc"))
        body.append(draw_run(inst, raw, 1010, y + 6, 31, "#8a96a5", 0.68))
        y += row_h
        grouped_count += 1

    height = int(y + 120)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">Ligconsolata Next confusable QA</title>
  <desc id="desc">Confusable glyph and operator QA samples rendered from Ligconsolata Next outlines.</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#111318"/>
      <stop offset="1" stop-color="#20252c"/>
    </linearGradient>
    <style>
      .sans {{ font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
      .bright {{ fill: #f5f7fa; }}
      .muted {{ fill: #9aa7b5; }}
      .panel {{ fill: #171b21; stroke: #313945; stroke-width: 1; }}
      .rule {{ stroke: #2e3743; stroke-width: 1; }}
      .category {{ fill: #70dec0; font-size: 13px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; }}
      .categoryCn {{ fill: #6a7787; font-size: 11px; }}
      .label {{ fill: #cdd6df; font-size: 16px; font-weight: 700; }}
      .head {{ fill: #cdd6df; font-size: 17px; font-weight: 800; }}
      .chip {{ fill: #222832; stroke: #3b4553; stroke-width: 1; }}
    </style>
  </defs>
  <rect width="{width}" height="{height}" rx="30" fill="url(#bg)"/>
  <text x="96" y="96" class="sans bright" font-size="42" font-weight="760">Ligconsolata Next QA</text>
  <text x="98" y="128" class="sans muted" font-size="17">Confusable glyphs, ambiguous operators, and context guards.</text>
  <text x="98" y="150" class="sans muted" font-size="13">易混字符、容易误读的操作符和上下文保护样例。</text>
  <rect x="80" y="212" width="1600" height="{height - 300}" rx="16" class="panel"/>
  <text x="136" y="260" class="sans head">Source</text>
  <text x="430" y="260" class="sans head">Ligatures ON / 连字开启</text>
  <text x="1010" y="260" class="sans head">Raw ASCII / 原始字符</text>
  <line x1="120" y1="292" x2="1640" y2="292" class="rule"/>
  {chr(10).join(body)}
  <g transform="translate(96 {height - 76})">
    <rect class="chip" width="314" height="32" rx="16"/>
    <text x="18" y="21" class="sans muted" font-size="13">{grouped_count} QA samples / {grouped_count} 个 QA 样例</text>
  </g>
</svg>
'''


def render_matrix(font: TTFont, font_path: Path, samples: list[str]) -> str:
    width = 1760
    height = 1120
    weights = weight_values(font)
    sizes = [11, 13, 16, 20]
    preview = samples[:2] if len(samples) >= 2 else samples
    themes = [
        SvgTheme("Dark editor", "深色背景", "#171b21", "#f7f9fc", "#8a96a5", "#2e3743"),
        SvgTheme("Light editor", "浅色背景", "#f4f7fb", "#1c232d", "#5f6b78", "#c7d0dc"),
    ]
    body = []
    panel_w = 760
    panel_h = 650
    start_xs = [80, 920]
    start_y = 220
    cell_w = 136
    row_h = 112

    for theme, panel_x in zip(themes, start_xs):
        body.append(f'<rect x="{panel_x}" y="{start_y}" width="{panel_w}" height="{panel_h}" rx="16" fill="{theme.panel_fill}" stroke="{theme.rule}"/>')
        body.append(f'<text x="{panel_x + 34}" y="{start_y + 46}" class="sans" font-size="22" font-weight="800" fill="{theme.text_fill}">{theme.name}</text>')
        body.append(f'<text x="{panel_x + 34}" y="{start_y + 70}" class="sans" font-size="13" fill="{theme.muted_fill}">{theme.name_cn}</text>')
        table_x = panel_x + 118
        table_y = start_y + 122
        for col, size in enumerate(sizes):
            body.append(f'<text x="{table_x + col * cell_w}" y="{table_y - 28}" class="sans" font-size="13" font-weight="800" fill="{theme.muted_fill}">{size}px</text>')
        for row, weight in enumerate(weights):
            y = table_y + row * row_h
            body.append(f'<line x1="{panel_x + 34}" y1="{y - 42}" x2="{panel_x + panel_w - 34}" y2="{y - 42}" stroke="{theme.rule}"/>')
            body.append(f'<text x="{panel_x + 34}" y="{y + 4}" class="sans" font-size="14" font-weight="800" fill="{theme.muted_fill}">{weight}</text>')
            inst = instance_font(font, weight)
            for col, size in enumerate(sizes):
                cell_x = table_x + col * cell_w
                for line_index, text in enumerate(preview):
                    glyphs = glyphs_for_text(font, font_path, text, enabled=True)
                    body.append(draw_run(inst, glyphs, cell_x, y + line_index * (size + 10), size, theme.text_fill))

    footer_y = 920
    body.append(f'<rect x="80" y="{footer_y}" width="1600" height="130" rx="16" fill="#171b21" stroke="#313945"/>')
    body.append(f'<text x="116" y="{footer_y + 42}" class="sans" font-size="17" font-weight="800" fill="#cdd6df">Secondary samples / 补充样例</text>')
    inst = instance_font(font, 400)
    x = 116
    y = footer_y + 86
    for text in samples[2:]:
        glyphs = glyphs_for_text(font, font_path, text, enabled=True)
        body.append(draw_run(inst, glyphs, x, y, 18, "#f7f9fc"))
        x += 340
        if x > 1480:
            x = 116
            y += 38
    body.append(f'<text x="116" y="{height - 44}" class="sans" font-size="13" fill="#8a96a5">Italic QA is recorded as a future target because the current Ligconsolata Next build only ships an upright variable source. / 当前构建只有直立体，Italic 作为后续有斜体源码后的 QA 目标。</text>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">Ligconsolata Next size and weight QA matrix</title>
  <desc id="desc">Ligconsolata Next ligature samples across size, weight, and dark or light backgrounds.</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#111318"/>
      <stop offset="1" stop-color="#20252c"/>
    </linearGradient>
    <style>
      .sans {{ font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
      .bright {{ fill: #f5f7fa; }}
      .muted {{ fill: #9aa7b5; }}
    </style>
  </defs>
  <rect width="{width}" height="{height}" rx="30" fill="url(#bg)"/>
  <text x="96" y="96" class="sans bright" font-size="42" font-weight="760">Size And Weight QA</text>
  <text x="98" y="128" class="sans muted" font-size="17">The same ligature samples across variable weights, editor sizes, and light or dark themes.</text>
  <text x="98" y="150" class="sans muted" font-size="13">同一组连字样例在不同字重、字号、深浅背景下的实际轮廓检查。</text>
  {chr(10).join(body)}
</svg>
'''


def main() -> None:
    args = parse_args()
    font_path = resolve_font(args.font)
    font = TTFont(font_path)
    confusable_samples = read_grouped_samples(args.confusable_samples)
    matrix_samples = read_plain_samples(args.matrix_samples)
    args.confusable_output.parent.mkdir(parents=True, exist_ok=True)
    args.confusable_output.write_text(render_confusables(font, font_path, confusable_samples), encoding="utf-8")
    args.matrix_output.parent.mkdir(parents=True, exist_ok=True)
    args.matrix_output.write_text(render_matrix(font, font_path, matrix_samples), encoding="utf-8")
    print(args.confusable_output)
    print(args.matrix_output)


if __name__ == "__main__":
    main()
