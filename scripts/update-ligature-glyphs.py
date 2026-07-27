#!/usr/bin/env python3
from __future__ import annotations

import copy
import io
import unicodedata
import argparse
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
    "x": "x",
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
    Ligature("[]", glyph_name_for_source("[]"), "bracket_pair"),
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

HASH_BADGE_LIGATURES = [
    Ligature("######", "numbersign_run6.dlig", "numbersign_badge"),
    Ligature("#####", "numbersign_run5.dlig", "numbersign_badge"),
    Ligature("####", "numbersign_run4.dlig", "numbersign_badge"),
    Ligature("###", "numbersign_run3.dlig", "numbersign_badge"),
    Ligature("##", "numbersign_run2.dlig", "numbersign_badge"),
]

CONTEXTUAL_CALT_ONLY_LIGATURE_SOURCES = {ligature.source for ligature in HASH_BADGE_LIGATURES}
CONTEXTUAL_BLOCK_COMMENT_LIGATURE_SOURCES = {"/*", "*/"}
CONTEXTUAL_SPACE_AROUND_LIGATURE_SOURCES = {"/\\", "\\/"}


OBSOLETE_GENERATED_GLYPHS = [
    "backslash.ss06",
    "numbersign_run8.dlig",
    "numbersign_run7.dlig",
    "numbersign_run6.dlig",
    "numbersign_run5.dlig",
    "numbersign_run4.dlig",
    "numbersign_run3.dlig",
    "numbersign_run2.dlig",
    glyph_name_for_source("######"),
    glyph_name_for_source("#####"),
    glyph_name_for_source("####"),
    glyph_name_for_source("###"),
    glyph_name_for_source("##"),
    glyph_name_for_source("____"),
    glyph_name_for_source("___"),
    glyph_name_for_source("__"),
    glyph_name_for_source("www"),
]


