STATUS: done (informational only — NOT catalog-copy-ready)
AGENT: claude
TICKET: lead (Claude's own capstone spot-check on AA's job — B's sites
07/17 and the hold-length-clear gesture — while waiting for Cursor to
pick up round3-tickets-proposal.md. NOT a Cursor scan.)
UPDATED: 2026-09-23T23:25+01:00
INPUT: firmware-re/firmware-images/keystep37_1.1.6.579_flash.bin (own
disassembly via capstone) + firmware-re/notes/scans/B-shift-ram.txt

**Do not catalog-copy from this file** — same reasoning as
`lead-usb-din.md`. If AA gets scanned properly, that supersedes this.

# Lead: what B's sites 07/17 actually are — a real mechanism, not hold-length-clear

## Finding: `0x200010b4` is a SysTick-decremented countdown, not a static flag

Whole-image literal-pool scan for the value `0x200010b4` found exactly
**3** references — the two already known (sites 07, 17) and a **third,
previously unflagged one at `0x0801827e`/`0x08018286`, inside
`SysTick_Handler`'s own body**, past the point `I-time.md`'s window
stopped disassembling. **S** — directly confirmed:

```
0x8018272  ldr r3,[pc]        ; some other countdown byte
0x8018274  ldrb r3,[r3]
0x8018276  cbz r3, #0x801827e   ; skip if already 0
0x8018278  subs r3,#1
0x801827a  ldr r2,[pc]
0x801827c  strb r3,[r2]         ; decrement, write back
0x801827e  ldr r3,[pc]          ; 0x200010b4
0x8018280  ldrb r3,[r3]
0x8018282  cbz r3, #0x801828a   ; skip if already 0
0x8018284  subs r3,#1
0x8018286  ldr r2,[pc]
0x8018288  strb r3,[r2]         ; decrement 0x200010b4, write back
```

This is a **repeated decrement-if-nonzero pattern applied to a short
list of byte timers**, one per tick, `0x200010b4` being one of several
in the list (at least one neighbor also present, not fully enumerated
here). **`0x200010b4` is a countdown timer, ticked once per SysTick
interrupt** — not a static state byte as earlier tickets' phrasing
implied.

## Finding: site 17 arms the timer, site 07's function checks it, and there's a wrap-around

Site 17 (`0x0801a288`, inside `shift_press_fn`, Oct-adjacent, runs when
Shift is **not** held): sets `0x200010b4 = 6` — arms a 6-tick window.

Site 07 sits inside a **real, separate function**, `0x08016968`
(confirmed clean `push {r3,r4,r5,lr}` entry via direct disassembly —
not in `B-shift-ram.txt`'s original dump, which only showed site 07's
12-insn window mid-function). Full shape:

```
0x08016968  push {r3,r4,r5,lr}
            r4=r0 (object), r5=r1 (a value)
            bl 0x800cc28; if 0 or [r4,#0x10]==0: skip everything
            [r4,#6]=1; [r4,#7]=r5        <- unconditionally records "last press + value"
            if Shift NOT held: skip the counter logic entirely (return)
            if [r4,#0xb]==0: skip (needs a prior trigger too)
            if 0x200010b4==0: skip (window expired)
            [r4,#0xb]++ (cap 3)
            if counter hits 3: re-arm 0x200010b4=6, reset counter to 1 (wrap, not a one-shot action)
```

**S** for the whole shape, directly disassembled. This is a genuine
**press-then-Shift-within-a-window repeat/accumulate mechanism** with a
wrapping counter (1→2→3→re-arm→1...), not a one-shot trigger and not a
simultaneous two-button chord.

## This is NOT the hold-length-clear gesture

Hold-length-clear (`stock-shift-map.md` §4: Shift+Oct−+Oct+ held
together) needs a **simultaneous both-held** check. What's here is a
**sequential timing window** (press something, then Shift-interact
within 6 ticks, repeatable up to 3x with wraparound) — structurally the
wrong shape for "both buttons down at once." **Ruling this location
out** for AA's actual target, same as Y already ruled out sites 15/16.

## What this new mechanism might actually be — H, not confirmed

The wrap-at-3 shape (not a distinct triggered action, just resets)
matches the flavor of `stock-shift-map.md` §2's **"Shift + Chord:
repeat = banks 1-4"** or a similar small-N cycling behavior more than
any Oct-specific gesture. Not confirmed — `fn 0x08016968`'s caller
could not be located: **no static `bl` and no stored Thumb function
pointer (checked at both 4-byte and 2-byte alignment) reference it
anywhere in the image.** It's reached some other way this quick check
didn't find (a computed offset, a table this search missed, or it's
part of the same event-dispatch table `vtable_slot8`/`0x0800e3e8`
already handles generically elsewhere in the catalog).

## Honest status for AA

Both of B's original sites (07, 17) are now fully understood
structurally — a real, previously-unknown countdown/repeat mechanism,
genuinely new territory, not junk. But it's the wrong gesture for
hold-length-clear. **Hold-length-clear remains completely unmapped**
after this pass too. If AA gets a proper Cursor scan, it should search
for a function that reads Oct− (compact index 2) and Oct+ (compact
index 3) state **simultaneously** — nothing found in this session's
spot-check does that.

STATUS: done
