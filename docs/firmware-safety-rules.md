# KeyStep 37 Firmware Safety Rules

These rules are for this device, from this project's own evidence. Do not
import checksum or vector-table assumptions from the original KeyStep.

## Non-negotiable rules

1. Never overwrite the bootloader region.
   - The update file starts at flash `0x08004000`. Bytes below that are
     the on-device bootloader and are not in this `.led`.
   - Do not write below `0x08004000`.

2. Preserve the **app** vector table at `0x08004000`.
   - SP `0x2000C000`, Reset `0x0801d311`. Do not treat Huaxin headers as
     a vector table. The framed `.led` decode is not a flat image.

3. Never modify the USB/MIDI stack or the stock update path.
   - That path is the only recovery method without opening the case.
   - Search the flash extract for USB `0x40005C00` literals and the GET
     handler `0x08005e84`. Framed-file names like `FUN_0800cc14` are
     obsolete.

4. Keep custom code isolated.
   - Place new logic in confirmed unused flash, with clean function
     boundaries. Do not patch unrelated blocks.

5. Do not flash an image whose packaging is not understood.
   - The bootloader-mode **wire** transfer has no extra CRC: each chunk is
     `F0` + a slice of the `.led` hex-ASCII text + `F7`.
   - The file itself uses Huaxin per-segment + program additive checksums.
     A modified image must go through `led_codec.py retarget` (or an
     equivalent rebuild of every footer u16 and the last-payload u16).

6. Maintain a stock firmware backup.
   - Keep an untouched vendor `.led` and use it as the first recovery
     action.

7. Validate in stages. Do not skip ahead.
   - Stage 1: stock firmware only — **done**
   - Stage 2: harmless cosmetic patch — **done** (MCC Flash C/D)
   - Stage 3: real feature work — **paused**. Current work is
     understanding 1.1.6. Do not flash Euclidean / chord images until
     the machine model exists.

8. Prefer reversible changes.
   - Do not patch a hot path until the exact edit location is verified
     against a **current-state** model of 1.1.6, not a mid-file findings
     paragraph.
   - If a change is not fully understood, do not flash it.

9. Treat the hardware as recoverable but not disposable.
   - A bad **application** flash can usually be corrected by reflashing
     stock, as long as the bootloader and USB/MIDI stack still run.
   - Permanent damage is only plausible if those are corrupted.

10. If in doubt, stop and verify.
    - No patch is worth a bricked device.

## Hard boundaries

Off-limits unless a verified flash map proves otherwise:

- bootloader flash region (not present in the `.led`)
- USB/MIDI stack and update-path code in the app image
- any region required to re-enter bootloader mode (product-key unlock,
  PID `1c75:0291` transfer)

## Recovery policy

1. Reflash the original stock `.led`.
2. Confirm the device enumerates as `1c75:0219` and still accepts updates.
3. Reassess the patch location and image packaging.
4. Only then retry.

## Decision rule

A patch may be flashed only when all of the following are true:

- flash layout (app start, image end, unused holes) is confirmed
- target region is unused or intentionally editable
- Huaxin program + footer checksums are recomputed (`led_codec.py retarget`)
- no protected region is touched
- a stock recovery image is available
