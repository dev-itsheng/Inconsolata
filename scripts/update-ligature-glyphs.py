#!/usr/bin/env python3
from __future__ import annotations

import copy
import io
from dataclasses import dataclass
from pathlib import Path

import glyphsLib
from glyphsLib.classes import GSComponent, GSNode, GSPath
from glyphsLib.writer import Writer


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "sources" / "Inconsolata.glyphs"

CHAR_GLYPHS = {
    "!": "exclam",
    "&": "ampersand",
    "#": "numbersign",
    "$": "dollar",
    "%": "percent",
    "*": "asterisk",
    "+": "plus",
    "-": "hyphen",
    ".": "period",
    "/": "slash",
    "0": "zero",
    ":": "colon",
    ";": "semicolon",
    "<": "less",
    "=": "equal",
    ">": "greater",
    "?": "question",
    "@": "at",
    "[": "bracketleft",
    "\\": "backslash",
    "]": "bracketright",
    "^": "asciicircum",
    "_": "underscore",
    "(": "parenleft",
    "{": "braceleft",
    "|": "bar",
    "}": "braceright",
    "~": "asciitilde",
    "w": "w",
}


@dataclass(frozen=True)
class Ligature:
    source: str
    glyph: str
    generator: str | None = None


def glyph_name_for_source(source: str) -> str:
    return "_".join(CHAR_GLYPHS[char] for char in source) + ".dlig"


def compact_ligature(source: str) -> Ligature:
    return Ligature(source, glyph_name_for_source(source), "compact_components")


FIRA_CODE_COMPAT_SOURCES = [
    "|||>",
    "<|||",
    "<!--",
    "~~>",
    "***",
    "|||",
    "||>",
    ":::",
    "::=",
    "!!.",
    ">>>",
    "<~~",
    "<~>",
    "<*>",
    "<||",
    "<|>",
    "<$>",
    "<<<",
    "<+>",
    "</>",
    "#_(",
    "..=",
    "..<",
    "+++",
    "///",
    "www",
    "^=",
    "~~",
    "~@",
    "~>",
    "~-",
    "*>",
    "\\/",
    "|}",
    "|]",
    "|>",
    "{|",
    "[|",
    "]#",
    "$>",
    "!!",
    ">>",
    "-~",
    "<~",
    "<*",
    "<|",
    "<$",
    "<<",
    "<+",
    "</",
    "#{",
    "#[",
    "#:",
    "#=",
    "#!",
    "#(",
    "#?",
    "#_",
    "%%",
    "..",
    ".?",
    "+>",
    "?=",
    ";;",
    "\\\\",
    "/\\",
    "/>",
]


