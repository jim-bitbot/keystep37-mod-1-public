STATUS: done
AGENT: claude
TICKET: D
UPDATED: 2026-09-23T19:20+01:00
INPUT: firmware-re/notes/scans/D-analog.txt

# D-analog — analog_knob_process kinds 0-4, strip_process_b Shift skip

Read-only pass over `scans/D-analog.txt` only. Tags: **S** = shown directly
in this scan, **H** = plausible, not shown, **unknown** = no evidence
either way in this scan.

## 1. Kind targets — no CC immediate found, so no panel names assigned

`analog_knob_process` (`0x08004918`) has one AutoTest/Test-20 emit path
(`0x08004974`-`0x08004982`), which calls `knob_index_to_cc`
(`0x080060a2`) then `test20_cc_value` (`0x080068c8`). That is the **only**
place in this scan's window (`0x08004918`-`0x08005a1f`, plus
`0x08004388`-`0x08004645` for the strip) that touches CC assignment at
all, and it passes the kind byte (`+0x58`) itself into `knob_index_to_cc`
as a runtime value — there is no literal `0x62`-`0x66` anywhere in either
disassembled window. `knob_index_to_cc`'s own body (which maps kind to a
specific CC) is not part of this scan.

Per the ticket instruction: a kind gets a panel name (Type/Notes/Vel/
Strum/Rate) only if this scan shows that CC immediate on that kind's
path. None do. **All five kind targets stay `unknown` in this file** —
this is not a rejection of the existing catalog's Type/Notes/Vel/Strum/
Rate naming (that naming is already **P**, live-verified via occupancy,
per `address-catalog.md`'s `knob_index_to_cc` row), it is a statement
that *this specific scan* supplies no independent confirmation of which
kind is which panel control.

| Kind | RAM (from A-boot, not re-derived here) | TBH slot | Entry VA | Panel name (this scan) |
|---|---|---|---|---|
| 0 | `0x20000468` | not a TBH case — `cbz r5,#0x0800498c` at `0x08004940` | `0x0800498c` | unknown |
| 1 | `0x2000121c` | TBH `r3=0` | `0x0800527c` | unknown |
| 2 | `0x20001294` | TBH `r3=1` | `0x080054c6` | unknown |
| 3 | `0x2000130c` | TBH `r3=2` | `0x080056cc` | unknown |
| 4 | `0x20001384` | TBH `r3=3` | `0x080058cc` | unknown |

Structural note, not a naming claim: kinds 1-3 (`0x0800527c`,
`0x080054c6`, `0x080056cc`) share one shape in the 20 disassembled insns
each — `bl` to a per-kind helper (`0x0801b246`/`0x0801b250`/`0x0801b278`),
`bl 0x080048f8` with a different immediate `r1` per kind (`0xd`, `0xf`,
`0x80`), then a signed 16-bit store to `obj+0x68` and a read/modify/write
of a flag word at `obj+0x68+8` (bit 0 set unconditionally). Kind 4's 20
insns are a different shape entirely (sign/threshold arithmetic on the
raw `+0x59` byte against constants `0x77`/`0x88`, a `smull`-based scale,
no call to any of the three per-kind helpers above). Kind 0's target is
different again (no TBH — reached only when `+0x58==0` via the `cbz`,
Shift-RAM-gated pickup math, no CC/panel call in the shown window).
**S** for all shapes shown; **unknown** for which panel control any of
them is.

## 2. Store of raw at `+0x5a`

Confirmed: exactly one store site in the whole scanned window
(`0x08004918`-`0x08005a1f`), at `0x08004930`
(`strb.w r3,[r4,#0x5a]`), storing the current `+0x59` value into `+0x5a`,
gated on `+0x5a != +0x59` (the `cmp`/`beq` at `0x0800492c`/`0x0800492e`).
This runs before the kind dispatch and before the AutoTest check — it
updates the "last raw value" byte regardless of which kind the object is
or whether AutoTest is on. **S.**

## 3. Shift+Mod — not shown in this scan

Ticket instruction: confirm or reject the Shift+Mod skip from the
`strip_process_b` `bne 0x08004428` at `0x200010d2` only, one sentence.

The scan's §4 shows the check clearly: `0x080043be` loads `0x200010d2`
(Shift-held byte), `0x080043c0` reads it, `0x080043c4`
(`bne.w #0x08004428`) branches away when it is nonzero (Shift held), and
`0x08004428` is inside the same function (`strip_process_b`,
`0x08004388`) — **the skip target is not a MIDI-emit call site in this
scan's disassembled window**, it is a small tail block that stores `4`
into `0x200010dc` (`0x0800442c`) and falls into a second flag check and
an early `pop`, so this scan shows Shift held causing `strip_process_b`
to take an early, different exit path through its own tail rather than
its normal fall-through, but it does **not** show that tail block
skipping a MIDI-emit call (no such call is visible in §4b at all) — so
this scan alone shows a *branch redirect on Shift-held*, tag **S**, but
does **not** by itself show that redirect is specifically a "skip the
MIDI emit" behavior; that stronger claim is **not shown** in this scan
and is not confirmed here.

## 4. Objects — five analog + one strip, confirmed distinct

`bl`-to search in §5: `analog_knob_process` (`0x08004918`) has exactly
five static callers, all inside `app_main_loop`, over the five kind
objects (`0x20000468`/`0x2000121c`/`0x20001294`/`0x2000130c`/
`0x20001384`); `strip_process_b` (`0x08004388`) has exactly one static
caller, over a distinct object (`0x2000039c`). Matches the existing
catalog's ctor-site RAM addresses (cited in the scan as "from
scans/A-boot.txt, not re-derived here" — not independently re-confirmed
by this scan, just consistent with it). **S** for the caller counts and
objects being distinct; the RAM-to-kind mapping itself is carried over
from A, not re-derived.

STATUS: done
