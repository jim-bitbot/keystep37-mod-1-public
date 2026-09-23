STATUS: done
AGENT: claude
TICKET: M
UPDATED: 2026-09-23T20:58+01:00
INPUT: firmware-re/notes/scans/M-chord.txt

# M-chord — field stores and the scale halfword

Read-only pass over `scans/M-chord.txt` only. Per ticket instruction:
stock chord/scale only, no patch notes.

## 1. param_field_dispatch — two parallel families writing +0x4d/+0x4e/+0x4f

TBH on `[r0,#0x3c]-1`. The byte-value-to-field map:

| Byte | Field written | Family |
|---|---|---|
| `0x08` | zero `+0x4d/+0x4e/+0x4f` **and `+0x50`** (new field, not previously catalogued) | zero/disable |
| `0x09`, `0x22` | `+0x4d = r1`, zero `+0x4e/+0x4f/+0x50` | enable (family A) |
| `0x0a` | `+0x4e` | family A |
| `0x0c` | `+0x4f` | family A |
| `0x16`, `0x19` | `+0x4d` | family B |
| `0x18`, `0x1a` | `+0x4e` | family B |
| `0x1b` | `+0x4f` | family B |
| `0x0b`, `0x0d`, `0x0e` | `+0x4e`/`+0x4e`/`+0x4f` | mixed, same fields |

**S** — every byte and target offset is a literal `strb.w` in the scan.
Two distinct byte-value clusters (`0x08-0x0e` and `0x16-0x1b`) write the
exact same three fields — a real structural duplication. **H** for why:
plausibly base Type/Notes/Vel knobs vs. a second knob bank (Chord
button's own "repeat = banks 1-4," `stock-shift-map.md` §2), not
confirmed by this scan.

**New field found**: `+0x50` is zeroed alongside `+0x4d/+0x4e/+0x4f` on
the disable path — a fourth chord-related field not in any prior
ticket's table. **S** existence, **H** role.

The enable write (`0x09`/`0x22`) always resets `+0x4e`/`+0x4f`/`+0x50`
to zero when setting `+0x4d` — turning Chord on re-zeroes
velocity/interval/the new field rather than preserving them. **S.**

## 2. Reader of +0x4d — same field, object identity not re-proven

`voice_note_on` (`0x0801bab8`) reads `+0x4d` on `fp`, which `J-voice.md`
established is `0x200051cc`. This scan's own text is explicit: **"the
two objects are not shown to be the same"** — `param_field_dispatch`'s
`r0` (what it writes) is not independently proven, in this scan, to be
the same address as what `voice_note_on` reads. Existing catalog rows
already treat `0x200051cc+0x4d/+0x4e/+0x4f` as one thing; this scan
doesn't contradict that, it just doesn't itself re-derive the identity.
**S** for both halves individually; **not re-tagging** the existing
identity claim based on this scan alone.

## 3. Scale mask — the G-ticket lead resolved cleanly

`0x20001e3a` is reached as `0x20001e04 + 0x30` (via `0x0801b37a`) then
`+6` (via `0x0801c670`'s `ldrh r0,[r0,#6]`) — **`0x30 + 6 = 0x36`
exactly**, confirming `A-objects.md` §5's original H guess ("scale mask
`0x36` bytes past `0x20001e04`") was right, just reached through two
helper calls rather than a raw offset. **Promoting `0x20001e04` as the
scale-mask object's base to S** (the addressing path is now directly
shown); the object's other fields stay unnamed.

The caller (`0x0800d950` region) tests bits 0-11 of the mask
(`asr.w r3,r6,r4` / `tst.w r3,#1`, looped `r4` 0-11 — one bit per pitch
class) and calls the LED writer `0x0800d26e` on a set bit. **This
directly ties Scale mode to per-pitch-class LED lighting** — confirms
the manual's "scale display" behavior at the code level. **S.**

## Net

Chord enable/interval/velocity fields extended by one (`+0x50`, new),
and shown to be written by two parallel byte-value families (not one) —
worth a dedicated look later at what selects between them. Scale-mask
object base is now S, not H. No interval table found in this scan (not
present in the disassembled window) — explicit missing, matching the
ticket's "if present" phrasing.

STATUS: done
