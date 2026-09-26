.syntax unified
.thumb
.section .text.sub_0801aca0,"ax",%progbits
.global sub_0801aca0
.thumb_func
sub_0801aca0:
    movs r1, #0xa0
    lsls r2, r1, #3
    adds r2, #0x79
    adds r1, r0, r2
    ldrb r0, [r1]
    bx lr
