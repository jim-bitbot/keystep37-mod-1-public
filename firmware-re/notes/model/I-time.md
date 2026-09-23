STATUS: done
AGENT: claude
TICKET: I
UPDATED: 2026-09-23T22:15+01:00 (corrected per Cursor's review — scan
was expanded after original modeling pass, not re-read until now)
INPUT: firmware-re/notes/scans/I-time.txt (current version); firmware-re/notes/model/H-shared.md

# I-time — what advances the step

Read-only pass over `scans/I-time.txt` only. Per ticket instruction:
internal-vs-MIDI clock source selection is **N**, out of scope here —
this file only answers "what advances step."

## One diagram

```
0x20002bec (tick object, ctor 0x08011d7c per G-objects.md)
         |
         v
app_main_loop (0x08015768) --r0=0x20002bec--> arp_seq_tick (0x080129cc)
                                                   |
                          reads/writes on r4 (incoming object):
                          +0x38  step position (load x4, store x1)
                          +0x10  length (load x1, compared)
                          +0x55  a signed byte (store x5, load x3)
                                 — separate from 0x200051cc's own +0x55
                                   (mode_byte_get's field); this +0x55
                                   is on the TICK object, not the shared
                                   block. Do not conflate the two.
                                   0x200051cc offsets touched in the
                                   same window: +0x49 +0x44 +0x48 +0x4f
                                   (+0x4f stored on to 0x200000c8 —
                                   transpose_ram, matches existing
                                   catalog)
```

`0x08015768` is the **only** static caller passing `0x20002bec` — this
scan doesn't re-confirm the multiplicity `C-loop.md` found (3 calls to
`arp_seq_tick` per loop pass on possibly different objects); it only
shows the one site that uses this specific tick object. **S** for this
one caller; the other two call sites' objects remain unresolved (as
`C-loop.md` already flagged).

## Step (`+0x38`)

Loaded at 4 sites (`0x08012ae4`, `0x08012b54`, `0x08012c1e`,
`0x08012d18`), stored once (`0x08012eb2`, storing `sb` — a value derived
earlier in the function, not walked further in this scan), and read as
a byte at `0x08012fc6`. **S** for existence of the read/write pattern;
the store's actual source computation is outside this scan's window.

## Length (`+0x10`) — correction: 5 sites, not 1

**Correction (Cursor's review caught this):** the scan lists **five**
`+0x10` sites — `0x08012aa2`, `0x08012b80`, `0x08012ba4`, `0x08012c34`,
`0x08012f0c` — not the one I originally reported. Only the first is
disassembled in full in this scan (`ldrb r3,[r4,#0x10]; cmp r3,r0`);
the other four are listed by address only, not dumped. **S** for
existence at all 5 sites (the scan lists them explicitly, even without
full instruction dumps); not enough shown to say what sets `r0` at the
one detailed compare, or what the other four sites do.

## `+0x55` on the tick object

Distinct from `0x200051cc`'s own `+0x55` field (`mode_byte_get`'s
target) — **this is a different object** (the tick object `r4`, not the
shared block). Stored at 5 sites, loaded at 3. One store
(`0x08012a88`) writes `r5` right next to a store of `r3` to `+0x54` —
two adjacent byte fields on the tick object, same shape as several
`0x200051cc` clusters `H-shared.md` found, but this is a **separate**
address, not another `0x200051cc` offset. **S** existence; role **H**.

## SysTick and TIM2 — confirmed not touching the tick object

Both `SysTick_Handler` (`0x08018200`) and `TIM2_IRQ` (`0x08018584`)
were searched through a window past their bodies for a pc-rel load of
`0x20002bec`; neither shows one. **This directly narrows `C-loop.md`'s
open TIM2 lead** ("candidate internal clock tick, distinct from
`arp_seq_tick`") — whatever TIM2's `0x200010de` counter and
`0x08011ee4` call do, it is **not** by touching the same tick object
`arp_seq_tick` uses. Either a separate, still-unnamed clock path, or
TIM2 feeds into the tick object indirectly through one of the two other
`arp_seq_tick` callers this scan didn't trace. **S** for the negative
result (not found in the searched windows); the "separate path" framing
is **H**.

## `timediv_skip_apply` — Time Div RAM identified, #8 compares now shown

Object `0x20001000` (ctor `0x08005aa4` per `G-objects.md`), field
`+0x6d`. This is the Time Div candidate object from ticket B, now with
a confirmed field offset. **S.**

**Correction: the scan was expanded after I first modeled it, and I
never re-read the update** (Cursor's review caught this). The current
`scans/I-time.txt` §6 shows the full body of `0x08005ab8` through
`0x08005b08`, including both `#8` compares I previously flagged as
unshown:

- `0x08005ae8  cmp r0,#8` — `r0` is the value just stored to `+0x6d`
  (the just-written new Time-Div value).
- `0x08005af0  cmp r1,#8` — `r1` is a fresh reload of `+0x6d`.

Both gate a call to `0x08011ee8` (skipped when either comparison hits
`8`) and, on the non-`8` path, a further branch builds an outbound
message via `bl 0x08006914` with `r0=0x68` (Time Div's own control ID,
matching `stock-shift-map.md` §10 exactly) after `r1+1`. **Promoting
this to S** — directly shown now, not inferred. The earlier "unverified
in this file" note is superseded by the scan update, not by new
reasoning on my part.

**Swing RAM: not found.** Searched both `arp_seq_tick`'s window
(`0x080129cc`-`0x08013040`) and `timediv_skip_apply` — no separate swing
address turned up in either. Explicit missing, per ticket instruction.

## Net for HANDOFF layer 4

Step (`+0x38`, 4 loads + 1 store) and length (`+0x10`, 5 sites) fields
exist on the tick object, confirmed by read/write sites; Time Div RAM
is the `timediv_skip_apply` object's `+0x6d`, and its `#8` sentinel
comparisons are now directly confirmed (corrected above). Swing RAM is
an explicit hole. The clock-*source*
question (internal vs MIDI, what actually calls `arp_seq_tick` on a
timer) is still open — SysTick/TIM2 are ruled out as *direct* touchers
of the tick object, which is a real (negative) result, not a dead end:
whoever does ticket N should start from `arp_seq_tick`'s other two
callers (`C-loop.md`'s open item) rather than re-searching TIM2/SysTick.

STATUS: done
