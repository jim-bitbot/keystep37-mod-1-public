STATUS: parked
AGENT: cursor
TICKET: queue
UPDATED: 2026-09-23T21:10+01:00
INPUT: docs/two-agent-protocol.md; docs/HANDOFF.md; model/round2-tickets-proposal.md

# Ticket queue — stock 1.1.6.579 machine model

Both agents read this. **Cursor writes** scan files named below.
**Claude writes** the matching `model/<letter>-*.md` + proposed catalog.
Ownership, STATUS headers, P/S/H/X, no-commit, no-flash, no-occupancy:
unchanged from `docs/two-agent-protocol.md`.

This list **splits** old protocol D–G, **adds** L–Q, then **R–Y**, then
**Z–AJ**, then **AK–AQ** (Cursor, 2026-09-23: leftovers after Z–AJ).
Follow **this** file. No letter after BA.

## Ceiling (not 100 of the .bin)

Z–AJ target **100 / 100 of HANDOFF layers 1–6**. That is not 100 of
the `.bin`. Left on the floor on purpose:

| Out | Why |
|---|---|
| Bootloader `0x08000000`–`0x08003FFF` | Off-limits |
| USB stack body (`0x08009662`, `0x40005C00`) | Off-limits; name the ISR thunk only |
| Live flash / MCC occupancy / Euclidean rebuild | Frozen |
| `other repo/` as fact | H until re-traced |
| `findings-2026-09-20.md` rewrite | Neither agent |

Do not add tickets for those. A Z–AJ “not found” / **X** is a valid
close. 100 of the phase means every layer question is S or X, not
that every byte is named.

## How a ticket runs (same as A–C)

1. Cursor writes `scans/<letter>-*.txt`, `STATUS: done` (raw VAs + 8–20
   insns, numbered sites, no novel).
2. Claude consumes **only** that `done` scan (+ listed INPUT). Writes
   `model/<letter>-*.md` and `model/<letter>-proposed-catalog.md`.
3. Cursor copies **P/S only** into `address-catalog.md` / `recreate.py`,
   3–6 HANDOFF lines, rejected-H one-liner. Then starts the next scan.

**Parallel (do this, do not idle):**

| When | Cursor | Claude |
|---|---|---|
| Scan N is `done`, proposed N not yet | write scan N+1 | model N |
| Proposed N is `done` | catalog-copy N (+ scan N+1 if not started) | model N+1 if that scan is `done`, else stop |

Do not consume `in-progress`. Do not invent catalog names Claude has
not proposed (except scan-only `ctor_bl_*` **S** rows).

## Board (A–AJ)

