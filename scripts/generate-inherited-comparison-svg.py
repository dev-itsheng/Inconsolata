#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "sources" / "Inconsolata.glyphs"
DEFAULT_LEGACY_FONT = ROOT / "fonts" / "variable" / "Inconsolata[wdth,wght].ttf"
DEFAULT_NEXT_FONT = Path("/tmp/ligconsolata-next-inherited/LigconsolataNext[wdth,wght].ttf")
DEFAULT_SAMPLES = ROOT / "documentation" / "inherited-ligature-comparison-samples.txt"
DEFAULT_OUTPUT = ROOT / "documentation" / "img" / "ligconsolata-next-inherited-comparison.svg"

LEGACY_FEATURES = "liga=0,dlig=1,calt=0"
NEXT_FEATURES = "liga=1,dlig=1,calt=1"

WIDTH = 1500
PANEL_X = 72
PANEL_Y = 214
PANEL_WIDTH = 1360
TABLE_LEFT = PANEL_X + 42
GRID_RIGHT = PANEL_X + PANEL_WIDTH - 42
SOURCE_X = TABLE_LEFT + 26
LEGACY_X = PANEL_X + 438
NEXT_X = PANEL_X + 892
SCALE = 0.052
ROW_GAP = 54
GROUP_TOP_GAP = 42
GROUP_CONTENT_GAP = 54


@dataclass(frozen=True)
class Sample:
    category: str
    text: str
    number: int


@dataclass(frozen=True)
class FontRun:
    font: TTFont
    glyphs: list[str]
    width: int


