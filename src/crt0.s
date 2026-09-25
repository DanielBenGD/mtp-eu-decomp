/*
 * Mario Power Tennis (Europe) — reset/startup routine at ROM 0x08000470.
 * Clean source implementation; assembles byte-identically with LLVM's ARM
 * assembler after final linking resolves the branch back to _start.
 */
.syntax unified
.arm
.section .text.startup, "ax", %progbits
.global _start
.type _start, %function
_start:
    mov r0, #0x12
    msr cpsr_fc, r0
    ldr sp, .Lirq_stack

    mov r0, #0x1f
    msr cpsr_fc, r0
    ldr sp, .Lsystem_stack

    ldr r1, .Lirq_vector
    add r0, pc, #0x278
    str r0, [r1]

    ldr r1, .Lmain_entry
    mov lr, pc
    bx r1
    b _start

.Lsystem_stack:
    .word 0x03007f00
.Lirq_stack:
    .word 0x03007fa0
.Lirq_vector:
    .word 0x03007ffc
.Lmain_entry:
    .word 0x08013349
.size _start, . - _start
