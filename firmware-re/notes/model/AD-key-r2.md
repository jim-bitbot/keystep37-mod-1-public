STATUS: done
AGENT: claude
TICKET: AD
UPDATED: 2026-09-24T00:05+01:00
INPUT: firmware-re/notes/scans/AD-key-r2.txt

# AD-key-r2 — sb isn't a boolean, it's a shift amount into a bitmask

Read-only pass over `scans/AD-key-r2.txt` only. This reframes
`E-keys.md`'s "r2=0 physical / r2=1 MIDI" claim rather than confirming
it as stated.

## 1. The four call sites — literals reconfirmed, nothing new here

Same as `E-keys.md`/`R-usbdin.txt`: 3 sites inside `key_scan` pass
`r2=0`, the 4th (unnamed containing fn, `0x08010326`) passes `r2=1`.
**S**, unchanged.

## 2. The first real read of `sb` — a shift amount, not a compare

`0x0801b750`'s incoming `r2` is saved to `sb` at entry
(`0x0801b75a`) and **not read again until `0x0801b8b2`**, deep inside
the function, in this shape:

```
0x0801b8b0  movs r2, #1
0x0801b8b2  lsl.w r2, r2, sb      <- r2 = 1 << sb
0x0801b8b6  uxtb r2, r2
0x0801b8b8  ldr  r0, [r6]
0x0801b8ba  bl   #0x801b460
```

**This is a "build a one-hot bitmask from an index" pattern**
(`1 << sb`), not a boolean branch. `sb` is being used as a **bit
position**, not tested for equality against 0 or 1. **S** — directly
shown.

## 2a. What this means for the "physical vs MIDI" claim

The existing catalog's claim (external source, `E-keys.md` kept at H)
is "`r2=0` from physical key scanner, `r2=1` from either MIDI port" —
phrased as a two-state boolean. **This scan's evidence is consistent
with `sb` being a boolean in practice** (only 0 and 1 are ever passed
by the four known callers) **but the mechanism that consumes it treats
it as a general bit-index**, building a mask that could in principle
represent more than two states (up to 32 with a 32-bit register). This
directly supports **`lead-usb-din.md`'s independent finding**: the same
function region builds per-source ownership bitmasks — this is very
likely the exact mechanism behind the catalog's "cross-port/channel
pitch tracker" (`0x20001ebc`) claim, now tied to a concrete instruction
rather than just an address. **Promoting the *mechanism* (bit-index
into an ownership mask) to S; the *physical-vs-MIDI meaning specifically*
of value 0 stays H** — this scan shows *how* the value is used, not
*what each specific value represents* semantically.

## 3. The surrounding branch structure — object-state dependent, not port-dependent

The 12 insns right after the `sb` usage (§3 of the scan) branch on
`[r0,#0x12]`, `[r0,#0x10]`, `[r0,#0x11]` — fields on the object
returned by the earlier `bl 0x801b460` call, not on `sb`/`r2` itself.
This confirms the port/source bit is used **once, early**, to build a
mask passed into `0x801b460`, after which the function's logic branches
on that callee's own object state, not on the raw port bit again in
this window. **S.**

## Net

`E-keys.md`'s "r2=0 physical / r2=1 MIDI" framing is **not wrong**, but
was under-describing the mechanism: it's not a simple if/else branch on
the incoming value, it's an index used to set one bit in an ownership
bitmask (`1 << sb`), consistent with and reinforcing
`lead-usb-din.md`'s independent discovery of a 128-entry per-note
ownership table on the same object family. The two threads (E/AD's key
`r2` question and R/Z/lead-usb-din's port-object investigation) are
very likely the same underlying mechanism, seen from two different
entry points.

STATUS: done
