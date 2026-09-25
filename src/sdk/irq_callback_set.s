/* Store one IRQ callback in both mirrored work-RAM slots. */
.syntax unified
.thumb
.section .text.irq_callback_set, "ax", %progbits

.global irq_callback_set
.thumb_func
irq_callback_set:
    ldr r1, .Lslot1
    str r0, [r1]
    ldr r1, .Lslot2
    str r0, [r1]
    bx lr
    .hword 0 /* original alignment padding */
.Lslot1:
    .word 0x03001364
.Lslot2:
    .word 0x030012b0
