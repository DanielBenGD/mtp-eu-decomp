# Mario Power Tennis (GBA, Europe) matching decompilation

A clean, code-only matching-decompilation project for the European Game Boy
Advance release of **Mario Power Tennis** (`BTMP`, revision 0), known as
*Mario Tennis: Power Tour* in North America.

## Important

This repository does **not** contain a ROM, game assets, extracted data, or
Nintendo/Camelot binaries. You must provide your own legally obtained dump.
Generated target files and analysis reports stay under ignored `build/` paths.

## Supported ROM

| Field | Value |
|---|---|
| Internal title | `MARIOTENNISA` |
| Game code | `BTMP` |
| Region / revision | Europe / 0 |
| Size | 16,777,216 bytes |
| MD5 | `f6c0a645317d6ed90abc4e04f7b33b46` |
| SHA-1 | `d61990974040d405b5bf8436ac8e1e0beb0f7964` |
| SHA-256 | `0a27490e4cfa8ea137b82d9157bc647c8b6df132f98b85999934d9b8784af622` |

## Requirements

- Python 3.10+
- `clang` with the `arm-none-eabi` target
- `ld.lld`
- `llvm-objcopy`
- Optional analysis tools: `pip install -r requirements-analysis.txt`
- Optional diff viewer: [objdiff](https://github.com/encounter/objdiff)

## Build and verify

Place your dump at `baserom_eu.gba` or pass `ROM=/path/to/file.gba`:

```sh
make verify
make all
```

Without a ROM, CI builds every clean source unit and checks it against reviewed
SHA-256 values derived from the supported ROM:

```sh
make base
python3 tools/check_match.py --base-only
```

Current verified result: **4 units, 160/160 bytes matching**.


## Build targets

### GBA hybrid rebuild

`make gba ROM=/path/to/mariopowertenniseudump.gba` verifies the EU dump,
assembles every reviewed clean-source unit, and inserts those units into a local
copy of the user-provided ROM. The current output is byte-identical and playable
on GBA hardware/emulators. Undecompiled code and assets still come from the
user's ROM and are never committed.

### Native PC runtime

`make pc` builds `build/pc/mpt_pc`. The runtime validates the EU ROM and provides
the initial GBA memory map needed by translated functions. Linux and Windows
x86 builds are covered by GitHub Actions. **Gameplay is not translated yet**;
the PC target currently initializes and exits rather than running the game.

This distinction is intentional: the GBA target is playable now as a hybrid
matching rebuild, while the native PC port becomes playable as game functions,
video, audio, input, timing, and save support are implemented.

## Function mapping

The mapper follows direct ARM/Thumb calls from reviewed entry points and writes
metadata only. Its reports are ignored because they are generated from the
user's ROM:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-analysis.txt
.venv/bin/python tools/map_functions.py baserom_eu.gba
```

Current conservative pass reaches 148 candidate functions (2 ARM, 146 Thumb)
from `_start`, the IRQ dispatcher, and `AgbMain`. Candidate boundaries remain
heuristic until manually reviewed and are not used as the progress denominator.

## objdiff and decomp.dev

After `make all`, open this repository in objdiff using `objdiff.json`. Target
objects are generated locally from the user-supplied ROM and are never tracked.
The repository is structurally ready for objdiff; a decomp.dev listing should be
requested only after a complete reviewed code map makes the global percentage
truthful.

## Legal

This is an unofficial reverse-engineering project. Mario, Mario Power Tennis,
Nintendo, Camelot, and related names are property of their respective owners.
No game files are distributed.
