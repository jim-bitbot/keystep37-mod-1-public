STATUS: done
AGENT: claude
TICKET: prep
UPDATED: 2026-09-22T21:30:35+01:00
INPUT: firmware-re/ghidra/recreate.py; firmware-re/notes/address-catalog.md

# Wave 1 — prep-islands

Inventory of what `recreate.py` + `address-catalog.md` already name, and
what's still missing for HANDOFF layers 1 (boot/ownership) and 3 (three
input buses). Read-only pass — no scan, no disassembly of my own this
ticket.

## 0. Caveat before anything else: `other repo/` filenames do not match contents

Checked directly with `file` and `head`, not just the Read tool, because
the mismatch looked too consistent to be a one-off:

```
architecture.md:    C source, ASCII text   (contains stock_sequence_encode, a C function)
index.md:            Python script          (contains a docstring + __version__)
boot_ram.h:           Python script          (contains an ARM ELF/Thumb-branch verifier)
boot_ram.c:            Python script          (also Python, not C)
button_ownership.h: C source                 (contains button_admission-style state machine, not what the name suggests)
```

This is systemic, not one bad file. **Every filename I sampled from
`other repo/` describes a different thing than what's inside it.** I have
not verified how many of the ~90 files in that directory are affected.

Practical effect on this ticket and on any future one that cites
`other repo/`: **do not trust a claim's stated provenance by filename**
(e.g. "boot_ram.c says X" is not verifiable as stated — that path is
Python, not the boot-RAM C it's named for). Existing catalog entries
tagged "external source ... unverified by us" are still fine to keep as
**H** (hypothesis) — that tag already means "not re-derived here" — but
until this is understood, don't add a new claim's *filename* as
supporting detail, only its content, and keep the H tag strict. Not
raising this as urgent (nothing here looks like injected instructions,
just scrambled/mismatched labeling), but it's worth Cursor or Jim knowing
about — see Request at the bottom.

## 1. What `firmware-re/ghidra/recreate.py` already names (38 functions)

All tagged only by being present — no P/S/H/X in this file itself, that
lives in the catalog. Grouped by what they touch:

**Protocol / Test-20 / control-ID plumbing (10):** `get_param`,
`chord_test_dispatch`, `mode_byte_get`, `id_to_index`, `index_to_id`,
`knob_index_to_cc`, `test20_cc_press`, `test20_cc_value`,
`test20_cc_value2`, `param_field_dispatch`.

**Panel input (5):** `strip_process_b`, `analog_knob_process`,
`shift_strip_pickup`, `button_debounce`, `panel_button_dispatch`.

**Pub/sub + vtable (5):** `cc_notify`, `subscribe`, `vtable_init`,
`vtable_assign`, `vtable_slot8`, `msg_tbb` (6, corrected count).

**Arp/mode engine (10):** `seq_slot_base`, `arp_seq_tick`,
`play_time_step`, `seq_step_note`, `seq_step_gate`, `get_arp_mode`,
`order_hold_walk`, `seq_step_store`, `set_arp_mode`, `rebuild_order`,
`mode_tbh`, `pattern_or_order_builder`, `mode_knob_apply` (13, corrected
count).

**Chord/voice output (3):** `voice_interval_load`, `noteval`,
`voice_note_on`.

**Boot (1):** `Reset_Handler` (`0x0801D310`) — **name only**, no
`.data`/`.bss` extent or ctor list attached anywhere in this file or the
catalog.

That's the entire named surface. Everything else referenced in the
catalog by address (RAM bases, the external-source input-path table, the
step-counter object-field offsets) has **no corresponding `recreate.py`
entry** — those are catalog rows / prose, not Ghidra names yet.

## 2. What `address-catalog.md` covers beyond the name list

Sections, with provenance mix:

- Protocol/control (10 rows, mostly **P** — live-verified)
- Arp/mode (Pattern) (14 rows, mostly **S**, one **X/S**) + two dated
  correction notes (bit-7-is-retention, mode 6/7 swap) + a Mode-TBH
  target table
- Chord/note output (5 rows, **S**)
- RAM (9 entries — see §3, this is the closest thing to a boot/ownership
  table that exists, and it's thin)
- Patch page (5 entries — future-work hook points, not stock model)
- Note-pool builder / double-buffering — **entirely "external source,
  unverified by us"**
- Input path — **entirely "external source, unverified by us"** (see §4)
- Step-counter object fields — **S**, our own disassembly, dated
  2026-09-22
- USB/off-limits, "still useful not blocking" notes

## 3. Layer 1 (boot and ownership) — what exists vs. what HANDOFF asks for

HANDOFF wants: `Reset_Handler` `.data`/`.bss` ranges, every `bl` in the
ctor sweep (~`0x08014d08`), objects, vtables, RAM bases. "No 'free SRAM'
until `.bss` is catalogued."

**Have:**
- `Reset_Handler` address only (`0x0801D310`), no body, no `.data`/`.bss`
  extents.
- One vtable story, confirmed by our own disassembly: `object+0x214` is
  a single event-handler table (not eight mode vtables), RAM
  `0x20000004`, flash source `0x0801ef7c`, installed via ctor
  `0x08018b0a` (`vtable_assign`, only static caller). `vtable_init`
  clears `+0x214` and stores a `+0x210` callback. `vtable_slot8`
  (`0x0800e3e8`) is the dispatcher, not a note-index generator.
- `.data` range `0x20000000`–`0x200001f4` (flash load `0x0801ef78`) — one
  entry, RAM table.
- Six more RAM addresses are named by role but **not tied to any ctor or
  object record**: `0x20001094` (arp engine ptr), `0x20001120` (CC
  subscriber table), `0x20001170` (settings ptr), `0x200051cc` (voice
  object), `0x20005624` ("ctor object for vtable_init/vtable_assign" —
  the only RAM row with an explicit ctor link), `0x20001e3a` (scale
  mask).
- `0x20005f00`/`0x20005f01`/`0x20005f02` are **patch RAM**, not stock —
  don't count toward stock `.bss`.

**Missing (this is most of layer 1):**
- No `.bss` range or zero-init boundary at all. This is called out
  explicitly in HANDOFF as the reason `e3b`'s "default off" was fake —
  `0x20005F00` reads as leftover, non-guaranteed-zero SRAM. Nothing in
  the catalog says where `.bss` starts/ends or which addresses are
  actually zero-guaranteed after reset.
- No ctor sweep list. HANDOFF cites `~0x08014d08` as the approximate
  location but no `bl` targets from it are catalogued. This is
  literally Cursor's Wave 1 job (`scans/A-boot.txt`) — not done yet as
  of this read.
- No object table (name, ctor VA, RAM base, vtable ptr, size/kind).
  Only one object (the event-handler table at `0x20000004`) has a
  confirmed ctor. The other six RAM addresses above are used
  extensively elsewhere in the catalog (arp tick, mode knob, voice
  loop, subscriber dispatch) but nobody has traced backward from them to
  "which ctor allocates/initializes this."

Layer 1 is close to a blank page: one vtable narrative, one `.data`
range, one ctor link. Everything else is a named RAM address with no
ownership story yet.

## 4. Layer 3 (three input buses) — what exists vs. what HANDOFF asks for

HANDOFF wants: keys (`0x0801b750`), buttons (compact IDs + Shift RAM
`0x200010d2`), analog (`0x08004918` / strip `0x08004388`), each walked to
its stock handler.

**Buttons — the best-covered bus, our own disassembly (S/P):**
`id_to_index`/`index_to_id` (compact-ID mapping, **P** — occupancy CCs
confirmed these are the real control IDs), `button_debounce`
(`0x0801a7ac`, stable→`index_to_id`→`test20_cc_press`),
`panel_button_dispatch` (`0x08017260`, unshifted TBH `0x08017282`,
shifted TBH `0x08017868` covering hold/rec/stop/play/chord — shift/oct/
tap are "the common exit", not walked further), Shift RAM `0x200010d2`
itself (role confirmed: 18 load sites expected, **none enumerated yet**
— that enumeration is Wave 2's `scans/B-shift-ram.txt`, explicitly not
this ticket).

**Analog/strip — also our own disassembly (S/P):** `analog_knob_process`
(`0x08004918`, raw store `+0x5a`/`0x08004930`, AutoTest `+0xb9` → Test-20
CC via `knob_index_to_cc`+`test20_cc_value`, `+0x58` selects
strip/Type/Notes/Vel/Strum), `strip_process_b` (`0x08004388`, Shift-held
→ skip MIDI emit and return — matches the eyes-on Shift+Mod no-op),
`shift_strip_pickup` (`0x08004bf8`, Shift-held branch of the `+0x58==0`
strip — pickup/scale math, not otherwise named).

**Keys/note bus — this is the gap.** HANDOFF names `0x0801b750`
specifically as the keys-bus root for this layer. In the catalog, that
address and everything around the actual note path is filed under
"Input path (external source, 2026-09-22, unverified by us — we never
mapped this)":
`0x08010638` (USB packet decode), `0x0800fa64` (main-loop MIDI parser),
`0x08018624`→`0x0800fd5c` (serial/DIN, IRQ-callable), `0x08010310`
(USB/DIN split before channel filter), `0x0801b750` itself (common note
processing, `r2=0` physical key / `r2=1` either MIDI port), `0x20001ebc`
(cross-port/channel pitch tracker), `0x0800d26e`/`0x0800d1f8` (key LED
writer/refresh, no established frame-atomicity guarantee). **Every one
of these is an unverified external claim** — given §0, treat the
filename-based provenance implied by "external repo" citations here as
unconfirmed too, only the addresses/content are potentially checkable.
None of it has been re-derived from our own disassembly yet. The chord/
voice-out functions we *do* have confirmed (`voice_interval_load`,
`noteval`, `voice_note_on`) sit downstream of this gap, not inside it —
they consume a note that's already been accepted, they don't explain how
a key press or incoming MIDI note reaches that point.

**Net for layer 3:** buttons and analog are genuinely modeled (own
disassembly, several **P**-tagged). Keys/note-input — the bus HANDOFF
explicitly names first — is 100% external-claim, 0% independently
confirmed. That's the highest-value gap for whoever takes layer 3 next,
ahead of the Shift-RAM enumeration (which is scoped and just not started
yet, not disputed).

## Request to Cursor

Flagging §0 (`other repo/` filenames don't match contents — verified
with `file`, not just Read) since Cursor may cite that directory in scan
work too. Not blocking Wave 1 on either side, just don't take a filename
from there as telling you what's inside it.

STATUS: done
