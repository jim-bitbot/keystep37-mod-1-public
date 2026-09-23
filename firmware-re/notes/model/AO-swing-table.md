STATUS: done
AGENT: claude
TICKET: AO
UPDATED: 2026-09-24T01:45+01:00
INPUT: firmware-re/notes/scans/AO-swing-table.txt

# AO-swing-table — a flash-resident swing lookup table, matching the manual exactly

Read-only pass over `scans/AO-swing-table.txt` only. This is a real,
well-evidenced find on a field that's been "not found" since ticket I.

## 1. The byte run matches the documented Swing values exactly

Bytes at `0x0801ec64`: `32 34 36 39 3c 3f 43 47 4b` (9 bytes, followed
by `00 00 00`). In decimal: `50, 52, 54, 57, 60, 63, 67, 71, 75`.

**This is an exact match to `stock-shift-map.md` §1's documented Swing
values** ("Off, 52, 54, 57, 60, 63, 67, 71, 75" — 9 values, manual
§3.6.3, keys 22-30). `50` is very plausibly the internal representation
of "Off" (a floor value below any real swing amount), and the
remaining 8 bytes match the 8 real percentages **in the same order,
exactly**, byte for byte. **S** — this is a flash-resident lookup
table, and the match to independently-documented panel values is not
coincidental (9 specific values in an unusual, non-arithmetic sequence
matching exactly is not the kind of thing that happens by chance).

## 2. The reader — index range matches the panel key range too

```
0x08016f7c  sub.w r4, r1, #0x15         ; index = r1 - 0x15 (21)
0x08016f80  ldr   r3,[pc] ; 0x0801ec64
0x08016f82  ldrb  r1,[r3,r4]            ; swing_table[index]
0x08016f84  ldr   r3,[pc] ; 0x20001150
0x08016f86  ldr   r0,[r3]
0x08016f88  bl    #0x801312e            ; apply(obj, value)
```

Valid when `0x15 (21) <= r1 <= 0x1d (29)` — a **9-value range**,
matching the table's 9 entries exactly. `r1`'s ultimate source (a
control ID, a key index, something else) isn't traced in this scan —
the scan's own honest caveat: "Role of r1... not named here." **S** for
the index arithmetic and range match; **H** for what `r1` actually is.

## 3. 0x801312e — the real "swing RAM" write is one function away, not found yet

This function receives the looked-up swing **value** (not an index)
plus an object pointer from `0x20001150`. **This is very likely where
the actual swing RAM field gets written** — but `0x801312e` itself
isn't walked in this scan. **Explicit next step, not guessed here.**

## 4. +0x401 sites — confirm existing knowledge, don't touch swing

The three `+0x401` load-then-use sites shown are all inside
`seq_step_store`'s already-mapped territory (`Y-record-clear.md`) —
same conclusion as `AJ-leftovers.md`: this flash slot header field
isn't the swing value itself. **S**, no new information.

## Net for HANDOFF layer 4 — swing is now much closer to closed

Not fully closed (the actual RAM destination via `0x801312e` isn't
found yet), but this is real, verifiable progress on a field that's
been an explicit "not found" since `I-time.md`: the **source table** is
identified, verified against independently-documented panel values,
and the one remaining function to trace (`0x801312e`) is named and
isolated — a much narrower next step than "search everywhere for
swing."

STATUS: done
