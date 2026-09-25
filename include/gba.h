#ifndef MPT_GBA_H
#define MPT_GBA_H

#include <stdint.h>

#define REG_BASE        0x04000000u
#define REG_IME         (*(volatile uint16_t *)(REG_BASE + 0x208u))
#define REG_IE          (*(volatile uint16_t *)(REG_BASE + 0x200u))
#define REG_IF          (*(volatile uint16_t *)(REG_BASE + 0x202u))
#define IRQ_VECTOR      (*(volatile uintptr_t *)0x03007FFCu)

#endif
