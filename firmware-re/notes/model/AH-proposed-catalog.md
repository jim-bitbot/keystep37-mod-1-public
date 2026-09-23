STATUS: done
AGENT: claude
TICKET: AH
UPDATED: 2026-09-23T23:50+01:00
INPUT: firmware-re/notes/scans/AH-10638.txt

# AH-proposed-catalog — rows for Cursor to review

Reasoning in `model/AH-usb-decode.md`. Format per `two-agent-protocol.md` §6.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| `0x0801509a` | | ring_consume (tentative) | Containing function of the sole `0x08010638` call site. Read-modify-clear pattern on a halfword field: calls the decoder, then zeroes the slot it read | S |
| (annotate `0x080150ae`) | | | Confirmed a separate, unrelated 1-instruction `bx lr` stub, not part of `0x0801509a` | S |

## Not proposed

Who calls `0x0801509a` — not found by static `bl` search or Thumb
pointer search (same negative-result shape as `lead-oct-combo.md`'s
`0x08016968` case). Flagging as a new open item, not a guess.

STATUS: done
