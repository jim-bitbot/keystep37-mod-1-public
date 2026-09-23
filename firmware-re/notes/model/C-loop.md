STATUS: done
AGENT: claude
TICKET: C
UPDATED: 2026-09-22T21:53:23+01:00
INPUT: firmware-re/notes/scans/C-loop-irq.txt; firmware-re/notes/model/A-objects.md; firmware-re/notes/model/B-shift-handlers.md; firmware-re/notes/address-catalog.md

# C-loop — main loop and IRQs

Read-only pass over `scans/C-loop-irq.txt`. Tags: **S** = confirmed by
this disassembly, **H** = plausible, unconfirmed. This ticket resolves
two things left open in earlier tickets and turns up one correction to
a previously "external, unverified" claim — flagged clearly below.

## 1. Boot → main loop chain, now fully closed

`Reset_Handler` → `libc_init_array` slot 4's ctor sweep (already known)
→ `0x08016838` (the only other static caller besides the ctor-sweep
path; GPIO/clock setup, then `bl 0x080150d0`) → `0x080150d0`, which
**never returns** — its own inner body ends in a backward branch
(`0x08015912  b #0x080157c8`), so the `pop {r4,pc}` back in `0x08016838`
after that `bl` is dead code, never reached. This is the actual
application main loop. **S.**

## 2. IRQ vector table

Only 13 of the ~60 vector slots are non-default; everything else
(including NMI, all three fault handlers except HardFault, SVCall,
Debug, PendSV, and most peripheral IRQs) points at
`0x0801d358: b #0x0801d358` — **an infinite spin, not a fault reporter.**
Worth flagging plainly: any unexpected/misconfigured interrupt on this
firmware hangs the device silently rather than resetting or signaling a
fault. Not a new risk we're introducing, just worth knowing before
anyone reasons about firmware robustness. **S.**

Handled: SysTick, FLASH (IRQ4), EXTI0 (IRQ6), EXTI3 (IRQ9), DMA1
CH1/2/3 (IRQ11-13), USB_HP/CAN_TX (IRQ19), USB_LP/CAN_RX0 (IRQ20), TIM2
(IRQ28), TIM4 (IRQ30), USART1 (IRQ37). Only SysTick, USB HP/LP, USART1,
and TIM2 are walked this ticket (below); FLASH/EXTI0/EXTI3/DMA1×3/TIM4
are named but not disassembled.

### SysTick (`0x08018200`)

Calls an unnamed `0x08007652`, then increments a 32-bit counter at
`0x20001090` and a byte at `0x2000528d` that wraps against `8` (compared
right after increment; branches away above `8`, i.e. cycles `0..8`,
9 values). Two plausible roles — a millisecond tick plus some kind of
9-way round-robin/stagger counter — neither confirmed by this scan.
**S** for the counters existing; **H** for what they're for. Note the
`0..8` cycle is the same width as the 9-object button-debounce family
(§4) — could be coincidence, could be related; not traced.

### USB ISR — and a correction to an existing external-only claim

IRQ19 (USB_HP) and IRQ20 (USB_LP) are two tiny trampolines, both loading
the **same** object (`0x20005888`) and calling the **same** function,
`0x08009662`. **S.**

`address-catalog.md`'s "Input path" section (filed "external source,
unverified by us") names `0x08010638` as "USB packet decode, writes a
byte ring." This scan's whole-image `bl`-to search (§4 of the scan) shows
**the only static caller of `0x08010638` is `0x080150a4`** — not the USB
ISR, not the main loop function. **The external claim's implied wiring
(interrupt → this function) doesn't hold up against our own
disassembly; the real USB ISR body is `0x08009662`, reached the way
shown above.** `0x080150a4` itself isn't characterized yet (it sits
immediately before the main loop function in flash, `0x080150d0`, but
that's proximity, not a demonstrated relationship). This is the biggest
open thread from this ticket for whoever does more USB/input work: how
`0x08010638` is actually reached is still unknown, but it is **not**
called directly from an interrupt handler as previously assumed. **S**
for what's shown (call-site fact); flagging the external claim's wiring
as unconfirmed-and-now-doubtful, not confirming or replacing it.

### USART1 / DIN ISR — external claim upgraded to confirmed

