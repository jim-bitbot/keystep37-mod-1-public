# KeyStep 37 — firmware 1.1.6 notes

Derived reverse-engineering notes for the stock Arturia KeyStep 37
**application** firmware 1.1.6.579. Not Arturia’s firmware, not a
replacement image, and not something you flash from this repo.
The notes and scripts here are [MIT](LICENSE); Arturia’s firmware
is not.

Vendor `.led` files, the stripped flash extract, official manuals, and
update captures are **not published**. They stay local (see
[`.gitignore`](.gitignore)). Everything here is addresses, dumps,
narratives, and tools that operate on a copy you already have.

If you came here for a custom firmware: there isn’t one.

## Start here

| File | What it is |
|---|---|
| [`firmware-re/notes/address-catalog.md`](firmware-re/notes/address-catalog.md) | Named flash/RAM addresses. This is the map. |
| [`firmware-re/notes/stock-shift-map.md`](firmware-re/notes/stock-shift-map.md) | Every panel gesture and its Test-20 control ID. |
| [`firmware-re/notes/scans/tickets.md`](firmware-re/notes/scans/tickets.md) | Ticket list A–BA and what each one asked. |
| [`firmware-re/notes/flash-map.md`](firmware-re/notes/flash-map.md) | MCU, app range, unused fill. |
| [`firmware-re/notes/led-header.md`](firmware-re/notes/led-header.md) | How a `.led` is framed (Huaxin segments + checksums). |
| [`docs/ARTURIA-FIRMWARE-RE-GUIDE.md`](docs/ARTURIA-FIRMWARE-RE-GUIDE.md) | How the notes were built (wire constant → `cmp` → callers). |

Catalog tags:

- **P** — live protocol or occupancy ID matches an immediate in code
- **S** — structure from disassembly or Unicorn
- **H** — hypothesis (including claims not re-traced here)
- **X** — ruled out

A ticket is a scan dump plus a model write-up. Scans live in
[`firmware-re/notes/scans/`](firmware-re/notes/scans/). Narratives and
proposed catalog rows live in
[`firmware-re/notes/model/`](firmware-re/notes/model/). The catalog is
the accepted subset.

Tickets **A–AS** are modeled and copied into the catalog. Scans **AT–BA**
are on disk and not modeled yet. The USB stack body and the bootloader
(`0x08000000`–`0x08003FFF`) were left alone on purpose.

[`firmware-re/notes/findings-2026-09-20.md`](firmware-re/notes/findings-2026-09-20.md)
is a chronological lab log. Mid-file “not yet” paragraphs are stale;
prefer the catalog.

## What the application looks like

STM32F1. Image base `0x08000000`. App Thumb `0x08004000`–`0x0801F400`.
Addresses in the catalog are **flash VAs** on the stripped extract, not
file offsets into a framed `.led`.

**Boot.** `Reset_Handler` copies `.data`, zeros `.bss` through
`0x20005eac`, then a ctor sweep builds on the order of fifty objects
(knobs, tick, ports, debounce, sequence blocks).

**Loop and IRQs.** One forever loop. SysTick, TIM2, USART1 (DIN MIDI),
a USB ISR thunk, and EXTI0 (GPIOD pulse into the step/play path). TIM2
does not itself walk the tick object.

**Three input buses.**

- Keys go through `0x0801b750`.
- Buttons use a compact ID table (`Hold/Shift/Oct−/Oct+/Tap/Rec/Stop/Play`,
  else Chord). Shift held is RAM `0x200010d2`.
- Analog kinds 1–4 map to Type / Notes / Vel / Strum (`0x62`–`0x65`);
  kind 0 and ≥5 map to Rate (`0x66`).

**Time.** Tick object `0x20002bec`: step at `+0x38`, length at `+0x10`,
tempo halfword at `+0xe` (clamped 3000–24000, then TIM2 ARR). Time Div
is a byte on `0x20001000`. Swing values are a nine-byte flash table at
`0x0801ec64`; the panel write lands at sequence-slot `+0x401`.