| L | Name | Status | Scan | Model |
|---|---|---|---|---|
| A | boot / analog kinds | **closed** | `A-boot.txt` | `A-objects.md` |
| B | Shift-RAM 18 sites | **closed** | `B-shift-ram.txt` | `B-shift-handlers.md` |
| C | main loop / IRQs | **closed** | `C-loop-irq.txt` | `C-loop.md` |
| D | analog bus → panel knobs | **closed** | `D-analog.txt` | `D-analog.md` |
| E | keys / note in | **closed** | `E-keys.txt` | `E-keys.md` |
| F | button TBHs + leftover Shift | **closed** | `F-buttons.txt` | `F-buttons.md` |
| G | remaining ctor objects | **closed** | `G-ctors.txt` | `G-objects.md` |
| H | shared block `0x200051cc` | **closed** | `H-shared.txt` | `H-shared.md` |
| I | time / Time Div / swing / step | **closed** | `I-time.txt` | `I-time.md` |
| J | voice out USB+DIN | **closed** | `J-voice.txt` | `J-voice.md` |
| K | protocol `globalParamId` | **closed** | `K-protocol.txt` | `K-protocol.md` |
| L | seq recorder | **closed** | `L-record.txt` | `L-record.md` |
| M | chord / scale | **closed** | `M-chord.txt` | `M-chord.md` |
| N | clock / sync / Tap tempo | **closed** | `N-sync.txt` | `N-sync.md` |
| O | settings + slot persist | **closed** | `O-persist.txt` | `O-persist.md` |
| P | LED / DMA | **closed** | `P-led.txt` | `P-led.md` |
| Q | promote leftover H | **closed** | `Q-h-rows.txt` | `Q-promote.md` |
| R | USB/DIN vtable identity | **closed** | `R-usbdin.txt` | `R-usbdin.md` |
| S | leftover ctor readers | **closed** | `S-ctor-readers.txt` | `S-ctor-roles.md` |
| T | clock source select | **closed** | `T-clock-source.txt` | `T-clock.md` |
| U | SET protocol | **closed** | `U-set-protocol.txt` | `U-set.md` |
| V | persist commit | **closed** | `V-persist-commit.txt` | `V-commit.md` |
| W | LED/DMA close | **closed** | `W-led-confirm.txt` | `W-led.md` |
| X | chord/knob selector | **closed** | `X-selectors.txt` | `X-selectors.md` |
| Y | recorder rest + clear | **closed** | `Y-record-rest.txt` | `Y-record-clear.md` |
| Z | USB/DIN by Unicorn | **closed** | `Z-usbdin-emu.txt` | `Z-usbdin-emu.md` |
| AA | swing + tempo RAM | **closed** | `AA-swing-tempo.txt` | `AA-swing-tempo.md` |
| AB | Sync DIP / clock select | **closed** | `AB-sync-dip.txt` | `AB-sync-dip.md` |
| AC | analog kind → panel name | **closed** | `AC-analog-names.txt` | `AC-analog-names.md` |
| AD | key `r2` physical vs MIDI | **closed** | `AD-key-r2.txt` | `AD-key-r2.md` |
| AE | Tap + hold-length-clear | **closed** | `AE-tap-clear.txt` | `AE-tap-clear.md` |
| AF | SET without a TBB | **closed** | `AF-set-alt.txt` | `AF-set.md` |
| AG | persist one level past V | **closed** | `AG-persist-wrap.txt` | `AG-commit.md` |
| AH | `0x08010638` caller chain | **closed** | `AH-10638.txt` | `AH-usb-decode.md` |
| AI | leftover ctors + init_array | **closed** | `AI-ctors-init.txt` | `AI-objects.md` |
| AJ | leftover fields / case 5 | **closed** | `AJ-leftovers.txt` | `AJ-leftovers.md` |
| AK | emit_seq `+0x18`/`+0x1c` | **closed** | `AK-emit-seq-slots.txt` | `AK-emit-seq.md` |
| AL | callers of `0x0801509a` | **closed** | `AL-1509a.txt` | `AL-1509a.md` |
| AM | kind TBB bytes | **closed** | `AM-kind-tbb.txt` | `AM-kind-tbb.md` |
| AN | Sync `+0x3c` / `transport_cmd` | **closed** | `AN-sync-13.txt` | `AN-sync-13.md` |
| AO | swing as flash table | **closed** | `AO-swing-table.txt` | `AO-swing-table.md` |
| AP | Rec LED | **closed** | `AP-rec-led.txt` | `AP-rec-led.md` |
| AQ | G sites 08–11 | **closed** | `AQ-sites-08-11.txt` | `AQ-sites-08-11.md` |
| AR | init_array sweep targets | **closed** | `AR-init-sweeps.txt` | `AR-init-sweeps.md` |
| AS | Sync GPIO IDR | **closed** | `AS-sync-idr.txt` | `AS-sync-idr.md` |
| AT | key_scan Oct−+Oct+ | **scan done** | `AT-keyscan-oct.txt` | waiting Claude |
| AU | TIM2 → tick | **scan done** | `AU-tim2-tick.txt` | waiting Claude |
| AV | USB send callers | **scan done** | `AV-usb-caller.txt` | waiting Claude |
| AW | stores to `+0x44` | **scan done** | `AW-plus44.txt` | waiting Claude |
| AX | swing reader callers | **scan done** | `AX-swing-reader.txt` | waiting Claude |
| AY | EXTI0 vs TIM2 | **scan done** | `AY-exti0.txt` | waiting Claude |
| AZ | `0x08011ff0` path | **scan done** | `AZ-11ff0.txt` | waiting Claude |
| BA | ctor stack `+0x18`/`+0x1c` | **scan done** | `BA-ctor-slots.txt` | waiting Claude |

**Parked 2026-09-23 night.**

A–AS catalog-closed. AT/AU–BA scans `STATUS: done`; no `model/AT`–`BA` proposed files yet. No letter after BA.

Tomorrow: Claude models AT + AU–BA. Cursor catalog-copies `STATUS: done` P/S only. No new letter, no flash, no occupancy, no commit.

---

## C — main loop / IRQs

**Status:** closed 2026-09-23.

**Cursor already wrote:** `scans/C-loop-irq.txt`

**Claude writes:** `model/C-loop.md`, `model/C-proposed-catalog.md`

**Job (Claude):** Name the forever fn `0x080150d0`, inner `b` at
`0x08015912 → 0x080157c8`, Reset → `0x08016838` → that fn. Who calls
analog ×5, `strip_b`, `arp_seq_tick` ×3, `0x0800fa64` ×2, debounce ×9.
IRQ table: SysTick, USB HP/LP → `0x08009662` (`r0=0x20005888`), USART1 →
`0x0800fd5c`, TIM2. USB body is **out** — thunk + object only. DIN is
USART1, not `0x08010638` (that bl is `0x080150a4` only). Debounce RAM
matches ctor sites 24–32 — existence **S**; button names wait for F.

**Stop:** proposed P/S rows for loop fn, parser `0x0800fa64`, USART1
path, USB thunk. No USB register story.

---

## D — analog bus → panel knobs

**Cursor:** `scans/D-analog.txt`
Disassemble `analog_knob_process` `0x08004918` TBH on `+0x58` kinds 0–4.
20 insns per kind + store sites (`+0x5a` raw). `strip_process_b`
`0x08004388` and Shift skip `bne 0x08004428`. Kind-0 vs `strip_b`
`0x2000039c`. Immediates that match `knob_index_to_cc` `0x62`–`0x66`.
Ctor objects: `0x20000468` / `121c` / `1294` / `130c` / `1384`.

**Claude:** `model/D-analog.md` + proposed.
Map kinds 0–4 onto Type / Notes / Vel / Strum / Rate (or say unknown).
Shift+Mod no-op is `strip_b` skip — confirm or reject from this scan,
not from occupancy prose.

