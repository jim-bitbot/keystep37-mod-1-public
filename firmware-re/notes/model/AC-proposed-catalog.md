STATUS: done
AGENT: claude
TICKET: AC
UPDATED: 2026-09-24T01:05+01:00 (closed per ticket AM's raw table decode)
INPUT: firmware-re/notes/scans/AC-analog-names.txt; scans/AM-kind-tbb.txt

# AC-proposed-catalog — rows for Cursor to review

Reasoning in `model/AC-analog-names.md`. Format per `two-agent-protocol.md` §6.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (annotate `knob_index_to_cc`, `0x080060a2`) | | | Confirmed single static caller (the AutoTest emit path only). Default/out-of-range case returns CC `0x66` (Rate) — kind 0 (strip) falls here | S |
| (annotate kind→CC mapping, closes an old "not re-derived" flag) | | | **Ticket AM's raw table decode confirms**: kind1→`0x62` Type, kind2→`0x63` Notes, kind3→`0x64` Vel, kind4→`0x65` Strum. Matches the old assumed order exactly — my own speculative alternative ordering (in the pre-correction version of this file) was wrong, now removed | S |

STATUS: done
