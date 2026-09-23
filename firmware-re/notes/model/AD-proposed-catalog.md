STATUS: done
AGENT: claude
TICKET: AD
UPDATED: 2026-09-24T00:05+01:00
INPUT: firmware-re/notes/scans/AD-key-r2.txt

# AD-proposed-catalog — rows for Cursor to review

Reasoning in `model/AD-key-r2.md`. Format per `two-agent-protocol.md` §6.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (annotate `0x0801b750`'s `sb`/incoming `r2`) | | | **Correction/reframe**: used as a shift amount (`1 << sb`) building a one-hot bitmask before `bl 0x801b460`, not tested as a boolean. Mechanism is S; the specific "0=physical, 1=MIDI" meaning of the value stays H, now understood as feeding the same ownership-bitmask mechanism `lead-usb-din.md` found independently | S (mechanism), H (semantic value) |

## Not proposed

No row for "physical vs MIDI" itself — still an external, unverified
claim about what value 0 vs 1 *means*, just now with the *mechanism*
that consumes it confirmed.

STATUS: done
