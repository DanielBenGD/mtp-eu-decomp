#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "config/eu.json").read_text())


def section_bytes(elf: Path) -> bytes:
    objcopy = os.environ.get("LLVM_OBJCOPY") or shutil.which("llvm-objcopy")
    if not objcopy:
        raise SystemExit("missing llvm-objcopy; set LLVM_OBJCOPY")
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "text.bin"
        subprocess.run([objcopy, "-O", "binary", "--only-section=.text", str(elf), str(out)], check=True)
        return out.read_bytes()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-only", action="store_true")
    args = parser.parse_args()
    matched = 0
    total = 0
    for unit in CFG["units"]:
        name = unit["name"]
        expected_size = int(unit["size"], 0)
        base = section_bytes(ROOT / "build" / "base" / f"{name}.elf")
        digest = hashlib.sha256(base).hexdigest()
        if len(base) != expected_size:
            raise SystemExit(f"{name}: built {len(base)} bytes, expected {expected_size}")
        if digest != unit["expected_sha256"]:
            raise SystemExit(f"{name}: clean source hash {digest} does not match reviewed target hash")
        if not args.base_only:
            target = section_bytes(ROOT / "build" / "target" / f"{name}.elf")
            if base != target:
                raise SystemExit(f"{name}: base and target differ")
        print(f"{name}: MATCH ({expected_size}/{expected_size} bytes)")
        matched += expected_size
        total += expected_size
    print(f"verified units: {len(CFG['units'])}; matched bytes: {matched}/{total}")


if __name__ == "__main__":
    main()
