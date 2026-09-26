.syntax unified
.thumb
.section .text.sub_0801c688,"ax",%progbits

.macro setter name, offset
.global \name
.thumb_func
\name:
    ldr r1, 1f
    ldr r1, [r1]
    str r0, [r1, #\offset]
    bx lr
1:
    .word 0x020033f0
.endm

setter sub_0801c688, 0x18
setter sub_0801c694, 0x1c
setter sub_0801c6a0, 0x20
