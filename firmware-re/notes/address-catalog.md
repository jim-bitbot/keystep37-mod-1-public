# Address catalog — KeyStep 37 firmware 1.1.6.579

**Current work (2026-09-22):** grow this catalog into a machine model
(boot, objects, RAM, loop/IRQs, three input buses, time, voice). Feature
patches (Euclidean / chord) are **future**. See
[`docs/HANDOFF.md`](../../docs/HANDOFF.md).

**Use the stripped flash extract**, not the framed `.led` decode:

`firmware-re/firmware-images/keystep37_1.1.6.579_flash.bin`

File offset 0 = `0x08000000`. Application pages start at **`0x08004000`**
(vector table + Thumb). The framed 117140-byte file is a Huaxin segment
stream; loading it as flat Thumb gives **file offsets, not flash VAs**.
Old catalog numbers in parentheses are those framed-file VAs.

Provenance: P = live protocol + code match, S = structure from
disassembly / unicorn, H = hypothesis, X = ruled out.

## Protocol / control

| Flash VA | Framed (obsolete) | Name | What | P |
|---|---|---|---|---|
| `0x08005e84` | `0x08001f68` | get_param | GET `globalParamId` | P |
| `0x08005df8` | `0x08001edc` | chord_test_dispatch | Control `0x69` (CC 105) ON/OFF | P |
| `0x08005ccc` | | mode_byte_get | `ldrb [r0,#0x55]` — live Mode value used as `r1` for `set_arp_mode` | S |
| `0x08006024` | | id_to_index | Control ID → compact 0–7 (hold/shift/octm/octp/tap/rec/stop/play); else 8. Occupancy CCs **are** these IDs | P |
| `0x0800606c` | | index_to_id | Compact → ID (TBB). Button debounce uses this before Test-20 emit | S |
| `0x080060a2` | | knob_index_to_cc | Knob compact → CC `0x62`–`0x66` (98–102 Type/Notes/Vel/Strum/Rate) | P |
| `0x080067f4` | | test20_cc_press | Builds `B0 <id> 01`. Called from debounce `0x0801a7f6` after `index_to_id` | P |
| `0x080068c8` | | test20_cc_value | Builds `B0 <id> <val>`. Analog Test-20 path `0x08004974` | P |
| `0x08006914` | | test20_cc_value2 | Same `B0` shape; Shift+Mode emits id `0x15`, Shift+TimeDiv id `0x68` when AutoTest `+0xb9` | P |
| `0x08016bc4` | `0x08013482` | cc_notify | Catalog name; real `push` is `0x08016bd4`. Test-20 occupancy CCs come from `0x080067f4` / `0x080068c8` | S |
| `0x0801cc5c` | `0x08019808` | subscribe | 3-slot × 20-byte callback table at `0x20001120` | S |

## Arp / mode (Pattern)

There are **not** eight mode vtables at `object+0x214`. That slot holds
one event-handler table (`.data` at RAM `0x20000004`, flash
`0x0801ef7c`). Slot `+8` is `0x0800e3e8` (event dispatcher).

Pattern is **arp-engine `+0x10` == 6** (panel CC21 = 7; CC21 = internal + 1).

