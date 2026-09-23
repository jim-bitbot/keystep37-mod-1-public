STATUS: done
AGENT: claude
TICKET: AN
UPDATED: 2026-09-24T01:40+01:00
INPUT: firmware-re/notes/scans/AN-sync-13.txt

# AN-proposed-catalog — rows for Cursor to review

Reasoning in `model/AN-sync-13.md`. Format per `two-agent-protocol.md` §6.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (annotate `transport_cmd`, `0x08012334`) | | | 5-case TBH on `r5`, heap-lazy-init via `0x20000214`. Confirmed touching `0x20001128` — the same GPIOD-pins object `AS-sync-idr.md` traces | S |

## Explicit missing (reinforces AB)

`+0x3c` vs `0x13`: confirmed zero hits, ruling out this candidate
location for a Sync-DIP-adjacent check.

STATUS: done
