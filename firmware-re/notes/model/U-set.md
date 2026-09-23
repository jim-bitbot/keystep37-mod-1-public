STATUS: done
AGENT: claude
TICKET: U
UPDATED: 2026-09-23T22:45+01:00
INPUT: firmware-re/notes/scans/U-set-protocol.txt

# U-set — SET counterpart search, honest negative result

Read-only pass over `scans/U-set-protocol.txt` only.

## 1. Exhaustive TBB/TBH inventory — 48 total, all accounted for

The scan lists every `tbb`/`tbh` in the application (48 instructions).
Cross-referencing against every closed ticket: all 48 are now
identified as belonging to an already-mapped dispatcher — the GET TBB
(K), `param_field_dispatch` (M), the three `panel_button_dispatch`
tables (F), the analog TBH (D), `seq_slot_base` (O), `seq_step_store`
(L), or `rebuild_order`/`mode_tbh` (existing catalog). **No unassigned
TBB/TBH remains that could plausibly be a second, SET-shaped dispatch
table.** **S** — this is a real, complete accounting, not a sample.

## 2. The `0x0800ee92` sibling (`0x0800ef38`) — structurally similar, not a SET path

Same shape as the GET TBB's own gate (`r2!=0` → `bx lr` at
`0x0800f044`). On `r2==0`, this one does something different: it reads
a byte, compares against `6`, and a second byte against `1` — a small
2-value special case, then falls into `param_field_dispatch`'s own
`push` (`0x0800f054`, confirmed by this scan's own prologue check, not
`0x0800ee92`'s TBB shape). **This is not a second signed-byte TBB** —
it's a short pre-check in front of `param_field_dispatch`, already
covered by ticket M. **S.**

## 3. GET's three handler bodies — no write-looking pattern beyond expected

`get_param`, `get_param_b`, and `get_param_c`'s bodies were checked for
`str`/`strb` instructions that could indicate an inline SET path rather
than a pure read. `get_param` and `get_param_b` both show a cluster of
stores (`str r3,[r5,#4]`, `str r4,[r3]`, several `strb`s) — but these
are writing into a **local reply-buffer structure** (building the GET
response message), not into the device's own settings storage. This
matches the existing catalog's protocol description (GET builds a
reply envelope) — **not new evidence of a SET path**, just confirms
GET's own reply-construction is store-heavy for an unrelated reason.
`get_param_c` has no stores at all before its first `pop`/`bx`. **S**
for what's shown; explicitly **not** claiming any of these stores is a
SET entry point.

## 4. Missing — stated as a real conclusion

**No SET entry point found in this scope.** The ticket instruction
anticipated either finding SET or explicitly failing to — this is the
latter, and it's a meaningful negative: with all 48 TBB/TBH structures
in the entire application now accounted for, and none shaped like a
second GET-style dispatcher, **SET (if it exists in this firmware at
all) is not implemented as a mirror of the GET TBB.** Candidate
directions not covered by this ticket: a SET path reached through a
completely different opcode scheme (not a signed-byte TBB at all — e.g.
per-field direct writes triggered elsewhere), or SET may genuinely not
exist in the app-mode protocol (settings changes could conceivably
route entirely through the panel/knob write paths already mapped in
D/F/M, with MCC's "write" UI actually just replaying panel-equivalent
actions rather than using a distinct wire opcode). Neither is confirmed
— both are honest hypotheses for a future ticket, not findings.

STATUS: done
