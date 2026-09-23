STATUS: done
AGENT: claude
TICKET: Q
UPDATED: 2026-09-23T22:15+01:00 (corrected per Cursor's review — one
address's structural confirmation had an unconfirmed external-source
name attached to it)
INPUT: firmware-re/notes/scans/Q-h-rows.txt

# Q-promote — every leftover H/unverified VA, resolved

Read-only pass over `scans/Q-h-rows.txt` only. Per ticket instruction:
every address gets S, X, or H-with-one-line-reason. No new islands, no
`other repo/` promotions.

## Two corrections that matter for `recreate.py` (flagging, not editing)

**`0x08011c88` (`pattern_or_order_builder`) is a LABEL, not a function
start.** The scan's own methodology (push, or previous-insn bx/pop) and
this address's actual bytes (`movs r6,#0` directly, no push, entered
only via the mode TBH's branch table) confirm it shares its caller's
stack frame. **Same finding for all seven Mode-TBH targets**
(`0x08011a9e` Up, `0x08011ae0` Down, `0x08011b2c` Incl, `0x08011bb6`
Excl, `0x08011c46` Random, `0x08011c88` Order, `0x08011cca` Pattern) —
every one is a case-body label inside the dispatch function containing
`rebuild_order`'s TBH, none is independently callable. `recreate.py`
currently names `0x08011C88` as if it were a function. **Request to
Cursor**: consider whether that entry should be removed or re-labeled
as a case body, not a function start — not editing `recreate.py`
myself.

**`0x08004bf8` (`shift_strip_pickup`) is also a LABEL, not a function
start.** No push at all (`prev movs r0,#0` then straight into
`ldr r3,[pc,#0x2f0]`) — a branch target inside `analog_knob_process`
or `strip_process_b`, not a separate function. `recreate.py` also names
this one as a function. **Same request to Cursor.**

Both were already behaviorally correct in the catalog (what happens at
that address is accurately described) — only the "this is a distinct
function" framing needs correcting.

## Two places I disagree with the scan's LABEL tag, with reasoning

`0x0801161c` and `0x08013c9a` are filed as `LABEL` in the per-site
dumps, but the scan's own prose flags the real ambiguity first: both
are **confirmed ctor-sweep `bl` targets** (`A-boot.txt`, re-confirmed in
`G-ctors.txt` — `arp_note_pool_ctor` and `note_pool_pair_ctor`
respectively, already named in `recreate.py`). Neither has a `push`
because both are minimal leaf ctors (a handful of `str`/`strb` then an
implicit fall-through or `bx lr`) — Thumb code has no obligation to
push if it touches no callee-saved registers. **A `bl` target reached
directly from the ctor sweep is a real function call by construction,
regardless of prologue shape.** Recommending **S**, not X, for both —
disagreeing with the scan's own push/bx/pop heuristic here because I
have stronger, independent evidence (two other tickets' ctor-sweep
citations) that these are genuine call targets, not case-body labels
reached by branch.

## Confirmed real function starts (S) — re-confirms existing rows

