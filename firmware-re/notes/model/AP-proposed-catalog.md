STATUS: done
AGENT: claude
TICKET: AP
UPDATED: 2026-09-24T01:50+01:00
INPUT: firmware-re/notes/scans/AP-rec-led.txt

# AP-proposed-catalog — rows for Cursor to review

Reasoning in `model/AP-rec-led.md`. Format per `two-agent-protocol.md` §6.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (annotate `0x0801d76c`) | | | CLZ-based bitmask-to-index decode — the inverse of the `1 << sb` pattern `AD-key-r2.md` found. Same mechanism family | S |

## Explicit missing (settled negative, fourth confirmation)

Rec LED: not in the direct notify path, matching L/P/W. Not
re-proposing a search location without a new method.

STATUS: done
