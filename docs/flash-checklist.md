# KeyStep 37 Flash Safety Checklist

Use this before every firmware attempt. Items marked known/unknown
reflect discovery status, not permission to skip them.

## Preflight

- [x] Stock firmware image is stored and verified. Vendor file in
      `og_firmware/`; frozen read-only copy at
      `firmware-re/recovery/keystep37_1.1.6.579_stock.led` (bit-identical).
- [x] Flash map: STM32F1 + GPIOE/TIM8/USB, sequence slots at
      `0x0803B000+n*0x800` ⇒ ≥256KB (likely F103VC). App at
      `0x08004000`–`0x08030000` in the extract. See `firmware-re/notes/flash-map.md`.
- [x] Bootloader is `0x08000000`–`0x08003FFF` (not in the `.led`).
      Do not write there. Sequence slots `0x0803B000+` are on-device only.
- [x] Preserve the app vector table at `0x08004000`.
- [x] USB/MIDI update path is known at the wire level (`productKey` then
      raw `.led` hex-ASCII chunks to PID `1c75:0291`). App-side ranges:
      `firmware-re/notes/flash-map.md` and `address-catalog.md`.
- [x] Recovery path to stock firmware is tested: MCC stock 1.1.6.579
      (Flash A and Flash D, 2026-09-20). Flash C (noop via MCC) also
      returned to `1c75:0219`. WSL/winmm app-mode `productKey` does not
      enter the updater. Enter with Rec+Stop+Play, then
      `ks37_flash.py --already-bootloader`. MCC stock is recovery.

## Binary preparation

- [x] `.led` is hex-ASCII Huaxin segments. Analyze
      `keystep37_1.1.6.579_flash.bin` at base `0x08000000`.
- [x] Binary has been disassembled (Ghidra / capstone).
- [x] Unused bytes: FF-fill `0x0801F400`–`0x0802FBFF` (66 KiB). Last page
      `0x0802FC00` holds the program checksum — leave it.
- [x] First live patch target is unused FF-fill `0x0801F400` (never
      executed). Last page `0x0802FC00` left alone. `implant-page` converts
      that fill record to a real 1 KiB page (`FF→FE` at byte 0).
- [x] Trailer u16s (`95c4` / `65fe` on 1.1.6.579) are Huaxin additive
      checksums. Recompute with `led_codec.py retarget` before any flash.

## Patch validation

- [x] No write occurs below the application boundary.
      E0–C2 only touch `0x0801F400` plus the named `bl` sites in app code.
- [x] No USB/MIDI stack code is altered.
      GET / `productKey` / Huaxin path untouched. MIDI CH stays MCC.
- [x] New code is isolated in a specific unused region.
      One 1 KiB page at `0x0801F400` (`ks37_patch.S`). Last page `0x0802FC00` left to `retarget`.
- [x] The change is small enough to reason about and validate.
      Flash C (MCC) wrote one unused byte at `0x0801F400`; D restored stock.
      Feature images unicorn-tested (`emulate_ks37.py euclid`). First E0
      MCC try stuck on `0291` and was stock-recovered. Next proof is WSL
      `--already-bootloader` (stock, then `listen_ks37.py e0`).

## Flash attempt

- [ ] Device is connected in a stable state.
- [ ] USB update path is the only method used (no SWD; case stays closed).
- [x] Vendor firmware recovery file is available
      (`firmware-re/recovery/keystep37_1.1.6.579_stock.led`).
- [x] Image packaging is valid (round-trip + `mutate-test` +
      decode/retarget/encode bit-identical to vendor).
- [ ] No power interruption or disconnect occurs during write.

## After flash

Per-attempt boxes. Flash C/D already proved enumeration + stock restore.
WSL `--already-bootloader` and E0 MIDI proof are still open.

- [ ] Device boots and enumerates as `1c75:0219`.
- [ ] MIDI/USB update path still functions.
- [ ] The custom behavior matches expectation (`listen_ks37.py e0` → IOI 3,3,2).
- [x] A stock recovery flash is immediately available
      (`firmware-re/recovery/keystep37_1.1.6.579_stock.led`).

## Recovery action

1. MCC-reflash the original stock `.led` (or Rec+Stop+Play +
   `flash_bl_wsl.sh` stock). Do not send app-mode `productKey` from WSL.
2. Confirm the firmware update path still works (`1c75:0219`, Identity 1.1.6).
3. Re-examine the patch region and header/packaging logic.
4. Resume only after the root cause is understood.

## Default rule

Packaging, flash map, and unused-page isolation are confirmed. Unchecked
items above are **per attempt** (device stable, no disconnect) and
**after flash** (WSL send + E0 hear-test). If a preflight or binary-prep
item becomes uncertain again, do not flash.
