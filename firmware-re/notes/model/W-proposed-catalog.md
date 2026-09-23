STATUS: done
AGENT: claude
TICKET: W
UPDATED: 2026-09-23T22:55+01:00
INPUT: firmware-re/notes/scans/W-led-confirm.txt

# W-proposed-catalog — rows for Cursor to review

Reasoning in `model/W-led.md`. Format per `two-agent-protocol.md` §6.

## Correction row

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (correct `P-led.md`'s DMA1_CH1 framing, `0x080185e8`) | | | Was called "best LED-DMA candidate" on structural grounds. This scan traces its full tail (`0x080045b6` → `0x08004566` → `0x0800781c`) and finds neither `led_write` nor `led_refresh` anywhere in it. **Ruling out**, not just leaving open | S (negative result) |

## Confirmed negative (not a gap)

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (annotate Rec LED search, cross-ref L) | | | Confirmed absent from two independent directions: Rec press's own calls (`0x0801d7b6`/`0x0801d76c`, not `led_write`), and `led_write`'s 33 callers (zero overlap with the button-dispatch window). Settled negative | S |

STATUS: done
