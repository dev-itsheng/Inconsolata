from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path

from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parents[1]
FONT_PATH = ROOT / "documentation" / "demo" / "fonts" / "LigconsolataNext[wdth,wght].ttf"
HB_SHAPE = shutil.which("hb-shape") or (
    "/opt/homebrew/bin/hb-shape" if Path("/opt/homebrew/bin/hb-shape").exists() else None
)
DEFAULT_FEATURES = "liga=1,calt=1,dlig=0"


def shape_glyphs(text: str, features: str = DEFAULT_FEATURES) -> list[str]:
    if HB_SHAPE is None:
        raise unittest.SkipTest("hb-shape is required for ligature guard tests")
    if not FONT_PATH.exists():
        raise unittest.SkipTest("build documentation/demo/fonts before running ligature guard tests")

    result = subprocess.run(
        [HB_SHAPE, str(FONT_PATH), text, f"--features={features}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    output = result.stdout.strip()
    if not output.startswith("[") or not output.endswith("]"):
        raise AssertionError(f"Unexpected hb-shape output for {text!r}: {output}")
    body = output[1:-1]
    return [chunk.split("=", 1)[0] for chunk in body.split("|") if chunk]


class LigatureContextGuardTests(unittest.TestCase):
    def assertHasGlyph(self, text: str, glyph: str, features: str = DEFAULT_FEATURES) -> None:
        glyphs = shape_glyphs(text, features)
        self.assertIn(glyph, glyphs, f"{text!r} shaped to {glyphs}")

    def assertLacksGlyph(self, text: str, glyph: str, features: str = DEFAULT_FEATURES) -> None:
        glyphs = shape_glyphs(text, features)
        self.assertNotIn(glyph, glyphs, f"{text!r} shaped to {glyphs}")

    def test_slash_comment_prefixes_do_not_ligate_urls(self) -> None:
        self.assertHasGlyph("// comment", "slash_slash.dlig")
        self.assertHasGlyph("/// reference", "slash_slash_slash.dlig")
        self.assertLacksGlyph("//TODO", "slash_slash.dlig")
        self.assertLacksGlyph("https://example.com", "slash_slash.dlig")
        self.assertLacksGlyph("file:///tmp/font", "slash_slash_slash.dlig")

    def test_block_comment_boundaries_do_not_ligate_globs(self) -> None:
        self.assertHasGlyph("/* block */", "slash_asterisk.dlig")
        self.assertHasGlyph("/* block */", "asterisk_slash.dlig")

        # Block comment boundaries are contextual calt behavior, not unconditional liga/dlig.
        self.assertLacksGlyph("/* block */", "slash_asterisk.dlig", "liga=1,calt=0,dlig=0")
        self.assertLacksGlyph("/* block */", "slash_asterisk.dlig", "liga=1,calt=0,dlig=1")
        self.assertHasGlyph("/* block */", "slash_asterisk.dlig", "liga=0,calt=1,dlig=0")

        for sample in ("/*note*/", "a/*.js", "ls /*", "*/5 * * * *"):
            self.assertLacksGlyph(sample, "slash_asterisk.dlig")
            self.assertLacksGlyph(sample, "asterisk_slash.dlig")

        for sample in (
            "**/*{.vue,.js,.jsx,.mjs,.ts,.tsx}",
            "!**/composables/**/*.ts",
        ):
            self.assertHasGlyph(sample, "asterisk_asterisk.dlig")
            self.assertLacksGlyph(sample, "slash_asterisk.dlig")
            self.assertLacksGlyph(sample, "asterisk_slash.dlig")
        self.assertLacksGlyph("src/*.ts", "slash_asterisk.dlig")

    def test_logic_slash_backslash_forms_require_spaces(self) -> None:
        self.assertHasGlyph("a /\\ b", "slash_backslash.dlig")
        self.assertHasGlyph("x \\/ y", "backslash_slash.dlig")
        self.assertLacksGlyph("regex /\\d/", "slash_backslash.dlig")
        self.assertLacksGlyph("path \\/tmp", "backslash_slash.dlig")

    def test_numeric_x_only_changes_hex_and_dimension_contexts(self) -> None:
        self.assertHasGlyph("hex 0xFF", "x.multiply")
        self.assertHasGlyph("size 800x600", "x.multiply")
        self.assertLacksGlyph("raw xray axb 0xG", "x.multiply")
        self.assertLacksGlyph("raw x86 0XFF 800X600", "x.multiply")

    def test_markdown_hash_badges_are_heading_context_only(self) -> None:
        self.assertHasGlyph("## title", "numbersign_run2.dlig")
        self.assertHasGlyph("###### title", "numbersign_run6.dlig")
        self.assertHasGlyph("####### title", "numbersign_start.seq")
        self.assertHasGlyph("####### title", "numbersign_end.seq")
        self.assertLacksGlyph("##title", "numbersign_run2.dlig")
        self.assertLacksGlyph("a ## b", "numbersign_run2.dlig")

    def test_fixed_equality_and_comparison_ligatures_survive_calt(self) -> None:
        self.assertHasGlyph("a != b", "exclam_equal.dlig")
        self.assertHasGlyph("a !== b", "exclam_equal_equal.dlig")
        self.assertHasGlyph("a == b", "equal_equal.dlig")
        self.assertHasGlyph("a === b", "equal_equal_equal.dlig")
        self.assertHasGlyph("a <= b", "less_equal.dlig")
        self.assertHasGlyph("a >= b", "greater_equal.dlig")

    def test_short_fixed_forms_are_not_stolen_by_long_arrow_calt(self) -> None:
        self.assertHasGlyph("i --", "hyphen_hyphen.dlig")
        self.assertHasGlyph("a ->> b", "hyphen_greater_greater.dlig")
        self.assertHasGlyph("a =>> b", "equal_greater_greater.dlig")
        self.assertHasGlyph("a ----> b", "hyphen_start.seq")
        self.assertHasGlyph("a ----> b", "greater_hyphen_end.seq")

    def test_comment_guard_helpers_preserve_width(self) -> None:
        if not FONT_PATH.exists():
            raise unittest.SkipTest("build documentation/demo/fonts before running ligature guard tests")
        font = TTFont(FONT_PATH)
        metrics = font["hmtx"].metrics
        self.assertEqual(metrics["slash_comment_spacer"][0], 0)
        self.assertEqual(metrics["slash_asterisk.dlig"][0], 1000)
        self.assertEqual(metrics["asterisk_slash.dlig"][0], 1000)


if __name__ == "__main__":
    unittest.main()