FIRA_CODE_CALT_FIXED_LIGATURES = [
    Ligature("########", "numbersign_run8.dlig", "compact_components"),
    Ligature("#######", "numbersign_run7.dlig", "compact_components"),
    Ligature("######", "numbersign_run6.dlig", "compact_components"),
    Ligature("#####", "numbersign_run5.dlig", "compact_components"),
    Ligature("####", "numbersign_run4.dlig", "compact_components"),
    Ligature("###", "numbersign_run3.dlig", "compact_components"),
    Ligature("##", "numbersign_run2.dlig", "compact_components"),
    Ligature("______", "underscore_run6.dlig", "underscore_run"),
    Ligature("_____", "underscore_run5.dlig", "underscore_run"),
    Ligature("____", "underscore_run4.dlig", "underscore_run"),
    Ligature("___", "underscore_run3.dlig", "underscore_run"),
    Ligature("__", "underscore_run2.dlig", "underscore_run"),
    Ligature("=/=", glyph_name_for_source("=/="), "compact_components"),
    Ligature("=!=", glyph_name_for_source("=!="), "compact_components"),
    Ligature("=:=", glyph_name_for_source("=:="), "compact_components"),
    Ligature("=~", glyph_name_for_source("=~"), "compact_components"),
    Ligature("!~", glyph_name_for_source("!~"), "compact_components"),
    Ligature("/==", glyph_name_for_source("/=="), "compact_components"),
    Ligature("/=", glyph_name_for_source("/="), "compact_components"),
    Ligature(".=", glyph_name_for_source(".="), "compact_components"),
    Ligature(".-", glyph_name_for_source(".-"), "compact_components"),
    Ligature(":-", glyph_name_for_source(":-"), "compact_components"),
    Ligature("[]", glyph_name_for_source("[]"), "compact_components"),
    Ligature("->>", glyph_name_for_source("->>"), "compact_components"),
    Ligature("<<-", glyph_name_for_source("<<-"), "compact_components"),
    Ligature("=>>", glyph_name_for_source("=>>"), "compact_components"),
    Ligature("=<<", glyph_name_for_source("=<<"), "compact_components"),
    Ligature(">--", glyph_name_for_source(">--"), "compact_components"),
    Ligature("--<", glyph_name_for_source("--<"), "compact_components"),
    Ligature("|--", glyph_name_for_source("|--"), "compact_components"),
    Ligature("--|", glyph_name_for_source("--|"), "compact_components"),
    Ligature(">==", glyph_name_for_source(">=="), "compact_components"),
    Ligature("==<", glyph_name_for_source("==<"), "compact_components"),
    Ligature("|==", glyph_name_for_source("|=="), "compact_components"),
    Ligature("==|", glyph_name_for_source("==|"), "compact_components"),
    Ligature("==/", glyph_name_for_source("==/"), "compact_components"),
    Ligature(">>-", glyph_name_for_source(">>-"), "compact_components"),
    Ligature(">-", glyph_name_for_source(">-"), "compact_components"),
    Ligature("-<", glyph_name_for_source("-<"), "compact_components"),
    Ligature("||-", glyph_name_for_source("||-"), "compact_components"),
    Ligature("-||", glyph_name_for_source("-||"), "compact_components"),
    Ligature("|->", glyph_name_for_source("|->"), "compact_components"),
    Ligature("<-|", glyph_name_for_source("<-|"), "compact_components"),
    Ligature("|=>", glyph_name_for_source("|=>"), "compact_components"),
    Ligature("<=|", glyph_name_for_source("<=|"), "compact_components"),
    Ligature("-|", glyph_name_for_source("-|"), "compact_components"),
    Ligature("|-", glyph_name_for_source("|-"), "compact_components"),
]


OBSOLETE_GENERATED_GLYPHS = [
    glyph_name_for_source("######"),
    glyph_name_for_source("#####"),
    glyph_name_for_source("####"),
    glyph_name_for_source("###"),
    glyph_name_for_source("##"),
    glyph_name_for_source("____"),
    glyph_name_for_source("___"),
    glyph_name_for_source("__"),
]


