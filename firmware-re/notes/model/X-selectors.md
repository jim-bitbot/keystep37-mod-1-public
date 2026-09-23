STATUS: done
AGENT: claude
TICKET: X
UPDATED: 2026-09-23T23:00+01:00
INPUT: firmware-re/notes/scans/X-selectors.txt

# X-selectors — param_field_dispatch family selector; F's unshifted 0/6/7

Read-only pass over `scans/X-selectors.txt` only.

## 1. Family selector — not found, but the search was real

`param_field_dispatch` has exactly **2** static callers
(`0x0800fd4e`, `0x0800ffda`), both inside functions that also
immediately precede — and share a stack frame shape with —
`0x0800fd5c` (the DIN ISR target) and `0x0800ffe0`
(`midi_realtime_dispatch`, from N/T). Both callers pass `r0=r5+0x28` /
`r0=r4+0x28` — a fixed offset into whatever object each caller holds,
**not a literal distinguishing which byte-value family (`0x08-0x0e` vs
`0x16-0x1b`) gets used.** The `+0x3c` search (12 sampled `str #0x3c`
sites across the image) found no site that looks like the actual
dispatch-byte write feeding `param_field_dispatch`'s own index read —
those 12 are unrelated `+0x3c` fields on other objects. **S** for the
negative result on both fronts; the family selector stays **H, unresolved**.

**New structural fact, not previously known**: both callers of
`param_field_dispatch` are reached from **MIDI-message-handling
territory** (right next to the DIN ISR target and the realtime
dispatcher), not from the panel/knob path directly. This suggests
`param_field_dispatch`'s two families might correspond to **panel-knob
writes vs. incoming-MIDI-CC writes to the same fields**, not a
"bank" selector as `M-chord.md` originally guessed. **H**, but a
different, better-evidenced hypothesis than the one this ticket set out
to test.

## 2. Unshifted index 0 (Hold) — resolved

Full body now shown: loads five objects (`0x20001094` arp-engine ptr,
`0x2000111c`, `0x20001120` subscriber table, `0x2000115c`, `0x20001160`
— the last two new addresses), stacks two of them, then
`bl 0x08014a8e`. This is a **multi-object notify/publish call**, same
family shape as the Rec/Stop/Play cases (F) — Hold's press publishes an
event through `0x08014a8e` with 5 object references as context, rather
than a simple flag toggle. **S** for the shape; `0x08014a8e`'s own body
isn't walked, so the specific effect stays **H**.

## 3. Unshifted index 6 (Stop) — resolved: double-notify, two different codes

Full body: reads `+0x12`, branches on `1`/`2`, and **on the `2` path,
publishes twice** — once with code `7` (`bl 0x0801d7b6`/`0x0801d76c`,
`r1=7`) and once with code `5` (`r1=5`, same two functions). Code `5`
is the **exact same code Rec press uses** (`F-buttons.md`,
`L-record.md`). **This is a real, concrete finding**: Stop (in its `+0x12==2`
state) publishes the same "code 5" event Rec press does — plausibly
"Stop after Rec" triggers Rec-adjacent bookkeeping (matches
`stock-shift-map.md`'s "Stop ×3 = All Notes Off" or a Rec-session-end
signal). **S** for the shared code; **H** for the semantic link.

## 4. Unshifted index 7 (Play) — resolved: scale-mask read confirmed

Full body: reads `+0x12` and `+0x10` fields in a 3-way branch
(`beq.w 0x8017584`, `beq.w 0x80176c4`, else falls to a `0x200051cc`
region), and on that fall-through path **reads `0x200051cc+0x63`
(Notes field, per M's `param_field_dispatch` table) then `+0x51`**
(the same offset `H-shared.md` flagged with 12 sites and `I-time.md`
uses inside `arp_seq_tick`). **This directly ties Play's press
handling to the shared block's Notes field and the `+0x51` field
`arp_seq_tick` also reads** — Play's behavior branches on current
chord/arp state, not just a flat play/pause toggle. **S** for the
reads; **H** for the full branch semantics (not all targets walked).

## Net

Family selector for M's chord/knob duplication: still open, but
re-hypothesized (panel vs. MIDI-CC write, not bank select) on stronger
grounds than before. All three of F's previously-unresolved unshifted
cases (0/6/7) now have full bodies and at least one concrete,
citable fact each — none are blank anymore.

STATUS: done
