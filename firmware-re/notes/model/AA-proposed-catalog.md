STATUS: done
AGENT: claude
TICKET: AA
UPDATED: 2026-09-23T23:45+01:00
INPUT: firmware-re/notes/scans/AA-swing-tempo.txt

# AA-proposed-catalog — rows for Cursor to review

Reasoning in `model/AA-swing-tempo.md`. Format per `two-agent-protocol.md` §6.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (annotate tick object `0x20002bec`, field `+0xe`) | | | `internal_tempo_period` (tentative). Clamped 3000-24000 by `0x08012048`, defaults to `0x2ee0`(12000), written to TIM2's real ARR register (`0x2c` offset, verified against STM32F1 timer map) via `0x08012084` | S |
| `0x08012048` | | tempo_clamp (tentative) | Clamps incoming value to 3000-24000 before storing as the tempo period | S |
| (annotate tick object, new pc-rel sites) | | | 4 new sites beyond `I-time.md`'s known one: `0x08015304`, `0x080154c6` (→ `0x0800fa16`, the unresolved "sibling parser"), `0x080157e6`/`0x08015802` (→ `0x08012330`, the shared busy-gate) | S |

## Explicit missing (per ticket instruction)

Swing RAM: still not found. The slot header `+0x401` field is
confirmed written by the recorder (existing rows) but shows no swing
role in this scan. The 218-hit occupancy-value search is too noisy to
propose a row from. No row proposed — genuinely absent from this
scan's reach.

STATUS: done
