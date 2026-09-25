/* Two small Thumb IRQ acknowledgement helpers at ROM 0x08013288. */
.syntax unified
.thumb
.section .text.irq_ack_helpers, "ax", %progbits

.global irq_ack_and_dispatch
.thumb_func
irq_ack_and_dispatch:
    movs r4, #3
    lsls r4, r4, #24
    ldr r1, [r0, r4]
    lsrs r3, r1, #22
    beq 1f
    movs r2, #0
    str r2, [r0, r4]
    movs r0, #4
    ands r3, r0
    str r1, [r3, r4]
1:
    bx lr
    .hword 0 /* original alignment padding */

.global irq_ack
.thumb_func
irq_ack:
    movs r4, #3
    lsls r4, r4, #24
    movs r1, #4
    lsrs r2, r0, #22
    ands r2, r1
    str r0, [r2, r4]
    bx lr
    .hword 0 /* original alignment padding */
