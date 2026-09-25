PYTHON ?= python3
CC ?= cc
ROM ?= baserom_eu.gba

.PHONY: all base target gba pc check analyze clean verify
all: base target check
base:
	$(PYTHON) tools/build.py base
target:
	$(PYTHON) tools/build.py target --rom "$(ROM)"
gba:
	$(PYTHON) tools/build_gba.py "$(ROM)"
pc:
	mkdir -p build/pc
	$(CC) -std=c99 -O2 -Wall -Wextra -Wpedantic -Ipc/include pc/src/main.c pc/src/runtime.c -o build/pc/mpt_pc
check:
	$(PYTHON) tools/check_match.py
verify:
	$(PYTHON) tools/verify_rom.py "$(ROM)"
analyze: verify
	$(PYTHON) tools/map_functions.py "$(ROM)"
clean:
	rm -rf build
