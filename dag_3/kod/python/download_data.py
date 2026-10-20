#!/usr/bin/env python3
"""Hämta AI4I 2020 från UCI och packa upp CSV-filen."""

from __future__ import annotations

import argparse
import io
import urllib.request
import zipfile
from pathlib import Path


URL = "https://archive.ics.uci.edu/static/public/601/ai4i+2020+predictive+maintenance+dataset.zip"
CODE_DIR = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=CODE_DIR / "data/ai4i2020.csv")
    args = parser.parse_args()

    print(f"Hämtar {URL}")
    with urllib.request.urlopen(URL, timeout=30) as response:
        archive = zipfile.ZipFile(io.BytesIO(response.read()))
        content = archive.read("ai4i2020.csv")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(content)
    print(f"Sparade {args.output} ({len(content):,} byte)")


if __name__ == "__main__":
    main()
