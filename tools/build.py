#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
CFG = json.loads((ROOT / "config/eu.json").read_text())


def tool(env, names):
    if os.environ.get(env):
        return os.environ[env]
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    raise SystemExit(f"missing tool: set {env} or install one of {', '.join(names)}")


def run(*args):
    print("+", " ".join(map(str, args)))
    subprocess.run(list(map(str, args)), check=True)


def compile_asm(source: Path, obj: Path, mode: str):
    clang = tool("CLANG", ["clang"])
    run(
        clang,
        "--target=arm-none-eabi",
        "-mcpu=arm7tdmi",
        "-mthumb" if mode == "thumb" else "-marm",
        "-c",
        source,
        "-o",
        obj,
    )


def link_unit(obj: Path, out: Path, address: str, script: Path):
    script.write_text(f"SECTIONS {{ . = {address}; .text : {{ *(.text*) }} }}\n")
    lld = tool("LD_LLD", ["ld.lld"])
    run(lld, "-m", "armelf", "--entry=0", "-T", script, "-o", out, obj)


def build_base():
    directory = BUILD / "base"
    directory.mkdir(parents=True, exist_ok=True)
    for unit in CFG["units"]:
        name = unit["name"]
        obj = directory / f"{name}.o"
        compile_asm(ROOT / unit["source"], obj, unit["mode"])
        link_unit(obj, directory / f"{name}.elf", unit["address"], directory / f"{name}.ld")


def verify_rom(path: Path):
    run(shutil.which("python3") or "python3", ROOT / "tools/verify_rom.py", path)


def build_target(rom_path: Path):
    verify_rom(rom_path)
    rom = rom_path.read_bytes()
    directory = BUILD / "target"
    directory.mkdir(parents=True, exist_ok=True)
    for unit in CFG["units"]:
        name = unit["name"]
        offset = int(unit["rom_offset"], 0)
        size = int(unit["size"], 0)
        blob = directory / f"{name}.bin"
        blob.write_bytes(rom[offset : offset + size])
        asm = directory / f"{name}_target.s"
        asm.write_text(
            ".syntax unified\n"
            + (".thumb\n" if unit["mode"] == "thumb" else ".arm\n")
            + f'.section .text,"ax",%progbits\n.incbin "{blob.as_posix()}"\n'
        )
        obj = directory / f"{name}.o"
        compile_asm(asm, obj, unit["mode"])
        link_unit(obj, directory / f"{name}.elf", unit["address"], directory / f"{name}.ld")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["base", "target", "all"])
    parser.add_argument("--rom", type=Path, default=ROOT / "baserom_eu.gba")
    args = parser.parse_args()
    if args.mode in ("base", "all"):
        build_base()
    if args.mode in ("target", "all"):
        build_target(args.rom)


if __name__ == "__main__":
    main()