**Gate:** C scan done (already). Catalog C may lag; D scan does not need
C-proposed.

**Stop:** each analog object has a panel name or an explicit unknown.

---

## E — keys / note in

**Cursor:** `scans/E-keys.txt`
Fn `0x0801b750`. Every static caller (C already: `0x0800cdfa`,
`0x0800cf30`, `0x0800d064`, `0x08010326`). 20 insns at entry: `r2=0`
vs `r2=1`. Path from physical scan vs MIDI parser into this fn. Do not
walk `noteval` (that is J).

**Claude:** `model/E-keys.md` + proposed.
One diagram: key scan / USB parse / DIN parse → `0x0801b750`. Tag H
anything not in the scan.

**Gate:** D scan may run in parallel with C-model; E scan may run in
parallel with D-model.

**Stop:** callers named, `r2` meaning S or still H.

---

## F — button TBHs + leftover Shift

**Cursor:** `scans/F-buttons.txt`
`panel_button_dispatch` `0x08017260`: unshifted TBH `0x08017282`,
shifted `0x08017868`. Decode **table bytes** (not as `lsls`). Compact
index 0–7 vs `id_to_index`. Re-dump B sites **05, 06, 08, 15, 16**
(`0x0800cd62`, `0x0800cfd8`, `0x08016afc`, `0x0801a078`, `0x0801a11a`)
and shifted cases 11/12 (`0x08017cac`, `0x08017cf0`) with enough body
to see which compact ID.

**Claude:** `model/F-buttons.md` + proposed.
Every compact ID → stock handler. Close B unknowns or leave
“unknown stock secondary”. Gesture names for Mode/TimeDiv skip-apply
become S only if this scan shows the ID.

**Gate:** B catalog closed (already). Better after D so analog IDs are
not confused with buttons.

**Stop:** 8 compact IDs have a row; leftover Shift sites are S, X, or
still unknown.

---

## G — remaining ctor objects

**Cursor:** `scans/G-ctors.txt`
From `A-boot.txt` sites **01–53 minus already-named** (analog 14,19–22;
strip 18; pools 37,39,42–44). For each leftover: dest prologue 12–20
insns, `r0` RAM, first `str`/`strb` offsets. Number them with the A
site index. Debounce ctor `0x08019f8c` sites 24–32: now have loop
readers — dump `+0xd` tag only, do not re-reject without the new
reader fact.

**Claude:** `model/G-objects.md` + proposed.
Object table continuation of A. Existence **S**. Role **H** unless a
later ticket already named it. Propose `recreate.py` names only for
function **starts**.

**Gate:** A closed. F not required, but debounce names are cleaner after F.

**Stop:** every ctor site has RAM base + ctor VA in the proposed table.

---

## H — shared block `0x200051cc`

**Cursor:** `scans/H-shared.txt`
Every pc-rel load of `0x200051cc` (same method as B). Number 1…N. 12
insns. List unique offsets (`+0x4d/+0x4e/+0x4f/+0xb9/+0x59/+0x49/+0x5c`
already seen — find the rest).

**Claude:** `model/H-shared.md` + proposed.
Field table. Propose rename off `voice_obj` if the scan shows it.
Do not call it “the voice object”.

**Gate:** C + F help (who writes `+0xb9`, `+0x49`). Can start after G
scan if those are `done`.

**Stop:** offset table covering all load sites in the scan.

---

## I — time

**Cursor:** `scans/I-time.txt`
`arp_seq_tick` `0x080129cc`: who loads Time Div / swing / length.
Block `+0x38` step, `+0x10` length, `+0x55` (catalog). TIM2 IRQ
`0x08018584` and SysTick `0x08018200` — 16 insns each, whether they
touch the tick object `0x20002bec`. `timediv_skip_apply` object
`0x20001000`. No Euclidean.

**Claude:** `model/I-time.md` + proposed.
One diagram: clock source → tick → current step. Internal vs MIDI
clock is **N**; here only “what advances step”.

**Gate:** C scan (tick called from loop). Better after H if tick uses
the shared block.

**Stop:** step, length, Time Div RAM, swing RAM each have a row or
explicit missing.

---

## J — voice out

**Cursor:** `scans/J-voice.txt`
`play_time_step` `0x08013e8c` → `pitch_gate_check` `0x08013ebc` →
`seq_step_note` / `seq_step_gate` / `seq_step_release` →
`voice_interval_load` `0x0801ba9c` → `noteval` `0x0801c3ca` →
`voice_note_on` `0x0801bab8`. Then **who emits** USB vs DIN (bl after
Note-On; USART vs USB object). Architecture, not hook targets.

**Claude:** `model/J-voice.md` + proposed.
Cell → pitch/vel/tie → Note-On/Off → port. Bit 7 = retention is
already S; do not reopen unless the scan contradicts.

**Gate:** E (note in) + I (step). Parallel with K is wrong — K sits on J.

**Stop:** USB and DIN emit VAs named or marked missing.

---

## K — protocol overlay

