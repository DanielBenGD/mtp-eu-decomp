# Project status

## Supported version

- Mario Power Tennis (Europe)
- Game code: `BTMP`
- Revision: 0
- ROM size: 16 MiB

## Verified matching source

| Unit group | Units | Instructions | Bytes | Status |
|---|---:|---:|---:|---|
| Boot | 1 | 13 | 68 | Instruction + byte match |
| SDK/runtime | 6 | 51 | 156 | Instruction + byte match |
| Game leaf routines | 5 | 30 | 60 | Instruction + byte match |
| **Total** | **12** | **94/94** | **284/284** | **100% reviewed accuracy** |

`tools/check_instructions.py` compares normalized ARM/Thumb instruction streams
for reviewed code ranges. `tools/check_match.py` separately verifies every byte,
including literal pools and padding. A local legal dump enables target checks;
CI validates clean source against reviewed hashes without containing the ROM.

### Coverage versus accuracy

- Reviewed instruction accuracy: **94/94 (100%)**
- Coverage of the current heuristic map: **94/8,877 (1.06%)**
- Whole-game coverage: **not claimed yet**, because the complete code denominator
  has not been established

## Buildability

- **GBA:** playable hybrid rebuild; 284 bytes currently come from clean matching
  source and the remaining undecompiled code/data comes from the legal base ROM.
- **PC:** native C99 runtime builds on Linux and Windows x86, validates the EU
  ROM, and implements the initial GBA memory regions. Gameplay execution, GPU,
  audio, input, timing, and saves remain to be translated.

## Code-map milestone

`tools/map_functions.py` performs conservative recursive ARM7TDMI discovery
from three reviewed seeds. On the supported EU ROM, the current pass reaches:

- 148 candidate functions
- 2 ARM and 146 Thumb candidates
- 8,877 unique decoded instruction addresses
- 234 direct call edges
- 138 candidates ending without a mapper warning

This is analysis coverage, not decompilation progress. Every candidate must be
reviewed before it is promoted to an objdiff unit or counted on decomp.dev.

## Next technical milestones

1. Review and extend ARM/Thumb boundaries, especially indirect calls and IRQ
   interworking stubs.
2. Identify compiler and runtime-library signatures.
3. Separate SDK/library code from Camelot game code.
4. Convert leaf routines from matching assembly to readable matching C.
5. Build the complete code denominator and generate an objdiff progress report.
6. Generate a complete instruction denominator, then publish an objdiff report and request the decomp.dev listing.
