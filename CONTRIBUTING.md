# Contributing

- Never commit ROMs, extracted graphics/audio, or generated target binaries.
- Work from a legally obtained European `BTMP` revision 0 dump.
- Run `make verify`, `make all`, and objdiff before opening a pull request.
- Run `make analyze` when changing function seeds or mapping logic.
- Treat generated function boundaries as candidates until manually reviewed.
- Decompiled functions should be readable source, not pasted disassembler output.
- Keep temporary nonmatching assembly under ignored `build/` output until the
  repository adopts a reviewed policy for assembly fallbacks.