**Voice out.** A step plays only if voice-0 pitch is not a rest/tie
(`0x81`/`0x82`) — that check is the emission gate, not `seq_step_gate`
bit 7 (retention). Key notes leave on DIN via USART1. USB MIDI out is a
separate call site, not a slot on the DIN/display object. Pattern mode
is engine `+0x10 == 6` (panel CC 21 = 7).

**Protocol.** App-mode GET is mapped. There is no sibling SET TBB;
writes are the panel/knob paths already in the catalog.

**Persist.** Slot flash can be loaded into RAM. The STM32 `FLASH_KEYR`
unlock sequence is identified. The application trigger that *commits* a
slot is not.

**Clock / sync.** A four-pin GPIOD object (`0x20004f00`) is read through
IDR bit tests and can gate TIM2 disable and MIDI-Start. Which pin is
the jack vs a DIP is still a hypothesis.

**Panel occupancy.** Shift+keys 1–16 are Keyboard MIDI channel, not
free. Shift+Tap is tempo. Chord-then-Rec lights Rec. The map is
[`stock-shift-map.md`](firmware-re/notes/stock-shift-map.md).

Ghidra names for confirmed **function starts** only:
[`firmware-re/ghidra/recreate.py`](firmware-re/ghidra/recreate.py).

## What’s in the tree

```
firmware-re/notes/address-catalog.md   accepted addresses
firmware-re/notes/scans/               raw Capstone dumps (A–BA)
firmware-re/notes/model/               narratives + proposed rows (A–AS)
firmware-re/notes/stock-shift-map.md   panel occupancy
firmware-re/ghidra/recreate.py         Ghidra name script
firmware-re/scripts/scan_firmware.py   TBB / bl-to / cmp-imm
firmware-re/scripts/led_codec.py       .led parse / extract / retarget
firmware-re/scripts/emulate_ks37.py    Unicorn harness
firmware-re/captures/                  occupancy + listen logs
docs/                                  method, safety, lab setup
midi_control_centre_analysis/          notes on MCC (no vendor exe)
```

Scripts under `scripts/` and `firmware-re/scripts/` are the lab
wrappers (scan, listen, flash-from-Windows, occupancy). They expect a
local extract and a device. Default flash is dry-run.

[`firmware-re/patches/`](firmware-re/patches/) is leftover source from
an earlier Euclidean / scale-chord experiment. It is not a supported
build in this repo, and the `.led` images are not checked in.

## If you have the extract

```
# image: firmware-re/firmware-images/keystep37_1.1.6.579_flash.bin
# file offset 0 = 0x08000000

python3 firmware-re/scripts/scan_firmware.py
```

Ghidra: import that bin as `ARM:LE:32:Cortex` at `0x08000000`, then run
`recreate.py` as a post-script.

`.led` packaging (checksums, extract, retarget) is
`firmware-re/scripts/led_codec.py`. Always retarget after you edit a
framed image.

## Safety

This repo does not ship a firmware image. If you work on a device
anyway: do not write the bootloader, the app vector table at
`0x08004000`, the USB/MIDI stack, or sequence-slot flash at
`0x0803B000`. Keep an untouched stock `.led` for recovery. Details:
[`docs/firmware-safety-rules.md`](docs/firmware-safety-rules.md).

Daniel Gruss reverse-engineered the original KeyStep. Confirmed here:
hex-encoded `.led`, unsigned app, SysEx update, separate bootloader.
KeyStep 37 checksums are the Huaxin/midiplus segment scheme, not a
20-byte flat header. The two binaries do not overlap.

## License

Notes, scripts, and other files in this repository are [MIT](LICENSE)
(Copyright 2026 Jim Curlis). Keep the copyright and permission notice
with copies.

That license covers **this** work only. It does not grant rights in
Arturia’s firmware, trademarks, manuals, MIDI Control Center, or any
`.led` / flash extract you obtain yourself. Those stay with their
owners and are not published here.

## Questions

A few things (factory / service-mode details among them) are kept out of
these public notes on purpose. If you’re working on something similar
and want more, DM me.
