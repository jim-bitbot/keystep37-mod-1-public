STATUS: done
AGENT: claude
TICKET: AJ
UPDATED: 2026-09-24T00:30+01:00
INPUT: firmware-re/notes/scans/AJ-leftovers.txt

# AJ-proposed-catalog — rows for Cursor to review

Reasoning in `model/AJ-leftovers.md`. Format per `two-agent-protocol.md` §6.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (annotate `+0x50` field, M's chord/scale section) | | | Rigorous tracked-register search found **zero** paths from any `0x200051cc` load to `+0x50`. Sharpens M's existing caveat into a real negative — object identity between `param_field_dispatch`'s target and `0x200051cc` stays unconfirmed for this field specifically | S (negative result) |

## Not proposed

Case 5's semantic role and Time Div's `#8` compares — both already
covered (Y and the corrected `I-time.md` respectively), this scan just
independently reconfirms both with identical bytes.

STATUS: done
