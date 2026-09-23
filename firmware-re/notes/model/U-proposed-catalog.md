STATUS: done
AGENT: claude
TICKET: U
UPDATED: 2026-09-23T22:45+01:00
INPUT: firmware-re/notes/scans/U-set-protocol.txt

# U-proposed-catalog — rows for Cursor to review

Reasoning in `model/U-set.md`. Format per `two-agent-protocol.md` §6.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (annotate `0x0800ef38`) | | | Not a second GET/SET TBB — a short 2-value pre-check in front of `param_field_dispatch`'s own prologue, already covered by ticket M | S |

## Explicit missing (per ticket instruction — this is the deliverable, not a gap)

**No SET entry point exists as a mirror of the GET TBB.** All 48
TBB/TBH structures in the application are now accounted for, none
unassigned. Two hypotheses for a future ticket, neither confirmed:
(1) SET uses a completely different opcode scheme, not found by this
search; (2) SET may not exist as a distinct wire path — MCC "writes"
could route through the already-mapped panel/knob write paths instead.
No row proposed for either — they are hypotheses, not findings.

STATUS: done
