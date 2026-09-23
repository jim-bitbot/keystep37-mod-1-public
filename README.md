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
are on disk and not modeled yet.

[`firmware-re/notes/findings-2026-09-20.md`](firmware-re/notes/findings-2026-09-20.md)
is a chronological lab log. Mid-file “not yet” paragraphs are stale;
prefer the catalog. `model/synthesis.md` still has a “Top open leads
(post Round-2)” list; treat the sections below as current.

## Coverage

App Thumb `0x08004000`–`0x0801F400` is about 109 KB. `recreate.py` names
roughly 85 function starts. The catalog has about 270 unique flash
addresses and 75 RAM addresses; about 30 rows are **P**, about 150 are
**S**. A C++ STM32 app this size usually has high-hundreds of functions,
so by count this is perhaps 10–15%. That is an order-of-magnitude guess,
not a measurement.

Function count undersells the hot path. Mapped end to end: boot and the
ctor sweep, the main loop and IRQs, the three input buses, the tick
object and tempo, the swing table, the 8-way mode TBH and its builders,
`play_time_step`, the step layout (8 voices × 2 bytes), the rest/tie
emission gate, the CC21 mapping, and the full panel occupancy. For
“clone a mode and change what it emits,” that is most of what matters.

As a map for adding one arp mode: perhaps two thirds of the way there.
The remaining gaps are a reliable step-gating model and a free gesture
to switch the mode. As a complete reading of the firmware: a small
fraction, and deliberately so.

## Deliberately out of scope

The bootloader (`0x08000000`–`0x08003FFF`), the USB stack body, and the
ST HAL were left alone for safety. That is about a fifth of the image
unexamined by design. It caps what “full” can mean.

## Still open

- The trigger that commits a RAM slot to flash
- Which GPIOD pin on `0x20004f00` is the sync jack and which is a DIP
  (Arturia’s docs say the rear DIP selects clock source and needs a
  reboot; the firmware object we have is the jack path)
- USB vs DIN identity on `0x20001d60` (DIN slot is confirmed; USB is a
  separate site)
- The family selector in `param_field_dispatch`
- About a dozen ctor objects that exist but have no role
- Case 5 of `seq_step_store`
- The hold-length-clear gesture (Shift+Oct−+Oct+)
- Named handlers for Shift secondaries — every Shift+key combo is
  taken, so a spare gesture for a new mode has to come from these
- Scans AT–BA: on disk, not modeled

The Shift-handler gap matters most if the goal is a new mode toggle.

The Euclidean hear-tests are a caution on the tick model. The same
flashed `e0b` image gave a steady 1,2,2, then ~90% every-step, then
3-in-8. The Walk/Pattern label swap explains some of that. Results that
change on one image also suggest a second entry into `play_time_step`
(EXTI0 → `0x08011ff0`) that is not pinned down. Get that reproducible
before trusting the tick model for a chord generator.

## Related work

These are host-side or family notes, not another 1.1.6 address catalog.

- [sysex-controls](https://github.com/soyersoyer/sysex-controls) — Linux
  MCC stand-in. KeyStep 37 pages use the same `0x41xx` global params as
  `KeyStep37.json`. It writes as well as reads. It does not dump
  sequencer banks.
- [midi-control, Arturia v2](https://docs.rs/midi-control/latest/midi_control/vendor/arturia/)
  — family verbs: `01` query, `02` = device report **and** host write.
  That is why there is no SET TBB. Ancestor:
  [untergeek on BeatStep](https://www.untergeek.de/2014/11/taming-arturias-beatstep-sysex-codes-for-programming-via-ipad/).
- [Arturia sync FAQ](https://support.arturia.com/hc/en-us/articles/4405748057618-KeyStep-37-General-Questions)
  — clock source is the rear DIP; reboot after a change.
- [Daniel Gruss, original KeyStep](https://dsgruss.github.io/notes/2020/10/02/keystep1.html)
  and [auduchinok’s 1.1.6 LED gist](https://gist.github.com/auduchinok/1dea3290af548be0a56767f9957fbadc)
  — Huaxin / octave-LED baseline used here.
- KeyStep 37 **mk2** manuals are a different product. Do not mix them
  into 1.1.6.

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

**Protocol.** App-mode GET is mapped. Host SET is Arturia v2 verb `02`
— the same `02 00 41 <id> <value>` shape as the GET reply. There is no
sibling SET TBB in the app.

**Persist.** Slot flash can be loaded into RAM. The STM32 `FLASH_KEYR`
unlock sequence is identified. The application trigger that *commits* a
slot is not.

**Clock / sync.** A four-pin GPIOD object (`0x20004f00`) is read through
IDR bit tests and can gate TIM2 disable and MIDI-Start. Arturia’s docs
say the rear DIP selects Internal / USB / MIDI / Sync In (reboot after
a change). Which of the four pins is the jack vs a DIP is still a
hypothesis.

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
