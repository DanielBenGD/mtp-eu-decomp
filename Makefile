PYTHON ?= python3
ROM ?= baserom_eu.gba

.PHONY: all base target check analyze clean verify
all: base target check
base:
	$(PYTHON) tools/build.py base
target:
	$(PYTHON) tools/build.py target --rom "$(ROM)"
check:
	$(PYTHON) tools/check_match.py
verify:
	$(PYTHON) tools/verify_rom.py "$(ROM)"
analyze: verify
	$(PYTHON) tools/map_functions.py "$(ROM)"
clean:
	rm -rf build
