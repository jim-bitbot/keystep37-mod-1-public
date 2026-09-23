STATUS: done
AGENT: claude
TICKET: AE
UPDATED: 2026-09-24T00:20+01:00
INPUT: firmware-re/notes/scans/AE-tap-clear.txt

# AE-proposed-catalog — rows for Cursor to review

Reasoning in `model/AE-tap-clear.md`. Format per `two-agent-protocol.md` §6.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (annotate B sites 07/17, `0x08016982`/`0x0801a288`) | | | Cross-validated: this scan's dump matches `lead-oct-combo.md`'s independent capstone investigation exactly. Confirmed a countdown/repeat mechanism (see that file), confirmed **not** hold-length-clear | S |

## Explicit missing (per ticket instruction — a strong, multiply-confirmed negative)

Simultaneous Oct−+Oct+ check: not found by this scan, matching Y's and
`lead-oct-combo.md`'s independent negatives. Three separate passes now
agree hold-length-clear isn't in the Shift-RAM/button-dispatch
territory this project has mapped. No row proposed — recommending
`key_scan` itself (`0x0800cc48`) as the next place to look, not
guessed as a location here.

STATUS: done
