STATUS: done
AGENT: claude
TICKET: AH
UPDATED: 2026-09-23T23:50+01:00
INPUT: firmware-re/notes/scans/AH-10638.txt

# AH-usb-decode — 0x080150a4's containing function, found

Read-only pass over `scans/AH-10638.txt` only.

## 1. Containing function closed — an open item since ticket C

`C-loop.md` flagged `0x080150a4` (the sole static caller of
`0x08010638`, "USB packet decode") as "itself uncharacterized." This
scan closes it: walking backward for the nearest `push {..,lr}` before
`0x080150a4` (stopping correctly at any `bx`/`pop`, none found in
between) lands on **`0x0801509a`**:

```
0x0801509a  push {r4, lr}
0x0801509c  mov  r4, r1
0x0801509e  mov  r1, r0
0x080150a0  ldrh r2, [r4]
0x080150a2  mov  r0, r3
0x080150a4  bl   #0x8010638
0x080150a8  movs r3, #0
0x080150aa  strh r3, [r4]
0x080150ac  pop  {r4, pc}
```

**S** — a small, complete function: takes 3 incoming values (`r0`→`r3`
position at call time, `r1`, and a halfword read from `[r4]` where
`r4=r1`), calls `0x08010638`, then zeroes the halfword it just read
before returning. This is a **read-modify-clear pattern on a 16-bit
field**, consistent with `0x08010638` itself being described elsewhere
as writing into a byte ring — this wrapper looks like "consume one
ring entry: call the decoder, then clear the slot."

Also closes the earlier flagged sibling: `0x080150ae` (`bx lr`,
immediately after this function's `pop`) is a **separate, unrelated
1-instruction stub**, not part of this function — confirms the
boundary is exactly `0x0801509a`-`0x080150ac`.

## 2. bl-to 0x08010638 — reconfirms, doesn't expand

Still exactly **1** static caller (`0x080150a4`), matching every prior
ticket (C, J, Q). **S.**

## 3. Thumb pointer search — honest negative, second time

No stored Thumb pointer (`0x08010639`) found anywhere in the image.
**S** for the negative — this function is either called only via the
one static `bl` already known (meaning something calls `0x0801509a`
itself, not found in this scan's scope), or reached through a
mechanism this search method doesn't catch (a computed offset, not a
literal). Same open-ended caveat as `lead-oct-combo.md`'s similar
negative result for `0x08016968` — worth noting as a recurring
limitation of the static Thumb-pointer search method, not a
per-ticket failure.

## Net

The immediate open item (`0x080150a4`'s containing function) is
closed: it's `0x0801509a`, a clean 4-argument read/decode/clear
wrapper. The *next* open item — who calls `0x0801509a` — is new, not
previously flagged, and unresolved by this scan.

STATUS: done
