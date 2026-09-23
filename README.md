# Arturia KeyStep 37 — firmware 1.1.6.579

**Read first:** [`docs/HANDOFF.md`](docs/HANDOFF.md). Addresses:
[`firmware-re/notes/address-catalog.md`](firmware-re/notes/address-catalog.md).
Packaging: [`firmware-re/notes/led-header.md`](firmware-re/notes/led-header.md).
MCU / holes: [`firmware-re/notes/flash-map.md`](firmware-re/notes/flash-map.md).
Evidence log: [`firmware-re/notes/findings-2026-09-20.md`](firmware-re/notes/findings-2026-09-20.md)
(chronological; mid-file “not yet located” paragraphs are stale).
Method: [`docs/ARTURIA-FIRMWARE-RE-GUIDE.md`](docs/ARTURIA-FIRMWARE-RE-GUIDE.md).

## Current goal (2026-09-22)

**Understand stock application 1.1.6.579 as a machine model** so later
patches can be designed from objects, RAM, loops, and the three input
buses — not from another feature hunt.

This is not a firmware rewrite. It is not a 9th Mode-knob detent. Do
**not** build or flash Euclidean / chord images in this phase. Those
experiments exist on disk (`e0b`…`c2`) and are **future work**.

Flash without MIDI Control Center is **solved lab infrastructure**. Do
not reopen the WSL ALSA updater. Do not attach `0291` to WSL.

## Status

| Area | State |
|---|---|
| Stock `.led` + stripped flash extract | Done |
| Huaxin packaging + checksums (`led_codec.py`) | Done |
| Flash without MCC (Rec+Stop+Play → `flash-win.sh`) | **Closed.** MCC is recovery only |
| Panel occupancy (silk + Test-20 CCs + eyes-on holes) | **Done enough.** [`stock-shift-map.md`](firmware-re/notes/stock-shift-map.md) |
| Machine model of 1.1.6 (boot, objects, loop, IRQs, three buses, time, voice) | **Current work.** Islands only (~40 named functions) |
| Euclidean restripe / latch / scale-chord | **Future.** Packaged; do not extend or reflash |

Analyze `firmware-re/firmware-images/keystep37_1.1.6.579_flash.bin`
(base `0x08000000`). App Thumb is `0x08004000`–`0x0801F400`.

## Flash lab (do not explore further)

Enter the updater with **Rec+Stop+Play** on plug (Hold/Shift alternate).
Device stays on **Windows** (stop AutoAttach; do not attach `0291` to WSL).

```
./scripts/flash-win.sh --dry-run
./scripts/flash-win.sh --already-bootloader --already-unlocked --confirm YES-FLASH \\
  /mnt/c/Users/jimcu/KeystepFlash/keystep37_1.1.6.579_stock.led
```

