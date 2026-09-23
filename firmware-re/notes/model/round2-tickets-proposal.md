STATUS: proposal — request to Cursor / Jim
AGENT: claude
TICKET: none (not a scan/model ticket itself — a proposed queue
extension for docs/HANDOFF.md ceiling review + tickets.md)
UPDATED: 2026-09-23T22:00+01:00
INPUT: model/synthesis.md; model/Q-promote.md; model/lead-usb-din.md;
all closed A-Q tickets

# Round 2 — proposed tickets R-Y

**Ceiling reminder, stated plainly**: `tickets.md`'s own board already
caps this method at **80-85/100**. Bootloader, USB-stack body, live
flash/occupancy re-run, and `other repo/`-as-fact stay excluded — this
batch does not ask to cross any of those lines. It targets the
concrete, evidenced gaps A-Q left open, not "everything."

Every item below cites the specific finding that motivates it — none
are speculative fishing expeditions. Format matches `tickets.md`'s
existing letter-ticket style so Cursor/Jim can drop these straight in
after Q closes. **Request, not a claim of authority over `tickets.md`
— I don't own that file.**

## R — USB/DIN vtable identity (highest priority, most isolated)

**Motivation**: `J-voice.md` found the port-switch mechanism;
`lead-usb-din.md` (my own capstone spot-check) found it operates on
`*(0x20001eb8+0)`, a pointer set once at ctor time from an external
arg — not on the three per-note tables I ended up mapping instead.
That pointer's own object (the real vtable holding USB/DIN send
functions) has never been disassembled.

