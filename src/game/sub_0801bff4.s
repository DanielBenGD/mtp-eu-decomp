.syntax unified
.thumb
.section .text.sub_0801bff4,"ax",%progbits
.extern ram_veneer_0300052c
.global sub_0801bff4
.thumb_func
sub_0801bff4:
    push {lr}
    bl ram_veneer_0300052c
    pop {pc}