LIGATURES = [
    Ligature("=====", "equal_equal_equal_equal_equal.dlig", "equal_run"),
    Ligature("-----", "hyphen_hyphen_hyphen_hyphen_hyphen.dlig", "hyphen_run"),
    Ligature("====", "equal_equal_equal_equal.dlig", "equal_run"),
    Ligature("----", "hyphen_hyphen_hyphen_hyphen.dlig", "hyphen_run"),
    Ligature("!==", "exclam_equal_equal.dlig"),
    Ligature("===", "equal_equal_equal.dlig"),
    Ligature("<=>", "less_equal_greater.dlig", "spaceship_equal"),
    Ligature("<->", "less_hyphen_greater.dlig", "spaceship_hyphen"),
    Ligature("-->", "hyphen_hyphen_greater.dlig", "scale_hyphen_greater"),
    Ligature("<--", "less_hyphen_hyphen.dlig", "mirror_hyphen_hyphen_greater"),
    Ligature("==>", "equal_equal_greater.dlig", "scale_equal_greater"),
    Ligature("<==", "less_equal_equal.dlig", "mirror_equal_equal_greater"),
    *FIRA_CODE_CALT_FIXED_LIGATURES,
    Ligature("...", "period_period_period.dlig", "compact_components"),
    Ligature("!=", "exclam_equal.dlig", "scale_exclam_equal_equal"),
    Ligature("==", "equal_equal.dlig", "scale_equal_equal_equal"),
    Ligature("->", "hyphen_greater.dlig"),
    Ligature("=>", "equal_greater.dlig"),
    Ligature(">=", "greater_equal.dlig"),
    Ligature("<-", "less_hyphen.dlig"),
    Ligature("<=", "less_equal.dlig"),
    Ligature("<>", "less_greater.dlig", "compact_components"),
    Ligature("::", "colon_colon.dlig", "compact_components"),
    Ligature(":=", "colon_equal.dlig", "colon_equal"),
    Ligature("&&", "ampersand_ampersand.dlig", "compact_components"),
    Ligature("||", "bar_bar.dlig", "compact_components"),
    Ligature("++", "plus_plus.dlig", "compact_components"),
    Ligature("--", "hyphen_hyphen.dlig", "spaced_components"),
    Ligature("**", "asterisk_asterisk.dlig", "compact_components"),
    Ligature("//", "slash_slash.dlig", "compact_components"),
    Ligature("/*", "slash_asterisk.dlig", "compact_components"),
    Ligature("*/", "asterisk_slash.dlig", "compact_components"),
    Ligature("??", "question_question.dlig", "compact_components"),
    Ligature("?.", "question_period.dlig", "compact_components"),
]

_existing_sources = {ligature.source for ligature in LIGATURES}
LIGATURES.extend(
    compact_ligature(source) for source in FIRA_CODE_COMPAT_SOURCES if source not in _existing_sources
)

SEQ_GLYPHS = [
    "hyphen_start.seq",
    "hyphen_middle.seq",
    "hyphen_end.seq",
    "less_hyphen_start.seq",
    "greater_hyphen_end.seq",
    "equal_start.seq",
    "equal_middle.seq",
    "equal_end.seq",
    "less_equal_start.seq",
    "greater_equal_end.seq",
    "underscore_start.seq",
    "underscore_middle.seq",
    "underscore_end.seq",
]


def layer_map(glyph) -> dict[str, object]:
    return {layer.layerId: layer for layer in glyph.layers}


def clear_layer(layer) -> None:
    while len(layer.paths):
        layer.paths.pop(0)
    while len(layer.components):
        layer.components.pop(0)


def empty_glyph(font, target: str, template: str = "equal_equal_equal.dlig"):
    glyph = copy.deepcopy(font.glyphs[template])
    glyph.name = target
    for layer in glyph.layers:
        clear_layer(layer)
    return glyph


def write_glyph(glyph) -> str:
    buffer = io.StringIO()
    Writer(buffer).writeValue(glyph)
    return buffer.getvalue()


def rect_path(x_min: float, y_min: float, x_max: float, y_max: float) -> GSPath:
    path = GSPath()
    path.closed = True
    path.nodes.append(GSNode((x_max, y_min), "line"))
    path.nodes.append(GSNode((x_max, y_max), "line"))
    path.nodes.append(GSNode((x_min, y_max), "line"))
    path.nodes.append(GSNode((x_min, y_min), "line"))
    return path


def clone_path(source_path: GSPath) -> GSPath:
    path = GSPath()
    path.closed = source_path.closed
    for source_node in source_path.nodes:
        path.nodes.append(
            GSNode(
                (source_node.position.x, source_node.position.y),
                source_node.type,
                smooth=source_node.smooth,
                name=source_node.name,
            )
        )
    return path


def path_bounds(path: GSPath) -> tuple[float, float, float, float]:
    xs = [node.position.x for node in path.nodes]
    ys = [node.position.y for node in path.nodes]
    return min(xs), min(ys), max(xs), max(ys)


def clone_path_shifted(source_path: GSPath, dx: float = 0, dy: float = 0) -> GSPath:
    path = clone_path(source_path)
    for node in path.nodes:
        node.position.x += dx
        node.position.y += dy
    return path


