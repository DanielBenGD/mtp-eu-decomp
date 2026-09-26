.syntax unified
.thumb
.section .text.sub_0801a240,"ax",%progbits
.extern sub_08019ea8
.global sub_0801a240
.thumb_func
sub_0801a240:
    push {lr}
    movs r1, #0
    movs r2, #0
    bl sub_08019ea8
    pop {pc}
