.syntax unified
.thumb
.section .text.bios_wrappers,"ax",%progbits
.global bios_cpu_fast_set
.thumb_func
bios_cpu_fast_set:
    svc #0x0b
    bx lr

.global bios_sound_bias_reset
.thumb_func
bios_sound_bias_reset:
    movs r0, #0
    svc #0x19
    bx lr
    .hword 0

.global bios_sound_bias_set
.thumb_func
bios_sound_bias_set:
    movs r0, #1
    svc #0x19
    bx lr
    .hword 0
