/* Thumb veneers for routines copied to IWRAM during startup. */
.syntax unified
.thumb
.section .text.ram_veneers, "ax", %progbits

.macro ram_veneer name, target
.global \name
.thumb_func
\name:
    ldr r3, 1f
    bx r3
1:
    .word \target
.endm

ram_veneer ram_veneer_0300052c, 0x0300052c
ram_veneer ram_veneer_03000538, 0x03000538
ram_veneer ram_veneer_0300050c, 0x0300050c
ram_veneer ram_veneer_03000518, 0x03000518
