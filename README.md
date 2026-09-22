# Arturia KeyStep 37 Custom Firmware Project

**Read first:** [`docs/HANDOFF.md`](docs/HANDOFF.md). Addresses:
[`firmware-re/notes/address-catalog.md`](firmware-re/notes/address-catalog.md).
Packaging: [`firmware-re/notes/led-header.md`](firmware-re/notes/led-header.md).
MCU / holes: [`firmware-re/notes/flash-map.md`](firmware-re/notes/flash-map.md).
Evidence log: [`firmware-re/notes/findings-2026-09-20.md`](firmware-re/notes/findings-2026-09-20.md)
(chronological; mid-file “not yet located” paragraphs are stale).

## Objective

Add Euclidean-rhythm gates (then scale-consistent chord) to the stock
KeyStep 37 Pattern/Seq player, while keeping the USB/MIDI update path
intact so the device can always be restored.

This is not a fresh rewrite and not a 9th Mode-knob detent (the knob is
8-position). Custom Thumb lives on one unused page at `0x0801F400`.
Pitches stay; gates are rewritten. Seq and Pattern share `play_time_step`
/ `seq_step_gate`, so one hook covers both.

## Status (2026-09-22)

Device is **e3b** (re-dumped the same image as a sender test). e0b hear-test
PASS 3-in-8; e1b k=n OK-ish; e3b Euclidean-on works, latch-off unproven
(Shift+C/C♯ is stock MIDI CH — see `firmware-re/notes/stock-shift-map.md`).

Enter the updater with **Rec+Stop+Play** on plug (Hold/Shift alternate).
Device stays on **Windows** (stop AutoAttach; do not attach `0291` to WSL).
From this repo:

```
./scripts/flash-win.sh --dry-run
./scripts/flash-win.sh --already-bootloader --already-unlocked --confirm YES-FLASH \\
  /mnt/c/Users/jimcu/KeystepFlash/<file>.led
```

