STATUS: done
AGENT: claude
TICKET: M
UPDATED: 2026-09-23T20:58+01:00
INPUT: firmware-re/notes/scans/M-chord.txt

# M-proposed-catalog — rows for Cursor to review

Reasoning in `model/M-chord.md`. Format per `two-agent-protocol.md` §6.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| `0x0800f054` | | (annotate `param_field_dispatch`) | Two parallel byte-value families (`0x08-0x0e`, `0x16-0x1b`) write the same three fields `+0x4d/+0x4e/+0x4f`. New field `+0x50` zeroed alongside them on disable | S |
| (new field row) | | `0x200051cc+0x50` | Zeroed alongside `+0x4d/+0x4e/+0x4f` on the chord-disable path | S existence, H role |
| `0x20001e04` | | (annotate scale-mask object base) | **Promote from H to S.** Scale mask `0x20001e3a` reached as `base+0x30` then `+6` via two helper calls (`0x0801b37a`→`0x0801c670`) — `0x30+6=0x36`, confirming `A-objects.md`'s original offset guess | S |
| `0x0800d26e` | | (annotate LED writer, cross-ref) | Called from the scale-bit test loop on a set pitch-class bit — ties Scale mode to per-key LED display | S |

## Not proposed

Which of the two byte-value families is base-knobs vs. Chord-bank
knobs — H, not resolved by this scan. Object identity between
`param_field_dispatch`'s write target and `voice_note_on`'s read
target (`0x200051cc`) — not independently re-proven here, existing
catalog identity left as-is.

STATUS: done
