STATUS: done
AGENT: claude
TICKET: D
UPDATED: 2026-09-23T19:20+01:00
INPUT: firmware-re/notes/scans/D-analog.txt

# D-proposed-catalog — rows for Cursor to review

Reasoning for each row is in `model/D-analog.md`. Format per
`two-agent-protocol.md` §6. Every row's What cell is a panel name or the
word unknown, per the ticket instruction — no row asserts Type/Notes/
Vel/Strum/Rate from this scan, since no `0x62`-`0x66` immediate appears
in the disassembled window.

## Kind targets — existence/shape only, no panel name

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| `0x0800498c` | | analog_kind0_strip (tentative) | Reached via `cbz r5,#0x0800498c` when `+0x58==0`, not a TBH case. Shift-RAM-gated (`0x200010d2`) pickup math on the raw `+0x59` byte. No CC/panel-name evidence in this scan. Panel name: unknown | S (existence/shape), unknown (name) |
| `0x0800527c` | | analog_kind1 (tentative) | TBH case `r3=0`. Calls `0x0801b246` then `0x080048f8` (imm `r1=0xd`); stores signed 16-bit to `obj+0x68`, sets bit 0 of `obj+0x70`. No CC/panel-name evidence in this scan. Panel name: unknown | S (existence/shape), unknown (name) |
| `0x080054c6` | | analog_kind2 (tentative) | TBH case `r3=1`. Same shape as kind 1: `0x0801b250` then `0x080048f8` (imm `r1=0xf`), `+2` adjustment before the 16-bit store. Panel name: unknown | S (existence/shape), unknown (name) |
| `0x080056cc` | | analog_kind3 (tentative) | TBH case `r3=2`. Same shape again: `0x0801b278` then `0x080048f8` (imm `r1=0x80`). Panel name: unknown | S (existence/shape), unknown (name) |
| `0x080058cc` | | analog_kind4 (tentative) | TBH case `r3=3`. Different shape from kinds 1-3: no call to the `0x0801bxxx` helper family; sign/threshold arithmetic on raw `+0x59` against `0x77`/`0x88`, `smull`-based scale. Panel name: unknown | S (existence/shape), unknown (name) |

## Store site

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| `0x08004930` | | analog_raw_latch (tentative) | `strb.w r3,[r4,#0x5a]` — only store of `+0x5a` in the scanned window. Updates "last raw" from `+0x59`, gated on inequality, before kind dispatch and before the AutoTest check | S |

## Object `0x2000039c` (strip)

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (no new address — existing `strip_b_ctor`/`0x2000039c` row) | | | Confirmed distinct object from all five analog-kind objects; sole static caller of `strip_process_b` (`0x08004388`). Shift-held (`0x200010d2` != 0) at `0x080043c4` redirects to tail block `0x08004428`, which stores `4` to `0x200010dc` — a branch-redirect on Shift-held is **S**; whether that redirect specifically skips a MIDI-emit call is **not shown** in this scan (no MIDI-emit call is visible in the shown tail) | S (redirect exists), not shown (MIDI-skip claim) |

## Not proposed

`knob_index_to_cc`'s CC-to-kind mapping itself (which kind gets which of
98-102) is not in this scan's disassembled window (only the *call* to it
is shown, with a runtime kind byte, not a literal). The existing
catalog's Type/Notes/Vel/Strum/Rate naming stays exactly as confident as
it already was (**P**, occupancy-verified) — this ticket neither
strengthens nor weakens it, it just does not independently reproduce it
from static disassembly.

STATUS: done
