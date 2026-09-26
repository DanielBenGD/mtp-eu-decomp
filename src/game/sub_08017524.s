.syntax unified
.thumb
.section .text.sub_08017524,"ax",%progbits
.global sub_08017524
.thumb_func
sub_08017524:
    ldr r0, .Lobject
    movs r1, #0x15
    strb r1, [r0, #4]
    bx lr
.Lobject:
    .word 0x020033a4
