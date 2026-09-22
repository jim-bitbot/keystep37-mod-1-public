# WSL Environment Setup

## What's installed

System packages: `alsa-utils`, `binwalk`, `xxd`, `bsdextrautils` (provides `hexdump`
— the old `hexdump` apt package no longer exists), `radare2`, `gcc-arm-none-eabi`,
`binutils-arm-none-eabi`, `gdb-multiarch`, `openocd`, `stlink-tools`, `dfu-util`,
`openjdk-21-jdk`, `wireshark-common`, `tshark`, `usbutils`, `libasound2-dev`.

Python packages live in the project venv, not system-wide (this Ubuntu release
enforces PEP 668 — `pip install` at the system level is blocked):

```
source .venv/bin/activate
```

Contains: mido, python-rtmidi, capstone, intelhex, pyserial, pillow.

External tools in `~/tools/`:
- `ghidra_12.1.3_PUBLIC/ghidraRun` — disassembler/decompiler
- `cutter.AppImage` — radare2 GUI (runs directly, no FUSE issues on this WSL setup)

## USB/MIDI passthrough — auto-attach configured on the Windows side

WSL2 has no direct USB access — the KeyStep 37 has to be attached from the
Windows host. **App-mode listen** uses AutoAttach. **A firmware dump
does the opposite:** stop `KeystepAutoAttach-USBIP` and leave `0291` on
Windows — do not `usbipd attach --wsl` the updater. If the KeyStep is
ever *not* showing up for listen, fall back to the manual steps below.

**Manual fallback, in an elevated (Administrator) PowerShell on Windows:**
```powershell
usbipd list
usbipd attach --wsl --busid <BUSID>
```
(`<BUSID>` is whatever `usbipd list` shows next to `1c75:0219` or
`1c76:0219` for app, or `1c75:0291` for updater.
Run `bind` first instead of `attach` only if state isn't already "Shared".
Do **not** attach `0291` to WSL when dumping — that is the ALSA stall.)

To restore auto-attach if it stops working:
```powershell
usbipd attach --wsl --busid <BUSID> --auto-attach
```
left running (originally wrapped in a Windows Scheduled Task at logon so it
starts automatically — check Task Scheduler on Windows if auto-attach isn't
working and this needs re-creating).

**Bind the app personality for listen.** After Rec+Stop+Play the KeyStep
leaves `1c75:0219` (sometimes `1c76:0219`) and re-enumerates as updater
`1c75:0291`. Match **PID**, not the product string. AutoAttach that only
knows `1c75:0219` will miss the `1c76` VID quirk.

For **listen**, attach app mode to WSL. For a **dump**, bind is fine but
do **not** attach `0291` to WSL:

```powershell
usbipd list
usbipd bind --busid <BUSID_0219>
usbipd attach --wsl --busid <BUSID_0219> --auto-attach
# dump: Stop-ScheduledTask KeystepAutoAttach-USBIP; leave 0291 Shared
```

## Updater entry (two LED patterns)

Both are firmware-update modes. Neither is factory reset (Oct−+Oct+
until the display shows `rST`).

| Entry | LEDs | How |
|---|---|---|
| Hardware force-update | Hold and Shift alternate | Unplug, hold Rec+Stop+Play, plug USB (no hub) |
| MCC software-update | Hold, Shift, Oct+, Oct− clockwise | MCC `productKey` |

Do **not** send app-mode `productKey` from WSL — it does not enter the
updater. Do **not** attach `0291` to WSL for a dump (ALSA stream stalls).
Stop AutoAttach, leave the updater on Windows, then from WSL:

```
./scripts/flash-win.sh --dry-run
# live restore stock only, after Rec+Stop+Play, AutoAttach off:
./scripts/flash-win.sh --already-bootloader --already-unlocked --confirm YES-FLASH \\
  /mnt/c/Users/jimcu/KeystepFlash/keystep37_1.1.6.579_stock.led
```