`address-catalog.md`'s same "Input path" section names
`0x08018624 → 0x0800fd5c` as "Serial (DIN) input can call this from IRQ
— not all note input is main-loop work," also filed external/unverified.
**This scan confirms it exactly**: IRQ37 (USART1, `0x08018624`) checks
an RXNE-style status bit (bit 5, checked twice against two register
reads), then a previously-uncatalogued gate at `0x200010e0` — only if
that's nonzero does it read the data byte and `bl 0x0800fd5c(r1=byte)`.
**Promoting this specific claim to S** — own disassembly, not
external — with one addition the external source didn't have: it's
gated on `*0x200010e0`, a DIN-enable-or-similar flag not in the catalog
before now.

### TIM2 ISR — new territory, one strong cross-reference

`0x08018584`: calls `0x0800b2ae(r0=0x20005534)` (likely the raw timer
peripheral wrapper — not traced further), then loads `*0x20001098` and
calls `0x08012330(r0=that)`, branching away if the result is nonzero.

**This is the exact same gate used inside `analog_knob_process`'s kind-0
branch** (Wave 2 scan, `0x0800498c`: `ldr r3,[pc]=0x20001098; ldr
r0,[r3]; bl 0x08012330; cmp r0,#0; bne <skip>`). Same pointer, same
callee, same "skip if nonzero" shape, in two otherwise-unrelated places
(a timer interrupt and analog processing). Strong evidence
`0x08012330(*0x20001098)` is a general-purpose "is some UI/mode state
busy, skip background work" gate, not something local to either caller.
**S** for the duplication being real; **H** for the "what it gates"
interpretation.

Past that gate, TIM2 checks a byte at `*0x20001158`; if nonzero,
increments a 16-bit counter at `0x200010de` and calls
`0x08011ee4(r0=*0x20001098)`. This is a **different** function from
`arp_seq_tick` (`0x080129cc`) — a second, hardware-timer-driven tick
path, not a duplicate of the main-loop clock call. Strong candidate for
the actual internal-clock pulse (HANDOFF layer 4, "Time"), gated behind
its own enable byte and counting its own ticks separately from
`arp_seq_tick`. **H**, but a good lead for whoever does layer 4 next —
not proposing a name without more evidence.

## 3. Main loop `0x080150d0` — structure

**One-shot head** (before the loop): registers an object at
`0x20002d90` into the subscriber table at `0x20001120` (`bl
0x0801d70e`, then `str r4,[r3]`). **This closes an open item from
`A-objects.md`**: `0x20002d90` was ctor-sweep site 4 (`A-boot.txt` §2),
listed there as unwalked. It's now confirmed to be the object the main
loop hands to the subscriber table at startup. **S.**

**Periodic body** (`0x080157c8` → back-branch at `0x08015912`), in
call order, once per pass unless noted:

1. `bl 0x0800cc48(r0=0x20000674)` — Cursor's own scan comment labels
   this **"keys/scan."** This is the function I could not identify in
   `B-shift-handlers.md` (sites 05/06 — filed "unknown stock secondary")
   — **it's the key-matrix scanner, not a Shift-panel handler.**
   Resolves both sites: Shift RAM is consulted *during key scanning*,
   for a reason not yet traced. **S** (function identity via Cursor's
   annotation + call-site confirmation).
2. `bl strip_process_b(0x2000039c)` — already known.
3. `bl arp_seq_tick` **three times** per pass (`0x0801576c`,
   `0x080157b4`, `0x080157e8`), only one `r0` shown (`0x20002bec`, at
   the first site). The other two objects aren't captured in this scan.
   Multiple calls per loop pass to the same function, on (at least
   sometimes) different objects, isn't explained yet — open thread. **S**
   for the multiplicity; not walked further.
4. `bl analog_knob_process` **five times**, over exactly the five
   objects from `A-objects.md` §4a (`0x20000468/0x2000121c/0x20001294/
   0x2000130c/0x20001384`) — confirms all five are polled once per main
   loop pass. **S.**