**Cursor:** `scans/K-protocol.txt`
`get_param` `0x08005e84`: TBB/`cmp` on `globalParamId`. SET counterpart
(search `bl` to `get_param`, sibling setter). `chord_test_dispatch`
`0x08005df8` id `0x69`. Immediates that match occupancy control IDs
(§10 `stock-shift-map.md`) — list them, do not re-run occupancy.

**Claude:** `model/K-protocol.md` + proposed.
GET/SET table on top of D–J. Occupancy CCs are firmware IDs, not MIDI
map. **P** only if immediate matches a known ID; else S/H.

**Gate:** D, F, I, J `done` (proposed). Scan can start once those scans
exist; model should wait for those models.

**Stop:** param IDs used by Mode / Time Div / Type / Notes / keys have
rows. Full 256-wide table not required.

---

## L — seq recorder

**Cursor:** `scans/L-record.txt`
`seq_step_store` `0x08014418` and ctor `0x08014416` (2-byte gap — fix
entry or X). Only static `bl` catalogued from `0x080065e4` — dump that
caller. Rec compact ID path from F. Chord-then-Rec is occupancy fact
**P**; find the Rec LED write.

**Claude:** `model/L-record.md` + proposed.
Record vs play vs hold-length-clear (Seq Shift+both Oct) if it appears
in this scan; else leave to F leftovers.

**Gate:** F + J.

**Stop:** store entry VA confirmed; Rec handler named or unknown.

---

## M — chord / scale

**Cursor:** `scans/M-chord.txt`
`param_field_dispatch` `0x0800f054` Type/Notes stores `+0x4d/+0x4e/+0x4f`.
Scale mask `0x20001e3a`. Chord ON test. Do not write `noteval_then_snap`
patch notes.

**Claude:** `model/M-chord.md` + proposed.
Stock chord/scale only. Interval table if present.

**Gate:** J + K help. Can scan after J scan.

**Stop:** chord enable field + scale mask reader named.

---

## N — clock / sync / Tap tempo

**Cursor:** `scans/N-sync.txt`
MIDI clock / start / stop bytes inside or under `0x0800fa64` (imm
`0xF8`/`0xFA`/`0xFC`). DIN clock vs USB. Tap: Shift+Tap is occupancy
**P** (tempo); find the handler from F compact Tap. Internal tempo
RAM if obvious.

**Claude:** `model/N-sync.md` + proposed.
Extends I with source selection. Tap = tempo, not a hole.

**Gate:** I + F. Parser from C.

**Stop:** clock source enum or “not found”. Tap handler S or unknown.

---

## O — settings + slot persist

**Cursor:** `scans/O-persist.txt`
`seq_slot_base` `0x0800dd30` / `0x0803B000 + n*0x800`. Who writes slot
flash (FLASH IRQ4 `0x080186d4` only as entry; do not reverse ST libs).
Settings object `*0x20001170`. GET of length/swing/gate at slot `+0x400`
— re-derive or leave H.

**Claude:** `model/O-persist.md` + proposed.
What survives power-cycle vs RAM. Slot header fields S only if this
scan reads them.

**Gate:** I + L + K.

**Stop:** slot base + settings ptr have store paths or explicit missing.

---

## P — LED / DMA

**Cursor:** `scans/P-led.txt`
Writers `0x0800d26e` / `0x0800d1f8` (catalog input-path; re-dump).
DMA1_CH1/2/3 IRQs from C vector (`0x080185e8`, `0x08018a40`,
`0x080186c4`). 16 insns. What buffer they read. No frame-atomicity
novel.

**Claude:** `model/P-led.md` + proposed.
Key LEDs vs other LEDs if the scan splits them. Rec LED from L if
not already named.

**Gate:** C vector + F (which button lights).

**Stop:** DMA source RAM + LED writer named.

---

## Q — promote leftover H

**Cursor:** `scans/Q-h-rows.txt`
Grep catalog for **H** and “unverified”. For each: 8–12 insns at the
cited VA, or `X` if wrong function start (`unaff_r*` / mid-fn).

**Claude:** `model/Q-promote.md` + proposed.
Every leftover H → S, X, or keep H with one-line reason. No new
islands. No `other repo/` promotions without this scan.

**Gate:** all of C–P catalog-copied (or explicitly skipped with Jim’s
say-so).

**Stop:** catalog has no drive-by H from tickets A–P. Remaining H is
labelled on purpose.

---

## R — USB/DIN vtable identity

**Cursor:** `scans/R-usbdin.txt`
Ctor `0x0801b572` stores incoming `r1` to `0x20001eb8+0`. Find that
`r1` source (ctor-sweep or other static write). Dump that source
object’s ctor. `port_switch` `0x0801b384` prologue. Key-path `r0`
through `0x0801b996` (`r6`). USART1 `0x40013800` and USB `0x40005C00`
literals within two `bl`s of `0x0801ad20` / `0x0801ae56`. Do **not**
walk `usb_isr_common` `0x08009662` or the USB stack body.

**Claude:** `model/R-usbdin.md` + proposed.
Close or fail to close which vtable slot is USB vs DIN.

**Gate:** none (A–Q closed).

**Stop:** a peripheral literal is reachable from the slots, or
explicitly not reachable by static means.

---

## S — leftover ctor readers

