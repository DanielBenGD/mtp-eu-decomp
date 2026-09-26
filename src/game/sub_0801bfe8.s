.syntax unified
.thumb
.section .text.sub_0801bfe8,"ax",%progbits
.global sub_0801bfe8
.thumb_func
sub_0801bfe8:
    movs r1, #0x80
    lsls r2, r1, #4
    adds r2, #0x2d
    adds r1, r0, r2
    ldrb r0, [r1]
    bx lr
