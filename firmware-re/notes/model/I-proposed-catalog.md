STATUS: done
AGENT: claude
TICKET: I
UPDATED: 2026-09-23T20:35+01:00
INPUT: firmware-re/notes/scans/I-time.txt

# I-proposed-catalog — rows for Cursor to review

Reasoning in `model/I-time.md`. Format per `two-agent-protocol.md` §6.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (annotate existing `arp_seq_tick`/`0x080129cc` row) | | | Tick object `0x20002bec` (ctor `0x08011d7c`, per `G-objects.md`): `+0x38` step position (4 loads, 1 store), `+0x10` length (**5** sites, corrected from an earlier undercount of 1), `+0x55` a separate signed byte on this object — **not** the same as `0x200051cc`'s own `+0x55`, do not conflate | S |
| `0x08018200` | | (annotate `SysTick_Handler`) | Confirmed: does not pc-rel load `0x20002bec` in the searched window. Narrows, does not resolve, the open TIM2/SysTick tick-source question from `C-loop.md` | S (negative result) |
| `0x08018584` | | (annotate `TIM2_IRQ`) | Same negative result: no pc-rel load of `0x20002bec` in the searched window | S (negative result) |
| `0x20001000` | | (annotate `timediv_skip_apply`'s object) | Field `+0x6d` confirmed as the Time Div byte this object carries. **Correction**: the `#8` compares (`0x08005ae8`, `0x08005af0`) are now directly shown in the current scan — promoting from "not shown" to S. Non-`8` path emits control ID `0x68` (Time Div, matches `stock-shift-map.md` §10) via `bl 0x08006914` | S |

## Explicit missing (per ticket instruction)

Swing RAM: not found in `arp_seq_tick`'s window or in
`timediv_skip_apply`. No row proposed — genuinely absent from this
scan, not a gap in modeling effort.

STATUS: done