That shells out to Windows `flash_win.py`, which imports this repo’s
`led_codec.py`. Do **not** use `flash_bl_wsl.sh` (ALSA stall; script now
refuses). Images live in `C:\Users\jimcu\KeystepFlash\` and local
`og_firmware/` / `firmware-re/recovery/` — **not in git**. MCC is recovery
only. Factory reset is Oct−+Oct+ / display `rST`.

**Next:** novel latch gesture (not Shift+keys 1–16). Details in HANDOFF.

## Core technical direction

1. ~~Download and validate the stock KeyStep 37 firmware from Arturia.~~ **Done** — `og_firmware/`.
2. ~~Decode the `.led` payload and map flash.~~ **Done** — Huaxin segments; stripped extract at `0x08000000`; app vector table at `0x08004000`.
3. ~~Identify Pattern generator and chord hook.~~ **Done** — engine `+0x10 == 7`, TBH `0x08011a38` case 7 → `0x08011c88`; player `0x08013e8c` / `seq_step_gate`; chord interval `voice+0x4f`. Do **not** hook `set_arp_mode` / TBH case 7. `object+0x214` is an event-handler table, not eight mode vtables.
4. ~~New Mode-knob ID.~~ **Withdrawn.** Keep Pattern/Seq; rewrite gates only.
5. Euclidean restripe. **Packaged** (E0 always-on 3-in-8, E1 hits-from-slot, E3 Shift latch). Unicorn PASS. Live MIDI hear-test remaining.
6. Scale-consistent chord. **Packaged** (C1 snap after `noteval`, C2 Shift+Type flavour). Stock extras do not snap.
7. ~~Understand `.led` checksums before flash.~~ **Done** — Huaxin additive program + per-footer u16s. Always `led_codec.py retarget`.

## Use of reference material

Daniel Gruss reverse-engineered the **original** KeyStep. Confirmed to
also apply here: hex-encoded `.led`, unsigned/unencrypted app image,
SysEx update, separate bootloader region.

**KS37 file checksums** are the Huaxin/midiplus segment scheme
(`led_codec.py`). The wire transfer itself has no extra CRC. The
original KeyStep binary has zero content overlap. See
`docs/firmware-safety-rules.md`.

## Safety philosophy

The device is recoverable via the stock firmware update path, but only if the bootloader, app vector table at `0x08004000`, and USB/MIDI stack remain intact. This project treats the following as non-negotiable:

- never write the bootloader (`0x08000000`–`0x08003FFF`, not in this `.led`)
- preserve the app vector table at `0x08004000`
- never modify the USB/MIDI stack or update path code
- keep all custom logic isolated in unused flash space with clean boundaries (`0x0801F400`)
- always keep an untouched stock firmware image on hand for recovery
- validate the update pipeline in stages before making behavioral changes
- do not write `0x0803B000` (on-device sequence slots)

## Required validation order

1. ~~Reflash stock firmware unmodified.~~ **Done** — MCC Flash A.
2. ~~Trivial cosmetic patch.~~ **Done** — MCC Flash C (`0x0801F400[0]=FE`); Flash D restored stock.
3. Euclidean / chord feature. **e0b live.** Send with Rec+Stop+Play then
   `./scripts/flash-win.sh` (Windows winmm). Do not attach `0291` to WSL.

## Protocol (done, live-verified)

Full trail: `firmware-re/notes/findings-2026-09-20.md`. Highlights:

- USB `1c75:0219` (app), `1c75:0291` (bootloader). No DFU/HID.
- Bootloader transfer: hardware Rec+Stop+Play (or MCC `productKey`) then
  `F0` + hex-ASCII `.led` slice + `F7`. No extra wire CRC. App-mode
  WSL/winmm `productKey` does not enter the updater — do not send it.
- App-mode GET uses the `arturia_v2` SysEx envelope (session bytes, checksum, 7-in-8 packing).
- Pattern = Mode knob CC 21 value **7**. Chord knobs CC 98/99/100/101.
- Arp ignores injected MIDI notes; physical keys only.

The old claim that framed-file `0x0800af84` is the 8-arp-mode dispatch is
**withdrawn** (file offset, not flash; and it is a 10-way message TBB).

## Directory layout

- `docs/HANDOFF.md` — current status; read this first in a new session
- `docs/firmware-safety-rules.md` — non-negotiable safety rules and recovery policy
- `docs/flash-checklist.md` — step-by-step validation and reflashing checklist
- `docs/project-brief.md` — short goal statement; defers to HANDOFF
- `docs/environment-setup.md` — WSL toolchain, USB/MIDI passthrough, Rec+Stop+Play updater
- `scripts/keystep-see.sh` — confirm stock / app mode (`0219`, Identity 1.1.6); 0291-ready print
- `scripts/flash-win.sh` — WSL → Windows `py.exe` `flash_win.py` (default dry-run; parser is `led_codec.py`)
- `scripts/flash_bl_wsl.sh` — **refuses** (ALSA stall); use `flash-win.sh`
- `scripts/attach_bootloader.sh` — **do not** attach `0291` to WSL for a dump
- `scripts/wait_mcc_stock.sh` / `scripts/wait_wsl_reattach.sh` — watch MCC restore and WSL reattach
- `scripts/flash_euclid_mcc.sh` — MCC fallback (`e0`…`c2`)
- `firmware-re/scripts/listen_ks37.py` — MIDI hear-test (`e0`, `e1`, `e3-off`, `e3-on`, `c1`, `c2`)
- `firmware-re/scripts/build_patch.py` — rebuild E0–C2 from `patches/ks37_patch.S` into KeystepFlash
- `firmware-re/recovery/` / `og_firmware/` / `firmware-re/firmware-images/` — **local only, gitignored** vendor `.led` / flash extracts
- `captures/` — saved MIDI/SysEx captures (pcap firmware dumps are gitignored)
- `firmware-re/notes/` — address catalog, flash map, `.led` notes, chronological findings
- `firmware-re/descriptors/` — USB descriptor dumps
- `midi_control_centre_analysis/` — first-pass MCC binary / resource analysis
- `arturia_manual/` — official KeyStep 37 user manual (PDFs gitignored)
- `.venv/` — Python virtualenv (mido, python-rtmidi, capstone, intelhex, pyserial, pillow)

## Important note

This project is intentionally conservative. The objective is to add a feature without risking permanent hardware damage. If a step cannot be verified, it is not attempted.