LIGATURES = [
    *HASH_BADGE_LIGATURES,
    Ligature("=====", "equal_equal_equal_equal_equal.dlig", "equal_run"),
    Ligature("-----", "hyphen_hyphen_hyphen_hyphen_hyphen.dlig", "hyphen_run"),
    Ligature("====", "equal_equal_equal_equal.dlig", "equal_run"),
    Ligature("----", "hyphen_hyphen_hyphen_hyphen.dlig", "hyphen_run"),
    Ligature("!==", "exclam_equal_equal.dlig"),
    Ligature("===", "equal_equal_equal.dlig", "equal_triple"),
    Ligature("<=>", "less_equal_greater.dlig", "spaceship_equal"),
    Ligature("<->", "less_hyphen_greater.dlig", "spaceship_hyphen"),
    Ligature("-->", "hyphen_hyphen_greater.dlig", "scale_hyphen_greater"),
    Ligature("<--", "less_hyphen_hyphen.dlig", "mirror_hyphen_hyphen_greater"),
    Ligature("==>", "equal_equal_greater.dlig", "scale_equal_greater"),
    Ligature("<==", "less_equal_equal.dlig", "mirror_equal_equal_greater"),
    *FIRA_CODE_CALT_FIXED_LIGATURES,
    Ligature("...", "period_period_period.dlig", "compact_components"),
    Ligature("!=", "exclam_equal.dlig", "scale_exclam_equal_equal"),
    Ligature("==", "equal_equal.dlig", "equal_pair"),
    Ligature("->", "hyphen_greater.dlig"),
    Ligature("=>", "equal_greater.dlig"),
    Ligature(">=", "greater_equal.dlig", "greater_equal"),
    Ligature("<-", "less_hyphen.dlig"),
    Ligature("<=", "less_equal.dlig", "less_equal"),
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

CONTEXTUAL_SPACE_LIGATURE_SOURCES = {"//", "///"}

_existing_sources = {ligature.source for ligature in LIGATURES}
LIGATURES.extend(
    compact_ligature(source) for source in FIRA_CODE_COMPAT_SOURCES if source not in _existing_sources
)

SEQ_GLYPHS = [
    "hyphen_start.seq",
    "hyphen_middle.seq",
    "hyphen_end.seq",
    "less_hyphen_start.seq",
    "less_hyphen_end.seq",
    "greater_hyphen_start.seq",
    "greater_hyphen_end.seq",
    "equal_start.seq",
    "equal_middle.seq",
    "equal_end.seq",
    "less_equal_start.seq",
    "less_equal_end.seq",
    "greater_equal_start.seq",
    "greater_equal_end.seq",
    "underscore_start.seq",
    "underscore_middle.seq",
    "underscore_end.seq",
    "bar_hyphen_start.seq",
    "bar_hyphen_end.seq",
    "bar_equal_start.seq",
    "bar_equal_end.seq",
    "slash_equal_start.seq",
    "slash_equal_middle.seq",
    "slash_equal_end.seq",
    "colon_equal_middle.seq",
    "exclam_equal_middle.seq",
    "numbersign_start.seq",
    "numbersign_middle.seq",
    "numbersign_end.seq",
]

SPACER_GLYPHS = [
    "slash_comment_spacer",
    "slash_logic_spacer",
    "backslash_logic_spacer",
    "numbersign_badge_spacer",
]

CENTER_GLYPHS = {
    "colon.center": "colon",
    "less.center": "less",
    "greater.center": "greater",
}

CASE_GLYPHS = {
    "hyphen.lc": ("hyphen", "x"),
    "plus.lc": ("plus", "x"),
    "asterisk.lc": ("asterisk", "x"),
    "colon.uc": ("colon", "H"),
}

CONTEXT_GLYPHS = {
    "x.multiply": "multiply",
}

STYLE_GLYPHS = {
    "backslash.thin": "backslash",
}

HEX_ZERO_CLASS_GLYPHS = [
    "zero",
    "zero.zero",
]

DIGIT_CLASS_GLYPHS = [
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
]

BADGE_DIGIT_GLYPHS = {
    2: "two",
    3: "three",
    4: "four",
    5: "five",
    6: "six",
}

HEX_DIGIT_CLASS_GLYPHS = [
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
]

TALL_CLASS_EXTRAS = [
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "parenleft",
    "parenright",
    "bracketleft",
    "bracketright",
    "braceleft",
    "braceright",
    "bar",
]

RUN_STOP_CLASS = "[space parenright bracketright braceright semicolon comma]"


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
    glyph.unicode = None
    glyph.unicodes = []
    for layer in glyph.layers:
        clear_layer(layer)
    return glyph


def zero_width_spacer_glyph(font, target: str):
    glyph = empty_glyph(font, target)
    for layer in glyph.layers:
        layer.width = 0
    return glyph


def cloned_outline_glyph(font, target: str, source_name: str):
    glyph = empty_glyph(font, target, source_name)
    source_layers = layer_map(font.glyphs[source_name])
    for layer in glyph.layers:
        source_layer = source_layers[layer.layerId]
        layer.width = source_layer.width
        for path in source_layer.paths:
            layer.paths.append(clone_path(path))
        for component in source_layer.components:
            layer.components.append(copy.deepcopy(component))
    return glyph


def thin_backslash_glyph(font, target: str, source_name: str):
    glyph = cloned_outline_glyph(font, target, source_name)
    glyph.unicode = None
    glyph.unicodes = []
    factor = 0.48
    for layer in glyph.layers:
        for path in layer.paths:
            if len(path.nodes) != 4:
                continue
            p0, p1, p2, p3 = [node.position for node in path.nodes]
            bottom_center_x = (p0.x + p3.x) / 2
            bottom_center_y = (p0.y + p3.y) / 2
            top_center_x = (p1.x + p2.x) / 2
            top_center_y = (p1.y + p2.y) / 2
            bottom_half_x = (p0.x - p3.x) * factor / 2
            bottom_half_y = (p0.y - p3.y) * factor / 2
            top_half_x = (p1.x - p2.x) * factor / 2
            top_half_y = (p1.y - p2.y) * factor / 2
            path.nodes[0].position = (bottom_center_x + bottom_half_x, bottom_center_y + bottom_half_y)
            path.nodes[1].position = (top_center_x + top_half_x, top_center_y + top_half_y)
            path.nodes[2].position = (top_center_x - top_half_x, top_center_y - top_half_y)
            path.nodes[3].position = (bottom_center_x - bottom_half_x, bottom_center_y - bottom_half_y)
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


def polygon_path(points: list[tuple[float, float]]) -> GSPath:
    path = GSPath()
    path.closed = True
    for point in points:
        path.nodes.append(GSNode(point, "line"))
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


def slanted_stroke_with_vertical_caps(source_path: GSPath, dx: float = 0, dy: float = 0) -> GSPath:
    top_left = source_path.nodes[5].position
    bottom_left = source_path.nodes[6].position
    top_right = source_path.nodes[4].position
    bottom_right = source_path.nodes[0].position
    left_center_y = (top_left.y + bottom_left.y) / 2
    right_center_y = (top_right.y + bottom_right.y) / 2
    right_center_x = (top_right.x + bottom_right.x) / 2
    slope = (right_center_y - left_center_y) / (right_center_x - top_left.x)
    stroke_height = top_left.y - bottom_left.y
    right_x = bottom_right.x
    right_center_y = left_center_y + slope * (right_x - top_left.x)
    path = GSPath()
    path.closed = True
    path.nodes.append(GSNode((right_x + dx, right_center_y - stroke_height / 2 + dy), "line"))
    path.nodes.append(GSNode((right_x + dx, right_center_y + stroke_height / 2 + dy), "line"))
    path.nodes.append(GSNode((top_left.x + dx, top_left.y + dy), "line"))
    path.nodes.append(GSNode((bottom_left.x + dx, bottom_left.y + dy), "line"))
    return path


def clone_path_transformed(source_path: GSPath, transform: tuple[float, float, float, float, float, float]) -> GSPath:
    xx, xy, yx, yy, dx, dy = transform
    path = GSPath()
    path.closed = source_path.closed
    for source_node in source_path.nodes:
        x = source_node.position.x
        y = source_node.position.y
        path.nodes.append(
            GSNode(
                (x * xx + y * yx + dx, x * xy + y * yy + dy),
                source_node.type,
                smooth=source_node.smooth,
                name=source_node.name,
            )
        )
    return path


def compose_transforms(
    first: tuple[float, float, float, float, float, float],
    second: tuple[float, float, float, float, float, float],
) -> tuple[float, float, float, float, float, float]:
    axx, axy, ayx, ayy, adx, ady = first
    bxx, bxy, byx, byy, bdx, bdy = second
    return (
        axx * bxx + axy * byx,
        axx * bxy + axy * byy,
        ayx * bxx + ayy * byx,
        ayx * bxy + ayy * byy,
        adx * bxx + ady * byx + bdx,
        adx * bxy + ady * byy + bdy,
    )


def append_layer_outlines(
    font,
    target_layer,
    source_layer,
    transform: tuple[float, float, float, float, float, float],
    seen: set[str] | None = None,
) -> None:
    seen = seen or set()
    for source_path in source_layer.paths:
        target_layer.paths.append(clone_path_transformed(source_path, transform))
    for component in source_layer.components:
        if component.name in seen or font.glyphs[component.name] is None:
            continue
        component_layers = layer_map(font.glyphs[component.name])
        component_layer = component_layers.get(source_layer.layerId)
        if component_layer is None:
            continue
        append_layer_outlines(
            font,
            target_layer,
            component_layer,
            compose_transforms(component.transform, transform),
            seen | {component.name},
        )


def path_center(path: GSPath) -> tuple[float, float]:
    x_min, y_min, x_max, y_max = path_bounds(path)
    return (x_min + x_max) / 2, (y_min + y_max) / 2


def transformed_bounds(
    bounds: tuple[float, float, float, float], transform: tuple[float, float, float, float, float, float]
) -> tuple[float, float, float, float]:
    x_min, y_min, x_max, y_max = bounds
    xx, xy, yx, yy, dx, dy = transform
    points = [
        (x_min, y_min),
        (x_min, y_max),
        (x_max, y_min),
        (x_max, y_max),
    ]
    transformed = [(x * xx + y * yx + dx, x * xy + y * yy + dy) for x, y in points]
    xs = [point[0] for point in transformed]
    ys = [point[1] for point in transformed]
    return min(xs), min(ys), max(xs), max(ys)


def layer_visual_bounds(font, layer, seen: set[str] | None = None) -> tuple[float, float, float, float] | None:
    seen = seen or set()
    bounds = [path_bounds(path) for path in layer.paths]
    for component in layer.components:
        if component.name in seen or font.glyphs[component.name] is None:
            continue
        component_layers = layer_map(font.glyphs[component.name])
        component_layer = component_layers.get(layer.layerId)
        if component_layer is None:
            continue
        component_bounds = layer_visual_bounds(font, component_layer, seen | {component.name})
        if component_bounds is not None:
            bounds.append(transformed_bounds(component_bounds, component.transform))
    if not bounds:
        return None
    return (
        min(bound[0] for bound in bounds),
        min(bound[1] for bound in bounds),
        max(bound[2] for bound in bounds),
        max(bound[3] for bound in bounds),
    )


def layer_visual_center_y(font, layer) -> float:
    bounds = layer_visual_bounds(font, layer)
    if bounds is None:
        return layer_center_y(layer)
    return (bounds[1] + bounds[3]) / 2


def layer_center_y(layer) -> float:
    bounds = [path_bounds(path) for path in layer.paths]
    if not bounds:
        return 0
    y_min = min(bound[1] for bound in bounds)
    y_max = max(bound[3] for bound in bounds)
    return (y_min + y_max) / 2


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


def center_glyph(font, target: str, source: str):
    glyph = copy.deepcopy(font.glyphs[source])
    glyph.name = target
    glyph.unicode = None
    glyph.unicodes = []
    source_layers = layer_map(font.glyphs[source])
    equal_layers = layer_map(font.glyphs["equal"])
    for layer in glyph.layers:
        source_layer = source_layers[layer.layerId]
        equal_layer = equal_layers[layer.layerId]
        dy = layer_center_y(equal_layer) - layer_center_y(source_layer)
        for path in layer.paths:
            for node in path.nodes:
                node.position.y += dy
        for component in layer.components:
            xx, xy, yx, yy, dx, current_dy = component.transform
            component.transform = (xx, xy, yx, yy, dx, current_dy + dy)
    return glyph


def shift_layer_y(layer, dy: float) -> None:
    for path in layer.paths:
        for node in path.nodes:
            node.position.y += dy
    for component in layer.components:
        xx, xy, yx, yy, dx, current_dy = component.transform
        component.transform = (xx, xy, yx, yy, dx, current_dy + dy)


def vertically_aligned_glyph(font, target: str, source: str, reference: str):
    glyph = copy.deepcopy(font.glyphs[source])
    glyph.name = target
    glyph.unicode = None
    glyph.unicodes = []
    reference_layers = layer_map(font.glyphs[reference])
    for layer in glyph.layers:
        reference_layer = reference_layers[layer.layerId]
        dy = layer_visual_center_y(font, reference_layer) - layer_visual_center_y(font, layer)
        shift_layer_y(layer, dy)
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


def equal_triple(font, target: str):
    glyph = empty_glyph(font, target)
    source_layers = layer_map(font.glyphs["equal_equal_equal.dlig"])
    equal_layers = layer_map(font.glyphs["equal"])
    for layer in glyph.layers:
        source_layer = source_layers[layer.layerId]
        equal_layer = equal_layers[layer.layerId]
        layer.width = source_layer.width
        bounds = [path_bounds(path) for path in source_layer.paths]
        x_min = min(bound[0] for bound in bounds)
        x_max = max(bound[2] for bound in bounds)
        y_min = min(bound[1] for bound in bounds)
        y_max = max(bound[3] for bound in bounds)
        dy = layer_center_y(equal_layer) - (y_min + y_max) / 2
        for _, y_min, _, y_max in sorted(bounds, key=lambda bound: (bound[1] + bound[3]) / 2, reverse=True):
            layer.paths.append(rect_path(x_min, y_min + dy, x_max, y_max + dy))
    return glyph


def bracket_pair(font, target: str):
    glyph = empty_glyph(font, target)
    left_layers = layer_map(font.glyphs["bracketleft"])
    right_layers = layer_map(font.glyphs["bracketright"])
    for layer in glyph.layers:
        left_layer = left_layers[layer.layerId]
        right_layer = right_layers[layer.layerId]
        raw_width = left_layer.width + right_layer.width
        compact_step = 0.7
        right_offset = left_layer.width * compact_step
        visual_width = right_offset + right_layer.width
        origin = (raw_width - visual_width) / 2

        layer.width = raw_width
        append_layer_outlines(font, layer, left_layer, (1, 0, 0, 1, origin, 0))
        append_layer_outlines(font, layer, right_layer, (1, 0, 0, 1, origin + right_offset, 0))

        bounds = [path_bounds(path) for path in layer.paths]
        if bounds:
            x_min = min(bound[0] for bound in bounds)
            x_max = max(bound[2] for bound in bounds)
            dx = layer.width / 2 - (x_min + x_max) / 2
            for path in layer.paths:
                for node in path.nodes:
                    node.position.x += dx
    return glyph


def comparison_equal(font, target: str, direction: str):
    glyph = empty_glyph(font, target)
    source_layers = layer_map(font.glyphs["greater_equal.dlig"])
    equal_layers = layer_map(font.glyphs["equal"])
    for layer in glyph.layers:
        source_layer = source_layers[layer.layerId]
        equal_layer = equal_layers[layer.layerId]
        sign_path = max(source_layer.paths, key=lambda path: path_bounds(path)[3])
        equal_paths = sorted(equal_layer.paths, key=lambda path: path_center(path)[1], reverse=True)
        upper_equal = equal_paths[0]
        lower_equal = equal_paths[-1]
        equal_gap = path_center(upper_equal)[1] - path_center(lower_equal)[1]

        layer.width = source_layer.width
        bar_path = slanted_stroke_with_vertical_caps(sign_path, 0, -equal_gap)
        if direction == "greater":
            layer.paths.append(clone_path(sign_path))
            layer.paths.append(bar_path)
        elif direction == "less":
            layer.paths.append(clone_path_transformed(sign_path, (-1, 0, 0, 1, layer.width, 0)))
            layer.paths.append(clone_path_transformed(bar_path, (-1, 0, 0, 1, layer.width, 0)))
        else:
            raise ValueError(direction)

        bounds = [path_bounds(path) for path in layer.paths]
        x_min = min(bound[0] for bound in bounds)
        x_max = max(bound[2] for bound in bounds)
        dx = layer.width / 2 - (x_min + x_max) / 2
        for path in layer.paths:
            for node in path.nodes:
                node.position.x += dx
    return glyph


def continuous_run(font, source: str, target: str, base_name: str):
    return line_run_glyph(font, target, base_name, len(source))


def horizontal_stroke_bands(layer, center_y: float, min_width: float) -> tuple[tuple[float, float], tuple[float, float]]:
    top_y_values = []
    bottom_y_values = []
    for path in layer.paths:
        nodes = list(path.nodes)
        for index, first in enumerate(nodes):
            second = nodes[(index + 1) % len(nodes)]
            if first.type != "line" or second.type != "line":
                continue
            y1 = first.position.y
            y2 = second.position.y
            x1 = first.position.x
            x2 = second.position.x
            if abs(y1 - y2) > 1 or abs(x1 - x2) < min_width:
                continue
            if y1 > center_y:
                top_y_values.append(y1)
            else:
                bottom_y_values.append(y1)
    if not top_y_values or not bottom_y_values:
        raise ValueError(f"Could not infer # horizontal stroke bands for {layer.name}")
    return (min(top_y_values), max(top_y_values)), (min(bottom_y_values), max(bottom_y_values))


def edge_stem_corners(layer, sign_bounds: tuple[float, float, float, float]):
    sign_x_min, sign_y_min, sign_x_max, sign_y_max = sign_bounds
    sign_height = sign_y_max - sign_y_min
    y_tolerance = max(8, sign_height * 0.04)
    bottom_xs = sorted(
        {
            round(node.position.x, 3)
            for path in layer.paths
            for node in path.nodes
            if node.position.y <= sign_y_min + y_tolerance
        }
    )
    top_xs = sorted(
        {
            round(node.position.x, 3)
            for path in layer.paths
            for node in path.nodes
            if node.position.y >= sign_y_max - y_tolerance
        }
    )
    if len(bottom_xs) < 4 or len(top_xs) < 4:
        stem_width = (sign_x_max - sign_x_min) * 0.14
        left_bottom = (sign_x_min + stem_width * 1.4, sign_x_min + stem_width * 2.4)
        right_bottom = (sign_x_max - stem_width * 2.4, sign_x_max - stem_width * 1.4)
        slant = (sign_x_max - sign_x_min) * 0.16
        left_top = (left_bottom[0] + slant, left_bottom[1] + slant)
        right_top = (right_bottom[0] + slant, right_bottom[1] + slant)
    else:
        left_bottom = (bottom_xs[0], bottom_xs[1])
        right_bottom = (bottom_xs[-2], bottom_xs[-1])
        left_top = (top_xs[0], top_xs[1])
        right_top = (top_xs[-2], top_xs[-1])
    return left_bottom, right_bottom, left_top, right_top


def slanted_stem_path(
    bottom_pair: tuple[float, float],
    top_pair: tuple[float, float],
    y_min: float,
    y_max: float,
    dx: float = 0,
    trim_top_to: float | None = None,
) -> GSPath:
    top_y = y_max if trim_top_to is None else min(max(trim_top_to, y_min), y_max)
    progress = 0 if y_max == y_min else (top_y - y_min) / (y_max - y_min)
    left_top_x = bottom_pair[0] + (top_pair[0] - bottom_pair[0]) * progress
    right_top_x = bottom_pair[1] + (top_pair[1] - bottom_pair[1]) * progress
    return polygon_path(
        [
            (bottom_pair[0] + dx, y_min),
            (bottom_pair[1] + dx, y_min),
            (right_top_x + dx, top_y),
            (left_top_x + dx, top_y),
        ]
    )


def numbersign_badge(font, source: str, target: str):
    glyph = empty_glyph(font, target)
    count = len(source)
    digit_name = BADGE_DIGIT_GLYPHS[count]
    numbersign_layers = layer_map(font.glyphs["numbersign"])
    digit_layers = layer_map(font.glyphs[digit_name])
    for layer in glyph.layers:
        numbersign_layer = numbersign_layers[layer.layerId]
        digit_layer = digit_layers[layer.layerId]
        cell = numbersign_layer.width
        layer.width = cell * count

        digit_bounds = layer_visual_bounds(font, digit_layer)
        sign_bounds = layer_visual_bounds(font, numbersign_layer)
        if digit_bounds is None or sign_bounds is None:
            continue
        sign_x_min, sign_y_min, sign_x_max, sign_y_max = sign_bounds
        sign_width = sign_x_max - sign_x_min
        sign_height = sign_y_max - sign_y_min
        center_y = (sign_y_min + sign_y_max) / 2
        top_band, bottom_band = horizontal_stroke_bands(numbersign_layer, center_y, cell * 0.18)
        left_bottom, right_bottom, left_top, right_top = edge_stem_corners(numbersign_layer, sign_bounds)

        cutout_width = sign_width * 0.72
        cutout_height = sign_height * 0.72
        cutout_x_max = cell * (count - 1) + sign_x_max
        cutout_x_min = cutout_x_max - cutout_width
        cutout_y_max = sign_y_max
        cutout_y_min = cutout_y_max - cutout_height

        digit_x_min, digit_y_min, digit_x_max, digit_y_max = digit_bounds
        digit_box_width = cutout_width * 0.8
        digit_box_height = cutout_height * 0.84
        scale = min(
            digit_box_width / (digit_x_max - digit_x_min),
            digit_box_height / (digit_y_max - digit_y_min),
        )
        digit_width = (digit_x_max - digit_x_min) * scale
        digit_height = (digit_y_max - digit_y_min) * scale
        digit_bold_offset = cell * 0.02
        digit_dx = cutout_x_min + (cutout_width - digit_width) / 2 - digit_x_min * scale + cell * 0.02
        digit_dy = cutout_y_min + (cutout_height - digit_height) / 2 - digit_y_min * scale - sign_height * 0.01
        digit_visual_x_min = digit_dx + digit_x_min * scale - digit_bold_offset / 2
        digit_visual_y_min = digit_dy + digit_y_min * scale
        badge_clear_x = digit_visual_x_min - cell * 0.12
        badge_clear_y = digit_visual_y_min - sign_height * 0.12

        top_x_start = sign_x_min
        top_x_end = badge_clear_x
        bottom_x_start = sign_x_min
        bottom_x_end = badge_clear_x
        layer.paths.append(rect_path(top_x_start, top_band[0], top_x_end, top_band[1]))
        layer.paths.append(rect_path(bottom_x_start, bottom_band[0], bottom_x_end, bottom_band[1]))

        for index in range(count):
            dx = cell * index
            if index == count - 1:
                layer.paths.append(
                    slanted_stem_path(left_bottom, left_top, sign_y_min, sign_y_max, dx, badge_clear_y)
                )
                layer.paths.append(
                    slanted_stem_path(right_bottom, right_top, sign_y_min, sign_y_max, dx, badge_clear_y)
                )
            else:
                layer.paths.append(slanted_stem_path(left_bottom, left_top, sign_y_min, sign_y_max, dx))
                layer.paths.append(slanted_stem_path(right_bottom, right_top, sign_y_min, sign_y_max, dx))

        append_layer_outlines(font, layer, digit_layer, (scale, 0, 0, scale, digit_dx - digit_bold_offset / 2, digit_dy))
        append_layer_outlines(font, layer, digit_layer, (scale, 0, 0, scale, digit_dx + digit_bold_offset / 2, digit_dy))
    return glyph


def numbersign_seq_glyph(font, target: str):
    glyph = empty_glyph(font, target)
    numbersign_layers = layer_map(font.glyphs["numbersign"])
    mode = target.removeprefix("numbersign_").removesuffix(".seq")
    for layer in glyph.layers:
        numbersign_layer = numbersign_layers[layer.layerId]
        cell = numbersign_layer.width
        layer.width = cell

        sign_bounds = layer_visual_bounds(font, numbersign_layer)
        if sign_bounds is None:
            continue
        sign_x_min, sign_y_min, sign_x_max, sign_y_max = sign_bounds
        center_y = (sign_y_min + sign_y_max) / 2
        top_band, bottom_band = horizontal_stroke_bands(numbersign_layer, center_y, cell * 0.18)
        left_bottom, right_bottom, left_top, right_top = edge_stem_corners(numbersign_layer, sign_bounds)
        overlap = cell * 0.04

        if mode == "start":
            rail_x_start, rail_x_end = sign_x_min, cell + overlap
        elif mode == "middle":
            rail_x_start, rail_x_end = -overlap, cell + overlap
        elif mode == "end":
            rail_x_start, rail_x_end = -overlap, sign_x_max
        else:
            raise ValueError(target)

        layer.paths.append(rect_path(rail_x_start, top_band[0], rail_x_end, top_band[1]))
        layer.paths.append(rect_path(rail_x_start, bottom_band[0], rail_x_end, bottom_band[1]))
        layer.paths.append(slanted_stem_path(left_bottom, left_top, sign_y_min, sign_y_max))
        layer.paths.append(slanted_stem_path(right_bottom, right_top, sign_y_min, sign_y_max))
    return glyph


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


def seq_bar_endpoint(font, target: str, base_name: str, mode: str):
    return seq_sign_endpoint(font, target, base_name, "bar", mode)


def seq_sign_endpoint(font, target: str, base_name: str, sign_name: str, mode: str):
    glyph = empty_glyph(font, target)
    base_layers = layer_map(font.glyphs[base_name])
    for layer in glyph.layers:
        base_layer = base_layers[layer.layerId]
        cell = base_layer.width
        layer.width = cell
        overlap = cell * 0.04
        if mode == "start":
            line_start, line_end = cell * 0.5, cell + overlap
        elif mode == "end":
            line_start, line_end = -overlap, cell * 0.5
        else:
            raise ValueError(mode)
        for source_path in base_layer.paths:
            _, y_min, _, y_max = path_bounds(source_path)
            layer.paths.append(rect_path(line_start, y_min, line_end, y_max))
        layer.components.append(GSComponent(sign_name, offset=(0, 0)))
    return glyph


def seq_slash_equal_endpoint(font, target: str, mode: str):
    glyph = empty_glyph(font, target)
    equal_layers = layer_map(font.glyphs["equal"])
    for layer in glyph.layers:
        equal_layer = equal_layers[layer.layerId]
        cell = equal_layer.width
        layer.width = cell
        overlap = cell * 0.04
        if mode == "start":
            line_start, line_end = cell * 0.5, cell + overlap
        elif mode == "end":
            line_start, line_end = -overlap, cell * 0.5
        else:
            raise ValueError(mode)
        for source_path in equal_layer.paths:
            _, y_min, _, y_max = path_bounds(source_path)
            layer.paths.append(rect_path(line_start, y_min, line_end, y_max))
        layer.components.append(GSComponent("slash", offset=(0, 0)))
    return glyph


def seq_equal_marker_middle(font, target: str, marker_name: str):
    glyph = empty_glyph(font, target)
    equal_layers = layer_map(font.glyphs["equal"])
    marker_layers = layer_map(font.glyphs[marker_name])
    for layer in glyph.layers:
        equal_layer = equal_layers[layer.layerId]
        marker_layer = marker_layers[layer.layerId]
        cell = equal_layer.width
        layer.width = cell
        overlap = cell * 0.04
        equal_paths = sorted(equal_layer.paths, key=lambda path: path_center(path)[1], reverse=True)
        for equal_path in equal_paths:
            _, y_min, _, y_max = path_bounds(equal_path)
            layer.paths.append(rect_path(-overlap, y_min, cell + overlap, y_max))
        if marker_name == "colon":
            marker_paths = sorted(marker_layer.paths, key=lambda path: path_center(path)[1], reverse=True)
            for marker_path, equal_path in zip(marker_paths, equal_paths):
                marker_x, marker_y = path_center(marker_path)
                _, equal_y = path_center(equal_path)
                layer.paths.append(clone_path_shifted(marker_path, cell * 0.5 - marker_x, equal_y - marker_y))
        else:
            layer.components.append(GSComponent(marker_name, offset=(0, 0)))
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
    if target == "less_hyphen_end.seq":
        return seq_sign_endpoint(font, target, "hyphen", "less", "end")
    if target == "greater_hyphen_start.seq":
        return seq_sign_endpoint(font, target, "hyphen", "greater", "start")
    if target == "greater_hyphen_end.seq":
        return seq_arrow_end(font, target, "hyphen", "right")
    if target == "less_equal_start.seq":
        return seq_arrow_end(font, target, "equal", "left")
    if target == "less_equal_end.seq":
        return seq_sign_endpoint(font, target, "equal", "less", "end")
    if target == "greater_equal_start.seq":
        return seq_sign_endpoint(font, target, "equal", "greater", "start")
    if target == "greater_equal_end.seq":
        return seq_arrow_end(font, target, "equal", "right")
    if target == "bar_hyphen_start.seq":
        return seq_bar_endpoint(font, target, "hyphen", "start")
    if target == "bar_hyphen_end.seq":
        return seq_bar_endpoint(font, target, "hyphen", "end")
    if target == "bar_equal_start.seq":
        return seq_bar_endpoint(font, target, "equal", "start")
    if target == "bar_equal_end.seq":
        return seq_bar_endpoint(font, target, "equal", "end")
    if target == "slash_equal_start.seq":
        return seq_slash_equal_endpoint(font, target, "start")
    if target == "slash_equal_middle.seq":
        return seq_equal_marker_middle(font, target, "slash")
    if target == "slash_equal_end.seq":
        return seq_slash_equal_endpoint(font, target, "end")
    if target == "colon_equal_middle.seq":
        return seq_equal_marker_middle(font, target, "colon")
    if target == "exclam_equal_middle.seq":
        return seq_equal_marker_middle(font, target, "exclam")
    if target.startswith("numbersign_"):
        return numbersign_seq_glyph(font, target)
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
    if generator == "equal_triple":
        return equal_triple(font, ligature.glyph)
    if generator == "bracket_pair":
        return bracket_pair(font, ligature.glyph)
    if generator == "greater_equal":
        return comparison_equal(font, ligature.glyph, "greater")
    if generator == "less_equal":
        return comparison_equal(font, ligature.glyph, "less")
    if generator == "equal_run":
        return continuous_run(font, ligature.source, ligature.glyph, "equal")
    if generator == "hyphen_run":
        return continuous_run(font, ligature.source, ligature.glyph, "hyphen")
    if generator == "underscore_run":
        return continuous_run(font, ligature.source, ligature.glyph, "underscore")
    if generator == "numbersign_badge":
        return numbersign_badge(font, ligature.source, ligature.glyph)
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


def feature_code(namespace: str) -> str:
    lines = []
    for ligature in LIGATURES:
        if (
            ligature.source in CONTEXTUAL_SPACE_LIGATURE_SOURCES
            or ligature.source in CONTEXTUAL_SPACE_AROUND_LIGATURE_SOURCES
            or ligature.source in CONTEXTUAL_CALT_ONLY_LIGATURE_SOURCES
            or ligature.source in CONTEXTUAL_BLOCK_COMMENT_LIGATURE_SOURCES
        ):
            continue
        glyph_names = " ".join(CHAR_GLYPHS[char] for char in ligature.source)
        lines.append(f"sub {glyph_names} by {ligature.glyph};")
    lines.append(
        f"""lookup ligconsolata_slash_slash_comment_{namespace} {{
  sub slash_comment_spacer slash_comment_spacer slash' space by slash_slash_slash.dlig;
  sub slash_comment_spacer slash' slash space by slash_comment_spacer;
  sub slash' slash slash space by slash_comment_spacer;
  sub slash_comment_spacer slash' space by slash_slash.dlig;
  sub slash' slash space by slash_comment_spacer;
}} ligconsolata_slash_slash_comment_{namespace};"""
    )
    return "\n".join(lines) + "\n"


def match_case_code() -> str:
    return """lookup ligconsolata_lowercase_hyphen {
  ignore sub @Tall hyphen' @Lowercase;
  ignore sub @Lowercase hyphen' @Tall;
  ignore sub hyphen' hyphen;
  ignore sub hyphen hyphen';
  ignore sub @Lowercase hyphen' greater;
  ignore sub less hyphen' @Lowercase;
  sub hyphen' @Lowercase by hyphen.lc;
  sub @Lowercase hyphen' by hyphen.lc;
} ligconsolata_lowercase_hyphen;

lookup ligconsolata_lowercase_plus {
  ignore sub @Tall plus' @Lowercase;
  ignore sub @Lowercase plus' @Tall;
  ignore sub plus' plus;
  ignore sub plus plus';
  sub plus' @Lowercase by plus.lc;
  sub @Lowercase plus' by plus.lc;
} ligconsolata_lowercase_plus;

lookup ligconsolata_lowercase_asterisk {
  ignore sub @Tall asterisk' @Lowercase;
  ignore sub @Lowercase asterisk' @Tall;
  ignore sub asterisk' asterisk;
  ignore sub asterisk asterisk';
  ignore sub slash asterisk';
  ignore sub asterisk' slash;
  ignore sub less asterisk';
  ignore sub asterisk' greater;
  sub asterisk' @Lowercase by asterisk.lc;
  sub @Lowercase asterisk' by asterisk.lc;
} ligconsolata_lowercase_asterisk;

lookup ligconsolata_uppercase_colon {
  ignore sub @Tall colon' @Lowercase;
  ignore sub @Lowercase colon' @Tall;
  ignore sub colon' colon;
  ignore sub colon colon';
  ignore sub colon' equal;
  sub @Tall colon' by colon.uc;
  sub colon' @Tall by colon.uc;
} ligconsolata_uppercase_colon;"""


def run_stop_ignores(base_name: str, min_length: int = 3, max_length: int = 10) -> str:
    lines = []
    for length in range(min_length, max_length + 1):
        tail = " ".join([base_name] * (length - 1))
        lines.append(f"  ignore sub {base_name}' {tail} @Lowercase;")
        lines.append(f"  ignore sub {base_name}' {tail} @Tall;")
        lines.append(f"  ignore sub {base_name}' {tail} {RUN_STOP_CLASS};")
    return "\n".join(lines)


def hash_badge_code() -> str:
    preceder_ignores = [
        "space",
        "@Lowercase",
        "@Tall",
        "@Digit",
        "[exclam ampersand dollar percent asterisk plus hyphen period slash colon semicolon less equal greater question at bracketleft backslash bracketright asciicircum underscore parenleft parenright braceleft braceright bar asciitilde comma quotedbl quotesingle quoteleft quoteright quotedblleft quotedblright grave]",
    ]
    lookups = []
    for ligature in HASH_BADGE_LIGATURES:
        count = len(ligature.source)
        lines = [f"lookup ligconsolata_hash_badge_{count} {{"]
        preceded_tail = " ".join(["numbersign"] * (count - 1))
        first_suffix = " ".join(["numbersign"] * (count - 1))
        for preceder in preceder_ignores:
            lines.append(f"  ignore sub {preceder} numbersign' {first_suffix} space;")
        lines.append(f"  ignore sub numbersign numbersign' {preceded_tail} space;")
        final_prefix = " ".join(["numbersign_badge_spacer"] * (count - 1))
        lines.append(f"  sub {final_prefix} numbersign' space by {ligature.glyph};")
        for consumed in range(count - 2, 0, -1):
            prefix = " ".join(["numbersign_badge_spacer"] * consumed)
            suffix = " ".join(["numbersign"] * (count - consumed - 1))
            lines.append(f"  sub {prefix} numbersign' {suffix} space by numbersign_badge_spacer;")
        lines.append(f"  sub numbersign' {first_suffix} space by numbersign_badge_spacer;")
        lines.append(f"}} ligconsolata_hash_badge_{count};")
        lookups.append("\n".join(lines))
    return "\n\n".join(lookups)


def hash_long_code(max_extenders: int = 96) -> str:
    extenders = []
    for index in range(max_extenders):
        extenders.append(
            f"""lookup ligconsolata_hash_long_extend_{index + 1} {{
  sub [numbersign_start.seq numbersign_middle.seq] numbersign' numbersign by numbersign_middle.seq;
  sub [numbersign_start.seq numbersign_middle.seq] numbersign' by numbersign_end.seq;
}} ligconsolata_hash_long_extend_{index + 1};"""
        )
    return f"""lookup ligconsolata_hash_long_start {{
  ignore sub [numbersign numbersign_start.seq numbersign_middle.seq] numbersign' numbersign numbersign numbersign numbersign numbersign numbersign;
  sub numbersign' numbersign numbersign numbersign numbersign numbersign numbersign by numbersign_start.seq;
}} ligconsolata_hash_long_start;

{chr(10).join(extenders)}"""


def logic_conjunction_code() -> str:
    return """lookup ligconsolata_slash_backslash_logic {
  sub space slash_logic_spacer backslash' space by slash_backslash.dlig;
  sub space slash' backslash space by slash_logic_spacer;
} ligconsolata_slash_backslash_logic;

lookup ligconsolata_backslash_slash_logic {
  sub space backslash_logic_spacer slash' space by backslash_slash.dlig;
  sub space backslash' slash space by backslash_logic_spacer;
} ligconsolata_backslash_slash_logic;"""


def block_comment_code() -> str:
    return """lookup ligconsolata_block_comment_start {
  sub slash_comment_spacer asterisk' space by slash_asterisk.dlig;
  sub slash' asterisk space by slash_comment_spacer;
} ligconsolata_block_comment_start;

lookup ligconsolata_block_comment_end {
  sub space slash_comment_spacer slash' by asterisk_slash.dlig;
  sub space asterisk' slash by slash_comment_spacer;
} ligconsolata_block_comment_end;"""


def thin_backslash_code() -> str:
    return """lookup ligconsolata_backslash_thin {
  ignore sub backslash.thin backslash';
  sub backslash' by backslash.thin;
} ligconsolata_backslash_thin;"""


def zero_code() -> str:
    return """sub zero by zero.zero;
sub zeroinferior by zeroinferior.zero;
sub zero.dnom by zero.dnom.zero;
sub zero.numr by zero.numr.zero;
sub zerosuperior by zerosuperior.zero;"""


def calt_code() -> str:
    hyphen_extenders = []
    equal_extenders = []
    for index in range(8):
        hyphen_extenders.append(
            f"""lookup ligconsolata_hyphen_arrow_extend_{index + 1} {{
  sub [less_hyphen_start.seq greater_hyphen_start.seq hyphen_start.seq hyphen_middle.seq bar_hyphen_start.seq] hyphen' [hyphen less greater bar] by hyphen_middle.seq;
  sub [less_hyphen_start.seq greater_hyphen_start.seq hyphen_start.seq hyphen_middle.seq bar_hyphen_start.seq] hyphen' by hyphen_end.seq;
  sub [less_hyphen_start.seq greater_hyphen_start.seq hyphen_start.seq hyphen_middle.seq bar_hyphen_start.seq] less' by less_hyphen_end.seq;
  sub [less_hyphen_start.seq greater_hyphen_start.seq hyphen_start.seq hyphen_middle.seq bar_hyphen_start.seq] greater' by greater_hyphen_end.seq;
  sub [less_hyphen_start.seq greater_hyphen_start.seq hyphen_start.seq hyphen_middle.seq bar_hyphen_start.seq] bar' by bar_hyphen_end.seq;
}} ligconsolata_hyphen_arrow_extend_{index + 1};"""
        )
        equal_extenders.append(
            f"""lookup ligconsolata_equal_arrow_extend_{index + 1} {{
  sub [less_equal_start.seq greater_equal_start.seq equal_start.seq equal_middle.seq bar_equal_start.seq slash_equal_start.seq slash_equal_middle.seq colon_equal_middle.seq exclam_equal_middle.seq] equal' [equal less greater bar slash] by equal_middle.seq;
  sub [less_equal_start.seq greater_equal_start.seq equal_start.seq equal_middle.seq bar_equal_start.seq slash_equal_start.seq slash_equal_middle.seq colon_equal_middle.seq exclam_equal_middle.seq] equal' colon equal by equal_middle.seq;
  sub [less_equal_start.seq greater_equal_start.seq equal_start.seq equal_middle.seq bar_equal_start.seq slash_equal_start.seq slash_equal_middle.seq colon_equal_middle.seq exclam_equal_middle.seq] equal' exclam equal by equal_middle.seq;
  sub [less_equal_start.seq greater_equal_start.seq equal_start.seq equal_middle.seq bar_equal_start.seq slash_equal_start.seq slash_equal_middle.seq colon_equal_middle.seq exclam_equal_middle.seq] equal' by equal_end.seq;
  sub [less_equal_start.seq greater_equal_start.seq equal_start.seq equal_middle.seq bar_equal_start.seq slash_equal_start.seq slash_equal_middle.seq colon_equal_middle.seq exclam_equal_middle.seq] less' by less_equal_end.seq;
  sub [less_equal_start.seq greater_equal_start.seq equal_start.seq equal_middle.seq bar_equal_start.seq slash_equal_start.seq slash_equal_middle.seq colon_equal_middle.seq exclam_equal_middle.seq] greater' by greater_equal_end.seq;
  sub [less_equal_start.seq greater_equal_start.seq equal_start.seq equal_middle.seq bar_equal_start.seq slash_equal_start.seq slash_equal_middle.seq colon_equal_middle.seq exclam_equal_middle.seq] bar' by bar_equal_end.seq;
  sub [less_equal_start.seq greater_equal_start.seq equal_start.seq equal_middle.seq bar_equal_start.seq slash_equal_start.seq slash_equal_middle.seq colon_equal_middle.seq exclam_equal_middle.seq] slash' equal by slash_equal_middle.seq;
  sub [less_equal_start.seq greater_equal_start.seq equal_start.seq equal_middle.seq bar_equal_start.seq slash_equal_start.seq slash_equal_middle.seq colon_equal_middle.seq exclam_equal_middle.seq] slash' by slash_equal_end.seq;
  sub [equal_start.seq equal_middle.seq] colon' equal by colon_equal_middle.seq;
  sub [equal_start.seq equal_middle.seq] exclam' equal by exclam_equal_middle.seq;
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
  ignore sub greater_hyphen_start.seq hyphen' [hyphen less];
  ignore sub bar_hyphen_start.seq hyphen' [hyphen greater bar];
  ignore sub hyphen' greater greater;
  ignore sub hyphen' less less;
  ignore sub less' hyphen bar;
{run_stop_ignores("hyphen")}
  sub bar' hyphen hyphen hyphen by bar_hyphen_start.seq;
  sub greater' hyphen hyphen hyphen by greater_hyphen_start.seq;
  sub less' hyphen hyphen hyphen by less_hyphen_start.seq;
  sub hyphen' hyphen hyphen by hyphen_start.seq;
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
  ignore sub greater_equal_start.seq equal' [equal less];
  ignore sub bar_equal_start.seq equal' [equal greater bar];
  ignore sub slash_equal_start.seq equal' [equal greater slash colon exclam];
  ignore sub equal' greater greater;
  ignore sub equal' less less;
  ignore sub equal' equal [less bar slash];
  ignore sub less' equal bar;
{run_stop_ignores("equal")}
  sub bar' equal equal equal by bar_equal_start.seq;
  ignore sub slash slash' equal equal equal;
  ignore sub equal equal equal slash' equal;
  ignore sub equal_start.seq equal equal slash' equal;
  sub slash' equal equal equal by slash_equal_start.seq;
  sub greater' equal equal equal by greater_equal_start.seq;
  sub less' equal equal equal by less_equal_start.seq;
  sub equal' equal equal by equal_start.seq;
}} ligconsolata_equal_arrow_start;

{chr(10).join(equal_extenders)}

lookup ligconsolata_center {{
  ignore sub colon' [less greater] [equal hyphen];
  ignore sub colon colon' [less greater];
  ignore sub [less greater]' colon colon;
  sub [less.center greater.center colon.center] colon' by colon.center;
  sub colon.center [less greater]' by [less.center greater.center];
  sub [less greater]' colon by [less.center greater.center];
  sub colon' [less greater] by colon.center;
}} ligconsolata_center;

lookup ligconsolata_hex_multiply_x {{
  sub @HexZero x' [@Digit @HexDigit] by x.multiply;
  sub @Digit x' @Digit by x.multiply;
}} ligconsolata_hex_multiply_x;

{match_case_code()}

{logic_conjunction_code()}

{block_comment_code()}

{thin_backslash_code()}

{hash_badge_code()}

{hash_long_code()}

lookup ligconsolata_underscore_run_start {{
  ignore sub [underscore underscore_start.seq underscore_middle.seq] underscore' underscore underscore underscore underscore underscore underscore;
  sub underscore' underscore underscore underscore underscore underscore underscore by underscore_start.seq;
}} ligconsolata_underscore_run_start;

{chr(10).join(underscore_extenders)}
"""


def feature_section_bounds(text: str) -> tuple[int, int]:
    start = text.index("features = (")
    end = text.index(");\nfontMaster", start)
    return start, end


def find_feature_block(text: str, name: str) -> tuple[int, int] | None:
    section_start, section_end = feature_section_bounds(text)
    name_marker = f"name = {name};"
    name_index = text.find(name_marker, section_start, section_end)
    if name_index < 0:
        return None
    start = text.rfind("{\nautomatic = 1;", section_start, name_index)
    if start < 0:
        raise ValueError(f"Could not find feature block start for {name}")
    depth = 0
    for index in range(start, section_end):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return start, index + 1
    raise ValueError(f"Could not find feature block end for {name}")


def replace_feature(text: str, name: str, code: str) -> str:
    feature_block = find_feature_block(text, name)
    if feature_block is None:
        raise ValueError(f"Could not find feature {name}")
    start, end = feature_block
    code_marker = 'code = "'
    code_start = text.find(code_marker, start, end)
    if code_start < 0:
        raise ValueError(f"Could not find code block for feature {name}")
    value_start = code_start + len(code_marker)
    value_end = text.index('\n";', value_start)
    return text[:value_start] + code + text[value_end:]


def upsert_feature(text: str, name: str, code: str, before_name: str) -> str:
    if find_feature_block(text, name) is not None:
        return replace_feature(text, name, code)
    before_block = find_feature_block(text, before_name)
    if before_block is None:
        raise ValueError(f"Could not find insertion point before feature {before_name}")
    block_start, _ = before_block
    block = f'{{\nautomatic = 1;\ncode = "{code}";\nname = {name};\n}},\n'
    return text[:block_start] + block + text[block_start:]


def delete_feature(text: str, name: str) -> str:
    feature_block = find_feature_block(text, name)
    if feature_block is None:
        return text
    start, end = feature_block
    if text[end : end + 2] == ",\n":
        end += 2
    elif text[start - 2 : start] == ",\n":
        start -= 2
    return text[:start] + text[end:]


def class_code_for_lowercase(font) -> str:
    names = []
    for glyph in font.glyphs:
        if glyph.name is None or glyph.unicode is None:
            continue
        try:
            char = chr(int(glyph.unicode, 16))
        except ValueError:
            continue
        if unicodedata.category(char) == "Ll":
            names.append(glyph.name)
    return " ".join(names)


def class_code_for_tall(font) -> str:
    extras = " ".join(name for name in TALL_CLASS_EXTRAS if glyph_exists(font, name))
    return f"@Uppercase {extras}".strip()


def class_code_for_names(font, names: list[str]) -> str:
    return " ".join(name for name in names if glyph_exists(font, name))


def find_class_block(text: str, name: str) -> tuple[int, int] | None:
    classes_start = text.index("classes = (")
    classes_end = text.index(");\ncopyright", classes_start)
    name_marker = f"name = {name};"
    name_index = text.find(name_marker, classes_start, classes_end)
    if name_index < 0:
        return None
    start = text.rfind("{\n", classes_start, name_index)
    if start < 0:
        raise ValueError(f"Could not find class block start for {name}")
    depth = 0
    for index in range(start, classes_end):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return start, index + 1
    raise ValueError(f"Could not find class block end for {name}")


def delete_class(text: str, name: str) -> str:
    existing = find_class_block(text, name)
    if existing is None:
        return text
    start, end = existing
    if text[end : end + 2] == ",\n":
        end += 2
    elif text[start - 2 : start] == ",\n":
        start -= 2
    return text[:start] + text[end:]


def upsert_class(text: str, name: str, code: str) -> str:
    block = f'{{\ncode = "{code}";\nname = {name};\n}}'
    existing = find_class_block(text, name)
    if existing is not None:
        start, end = existing
        return text[:start] + block + text[end:]
    classes_start = text.index("classes = (")
    classes_end = text.index(");\ncopyright", classes_start)
    prefix = text[:classes_end].rstrip()
    separator = "," if prefix.endswith("}") else ""
    return prefix + f"{separator}\n{block}\n" + text[classes_end:]


def main() -> None:
    parser = argparse.ArgumentParser(description="Regenerate Ligconsolata Next ligature glyphs and feature code.")
    parser.add_argument(
        "--features-only",
        action="store_true",
        help="Only update OpenType classes/features; skip generated glyph blocks.",
    )
    args = parser.parse_args()

    print(f"Loading {SOURCE} ...", flush=True)
    with SOURCE.open("r", encoding="utf-8") as fp:
        font = glyphsLib.load(fp)

    text = SOURCE.read_text(encoding="utf-8")
    generated_count = 0
    if not args.features_only:
        for glyph_name in OBSOLETE_GENERATED_GLYPHS:
            text = delete_glyph_block(text, glyph_name)
        for glyph_name, source_name in CENTER_GLYPHS.items():
            glyph = center_glyph(font, glyph_name, source_name)
            text = upsert_glyph_block(text, glyph_name, write_glyph(glyph))
            generated_count += 1
            print(f"  generated center glyph {glyph_name}", flush=True)
        for glyph_name, (source_name, reference_name) in CASE_GLYPHS.items():
            glyph = vertically_aligned_glyph(font, glyph_name, source_name, reference_name)
            text = upsert_glyph_block(text, glyph_name, write_glyph(glyph))
            generated_count += 1
            print(f"  generated case glyph {glyph_name}", flush=True)
        for glyph_name, source_name in CONTEXT_GLYPHS.items():
            glyph = cloned_outline_glyph(font, glyph_name, source_name)
            text = upsert_glyph_block(text, glyph_name, write_glyph(glyph))
            generated_count += 1
            print(f"  generated context glyph {glyph_name}", flush=True)
        for glyph_name, source_name in STYLE_GLYPHS.items():
            glyph = thin_backslash_glyph(font, glyph_name, source_name)
            text = upsert_glyph_block(text, glyph_name, write_glyph(glyph))
            generated_count += 1
            print(f"  generated style glyph {glyph_name}", flush=True)
        for glyph_name in SEQ_GLYPHS:
            glyph = seq_glyph(font, glyph_name)
            text = upsert_glyph_block(text, glyph_name, write_glyph(glyph))
            generated_count += 1
            print(f"  generated sequence glyph {glyph_name}", flush=True)
        for glyph_name in SPACER_GLYPHS:
            glyph = zero_width_spacer_glyph(font, glyph_name)
            text = upsert_glyph_block(text, glyph_name, write_glyph(glyph))
            generated_count += 1
            print(f"  generated spacer glyph {glyph_name}", flush=True)
        for ligature in LIGATURES:
            if ligature.generator is None:
                continue
            glyph = make_glyph(font, ligature)
            text = upsert_glyph_block(text, ligature.glyph, write_glyph(glyph))
            generated_count += 1
            print(f"  generated {ligature.source} -> {ligature.glyph}", flush=True)
    else:
        print("  skipped generated glyph blocks (--features-only)", flush=True)

    text = upsert_class(text, "Lowercase", class_code_for_lowercase(font))
    text = upsert_class(text, "Tall", class_code_for_tall(font))
    text = upsert_class(text, "Digit", class_code_for_names(font, DIGIT_CLASS_GLYPHS))
    text = upsert_class(text, "HexDigit", class_code_for_names(font, HEX_DIGIT_CLASS_GLYPHS))
    text = upsert_class(text, "HexZero", class_code_for_names(font, HEX_ZERO_CLASS_GLYPHS))
    text = delete_class(text, "HashBadgePreceder")
    text = upsert_feature(text, "calt", calt_code(), "dlig")
    text = replace_feature(text, "dlig", feature_code("dlig"))
    text = replace_feature(text, "liga", feature_code("liga"))
    text = replace_feature(text, "zero", zero_code())
    text = delete_feature(text, "ss06")
    SOURCE.write_text(text, encoding="utf-8")
    print(f"Updated {SOURCE} with {generated_count} generated glyphs and {len(LIGATURES)} feature rules.")


if __name__ == "__main__":
    main()