That shells out to Windows `flash_win.py`, which imports this repo’s
`led_codec.py`. `flash_bl_wsl.sh` refuses (ALSA stall). Images live in
`C:\Users\jimcu\KeystepFlash\` and local `og_firmware/` /
`firmware-re/recovery/` — **not in git**. Factory reset is Oct−+Oct+ /
display `rST`.

## Already known (islands, not a model)

1. Stock firmware downloaded — `og_firmware/`.
2. `.led` is Huaxin segments; stripped extract at `0x08000000`; app
   vector table at `0x08004000`.
3. Pattern player named: engine `+0x10 == 6` (CC21=7), TBH `0x08011a38`,
   `play_time_step` `0x08013e8c`. Pitch-gate (not `seq_step_gate` bit 7)
   is the note-emission check. `object+0x214` is an event table, not
   eight mode vtables.
4. Panel control IDs = Test-20 CCs. Shift held = RAM `0x200010d2`.
5. Checksums: Huaxin additive program + per-footer u16s. Always
   `led_codec.py retarget` before any future dump.

Daniel Gruss reverse-engineered the **original** KeyStep. Confirmed here:
hex-encoded `.led`, unsigned/unencrypted app, SysEx update, separate
bootloader. **KS37 checksums** are Huaxin/midiplus, not a 20-byte flat
header. The original KeyStep binary has zero content overlap.

## Future (not this phase)

Custom Thumb, when it happens, lives on unused fill at `0x0801F400`.
Earlier Euclidean (e0b/e1b/e3b) and scale-chord (C1/C2) images are
frozen experiments. Do not steal Shift+keys 1–16 (stock MIDI CH). A
later latch, if any, comes from empty cells in `stock-shift-map.md` §8
after the 1.1.6 model exists.

## Safety

Recoverable via stock update only if bootloader, app vector table at
`0x08004000`, and USB/MIDI stack stay intact:

- never write the bootloader (`0x08000000`–`0x08003FFF`, not in this `.led`)
- preserve the app vector table at `0x08004000`
- never modify the USB/MIDI stack or update path code
- keep future custom logic isolated in unused flash (`0x0801F400`)
- always keep an untouched stock firmware image for recovery
- do not write `0x0803B000` (on-device sequence slots)
- do not flash anything whose behaviour is not understood

See [`docs/firmware-safety-rules.md`](docs/firmware-safety-rules.md).

## Required validation order

1. ~~Reflash stock firmware unmodified.~~ **Done** — MCC Flash A.
2. ~~Trivial cosmetic patch.~~ **Done** — MCC Flash C (`0x0801F400[0]=FE`); Flash D restored stock.
3. Feature hear-test / Euclidean / chord. **Paused** (stage 3). Do not
   `cycle.sh --live` a feature image. Gate: `KS37_FEATURE_FLASH`.

## Protocol (done, live-verified)

- USB `1c75:0219` (app; sometimes `1c76:0219`), `1c75:0291` (bootloader). No DFU/HID.
- Bootloader transfer: Rec+Stop+Play (or MCC `productKey`) then `F0` +
  hex-ASCII `.led` slice + `F7`. App-mode `productKey` does not enter the
  updater — do not send it.
- App-mode GET uses the `arturia_v2` SysEx envelope.
- Pattern = Mode knob CC 21 value **7**. Occupancy CCs: [`stock-shift-map.md`](firmware-re/notes/stock-shift-map.md) §10.
- Arp ignores injected MIDI notes; physical keys only.

## Directory layout

- `docs/HANDOFF.md` — current status; read this first in a new session
- `docs/two-agent-protocol.md` — Cursor vs Claude file ownership (same repo)
- `AGENTS.md` / `CLAUDE.md` — pointers for both agents
- `firmware-re/notes/scans/` — **Cursor only** (binary dumps)
- `firmware-re/notes/model/` — **Claude only** (narratives + proposed catalog)
- `docs/firmware-safety-rules.md` — non-negotiable safety rules
- `docs/flash-checklist.md` — flash lab checklist (infrastructure)
- `docs/project-brief.md` — short goal statement
- `docs/environment-setup.md` — WSL toolchain, USB/MIDI, updater
- `scripts/flash-win.sh` — WSL → Windows `py.exe` `flash_win.py` (default dry-run)
- `scripts/flash_bl_wsl.sh` — **refuses** (ALSA stall)
- `scripts/keystep-see.sh` — confirm app mode (`0219`, Identity 1.1.6)
- `firmware-re/scripts/led_codec.py` — Huaxin parse / extract-flash / retarget
- `firmware-re/scripts/scan_firmware.py` — TBB / `bl-to` / cmp-imm on the extract
- `firmware-re/ghidra/recreate.py` — confirmed names only
- `firmware-re/notes/stock-shift-map.md` — panel occupancy + control IDs
- `firmware-re/notes/address-catalog.md` — flash VAs (P/S/H/X)
- `firmware-re/recovery/` / `og_firmware/` / `firmware-re/firmware-images/` — **gitignored** vendor `.led` / extract
- `firmware-re/patches/` / `build_patch.py` / E0–C2 images — **future** feature work
- `arturia_manual/` — official KeyStep 37 1.1 EN (PDFs gitignored)
- `.venv/` — capstone, mido, python-rtmidi, …

## Important note

This project is conservative. The current objective is to **understand
stock 1.1.6**. If a step cannot be verified, it is not flashed.

## Questions

This repo is the derived-notes side of the project — verified facts and
reasoning, not vendor material. A few things (factory/service-mode
details among them) are intentionally kept out of the public notes here.
If you're working on something similar and want more, DM me.