def path_center(path: GSPath) -> tuple[float, float]:
    x_min, y_min, x_max, y_max = path_bounds(path)
    return (x_min + x_max) / 2, (y_min + y_max) / 2


def component_glyph(font, source: str, target: str, compact: bool = False, compact_step: float = 0.7):
    glyph = empty_glyph(font, target)
    base_layers = {name: layer_map(font.glyphs[name]) for name in set(CHAR_GLYPHS[ch] for ch in source)}
    for layer in glyph.layers:
        raw_width = sum(base_layers[CHAR_GLYPHS[char]][layer.layerId].width for char in source)
        visual_width = raw_width
        offsets = []
        cursor = 0
        if compact and len(source) > 1:
            offsets = [0]
            cursor = 0
            for char in source[:-1]:
                base_name = CHAR_GLYPHS[char]
                cursor += base_layers[base_name][layer.layerId].width * compact_step
                offsets.append(cursor)
            last_width = base_layers[CHAR_GLYPHS[source[-1]]][layer.layerId].width
            visual_width = offsets[-1] + last_width
            origin = (raw_width - visual_width) / 2
        else:
            origin = 0
        for char in source:
            base_name = CHAR_GLYPHS[char]
            if compact:
                cursor = offsets.pop(0)
            component = GSComponent(base_name, offset=(origin + cursor, 0))
            layer.components.append(component)
            if not compact:
                cursor += base_layers[base_name][layer.layerId].width
        layer.width = raw_width
    return glyph


def line_run_glyph(font, target: str, base_name: str, length: int, y_source: str | None = None):
    glyph = empty_glyph(font, target)
    base_layers = layer_map(font.glyphs[base_name])
    y_layers = layer_map(font.glyphs[y_source or base_name])
    for layer in glyph.layers:
        base_layer = base_layers[layer.layerId]
        y_layer = y_layers[layer.layerId]
        layer.width = base_layer.width * length
        for source_path in y_layer.paths:
            x_min, y_min, x_max, y_max = path_bounds(source_path)
            right_margin = base_layer.width - x_max
            layer.paths.append(rect_path(x_min, y_min, layer.width - right_margin, y_max))
    return glyph


def equal_pair(font, source: str, target: str):
    glyph = empty_glyph(font, target)
    equal_layers = layer_map(font.glyphs["equal"])
    for layer in glyph.layers:
        source_layer = equal_layers[layer.layerId]
        layer.width = source_layer.width * 2
        for source_path in source_layer.paths:
            path = clone_path(source_path)
            for node in path.nodes:
                node.position.x *= 2
            layer.paths.append(path)
    return glyph


def continuous_run(font, source: str, target: str, base_name: str):
    return line_run_glyph(font, target, base_name, len(source))


def arrow_body(font, target: str, line_name: str, head_left: bool, head_right: bool, double_line: bool = False):
    glyph = empty_glyph(font, target)
    line_layers = layer_map(font.glyphs[line_name])
    less_layers = layer_map(font.glyphs["less"])
    greater_layers = layer_map(font.glyphs["greater"])
    for layer in glyph.layers:
        line_layer = line_layers[layer.layerId]
        cell = line_layer.width
        layer.width = cell * 3
        left_gap = cell * (0.48 if head_left else 0.08)
        right_gap = cell * (0.48 if head_right else 0.08)
        x_start = left_gap
        x_end = layer.width - right_gap
        for source_path in line_layer.paths:
            _, y_min, _, y_max = path_bounds(source_path)
            layer.paths.append(rect_path(x_start, y_min, x_end, y_max))
        if head_left:
            layer.components.append(GSComponent("less", offset=(0, 0)))
        if head_right:
            layer.components.append(GSComponent("greater", offset=(cell * 2, 0)))
    return glyph