| Flash VA | Framed (obsolete) | Name | What | P |
|---|---|---|---|---|
| `0x08011794` | | set_arp_mode | `if (*obj+0x10 != r1) { *+0x10 = r1; notify }` | S |
| `0x08011a1c` | | rebuild_order | 8-way **TBH** on `ldrb [obj,#0x10]`; `cmp #7` | S |
| `0x08011a38` | | mode_tbh | Cases 0–7 → Up / Down / Incl / Excl / Random / Order / Walk / **Pattern** | S |
| `0x08011c88` | | pattern_or_order_builder | TBH cases **5 and 7** (Order and Pattern share the hold-order list build) | S |
| `0x08016a26` | | mode_knob_apply | `mode_byte_get` then `set_arp_mode`. Settings ptr `*0x20001170`, engine `*0x20001094` | S |
| `0x08017f20` | | set_mode_alt | Second `bl` to `set_arp_mode` | S |
| `0x0800e4d2` | `0x0800a9b2` | vtable_init | Clears `+0x214`, stores `+0x210` callback | S |
| `0x0800e4fe` | `0x0800a9de` | vtable_assign | `str.w r1,[r0,#0x214]`. Only static `bl` is ctor `0x08018b0a` (installs RAM vtable `0x20000004`) | S |
| `0x0800e3e8` | | vtable_slot8 | Event dispatcher, not a note-index generator | S |
| `0x0800ea7e` | `0x0800af7c` | msg_tbb | 10-way message TBB. **Not arp modes** | X/S |
| `0x0800dd30` | `0x0800a1d4` | seq_slot_base | `0x0803B000 + n*0x800` | S |
| `0x080129cc` | | arp_seq_tick | Clock. Computes the current step, then `bl 0x08013e8c` at `0x08012ec0` (`r1` = step, `r0` = `*(tick+0x50)`). Also `bl rebuild_order` at `0x08012b62` | S |
| `0x08013e8c` | | play_time_step | **Pattern player.** Reads the current slot step and emits. Callers: tick `0x08012ec0` (Arp, once per step change), dispatch `0x08012028` via `0x08011ff0` (different object, gated on `*(0x20001124)+0x10==2`). When `engine+0xf==0` and `+0x10==5` (Order) remaps the step through `0x08011878`; **mode 6 (Pattern) and mode 7 keep the sequencer step** | S |
| `0x080130e8` | | seq_step_note | `*(uint8*)(*obj + (voice + step*8)*2)` — 16-byte stride, 8 voices × 2 bytes. Voice 0 is the Pattern pitch byte | S |
| `0x080130f4` | | seq_step_gate | Byte +1 of the same cell. `0x82` at step 0 is the empty-slot magic from `0x080137c4`. Callers (all inside `play_time_step`): `0x08013f62`, `0x08013fde`, `0x080141d2` — E0+ retarget these to `euclid_wrap` | S |
| `0x08011874` | | get_arp_mode | `ldrb r0,[r0,#0x10]` | S |
| `0x08011878` | | order_hold_walk | Order-only index into the rebuilt hold list | S |
| `0x08014418` | `0x08010bc8` | seq_step_store | **Recorder**, not the player. One `bl` from `0x080065e4` | S |
| `0x0801415c` | | seq_step_release | Release/tie handling: scans voices for pitch `==0x81` (tie) first; only if none found, tests bit 7 of `seq_step_gate`'s return to decide whether to release a held note. Confirmed by direct disassembly, 2026-09-22. Governs tie/Note-Off timing, not note-start gating. | S |
| `0x08013ebc`–`0x08013ecc` | | pitch_gate_check | Inside `play_time_step`. Reads voice 0's pitch via `seq_step_note`, computes `(pitch+0x7f)&0xff`, early-returns (no note attempted) if `<=1` — true exactly for `pitch==0x81`/`0x82`. **The actual note-emission gate.** Confirmed by direct disassembly, 2026-09-22. Candidate hook point for a rhythmic/Euclidean patch, in place of `seq_step_gate`. | S |

### Correction (external source, 2026-09-22): bit 7 is retention, not a gate

**Revises the `seq_step_gate` entry above.** An independently-developed
external repo studying the same firmware (same version, 1.1.6.579)
describes the byte at `step*16 + voice*2 + 1` more precisely: bits 0-6
are velocity; **bit 7, voice 0 only, "participates in retention"** (i.e.
tie/hold-over-from-previous-step), not a direct "should this step
produce a Note-On" flag. This directly explains the E0 hear-test
failures logged in `findings-2026-09-20.md` and `docs/HANDOFF.md`:
clearing bit 7 on a Euclidean "miss" (what `euclid_wrap` does) most
likely changes whether the step is treated as a tied continuation versus
a fresh articulation, not whether a note sounds at all — consistent with
every hear-test showing a Note-On on every step regardless.

**Update, 2026-09-22: independently confirmed**, not just an external
claim anymore. Disassembled `play_time_step` and `seq_step_release`
directly. The real "does this step attempt a note" gate is voice 0's
**pitch byte** checked at `0x08013ebc`-`0x08013ecc`
(`(pitch+0x7f)&0xff <= 1`, true exactly for `pitch==0x81` or `0x82`,
verified by hand) — an early function return, nothing to do with
`seq_step_gate` at all. `seq_step_gate`'s bit 7 is consumed by
`seq_step_release` (tie-scan fallback) and by a local flag inside
`play_time_step` that gates writing a cached previous output pitch into
a retention-tracking array — real, but unrelated to note emission. See
`findings-2026-09-20.md`'s "Root cause ... confirmed" entry for the full
trace. Treat the old "gate / `0x80` flags" wording above as superseded.

### Header fields (external source, 2026-09-22, unverified by us)

