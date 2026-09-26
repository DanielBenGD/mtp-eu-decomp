#!/usr/bin/env python3
"""Compare reviewed ARM/Thumb instruction streams independently of data bytes."""
import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "config/eu.json").read_text())


def section_bytes(path: Path) -> bytes:
    objcopy = os.environ.get("LLVM_OBJCOPY") or shutil.which("llvm-objcopy")
    if not objcopy:
        raise SystemExit("missing llvm-objcopy; set LLVM_OBJCOPY")
    with tempfile.TemporaryDirectory() as td:
        output = Path(td) / "text.bin"
        subprocess.run([objcopy, "-O", "binary", "--only-section=.text", str(path), str(output)], check=True)
        return output.read_bytes()


def stream(data: bytes, address: int, mode: str):
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB if mode == "thumb" else CS_MODE_ARM)
    return [(i.mnemonic, i.op_str) for i in md.disasm(data, address)]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-only", action="store_true")
    args = parser.parse_args()
    matched = total = 0
    for unit in CFG["units"]:
        base = section_bytes(ROOT / "build/base" / f"{unit['name']}.elf")
        target = None if args.base_only else section_bytes(ROOT / "build/target" / f"{unit['name']}.elf")
        seen = 0
        for offset, size in unit["instruction_ranges"]:
            expected = stream(base[offset:offset+size], int(unit["address"], 0)+offset, unit["mode"])
            if target is not None:
                actual = stream(target[offset:offset+size], int(unit["address"], 0)+offset, unit["mode"])
                if expected != actual:
                    raise SystemExit(f"{unit['name']}: instruction mismatch at +0x{offset:x}")
            seen += len(expected)
        configured = unit["instruction_count"]
        if seen != configured:
            raise SystemExit(f"{unit['name']}: decoded {seen} instructions, configured {configured}")
        matched += seen
        total += configured
        print(f"{unit['name']}: {seen}/{configured} instructions match")
    print(f"instruction accuracy in reviewed units: {matched}/{total} (100.00%)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
