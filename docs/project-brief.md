# Project Brief: KeyStep 37 firmware 1.1.6.579

## Goal (current)

Understand the stock Arturia KeyStep 37 **application 1.1.6.579** well
enough that later patches can be designed from a machine model (boot,
objects, RAM, main loop / IRQs, three input buses, time, voice out).

This is not a rewrite and not a 9th Mode-knob detent. **Do not build or
flash Euclidean / chord images in this phase.** Those experiments are
future work (see [HANDOFF.md](HANDOFF.md) “Feature page”).

Flash without MIDI Control Center is **solved infrastructure**:
Rec+Stop+Play, leave `0291` on Windows, `./scripts/flash-win.sh`. MCC is
recovery. Never attach `0291` to WSL.

## What is already known

Authoritative detail lives in [HANDOFF.md](HANDOFF.md).
[../firmware-re/notes/findings-2026-09-20.md](../firmware-re/notes/findings-2026-09-20.md)
is the chronological evidence log — do not take mid-file “not yet
located” paragraphs as current.

Confirmed (flash VAs on the stripped extract):

- Protocol (USB/MIDI, `arturia_v2` GET, bootloader `.led` transfer) is
  solved and live-verified. Flash-without-MCC is closed.
- `.led` is hex-ASCII Huaxin segments. App loads at `0x08004000` (vector
  table + Reset `0x0801d311`). Bootloader is the 16 KiB below that.
- Pattern player named: engine `+0x10 == 6` (CC21=7). TBH `0x08011a38`.
  Play-time `0x08013e8c`. Emission gate is pitch-gate `0x08013ebc`, not
  `seq_step_gate` bit 7. Do not hook `set_arp_mode` / TBH case 7.
  `object+0x214` is an event-handler table, not eight mode vtables.
- Panel occupancy: [stock-shift-map.md](../firmware-re/notes/stock-shift-map.md).
  Test-20 CCs **are** firmware control IDs. Shift held = `0x200010d2`.
  Shift+keys 1–16 = Keyboard MIDI CH.
- Trailer u16s are Huaxin additive checksums (`led_codec.py retarget`).
- The Mode knob is 8-detent. A new visible 9th mode is not possible.

These are **islands**. Boot/object/RAM/loop maps are not done.

## Precedent, with a caution

Daniel Gruss reverse-engineered the **original** KeyStep. Useful and
confirmed here: hex-encoded `.led`, unsigned/unencrypted app image,
SysEx update, separate bootloader region.

**KS37 checksums are the Huaxin/midiplus segment scheme** (Gruss /
auduchinok), not a 20-byte flat header. Wire transfer still has no extra
CRC. The original KeyStep binary has zero content overlap.

## Safety

See [firmware-safety-rules.md](firmware-safety-rules.md) and
[flash-checklist.md](flash-checklist.md).

1. Discovery needed to **operate** the flash lab is done.
2. MCC Flash A (stock) → C (unused-page poke) → D (stock restore) done.
3. `flash-win.sh` live PASS (2026-09-22). ALSA dump stays refused.
4. Feature images (E0–C2) are frozen experiments — **future**, not current.

Never touch bootloader, USB/MIDI stack, or the update path. Do not write
`0x0803B000`.

## Immediate work

Static analysis of
`firmware-re/firmware-images/keystep37_1.1.6.579_flash.bin`.
Two agents: [two-agent-protocol.md](two-agent-protocol.md). Grow
[address-catalog.md](../firmware-re/notes/address-catalog.md) **via
Cursor only** from Claude’s `model/*-proposed-catalog.md`.
[ARTURIA-FIRMWARE-RE-GUIDE.md](ARTURIA-FIRMWARE-RE-GUIDE.md) (wire
constant → `cmp` imm → correct function boundary). No live flash unless
Jim says restore stock.
