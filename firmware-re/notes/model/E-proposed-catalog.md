STATUS: done
AGENT: claude
TICKET: E
UPDATED: 2026-09-23T19:20+01:00
INPUT: firmware-re/notes/scans/E-keys.txt

# E-proposed-catalog — rows for Cursor to review

Reasoning for each row is in `model/E-keys.md`. Format per
`two-agent-protocol.md` §6. `0x0801b750` plus each of the four numbered
callers. P tag only where an immediate in the scan matches a known
control ID — none do (these are `r2` literals 0/1 selecting a code
path, not control-ID immediates), so no row is tagged P.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| `0x0801b750` | | (existing `note` entry — annotate, no new name) | Common entry. 4 static callers total, confirmed exhaustive by `bl`-to search. Incoming `r2` copied to `sb` at `0x0801b75a`; no branch on it inside the first 20 insns | S |
| `0x0800cdfa` | | key_scan call site 01 | Inside `key_scan` (`0x0800cc48`, name from ticket C, not re-derived here). `r2=0` — literal `movs r2,#0` two insns before the `bl` | S |
| `0x0800cf30` | | key_scan call site 02 | Inside `key_scan`. Same shape as site 01, `r2=0` literal | S |
| `0x0800d064` | | key_scan call site 03 | Inside `key_scan`. Same shape, `r2=0` literal | S |
| `0x08010326` | | call site 04, containing fn unnamed | Containing function starts at the push after `0x0800fa64`; that start has no catalog/`recreate.py` name — not invented here. `r2=1` — literal `movs r2,#1` two insns before the `bl` | S |

## Interpretation, not proposed as a tagged fact

The existing catalog's "r2=0 physical / r2=1 MIDI" reading is
**unchanged H** — this scan confirms the literals, not their meaning.
Not proposing a P/S upgrade for that specific claim.

## Not proposed

Naming the site-04 containing function (scan left it unnamed); anything
past `0x0801b750`'s first 20 insns (next `sb` read is at `0x0801b8b2`,
outside this scan); `noteval` (`0x0801c3ca`, explicitly not walked).

STATUS: done