def colon_equal(font, target: str):
    glyph = empty_glyph(font, target)
    equal_layers = layer_map(font.glyphs["equal"])
    colon_layers = layer_map(font.glyphs["colon"])
    for layer in glyph.layers:
        equal_layer = equal_layers[layer.layerId]
        colon_layer = colon_layers[layer.layerId]
        cell = equal_layer.width
        layer.width = cell * 2
        equal_paths = sorted(equal_layer.paths, key=lambda path: path_center(path)[1], reverse=True)
        colon_paths = sorted(colon_layer.paths, key=lambda path: path_center(path)[1], reverse=True)
        bar_left = cell * 0.48
        bar_right = layer.width - (cell - path_bounds(equal_paths[0])[2])
        dot_center_x = cell * 0.28
        for equal_path in equal_paths:
            _, y_min, _, y_max = path_bounds(equal_path)
            layer.paths.append(rect_path(bar_left, y_min, bar_right, y_max))
        for colon_path, equal_path in zip(colon_paths, equal_paths):
            colon_x, colon_y = path_center(colon_path)
            _, equal_y = path_center(equal_path)
            layer.paths.append(clone_path_shifted(colon_path, dot_center_x - colon_x, equal_y - colon_y))
    return glyph


def seq_line(font, target: str, base_name: str, mode: str):
    glyph = empty_glyph(font, target)
    base_layers = layer_map(font.glyphs[base_name])
    for layer in glyph.layers:
        base_layer = base_layers[layer.layerId]
        layer.width = base_layer.width
        overlap = base_layer.width * 0.04
        for source_path in base_layer.paths:
            x_min, y_min, x_max, y_max = path_bounds(source_path)
            if mode == "start":
                x0, x1 = x_min, base_layer.width + overlap
            elif mode == "middle":
                x0, x1 = -overlap, base_layer.width + overlap
            elif mode == "end":
                x0, x1 = -overlap, x_max
            else:
                raise ValueError(mode)
            layer.paths.append(rect_path(x0, y_min, x1, y_max))
    return glyph


def seq_arrow_end(font, target: str, base_name: str, direction: str):
    glyph = empty_glyph(font, target)
    base_layers = layer_map(font.glyphs[base_name])
    head_name = "greater" if direction == "right" else "less"
    head_layers = layer_map(font.glyphs[head_name])
    for layer in glyph.layers:
        base_layer = base_layers[layer.layerId]
        head_layer = head_layers[layer.layerId]
        layer.width = base_layer.width
        overlap = base_layer.width * 0.04
        if direction == "right":
            line_end = base_layer.width * 0.58
            head_offset = 0
            line_start = -overlap
        else:
            line_start = base_layer.width * 0.42
            line_end = base_layer.width + overlap
            head_offset = 0
        for source_path in base_layer.paths:
            _, y_min, _, y_max = path_bounds(source_path)
            layer.paths.append(rect_path(line_start, y_min, line_end, y_max))
        layer.components.append(GSComponent(head_name, offset=(head_offset, 0)))
    return glyph


def seq_glyph(font, target: str):
    if target.startswith("hyphen_"):
        return seq_line(font, target, "hyphen", target.removeprefix("hyphen_").removesuffix(".seq"))
    if target.startswith("equal_"):
        return seq_line(font, target, "equal", target.removeprefix("equal_").removesuffix(".seq"))
    if target.startswith("underscore_"):
        return seq_line(font, target, "underscore", target.removeprefix("underscore_").removesuffix(".seq"))
    if target == "less_hyphen_start.seq":
        return seq_arrow_end(font, target, "hyphen", "left")
    if target == "greater_hyphen_end.seq":
        return seq_arrow_end(font, target, "hyphen", "right")
    if target == "less_equal_start.seq":
        return seq_arrow_end(font, target, "equal", "left")
    if target == "greater_equal_end.seq":
        return seq_arrow_end(font, target, "equal", "right")
    raise ValueError(target)


def glyph_exists(font, glyph_name: str) -> bool:
    return font.glyphs[glyph_name] is not None



