STATUS: done
AGENT: claude
TICKET: O
UPDATED: 2026-09-23T21:06+01:00
INPUT: firmware-re/notes/scans/O-persist.txt

# O-persist — what survives power-cycle vs RAM

Read-only pass over `scans/O-persist.txt` only.

## 1. seq_slot_base — arithmetic re-confirmed exactly

TBB gives all 8 slots explicitly: `0x0803b000 + r1*0x800` for
`r1=0..7`, landing on `0x0803b000`...`0x0803e800`. **S** — matches
`flash-map.md`'s prior "slot 7 `0x0803E800`" claim exactly, an
independent arithmetic re-derivation, not just a repeated assertion.
Three static callers found (`0x0800de16`, `0x0800de96`, `0x0800e21a`) —
none walked further in this scan; new addresses for whoever traces
"who reads a slot" next.

## 2. FLASH IRQ4 — entry only, second callee's field shape matches a G-ticket object

`0x080186d4` calls `0x08008140` (ST-library territory, correctly not
walked per instruction) then `0x0800dd8c(r0=*0x20001154)`. That second
function's field shape — `[r0,#0x800]` (byte, cbz/cmp `#1`), then
`[r0,#0x802]`/`[r0,#0x804]` (halfwords, compared) — **matches
`G-objects.md`'s site-46 object exactly** (`0x200007dc`, ctor
`0x0800dd04`: `+0x800` byte, `+0x801` byte, `+0x802` halfword,
`+0x808` word). Not proven to be the *same* RAM address (`*0x20001154`
is a pointer, not shown to resolve to `0x200007dc` specifically), but
the field layout is identical. **S** for the shape match; **H** for
literal object identity.

## 3. Settings pointer — closes an existing catalog gap

`0x20001170` has **exactly one store** in the whole search window,
writing the literal `0x200004f4` — **which is `mode_skip_apply`'s own
object** (`G-objects.md`, site 15). This directly closes
`address-catalog.md`'s RAM table row "`0x20001170` — Pointer to
settings object (Mode at `*ptr + 0x55`)," which previously had no
confirmed target address. **The "settings object" is the Mode object,
not a separate generic settings block.** **S.**

Both reads of `*0x20001170` feed `mode_byte_get` (`0x08005ccc`) — one
compared against `8` (matches the existing catalog's "except when
`+0x55==8`, no CC" note), the other feeding directly into
`set_arp_mode` via `mode_knob_apply`'s own already-documented sequence.
This scan re-derives `mode_knob_apply`'s plumbing from scratch and it
matches the existing catalog exactly — a clean cross-check, not a new
claim.

## 4. What survives power-cycle vs RAM — the honest answer

`seq_step_store`'s `+0x400/+0x401/+0x402` writes (ticket L) land on a
**RAM staging block** reached via `*0x200010fc`, not on the flash slot
base directly. This scan searched `0x0800dd30`-`0x0800e400` (the slot-
base function and its neighborhood) for any load/store of flash offset
`+0x400` and found none. **The two are confirmed to be different
objects** — L's writes are session/RAM state, not yet shown to reach
flash. **No mechanism that commits RAM sequence state to the flash
slots (`0x0803B000+`) has been found by any ticket so far.** This is a
real, explicit gap, not a modeling failure: state that "survives power-
cycle" is currently **unconfirmed** for anything; state that is
"RAM-only, confirmed" is the `seq_step_store` staging block.

## Net for HANDOFF layer (settings + persist)

Slot base: fully confirmed, arithmetic re-verified. Settings pointer:
closed — it's the Mode object. Persistence mechanism (RAM → flash
commit): open, and now framed precisely (the FLASH IRQ4 entry point is
known; its actual write path through the ST HAL is correctly left
unwalked per instruction) — a concrete, bounded next step rather than
an open-ended search.

STATUS: done
