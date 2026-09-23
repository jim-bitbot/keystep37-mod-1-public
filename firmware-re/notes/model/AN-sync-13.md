STATUS: done
AGENT: claude
TICKET: AN
UPDATED: 2026-09-24T01:40+01:00
INPUT: firmware-re/notes/scans/AN-sync-13.txt

# AN-sync-13 — transport_cmd's full gate; +0x3c negative confirmed

Read-only pass over `scans/AN-sync-13.txt` only.

## 1. transport_cmd (0x08012334) — full gate mechanism now shown

Gated on `0x20000214` (the same heap-ish pointer `AC`/`test20_cc_value`
use), dispatches via a **5-case TBH** on `r5` (`cmp r5,#4; bhi
→ default`). On first use, lazily allocates a 160-byte (`0xa0`) object
via `0x801d862`/`0x8010b30` and stores it to `0x20000214`, then loops
back to actually dispatch. **S.** This object is shared with several
other functions already touched (§4's pc-rel list: `0x20001128` — the
`AS`-ticket GPIOD-pins object! — `0x20005534`/`0x200054bc` the TIM2
pair, `0x200000bc`/`0x200000c4`, `0x20001120` subscriber table). **This
directly ties `transport_cmd` into the same object family `AS-sync-idr.md`
traces** — consistent with `AS`'s own finding that `transport_cmd`
writes to the GPIOD-pins object via `0x80191ce`/`0x80191e6`.

## 2. +0x3c after cmp #0x13 — confirmed absent, reinforces AB

Zero hits for a `cmp #0x13` following a `+0x3c` load anywhere searched.
**S** — this specific field (`param_field_dispatch`'s own dispatch
index) never gets compared against `0x13`, ruling out one more
candidate location for a Sync-DIP-adjacent check.

## 3. 0x0800f32a — a dispatch case that writes its own index field

Inside `param_field_dispatch`'s own TBB (a sub-case, index computed
from `r3-0x20`), one case writes literal `0x13` **into the function's
own `+0x3c` dispatch field** (`strb r3,[r0,#0x3c]`) before branching
away. This is self-referential — a case that re-arms the dispatcher for
a different case next time, not a Sync DIP read. **S** for the shape;
unrelated to clock source.

## Net

Two things closed: `transport_cmd`'s dispatch mechanism (5-case TBH,
heap-lazy-init) is now fully shown, and it's structurally linked to
`AS-sync-idr.md`'s GPIOD-pins object family, not a coincidence — both
tickets independently converged on the same object cluster. The `+0x3c`
Sync-DIP hypothesis is now ruled out cleanly.

STATUS: done
