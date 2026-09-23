STATUS: proposal — request to Cursor / Jim
AGENT: claude
TICKET: none
UPDATED: 2026-09-24T00:50+01:00
INPUT: model/synthesis.md's post-Round-4 state; AI/AB/AC/AE/Z's specific
open items

# Round 5 — proposed tickets AK-AP

Six tickets, ranked by expected value. AK is the clear priority — it's
the only lead from four rounds of work that could plausibly move
layer 1 by double digits, not fractions of a point.

## AK — open the three unexamined ctor sweeps (highest priority)

**Motivation**: `AI-objects.md` found `init_array` slots 2, 3, 5 wrapped
in the exact same gate shape as `ctor_sweep` (`r0=1,r1=0xffff`), one
with a matching dead-wrapper sibling. None of `0x8005da8`, `0x8010f40`,
`0x8015f74` has been opened. If even one is a real object-construction
table, this could mean dozens of uncatalogued objects — the single
highest-leverage remaining scan in the project.

**Cursor:** `scans/AK-sweep-open.txt`. For each of the three targets:
confirm it's gated the same way (`r0==1 && r1==0xffff` check), then
dump the first 40-60 instructions looking for a repeated `bl`-with-
fresh-RAM-literal pattern (the `ctor_sweep` shape). If it's real,
number the `bl` sites the same way `A-boot.txt` numbered the original
53.

**Claude:** `model/AK-sweeps.md` + proposed. Object table continuation,
same tagging discipline as G.

**Gate:** none — can start immediately.

**Stop:** each of the three targets classified as "real sweep, N sites
found" or "not a sweep, here's what it actually is" — either is a
valid close.

## AL — Sync DIP, sharper method

**Motivation**: `AB-sync-dip.md`'s bare-immediate search was too broad
and got drowned in unrelated `0x13` hits. Re-attempt with a method
targeted at the actual hardware operation.

**Cursor:** `scans/AL-dip-gpio.txt`. Search specifically for a GPIO
**IDR** read (offset `+0x08` on any of the 5 known GPIO bases) followed
within ~10 instructions by a single-bit test (`tst`/`and` with a small
power-of-2 immediate), in code reachable from boot/init or
`app_main_loop`'s one-shot head.

**Claude:** `model/AL-dip.md` + proposed.

**Gate:** none.

**Stop:** DIP pin/register found, or explicit "not found by this
method either" — a second real negative is still useful.

## AM — hold-length-clear, outside Shift-RAM territory

**Motivation**: Three independent passes (Y, my own side investigation,
AE) confirm hold-length-clear isn't anywhere in the Shift-RAM/
button-dispatch code this project has mapped. `AE-tap-clear.md`
recommends `key_scan` itself as the next place to look.

**Cursor:** `scans/AM-keyscan-oct.txt`. Full body of `key_scan`
(`0x0800cc48`) — not just its already-mapped call sites into other
functions, the function's *own* logic — looking for a simultaneous
Oct−/Oct+ (compact index 2 and 3) check.

**Claude:** `model/AM-clear.md` + proposed.

**Gate:** none.

**Stop:** gesture found, or a fourth independent negative (still
useful — would mean the gesture isn't reachable via any input path
this project's method can see, which is itself worth stating plainly).

## AN — analog kind 1-4, proper TBB table decode

**Motivation**: `AC-analog-names.md` found kind-0's fallback maps to
Rate's CC but couldn't confirm the kind1-4 ordering — the scan didn't
extract `knob_index_to_cc`'s raw table bytes, only inferred from code
layout.

**Cursor:** `scans/AN-tbb-bytes.txt`. Raw byte dump of
`knob_index_to_cc`'s table (4 bytes immediately after the `tbb` at
`0x080060a8`), decoded per the same method `F-buttons.txt` used for
`panel_button_dispatch`'s tables (explicit `case N → byte → target`).

**Claude:** `model/AN-analog-order.md` + proposed.

**Gate:** AC done (already true).

**Stop:** kind1-4 → CC mapping confirmed exactly, closing AC's H.

## AO — USB send entry, one level in

**Motivation**: `Z-usbdin-emu.md` found `0x08010e46` is the real USB
send entry (`bl 0x080091ca`), never reached from `emit_key`/`emit_seq`.
Nobody has found *what calls* `0x08010e46`.

**Cursor:** `scans/AO-usb-caller.txt`. `bl`-to search for
`0x08010e46`. If found, 12 insns of context at the caller. **Do not**
walk into `0x080091ca` itself or below — that's USB-stack-body
territory, off-limits per project rules.

**Claude:** `model/AO-usb-trigger.md` + proposed.

**Gate:** Z done (already true).

**Stop:** caller found (closing the question of what triggers USB
output), or explicit "not found by static bl / Thumb-pointer search"
(same honest-negative shape as AH's `0x0801509a` question).

## AP — emit_seq's unpopulated Note-On slot

**Motivation**: `Z-usbdin-emu.md`'s most concrete new gap: `emit_seq`'s
Note-On path reads object fields `+0x18`/`+0x1c` that the traced
`0x0801acb0` ctor never writes. Real structural hole, not a harness
artifact (Z's own scan says "did not invent a target").

**Cursor:** `scans/AP-emitseq-slots.txt`. Search for any static write
to `0x20001d60+0x18` or `+0x1c` (the object `R-usbdin.txt` traced)
anywhere in the image, including inside functions not yet walked.

**Claude:** `model/AP-emitseq.md` + proposed.

**Gate:** R + Z done (already true).

**Stop:** writer found, or explicit "these fields are never written —
this code path is dead in stock firmware" (a real, citable conclusion
either way).

## Suggested order

AK first, alone if throughput is limited — it's the one ticket here
that could change the shape of layer 1, not just add a fact to it.
AL/AM/AN/AO/AP have no dependencies on each other or on AK.
