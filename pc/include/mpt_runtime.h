#ifndef MPT_RUNTIME_H
#define MPT_RUNTIME_H

#include <stddef.h>
#include <stdint.h>

typedef struct MptRuntime {
    uint8_t *rom;
    size_t rom_size;
    uint8_t ewram[0x40000];
    uint8_t iwram[0x8000];
    uint8_t io[0x400];
    uint8_t palette[0x400];
    uint8_t vram[0x18000];
    uint8_t oam[0x400];
} MptRuntime;

int mpt_runtime_init(MptRuntime *runtime, const char *rom_path);
void mpt_runtime_destroy(MptRuntime *runtime);
uint8_t mpt_read8(MptRuntime *runtime, uint32_t address);
void mpt_write8(MptRuntime *runtime, uint32_t address, uint8_t value);

#endif
