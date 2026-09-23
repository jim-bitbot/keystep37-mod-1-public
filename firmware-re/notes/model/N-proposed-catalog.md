STATUS: done
AGENT: claude
TICKET: N
UPDATED: 2026-09-23T21:02+01:00
INPUT: firmware-re/notes/scans/N-sync.txt

# N-proposed-catalog — rows for Cursor to review

Reasoning in `model/N-sync.md`. Format per `two-agent-protocol.md` §6.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| `0x0800ffe0` | | midi_realtime_dispatch (tentative) | Dispatches `0xFA`/`0xF8`/`0xFC`/`0xFB` (Start/Clock/Stop/Continue) on the incoming byte at `[r4]` | S |
| `0x20005534` | | (annotate, cross-ref to I-time) | Loaded by both the `0xF8` MIDI-Clock case here and `TIM2_IRQ` (`I-time.md`) — same object, two different clock sources. Candidate clock-convergence point | S (shared address), H (role) |
| `0x08012334` | | transport_cmd (tentative) | Takes a numeric command in `r1`: `1` from MIDI Start (this scan), `4` from Shift+Play (`J-voice.md`). Shared sink for two unrelated triggers | S |
| (annotate all three `panel_button_dispatch` tables, index 4) | | | Confirmed: Tap (compact index 4) is a no-op in every table. Tap tempo logic lives elsewhere, not in this dispatcher | S (negative result) |

## Explicit missing (per ticket instruction)

Internal tempo RAM: not found. Clock source selection (internal vs
MIDI, Sync DIP): not resolved by this scan — no row proposed, flagged
as the real next step for whoever continues clock work.

STATUS: done