`flash_bl_wsl.sh` refuses. MCC is recovery only. Detach to Windows first
if using MCC — never `usbipd detach` a live `0291` (unplug instead).

**Current work is static analysis of 1.1.6**, not occupancy or feature
flash. Occupancy map is done:
[`firmware-re/notes/stock-shift-map.md`](../firmware-re/notes/stock-shift-map.md).
`./scripts/cycle.sh` remains unicorn + dry-run. Leftover FLAG FAIL is
non-fatal for `emulate all` (fatal for `emulate_ks37.py euclid` until a
**future** BSS-init). Do not `--live` feature images.

Watch app-mode restore from WSL after a dump (physical unplug/replug,
then AutoAttach if you want listen):

```
./scripts/wait_wsl_reattach.sh
./scripts/keystep-see.sh
```

**From WSL, verify with one command:**
```
./scripts/keystep-see.sh
```
(`keystep-check.sh` is the same script.) App: `0219`, ALSA, `amidi`,
MIDI Identity (`00 20 6B` / `00 06 01 01`), and one GET. Bootloader:
`0291` + any `hw:` rawmidi → ready for `--already-bootloader`.

## Known permanent limitations

- **No `snd_seq` module in this WSL2 kernel.** Microsoft's WSL2 kernel
  doesn't build ALSA sequencer support, so `aconnect` and anything relying
  on `/dev/snd/seq` will never work here — this is a kernel limitation, not
  fixable via `apt`/`modprobe`. Not a blocker: `amidi` talks to the rawmidi
  device (`/dev/snd/midiC0D0`, port `hw:0,0,0`) directly and doesn't need
  the sequencer. Raw SysEx/MIDI work should go through `amidi` or the
  `mido`/`python-rtmidi` venv (ALSA rawmidi backend, confirmed working).
- **Group membership for `/dev/snd/*` access** (`audio`, `plugdev`) is
  already set permanently in `/etc/group` for this user — persists across
  reboots. It only needs to be *active in the current shell*, which
  requires one fresh login per WSL session (a brand new WSL terminal, or
  `wsl --shutdown` + reopen from Windows, picks it up automatically). Until
  then, MIDI commands need `sudo`.
- **No USB-DFU interface on the KeyStep 37 itself** — confirmed from the
  USB descriptor dump (`firmware-re/descriptors/lsusb_verbose_dump.txt`):
  only two interfaces, both USB Audio class (AudioControl + MIDIStreaming),
  no DFU class interface. `dfu-util` has nothing to talk to over this same
  USB link — SWD is the only flashing fallback for this device, not
  `dfu-util`.

## Quick reference

| What | Value |
|---|---|
| VID:PID (app) | `1c75:0219` |
| VID:PID (updater) | `1c75:0291` (name may be Updater / MiniLab / UNKNOWN) |
| Hardware updater | Rec+Stop+Play on plug — Hold/Shift alternate |
| MCC updater | `productKey` — Hold/Shift/Oct clockwise |
| ALSA card (app) | `A37` — "Arturia KeyStep 37" |
| MIDI port | `hw:0,0,0` (any `hw:` in updater) |
| Cycle | `./scripts/cycle.sh` (unicorn then dry-run; **no `--live`** this phase) |
| Occupancy | **Done.** `firmware-re/notes/stock-shift-map.md` |
| Live flash | `./scripts/flash-win.sh` (infrastructure; default dry-run). Feature images = **future** |
| Recovery `.led` | `firmware-re/recovery/keystep37_1.1.6.579_stock.led` |
| Descriptor dump | `firmware-re/descriptors/lsusb_verbose_dump.txt` |
| Sample MIDI capture | `captures/keystep_midi_test_20260920.txt` |
| Current status | `docs/HANDOFF.md` |
| Reverse-engineering findings | `firmware-re/notes/findings-2026-09-20.md` |
