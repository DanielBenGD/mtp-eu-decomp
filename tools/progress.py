#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
cfg = json.loads((ROOT / "config/eu.json").read_text())
units = cfg["units"]
matched_bytes = sum(int(u["size"], 0) for u in units)
matched_instructions = sum(u["instruction_count"] for u in units)
print(f"reviewed units: {len(units)}")
print(f"byte-exact source: {matched_bytes} bytes")
print(f"instruction-matched source: {matched_instructions} instructions")
summary = ROOT / "build/analysis/map-summary.json"
if summary.exists():
    mapped = json.loads(summary.read_text())["instruction_addresses"]
    print(f"candidate-map coverage: {matched_instructions}/{mapped} instructions ({matched_instructions/mapped*100:.2f}%)")
else:
    print("candidate-map coverage: run 'make analyze ROM=...' first")
