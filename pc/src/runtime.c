#include "mpt_runtime.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define EXPECTED_ROM_SIZE 0x01000000u

static uint8_t *region(MptRuntime *r, uint32_t address, size_t *remaining) {
    uint32_t offset;
    switch (address >> 24) {
    case 0x02:
        offset = address & 0x3FFFFu; *remaining = sizeof(r->ewram) - offset; return r->ewram + offset;
    case 0x03:
        offset = address & 0x7FFFu; *remaining = sizeof(r->iwram) - offset; return r->iwram + offset;
    case 0x04:
        offset = address & 0x3FFu; *remaining = sizeof(r->io) - offset; return r->io + offset;
    case 0x05:
        offset = address & 0x3FFu; *remaining = sizeof(r->palette) - offset; return r->palette + offset;
    case 0x06:
        offset = address & 0x1FFFFu;
        if (offset >= sizeof(r->vram)) offset -= 0x8000u;
        *remaining = sizeof(r->vram) - offset; return r->vram + offset;
    case 0x07:
        offset = address & 0x3FFu; *remaining = sizeof(r->oam) - offset; return r->oam + offset;
    case 0x08: case 0x09:
        offset = address - 0x08000000u;
        if (offset < r->rom_size) { *remaining = r->rom_size - offset; return r->rom + offset; }
        break;
    }
    *remaining = 0;
    return NULL;
}

int mpt_runtime_init(MptRuntime *r, const char *path) {
    FILE *file;
    long size;
    memset(r, 0, sizeof(*r));
    file = fopen(path, "rb");
    if (!file) return 0;
    if (fseek(file, 0, SEEK_END) || (size = ftell(file)) < 0 || fseek(file, 0, SEEK_SET)) { fclose(file); return 0; }
    if ((size_t)size != EXPECTED_ROM_SIZE) { fclose(file); return 0; }
    r->rom = (uint8_t *)malloc((size_t)size);
    if (!r->rom) { fclose(file); return 0; }
    r->rom_size = (size_t)size;
    if (fread(r->rom, 1, r->rom_size, file) != r->rom_size) { fclose(file); mpt_runtime_destroy(r); return 0; }
    fclose(file);
    if (memcmp(r->rom + 0xA0, "MARIOTENNISA", 12) || memcmp(r->rom + 0xAC, "BTMP", 4)) {
        mpt_runtime_destroy(r); return 0;
    }
    return 1;
}

void mpt_runtime_destroy(MptRuntime *r) {
    free(r->rom);
    r->rom = NULL;
    r->rom_size = 0;
}

uint8_t mpt_read8(MptRuntime *r, uint32_t address) {
    size_t remaining;
    uint8_t *p = region(r, address, &remaining);
    return remaining ? *p : 0;
}

void mpt_write8(MptRuntime *r, uint32_t address, uint8_t value) {
    size_t remaining;
    uint8_t *p = region(r, address, &remaining);
    if (remaining && (address >> 24) < 0x08) *p = value;
}
