#!/usr/bin/env python3
"""Conservative recursive ARM7TDMI function mapper for the supported EU ROM.

This tool emits metadata only (addresses, modes, extents, and call edges). It
never copies ROM bytes into the repository. Results go under ignored build/.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path

from capstone import (
    CS_ARCH_ARM,
    CS_GRP_CALL,
    CS_GRP_JUMP,
    CS_MODE_ARM,
    CS_MODE_THUMB,
    Cs,
)
from capstone.arm import ARM_OP_IMM, ARM_REG_LR, ARM_REG_PC

ROM_BASE = 0x08000000
ROM_END = 0x0A000000
MAX_FUNCTION_BYTES = 0x10000
MAX_FUNCTIONS = 20000


@dataclass
class Function:
    address: int
    mode: str
    name: str
    blocks: set[int] = field(default_factory=set)
    instruction_addresses: set[int] = field(default_factory=set)
    calls: set[tuple[int, str]] = field(default_factory=set)
    complete: bool = True
    reason: str = ""

    @property
    def end(self) -> int:
        return max(self.instruction_addresses, default=self.address) + (2 if self.mode == "thumb" else 4)

    @property
    def size(self) -> int:
        return self.end - self.address


def parse_int(value: str) -> int:
    return int(value, 0)


def canonical_target(value: int, fallback_mode: str) -> tuple[int, str]:
    if value & 1:
        return value & ~1, "thumb"
    return value, fallback_mode


def load_seeds(path: Path) -> list[tuple[int, str, str]]:
    rows: list[tuple[int, str, str]] = []
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            address = parse_int(row["address"])
            mode = row["mode"].strip().lower()
            if mode not in {"arm", "thumb"}:
                raise ValueError(f"invalid mode {mode!r} for {row['address']}")
            rows.append((address, mode, row.get("name", "").strip() or f"sub_{address:08X}"))
    return rows


def immediate_target(insn) -> int | None:
    if not insn.operands or insn.operands[0].type != ARM_OP_IMM:
        return None
    return int(insn.operands[0].imm)


def returns_from(insn) -> bool:
    m = insn.mnemonic
    if m == "bx" and insn.operands and insn.operands[0].type != ARM_OP_IMM:
        return insn.reg_name(insn.operands[0].reg) == "lr"
    if m in {"pop", "ldm", "ldmia", "ldmfd"}:
        return any(op.type != ARM_OP_IMM and op.reg == ARM_REG_PC for op in insn.operands)
    if m == "mov" and insn.operands and insn.operands[0].type != ARM_OP_IMM:
        return insn.operands[0].reg == ARM_REG_PC
    return False


def valid_rom_address(address: int, rom_size: int, mode: str) -> bool:
    align = 2 if mode == "thumb" else 4
    return ROM_BASE <= address < ROM_BASE + rom_size and address % align == 0


def map_function(rom: bytes, seed: tuple[int, str, str], known_starts: set[tuple[int, str]]) -> Function:
    start, mode, name = seed
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB if mode == "thumb" else CS_MODE_ARM)
    md.detail = True
    fn = Function(start, mode, name)
    work = [start]
    visited_blocks: set[int] = set()

    while work:
        block = work.pop()
        if block in visited_blocks:
            continue
        if not valid_rom_address(block, len(rom), mode):
            fn.complete, fn.reason = False, "branch leaves ROM"
            continue
        if block != start and (block, mode) in known_starts:
            continue
        if abs(block - start) >= MAX_FUNCTION_BYTES:
            fn.complete, fn.reason = False, "branch exceeds function limit"
            continue
        visited_blocks.add(block)
        fn.blocks.add(block)
        pc = block

        while valid_rom_address(pc, len(rom), mode) and pc - start < MAX_FUNCTION_BYTES:
            if pc != start and (pc, mode) in known_starts:
                break
            offset = pc - ROM_BASE
            insns = list(md.disasm(rom[offset : offset + 4], pc, count=1))
            if not insns or insns[0].address != pc:
                fn.complete, fn.reason = False, "undecodable instruction"
                break
            insn = insns[0]
            fn.instruction_addresses.add(pc)
            next_pc = pc + insn.size
            target = immediate_target(insn)

            if insn.group(CS_GRP_CALL):
                if target is not None:
                    target_mode = "thumb" if insn.mnemonic.startswith("blx") and mode == "arm" else mode
                    target, target_mode = canonical_target(target, target_mode)
                    if valid_rom_address(target, len(rom), target_mode):
                        fn.calls.add((target, target_mode))
                pc = next_pc
                continue

            if returns_from(insn):
                break

            if insn.group(CS_GRP_JUMP):
                conditional = insn.mnemonic not in {"b", "bx"}
                if target is None:
                    break
                target, target_mode = canonical_target(target, mode)
                if target_mode != mode:
                    fn.calls.add((target, target_mode))
                    break
                # Far/backward unconditional branches are conservatively treated as tail calls.
                far = target < start or target >= start + MAX_FUNCTION_BYTES
                if not conditional and far:
                    if valid_rom_address(target, len(rom), mode):
                        fn.calls.add((target, mode))
                    break
                if valid_rom_address(target, len(rom), mode):
                    work.append(target)
                else:
                    fn.complete, fn.reason = False, "branch leaves ROM"
                if not conditional:
                    break

            pc = next_pc
        else:
            fn.complete, fn.reason = False, "function limit reached"

    return fn


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("rom", type=Path)
    parser.add_argument("--seeds", type=Path, default=Path("config/function_seeds.csv"))
    parser.add_argument("--output", type=Path, default=Path("build/analysis/functions.csv"))
    parser.add_argument("--edges", type=Path, default=Path("build/analysis/calls.csv"))
    parser.add_argument("--summary", type=Path, default=Path("build/analysis/map-summary.json"))
    args = parser.parse_args()

    rom = args.rom.read_bytes()
    seeds = load_seeds(args.seeds)
    queue = deque(seeds)
    queued = {(a, m) for a, m, _ in seeds}
    mapped: dict[tuple[int, str], Function] = {}

    while queue and len(mapped) < MAX_FUNCTIONS:
        seed = queue.popleft()
        key = (seed[0], seed[1])
        if key in mapped:
            continue
        fn = map_function(rom, seed, set(mapped) | queued)
        mapped[key] = fn
        for address, mode in sorted(fn.calls):
            key2 = (address, mode)
            if key2 not in mapped and key2 not in queued:
                queued.add(key2)
                queue.append((address, mode, f"sub_{address:08X}"))

    for path in (args.output, args.edges, args.summary):
        path.parent.mkdir(parents=True, exist_ok=True)

    functions = sorted(mapped.values(), key=lambda f: (f.address, f.mode))
    with args.output.open("w", newline="", encoding="utf-8") as f:
        out = csv.writer(f)
        out.writerow(["address", "mode", "end", "span_bytes", "instruction_count", "call_count", "complete", "name", "note"])
        for fn in functions:
            out.writerow([
                f"0x{fn.address:08X}", fn.mode, f"0x{fn.end:08X}", fn.size,
                len(fn.instruction_addresses), len(fn.calls), str(fn.complete).lower(), fn.name, fn.reason,
            ])

    with args.edges.open("w", newline="", encoding="utf-8") as f:
        out = csv.writer(f)
        out.writerow(["caller", "caller_mode", "callee", "callee_mode"])
        for fn in functions:
            for address, mode in sorted(fn.calls):
                out.writerow([f"0x{fn.address:08X}", fn.mode, f"0x{address:08X}", mode])

    summary = {
        "functions": len(functions),
        "arm_functions": sum(f.mode == "arm" for f in functions),
        "thumb_functions": sum(f.mode == "thumb" for f in functions),
        "complete_functions": sum(f.complete for f in functions),
        "instruction_addresses": len({(a, f.mode) for f in functions for a in f.instruction_addresses}),
        "call_edges": sum(len(f.calls) for f in functions),
        "warning": "Heuristic map: every boundary must be reviewed before becoming a progress unit.",
    }
    args.summary.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if queue:
        print(f"error: stopped at {MAX_FUNCTIONS} functions", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
