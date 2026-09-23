STATUS: done
AGENT: claude
TICKET: AK
UPDATED: 2026-09-24T01:25+01:00
INPUT: firmware-re/notes/scans/AK-emit-seq-slots.txt

# AK-proposed-catalog — rows for Cursor to review

Reasoning in `model/AK-emit-seq.md` and `R-usbdin.md`'s correction.
Format per `two-agent-protocol.md` §6.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (annotate `0x0801acb0`, correction) | | | 8-word copy (`+0`-`+0x1c`), not 6 — corrects `R-usbdin.md`. `emit_seq`'s Note-On fields are populated | S |

## Explicit missing (per ticket instruction)

What values the ctor-sweep's own stack supplies for `sp+0x24`/`sp+0x28`
at the call site — not re-derived, needs walking further back into the
sweep's argument setup.

STATUS: done
