STATUS: done
AGENT: claude
TICKET: O
UPDATED: 2026-09-23T21:06+01:00
INPUT: firmware-re/notes/scans/O-persist.txt

# O-proposed-catalog — rows for Cursor to review

Reasoning in `model/O-persist.md`. Format per `two-agent-protocol.md`
§6.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| `0x20001170` | | (annotate existing RAM row) | **Close the gap**: the one store to this pointer writes `0x200004f4` — `mode_skip_apply`'s own object. "Settings object" = the Mode object, not a separate block | S |
| `0x080186d4` | | (annotate FLASH IRQ4 entry) | Calls `0x08008140` (ST HAL, not walked) then `0x0800dd8c(*0x20001154)`, whose field shape (`+0x800/+0x802/+0x804`) matches `G-objects.md` site-46's object layout | S (entry+shape), H (object identity) |

## Explicit missing (per ticket instruction)

No load/store of flash-slot offset `+0x400` found in
`0x0800dd30`-`0x0800e400`. The RAM→flash commit path for sequence data
is unconfirmed by any ticket to date — not proposing a row, flagging it
plainly as the real open item for persistence.

STATUS: done
