# Project Brief: KeyStep 37 custom firmware

## Goal

Add custom arp/chord behavior to the Arturia KeyStep 37 by patching the
stock application image, while keeping the USB/MIDI update path intact so
the device can always be restored.

The first feature is a Euclidean gate restripe (Pattern and Seq share
`play_time_step`) plus later scale-consistent chord. Thumb lives at
`0x0801F400`. Images are packaged. Enter updater with Rec+Stop+Play;
WSL `--already-bootloader`. Device is stock 1.1.6. Next: WSL stock
round-trip, then E0 + `listen_ks37.py e0`.
See [HANDOFF.md](HANDOFF.md) **Resume here**.

## What is already known

Authoritative detail lives in [HANDOFF.md](HANDOFF.md).
[../firmware-re/notes/findings-2026-09-20.md](../firmware-re/notes/findings-2026-09-20.md)
is the chronological evidence log — do not take mid-file “not yet
located” paragraphs as current.

Confirmed (flash VAs on the stripped extract — see [HANDOFF.md](HANDOFF.md)):

- Protocol (USB/MIDI, `arturia_v2` GET, bootloader `.led` transfer) is
  solved and live-verified.
- `.led` is hex-ASCII Huaxin segments. App loads at `0x08004000` (vector
  table + Reset `0x0801d311`). Bootloader is the 16 KiB below that.
- Pattern = Mode-knob CC 21 value `7` = engine `+0x10`. TBH `0x08011a38`
  case 7 → builder `0x08011c88`. Player `0x08013e8c` / `seq_step_note`
  `0x080130e8`. Do not hook `set_arp_mode` / TBH case 7.
- Chord interval is `voice+0x4f`; transpose is `0x200000C8`. Voice loop
  is generic poly on `+0x4d`. Stock extras do not snap to scale.
- Trailer u16s are Huaxin additive checksums (`led_codec.py retarget`).
- The Mode knob is 8-detent. A new visible 9th mode is not possible.

## Precedent, with a caution

Daniel Gruss reverse-engineered the **original** KeyStep. Useful and
confirmed here: hex-encoded `.led`, unsigned/unencrypted app image,
SysEx update, separate bootloader region.

**KS37 checksums are the Huaxin/midiplus segment scheme** (Gruss /
auduchinok), not a 20-byte flat header. Wire transfer still has no extra
CRC. The original KeyStep binary has zero content overlap.

## Safety and test order

See [firmware-safety-rules.md](firmware-safety-rules.md) and
[flash-checklist.md](flash-checklist.md).

1. Discovery needed to **design** a patch is done.
2. MCC Flash A (stock) → C (unused-page poke) → D (stock restore) done.
3. Feature images packaged and unicorn-tested. Live send is Rec+Stop+Play
   then WSL `--already-bootloader`. Never touch bootloader, USB/MIDI
   stack, or the update path. Do not write `0x0803B000`.

## Immediate work

Hardware Rec+Stop+Play, then `flash_bl_wsl.sh` with stock 1.1.6, then E0
+ `listen_ks37.py e0`. Abort = MCC stock. Then E1 → skip E2 → E3 → C1 → C2.
See [HANDOFF.md](HANDOFF.md) **Resume here**.
