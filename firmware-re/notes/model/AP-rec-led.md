STATUS: done
AGENT: claude
TICKET: AP
UPDATED: 2026-09-24T01:50+01:00
INPUT: firmware-re/notes/scans/AP-rec-led.txt

# AP-rec-led — fourth confirmation Rec LED isn't in the direct path; a bitmask-decode detail found

Read-only pass over `scans/AP-rec-led.txt` only.

## 1. Rec LED — reconfirms L/P/W, no new location

`led_write` (33 callers) and `led_refresh` don't appear in Rec press's
window. **S** — this is the fourth independent confirmation (L, P, W,
now AP) of the same negative. Treating this as settled, not
re-checking again without a genuinely new method.

## 2. 0x0801d76c's body — a CLZ-based bitmask-to-index decode

Walked for the first time: `clz r2,r2; lsrs r2,r2,#5` — count-leading-
zeros on a one-hot value, shifted to extract the bit position. **This
is the inverse of the `1 << sb` bitmask-building pattern `AD-key-r2.md`
found** — one function builds a one-hot mask from an index, this one
recovers the index from a one-hot mask. Then indexes a small table at
`0x0801ef50` and calls `0x0801d364`. **S** — a consistent mechanism
used in at least two places in this project now, worth recognizing as
a general idiom rather than two unrelated findings.

## 3. 0x0801d7b6's body — a slot-clear pattern

`adds r2,r0,r1; strb #0,[r2,#4]; strb #0,[r2,#0xc]; ...; strh #0,[...]`
— zeroes several fields of an indexed entry. Consistent with a
subscriber-table or event-queue "clear this slot" operation, matching
the existing `notify_013fc`/subscriber-table framing from earlier
tickets. **S** for the shape; role stays consistent with what's already
known, no correction needed.

## Net

No new Rec LED location — this question is now settled at 4-for-4
negative. The real contribution here is recognizing the CLZ/shift
bitmask idiom as a repeated pattern, tying `AD`'s and this ticket's
findings together into one mechanism rather than two separate facts.

STATUS: done
