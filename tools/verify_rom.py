#!/usr/bin/env python3
import argparse, hashlib, json, struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "config/eu.json").read_text())

def digest(data, name):
    return hashlib.new(name, data).hexdigest()

def main():
    ap = argparse.ArgumentParser(description="Verify a user-supplied Mario Power Tennis EU ROM")
    ap.add_argument("rom", type=Path)
    args = ap.parse_args()
    data = args.rom.read_bytes()
    got = {
        "rom_size": len(data),
        "md5": digest(data, "md5"),
        "sha1": digest(data, "sha1"),
        "sha256": digest(data, "sha256"),
    }
    title = data[0xA0:0xAC].rstrip(b"\0 ").decode("ascii", "replace") if len(data) >= 0xC0 else ""
    code = data[0xAC:0xB0].decode("ascii", "replace") if len(data) >= 0xC0 else ""
    header_sum = (-sum(data[0xA0:0xBD]) - 0x19) & 0xFF if len(data) >= 0xC0 else -1
    ok = all(got[k] == CFG[k] for k in got)
    ok &= title == CFG["internal_title"] and code == CFG["game_code"]
    ok &= len(data) >= 0xBE and data[0xB2] == 0x96 and data[0xBD] == header_sum
    print(f"title={title} code={code} size={len(data)}")
    for k in ("md5", "sha1", "sha256"): print(f"{k}={got[k]}")
    print(f"header_checksum_valid={len(data) >= 0xBE and data[0xBD] == header_sum}")
    if not ok:
        raise SystemExit("ROM does not match the supported European revision")
    print("ROM verified: Mario Power Tennis (Europe), BTMP, Rev 0")

if __name__ == "__main__": main()