`0x0800dad4` (`notify_013fc`), `0x08005a20` (`mode_skip_apply`),
`0x08005ab8` (`timediv_skip_apply`), `0x08018200` (`SysTick_Handler`),
`0x08018584` (`TIM2_IRQ`), `0x08019f8c` (debounce-family ctor),
`0x0801b750` (common note entry), `0x0800f054`
(`param_field_dispatch`), `0x080186d4` (FLASH IRQ4), `0x080185e8`
(DMA1_CH1 IRQ), `0x0801196c` (Pattern's semi-random builder target),
`0x08013de8` (scale-quantizing pitch generator, already cited in the
catalog's mode-TBH note), `0x0801306c` (`seq_block_ptrs_ctor`),
`0x08013e40` (`play_time_step_obj_ctor`), `0x0800fa64` (main-loop
MIDI parser), `0x0800fd5c` (DIN ISR target) — all **S**, all
re-confirmations of tickets A-P, no corrections needed.

**Correction (Cursor's review caught this):** `0x08010638` — the scan
shows a real `push`, so **the function-start question is S**. **"USB
packet decode" is not** — that's still the old external-source label
from `address-catalog.md`'s "Input path (external source, unverified
by us)" section. This scan shows only the prologue (`push
{r4,r5,r6,r7}`, `bic r6,r2,#3`, ...), nothing about USB or packet
decoding specifically. I wrote the label as if it had been confirmed
alongside the structural fact — it hasn't. Its caller `0x080150a4` is
still not itself a confirmed start either way (unchanged from below).

## New confirmed function starts, not previously named

- `0x08007652` — clean start-after-`bx`, called from `SysTick_Handler`.
  Not previously named. **S existence**, no role claim.
- `0x08006988` — clean start-after-`bx`. This is the same address
  `H-shared.md` cited as an *example site* for the `+0x54/+0x55/+0x56/
  +0x57/+0x5b` field cluster on the shared block — now confirmed it's
  also a genuine function, not just a field-read location. **S.**
- `0x08013028` — tiny 3-instruction leaf (`ldr r3,[r0,#4]; str r3,[r0];
  bx lr`). This is `J-voice.md`'s "second caller" of the seq-block
  update (`0x08012bd6 → 0x08013028`) and matches the existing catalog's
  "external source" note **exactly**: "replaces the current pointer
  with the pending pointer." Own disassembly now confirms that claim
  precisely — `current_ptr = pending_ptr` in one line. **Promoting that
  specific external claim to S.**

## Correction to a B/F-ticket containing-function citation — since superseded by ticket Y

`0x08016afc` was flagged here as start-after-pop, a genuine separate
function. **Ticket Y directly disassembled `0x08016ac0` and found both
readings were partly right**: `0x08016ac0` is a real function (push
`{r4,r5,lr}`), and it branches to `0x08016afc` internally on `r1==1`
(`cmp r1,#1; beq 0x8016afc`) — so `0x08016afc` is reached both by
fallthrough (what this scan found) and by that internal branch, but has
no independent `bl` target of its own. Net: B/F's original "inside fn
`0x08016ac0`" citation is the more accurate framing after all — see
`model/Y-record-clear.md` §4 for the full correction.

## Confirmed labels (X) — case-body/branch targets, not function starts

All of: `0x08017856`, `0x0801787e`, `0x080178c8`, `0x080178a8`,
`0x08017a34`, `0x08017a40`, `0x08012b48`, `0x08006a10`, `0x08012d56`,
`0x0801557c`, `0x0801b910`, `0x08011a9e`, `0x08011ae0`, `0x08011b2c`,
`0x08011bb6`, `0x08011c46`, `0x08011c88`, `0x08011cca`, `0x08012b62`,
`0x08012bd6`, `0x08010310`, `0x08004930`, `0x08004bf8`, `0x0801a078`,
`0x0801a11a`, `0x0800f4b8`, `0x0801b75a`, `0x080150a4`. **X on the
"is this a function start" question for all 28.** None of the
underlying *behavioral* catalog content at these addresses (from F, H,
I, M, and pre-existing rows) is contradicted by this — they were all
already described as sites/fields/case-bodies, not asserted as
function starts, with the two exceptions called out above
(`0x08011c88`, `0x08004bf8`, both already in `recreate.py`).

`0x080150a4` specifically: confirmed not itself a start, but its own
containing function's real entry point is still not found in this
scan's window (ends at `0x080150ac` with `pop`, start not shown) — this
was already an open item in `C-loop.md`, staying open, not newly
resolved.

## Stop condition check

Per ticket instruction ("catalog has no drive-by H from tickets A-P;
remaining H is labelled on purpose"): every address this scan covered
now has an explicit S, X, or reasoned-H verdict above. Two genuine
`recreate.py` corrections flagged (not edited, per file ownership).
One containing-function citation corrected. Two scan-tag disagreements
resolved with stated reasoning, not silently overridden.

STATUS: done
