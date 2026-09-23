STATUS: done
AGENT: claude
TICKET: P
UPDATED: 2026-09-23T21:10+01:00
INPUT: firmware-re/notes/scans/P-led.txt

# P-proposed-catalog — rows for Cursor to review

Reasoning in `model/P-led.md`. Format per `two-agent-protocol.md` §6.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| `0x0800d26e` | | led_write (tentative) | General LED writer, index `r1` 0-40, 33 static callers clustered in `0x0800d2f2`-`0x0800daac`. Not split by function this ticket | S |
| `0x0800d1f8` | | led_refresh (tentative) | Dirty-check (`+0x944` vs `+0x946`) then conditional flush via `0x0800b6ec(0x200055a8)` | S |
| `0x080185e8` | | (annotate DMA1_CH1 IRQ) | Only DMA entry of the three that reads an indirect buffer pointer (`*0x200010f0`) and dispatches further — best LED-DMA candidate | S (structure), H (LED role) |
| `0x08018a40` | | (annotate DMA1_CH2 IRQ) | Confirmed **not** the key-refresh path — calls a bare `bx lr` stub, does not reach `0x0800d1f8` | S (negative result) |

## Not proposed

Key-LED vs other-LED split (no evidence in this scan). Rec LED writer
(still not found — matches ticket L independently). DMA1_CH3
(`0x080186c4`) — no buffer read shown, nothing to propose either way.

STATUS: done
