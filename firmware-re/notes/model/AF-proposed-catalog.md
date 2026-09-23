STATUS: done
AGENT: claude
TICKET: AF
UPDATED: 2026-09-24T00:15+01:00
INPUT: firmware-re/notes/scans/AF-set-alt.txt

# AF-proposed-catalog — rows for Cursor to review

Reasoning in `model/AF-set.md`. Format per `two-agent-protocol.md` §6.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (annotate GET family stores, `get_param`/`get_param_b`/sibling `0x0800ef38`) | | | Checked: all stores write local reply/stack structures, none touch persistent state. Reinforces `U-set.md`'s negative from a second, independent angle | S (negative result) |

## Explicit missing (per ticket instruction — reinforces U, not new)

No SET write path found. Same two open hypotheses as `U-set.md`
(different opcode scheme, or no distinct SET wire path at all) — not
resolved further, not guessed here.

STATUS: done
