STATUS: done
AGENT: claude
TICKET: Y
UPDATED: 2026-09-23T23:05+01:00
INPUT: firmware-re/notes/scans/Y-record-rest.txt

# Y-proposed-catalog — rows for Cursor to review

Reasoning in `model/Y-record-clear.md`. Format per `two-agent-protocol.md` §6.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (annotate `seq_step_store` case 3, `0x0801446a`) | | | The real recording write: 32-entry match loop, writes bit 7 (retention, per corrected catalog understanding) on match, clears on no-match | S |
| (annotate `seq_step_store` case 6, `0x080144c2`) | | | Writes voice-0 pitch directly. Empty-slot + past-length → `0x82`; empty-slot + within-length → `0x81`; occupied → raw pitch. Matches the existing sentinel table exactly | S |
| (correction to `Q-promote.md`'s `0x08016afc` claim) | | | `0x08016ac0` **is** a real function (confirmed by this scan); `0x08016afc` is reached both by fallthrough (Q's finding) **and** by `0x08016ac0`'s own `r1==1` branch — best described as an internal target, not an independently-callable separate function | S |
| (annotate `0x200010d0`/`0x200010d6`) | | | Two-button chord/combo detector — each triggers `0x0800c5ee` when the other byte is set. **Not** the hold-length-clear gesture (no Oct-related ID or `seq_step_store` link found) | S |

## Not proposed

Case 5's semantic role (accumulate-then-copy shape shown, meaning not
resolved). Hold-length-clear (Shift+Oct−+Oct+) — still genuinely
unmapped; this ticket narrows where it isn't, not where it is.

STATUS: done