**Cursor:** `scans/S-ctor-readers.txt`
For each G row still tagged H-role (sites 01–03, 05–13, 17, 23, 34–36,
41, 45–53; RAM list in `model/G-objects.md`), whole-image pc-rel or
`bl` to that RAM outside its ctor. 10 insns per reader. Skip sites
already S-role (04, 15, 16, 33, 40, 24–32, 38).

**Claude:** `model/S-ctor-roles.md` + proposed.
Role S only when a reader plus behavior is unambiguous.

**Gate:** none.

**Stop:** every listed object has a reader or an explicit “no reader
found.”

---

## T — clock source select

**Cursor:** `scans/T-clock-source.txt`
INPUT includes `scans/N-05534.txt` (14 pc-rel loads of `0x20005534`,
init `0x080186e8`, leaves `0x0800b0c6` / `0x0800b0ae` / `0x0800b2ae`).
Do not re-list those 14 sites. Add: every **store** to the object
(not through the TIM2 pointer), full remaining bodies of the two
leaves if N cut them, any `#0x13` immediate near those windows
(Sync DIP). Arbitration flag if present.

**Claude:** `model/T-clock.md` + proposed.

**Gate:** none.

**Stop:** source-select named, or explicit “no arbitration in these
callees.”

---

## U — SET protocol counterpart

**Cursor:** `scans/U-set-protocol.txt`
Second TBB/switch shaped like `0x0800ee92` (signed byte from a buffer).
Write-path branches in `get_param` `0x08005e84`, `get_param_b`
`0x0800614c`, `get_param_c` `0x080060c4` if any.

**Claude:** `model/U-set.md` + proposed.

**Gate:** K closed (true).

**Stop:** SET entry named, or not found in a stated scope.

---

## V — persist commit (application only)

**Cursor:** `scans/V-persist-commit.txt`
`0x080186d4` is FLASH IRQ4 (vector). Expect no static `bl`. Walk
`seq_slot_base` callers `0x0800de16`, `0x0800de96`, `0x0800e21a`
(10+ insns). Do not reverse `0x08008140` or deeper ST HAL.

**Claude:** `model/V-commit.md` + proposed.

**Gate:** O closed (true).

**Stop:** commit trigger named, or not found at the application
boundary.

---

## W — LED/DMA close

**Cursor:** `scans/W-led-confirm.txt`
Bodies of `0x080045b6` and `0x08004566`. Do they reach `led_write`
`0x0800d26e` or `led_refresh` `0x0800d1f8`? Rec-press `0x0801780c`
notify chain vs the 33 `led_write` callers.

**Claude:** `model/W-led.md` + proposed.

**Gate:** P + L closed (true).

**Stop:** DMA1_CH1 LED role confirmed or ruled out; Rec LED found or
exhausted in that caller set.

---

## X — chord/knob family + leftover button cases

**Cursor:** `scans/X-selectors.txt`
Callers of `param_field_dispatch` `0x0800f054`. What sets `+0x3c`.
Bank selector (candidate `+0x15`). Full unshifted Hold/Stop/Play:
`0x08017834` / `0x08017298` / `0x0801743e` (F cut these short).

**Claude:** `model/X-selectors.md` + proposed.

**Gate:** F + M closed (true).

**Stop:** family selector named or explicit H; Hold/Stop/Play bodies
shown.

---

## Y — recorder rest + hold-length-clear

**Cursor:** `scans/Y-record-rest.txt`
`seq_step_store` TBB cases 3/5/6 at `0x0801446a`, `0x08014494`,
`0x080144c2` (20 insns). B/F sites 15/16 (`0x0801a078`, `0x0801a11a`)
and other loads of `0x200010d0` / `0x200010d6`. Also dump `0x08016ac0`
(Q: site 08 at `0x08016afc` is the next function after a `pop`).

**Claude:** `model/Y-record-clear.md` + proposed.

**Gate:** L + F closed (true).

**Stop:** case 3 named; hold-length-clear mapped or still unmapped.

---

## Z — USB/DIN by Unicorn

Layer 5. R closed static search: slots on `0x20001d60` have no
USART1/USB literal.

**Cursor:** `scans/Z-usbdin-emu.txt`
Hook `port_emit_key` `0x0801ad20` and `port_emit_seq` `0x0801ae56`
`blx` slots (`+4/+0x14/+0xc`). Existing Unicorn harness only
(`emulate_ks37.py` or equivalent). Watch whether the callee writes
`0x200055e4` / USART1 `0x40013800` or the USB object `0x20005888`.
Do **not** walk `usb_isr_common` `0x08009662` or the USB stack body.
No live flash.

**Claude:** `model/Z-usbdin-emu.md` + proposed.
Name which slot is DIN and which is USB, or **X** “not recoverable
without hardware.”

**Gate:** R closed (true).

**Stop:** slots labelled, or Unicorn cannot reach the `blx` (state
that; do not invent another static ticket).

---

## AA — swing + tempo RAM

Layer 4. I/N/T: swing and internal tempo not found.

**Cursor:** `scans/AA-swing-tempo.txt`
Every store to tick object `0x20002bec+0x10` (length) and any byte
that is not `+0x38/+0x10/+0x55`. Slot header `+0x401` (external
Swing name — keep **H** until a reader is this ticket). Search
`cmp`/`strb` of the occupancy swing values (52, 54, 57, 60, 63, 67,
71, 75) and Tap-adjacent RAM. Internal tempo: who writes TIM2 ARR
`[0x20005534]+0x2c` besides `0x08012084`.

