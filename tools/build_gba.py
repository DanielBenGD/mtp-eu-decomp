#!/usr/bin/env python3
"""Build a playable hybrid GBA ROM from a legal EU base dump.

Undecompiled ranges and assets come from the user's ROM. Every reviewed unit is
replaced with freshly assembled clean source. Nothing extracted is tracked.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "config/eu.json").read_text())


def objcopy() -> str:
    value = os.environ.get("LLVM_OBJCOPY") or shutil.which("llvm-objcopy")
    if not value:
        raise SystemExit("missing llvm-objcopy; set LLVM_OBJCOPY")
    return value


def section_bytes(elf: Path) -> bytes:
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "text.bin"
        subprocess.run([objcopy(), "-O", "binary", "--only-section=.text", str(elf), str(out)], check=True)
        return out.read_bytes()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("rom", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "build" / "mpt_eu_rebuilt.gba")
    args = parser.parse_args()

    subprocess.run([sys.executable, str(ROOT / "tools/verify_rom.py"), str(args.rom)], check=True)
    subprocess.run([sys.executable, str(ROOT / "tools/build.py"), "base"], check=True)

    image = bytearray(args.rom.read_bytes())
    replaced = 0
    for unit in CFG["units"]:
        offset = int(unit["rom_offset"], 0)
        size = int(unit["size"], 0)
        clean = section_bytes(ROOT / "build" / "base" / f"{unit['name']}.elf")
        if len(clean) != size:
            raise SystemExit(f"{unit['name']}: built {len(clean)} bytes, expected {size}")
        image[offset : offset + size] = clean
        replaced += size

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(image)
    identical = image == args.rom.read_bytes()
    print(f"GBA image: {args.output}")
    print(f"clean-source bytes inserted: {replaced}")
    print(f"byte-identical to supported ROM: {identical}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
