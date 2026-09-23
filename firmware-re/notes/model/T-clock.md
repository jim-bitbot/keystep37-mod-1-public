STATUS: done
AGENT: claude
TICKET: T
UPDATED: 2026-09-23T22:40+01:00
INPUT: firmware-re/notes/scans/T-clock-source.txt; firmware-re/notes/scans/N-05534.txt

# T-clock — arbitration on the TIM2 wrapper object

Read-only pass over `scans/T-clock-source.txt` (plus `N-05534.txt`,
already modeled into `synthesis.md`'s addendum). This extends I/N: does
the clock diagram get a real source-select node?

## 1. Object fields, now fully mapped

Init (`0x080186e8`): `+0`=TIM2 peripheral base (`0x40000000`), `+4=0xb`,
`+8=0`, `+0xc=0x15b2`, `+0x10=0`. One later overwrite:
`0x08012086 str r3,[r2,#0xc]` replaces the init value on the ARR
(auto-reload) path. **No other direct store to the object itself found
besides these two** — everything else touches TIM2's own hardware
registers through `[obj+0]`, not the object's own fields. **S.**

## 2. Arbitration — the honest answer is "none found"

Per the ticket's own stated goal: is there a source-select flag gating
TIM2 vs MIDI-clock-byte writes to this object? **Searched explicitly for
control ID `0x13` (Sync DIP, per `stock-shift-map.md`'s unshifted-panel
table) inside all five call-site windows (`0x0800b0ae`, `0x0800b0c6`,
`0x0800b2ae`, the init, `TIM2_IRQ`) — found in none of them.** The one
`0x13` hit in this scan (`0x080100de`, inside the `0xF8` MIDI-Clock
path) is a different immediate context, not confirmed as the Sync DIP
read. **The two leaf functions that both TIM2 and MIDI-Clock-byte
handling call (`0x0800b0c6`/`0x0800b0ae`) test only TIM2's own SR/DIER
hardware bits — not a software source-select flag.** **S** for the
negative result: there is no software arbitration gate in the traced
functions. Either both sources are allowed to drive the same timer
unconditionally (plausible — a MIDI Clock byte arriving while running
on internal sync would just re-trigger/resync TIM2, a common hardware
timer pattern), or arbitration happens upstream of every call site this
ticket searched (not found).

## 2a. Five real call sites, confirmed, not just claimed

`midi_realtime_dispatch` (`0x0800ffe0`'s `0xF8` case), an unnamed
function at `0x08011f60`/`0x08011f9c`/`0x08012048` (three related
sites), `transport_cmd` (`0x08012334`, from N — **also** touches the
CNT register directly at `0x08012388`, resetting the counter on
whatever transport command triggered it), EXTI0 (`0x0801831c`), and
`TIM2_IRQ` itself. **All confirmed by direct disassembly**, matching
`N-05534.txt` exactly. **S.**

## 3. The sibling, confirmed distinct

`0x200054bc` is a separate object, same shape, used by `TIM4_IRQ`
(`0x080185cc`) exclusively via the same leaf (`0x0800b2ae`). Never
mixed with `0x20005534` in any traced call. **S.**

## Net for HANDOFF layer 4 — extends I/N

**Diagram gets a real node, but not a real gate.** `0x20005534` is
confirmed as a genuine TIM2 hardware wrapper, touched by exactly the
set of sources N-05534.txt found (internal timer IRQ, incoming MIDI
Clock byte, EXTI0 external pulse, transport commands). What it does
**not** have is a software arbitration flag choosing between them —
every source that reaches this object just directly pokes TIM2's
registers (start/stop/reset), unconditionally. This is a genuine,
useful negative result: "internal vs MIDI clock" in this firmware looks
less like a selected mode and more like whichever source last touched
the timer wins, with the hardware DIP switch (control ID `0x13`,
un-located in software) as the only actual mode gate this project has
found so far — and even that is not confirmed to touch this object.

STATUS: done