**Claude:** `model/AA-swing-tempo.md` + proposed.

**Gate:** I + T closed (true).

**Stop:** swing RAM and tempo writer named, or each is **X** not in
the searched windows.

---

## AB — Sync DIP / clock select

Layer 4. T: no `#0x13` in the timer leaves.

**Cursor:** `scans/AB-sync-dip.txt`
Immediates `#0x13` / `#19` in the app (control ID Sync). GPIO reads
that gate `0x20005534` / `0x0800b0c6` / `0x0800b2ae` / `transport_cmd`.
Rear-panel Sync if it is a GPIO and not a RAM flag: say so.

**Claude:** `model/AB-sync-dip.md` + proposed.

**Gate:** T + N closed (true).

**Stop:** source-select named, or **X** “GPIO / not in these
windows.”

---

## AC — analog kind → panel name

Layer 3. D: no `0x62`–`0x66` in the kind windows.

**Cursor:** `scans/AC-analog-names.txt`
Callers of `knob_index_to_cc` `0x080060a2` and `test20_cc_value`
`0x080068c8`. Which analog object (`0x2000121c` / `1294` / `130c` /
`1384` / kind 0) feeds which ID. Site 17 `0x2000058c` (Rate
candidate) in the same call pattern.

**Claude:** `model/AC-analog-names.md` + proposed.
P only if an immediate matches occupancy. Else S structure + **X**
on firmware panel names (occupancy remains the name).

**Gate:** D + S closed (true).

**Stop:** five kinds named or explicitly unnamed in firmware.

---

## AD — key `r2` physical vs MIDI

Layer 3. E: four callers; `r2=0` vs `r2=1` still **H**.

**Cursor:** `scans/AD-key-r2.txt`
20 insns before each `bl 0x0801b750`. What `r2` selects inside
`0x0801b750` (first read of `sb` at `0x0801b8b2` and later). If
static still cannot tell physical vs MIDI, one Unicorn run of a
key-scan caller vs `0x08010326`.

**Claude:** `model/AD-key-r2.md` + proposed.

**Gate:** E closed (true).

**Stop:** `r2` meaning S or **X** “not physical/MIDI.”

---

## AE — Tap + hold-length-clear

Layer 3. F: compact 4 is a pop in all three TBHs. Y: combo bytes
are not hold-length-clear.

**Cursor:** `scans/AE-tap-clear.txt`
Every `#0x67` besides `id_to_index` / `index_to_id`. Shift+Tap
occupancy (tempo) if a second path exists. Shift+Oct−+Oct+:
search both Oct compact indexes (2 and 3) held together, and any
`bl` to `seq_step_store` or a length-preserving clear.

**Claude:** `model/AE-tap-clear.md` + proposed.

**Gate:** F + Y closed (true).

**Stop:** each gesture mapped or **X** unmapped after this search.

---

## AF — SET without a TBB

Layer 6. U: no SET TBB; `0x0800ef38` is a pre-check.

**Cursor:** `scans/AF-set-alt.txt`
`param_field_dispatch` `0x0800f054` write path (already two
callers in X). SysEx / MCC write that is not a TBB (search
`strb` after `get_param` family). Do not walk USB stack.

**Claude:** `model/AF-set.md` + proposed.
SET entry, or **X** “writes are the panel/knob paths already
mapped.”

**Gate:** U + X closed (true).

**Stop:** SET named or ruled not a separate wire path.

---

## AG — persist one level past V

Layer 5 / persist. V stopped before `0x0800ddf6`, `0x08008290`,
`0x08008338`.

**Cursor:** `scans/AG-persist-wrap.txt`
Prologue + 16 insns of those three only. If a function is ST HAL
(`0x40022000` FLASH) stop at the first peripheral store and tag
**X** (do not reverse the HAL). Stay application-side: who calls
`0x0800de90` / `0x0800de10` / the `0x0800e21a` container.

**Claude:** `model/AG-commit.md` + proposed.

**Gate:** V closed (true).

**Stop:** commit trigger named, or **X** “only HAL beyond this
line.”

---

## AH — `0x08010638` caller chain

Layer 2. C: only static caller `0x080150a4`; that start was never
found.

**Cursor:** `scans/AH-10638.txt`
Walk back from `0x080150a4` to the real push. Every `bl` to
`0x08010638` including table pointers (Thumb `|1`). 12 insns at
the containing start. Do not walk USB registers.

**Claude:** `model/AH-usb-decode.md` + proposed.

**Gate:** C closed (true).

**Stop:** containing function named or **X** still no start.

---

## AI — leftover ctors + init_array

Layer 1. S left sites 01, 05–13, 23, 34–36, 41, 46–48, 50, 52–53
without a role row. A: init_array slots 1/2/3/5 not walked.

**Cursor:** `scans/AI-ctors-init.txt`
The five Thumb pointers at `0x0801ef58`–`0x0801ef6c`. One reader
window (10 insns) per still-H-role RAM from S’s “not proposed”
list. Rate `0x2000058c` if AC did not already close it.

