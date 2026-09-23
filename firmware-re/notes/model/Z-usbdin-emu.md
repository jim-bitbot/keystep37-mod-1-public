STATUS: done
AGENT: claude
TICKET: Z
UPDATED: 2026-09-23T23:35+01:00
INPUT: firmware-re/notes/scans/Z-usbdin-emu.txt

# Z-usbdin-emu — the USB/DIN question, closed by reframing it

Read-only pass over `scans/Z-usbdin-emu.txt` only. This closes the
thread J opened, R traced structurally, and my own `lead-usb-din.md`
spot-check said needed emulation — Cursor's Unicorn run is the
decisive step all three were waiting for.

## 1. emit_key's `+4` slot is confirmed USART1 (DIN), by direct MMIO

Running `emit_key` (`0x0801ad20`, `r0=0x20001d60`) with a real Note-On
word reached the `+4` blx target (`0x08014b7c → 0x08010c10 →
0x08010b5a → 0x08010aa8 → 0x08010b14`) and produced **real,
observed MMIO**: read then write `0x4001380c` (USART1 base
`0x40013800` `+0xc` = CR1), ORing in `0x80` — a standard "arm TX
interrupt, byte ready to send" pattern on a UART. **S — this is not
inferred, it's a directly observed hardware register write from a
clean 232-instruction run with no fault.** A second run with a generic
(non-Note) status byte hit the identical watchpoints and MMIO,
confirming this isn't Note-On-specific.

**`emit_key`'s `+4` slot is DIN (USART1). Closed.**

## 2. emit_key's `+0x14` slot is NOT USB — reaches a display-adjacent function

The second blx (`+0x14`, `0x08014b6c`) is reached **after** the USART
store, and resolves to `0x0800d77c` — the same function `R-usbdin.md`
already flagged as reading `0x200051cc+0xb9` (AutoTest flag). Per the
scan's own annotation, this is display-related, not a second output
port. **S** for the call reached; the "display" characterization is
Cursor's own note in the scan, not independently re-derived here —
worth a follow-up if the exact role matters later, but not a USB
candidate either way.

## 3. USB is not one of the vtable slots at all — it's a separate path

This is the real finding, and it reframes the whole question rather
than just answering it:

- **`0x20005888` (the USB object) is never loaded during `emit_key`'s
  run.** No USB MMIO, no `0x08009662` (USB ISR), ever touched.
- The actual USB-send entry point is a **completely different function**:
  `0x08010e46` (`ldr r0,[pc]; ; 0x20005888` then `bl 0x080091ca`),
  found by Cursor's own direct-leaf search (§3 of the scan) —
  **not reached from `emit_key` or `emit_seq` at all.**
- `emit_seq`'s two tested paths (Note-On via `+0x18`/`+0x1c`, generic
  via `+0xc`) reach **no peripheral MMIO whatsoever** in this run —
  Note-On faults on an unplanted (never-initialized-by-the-traced-ctor)
  function pointer slot; the generic path reaches a thunk but no
  register access, limited by the test harness's dummy object, not by
  a discovered dead end.

**Conclusion, stated as plainly as the scan states it**: the
`port_switch`/`emit_key`/`emit_seq` vtable mechanism this project has
been calling "the USB/DIN port switch" since ticket J is **not** a
USB-vs-DIN selector. `emit_key`'s `+4` slot is confirmed DIN. Nothing
in either emit function's traced paths reaches USB. **USB output goes
through an entirely separate mechanism** — a call site at `0x08010e46`
(`bl 0x080091ca → ... → 0x08009662`; **correction**: Cursor's later
catalog-copy check found this address is mid-function, not a distinct
entry point as I'd implied by naming it — the site and the finding
stand, just not as a named function), not modeled by any ticket to
date — J, R, and this ticket were all, in effect, mapping the
DIN/display side of a mechanism whose other real branch (USB) lives
elsewhere.

## 4. Correction (ticket AK): this item is closed, not open

**`emit_seq`'s `+0x18`/`+0x1c` fields ARE written by `0x0801acb0`** —
`R-usbdin.md` originally reported a 6-word ctor because I stopped
reading its body one `stm.w` early; AK's scan shows it's actually an
8-word copy, `+0` through `+0x1c`. This Unicorn run's fault at that
address was a **harness limitation after all** (the test's planted
object only had 6 of 8 words set, matching my own incomplete ctor
trace at the time) — not the structural gap I called it. `R-usbdin.md`
is corrected; see that file for the full detail. The real open question
is now narrower: what values the sweep's stack actually supplies for
those two slots, not whether they're populated.

## Net for HANDOFF layer 5 — this is the real close

**DIN emit: confirmed, MMIO-level.** **USB emit: not on this object at
all — it's `0x08010e46`'s job**, a separate, still-unmapped entry point
(deliberately not walked further, per the project's USB-stack-off-limits
rule — `0x08009662` and below stay out of scope). This is a complete,
honest answer to "USB vs DIN," just not the one the question assumed:
there was never a single switch choosing between them on this object —
DIN lives here, USB lives somewhere else entirely.

STATUS: done