**Cursor:** `scans/R-usbdin.txt`. Find every ctor-sweep site (or other
static write) that stores into `0x20001eb8+0` — i.e. what gets passed
as `r6` into `0x0801b572`'s ctor. Disassemble that source object's own
ctor. Also: full prologue of `0x0801b384` (port_switch) itself — where
does *its* `r0` argument ultimately originate on the key path (trace
back through `0x0801b996`'s `r6`, per `lead-usb-din.md`)? Search for
`0x40013800` (USART1) and `0x40005C00` (USB) literals anywhere within
2 call-levels of `0x0801ad20`/`0x0801ae56`.

**Claude:** `model/R-usbdin.md` + proposed. Close or explicitly fail to
close which vtable slot is USB vs DIN.

**Gate:** none — scan can start immediately, doesn't depend on any
other Round-2 ticket.

**Stop:** either a peripheral literal is found reachable from the
vtable slots (close it), or explicitly state it isn't reachable by
static means and the question needs emulation (Unicorn) instead — a
real, useful negative result either way.

## S — Remaining ctor roles, second pass

**Motivation**: `G-objects.md` left ~24 ctor sites with existence-only,
no role. Several now have more context than G had (H's field table,
J/M's port and chord findings) that could resolve a few without new
disassembly of the ctors themselves — but some genuinely need their
*readers* found, which G explicitly didn't do.

**Cursor:** `scans/S-ctor-readers.txt`. For each of G's still-role-less
RAM addresses (list in `G-objects.md`'s table, rows tagged "H role"),
whole-image search for static `bl`/load references to that address
outside its own ctor. Report every reader found, 10 insns each.

**Claude:** `model/S-ctor-roles.md` + proposed. Assign role S wherever
a reader plus its behavior makes it unambiguous (same method that
closed the debounce-family role in ticket C). Leave H with reasoning
otherwise.

**Gate:** none — independent of R.

**Stop:** every G-flagged role-less object either has a reader-based
role or an explicit "no reader found" note.

## T — Clock source selection

**Motivation**: `I-time.md` and `N-sync.md` both converge on
`0x20005534` as the likely internal/MIDI clock meeting point, but
neither traces what actually writes tempo/interval data into it, or
how the two sources (TIM2 vs `0xF8` MIDI Clock byte) are arbitrated
if both are active.

**Cursor:** `scans/T-clock-source.txt`. Every static write to
`0x20005534`. `0x0800b0c6` (the MIDI-Clock-byte callee) and
`0x0800b2ae` (TIM2's callee) — full bodies, 20 insns each. Whether
either checks a "which source is active" flag first (candidate: the
Sync DIP, control ID `0x13` per `stock-shift-map.md`'s unshifted-panel
table — search for that immediate too).

**Claude:** `model/T-clock.md` + proposed. Extends I/N: does the
diagram get a real source-select node, or does it stay "both write the
same place, arbitration unclear"?

**Gate:** none.

**Stop:** clock source enum resolved, or explicit "no arbitration
logic found in these two callees" (still useful — narrows to the DIP
switch's own GPIO read, which may be genuinely out of software scope).

## U — SET protocol counterpart

**Motivation**: `K-protocol.md` mapped GET (`0x0800ee92`'s TBB) and
found `r2!=0` is a bare `bx lr` — no SET body on that branch. A SET
path must exist (MCC can write settings), just not through this
function.

**Cursor:** `scans/U-set-protocol.txt`. Search for a second TBB/switch
structure shaped like `0x0800ee92`'s (indexed on a signed byte from an
incoming buffer) anywhere else in the image. Also check the 3 sibling
GET handlers (`0x0800614c`, `0x080060c4`, existing `get_param`) for a
write-path branch not yet walked.

**Claude:** `model/U-set.md` + proposed. GET/SET pairing table, or
explicit "SET is not a mirror of GET, found elsewhere as X."

**Gate:** K done (already true).

**Stop:** SET entry point named, or explicitly not found in a stated
search scope.

## V — Persistence commit path (application level only)

**Motivation**: `O-persist.md` states plainly that no RAM-to-flash
commit path for sequence data has been found. `seq_step_store`'s
writes land on a RAM staging block (`*0x200010fc`), not the flash slot
base. **Do not reverse ST HAL internals** (`0x08008140`,
`0x0800dd8c`'s deeper callees past the application boundary already
walked in O) — stay at the application-call level only.

**Cursor:** `scans/V-persist-commit.txt`. Static callers of
`0x080186d4` (FLASH IRQ4) and of `seq_slot_base`'s three known callers
(`0x0800de16`, `0x0800de96`, `0x0800e21a`, from O) — walk those three,
10 insns each, to see if any one of them is the actual RAM→flash copy
trigger.

**Claude:** `model/V-commit.md` + proposed.

**Gate:** O done (already true).

**Stop:** commit trigger named, or explicit "not found within the
application-level boundary this ticket searched."

## W — LED/DMA closure

**Motivation**: `P-led.md` narrowed DMA to one candidate
(`0x080185e8`/`*0x200010f0`) but didn't confirm it's LEDs specifically.
Rec LED remains unfound across two independent tickets (L, P).

**Cursor:** `scans/W-led-confirm.txt`. Full body of `0x080045b6` and
its tail-call `0x08004566` (from P) — does either reach the LED writer
`0x0800d26e` or the refresh `0x0800d1f8`? Also: of the writer's 33
callers (`0x0800d2f2`-`0x0800daac`, from P), which ones are reached
from the Rec-press path (`0x0801780c`'s notify calls, or
`0x200010b6`'s read sites from L) — even an indirect chain.

**Claude:** `model/W-led.md` + proposed.

**Gate:** P + L done (already true).

**Stop:** DMA1_CH1's LED role confirmed or ruled out; Rec LED found or
explicitly exhausted within the 33-caller search space P already
bounded.

## X — Chord/knob family selector + F's leftover cases

**Motivation**: `M-chord.md` found two parallel byte-value families
(`0x08-0x0e`, `0x16-0x1b`) writing the same three fields, selector
unknown. `F-buttons.md` left unshifted index 0 (Hold) unresolved and
indices 6/7 (Stop/Play) target addresses not fully shown.

**Cursor:** `scans/X-selectors.txt`. Static callers of
`param_field_dispatch` (`0x0800f054`) — what sets the `+0x3c` index
byte for each family, and is there a visible "bank" selector nearby
(candidate: `+0x15` field, already seen gating Shift+Chord in F).
Also: full bodies of unshifted-table indices 0/6/7
(`0x08017834`/`0x08017298`/`0x0801743e`, cut off in F's scan).

**Claude:** `model/X-selectors.md` + proposed.

**Gate:** F + M done (already true).

**Stop:** family selector named or explicit H; Hold/Stop/Play unshifted
cases each have a full target read.

## Y — Recorder remainder + hold-length-clear gesture

**Motivation**: `L-record.md` left TBB cases 3/5/6 of
`seq_step_store`'s dispatch unwalked (case 3's per-step loop is the
actual note recording). `stock-shift-map.md`'s "Shift+Oct−+Oct+ clears
all notes, keeps length" gesture has never been mapped to firmware —
candidate location: F's B-sites 15/16 (`0x200010d0`/`0x200010d6`
bookkeeping, flagged as a plausible multi-button mechanism, never
confirmed).

**Cursor:** `scans/Y-record-rest.txt`. `seq_step_store`'s TBB cases 3
(`0x0801446a`), 5 (`0x08014494`), 6 (`0x080144c2`), 20 insns each.
Also re-dump B/F sites 15/16 with enough body to see what reads
`0x200010d0`/`0x200010d6` besides the write sites already known.

**Claude:** `model/Y-record-clear.md` + proposed.

**Gate:** L + F done (already true).

**Stop:** case 3 (the real recording write) named; hold-length-clear
either mapped to a handler or explicitly still unmapped.

## Suggested wave order

R, S, T, U, V, W, X, Y have **no cross-dependencies on each other** —
all gates are satisfied by already-closed tickets (Q and earlier).
Cursor can scan them in any order or parallel; I'll model whichever
scan lands first, same standing-instruction pattern as the A-Q run.

## What this batch does NOT attempt (staying inside the ceiling)

USB/MIDI stack body, bootloader, live flash of any kind, occupancy
re-run, full 256-wide GET/SET param table, exhaustive naming of every
remaining ctor site regardless of reader evidence, and any `other
repo/` claim not re-derived by a scan. If R-Y all close cleanly, the
honest next self-assessment would land somewhere in the 60s out of
100 — still short of the stated 80-85 ceiling, which is itself short
of 100 by design.