@dataclass(frozen=True)
class PreparedSample:
    sample: Sample
    legacy: FontRun
    current: FontRun


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a real-outline SVG comparing inherited Inconsolata dlig ligatures with Ligconsolata Next."
    )
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="Glyphs source used when --build is set.")
    parser.add_argument("--legacy-font", type=Path, default=DEFAULT_LEGACY_FONT, help="Upstream Inconsolata baseline font.")
    parser.add_argument("--next-font", type=Path, default=DEFAULT_NEXT_FONT, help="Temporary Ligconsolata Next build.")
    parser.add_argument("--samples", type=Path, default=DEFAULT_SAMPLES, help="Grouped sample text file.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="SVG output path.")
    parser.add_argument("--build", action="store_true", help="Build a fresh Ligconsolata Next font before generating SVG.")
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
    category = "Inherited"
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


def hb_shape(font_path: Path, text: str, features: str) -> list[str]:
    hb_shape_command = shutil.which("hb-shape") or "/opt/homebrew/bin/hb-shape"
    if not Path(hb_shape_command).exists():
        raise FileNotFoundError("hb-shape is required to generate a real shaping comparison.")
    result = subprocess.run(
        [hb_shape_command, str(font_path), text, f"--features={features}"],
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


def raw_glyphs(font: TTFont, text: str) -> list[str]:
    cmap = font.getBestCmap()
    glyphs = []
    for char in text:
        glyph_name = cmap.get(ord(char))
        if glyph_name is None:
            raise KeyError(f"Missing glyph for character {char!r}")
        glyphs.append(glyph_name)
    return glyphs


def advance_width(font: TTFont, glyphs: list[str]) -> int:
    hmtx = font["hmtx"].metrics
    return sum(hmtx[glyph_name][0] for glyph_name in glyphs)


def prepare_run(font: TTFont, font_path: Path, text: str, features: str) -> FontRun:
    shaped = hb_shape(font_path, text, features)
    raw_width = advance_width(font, raw_glyphs(font, text))
    shaped_width = advance_width(font, shaped)
    if shaped_width != raw_width:
        raise ValueError(f"Width mismatch for {text!r} in {font_path}: raw={raw_width}, shaped={shaped_width}")
    return FontRun(font=font, glyphs=shaped, width=shaped_width)


def grouped(samples: list[PreparedSample]) -> list[tuple[str, list[PreparedSample]]]:
    groups: list[tuple[str, list[PreparedSample]]] = []
    for sample in samples:
        if not groups or groups[-1][0] != sample.sample.category:
            groups.append((sample.sample.category, []))
        groups[-1][1].append(sample)
    return groups


def safe_comment(text: str) -> str:
    comment = html.escape(text, quote=False)
    while "--" in comment:
        comment = comment.replace("--", "- -")
    if comment.endswith("-"):
        comment += " "
    return comment


def path_element(font: TTFont, glyph_name: str, x: float, baseline: float, fill: str, opacity: float) -> str:
    glyph_set = font.getGlyphSet()
    pen = SVGPathPen(glyph_set)
    glyph_set[glyph_name].draw(pen)
    commands = pen.getCommands()
    if not commands:
        return ""
    return (
        f'<path d="{html.escape(commands)}" fill="{fill}" opacity="{opacity:.2f}" '
        f'transform="translate({x:.2f} {baseline:.2f}) scale({SCALE:.5f} {-SCALE:.5f})"/>'
    )


def draw_run(run: FontRun, x: float, baseline: float, fill: str, opacity: float) -> str:
    hmtx = run.font["hmtx"].metrics
    parts = []
    cursor = x
    for glyph_name in run.glyphs:
        parts.append(path_element(run.font, glyph_name, cursor, baseline, fill, opacity))
        cursor += hmtx[glyph_name][0] * SCALE
    return "\n".join(part for part in parts if part)


def render_rows(samples: list[PreparedSample]) -> tuple[str, float]:
    parts = []
    cursor_y = PANEL_Y + 164
    for category, group_samples in grouped(samples):
        cursor_y += GROUP_TOP_GAP
        parts.append(f'  <line x1="{TABLE_LEFT}" y1="{cursor_y}" x2="{GRID_RIGHT}" y2="{cursor_y}" class="rule"/>')
        parts.append(
            f'  <text x="{SOURCE_X}" y="{cursor_y - 12}" class="sans category" font-size="14" font-weight="800">{html.escape(category)}</text>'
        )
        cursor_y += GROUP_CONTENT_GAP
        for item in group_samples:
            source = html.escape(item.sample.text)
            source_width = max(item.legacy.width, item.current.width)
            parts.append(f"  <!-- {safe_comment(item.sample.text)} -->")
            parts.append(
                f'  <text x="{SOURCE_X}" y="{cursor_y - 3}" class="sans rowIndex" font-size="13">{item.sample.number:02d}</text>'
            )
            parts.append(f'  <text x="{SOURCE_X + 38}" y="{cursor_y - 3}" class="mono source" font-size="20">{source}</text>')
            parts.append(draw_run(item.legacy, LEGACY_X, cursor_y, "#8d99a8", 0.70))
            parts.append(draw_run(item.current, NEXT_X, cursor_y, "#f7f9fc", 1.00))
            measure_width = source_width * SCALE
            measure_y = cursor_y + 17
            parts.append(
                f'  <line x1="{LEGACY_X}" y1="{measure_y}" x2="{LEGACY_X + measure_width:.1f}" y2="{measure_y}" class="measure legacyMeasure"/>'
            )
            parts.append(
                f'  <line x1="{NEXT_X}" y1="{measure_y}" x2="{NEXT_X + measure_width:.1f}" y2="{measure_y}" class="measure nextMeasure"/>'
            )
            cursor_y += ROW_GAP
    return "\n".join(parts), cursor_y


def render_svg(rows: str, sample_count: int, end_y: float) -> str:
    panel_height = end_y - PANEL_Y + 64
    height = int(PANEL_Y + panel_height + 104)
    shadow_width = WIDTH - 108
    chips_y = PANEL_Y + panel_height + 36
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" role="img" aria-labelledby="title desc">
  <title id="title">Ligconsolata Next Inherited Ligature Comparison</title>
  <desc id="desc">A real font outline comparison of upstream Inconsolata dlig ligatures and the current Ligconsolata Next shaping result.</desc>
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
      .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
      .muted {{ fill: #9aa7b5; }}
      .soft {{ fill: #cdd6df; }}
      .bright {{ fill: #f5f7fa; }}
      .accent {{ fill: #5ed6af; }}
      .category {{ fill: #70dec0; letter-spacing: .06em; }}
      .source {{ fill: #b7c1cd; }}
      .rowIndex {{ fill: #667487; font-weight: 800; }}
      .panel {{ fill: #171b21; stroke: #313945; stroke-width: 1; }}
      .chip {{ fill: #222832; stroke: #3b4553; stroke-width: 1; }}
      .rule {{ stroke: #344050; stroke-width: 1; }}
      .measure {{ stroke-width: 1; stroke-dasharray: 4 5; opacity: .42; }}
      .legacyMeasure {{ stroke: #5e6978; }}
      .nextMeasure {{ stroke: #8fb8ff; }}
    </style>
  </defs>

  <rect width="{WIDTH}" height="{height}" rx="30" fill="url(#bg)"/>
  <path d="M0 {height - 154} C260 {height - 238} 470 {height - 108} 704 {height - 198} C930 {height - 284} 1140 {height - 228} {WIDTH} {height - 318} L{WIDTH} {height} L0 {height} Z" fill="#15191f" opacity=".72"/>
  <rect x="54" y="42" width="{shadow_width}" height="{height - 84}" rx="24" fill="#11151b" opacity=".78" filter="url(#softShadow)"/>

  <text x="96" y="96" class="sans bright" font-size="42" font-weight="760">Inherited Ligatures</text>
  <text x="98" y="128" class="sans muted" font-size="17">Legacy Inconsolata dlig outlines versus current Ligconsolata Next shaping.</text>
  <text x="98" y="150" class="sans muted" font-size="13">左侧是上游 Inconsolata 原有 dlig，右侧是当前 Ligconsolata Next；用于检查 `=&gt;` 等继承连字是否漂移。</text>
  <rect x="98" y="170" width="360" height="34" rx="17" fill="url(#accent)" opacity=".95"/>
  <text x="118" y="192" class="sans" font-size="14" font-weight="800" fill="#0c1217">Real outlines, same source / 真实轮廓，同一源码</text>

  <rect x="{PANEL_X}" y="{PANEL_Y}" width="{PANEL_WIDTH}" height="{panel_height:.0f}" rx="16" class="panel"/>
  <text x="{SOURCE_X}" y="{PANEL_Y + 44}" class="sans soft" font-size="17" font-weight="800">Source</text>
  <text x="{SOURCE_X}" y="{PANEL_Y + 68}" class="sans muted" font-size="13">same text / 同一文本</text>
  <text x="{LEGACY_X}" y="{PANEL_Y + 44}" class="sans soft" font-size="17" font-weight="800">Legacy Inconsolata</text>
  <text x="{LEGACY_X}" y="{PANEL_Y + 68}" class="sans muted" font-size="13">dlig on, liga/calt off / 仅开 dlig</text>
  <text x="{NEXT_X}" y="{PANEL_Y + 44}" class="sans accent" font-size="17" font-weight="800">Ligconsolata Next</text>
  <text x="{NEXT_X}" y="{PANEL_Y + 68}" class="sans muted" font-size="13">liga + dlig + calt on / 当前默认链路</text>

{rows}

  <g transform="translate(96 {chips_y:.0f})">
    <rect class="chip" width="318" height="32" rx="16"/>
    <text x="18" y="21" class="sans soft" font-size="13">{sample_count} samples / {sample_count} 个样例</text>
    <rect x="336" class="chip" width="360" height="32" rx="16"/>
    <text x="354" y="21" class="sans soft" font-size="13">Baseline: Inconsolata dlig / 基准 dlig</text>
    <rect x="714" class="chip" width="408" height="32" rx="16"/>
    <text x="732" y="21" class="sans soft" font-size="13">No Unicode substitutes / 不使用替代符号</text>
  </g>
</svg>
'''


def main() -> None:
    args = parse_args()
    if args.build or not args.next_font.exists():
        build_font(args.source, args.next_font)
    if not args.legacy_font.exists():
        raise FileNotFoundError(f"Legacy baseline font not found: {args.legacy_font}")
    if not args.next_font.exists():
        raise FileNotFoundError(f"Ligconsolata Next font not found: {args.next_font}")

    samples = read_samples(args.samples)
    legacy_font = TTFont(args.legacy_font)
    next_font = TTFont(args.next_font)
    prepared = [
        PreparedSample(
            sample=sample,
            legacy=prepare_run(legacy_font, args.legacy_font, sample.text, LEGACY_FEATURES),
            current=prepare_run(next_font, args.next_font, sample.text, NEXT_FEATURES),
        )
        for sample in samples
    ]
    rows, end_y = render_rows(prepared)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_svg(rows, len(samples), end_y), encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
