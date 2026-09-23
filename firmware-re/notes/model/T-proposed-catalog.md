STATUS: done
AGENT: claude
TICKET: T
UPDATED: 2026-09-23T22:40+01:00
INPUT: firmware-re/notes/scans/T-clock-source.txt; firmware-re/notes/scans/N-05534.txt

# T-proposed-catalog — rows for Cursor to review

Reasoning in `model/T-clock.md`. Format per `two-agent-protocol.md` §6.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| `0x20005534` | | tim2_wrapper (tentative) | `+0`=TIM2 base, `+4/+8/+0xc/+0x10` config. Touched by 5 confirmed sources: `midi_realtime_dispatch`'s `0xF8` case, an unnamed 3-site function, `transport_cmd`, EXTI0, `TIM2_IRQ` itself | S |
| `0x200054bc` | | (sibling, tentative) | Same shape, used exclusively by `TIM4_IRQ`. Never touched by any `0x20005534` caller | S |
| `0x08012334` | | (annotate `transport_cmd`) | Also resets TIM2's CNT register directly (`0x08012388`), not just a downstream dispatcher | S |

## Explicit missing / negative result (per ticket instruction)

No software source-arbitration flag found gating `0x20005534` access
between TIM2-IRQ-driven and MIDI-Clock-byte-driven writes — every
source pokes the same registers unconditionally. Control ID `0x13`
(Sync DIP) not confirmed to touch this object. Stated as a real
finding, not a gap.

STATUS: done
