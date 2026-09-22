@ KeyStep 37 patch page at 0x0801F400. Cortex-M3 Thumb-2.
@ --defsym FEAT_LATCH=0/1 FEAT_HITS_SLOT=0/1 FEAT_SHIFT=0/1
@ --defsym FEAT_CHORD=0/1 FEAT_FLAVOUR=0/1 FEAT_PITCH_GATE=0/1
@
@ FEAT_PITCH_GATE (2026-09-22): alternative hook, NOT wired into any
@ existing build level yet. Confirmed by direct disassembly that
@ seq_step_gate (hooked by euclid_wrap above) is consumed only by
@ tie/retention bookkeeping (seq_step_release's fallback, and a cached-
@ pitch retention flag inside play_time_step) - never the note-emission
@ decision. The real "does this step attempt a note at all" gate is
@ voice 0's pitch byte, read via seq_step_note and checked in
@ play_time_step at 0x08013ebc-0x08013ecc: (pitch+0x7f)&0xff<=1, true
@ exactly for pitch==0x81 or 0x82, triggers an immediate return. This
@ hook replaces the single seq_step_note call at 0x08013ec2 with a
@ wrapper that calls the original, and - only for a pitch that is not
@ already a native tie(0x81)/rest(0x82) - substitutes 0x82 on a
@ Euclidean miss, reusing that exact existing early-return path rather
@ than inventing new state.
@
@ Built as e0b, flashed, hardware-tested 2026-09-22: the rhythm produced
@ was slot-dependent (different sequence slots gave different, but each
@ internally consistent, repeating patterns - neither the intended
@ 3-in-8). Confirmed by direct disassembly of play_time_step's two
@ callers: the "step" argument fed to euclid_gate below was the native
@ engine's own live step-position field (block+0x38, wrap-checked
@ against a length field at block+0x10) for whichever sequence block is
@ currently active - not an independent counter this patch controlled.
@ Fixed by maintaining our own free-running counter in STEP_CTR_RAM,
@ incremented once per real (non-tie/rest) call, and gating on that
@ instead - makes the rhythm self-contained regardless of which slot is
@ loaded. See docs/HANDOFF.md and firmware-re/notes/
@ findings-2026-09-20.md ("Root cause of the slot-dependence, confirmed
@ by direct disassembly", 2026-09-22).
    .syntax unified
    .thumb
    .cpu cortex-m3
    .ifndef FEAT_LATCH
    .equ FEAT_LATCH, 0
    .endif
    .ifndef FEAT_HITS_SLOT
    .equ FEAT_HITS_SLOT, 0
    .endif
    .ifndef FEAT_SHIFT
    .equ FEAT_SHIFT, 0
    .endif
    .ifndef FEAT_CHORD
    .equ FEAT_CHORD, 0
    .endif
    .ifndef FEAT_FLAVOUR
    .equ FEAT_FLAVOUR, 0
    .endif
    .ifndef FEAT_PITCH_GATE
    .equ FEAT_PITCH_GATE, 0
    .endif

    .equ SEQ_STEP_GATE, 0x080130F5
    .equ SEQ_STEP_NOTE, 0x080130E9
    .equ NOTEVAL,       0x0801C3CB
    .equ FLAG_RAM,      0x20005F00
    .equ FLAVOUR_RAM,   0x20005F01
    .equ STEP_CTR_RAM,  0x20005F02
    .equ EVENT_PP,      0x20001120
    .equ VOICE_OBJ,     0x200051CC
    .equ SCALE_MASK,    0x20001E3A
    .equ KEY_ON,        36
    .equ KEY_OFF,       37

    .global euclid_wrap
    .type euclid_wrap, %function
euclid_wrap:
    push    {r4, r5, r6, r7, lr}
    mov     r4, r0
    mov     r5, r1
    mov     r6, r2
    ldr     r3, =SEQ_STEP_GATE
    blx     r3
    mov     r7, r0
.if FEAT_LATCH
    ldr     r0, =FLAG_RAM
    ldrb    r0, [r0]
    cmp     r0, #0
    beq     .Lpass
.endif
.if FEAT_HITS_SLOT
    ldr     r3, [r4]
    ldrb    r1, [r3, #0x400]
    cmp     r1, #0
    bne     1f
    movs    r1, #8
1:
    cmp     r1, #0x40
    it      hi
    movhi   r1, #0x40
    movs    r2, #0
    movs    r0, #0
.Lcount:
    push    {r0, r1, r2}
    mov     r1, r0
    movs    r2, #0
    mov     r0, r4
    ldr     r3, =SEQ_STEP_GATE
    blx     r3
    mov     r3, r0
    pop     {r0, r1, r2}
    cmp     r3, #0x82
    beq     .Lnext
    tst     r3, #0x80
    beq     .Lnext
    adds    r2, #1
.Lnext:
    adds    r0, #1
    uxtb    r0, r0
    cmp     r0, r1
    blo     .Lcount
    mov     r0, r5
    bl      euclid_gate
.else
    mov     r0, r5
    movs    r1, #8
    movs    r2, #3
    bl      euclid_gate
.endif
    cmp     r0, #0
    bne     .Lpass
    bic     r7, r7, #0x80
.Lpass:
    mov     r0, r7
    pop     {r4, r5, r6, r7, pc}

    .global euclid_gate
    .type euclid_gate, %function
euclid_gate:
    @ r0=step r1=length r2=hits -> r0=0|1
    cmp     r1, #0
    beq     .Lone
    cmp     r2, #0
    beq     .Lzero
    cmp     r2, r1
    bge     .Lone
    udiv    r3, r0, r1
    mls     r0, r3, r1, r0
    mul     r0, r0, r2
    udiv    r3, r0, r1
    mls     r0, r3, r1, r0
    cmp     r0, r2
    ite     lo
    movlo   r0, #1
    movhs   r0, #0
    bx      lr
.Lone:
    movs    r0, #1
    bx      lr
.Lzero:
    movs    r0, #0
    bx      lr

.if FEAT_SHIFT
    .global shift_note_hook
    .type shift_note_hook, %function
shift_note_hook:
    mov     sb, r2
    mov     r4, r3
    push    {r0, r1, r2, r3, r5, lr}
    ldr     r0, =EVENT_PP
    ldr     r0, [r0]
    cmp     r0, #0
    beq     .Lsout
    ldrb    r0, [r0, #0x25]
    cmp     r0, #0
    beq     .Lsout
    mov     r2, r1
    and     r2, r2, #0xF0
    cmp     r2, #0x90
    bne     .Lsout
    lsrs    r2, r1, #8
    uxtb    r2, r2
    ldr     r5, =FLAG_RAM
    cmp     r2, #KEY_ON
    bne     2f
    movs    r0, #1
    strb    r0, [r5]
    b       .Lsout
2:
    cmp     r2, #KEY_OFF
    bne     .Lsout
    movs    r0, #0
    strb    r0, [r5]
.Lsout:
    pop     {r0, r1, r2, r3, r5, pc}
.endif

.if FEAT_CHORD
    .global noteval_then_snap
    .type noteval_then_snap, %function
noteval_then_snap:
    push    {r4, lr}
    ldr     r3, =NOTEVAL
    blx     r3
    mov     r4, r0
    ldr     r0, =VOICE_OBJ
    ldrb    r1, [r0, #0x4d]
    cmp     r1, #0
    beq     .Lnosnap
.if FEAT_FLAVOUR
    ldr     r0, =FLAVOUR_RAM
    ldrb    r0, [r0]
    cmp     r0, #64
    bhi     .Lnosnap
.endif
    ldr     r0, =SCALE_MASK
    ldrh    r1, [r0]
    movw    r2, #0x0FFF
    cmp     r1, r2
    beq     .Lnosnap
    mov     r0, r4
    bl      snap_scale
    pop     {r4, pc}
.Lnosnap:
    mov     r0, r4
    pop     {r4, pc}

    .global snap_scale
    .type snap_scale, %function
snap_scale:
    push    {r4, r5, r6, r7, lr}
    mov     r4, r0
    mov     r5, r1
    movs    r1, #12
    sdiv    r2, r0, r1
    mls     r6, r2, r1, r0
    lsrs    r2, r5, r6
    tst     r2, #1
    bne     .Ldone_in
    movs    r7, #1
.Lsrch:
    add     r3, r6, r7
    cmp     r3, #12
    bge     1f
    lsrs    r2, r5, r3
    tst     r2, #1
    beq     1f
    add     r0, r4, r7
    b       .Ldone
1:
    subs    r3, r6, r7
    bmi     2f
    lsrs    r2, r5, r3
    tst     r2, #1
    beq     2f
    subs    r0, r4, r7
    b       .Ldone
2:
    adds    r7, #1
    cmp     r7, #12
    blo     .Lsrch
    mov     r0, r4
    b       .Ldone
.Ldone_in:
    mov     r0, r4
.Ldone:
    uxtb    r0, r0
    pop     {r4, r5, r6, r7, pc}
.endif

.if FEAT_FLAVOUR
    .global type_strb_hook
    .type type_strb_hook, %function
type_strb_hook:
    push    {r2, r3, lr}
    ldr     r2, =EVENT_PP
    ldr     r2, [r2]
    cmp     r2, #0
    beq     .Lorigt
    ldrb    r2, [r2, #0x25]
    cmp     r2, #0
    beq     .Lorigt
    ldr     r3, =FLAVOUR_RAM
    strb    r1, [r3]
    pop     {r2, r3, pc}
.Lorigt:
    strb.w  r1, [r0, #0x4f]
    pop     {r2, r3, pc}
.endif

.if FEAT_PITCH_GATE
    @ Replaces the single seq_step_note call at 0x08013ec2 (voice-0
    @ master gate read inside play_time_step). Same args as the
    @ original: r0=obj (first word = slot data), r1=step, r2=voice(0).
    .global pitch_gate_wrap
    .type pitch_gate_wrap, %function
pitch_gate_wrap:
    push    {r4, r5, r6, lr}
    mov     r4, r0              @ obj (needed after seq_step_note returns)
    ldr     r3, =SEQ_STEP_NOTE
    blx     r3
    mov     r5, r0
    adds    r0, #0x7f
    uxtb    r0, r0
    cmp     r0, #1
    bls     .Lpgkeep            @ already native tie(0x81)/rest(0x82): untouched
.if FEAT_LATCH
    ldr     r0, =FLAG_RAM
    ldrb    r0, [r0]
    cmp     r0, #0
    beq     .Lpgkeep            @ unarmed: stock pitch, counter frozen
.endif
.if FEAT_HITS_SLOT
    @ length = slot[+0x400], default 8, clamp 64. hits = voice-0 pitches
    @ that are not 0x81/0x82/0xFF. Same contract as old E1, in the pitch
    @ domain (seq_step_gate bit 7 is not a note gate).
    ldr     r3, [r4]
    ldrb    r1, [r3, #0x400]
    cmp     r1, #0
    bne     1f
    movs    r1, #8
1:
    cmp     r1, #0x40
    it      hi
    movhi   r1, #0x40
    movs    r2, #0              @ hits
    movs    r0, #0              @ i
.Lpgcount:
    push    {r0, r1, r2}
    mov     r1, r0
    movs    r2, #0
    mov     r0, r4
    ldr     r3, =SEQ_STEP_NOTE
    blx     r3
    mov     r3, r0
    pop     {r0, r1, r2}
    cmp     r3, #0xff
    beq     .Lpgnext
    adds    r6, r3, #0x7f
    uxtb    r6, r6
    cmp     r6, #1
    bls     .Lpgnext
    adds    r2, #1
.Lpgnext:
    adds    r0, #1
    uxtb    r0, r0
    cmp     r0, r1
    blo     .Lpgcount
    ldr     r3, =STEP_CTR_RAM
    ldrb    r0, [r3]
    bl      euclid_gate
.else
    ldr     r3, =STEP_CTR_RAM
    ldrb    r0, [r3]
    movs    r1, #8
    movs    r2, #3
    bl      euclid_gate         @ gate on OUR counter, not the native step arg
.endif
    ldr     r3, =STEP_CTR_RAM   @ r3 clobbered by the call above; reload
    ldrb    r1, [r3]
    adds    r1, #1
    uxtb    r1, r1
    strb    r1, [r3]
    cmp     r0, #0
    bne     .Lpgkeep            @ hit: pass the real pitch through
    movs    r5, #0x82           @ miss: reuse the existing "no new note" path
.Lpgkeep:
    mov     r0, r5
    pop     {r4, r5, r6, pc}
.endif
    .ltorg
