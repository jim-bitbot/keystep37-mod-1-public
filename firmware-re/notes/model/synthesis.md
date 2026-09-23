STATUS: done
AGENT: claude
TICKET: synthesis (not a lettered ticket — current-state map per HANDOFF.md's stated deliverable)
UPDATED: 2026-09-24T02:00+01:00 (Round 5 — tickets AK-AS all closed)
INPUT: firmware-re/notes/model/A-objects.md through AQ-sites-08-11.md
(all closed tickets to date, A-Y, Z, AA-AQ)

## Round 5 (AK-AS) headlines

- **AS**: strongest clock-source lead yet — a 4-pin GPIOD object, read
  via real IDR bit tests, directly gates both TIM2-disable and
  MIDI-Start transport actions. Explains why T found no arbitration
  flag: it lives on a separate object, not the TIM2 wrapper itself.
  Mechanism confirmed; physical pin identity (Sync DIP vs jack) stays H.
- **AO**: found the swing value table — 9 flash bytes matching
  `stock-shift-map.md`'s documented Swing panel values exactly
  (50/52/54/57/60/63/67/71/75). Narrows "swing: not found" to one
  unwalked function (`0x801312e`).
- **AM**: fully decoded `knob_index_to_cc`'s TBB table, arithmetic-
  verified — confirms the analog kind ordering (Type/Notes/Vel/Strum)
  exactly as originally assumed, closing AC's open item.
- **AR**: opened the 3 sweeps AI flagged — corrects my own overstated
  framing (not more `ctor_sweep`-scale tables), but one target turned
  out to be `0x200051cc`'s own field initializer, closing a long-opaque
  "what are the defaults" question for that shared block.
- **AK**: caught my own error — `R-usbdin.md`'s "6-word ctor" was
  actually 8 words; `Z-usbdin-emu.md`'s "unpopulated slot" finding is
  retracted, both files corrected.
- **AN/AP**: reinforce AB's Sync-DIP negative and the Rec-LED negative
  (4th confirmation) from new angles; both surface a shared object
  family / a repeated CLZ-bitmask idiom respectively.
- **AL, AQ**: honest negatives and existence-only findings, no
  corrections needed.

## Round 4 (Z, AA-AJ) headlines

- **Z**: USB/DIN closed by reframing — `emit_key`'s `+4` slot is
  confirmed DIN (real MMIO on USART1 CR1). USB was never one of the
  vtable slots at all; it's a separate entry point (`0x08010e46`),
  never reached from the mechanism this project called "the port
  switch" since ticket J.
- **AA**: internal tempo RAM closed — tick object `+0xe`, full chain to
  TIM2's real ARR register, verified against the STM32F1 timer map.
  Swing stays unfound, now a stronger negative.
- **AG**: persistence commit path closed — `0x08008290` is the real
  STM32 FLASH_KEYR unlock sequence, verified against the documented
  key pair. Corrects `V-commit.md`'s implicit direction assumption on
  `0x0800ddf6` (it's a load, not a save).
- **AI**: found 3 more `init_array` slots shaped exactly like
  `ctor_sweep` — unopened, likely the single biggest unexplored area
  left in the binary.
- **AC**: kind-0/strip's AutoTest path maps to Rate's own CC, not
  Pitch/Mod as might be assumed — closes a real gap, though the
  kind-1-4 ordering needs proper TBB table decode to fully close.
- **AD**: reframes the key `r2` "physical vs MIDI" claim — it's a
  shift-amount into a one-hot bitmask, not a boolean branch, tying
  directly into the `lead-usb-din.md` pitch-tracker finding.
- **AH**: closed `0x080150a4`'s containing function (`0x0801509a`).
- **AB, AE, AF**: honest negatives — Sync DIP GPIO read not isolated,
  hold-length-clear still unmapped after a third independent pass, SET
  protocol confirmed absent by a second search method.
- **AJ**: sharpened M's `+0x50` caveat into a real negative; reconfirmed
  Y and the corrected `I-time.md` independently.

# Synthesis — current-state map, HANDOFF's six layers

Not a scan-derived ticket. This is a read-only consolidation of the
model files closed so far (A-Q), organized by `docs/HANDOFF.md`'s own
six-layer breakdown, so the state of the model doesn't only exist as
separate files. No new claims — every line below cites the ticket that
established it.

**Addendum since the original A-P version (Q + two side threads):**

- **Ticket Q** closed two real `recreate.py` corrections (`0x08011c88`
  `pattern_or_order_builder` and `0x08004bf8` `shift_strip_pickup` are
  both case-body labels, not function starts — flagged as requests, not
  edited), one containing-function correction (`0x08016afc` is its own
  start, not "inside `0x08016ac0`" as B/F assumed), and confirmed
  `0x08013028` = `current_ptr = pending_ptr` for the seq-block
  double-buffer swap (promotes an old external-source claim to S). Full
  detail: `model/Q-promote.md`.
- **`lead-usb-din.md`** (my own capstone spot-check, not a Cursor scan
  — do not catalog-copy from it directly) found that
  `0x20001eb8+4 = 0x20001ebc` exactly, matching the existing catalog's
  long-unverified "cross-port/channel pitch tracker" row — now
  independently confirmed as a real 128-entry (per-MIDI-note) table,
  one of three such tables on that object. The original USB/DIN
  question turned out to live in a *different* field (`+0`, a vtable
  pointer) on the same object — not fully resolved, reframed as
  ticket R in `round2-tickets-proposal.md`.
- **`scans/N-05534.txt`** (Cursor, already covers most of proposed
  ticket T) shows `0x20005534` is a real TIM2 hardware-register wrapper
  object (`+0` = TIM2 peripheral base `0x40000000`, `+4`/`+0xc`/`+0x10`
  = ARR/CCMR-shaped config, leaf functions touch DIER/CR1/CNT/SR
  directly) — and that **five different call sites** touch it: the MIDI
  realtime-byte dispatcher, EXTI0, `transport_cmd` (`0x08012334`, from
  N), and TIM2's own IRQ. A sibling object `0x200054bc` exists and is
  used by TIM4_IRQ specifically, not this one. Strongly suggests TIM2
  is the actual internal-clock hardware timer, started/stopped/reset by
  whichever source (external MIDI clock, an external analog pulse via
  EXTI0, or a transport command) is currently driving tempo — not yet
  modeled into a ticket file; ticket T (proposed) would close this.

## Layer 1 — Boot and ownership

**Solid**: `.data` (`0x20000000`-`0x200001f4`) and `.bss`
(`0x200001f8`-`0x20005eac`) ranges confirmed (A). Ctor sweep is one
53-call hand-written table, gated `r0==1 && r1==0xffff` (A). ~30 of
those 53 sites now have a RAM base + ctor VA (A, G); several have a
confirmed *role* via cross-ticket reads, not just existence: the
subscriber object (`0x20002d90`, role via C), `key_scan`'s own object
(`0x20000674`, role via C), the tick object (`0x20002bec`, role via I),
`mode_skip_apply`'s and `timediv_skip_apply`'s objects (`0x200004f4`,
`0x20001000`, roles via B/O).

**Still open**: ~23 ctor sites exist but have no role beyond "an object
is here" (G). 4 of 5 `init_array` slots never walked (A). `0x20001170`
(settings ptr) is now closed — it's the Mode object (O).

## Layer 2 — Main loop and IRQs

**Closed, essentially**: full periodic call list of `app_main_loop`
(`0x080150d0`) confirmed (C): key_scan → strip → 3×tick → 5×analog →
mode/timediv/third-detent skip-apply → 2×MIDI parse → 9×button
debounce. IRQ vector table fully enumerated; most slots are an infinite
spin, not a fault handler (C). USB HP/LP share one ISR body (C). DIN
(USART1) ISR confirmed and gated on a previously-uncatalogued flag
`0x200010e0` (C). TIM2 confirmed to gate through the same function
(`0x08012330`) analog processing uses — a general "skip if busy" check
(C) — and, per I, does **not** touch the tick object `arp_seq_tick`
uses, narrowing but not closing the internal-clock question.

**Still open**: `0x08010638`'s real caller chain (only known caller,
`0x080150a4`, itself uncharacterized — C). Two "early" debounce calls
and 3 stray `panel_button_dispatch` calls outside the main periodic
body (C).

## Layer 3 — Three input buses

**Buttons**: essentially closed. Compact index 0-8 = Hold, Shift, Oct−,
Oct+, Tap, Rec, Stop, Play, Chord (F, cross-validated against live
occupancy data from `stock-shift-map.md` — exact match). All three
`panel_button_dispatch` tables (unshifted, shifted, `r2==0`) have a
per-index row, most **S** structure with **H** semantic names matching
documented stock behavior (F). 2 of B's original 5 "unknown" Shift-RAM
sites closed to S structure (05/06, gated on Rec-armed and Pattern-mode
respectively — F); 3 stay unknown-as-a-gesture, 2 of those (15/16) now
have a plausible multi-button-bookkeeping mechanism (F).

**Analog**: objects and TBH shapes confirmed (D), but the actual
Type/Notes/Vel/Strum/Rate panel-name assignment has **no CC immediate
in the disassembled window** — that naming stays exactly as confident
as the pre-existing occupancy-only claim, not independently
re-derived (D). Shift+Mod's redirect is confirmed structurally; whether
it specifically skips a MIDI emit is not shown (D).

**Keys**: 4 static callers into the common note-entry point
(`0x0801b750`) confirmed, 3 inside `key_scan` (`r2=0`), 1 in an unnamed
function (`r2=1`) — all literal, all **S**. The physical/MIDI meaning
of `r2` itself stays **H**, an external claim not re-derived (E). **New
this round (J)**: that same entry point is also where
`voice_interval_load`/`voice_note_on` live — the key path and the
chord/voice-output path are one function, not two that converge.

## Layer 4 — Time

**Fields confirmed on the tick object** (`0x20002bec`): step (`+0x38`),
length (`+0x10`), a separate signed byte (`+0x55`, not to be confused
with the shared block's own `+0x55`) (I). Time Div RAM confirmed as
`timediv_skip_apply`'s object, field `+0x6d` (I, O). **Swing RAM: not
found anywhere searched** (I) — explicit hole, not a gap in effort.

**Clock source — narrowed, not closed**: SysTick and TIM2 confirmed to
*not* touch the tick object directly (I). Incoming MIDI Clock bytes and
TIM2 both load the same RAM address, `0x20005534` — the single
strongest concrete lead for where internal/MIDI clock converge (N,
cross-validated against I). A shared transport-command function
(`0x08012334`) is fed both by MIDI Start (`r1=1`) and Shift+Play
(`r1=4`) (N, cross-validated against J). Neither is a confirmed name.
Internal tempo RAM: not found (N). Rear-panel Sync DIP source-select:
out of scope for every ticket run so far.

## Layer 5 — Voice out

**Cell → pitch/vel/tie**: `seq_step_note`/`seq_step_gate` confirmed
exactly matching the existing catalog (J) — no correction needed.
`seq_step_release`'s actual callers narrowed (not inside
`play_time_step` itself, three external call sites — J). Pitch-gate
emission check (`0x08013ebc`) re-confirmed from this ticket's own bytes
(J).

**Chord/voice fields**: `+0x4d/+0x4e/+0x4f` (enable/vel/interval)
confirmed, plus a **new fourth field `+0x50`**, zeroed alongside them on
disable (M). Two parallel byte-value families write the same three
fields — real duplication, semantic split (base knobs vs. Chord-bank
knobs?) still H (M). Scale-mask object base promoted to S
(`0x20001e04`, offset `+0x36` confirmed via two chained helper calls —
M), and directly tied to per-key LED display via the general LED writer
(M, cross-validated against P).

**Port/USB-DIN**: a real structural finding — sequencer and key/voice
paths converge on one indirect port-switch (`0x0801b384`), sequencer
using object slot `+0xc`, key path using `+4`/`+0x14` (J). **Which slot
is USB and which is DIN remains unresolved** — the switch itself uses
indirect (`blx`) calls through object fields, not static addresses, so
the answer is in whatever ctor populates those fields, not in the
switch code (J). This is the single most concrete "next ticket" lead in
the whole model: find that ctor.

## Layer 6 — Protocol overlay

**GET dispatcher mapped**: `0x0800ee92`, a TBB on a signed byte, three
sibling GET-handler families sharing `get_param`'s prologue shape (K).
**Confirmed negative result**: none of Mode/Time Div/Type/Notes/the 8
button IDs are special-cased in this table — each is handled by its own
already-mapped mechanism (D/F/I/B), not this dispatcher (K). No SET
counterpart found — the `r2!=0` branch is a bare return (K).
`chord_test_dispatch` re-confirmed orphaned (no static caller, no
Thumb pointer) — same status as before, not newly discovered (K).

## Seq recorder (extends layer 3/5, ticket L)

`seq_step_store` entry and sole caller confirmed. Header fields
`+0x400/+0x401/+0x402` (Length/Swing/Gate) **promoted from
external-only to S** via this project's own disassembly (L). Rec-armed
flag (`0x200010b6`) identity confirmed by press/release symmetry, read
by both `key_scan` and `play_time_step` — the mechanism side of "Rec
held + keys 1-16 = Pattern length" (L). Rec LED write: not found (L, P
— independently, consistent).