def scaled_existing(
    font,
    source_glyph: str,
    target: str,
    scale_x: float,
    replacements: dict[str, str] | None = None,
    scale_components: bool = True,
):
    glyph = copy.deepcopy(font.glyphs[source_glyph])
    glyph.name = target
    replacements = replacements or {}
    for layer in glyph.layers:
        layer.width *= scale_x
        for component in layer.components:
            if component.name in replacements:
                component.name = replacements[component.name]
            if scale_components:
                xx, xy, yx, yy, dx, dy = component.transform
                component.transform = (xx * scale_x, xy, yx * scale_x, yy, dx * scale_x, dy)
        for path in layer.paths:
            for node in path.nodes:
                node.position.x *= scale_x
    return glyph


def mirrored_existing(font, source_glyph: str, target: str):
    glyph = empty_glyph(font, target)
    source_layers = layer_map(font.glyphs[source_glyph])
    for layer in glyph.layers:
        source_layer = source_layers[layer.layerId]
        layer.width = source_layer.width
        layer.components.append(GSComponent(source_glyph, transform=(-1, 0, 0, 1, source_layer.width, 0)))
    return glyph


def overlap_pair(font, target: str, left: str, right: str):
    glyph = empty_glyph(font, target)
    left_layers = layer_map(font.glyphs[left])
    right_layers = layer_map(font.glyphs[right])
    for layer in glyph.layers:
        left_layer = left_layers[layer.layerId]
        right_layer = right_layers[layer.layerId]
        overlap = left_layer.width / 2
        layer.width = left_layer.width + right_layer.width - overlap
        layer.components.append(GSComponent(left, offset=(0, 0)))
        layer.components.append(GSComponent(right, offset=(overlap, 0)))
    return glyph


def make_glyph(font, ligature: Ligature):
    generator = ligature.generator
    if generator == "components":
        return component_glyph(font, ligature.source, ligature.glyph)
    if generator == "compact_components":
        return component_glyph(font, ligature.source, ligature.glyph, compact=True)
    if generator == "spaced_components":
        return component_glyph(font, ligature.source, ligature.glyph, compact=True, compact_step=0.88)
    if generator == "equal_pair":
        return equal_pair(font, ligature.source, ligature.glyph)
    if generator == "equal_run":
        return continuous_run(font, ligature.source, ligature.glyph, "equal")
    if generator == "hyphen_run":
        return continuous_run(font, ligature.source, ligature.glyph, "hyphen")
    if generator == "underscore_run":
        return continuous_run(font, ligature.source, ligature.glyph, "underscore")
    if generator == "spaceship_equal":
        return arrow_body(font, ligature.glyph, "equal", head_left=True, head_right=True, double_line=True)
    if generator == "spaceship_hyphen":
        return arrow_body(font, ligature.glyph, "hyphen", head_left=True, head_right=True)
    if generator == "colon_equal":
        return colon_equal(font, ligature.glyph)
    if generator == "scale_exclam_equal_equal":
        return scaled_existing(
            font,
            "exclam_equal_equal.dlig",
            ligature.glyph,
            2 / 3,
            {"equal_equal_equal.dlig": "equal_equal.dlig"},
            scale_components=False,
        )
    if generator == "scale_equal_equal_equal":
        return scaled_existing(font, "equal_equal_equal.dlig", ligature.glyph, 2 / 3)
    if generator == "scale_hyphen_greater":
        return scaled_existing(font, "hyphen_greater.dlig", ligature.glyph, 3 / 2)
    if generator == "scale_equal_greater":
        return scaled_existing(font, "equal_greater.dlig", ligature.glyph, 3 / 2)
    if generator == "mirror_hyphen_hyphen_greater":
        return mirrored_existing(font, "hyphen_hyphen_greater.dlig", ligature.glyph)
    if generator == "mirror_equal_equal_greater":
        return mirrored_existing(font, "equal_equal_greater.dlig", ligature.glyph)
    if generator == "overlap_less_equal_greater":
        return overlap_pair(font, ligature.glyph, "less_equal.dlig", "equal_greater.dlig")
    if generator == "overlap_less_hyphen_greater":
        return overlap_pair(font, ligature.glyph, "less_hyphen.dlig", "hyphen_greater.dlig")
    raise ValueError(f"No generator for {ligature.source}: {ligature.glyph}")