| Block offset | Meaning |
|---|---|
| `0x400` | Length, max 64 |
| `0x401` | Swing (slot-global) |
| `0x402` | Gate (slot-global) — distinct from the per-step byte above |
| `0x403` | Partially-understood flags; preserve unknown bits |
| `0x404` | Retention-source selector, read by `seq_step_release` (`0x0801415c`) |
| `0x405–0x407` | Unknown |

### Pitch/marker sentinels (external source, 2026-09-22, unverified by us)

Sharper than the earlier "`0x82` = empty-slot magic" phrasing:

- `0xFF` — terminates a voice
- `0x81` — retains the preceding note (tie start)
- `0x82` — starts no new note, but is **not** an unconditional Note-Off
  (a held/tied note can still be sounding)

Mode TBH targets (1.1.6.579):

| Value | Name | Builder |
|---|---|---|
| 0 | Up | `0x08011a9e` |
| 1 | Down | `0x08011ae0` |
| 2 | Incl | `0x08011b2c` |
| 3 | Excl | `0x08011bb6` |
| 4 | Random | `0x08011c46` |
| 5 | Order | `0x08011c88` |
| 6 | **Pattern** (was labeled Walk) | `0x08011cca` |
| 7 | **Order-twin, UI label unconfirmed** (was labeled Pattern) | `0x08011c88` (same as Order) |

**Resolved, 2026-09-22, by our own disassembly** (not just the external
source): `0x08011cca` is a 2-instruction trampoline into `0x0801196c`,
which calls a scale-quantizing pitch generator (`0x08013de8`) in a loop
to build bounded semi-random pitches — this is the manual's §5.3.8
"Pattern" behavior (semi-random, "optional octave movement"), not Walk's
simple 50/25/25 next/repeat/previous dice. Internal mode 7 shares its
builder with mode 5 (Order) — no randomization at all. **The `names`
table in `emulate_ks37.py` and this catalog had Walk and Pattern swapped
at the internal-mode-index level** — corrected above. This was flagged
as an open discrepancy days before 2026-09-22's hardware testing and
wasn't resolved before that testing started. **CC21-to-internal mapping
is now confirmed (2026-09-22, from the flash extract, not from a GET):**
the CC-transmit path at `0x08005a72` does `adds r1, r0, #1` then
`movs r0, #0x15` (`bl 0x08006914`) — outbound CC21 = `settings+0x55` + 1,
except when `+0x55==8` (no CC). `mode_byte_get` is a raw
`ldrb [r0,#0x55]`; `set_arp_mode` stores that byte raw to `engine+0x10`.
Panel Pattern (CC21=7) is internal 6, the semi-random builder. Panel Walk
(CC21=6) is internal 5 (Order builder + play-time walk helper
`0x08011878`). Panel Order (CC21=8) is internal 7 (Order-twin).

### How a Pattern step becomes a hold index

`play_time_step` does **not** store indices. Each step is 16 bytes
(`8 × uint16`): voice 0's first byte is a MIDI note. Unicorn
(`emulate_ks37.py play`) planted the live pitch string

`34 48 34 48 3C 34 3C 48 3C 3C 48 52 3C 3C 3C 48`

at a synthetic slot and ran `seq_step_note`; mapping those pitches onto
hold `{0x34, 0x3C, 0x48, 0x52}` reproduces

`(0, 2, 0, 2, 1, 0, 1, 2, 1, 1, 2, 3, 1, 1, 1, 2)`.

On-device bytes live at `0x0803B000+n*0x800` (not in the `.led`). A live
dump would need an existing SysEx/GET or watching MIDI — not SWD.
`+0x400` in a slot is length; `+0x403` is flags.

## Chord / note output

| Flash VA | Framed (obsolete) | Name | What | P |
|---|---|---|---|---|
| `0x0801ba9c` | `0x080185b2` | voice_interval_load | Unicorn: `r3=0x200000C8`, `r1=*(int8*)0x200000C8` (transpose), `r2=*(int8*)(voice+0x4f)` (interval), `r0` = held note | S |
| `0x0801c3ca` | (`0x08018ee0` was a mid-fn entry) | noteval | `note + interval - transpose`, octave-wrap 0–127 | S |
| `0x0801bab8` | `0x080185ce` | voice_note_on | If `voice+0x4d` nonzero, emit `0x90\|ch` with vel `+0x4e` | S |
| `0x0800f054` | | param_field_dispatch | Large setter; Type/Notes land here. `+0x44` then TBB (`subs r1,#3; cmp #0xb` at `0x0800f22c`). Writes `+0x4d/+0x4e/+0x4f` | S |
| `0x200051cc` | | voice_obj | `fp` in the voice loop | S |
| `0x200000c8` | | transpose_ram | Subtracted operand of `noteval` | S |

