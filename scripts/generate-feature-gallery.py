#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import quote

from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FONT = ROOT / "documentation" / "demo" / "fonts" / "LigconsolataNext[wdth,wght].ttf"
DEFAULT_OUTPUT = ROOT / "documentation" / "ligconsolata-next-feature-gallery.md"
DEFAULT_IMAGE_DIR = ROOT / "documentation" / "img" / "features"
DEFAULT_FEATURES = "liga=1,dlig=0,calt=1"


@dataclass(frozen=True)
class FeaturePanel:
    slug: str
    title: str
    title_cn: str
    tags: tuple[str, ...]
    summary: str
    summary_cn: str
    samples: tuple[str, ...]
    notes: tuple[str, ...] = field(default_factory=tuple)
    notes_cn: tuple[str, ...] = field(default_factory=tuple)
    caption: str | None = None
    caption_cn: str | None = None
    features: str = DEFAULT_FEATURES
    badge: str = "liga + calt default / 默认编辑器路径"


PANELS = [
    FeaturePanel(
        slug="01-core-equality-comparison",
        title="Core Equality And Comparison",
        title_cn="核心相等与比较",
        tags=("liga", "calt"),
        summary=(
            "Inherited comparison ligatures are exposed on the default editor path, while "
            "`==` / `!=` are redrawn as two-bar forms and `===` / `!==` stay visibly three-bar."
        ),
        summary_cn="继承比较符进入默认编辑器路径；双横线和三横线保持清楚区分。",
        samples=(
            "a != b",
            "a !== b",
            "a == b",
            "a === b",
            "value <= max",
            "value >= min",
            "left <=> right",
        ),
        notes=(
            "`<=` and `>=` are comparison glyphs, not arrow glyphs.",
            "`==` / `!=` stay two-bar; `===` / `!==` stay three-bar.",
        ),
        notes_cn=(
            "`<=` 和 `>=` 是比较符，不按箭头逻辑处理。",
            "`==` / `!=` 保持两条横线；`===` / `!==` 保持三条横线。",
        ),
    ),
    FeaturePanel(
        slug="02-common-operators",
        title="Common Operators",
        title_cn="常用操作符",
        tags=("liga",),
        summary=(
            "Everyday ASCII operators are compacted without changing advance width. Comment "
            "prefixes are shown together with URL guards so the boundary is visible."
        ),
        summary_cn="常用 ASCII 操作符在不改变宽度的前提下压缩；注释和 URL 边界一起展示。",
        samples=(
            "a <-> b",
            "a --> b",
            "a <-- b",
            "a ==> b",
            "a <== b",
            "items ...",
            "a <> b",
            "ns :: value",
            "key := value",
            "a && b",
            "a || b",
            "i ++",
            "i --",
            "a ** b",
            "// comment",
            "https://example.com",
            "/* block",
            "block */",
            "a ?? b",
            "a ?. b",
        ),
        notes=(
            "`//` / `///` only ligate as comment prefixes followed by a normal space.",
            "`/*` requires a following space, and `*/` requires a preceding space.",
            "URLs, paths, and glob patterns keep raw slash glyphs.",
        ),
        notes_cn=(
            "`//` 和 `///` 只有后面跟普通空格、像注释前缀时才连写。",
            "`/*` 需要后接空格，`*/` 需要前接空格。",
            "URL、路径和 glob 模式里的斜线保持原始字形。",
        ),
    ),
    FeaturePanel(
        slug="03-fira-style-fixed-operators",
        title="Fira Code Inspired Fixed Operators",
        title_cn="Fira Code 灵感固定操作符",
        tags=("liga",),
        summary=(
            "A broad fixed-operator batch follows Fira Code's coverage as a behavior reference, "
            "but all outlines are assembled from the Inconsolata family."
        ),
        summary_cn="这一组参考 Fira Code 的覆盖面，但字形轮廓仍从 Inconsolata 家族推导。",
        samples=(
            "a |||> b",
            "a <||| b",
            "html <!--",
            "a ~~> b",
            "a *** b",
            "a ||| b",
            "a ||> b",
            "scope :::",
            "scope ::=",
            "bang !!.",
            "a >>> b",
            "a <~~ b",
            "a <~> b",
            "a <*> b",
            "a <|| b",
            "a <|> b",
            "a <$> b",
            "a <<< b",
            "a <+> b",
            "tag </>",
            "hash #_(x)",
            "range ..=",
            "range ..<",
            "a +++ b",
            "query ?= value",
        ),
        notes=(
            "`www` is intentionally not merged so URLs, domains, and prose remain raw.",
            "This is a default-friendly subset, not a claim that every Fira Code variant is copied.",
        ),
        notes_cn=(
            "`www` 有意不合并，避免 URL、域名和普通文本变得难扫读。",
            "这里是适合默认启用的子集，不表示完整复制 Fira Code 的所有变体。",
        ),
    ),
    FeaturePanel(
        slug="04-fira-style-pairs",
        title="Fira Code Inspired Pairs",
        title_cn="Fira Code 灵感双字符",
        tags=("liga",),
        summary=(
            "The shorter fixed pairs cover pipes, brackets, hash-prefixed operators, point forms, "
            "question forms, and escaped slash pairs."
        ),
        summary_cn="较短的固定组合覆盖管道、括号、井号前缀、点号、问号和转义斜线组合。",
        samples=(
            "a ^= b",
            "a ~~ b",
            "a ~@ b",
            "a ~> b",
            "a ~- b",
            "a *> b",
            "path \\/ item",
            "a |} b",
            "a |] b",
            "a |> b",
            "a {| b",
            "a [| b",
            "a ]# b",
            "a $> b",
            "a !! b",
            "a >> b",
            "a -~ b",
            "a <~ b",
            "a <* b",
            "a <| b",
            "a <$ b",
            "a << b",
            "a <+ b",
            "tag </",
            "hash #{",
            "hash #[",
            "hash #:",
            "hash #=",
            "hash #!",
            "hash #(",
            "hash #?",
            "hash #_",
            "a %% b",
            "range ..",
            "maybe .?",
            "a +> b",
            "a ?= b",
            "a ;; b",
            "path \\\\ name",
            "path /\\ name",
            "tag />",
        ),
        notes=("Hash-prefixed operators such as `#{` / `#[` stay separate from Markdown heading badges.",),
        notes_cn=("`#{` / `#[` 这类井号操作符和 Markdown 标题徽标分开处理。",),
    ),
    FeaturePanel(
        slug="05-calt-inspired-fixed-forms",
        title="Calt Inspired Fixed Forms",
        title_cn="calt 灵感固定组合",
        tags=("liga", "dlig"),
        summary=(
            "Some Fira Code contextual forms can be represented safely as fixed substitutions in "
            "Ligconsolata Next before porting the full external state machine."
        ),
        summary_cn="一部分 Fira Code 上下文形态可以先安全落成固定替换，不需要搬完整状态机。",
        samples=(
            "snake __ name",
            "snake ___ name",
            "snake ____ name",
            "snake _____ name",
            "snake ______ name",
            "a =/= b",
            "a =!= b",
            "a =:= b",
            "a =~ b",
            "a !~ b",
            "a /== b",
            "a /= b",
            "obj .= x",
            "a .- b",
            "a :- b",
            "list []",
            "a ->> b",
            "a <<- b",
            "a =>> b",
            "a =<< b",
        ),
        notes=("Short underscore runs through six cells use fixed glyphs; longer runs use contextual extension.",),
        notes_cn=("最多六格的下划线 run 使用固定字形；更长的 run 交给上下文延展。",),
    ),
    FeaturePanel(
        slug="06-contextual-long-arrows",
        title="Contextual Long Arrows",
        title_cn="上下文长箭头",
        tags=("calt",),
        summary=(
            "Long `-` and `=` arrows use start / middle / end sequence glyphs, so the arrow body "
            "can grow naturally instead of relying on a finite hard-coded list."
        ),
        summary_cn="长 `-` / `=` 箭头用起始、延展和结尾片段拼接，可以自然变长。",
        samples=(
            "a ----> b",
            "a <---- b",
            "a ====> b",
            "a <==== b",
            "a <---> b",
            "a <===> b",
            "a ------> b",
            "a <------ b",
            "a ======> b",
            "a <====== b",
            "a >--- b",
            "a ---< b",
            "a >=== b",
            "a ===< b",
            "a >----- b",
            "a -----< b",
        ),
        notes=(
            "Short fixed ligatures such as `->`, `=>`, `-->`, and `==>` still win where appropriate.",
            "`<=` / `>=` are not treated as arrows.",
        ),
        notes_cn=(
            "`->`、`=>`、`-->`、`==>` 等短固定连字仍优先生效。",
            "`<=` / `>=` 不会被当成箭头处理。",
        ),
    ),
    FeaturePanel(
        slug="07-endpoints-and-markers",
        title="Endpoint And Marker Runs",
        title_cn="端点与标记运行符",
        tags=("liga", "calt"),
        summary=(
            "Pipe, slash, colon, and exclamation marker batches cover the safe endpoint cases that "
            "do not collide with URL, comment, or regex readability."
        ),
        summary_cn="管道、斜线、冒号和感叹号端点只覆盖安全场景，避开 URL、注释和正则误伤。",
        samples=(
            "a >-- b",
            "a --< b",
            "a |-- b",
            "a --| b",
            "a >== b",
            "a ==< b",
            "a |== b",
            "a ==| b",
            "a ==/ b",
            "a >>- b",
            "a >- b",
            "a -< b",
            "a ||- b",
            "a -|| b",
            "a |-> b",
            "a <-| b",
            "a |=> b",
            "a <=| b",
            "a |---> b",
            "a <---| b",
            "a |===> b",
            "a <===| b",
            "a /===> b",
            "a <===/ b",
            "a ===/=== b",
            "a ==:= b",
            "a ==!= b",
        ),
        notes=("Double-slash endpoint machinery is intentionally not default-migrated yet.",),
        notes_cn=("双斜线端点机制暂时不迁入默认路径。",),
    ),
    FeaturePanel(
        slug="08-contextual-alignment",
        title="Contextual Alignment",
        title_cn="上下文视觉对齐",
        tags=("calt",),
        summary=(
            "Small `.center`, `.lc`, and `.uc` alternates align punctuation with neighboring glyphs "
            "without pretending these are new source-level ligatures."
        ),
        summary_cn="`.center`、`.lc`、`.uc` 只做视觉对齐，不把源码伪装成新的操作符。",
        samples=(
            "a <: b",
            "a :> b",
            "a <:> b",
            "a >:< b",
            "var-name",
            "a+b",
            "*ptr",
            "CONST:VALUE",
            "A:b",
            "a:B",
        ),
        notes=(
            "Mixed-height contexts such as `A:b` and `a:B` stay raw.",
            "`:<` / `:>` use visual alternates, not `.dlig` ligature glyphs.",
        ),
        notes_cn=(
            "`A:b`、`a:B` 这种混合高度上下文保持原始字形。",
            "`:<` / `:>` 使用视觉变体，不是新的 `.dlig` 连字。",
        ),
    ),
    FeaturePanel(
        slug="09-numeric-contexts",
        title="Numeric Contexts",
        title_cn="数字上下文",
        tags=("calt",),
        summary=(
            "The lowercase `x` becomes an Inconsolata-derived multiply glyph only in hexadecimal "
            "and dimension-like numeric contexts."
        ),
        summary_cn="小写 `x` 只在十六进制和尺寸数字上下文里变成乘号风格字形。",
        samples=(
            "hex 0xFF",
            "hex 0xff",
            "hex 0x10",
            "size 800x600",
            "size 1920x1080",
            "raw xray axb 0xG",
            "raw x86 0XFF 800X600",
        ),
        notes=("Uppercase `X`, ordinary words, and invalid hex-like text stay raw.",),
        notes_cn=("大写 `X`、普通单词和无效十六进制样式保持原始字形。",),
    ),
    FeaturePanel(
        slug="10-markdown-hash-runs",
        title="Markdown Hash Runs",
        title_cn="Markdown 井号运行符",
        tags=("calt",),
        summary=(
            "`## title` through `###### title` get countable number badges; seven or more hashes "
            "connect as an unnumbered rail sequence."
        ),
        summary_cn="`## title` 到 `###### title` 显示可数徽标；七个及以上井号连成无编号长线。",
        samples=(
            "\\# title",
            "\\## title",
            "\\### title",
            "\\#### title",
            "\\##### title",
            "\\###### title",
            "\\####### title",
            "\\######## title",
            "\\##title",
            "a ## b",
            "\\#include <stdio.h>",
        ),
        notes=(
            "Badges only cover Markdown heading levels 2 through 6.",
            "Seven or more hashes connect without a number; they are treated like long runs, not heading levels.",
        ),
        notes_cn=(
            "数字徽标只覆盖 Markdown 二级到六级标题。",
            "七个及以上井号只连成长 run，不再标数字，也不伪装成标题层级。",
        ),
        badge="calt hash logic / Markdown 井号规则",
    ),
    FeaturePanel(
        slug="11-guards-slashes-logic",
        title="Slash And Logic Guards",
        title_cn="斜线与逻辑符号保护",
        tags=("liga", "calt"),
        summary=(
            "Slash-related ligatures are deliberately guarded so comment prefixes and logical "
            "operators improve, while URLs, paths, and regexes remain readable."
        ),
        summary_cn="斜线相关连字都带保护：改善注释和逻辑符号，同时让 URL、路径、正则保持可读。",
        samples=(
            "// comment",
            "/// reference",
            "/* block */",
            "https://example.com",
            "file:///tmp/font",
            "glob **/*.{ts,tsx}",
            "glob !**/composables/**/*.ts",
            "a /\\ b",
            "regex /\\d/",
            "x \\/ y",
            "path \\/tmp",
        ),
        notes=(
            "`//` / `///` require a following normal space.",
            "`/*` / `*/` are block-comment boundaries, not glob-star helpers.",
            "`/\\` / `\\/` require ordinary spaces on both sides.",
        ),
        notes_cn=(
            "`//` / `///` 必须后接普通空格才触发。",
            "`/*` / `*/` 是块注释边界，不是 glob-star 辅助符号。",
            "`/\\` / `\\/` 必须左右都有普通空格才触发。",
        ),
    ),
    FeaturePanel(
        slug="12-runs-and-dividers",
        title="Runs And Dividers",
        title_cn="运行符与分割线",
        tags=("liga", "calt"),
        summary=(
            "Long underscore, equal, and hyphen runs are shaped for code comments and separators "
            "while preserving short operator meaning."
        ),
        summary_cn="长下划线、等号和横线 run 用于注释分割线，同时保留短操作符的语义。",
        samples=(
            "snake ______ name",
            "snake _______ name",
            "// ====",
            "// =====",
            "// ----",
            "// -----",
            "i --",
            "a ----> b",
        ),
        notes=(
            "`--` keeps a visible two-minus feel; `----` and longer divider samples can connect.",
            "Long underscore runs use sequence glyphs after the fixed six-cell range.",
        ),
        notes_cn=(
            "`--` 保留两个减号的观感；`----` 和更长分割线可以连起来。",
            "超过六格的下划线 run 使用 sequence glyph 延展。",
        ),
    ),
    FeaturePanel(
        slug="13-cjk-dash-width",
        title="CJK Dash Width And Continuity",
        title_cn="中文破折号宽度与连续性",
        tags=("glyph width",),
        summary=(
            "This is not a GSUB ligature. U+2014 and U+2015 are widened to two Latin cells and "
            "drawn edge-to-edge for Chinese mixed typesetting."
        ),
        summary_cn="这不是 GSUB 连字，而是把 U+2014 和 U+2015 加宽到两个 Latin cell 并画到边缘。",
        samples=(
            "a——b",
            "dash —— ———",
            "path ― marker",
            "bar ――",
        ),
        notes=(
            "`endash` and `figuredash` stay one Latin cell wide.",
            "The fix works through glyph width and outline continuity, not an `emdash emdash` substitution.",
        ),
        notes_cn=(
            "`endash` 和 `figuredash` 仍保持一格宽。",
            "这个修正靠字宽和轮廓连续性，不靠 `emdash emdash` 替换。",
        ),
        badge="glyph width fix / 字宽修正",
    ),
    FeaturePanel(
        slug="14-calt-thin-backslash",
        title="Thin Backslash",
        title_cn="细反斜杠",
        tags=("calt",),
        summary=(
            "Raw backslashes switch to a thinner Inconsolata-derived outline on the default "
            "`calt` path, making escapes and regexes quieter without requiring an opt-in stylistic set."
        ),
        summary_cn="反斜杠在默认 `calt` 路径切换成更细的 Inconsolata 派生轮廓，弱化转义噪音。",
        samples=(
            "escape \\n \\t \\d",
            "path C:\\Users\\name",
            "regex /\\w+\\s?/",
            "logic a /\\ b",
        ),
        notes=(
            "This is handled by `calt`, so ordinary editor ligature toggles can reach it.",
            "This changes the backslash outline, not its color or opacity.",
        ),
        notes_cn=(
            "它由 `calt` 处理，普通编辑器的连写开关也能覆盖。",
            "它只改变反斜杠轮廓，不改变颜色或透明度。",
        ),
        badge="calt thin backslash / 默认细反斜杠",
    ),
]