## Persistence (ticket O)

Slot base arithmetic re-confirmed exactly (`0x0803b000+n*0x800`, all 8
slots). Settings pointer closed (it's the Mode object). **Real open
item, stated plainly**: no RAM→flash commit path for sequence data has
been found by any ticket — `seq_step_store`'s writes land on a RAM
staging block, not the flash slot base (O).

## LED/DMA (ticket P)

General LED writer (`0x0800d26e`, 33 callers) and a dirty-check-then-
flush refresh function (`0x0800d1f8`) both confirmed. One DMA channel
(`0x080185e8`) is the strongest LED-DMA candidate (reads an indirect
buffer pointer); one (`0x08018a40`) is explicitly ruled out as the
key-refresh path; one (`0x080186c4`) shows no evidence either way.

## Round 2 (R-Y) — closed since the addendum above

All 8 proposed tickets closed. Headline results, each a real
structural close even where the final semantic question stayed open:

- **R (USB/DIN)**: fully traced the 3-level ctor chain
  (`0x20001eb8 → 0x20001e04 → 0x20001d60`) both the key path and
  sequencer path share, down to `port_switch`'s actual vtable object.
  **No peripheral literal anywhere in the chain** — a real, exhaustive
  negative result. Honest conclusion: this needs Unicorn emulation, not
  more static search, and the model file says so explicitly.
- **S (ctor roles)**: closed 2 genuine open items — sites 02/03 explain
  `C-loop.md`'s unexplained "two early debounce calls," and site 45
  (`0x20002ddc`) is confirmed as `panel_button_dispatch`'s own object.
- **T (clock)**: `0x20005534` confirmed as a real TIM2 wrapper touched
  by 5 sources, but **no software arbitration flag exists** between
  them — internal and MIDI clock both just poke the same registers
  unconditionally. Real negative result.
- **U (SET protocol)**: exhaustively accounted for all 48 TBB/TBH
  structures in the app — **none is a second GET-shaped SET
  dispatcher.** SET, if it exists, isn't a mirror of GET.
- **V (persistence)**: FLASH IRQ4 has zero static callers (pure
  hardware ISR). No RAM→flash commit trigger found within the
  application-level boundary this ticket was scoped to.
- **W (LED/DMA)**: **corrected** P's "best candidate" DMA1_CH1 —
  traced its full tail, neither LED function appears in it. Rec LED
  confirmed absent from two independent directions now.
- **X (selectors)**: `param_field_dispatch`'s family split
  re-hypothesized as panel-knob-write vs. MIDI-CC-write (both callers
  sit in MIDI territory) rather than M's original "bank" guess. F's
  three previously-blank unshifted cases (Hold/Stop/Play) all resolved
  to at least one concrete fact each.
- **Y (recorder + clear)**: `seq_step_store`'s remaining TBB cases
  fully confirmed, independently matching the existing tie/rest
  sentinel table exactly. **Corrected** Q's `0x08016afc` claim — Y
  directly disassembled `0x08016ac0` and found B/F's original framing
  was right after all. Hold-length-clear gesture: ruled out at sites
  15/16 (confirmed as an unrelated two-button chord detector), still
  genuinely unmapped elsewhere.

## Top open leads, ranked (post Round-2)

1. **USB/DIN peripheral identity on `0x20001d60`** (R) — structure
   fully known, needs emulation not static search.
2. **`param_field_dispatch`'s family selector** (X) — panel vs. MIDI-CC
   hypothesis, unconfirmed.
3. **RAM→flash commit trigger** (V) — not found within the
   application-level boundary; next step is past the ST-HAL line this
   project deliberately doesn't cross.
4. **Case 5 of `seq_step_store`** (Y) — accumulate-then-copy shape
   shown, semantic role open.
5. Remaining ctor sites still existence-only after S (roughly a dozen).
6. Hold-length-clear gesture (Shift+Oct−+Oct+) — still fully unmapped.

STATUS: done