**Claude:** `model/AI-objects.md` + proposed.
Every leftover object: role S or explicit no-role **X**.

**Gate:** A + S closed (true).

**Stop:** init_array walked; leftover G sites each S or X.

---

## AJ — leftover fields / case 5

Layers 3–5. M: `+0x50` role H; family `0x08–0x0e` vs `0x16–0x1b`
unconfirmed. Y: store case 5 unwalked. I: `#8` Time Div compares
are now in `I-time.txt` and were never remodeled.

**Cursor:** `scans/AJ-leftovers.txt`
Readers of `0x200051cc+0x50`. Case 5 `0x08014494` (20 insns; Y
already has a dump — re-read, add callers). Time Div `#8` at
`0x08005ae8` / `0x08005af0` (I rewrite). Family selector only if
a new immediate appears; do not guess.

**Claude:** `model/AJ-leftovers.md` + proposed.

**Gate:** M + Y + I closed (true).

**Stop:** each leftover is S or kept H with one line. No new
islands.

---

## AK — emit_seq `+0x18`/`+0x1c`

Layer 5. Z: those slots are not in the `0x0801acb0` six-word copy.

**Cursor:** `scans/AK-emit-seq-slots.txt`
Every store to `+0x18` / `+0x1c` after a pc-rel of `0x20001d60` /
`0x20001e04` / `0x20001eb8`. Also `str` of a Thumb address into those
offsets. Do not invent a callee if the store is missing.

**Claude:** `model/AK-emit-seq.md` + proposed.

**Gate:** Z closed (true).

**Stop:** writer named, or **X** not stored by the traced objects.

---

## AL — callers of `0x0801509a`

Layer 2. AH: containing start found; no `bl` / Thumb ptr in that scan.

**Cursor:** `scans/AL-1509a.txt`
`bl` to `0x0801509a`, word `0x0801509b`, and any `blx` table that
holds that Thumb ptr. 12 insns at each site. Do not walk USB
registers.

**Claude:** `model/AL-ring-callers.md` + proposed.

**Gate:** AH closed (true).

**Stop:** a caller, or **X** no static caller.

---

## AM — kind TBB bytes

Layer 3. AC: kind 0 / `≥5` → CC `0x66`. Kind 1–4 table not decoded.

**Cursor:** `scans/AM-kind-tbb.txt`
Raw 4 bytes at `0x080060ac` (TBB after `0x080060a8`). Case targets.
`subs r0,#1` so incoming kind 1 = table index 0. No occupancy names
unless the immediate is in the case body (already `0x62`–`0x65`).

**Claude:** `model/AM-kind-cc.md` + proposed.

**Gate:** AC closed (true).

**Stop:** four kind→CC rows or **X** table unreadable.

---

## AN — Sync `#0x13` on `+0x3c` + real `transport_cmd`

Layer 4. AB dump labelled `0x0800fa64` as `transport_cmd` — that is
wrong. Catalog `transport_cmd` is `0x08012334`.

**Cursor:** `scans/AN-sync-13.txt`
`0x0800f32a` window (stores `#0x13` to `+0x3c`). Readers of that
`+0x3c` that `cmp #0x13`. Body of `0x08012334` (20 insns) and any
GPIO literal in that function only. Do not re-list every `#0x13`.

**Claude:** `model/AN-sync.md` + proposed.

**Gate:** T + AB scan exist.

**Stop:** source-select named, or **X** GPIO / not in these windows.

---

## AO — swing as a flash table

Layer 4. AA: occupancy immediates were offset noise. `+0x401` stores
exist; no swing role shown.

**Cursor:** `scans/AO-swing-table.txt`
Search the app for the byte run `34 36 39 3c 3f 43 47 4b` (occupancy
swing percents). Readers of slot `+0x401` that then use the loaded
byte (index / cmp / table). 12 insns each. Name stays **H** unless
this scan ties the value to time.

**Claude:** `model/AO-swing.md` + proposed.

**Gate:** AA closed (true).

**Stop:** swing RAM or table named, or **X** not in the image.

---

## AP — Rec LED

Layer 5. W: Rec LED not in Rec-press or the 33 `led_write` callers.

**Cursor:** `scans/AP-rec-led.txt`
Unshifted Rec `0x0801780c` notify chain one more hop. Any
`led_write` / `led_refresh` from that chain. If none, **X** and stop.
Do not invent a new LED writer.

**Claude:** `model/AP-rec-led.md` + proposed.

**Gate:** W + L closed (true).

**Stop:** Rec LED named or **X**.

---

## AQ — G sites 08–11

Layer 1. AI skipped these four.

**Cursor:** `scans/AQ-sites-08-11.txt`
RAM `0x20002cdc` / `0x20002cf8` / `0x20002dbc` / `0x20002e80`. One
outside-ctor reader window (10 insns) each.

**Claude:** `model/AQ-objects.md` + proposed.

**Gate:** S + AI scan exist.

**Stop:** each site S or explicit no-reader **X**.

---

## AR — init_array wrapper targets

Layer 1. AI: slots 2/3/5 are the same gate as `ctor_sweep_wrapper_live`.
Claude asked these three opened.

