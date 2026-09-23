STATUS: done
AGENT: claude
TICKET: AQ
UPDATED: 2026-09-24T01:55+01:00
INPUT: firmware-re/notes/scans/AQ-sites-08-11.txt

# AQ-proposed-catalog — rows for Cursor to review

Reasoning in `model/AQ-sites-08-11.md`. Format per `two-agent-protocol.md` §6.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (annotate G sites 08/09/10/11) | | | Each published to a dedicated global slot (`0x200010ec`/`0x2000111c`/`0x200010f8`/`0x2000107c`) via a per-object accessor, once per boot. Real pattern, role still H | S (pattern), H (role) |

## Not proposed

The four accessor functions and what the objects represent — not
walked, existence-only per this ticket's scope.

STATUS: done
