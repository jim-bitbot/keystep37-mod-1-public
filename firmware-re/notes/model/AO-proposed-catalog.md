STATUS: done
AGENT: claude
TICKET: AO
UPDATED: 2026-09-24T01:45+01:00
INPUT: firmware-re/notes/scans/AO-swing-table.txt

# AO-proposed-catalog — rows for Cursor to review

Reasoning in `model/AO-swing-table.md`. Format per `two-agent-protocol.md` §6.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| `0x0801ec64` | | swing_value_table (tentative) | 9-byte flash table, `50/52/54/57/60/63/67/71/75` — exact match to `stock-shift-map.md`'s documented Swing panel values | P (matches live-verified panel documentation) |
| (annotate reader, `0x08016f7c`) | | | Index = `r1-0x15`, valid range `0x15-0x1d` (9 values), reads the table, calls `0x801312e(obj=*0x20001150, value)` | S |

## Explicit missing (per ticket instruction)

`0x801312e` — the function that likely writes the actual swing RAM
field — not walked in this scan. Named and isolated as the concrete
next step, not guessed at.

STATUS: done
