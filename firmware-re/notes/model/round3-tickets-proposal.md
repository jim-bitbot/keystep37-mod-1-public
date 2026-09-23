STATUS: proposal — request to Cursor / Jim
AGENT: claude
TICKET: none
UPDATED: 2026-09-23T23:15+01:00
INPUT: model/synthesis.md's post-Round-2 open-leads list

# Round 3 — proposed tickets Z, AA (deliberately small)

Round 2 closed cleanly, but three of its own tickets (R, T, V)
concluded — as real findings, not excuses — that **further static
disassembly is the wrong tool** for what's left: R needs runtime state
a static scan can't produce, T found no software gate to keep
searching for, V hit a real scope boundary (ST HAL internals, out of
bounds by this project's own rules). Proposing two small tickets for
what's actually still reachable by scanning, plus one explicit
non-ticket recommendation.

## Z — param_field_dispatch's family selector

**Motivation**: `X-selectors.md` re-hypothesized the two byte-value
families (`0x08-0x0e` vs `0x16-0x1b`) as panel-knob-write vs.
MIDI-CC-write, based on both callers sitting in MIDI-message territory
— but didn't confirm it. This is the one still-open item from Round 2
that looks genuinely findable by more static search, not emulation.

**Cursor:** `scans/Z-dispatch-source.txt`. Full bodies of
`param_field_dispatch`'s two callers' *own* callers (one level further
up from `0x0800fd4e`/`0x0800ffda`) — does either trace back to a panel
knob interrupt/poll path (`analog_knob_process`, `D`) versus a MIDI-CC
parse path (`0x0800fa64`, main-loop parser)? That would directly
confirm or kill the panel-vs-MIDI-CC hypothesis.

**Claude:** `model/Z-selector.md` + proposed.

**Gate:** X done (already true).

**Stop:** hypothesis confirmed, killed with a replacement, or explicit
"still not resolvable by static search" — any of the three is a valid
close.

## AA — hold-length-clear gesture (Shift+Oct−+Oct+)

**Motivation**: Still the only stock-documented gesture
(`stock-shift-map.md` §4, confirmed live) with zero firmware mapping
after 25 closed tickets. Y ruled out sites 15/16. B's own sites 07/17
were flagged as "Oct/Tap/Chord family, weak/moderate H" and never
resolved past that.

**Cursor:** `scans/AA-oct-combo.txt`. Full bodies of B's sites 07
(`0x08016982`) and 17 (`0x0801a288`) — both only partially dumped in
the original B scan. Also: search for any function that reads **both**
Oct− and Oct+ compact-ID state (indices 2 and 3) simultaneously — a
combo detector would need to check both, not just one Shift-RAM byte.

**Claude:** `model/AA-oct-clear.md` + proposed.

**Gate:** B + F done (already true).

**Stop:** gesture mapped to a handler, or explicit "not found in the
18 Shift-RAM sites or button dispatch — must be elsewhere" (still
useful: narrows where it isn't).

## Not a ticket — recommendation on USB/DIN

`R-usbdin.md`'s conclusion stands: the peripheral identity on
`0x20001d60`'s vtable slots needs **Unicorn emulation** of the ctor
call site with real register state, not another static scan. This
doesn't fit the Cursor-scans/Claude-models division of labor this
project has used — it's a different tool (`emulate_ks37.py` already
exists in the repo) and I'm not certain who owns writing a new
emulation harness under the current file-ownership rules. Flagging for
Jim to decide, not assuming it's either agent's job by default.

## What this batch does NOT include, and why

No third pass at G's remaining existence-only ctor sites (S already
found diminishing returns there). No further V/persistence ticket (real
scope boundary hit, not unexplored). No case-5 semantic ticket for Y
(minor, better folded into AA or a future pass than given its own
letter).
