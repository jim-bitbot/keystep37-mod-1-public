STATUS: done
AGENT: claude
TICKET: AJ
UPDATED: 2026-09-24T00:30+01:00
INPUT: firmware-re/notes/scans/AJ-leftovers.txt

# AJ-leftovers — +0x50 confirmed not on 0x200051cc; case 5 and Time Div #8 reconfirm existing work

Read-only pass over `scans/AJ-leftovers.txt` only.

## 1. 0x200051cc+0x50 — a proper tracked-register search, real negative

Unlike `M-chord.md`'s informal note ("param_field_dispatch r0 writes
`+0x50` next to Type/Notes/Vel"), this scan did the rigorous version:
tracked the destination register of **every** `0x200051cc` pc-rel load,
then searched the following 20 instructions for `[that-reg,#0x50]`.
**Zero hits.** The `+0x50` writes that do exist (`param_field_dispatch`'s
own `r0`, confirmed again here at `0x0800f2f0`/`0x0800f30e`/`0x0800f55a`)
are **not shown to be on `0x200051cc` at all** — this scan's dedicated
search found no path from a `0x200051cc` load to that field. **This
sharpens `M-chord.md`'s own caveat** ("the two objects are not shown to
be the same") into a real negative for this specific field: **S** —
`+0x50` is confirmed **not** reachable from `0x200051cc` by this
method, strengthening the case that `param_field_dispatch`'s object and
`0x200051cc` may be different objects, at least for this field.

## 2. Case 5 (0x08014494) — identical bytes to Y, no new content

This scan's dump matches `Y-record-clear.md`'s case-5 analysis exactly,
byte for byte. **S** — independent re-confirmation, not new information.
Semantic role stays open, same as Y left it.

## 3. Time Div #8 compares — identical to my own corrected I-time.md

This scan's `0x08005ab8`-`0x08005afe` dump is **identical** to the
current (corrected) version of `I-time.md`'s §6 — the same `#8`
compares at `0x08005ae8`/`0x08005af0` I already promoted to S after
Cursor's review caught the earlier stale-scan gap. **S** — this is
useful independent confirmation that the correction I made was
accurate, not new information.

## Net

One genuine tightening (the `+0x50` field's object identity is now more
firmly in question, not just caveated), two clean reconfirmations of
already-closed work. No corrections needed to existing model files from
this ticket.

STATUS: done
