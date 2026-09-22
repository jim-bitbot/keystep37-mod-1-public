# Analysis recipes

Scripts in `firmware-re/scripts/` and `firmware-re/ghidra/`.
Current resume: [`docs/HANDOFF.md`](../../docs/HANDOFF.md).

Always analyze **`keystep37_1.1.6.579_flash.bin`** (base `0x08000000`).
Create it with:

```
python3 firmware-re/scripts/led_codec.py extract-flash \
  "og_firmware/keystep37_Firmware_Update_1_1_6_579 (1).led" \
  firmware-re/firmware-images/keystep37_1.1.6.579_flash.bin
```

Ghidra:

```
analyzeHeadless <project> <name> \
  -import firmware-re/firmware-images/keystep37_1.1.6.579_flash.bin \
  -processor "ARM:LE:32:Cortex" -loader BinaryLoader \
  -loader-baseAddr 0x08000000 \
  -postScript firmware-re/ghidra/recreate.py
```

If a decompile shows `unaff_r*` or exception-vector names, the entry is
wrong — walk branches from a real `push {…,lr}` and recreate the function.

`.led` checksums (both u16s):

```
python3 firmware-re/scripts/led_codec.py inspect "<file.led>"
python3 firmware-re/scripts/led_codec.py mutate-test "<file.led>"
python3 firmware-re/scripts/led_codec.py retarget <patched.bin> <out.bin>
```

Bounded unicorn:

```
python3 firmware-re/scripts/emulate_ks37.py all
python3 firmware-re/scripts/emulate_ks37.py play
python3 firmware-re/scripts/emulate_ks37.py euclid
```

Rebuild a feature image:

```
python3 firmware-re/scripts/build_patch.py e0   # or e1|e3|c1|c2
```

Device / hardware bootloader / listen:

```
./scripts/keystep-see.sh
# Jim: unplug, Rec+Stop+Play, plug USB (Hold/Shift alternate).
# AutoAttach off; 0291 stays on Windows. Then from WSL:
./scripts/flash-win.sh --already-bootloader --already-unlocked --confirm YES-FLASH \\
  /mnt/c/Users/jimcu/KeystepFlash/keystep37_1.1.6.579_stock.led
./scripts/wait_wsl_reattach.sh
./scripts/keystep-see.sh
python3 firmware-re/scripts/listen_ks37.py e0 --seconds 25
# then e1, e3-off, e3-on, c1 --scale major, c2
# e3 Shift+1/2 is stock MIDI CH — do not treat that as the latch.
```

Do not send app-mode `productKey` from WSL. MCC stock is recovery
(clockwise Hold/Shift/Oct chase). Packaging check:

```
./scripts/flash-win.sh --dry-run /mnt/c/Users/jimcu/KeystepFlash/keystep37_1.1.6.579_stock.led
```

Scanners (flash extract):

```
python3 firmware-re/scripts/scan_firmware.py stores-214
python3 firmware-re/scripts/scan_firmware.py tbb
python3 firmware-re/scripts/scan_firmware.py ptr-runs
python3 firmware-re/scripts/scan_firmware.py bl-to 0x08011794
```