5. `bl mode_skip_apply(0x200004f4)` then `bl
   timediv_skip_apply(0x20001000)` — first time either function's actual
   *object* argument is known (`B-shift-handlers.md` only had the
   functions themselves, not their callers' object bases). **S.**
6. `bl 0x08005d68(0x2000058c)` — a third, not-yet-named call,
   structurally in the same "one call per detent-style object" position
   as 5 above. `0x2000058c` is the RAM address `A-objects.md` §5 flagged
   as an unconfirmed lead ("possible settings object," tied loosely to
   `mode_byte_get`'s neighbouring ctor). **This scan doesn't confirm
   that lead's original reasoning, but it does confirm the object is
   real and is processed once per loop by a dedicated handler**, which
   is independent supporting evidence for treating it as a genuine
   third "detent knob"-shaped object (Rate, per the manual's parallel
   description, is the obvious remaining candidate — not confirmed).
   **H, moderately strengthened.**
7. `bl 0x0800fa64` (MIDI parser) **twice** per pass. `address-catalog.md`
   has this as external/unverified ("main-loop MIDI parser, ≤50 bytes
   per invocation"). **The "called from the main loop" half of that
   claim is now confirmed** (own disassembly, two call sites, both here)
   — the "≤50 bytes per invocation" detail isn't checked by this scan
   (would need the function body). Partial upgrade: **S** for call-site
   existence, claim's internal-behavior detail stays unverified.
   Also noted: an earlier, different call at `0x080154cc → 0x0800fa16`
   (a function immediately before `0x0800fa64` in flash) — possibly a
   "sibling parser," not traced. **H, open lead.**
8. Nine `bl button_debounce` calls, over **exactly** the nine objects
   from the `0x08019f8c` ctor family (`A-objects.md` §6:
   `0x20000388/0x20000564/0x2000042c/0x20000440/0x200005e4/0x200004e0/
   0x20000578/0x20000454/0x20000374`, kinds 0-8).

   **This is the confirmation `A-objects.md` §6 was missing.** That
   ticket flagged the nine-object family as a strong structural match
   for `id_to_index`'s nine compact button IDs, but explicitly did not
   propose it as a catalog row because no *reader* of those objects had
   been traced. `docs/HANDOFF.md`'s ticket-A-close note records Cursor
   rejecting exactly that hypothesis for lack of a reader
   ("Rejected H: `small_indexed_obj_ctor` `0x08019f8c`"). **This scan
   supplies precisely the missing reader**: `button_debounce`, called
   once per object, once per main-loop pass, over all nine. Re-proposing
   below with this new evidence. **S** (existence of the ctor family was
   already S; the reader link is now S too — the *role* — "one object
   per compact button ID" — is still inference from the count matching,
   not from reading `button_debounce`'s use of the object's fields, so
   keeping that specific interpretation at H).

Also present but not on the backward-branch path (so not necessarily
once-per-pass): two "early" `button_debounce` calls (`0x080154e0`,
`0x080154e6` — two objects, not among the nine) and three
`panel_button_dispatch` calls (`0x08015936`, `0x08015954`, `0x08015970`).
Neither set is explained by this scan — flagging as open, not guessing.

## 4. Whole-image `bl`-to cross-reference (scan §4) — confirms several "exactly one caller" facts

- `analog_knob_process`, `strip_process_b`, `arp_seq_tick`,
  `button_debounce` (main nine + two early): **every static call site in
  the whole image is inside `0x080150d0`.** No other code path invokes
  panel/analog scanning directly. **S.**
- `0x0801b750` (the note-processing entry point HANDOFF layer 3 names,
  previously 100% external-sourced per `prep-islands.md` §3) has **four**
  call sites: `0x0800cdfa`, `0x0800cf30`, `0x0800d064`, `0x08010326`.
  The first two sit inside/near `0x0800cc48` — **the same "keys/scan"
  function identified in §3 item 1 above.** This is the first
  own-disassembly evidence tying physical key scanning to the note-entry
  point named in the external source, and it lines up with that
  source's own description of `0x0801b750` ("r2=0 from physical key
  scanner, r2=1 from either MIDI port") — two key-side call sites here
  is consistent with that split, though which `r2` value each site
  passes isn't verified. **S** for the call-site existence and the
  keys-side location; **H** for the r2=0/r2=1 interpretation, which
  remains the external source's claim, not re-derived.

## Net for HANDOFF layer 2

Main loop and its full periodic call list are now mapped: keys/scan →
strip → 3× tick → 5× analog → mode/timediv/third-detent skip-apply →
2× MIDI parse → 9× button debounce, plus the boot chain into it and four
of the ~13 live IRQs walked. Two things from earlier tickets got closed
(ctor site `0x20002d90`'s role, the nine-object button family's reader).
One external claim got upgraded to confirmed (DIN ISR). One external
claim's wiring got specifically contradicted by our own disassembly
(USB packet decode is not called from the ISR) — flagged, not silently
corrected, since `0x08010638`'s real caller (`0x080150a4`) isn't
characterized yet either.
