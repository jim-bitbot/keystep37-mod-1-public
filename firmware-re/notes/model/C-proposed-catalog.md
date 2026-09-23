STATUS: done
AGENT: claude
TICKET: C
UPDATED: 2026-09-22T21:53:23+01:00
INPUT: firmware-re/notes/scans/C-loop-irq.txt; firmware-re/notes/model/C-loop.md

# C-proposed-catalog — rows for Cursor to review

Reasoning for each row is in `model/C-loop.md`. Format per
`two-agent-protocol.md` §6.

## New section: Main loop / IRQs

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| `0x080150d0` | | `app_main_loop` | Entered once from `0x08016838` (post-init), never returns. One-shot head registers `0x20002d90` into the subscriber table (`0x20001120`); periodic body is the back-branch at `0x08015912` | S |
| `0x0801d358` | | `default_irq_stub` | Target of every unhandled vector (NMI, all faults except HardFault, SVCall, Debug, PendSV, most peripheral IRQs): `b #0x0801d358` — an infinite spin, not a fault reporter. Any unexpected IRQ on this firmware hangs silently | S |
| `0x08018200` | | `SysTick_Handler` | Calls unnamed `0x08007652`; increments 32-bit counter `0x20001090` and a byte at `0x2000528d` that cycles `0..8`. Role of the second counter not determined | S existence / H role |
| `0x08009662` | | `usb_isr_common` | Shared body for both USB_HP (IRQ19) and USB_LP (IRQ20), both called with the same object `0x20005888` | S |
| `0x08018624` | | `USART1_IRQ` (din_isr) | RXNE-style check, gated on new flag `0x200010e0`, then `bl 0x0800fd5c(r1=byte)`. **Upgrades an existing external/unverified catalog row to confirmed** — see note below | S |
| `0x08018584` | | `TIM2_IRQ` | `bl 0x0800b2ae(0x20005534)`; then `*0x20001098` through the same gate (`0x08012330`) `analog_knob_process` kind-0 uses; if not gated, increments `0x200010de` and calls `0x08011ee4(*0x20001098)` — candidate internal clock tick, distinct from `arp_seq_tick` | S structure / H role |
| `0x0800cc48` | | `key_scan` (tentative) | Called once per main-loop pass with `r0=0x20000674`. Cursor's own scan comment labels it "keys/scan." Internally reaches `0x0801b750` (note-processing entry, previously 100%-external per `prep-islands.md`) via two of that function's four call sites. Resolves `B-shift-handlers.md` sites 05/06 ("unknown stock secondary") as living inside this function, not a Shift-panel handler | S |

## Existing row to upgrade — provenance only

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (existing "Input path" row: `0x08018624` → `0x0800fd5c`) | | | Was filed "external source, unverified by us." This scan confirms it directly by our own disassembly, plus the previously-uncatalogued gate `*0x200010e0`. Requesting provenance upgrade to **S** | S |

## Existing row to flag — wiring contradicted, not confirmed

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (existing "Input path" row: `0x08010638`, "USB packet decode, writes a byte ring") | | | Whole-image `bl`-to search: only static caller is `0x080150a4`, **not** the USB ISR (`0x08009662`) and not the main loop. The claim's *existence*/description may still be right, but its implied "reached from IRQ" wiring does not match our disassembly. Recommend keeping the row H but adding this caveat rather than treating the wiring as settled | H, flag added |

## Re-proposing a previously-rejected hypothesis, with new evidence

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (re-raising `small_indexed_obj_ctor`, `0x08019f8c`, rejected at Ticket A close for lack of a reader) | | | `app_main_loop` calls `button_debounce` over **exactly** these nine objects, once per pass, in kind order 0-8. This is the reader that was missing. Existence of the ctor family + this reader link: **S**. "One object per compact button ID" (the original interpretation) is still not confirmed by reading `button_debounce`'s use of the object fields — keeping that specific claim at **H** | S (ctor + reader) / H (role) |

## Not proposed — open threads, see `C-loop.md` for detail

Real caller chain into `0x08010638` (only known caller `0x080150a4`,
itself uncharacterized); possible "sibling parser" `0x0800fa16`
(one call site, `0x080154cc`); two "early" `button_debounce` calls
outside the nine-object family; three `panel_button_dispatch` calls off
the main back-branch path; `arp_seq_tick`'s other two call sites' object
arguments; the other two `0x0801b750` call sites (`0x0800d064`,
`0x08010326`) and whether they're the MIDI-side (`r2=1`) callers the
external source describes. All flagged, none proposed as rows.
