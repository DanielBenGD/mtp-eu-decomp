# Project status

## Supported version

- Mario Power Tennis (Europe)
- Game code: `BTMP`
- Revision: 0
- ROM size: 16 MiB

## Verified matching source

| Unit | Address | Size | Category | Status |
|---|---:|---:|---|---|
| Reset/startup (`crt0`) | `0x08000470` | 68 bytes | Boot | Matching |
| IWRAM veneers | `0x08002190` | 32 bytes | SDK | Matching |
| IRQ acknowledgement helpers | `0x08013288` | 40 bytes | SDK | Matching |
| IRQ callback setter | `0x080150FC` | 20 bytes | SDK | Matching |
| **Total** | — | **160 bytes** | — | **4/4 units** |

CI assembles all clean units without a ROM and verifies their reviewed target
hashes. A local legal dump enables byte-for-byte base/target comparison.

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
6. Publish the GitHub repository, then request its decomp.dev listing.