The voice loop is **generic poly** (`cbz` on `+0x4d`), not chord-only.
Chord ON still sets `+0x4d`; that is a usable seam.

Literal pool at `0x0801bd38` (was framed `0x0801886c`):

- `0x20001150`
- `0x200000C8` ← loaded by the interval snippet (transpose)
- `0x200010D4`
- `0x2000112C`
- `0x20001180`

## RAM

| VA | What |
|---|---|
| `0x20000000`–`0x200001f4` | `.data` (flash load `0x0801ef78`) |
| `0x20000004` | Event-handler vtable installed at `object+0x214` |
| `0x20001094` | Pointer to arp engine (mode byte at engine `+0x10`) |
| `0x20001120` | CC subscriber table |
| `0x20001170` | Pointer to settings object (Mode at `*ptr + 0x55`) |
| `0x200051cc` | Voice object (`+0x4d` active, `+0x4e` vel, `+0x4f` interval) |
| `0x20005624` | Ctor object for `vtable_init` / `vtable_assign` |
| `0x20001e3a` | Scale pitch-class mask (`ldrh`). Chromatic = `0x0FFF` |
| `0x20005f00` | Patch latch: Euclidean armed (E3+; default 0) |
| `0x20005f01` | Patch flavour: Shift+Type value (C2) |
| `0x20005f02` | `STEP_CTR_RAM` — e0b's own free-running Euclidean step counter, decoupled from the native step-position field (see below); advances only on a real (non-tie/rest) `pitch_gate_wrap` call |

## Patch page (`0x0801F400`)

| VA | Name | What |
|---|---|---|
| `0x0801F400` | euclid_wrap | Same args as `seq_step_gate` (`r0` obj, `r1` step, `r2` voice). Calls stock gate, then clears bit 7 on a Euclidean miss |
| | euclid_gate | `(step % n) * k % n < k` → 0\|1 |
| | shift_note_hook | Replaces `mov sb,r2; mov r4,r3` at `0x0801b75a`. Shift+MIDI 36/37 sets/clears `0x20005F00`. **Collision:** those keys are stock Keyboard MIDI CH (manual 1.1 §3.6.1). See `stock-shift-map.md`. |
| | noteval_then_snap | After `noteval`; snaps if Chord ON and mask ≠ chromatic |
| | type_strb_hook | Replaces `strb.w r1,[r0,#0x4f]` at Type stores `0x0800f4b8` / `0x0800f54e` / `0x0800f6fc` |

## Note-pool builder and sequence double-buffering (external source, 2026-09-22, unverified by us)

Not something we had mapped at all before this cross-check.

| VA | Name | What |
|---|---|---|
| `0x2000063c` | arp_note_pool_builder | Builds voice-0 data for the mode TBH above. Uses `0x20002dfc` (primary pool, up to 32 unique pitches + velocity, insertion order and ascending-pitch order tracked separately) and `0x20002d0c` (deferred-release pool — held notes pending release, not a physical-key ledger). Duplicate pitch does not update velocity. |
| `0x20002c4c` | seq_block_ptrs | `+0` current-block pointer, `+4` pending-block pointer. Sequence data is double-buffered, not a single live block. |
| `0x20004ed4` | play_time_step_obj | RAM object `play_time_step` (`0x08013e8c`) consumes a step through; retains actual output pitches for release. |

**Three competing update paths** (their phrasing, useful framing even
before we re-derive it ourselves): `0x08012b62 → 0x08011a1c` rebuilds
voice 0 in the *current* block in place; `0x08012bd6 → 0x08013028`
replaces the current pointer with the pending pointer; `0x0801415c`
(`seq_step_release` above) reads current-block retention metadata and
releases saved output pitches. Swing is read before rebuild/pointer
publication; length and gate are read later — a pointer swap alone can
expose mixed timing metadata mid-transition. Relevant to any future patch
that touches sequence timing, not just Pattern specifically.

## Input path (external source, 2026-09-22, unverified by us — we never mapped this)

