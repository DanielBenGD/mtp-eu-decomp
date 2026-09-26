.syntax unified
.thumb
.section .text.sub_08016678,"ax",%progbits
.global sub_08016678
.thumb_func
sub_08016678:
    movs r1, #0xc0
    lsls r2, r1, #2
    adds r2, #0xad
    adds r1, r0, r2
    ldrb r0, [r1]
    bx lr