IMAGE_SUMMARIES = {
    "01-core-equality-comparison": (
        "Default equality and comparison forms stay width-preserving and visually distinct.",
        "默认相等与比较符保持等宽，并清楚区分两横线和三横线。",
    ),
    "02-common-operators": (
        "Common operators compact safely while URL and comment boundaries stay visible.",
        "常用操作符安全压缩，同时保留 URL 和注释边界。",
    ),
    "03-fira-style-fixed-operators": (
        "Fira Code-inspired fixed coverage, redrawn from Inconsolata-family shapes.",
        "参考 Fira Code 的固定覆盖面，但轮廓来自 Inconsolata 家族。",
    ),
    "04-fira-style-pairs": (
        "Short fixed pairs cover pipes, brackets, hash operators, dots, and slashes.",
        "短固定组合覆盖管道、括号、井号操作符、点号和斜线。",
    ),
    "05-calt-inspired-fixed-forms": (
        "Low-risk contextual ideas are exposed as stable fixed substitutions.",
        "低风险上下文思路先落成稳定的固定替换。",
    ),
    "06-contextual-long-arrows": (
        "Long arrows grow with start, middle, and end sequence glyphs.",
        "长箭头用起始、延展和结尾片段自然变长。",
    ),
    "07-endpoints-and-markers": (
        "Endpoint and marker runs avoid URL, comment, and regex collisions.",
        "端点和标记运行符避开 URL、注释和正则误伤。",
    ),
    "08-contextual-alignment": (
        "Contextual alternates align punctuation without changing source meaning.",
        "上下文变体只做视觉对齐，不改变源码含义。",
    ),
    "09-numeric-contexts": (
        "The lowercase x becomes multiplication only in numeric contexts.",
        "小写 x 只在数字上下文里变成乘号风格。",
    ),
    "10-markdown-hash-runs": (
        "Markdown hashes get countable badges or unnumbered long rails.",
        "Markdown 井号显示可数徽标，长 run 则连成无编号横线。",
    ),
    "11-guards-slashes-logic": (
        "Slash ligatures improve comments and logic while protecting URLs and regexes.",
        "斜线连字改善注释和逻辑符号，同时保护 URL 和正则。",
    ),
    "12-runs-and-dividers": (
        "Long runs become cleaner dividers without hiding short operators.",
        "长 run 变成清爽分割线，同时不隐藏短操作符。",
    ),
    "13-cjk-dash-width": (
        "Chinese dash continuity is fixed through glyph width, not GSUB.",
        "中文破折号连续性通过字宽修正，不靠 GSUB。",
    ),
    "14-calt-thin-backslash": (
        "Thin backslash now lives on the default calt editor path.",
        "细反斜杠已经迁到默认 calt 编辑器路径。",
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate per-feature Ligconsolata Next SVGs and a gallery markdown file.")
    parser.add_argument("--font", type=Path, default=DEFAULT_FONT, help="Built Ligconsolata Next font.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Markdown output path.")
    parser.add_argument("--image-dir", type=Path, default=DEFAULT_IMAGE_DIR, help="Directory for generated feature SVGs.")
    parser.add_argument("--build", action="store_true", help="Build demo fonts before generating the gallery.")
    return parser.parse_args()


def load_update_module():
    script = ROOT / "scripts" / "update-ligature-glyphs.py"
    spec = importlib.util.spec_from_file_location("ligconsolata_update_ligatures", script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {script}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def maybe_build_font(font_path: Path, build: bool) -> None:
    if build or not font_path.exists():
        subprocess.run([sys.executable, str(ROOT / "scripts" / "build-demo-assets.py")], cwd=ROOT, check=True)


def sample_file_text(panel: FeaturePanel) -> str:
    lines = [
        f"# Generated sample file for {panel.title}.",
        "# Regenerate with scripts/generate-feature-gallery.py.",
        "",
        f"## {panel.title}",
        *panel.samples,
        "",
    ]
    return "\n".join(lines)


def render_panel_svg(panel: FeaturePanel, font_path: Path, image_dir: Path) -> Path:
    image_dir.mkdir(parents=True, exist_ok=True)
    output = image_dir / f"{panel.slug}.svg"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False) as fp:
        fp.write(sample_file_text(panel))
        sample_path = Path(fp.name)
    try:
        caption, caption_cn = IMAGE_SUMMARIES.get(panel.slug, (panel.caption or panel.summary, panel.caption_cn or panel.summary_cn))
        command = [
            sys.executable,
            str(ROOT / "scripts" / "generate-overview-svg.py"),
            "--font",
            str(font_path),
            "--samples",
            str(sample_path),
            "--output",
            str(output),
            "--title",
            panel.title,
            "--title-cn",
            panel.title_cn,
            "--subtitle",
            caption,
            "--subtitle-cn",
            caption_cn,
            "--badge",
            panel.badge,
            "--features",
            panel.features,
            "--hide-badge",
            "--hide-footer-chips",
            "--hide-category-labels",
        ]
        for index, note in enumerate(panel.notes):
            command.extend(["--note", note])
            if index < len(panel.notes_cn):
                command.extend(["--note-cn", panel.notes_cn[index]])
        subprocess.run(command, cwd=ROOT, check=True)
    finally:
        sample_path.unlink(missing_ok=True)
    return output


def code_block_lines(items: list[str], line_size: int = 8) -> str:
    lines = []
    for index in range(0, len(items), line_size):
        lines.append(" ".join(f"`{item}`" for item in items[index : index + line_size]))
    return "\n".join(lines)


def md_image_path(output: Path, image_path: Path) -> str:
    return image_path.relative_to(output.parent).as_posix()


def display_samples(panel: FeaturePanel) -> str:
    return "\n".join(sample.replace("\\#", "#") for sample in panel.samples)


def playground_path(panel: FeaturePanel) -> str:
    return "demo/index.html?sample=" + quote(display_samples(panel), safe="")


def built_feature_tags(font_path: Path) -> list[str]:
    font = TTFont(font_path)
    return sorted({record.FeatureTag for record in font["GSUB"].table.FeatureList.FeatureRecord})


def render_markdown(output: Path, image_paths: dict[str, Path], update_module, font_path: Path) -> str:
    ligature_sources = [ligature.source for ligature in update_module.LIGATURES]
    fixed_sources = [
        source
        for source in ligature_sources
        if source not in update_module.CONTEXTUAL_CALT_ONLY_LIGATURE_SOURCES
        and source not in update_module.CONTEXTUAL_SPACE_LIGATURE_SOURCES
        and source not in update_module.CONTEXTUAL_SPACE_AROUND_LIGATURE_SOURCES
        and source not in update_module.CONTEXTUAL_BLOCK_COMMENT_LIGATURE_SOURCES
    ]
    contextual_badges = [ligature.source for ligature in update_module.HASH_BADGE_LIGATURES]
    comment_prefix_sources = sorted(update_module.CONTEXTUAL_SPACE_LIGATURE_SOURCES)
    block_comment_sources = sorted(update_module.CONTEXTUAL_BLOCK_COMMENT_LIGATURE_SOURCES)
    logic_guard_sources = sorted(update_module.CONTEXTUAL_SPACE_AROUND_LIGATURE_SOURCES)
    sequence_glyphs = list(update_module.SEQ_GLYPHS)
    center_glyphs = list(update_module.CENTER_GLYPHS.keys())
    case_glyphs = list(update_module.CASE_GLYPHS.keys())
    context_glyphs = list(update_module.CONTEXT_GLYPHS.keys())
    style_glyphs = list(update_module.STYLE_GLYPHS.keys())
    feature_tags = built_feature_tags(font_path)

    parts = [
        "# Ligconsolata Next Feature Gallery",
        "",
        "This gallery is generated from the current Ligconsolata Next source and the local demo font. Each image renders the same sample text twice: the left side uses Ligconsolata Next shaping, and the right side keeps raw ASCII glyphs.",
        "",
        "这份图库由当前 Ligconsolata Next 源码和本地 demo 字体生成。每张图都会把同一段样例渲染两遍：左侧是 Ligconsolata Next 连字结果，右侧是原始 ASCII。",
        "",
        "Each feature image contains its own bilingual title, summary, and notes. The text below each image is kept for direct playground links and copyable samples only, so the same explanation is not repeated in two places.",
        "",
        "每张功能图内部都包含双语标题、摘要和说明。图片下方只保留可直接打开 Playground 的链接和可复制样例，避免同一段解释在图内外重复出现。",
        "",
        "## OpenType Feature Map",
        "",
        "| Feature | Role / 作用 | Notes / 说明 |",
        "| --- | --- | --- |",
        "| `liga` | Default fixed programming ligatures / 默认固定编程连字 | Most short operators and safe fixed forms are available here. / 多数短操作符和安全固定组合放在这里。 |",
        "| `calt` | Contextual behavior / 上下文行为 | Long arrows, hash runs, numeric `x`, punctuation alignment, guards, and thin backslash. / 长箭头、井号 run、数字 `x`、标点对齐、保护规则和细反斜杠放在这里。 |",
        "| `dlig` | Compatibility mirror / 兼容镜像 | Kept for Inconsolata / Ligconsolata history, but the default editor story is `liga + calt`. / 保留历史兼容；默认编辑器路径仍是 `liga + calt`。 |",
        "| glyph width fix | Non-GSUB punctuation fix / 非 GSUB 标点修正 | U+2014 `emdash` and U+2015 `horizontalbar` are widened for CJK dash continuity. / U+2014 和 U+2015 加宽以适配中文破折号连续性。 |",
        "",
        "The built font also contains inherited upstream typographic feature tags. They are present in the font, but they are not the main Ligconsolata Next coding-ligature gallery:",
        "",
        "构建产物里也包含上游继承的排版 feature tag。它们存在于字体中，但不是这份 Ligconsolata Next 编码连字图库的重点。",
        "",
        code_block_lines(feature_tags, line_size=10),
        "",
        "## Feature Panels",
        "",
    ]

    for panel in PANELS:
        parts.extend(
            [
                f"### {panel.title} / {panel.title_cn}",
                "",
                f"Tags: {', '.join(f'`{tag}`' for tag in panel.tags)}",
                "",
                f"![{panel.title}]({md_image_path(output, image_paths[panel.slug])})",
                "",
                f"Samples / 样例: [Open in playground / 在 Playground 打开]({playground_path(panel)})",
                "",
                "```text",
                display_samples(panel),
                "```",
                "",
            ]
        )
    parts.extend(
        [
            "## Complete Rule Inventory",
            "",
            f"`scripts/update-ligature-glyphs.py` currently maintains `{len(update_module.LIGATURES)}` generated ligature rules. The fixed/default-friendly source sequences are:",
            "",
            code_block_lines(fixed_sources),
            "",
            "Contextual Markdown badge sources:",
            "",
            code_block_lines(contextual_badges),
            "",
            "Comment-prefix guarded sources:",
            "",
            code_block_lines(comment_prefix_sources),
            "",
            "Block-comment guarded sources:",
            "",
            code_block_lines(block_comment_sources),
            "",
            "Space-around logic guard sources:",
            "",
            code_block_lines(logic_guard_sources),
            "",
            "Sequence/helper glyphs used by `calt`:",
            "",
            code_block_lines(sequence_glyphs, line_size=4),
            "",
            "Visual alternate glyphs generated for contextual behavior:",
            "",
            code_block_lines(center_glyphs + case_glyphs + context_glyphs + style_glyphs, line_size=6),
            "",
            "Zero-width spacer helper glyphs:",
            "",
            code_block_lines(list(update_module.SPACER_GLYPHS), line_size=4),
            "",
            "## Regeneration",
            "",
            "```sh",
            "python scripts/build-demo-assets.py",
            "python scripts/generate-feature-gallery.py",
            "```",
            "",
            "The generated SVGs live in `documentation/img/features/`.",
            "",
        ]
    )
    return "\n".join(parts)


def main() -> None:
    args = parse_args()
    maybe_build_font(args.font, args.build)
    if not args.font.exists():
        raise FileNotFoundError(args.font)

    args.image_dir.mkdir(parents=True, exist_ok=True)
    for stale_svg in args.image_dir.glob("*.svg"):
        stale_svg.unlink()

    image_paths = {}
    for panel in PANELS:
        image_paths[panel.slug] = render_panel_svg(panel, args.font, args.image_dir)

    update_module = load_update_module()
    args.output.write_text(render_markdown(args.output, image_paths, update_module, args.font), encoding="utf-8")
    print(args.output)
    for image_path in image_paths.values():
        print(image_path)


if __name__ == "__main__":
    main()
