STATUS: done
AGENT: claude
TICKET: X
UPDATED: 2026-09-23T23:00+01:00
INPUT: firmware-re/notes/scans/X-selectors.txt

# X-proposed-catalog — rows for Cursor to review

Reasoning in `model/X-selectors.md`. Format per `two-agent-protocol.md` §6.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (annotate unshifted index 0, `0x08017834`) | | | Multi-object notify/publish via `bl 0x08014a8e`, 5 object refs as context — same family shape as Rec/Stop/Play, not a simple toggle | S (shape), H (effect) |
| (annotate unshifted index 6, `0x08017298`) | | | On `+0x12==2`, publishes **two** codes: `7` and `5`. Code `5` is the exact code Rec press uses (F/L) — Stop shares Rec's publish code in this state | S |
| (annotate unshifted index 7, `0x0801743e`) | | | Reads `0x200051cc+0x63` (Notes, per M) then `+0x51` (also used in `arp_seq_tick`, per I) — Play's handling branches on chord/arp state | S |

## Not proposed

`param_field_dispatch`'s family selector (`0x08-0x0e` vs `0x16-0x1b`)
— re-hypothesized as panel-knob-write vs. MIDI-CC-write (both callers
sit in MIDI-message territory), but not confirmed. No row proposed for
a guess.

STATUS: done
