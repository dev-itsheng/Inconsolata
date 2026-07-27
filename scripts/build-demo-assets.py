#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "sources" / "Inconsolata.glyphs"
ORIGINAL_FONT = ROOT / "fonts" / "variable" / "Inconsolata[wdth,wght].ttf"
DEMO_FONTS = ROOT / "documentation" / "demo" / "fonts"
NEXT_FONT = DEMO_FONTS / "LigconsolataNext[wdth,wght].ttf"
ORIGINAL_DEMO_FONT = DEMO_FONTS / "Inconsolata[wdth,wght].ttf"
VERSION_RE = re.compile(r"(\d+)\.(\d+)")


def format_version(version: tuple[int, int]) -> str:
    major, minor = version
    return f"{major}.{minor:03d}"


def bump_version(version: tuple[int, int]) -> tuple[int, int]:
    major, minor = version
    return major, minor + 1


def read_font_version(path: Path) -> tuple[int, int] | None:
    if not path.exists():
        return None
    font = TTFont(path)
    try:
        for record in font["name"].names:
            if record.nameID != 5:
                continue
            match = VERSION_RE.search(record.toUnicode())
            if match:
                return int(match.group(1)), int(match.group(2))

        revision = float(font["head"].fontRevision)
        major = int(revision)
        minor = round((revision - major) * 1000)
        return major, minor
    finally:
        font.close()


def set_name_text(record, text: str) -> None:
    record.string = text.encode(record.getEncoding(), errors="replace")


def bump_install_version(path: Path, previous_version: tuple[int, int] | None) -> tuple[int, int]:
    font = TTFont(path)
    try:
        built_version = read_font_version(path)
        baseline = max(version for version in (previous_version, built_version) if version is not None)
        next_version = bump_version(baseline)
        next_version_text = format_version(next_version)

        font["head"].fontRevision = float(next_version_text)
        for record in font["name"].names:
            if record.nameID == 5:
                set_name_text(record, f"Version {next_version_text}")
            elif record.nameID == 3:
                unique_id = record.toUnicode()
                set_name_text(record, VERSION_RE.sub(next_version_text, unique_id, count=1))

        font.save(path)
        return next_version
    finally:
        font.close()


def build_next_font() -> None:
    fontmake = Path(sys.executable).with_name("fontmake")
    fontmake_command = str(fontmake if fontmake.exists() else "fontmake")
    subprocess.run(
        [
            fontmake_command,
            "-g",
            str(SOURCE),
            "-o",
            "variable",
            "--master-dir",
            "{tmp}",
            "--output-path",
            str(NEXT_FONT),
        ],
        cwd=ROOT,
        check=True,
    )


def main() -> None:
    DEMO_FONTS.mkdir(parents=True, exist_ok=True)
    if not ORIGINAL_FONT.exists():
        raise FileNotFoundError(ORIGINAL_FONT)
    shutil.copy2(ORIGINAL_FONT, ORIGINAL_DEMO_FONT)
    previous_version = read_font_version(NEXT_FONT)
    build_next_font()
    next_version = bump_install_version(NEXT_FONT, previous_version)
    print(ORIGINAL_DEMO_FONT)
    print(f"{NEXT_FONT} Version {format_version(next_version)}")


if __name__ == "__main__":
    main()
