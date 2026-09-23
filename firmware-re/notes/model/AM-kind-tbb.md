STATUS: done
AGENT: claude
TICKET: AM
UPDATED: 2026-09-24T01:35+01:00
INPUT: firmware-re/notes/scans/AM-kind-tbb.txt

# AM-kind-tbb — knob_index_to_cc's table, fully decoded and arithmetic-verified

Read-only pass over `scans/AM-kind-tbb.txt` only. This is the ticket
that closed `AC-analog-names.md`'s open item — full detail already
folded into that file's correction; this is the ticket-native record.

## Table decode

Table at `0x080060ac`, 4 bytes: `0a 04 06 08`. Verified every target
by direct arithmetic (`table_base + byte*2`, `table_base = 0x080060ac`):

| Index (kind-1) | Byte | Computed target | Shown target | Match |
|---|---|---|---|---|
| 0 (kind 1) | `0x0a` | `0xac+0x14=0xc0` | `0x080060c0` | ✓ |
| 1 (kind 2) | `0x04` | `0xac+0x08=0xb4` | `0x080060b4` | ✓ |
| 2 (kind 3) | `0x06` | `0xac+0x0c=0xb8` | `0x080060b8` | ✓ |
| 3 (kind 4) | `0x08` | `0xac+0x10=0xbc` | `0x080060bc` | ✓ |

All four independently verified, not just read off the scan. **S,
fully closed** — kind1→`0x62`(Type), kind2→`0x63`(Notes),
kind3→`0x64`(Vel), kind4→`0x65`(Strum), default(kind0/≥5)→`0x66`(Rate).

## Net

Confirms the old assumed kind ordering exactly. See `AC-analog-names.md`
for the corrected write-up (my original AC pass had flagged an
alternative ordering as the leading hypothesis without the table
bytes — this ticket disproves it and closes the question).

STATUS: done
