STATUS: done
AGENT: claude
TICKET: R
UPDATED: 2026-09-23T22:35+01:00
INPUT: firmware-re/notes/scans/R-usbdin.txt

# R-proposed-catalog — rows for Cursor to review

Reasoning in `model/R-usbdin.md`. Format per `two-agent-protocol.md` §6.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| `0x0801acb0` | | port_vtable_ctor (tentative) | Copies 6 words from call-site args into `0x20001d60`. Args include the `notify_013fc` sink object and 4 Thumb wrapper pointers; none touch USART1/USB literals | S |
| `0x0801b02c` | | (annotate G site 50, `0x20001e04`) | Confirmed: `*0x20001e04 = 0x20001d60`, stored by this ctor. Ties the scale-mask object (M) into the same ctor-sweep group as the port chain | S |
| `0x0801b572` | | (annotate G site 51, `0x20001eb8`) | Confirmed: `*0x20001eb8 = 0x20001e04`. Root of the 3-level chain both `play_time_step` and the key path share | S |
| `0x0801b384` | | (annotate `port_switch`) | Confirmed operating on `0x20001d60` (two indirections from the fixed root), not directly on `0x20001eb8` | S |

## Explicit missing (per ticket instruction)

Which vtable slot on `0x20001d60` is USB vs DIN — not resolved by
static search. No peripheral literal anywhere in the traced ctor chain
or `port_switch`'s callees. Recommending Unicorn emulation as the next
step, not a further static scan — stated as a real methodological
conclusion, not a placeholder.

STATUS: done