**Cursor:** `scans/AR-init-sweeps.txt`
Bodies of `0x08005da8`, `0x08010f40`, `0x08015f74`. Every `bl` and
pc-rel RAM. Stop at HAL / USB.

**Claude:** `model/AR-sweeps.md` + proposed.

**Gate:** AI closed (true).

**Stop:** each target is a sweep or a small init, named or **X** role.

---

## AS — Sync GPIO IDR

Layer 4. AB proposed: no row; asked for IDR `+0x08` plus a single-bit
test, not another `#0x13` sweep.

**Cursor:** `scans/AS-sync-idr.txt`
GPIO-base pc-rel then `ldr [reg,#8]`. HAL IDR helpers. Callers near
boot / `transport_cmd` / TIM2. Stop at USB stack.

**Claude:** `model/AS-sync-idr.md` + proposed.

**Gate:** AB closed (true).

**Stop:** pin/object named or method **X**.

---

## AT — key_scan Oct−+Oct+

Layer 3. AE: hold-length-clear not in Shift-RAM / button TBH.
Asked for `key_scan` `0x0800cc48` own body.

**Cursor:** `scans/AT-keyscan-oct.txt`
Every `cmp` and `bl` in `0x0800cc48`–`0x0800d112`. Compact index
2-and-3, or **X**. One level of unique helpers only.

**Claude:** `model/AT-keyscan-oct.md` + proposed.

**Gate:** AE closed (true).

**Stop:** gesture found or fourth **X**.

---

## AU — TIM2 → tick

Layer 4. TIM2_IRQ calls `0x0800b2ae(0x20005534)` then
`0x08011ee4(*0x20001098)`. Tick object is `0x20002bec`. Does this
path store `+0x38` or `bl arp_seq_tick`?

**Cursor:** `scans/AU-tim2-tick.txt`
Bodies of `0x08018584`, `0x0800b2ae`, `0x08011ee4`. Every `bl` and
pc-rel. Stop at USB / HAL.

**Claude:** `model/AU-tim2-tick.md` + proposed.

**Gate:** N + I closed (true).

**Stop:** link named or explicit no-touch **X**.

---

## AV — USB send callers

Layer 5. `0x08010e46` is mid-fn USB send. Who calls that site /
containing fn? Do **not** walk `0x080091ca`.

**Cursor:** `scans/AV-usb-caller.txt`
`bl` and Thumb-ptr to the containing function start and to
`0x08010e46`. 12 insns at each caller.

**Claude:** `model/AV-usb-caller.md` + proposed.

**Gate:** Z closed (true).

**Stop:** caller found or static **X**.

---

## AW — stores to `0x200051cc+0x44`

Layer 4. Boot default is `3` (AR). 19 loads. Who writes it?

**Cursor:** `scans/AW-plus44.txt`
Tracked-reg stores to `+0x44` after a `0x200051cc` load. Dump each
writer window.

**Claude:** `model/AW-plus44.md` + proposed.

**Gate:** AR + H closed (true).

**Stop:** writers S or none **X**.

---

## AX — swing reader callers

Layer 4. Table `0x0801ec64`, reader `0x08016f80` indexes `r1-0x15`.

**Cursor:** `scans/AX-swing-reader.txt`
Every `bl` to the containing fn of `0x08016f80`. What is `r1` at
each site. Dest of `0x0801312e`.

**Claude:** `model/AX-swing.md` + proposed.

**Gate:** AO scan exists.

**Stop:** r1 / dest named or **X**.

---

## AY — EXTI0 vs TIM2

Layer 4. Catalog: EXTI0 touches `tim2_wrapper`. Analog clock pulse?

**Cursor:** `scans/AY-exti0.txt`
EXTI0 vector target. Every `bl` and pc-rel of `0x20005534` /
`0x20001128` / `0x200051cc`. Stop at USB.

**Claude:** `model/AY-exti0.md` + proposed.

**Gate:** N closed (true).

**Stop:** pulse path S or **X**.

---

## AZ — `0x08011ff0`

Layer 4/5. Second `play_time_step` feeder. `r1==0` advances step;
`r1!=0` plays. Who calls it?

**Cursor:** `scans/AZ-11ff0.txt`
Full body + every static caller. pc-rel RAM.

**Claude:** `model/AZ-11ff0.md` + proposed.

**Gate:** I + J closed (true).

**Stop:** callers S.

---

## BA — ctor stack for emit_seq slots

Layer 5. AK: eight-word copy. What the sweep puts on `sp+0x24` /
`sp+0x28` at `0x0801acb0`.

**Cursor:** `scans/BA-ctor-slots.txt`
Ctor-sweep window that `bl`s `0x0801acb0`. Stack stores before
that `bl`.

**Claude:** `model/BA-ctor-slots.md` + proposed.

**Gate:** AK closed (true).

**Stop:** two words identified or **X**.

---

## Copy-paste when resuming

**To Claude, next:**
Parked 2026-09-23. AT + AU–BA scans `STATUS: done`. Write `model/<letter>-*.md` + proposed catalogs. Do not edit scans/, catalog, HANDOFF, or `recreate.py`.

**To Cursor, next:**
Catalog-copy every `STATUS: done` proposed file not yet copied (P/S only; function starts only in `recreate.py`). No letter after BA. No flash, occupancy, commit.