| VA | What |
|---|---|
| `0x08010638` | USB packet decode, writes a byte ring |
| `0x0800fa64` | Main-loop MIDI parser, ≤50 bytes per invocation |
| `0x08018624` → `0x0800fd5c` | Serial (DIN) input can call this from IRQ — not all note input is main-loop work |
| `0x08010310` | Parsed MIDI path still distinguishes USB/DIN before channel filtering |
| `0x0801b750` | Common note processing; `r2=0` from physical key scanner, `r2=1` from either MIDI port |
| `0x20001ebc` | Cross-port/channel pitch tracker. Releasing a pitch from one "owner" (port/channel) can clear its slot while another owner still holds the same pitch. |
| `0x08004918` | Analog/knob process. Store new raw at `+0x5a` (`0x08004930`). AutoTest `obj+0xb9` → emit CC via `0x080060a2`+`0x080068c8`. `+0x58==0` = strip; `1..4` = Type/Notes/Vel/Strum |
| `0x08004930` | Raw control boundary (inside `0x08004918`), precedes page/routing. Other-repo `ks37_control_hook` patches this STRB |
| `0x08004bf8` | Shift-held branch of the `+0x58==0` strip: pickup/scale math, not a named panel function |
| `0x08004388` | Other strip processor. If `*(0x200010d2)` (Shift) ≠ 0, skips MIDI emit (`bne 0x08004428`) and returns — matches Shift+Mod eyes-on no-op |
| `0x0801a7ac` | Button debounce wrapper. Stable → `index_to_id` then `test20_cc_press` |
| `0x08017260` | Panel button dispatch. Reads Shift RAM; unshifted TBH `0x08017282`, shifted TBH `0x08017868` (hold/rec/stop/play/chord). Shift/oct/tap in this table are the common exit |
| `0x200010d2` | Shift-held byte. 18 load sites (Mode/TimeDiv skip-apply, strip, note emit, button TBH) |
| `0x0800d26e` / `0x0800d1f8` | Key LED writer / refresh — DMA reads a live source; no established frame-atomicity guarantee |

## Step-counter object fields, confirmed by our own disassembly — 2026-09-22

Traced directly (not from the external repo) to explain why the `e0b`
pitch-gate hook (`docs/HANDOFF.md`, findings log) produced different
rhythms on real hardware depending on which sequence slot was active.
Independently corroborates and refines the external repo's
`seq_block_ptrs`/`play_time_step_obj` framing above with exact field
offsets on the block `play_time_step` (`0x08013e8c`) operates on (the
pointer at block `+0x50`, i.e. the *content* of whichever slot
`seq_block_ptrs` currently designates current/pending):

| VA / offset | What |
|---|---|
| block `+0x38` | Live step-position counter. Both callers of `play_time_step` write this field before calling it. |
| block `+0x10` | Length field. Checked as `if step >= length-1: wrap` at the one caller (`0x08011ff0`) that increments `+0x38`. |
| `0x08013e94` | `play_time_step` spills its own incoming `r1` (the step arg) to the stack immediately — it does not compute step itself, a caller does. |
| `0x08011ff0`–`0x08012028` | Caller taking a mode flag in `r1`. `r1==0`: advances `+0x38` (wrap-checked against `+0x10`), calls `seq_step_release`, does **not** call `play_time_step`. `r1!=0`: reloads `+0x38` unincremented (clamped ≥0), calls `play_time_step` with it. |
| `0x08012e56`–`0x08012ec0` | Second caller; computes a new step value via separate logic (compared against the previous value and a signed byte at block `+0x55`, suggesting a possible fixed/held-step override), stores it to `+0x38`, calls `play_time_step`. |

**Conclusion**: the `step` value our `pitch_gate_wrap` hook feeds into
`euclid_gate(step, 8, 3)` is the native engine's real, persistent
step-position state for whichever sequence block is currently active —
bounded by that block's own length field — not an independent 0–7
counter under our control. This directly explains the hardware
hear-test results being slot-dependent (see findings log, "Root cause of
the slot-dependence, confirmed by direct disassembly"). Fix proposed
there: maintain our own free-running counter in patch RAM instead of
reusing this native value.

## USB / off-limits (flash VAs)

Search the extract for the same byte sequences if a framed number is
cited in older notes. Do not patch USB (`0x40005C00` literals), SysEx
GET, or Huaxin footers.

## Still useful, not blocking

- Which ADC/encoder path writes settings `+0x55` (the 8 detents). Closed
  from the other direction: CC21 outbound is `+0x55 + 1` at `0x08005a72`.
  `set_arp_mode` is enough of a hook without that store.
- Independently re-verify (disassembly or emulation, our own tooling)
  the highest-value external claims above before designing any new
  patch on top of them: the bit-7-is-retention correction, the
  `0x0801415c` release/look-ahead behavior, and the mode-6 discrepancy.
  Everything in this catalog marked `H (external)` or "unverified by us"
  is a claim from a separate research effort, not yet re-derived here —
  same evidentiary bar this project has always used for any relayed
  claim.