def find_glyph_block(text: str, glyphname: str) -> tuple[int, int] | None:
    marker = f"{{\nglyphname = {glyphname};"
    try:
        start = text.index(marker)
    except ValueError:
        return None
    depth = 0
    for index in range(start, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return start, index + 1
    raise ValueError(f"Could not find end of glyph block {glyphname}")


def delete_glyph_block(text: str, glyphname: str) -> str:
    existing = find_glyph_block(text, glyphname)
    if existing is None:
        return text
    start, end = existing
    if text[end : end + 2] == ",\n":
        end += 2
    elif text[start - 2 : start] == ",\n":
        start -= 2
    return text[:start] + text[end:]


def upsert_glyph_block(text: str, glyphname: str, block: str, anchor: str = "{\nglyphname = equal_equal_equal.dlig;") -> str:
    existing = find_glyph_block(text, glyphname)
    if existing is not None:
        start, end = existing
        return text[:start] + block + text[end:]
    if anchor not in text:
        raise ValueError(f"Missing glyph insertion anchor: {anchor!r}")
    return text.replace(anchor, block + ",\n" + anchor, 1)


def feature_code() -> str:
    lines = []
    for ligature in LIGATURES:
        glyph_names = " ".join(CHAR_GLYPHS[char] for char in ligature.source)
        lines.append(f"sub {glyph_names} by {ligature.glyph};")
    return "\n".join(lines) + "\n"


def calt_code() -> str:
    hyphen_extenders = []
    equal_extenders = []
    for index in range(8):
        hyphen_extenders.append(
            f"""lookup ligconsolata_hyphen_arrow_extend_{index + 1} {{
  sub [less_hyphen_start.seq hyphen_start.seq hyphen_middle.seq] hyphen' [hyphen greater] by hyphen_middle.seq;
  sub [less_hyphen_start.seq hyphen_start.seq hyphen_middle.seq] hyphen' by hyphen_end.seq;
  sub [less_hyphen_start.seq hyphen_start.seq hyphen_middle.seq] greater' by greater_hyphen_end.seq;
}} ligconsolata_hyphen_arrow_extend_{index + 1};"""
        )
        equal_extenders.append(
            f"""lookup ligconsolata_equal_arrow_extend_{index + 1} {{
  sub [less_equal_start.seq equal_start.seq equal_middle.seq] equal' [equal greater] by equal_middle.seq;
  sub [less_equal_start.seq equal_start.seq equal_middle.seq] equal' by equal_end.seq;
  sub [less_equal_start.seq equal_start.seq equal_middle.seq] greater' by greater_equal_end.seq;
}} ligconsolata_equal_arrow_extend_{index + 1};"""
        )
    underscore_extenders = []
    for index in range(8):
        underscore_extenders.append(
            f"""lookup ligconsolata_underscore_run_extend_{index + 1} {{
  sub [underscore_start.seq underscore_middle.seq] underscore' underscore by underscore_middle.seq;
  sub [underscore_start.seq underscore_middle.seq] underscore' by underscore_end.seq;
}} ligconsolata_underscore_run_extend_{index + 1};"""
        )
    return f"""lookup ligconsolata_hyphen_arrow_start {{
  ignore sub hyphen' hyphen [space parenright bracketright braceright semicolon comma];
  ignore sub hyphen hyphen' [space parenright bracketright braceright semicolon comma];
  ignore sub less' hyphen [space parenright bracketright braceright semicolon comma];
  ignore sub hyphen' greater [space parenright bracketright braceright semicolon comma];
  ignore sub hyphen hyphen' [hyphen greater];
  ignore sub hyphen_start.seq hyphen' [hyphen greater];
  ignore sub less_hyphen_start.seq hyphen' [hyphen greater];
  ignore sub hyphen' greater greater;
  ignore sub less' hyphen bar;
  sub less' hyphen by less_hyphen_start.seq;
  sub hyphen' hyphen hyphen by hyphen_start.seq;
  sub hyphen' greater by hyphen_start.seq;
}} ligconsolata_hyphen_arrow_start;

{chr(10).join(hyphen_extenders)}

lookup ligconsolata_equal_arrow_start {{
  ignore sub exclam equal' equal;
  ignore sub exclam equal equal';
  ignore sub equal' equal equal [space parenright bracketright braceright semicolon comma];
  ignore sub equal equal' equal [space parenright bracketright braceright semicolon comma];
  ignore sub equal equal equal' [space parenright bracketright braceright semicolon comma];
  ignore sub equal' equal [space parenright bracketright braceright semicolon comma];
  ignore sub equal equal' [space parenright bracketright braceright semicolon comma];
  ignore sub less' equal [space parenright bracketright braceright semicolon comma];
  ignore sub equal' greater [space parenright bracketright braceright semicolon comma];
  ignore sub equal equal' [equal greater];
  ignore sub equal_start.seq equal' [equal greater];
  ignore sub less_equal_start.seq equal' [equal greater];
  ignore sub equal' greater greater;
  ignore sub equal' equal [less bar slash];
  ignore sub less' equal bar;
  sub less' equal by less_equal_start.seq;
  sub equal' [equal greater] by equal_start.seq;
}} ligconsolata_equal_arrow_start;

{chr(10).join(equal_extenders)}

lookup ligconsolata_underscore_run_start {{
  ignore sub [underscore underscore_start.seq underscore_middle.seq] underscore' underscore underscore underscore underscore underscore underscore;
  sub underscore' underscore underscore underscore underscore underscore underscore by underscore_start.seq;
}} ligconsolata_underscore_run_start;

{chr(10).join(underscore_extenders)}
"""


def replace_feature(text: str, name: str, code: str) -> str:
    name_marker = f"name = {name};"
    name_index = text.index(name_marker)
    code_marker = 'code = "'
    code_start = text.rfind(code_marker, 0, name_index)
    if code_start < 0:
        raise ValueError(f"Could not find code block for feature {name}")
    value_start = code_start + len(code_marker)
    value_end = text.index('\n";', value_start)
    return text[:value_start] + code + text[value_end:]


def upsert_feature(text: str, name: str, code: str, before_name: str) -> str:
    if f"name = {name};" in text:
        return replace_feature(text, name, code)
    before_index = text.index(f"name = {before_name};")
    block_start = text.rfind("{\nautomatic = 1;", 0, before_index)
    if block_start < 0:
        raise ValueError(f"Could not find insertion point before feature {before_name}")
    block = f'{{\nautomatic = 1;\ncode = "{code}";\nname = {name};\n}},\n'
    return text[:block_start] + block + text[block_start:]


def main() -> None:
    print(f"Loading {SOURCE} ...", flush=True)
    with SOURCE.open("r", encoding="utf-8") as fp:
        font = glyphsLib.load(fp)

    text = SOURCE.read_text(encoding="utf-8")
    generated_count = 0
    for glyph_name in OBSOLETE_GENERATED_GLYPHS:
        text = delete_glyph_block(text, glyph_name)
    for glyph_name in SEQ_GLYPHS:
        glyph = seq_glyph(font, glyph_name)
        text = upsert_glyph_block(text, glyph_name, write_glyph(glyph))
        generated_count += 1
        print(f"  generated sequence glyph {glyph_name}", flush=True)
    for ligature in LIGATURES:
        if ligature.generator is None:
            continue
        glyph = make_glyph(font, ligature)
        text = upsert_glyph_block(text, ligature.glyph, write_glyph(glyph))
        generated_count += 1
        print(f"  generated {ligature.source} -> {ligature.glyph}", flush=True)

    code = feature_code()
    text = upsert_feature(text, "calt", calt_code(), "dlig")
    text = replace_feature(text, "dlig", code)
    text = replace_feature(text, "liga", code)
    SOURCE.write_text(text, encoding="utf-8")
    print(f"Updated {SOURCE} with {generated_count} generated glyphs and {len(LIGATURES)} feature rules.")


if __name__ == "__main__":
    main()
