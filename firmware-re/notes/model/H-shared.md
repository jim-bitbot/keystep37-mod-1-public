STATUS: done
AGENT: claude
TICKET: H
UPDATED: 2026-09-23T20:30+01:00
INPUT: firmware-re/notes/scans/H-shared.txt

# H-shared — field table for 0x200051cc

Read-only pass over `scans/H-shared.txt`'s index and unique-offset
summary (197 sites, ~40 unique offsets), cross-checked against fields
already named in other tickets. Per the ticket instruction: **do not
call this "the voice object."** It is a large shared state block with
callers spanning boot config, analog processing, mode/timediv logic,
panel-button dispatch, arp tick, and note/chord output.

## Field table

| Offset | Sites | Known role | Source | Tag |
|---|---|---|---|---|
| `+0x4d` | 5 | Chord ON flag | existing catalog (`voice_note_on` gate) | S |
| `+0x4e` | 5 | Velocity | existing catalog (`voice_note_on`) | S |
| `+0x4f` | 21 | Chord interval | existing catalog (`voice_interval_load`) | S |
| `+0xb9` | 20 | AutoTest flag | existing catalog + A-objects.md §4c | S |
| `+0x59` | 5 | Mode-related (B sites 03/04 gate) | B-shift-handlers.md | S existence, H exact role |
| `+0x49` | 6 | Read by shifted-panel case (B site 12; F's Shift+Rec case) | B/F | S existence, H exact role |
| `+0x5c` | 9 | Bit 0 read (B site 17, Oct-family) | B-shift-handlers.md | S existence, H exact role |
| `+0x44` | 19 | **New, most-touched offset after `+0x4f`.** Loaded repeatedly inside `arp_seq_tick`'s window (I-time.txt §3: sites `0x08012b48`,`0x08012c5a`,`0x08012d0e`,`0x08012d96`,`0x08012eca`,`0x08012fd6` all `+0x44`) | I-time cross-reference | S existence, H role |
| `+0x34` | 16 | Read at several sites incl. `0x08006a10`/`0x08006a18`/`0x08006d04`/`0x08006d0c` in pairs (r3 then r2) — a two-register read pattern repeats 3 times | this scan | S existence, H role |
| `+0x51` | 12 | Read inside `arp_seq_tick` window (I-time.txt: `0x08012d56`) alongside `+0x44`/`+0x48`/`+0x4f` | I-time cross-reference | S existence, H role |
| `+0xbc` | 10 | Always co-occurs with `+0x3f` in the two sites that show both (`0x0801557c`, `0x08015f84`) | this scan | S existence, H role |
| `+0x47` | 6 | — | this scan | S existence, H role |
| `+0x46` | 5 | Five sites clustered at `0x08019496`-`0x0801950e`, close together in flash — one function reading it 5 times | this scan | S existence, H role |
| `+0x4a` | 4 | Co-occurs with `+0x4f` at `0x0801b910`/`0x0801b91c` and `0x0801be70`/`0x0801be7c` and `0x0801c208`/`0x0801c212` — paired reads across 3 separate call sites, same two-offset shape each time | this scan | S existence, H role |
| `+0x3f` | 4 | — | this scan | S existence, H role |
| `+0x55` `+0x56` `+0x57` | 3 each | Clustered together at `0x08006988`-`0x080069ea` (repeating pattern across several sub-blocks: `+0x54`,`+0x56`,`+0x57` then `+0x56`,`+0x57`,`+0x54`,`+0x56`,`+0x5b`,`+0x57` — looks like a small state machine cycling through adjacent byte fields) | this scan | S existence, H role |
| `+0x54` | 2 | Same cluster as above | this scan | S existence, H role |
| `+0x5b` | 2 | Same cluster as above | this scan | S existence, H role |
| `+0x38` | 2 | — | this scan | S existence, H role |
| `+0x48` | 2 | Co-occurs with `+0x4f` at `0x08012bc8` (I-time.txt, `arp_seq_tick` window) and appears alone at `0x08012b6e` | I-time cross-reference | S existence, H role |
| `+0x58` `+0x60` `+0x62` | 2 each | — | this scan | S existence, H role |
| `+0x0` `+0x1` `+0x2` `+0x3` | 1-2 each | Small, likely early struct fields (vptr region or flags) | this scan | S existence, H role |
| `+0x41` `+0x42` `+0x43` `+0x45` `+0x52` `+0x53` `+0x61` `+0x63` `+0x68` `+0x69` `+0x6a` | 1-2 each | Singletons in this scan, no cross-reference elsewhere | this scan | S existence, H role |
| `+0x6a` | 2 | Read at `0x0801cbc0`, formats into a small local buffer (`sp+0xc..0xe`) with literal bytes `0x01`/`0x2e` — looks like it's building a display/label string (`0x2e` = `.`) | this scan | S existence, H (display formatting) |

25 sites report "offset not in window" — the loaded pointer is used
without a `[reg,#imm]` access inside the 12-insn capture, or the object
is passed onward (e.g. as an argument) rather than read directly at that
site. Not resolvable from this scan.

## Rename proposal

The ticket asks to propose a rename off `voice_obj` **if the scan shows
one**. It does not — nothing in this scan's 197 sites or their callers
supplies a name for the block as a whole; the callers span too many
unrelated subsystems (boot/config, analog, mode/timediv, panel buttons,
arp tick, chord/voice) for any single-subsystem name to be accurate.
**Not proposing a rename.** Recommending the catalog keep calling it by
address (`0x200051cc`) or adopt a deliberately generic label like
`shared_state_block` — a decision for whoever owns the catalog, not
asserted here as a fact this scan established.

## What this closes

- Confirms `A-objects.md` §4c and `B-shift-handlers.md`'s cross-cutting
  finding (this is one large multi-subsystem block, not "the voice
  object with extra flags") at much larger scale: 197 load sites across
  ~40 distinct offsets, not the 6 offsets those two tickets had found.
- Directly explains why `I-time.txt` and `J-voice.txt` each independently
  found more offsets (`+0x44`,`+0x48`,`+0x51` in I; `+0x4d/+0x4e/+0x4f`
  confirmed again in J) on the same address — this scan's index shows
  those exact same sites, cross-validating both narrower scans against
  this exhaustive one.

STATUS: done
