# Analysis recipes

Scripts in `firmware-re/scripts/` and `firmware-re/ghidra/`.
**Current work:** understand stock 1.1.6.579 — see
[`docs/HANDOFF.md`](../../docs/HANDOFF.md) and
[`docs/two-agent-protocol.md`](../../docs/two-agent-protocol.md).
Cursor dumps go in `firmware-re/notes/scans/`. Claude prose in
`firmware-re/notes/model/`. Do not both edit the catalog.
[`docs/ARTURIA-FIRMWARE-RE-GUIDE.md`](../../docs/ARTURIA-FIRMWARE-RE-GUIDE.md).
Do not `build_patch.py` / live-flash Euclidean or chord images in this
phase.

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

`.led` checksums (both u16s) — infrastructure, not current feature work:

```
python3 firmware-re/scripts/led_codec.py inspect "<file.led>"
python3 firmware-re/scripts/led_codec.py mutate-test "<file.led>"
python3 firmware-re/scripts/led_codec.py retarget <patched.bin> <out.bin>
```

Bounded unicorn (`all` leftover FLAG FAIL is a warning until BSS-init;
`euclid` leftover FAIL is fatal):

```
python3 firmware-re/scripts/emulate_ks37.py all
python3 firmware-re/scripts/emulate_ks37.py play
```

Scanners (flash extract) — **this phase**:

```
python3 firmware-re/scripts/scan_firmware.py stores-214
python3 firmware-re/scripts/scan_firmware.py tbb
python3 firmware-re/scripts/scan_firmware.py ptr-runs
python3 firmware-re/scripts/scan_firmware.py bl-to 0x08011794
python3 firmware-re/scripts/scan_firmware.py cmp-imm
```

Device / hardware (restore stock only unless Jim says otherwise):

```
./scripts/keystep-see.sh
# dump: unplug, Rec+Stop+Play, plug USB (Hold/Shift alternate).
# AutoAttach off; 0291 stays on Windows. Then from WSL:
./scripts/flash-win.sh --already-bootloader --already-unlocked --confirm YES-FLASH \\
  /mnt/c/Users/jimcu/KeystepFlash/keystep37_1.1.6.579_stock.led
./scripts/wait_wsl_reattach.sh
./scripts/keystep-see.sh
```

Do not send app-mode `productKey` from WSL. MCC stock is recovery
(clockwise Hold/Shift/Oct chase). Packaging check:

```
./scripts/flash-win.sh --dry-run /mnt/c/Users/jimcu/KeystepFlash/keystep37_1.1.6.579_stock.led
```

**Future** (refused unless `KS37_FEATURE_FLASH=YES-FEATURE-FLASH`):
`build_patch.py e0|e1|e3|c1|c2`, `listen_ks37.py e0|e1|e3-off|c1|c2`,
feature-level `cycle.sh` / `--live`.
