STATUS: done
AGENT: claude
TICKET: K
UPDATED: 2026-09-23T20:45+01:00
INPUT: firmware-re/notes/scans/K-protocol.txt

# K-protocol — GET/SET table on top of D-J

Read-only pass over `scans/K-protocol.txt` only. Per ticket instruction:
occupancy CCs are firmware control IDs, not a MIDI map; **P** only where
an immediate in this scan matches a known ID.

## GET dispatcher structure

`0x0800ee92` is a **TBB** (not the §10 control-ID scheme) indexed on
`([r1] as signed) − 1`, gated on `r2==0`. Three real targets across a
127-byte table, all the rest fall to `pop` (no-op):

| Byte at `[r1]` | Target | Callee |
|---|---|---|
| `0x2,0xc,0x21,0x23,0x25,0x26` | `0x0800ef16` | `bl 0x0800614c` (`r0+=0x28`) |
| `0x1,0x9,0xb,0x20,0x22,0x24,0x7f` | `0x0800ef1e` | `bl get_param` (`0x08005e84`, `r0+=0x38`) |
| `0x5,0x6,0x7,0x8,0xa,0xf` | `0x0800ef26` | `bl 0x080060c4` (`r0+=0x48`) |

**S** — every byte value and target is a literal in the scan. This is a
three-way sub-dispatch on top of `get_param`'s own `deviceGlobalParamId`
GET, not a second protocol layer — `0x0800614c` and `0x080060c4` share
`get_param`'s exact prologue shape (`r5=r0`, `r6=r1`, load
`*0x20000214` into `[r5,#4]`), so this is one family of three sibling
GET-style handlers, likely selected by a leading opcode byte this scan
doesn't name. **H** for what distinguishes the three families
semantically.

## Mode/Time Div/Type/Notes are NOT in this table

Per ticket instruction and the scan's own §6: none of the §10 control
IDs (Mode `0x15`, Time Div `0x68`, Type `0x62`, Notes `0x63`, Vel
`0x64`, Strum `0x65`, Rate `0x66`, Chord `0x69`, Seq/Arp `0x12`, the
eight button IDs) appear as a special-cased index in this TBB — they
all fall through to the default `pop`. **This confirms they are handled
by a different mechanism entirely** (the compact-index/button-dispatch
machinery from tickets D/F, and `param_field_dispatch`/`0x0800f054`
from the existing catalog for Type/Notes), not by this GET table. **S**
— direct negative result, not inferred.

Two of §10's control IDs *do* appear in this scan, but each as an
unrelated second-byte compare inside a **different** function, not as
this TBB's index:

- `0x40` — compared inside `0x080060c4` (`0x080060d0`, against
  `[r1,#2]`, the *third* byte of the message, not the TBB-indexing
  byte).
- `0x41` — compared inside `get_param` itself (`0x08005fbe`, against
  `[r6,#1]`, the *second* byte).

Neither is the TBB index (`[r1]`, byte 0). **S** for location; not
proposing these as GET/SET opcode rows since their role (sub-selector
within an already-dispatched handler) isn't resolved.

## `chord_test_dispatch` — confirmed unreachable statically, again

`0x08005df8`'s `0x69` compare (Chord control ID) is confirmed exactly
as the existing catalog already had it. This scan adds: **no static
`bl` anywhere in the image calls this function, and no Thumb pointer to
it exists either** — same "orphaned, must be reached indirectly"
situation the existing catalog already flags for several dispatch
functions (e.g. `chord_test_dispatch`'s own catalog row already says
"Control 0x69... ON/OFF" with no caller cited). **S** — re-confirms,
doesn't newly discover.

## GET/SET table (what this ticket can actually fill)

| Param area | ID/immediate | Mechanism | Tag |
|---|---|---|---|
| Global params (generic) | `0x1,0x9,0xb,0x20,0x22,0x24,0x7f` at `[r1]` | GET TBB → `get_param` family | S |
| Global params, second family | `0x2,0xc,0x21,0x23,0x25,0x26` at `[r1]` | GET TBB → `0x0800614c` | S |
| Global params, third family | `0x5,0x6,0x7,0x8,0xa,0xf` at `[r1]` | GET TBB → `0x080060c4` | S |
| Mode | `0x15` | NOT this TBB — `mode_knob_apply`/`mode_byte_get` (existing catalog) | S (negative) |
| Time Div | `0x68` | NOT this TBB — `timediv_skip_apply` (ticket B/I) | S (negative) |
| Type/Notes | `0x62`/`0x63` | NOT this TBB — `param_field_dispatch` (existing catalog) | S (negative) |
| Chord | `0x69` | `chord_test_dispatch`, still no static caller found | S (unreachable statically) |
| Vel/Strum/Rate | `0x64`/`0x65`/`0x66` | NOT this TBB — not otherwise traced this ticket | H |
| 8 button IDs | `0x55/0x56/0x10/0x11/0x67/0x57/0x59/0x5a` | NOT this TBB — `id_to_index`/`panel_button_dispatch` (ticket F) | S (negative) |
| Seq/Arp switch | `0x12` | NOT this TBB — not otherwise traced this ticket | H |

**No SET counterpart found** — `0x0800ee92`'s `r2!=0` branch is a bare
`bx lr`, "no SET body on that branch" per the scan. If a SET path
exists, it is not this function. Explicit missing.

## Net for HANDOFF layer 6

The ticket's own goal ("param IDs used by Mode/Time Div/Type/Notes/keys
have rows") is met, but the honest answer for all of them is **negative
evidence**: none of those five families are inside this GET TBB — each
is handled by its own already-mapped mechanism from D-J. What this
scan actually maps is a *different*, previously-uncharted three-family
GET dispatcher for the remaining global parameters, whose specific
semantic meaning (which parameter each byte value corresponds to) isn't
resolved — that would need the `KeyStep37.json` `globalParamId` table
cross-referenced against these byte values, which this ticket doesn't
do.

STATUS: done
