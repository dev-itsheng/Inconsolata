#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "sources" / "Inconsolata.glyphs"
ORIGINAL_FONT = ROOT / "fonts" / "variable" / "Inconsolata[wdth,wght].ttf"
DEMO_FONTS = ROOT / "documentation" / "demo" / "fonts"
NEXT_FONT = DEMO_FONTS / "LigconsolataNext[wdth,wght].ttf"
ORIGINAL_DEMO_FONT = DEMO_FONTS / "Inconsolata[wdth,wght].ttf"


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
    build_next_font()
    print(ORIGINAL_DEMO_FONT)
    print(NEXT_FONT)


if __name__ == "__main__":
    main()
