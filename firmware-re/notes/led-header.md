# `.led` container — KeyStep 37

## Encode / decode

The distributed file is uppercase hex-ASCII. Two characters = one payload byte.

```
1.1.6.579  234280 chars  →  117140 bytes
1.0.4.179  232208 chars  →  116104 bytes
```

Round-trip of 1.1.6.579 with uppercase hex is byte-identical to
`og_firmware/keystep37_Firmware_Update_1_1_6_579 (1).led`.

Wire transfer (already solved): each bootloader chunk is `F0` + a slice of
that hex-ASCII text + `F7`. No extra encoding.

`firmware-re/scripts/led_codec.py` implements decode / encode / inspect /
compare / roundtrip / retarget / extract-flash / mutate-test.

## Not a flat image

After hex-decode the file is a **Huaxin / midiplus (Gruss, auduchinok)
segment stream**, not Thumb starting at file offset 0. Each data record:

```
[18-byte big-endian header] [record_length bytes] [12-byte footer]
```

The last data record uses a **24-byte** footer (`footer[6] == 0x0D`).
`00 10 68 74` records are header-only and mean “fill the next 1 KiB of
flash with `0xFF`”.

Header unpack: `struct.Struct(">7sH7sH")` → `(p1, offset, p2, record_length)`.
`offset` is in **256-byte** units. First KS37 record is offset 64 →
**`0x08004000`**. Offsets then step by 4 (1 KiB pages) through
`0x0802FC00`. The 16 KiB below that is the on-device bootloader and is
**not** in this `.led`.

Both versions share the same first 18 header bytes
(`04 1C 68 74 DA 51 09 00 40 00 00 00 0A 00 00 00 04 00`). The old “20-byte
header” reading was those 18 bytes plus the first two payload bytes
(`00 C0` on both images) — not product magic of a flat container.

## The two content-tracking 16-bit fields

What used to be described as a 26-byte trailer is:

```
[last 2 bytes of last 1024-byte payload] [24-byte last footer]
```

On 1.1.6.579 that is `95c4` + `0b02fc0004000d02fc0000000e02fc0000000000000065fe`.
On 1.0.4.179: `8777` + `…c0fe`.

| Field | On-wire | Algorithm |
|---|---|---|
| Program checksum | last payload `[-2:]` (`95c4` / `8777`) | LE u16 = `(0x10000 - (sum(all segment payloads except those 2 bytes) & 0xFFFF))`. FF-fill records contribute `1024 × 0xFF`. |
| Last-segment checksum | last footer `[-2:]` (`65fe` / `c0fe`) | LE u16 = `(0x10000 - (sum(header[2:]) + sum(payload) + sum(footer[:-2])) & 0xFFFF)` |

Every non-fill footer uses that same per-segment formula (12-byte
footers on the earlier pages). `led_codec.py retarget` rewrites the
program u16 and **all** footer u16s. `mutate-test` flips one payload
byte on 1.1.6.579: `C495 → C494`, `FE65 → FE66`, verify OK.

MCC’s “Firmware file CRC error” is this additive Huaxin check, not a
CRC16/CRC32 polynomial. Do not use Gruss’s original-KeyStep 20-byte
flat-header recipe on this product.

## Flash extract

```
python3 firmware-re/scripts/led_codec.py extract-flash \
  "og_firmware/keystep37_Firmware_Update_1_1_6_579 (1).led" \
  firmware-re/firmware-images/keystep37_1.1.6.579_flash.bin
```

The extract is 196608 bytes with file offset 0 = `0x08000000`
(`0xFF` through `0x08003FFF`, app pages from `0x08004000`, last page
`0x0802FC00`, FF-fill `0x0801F400`–`0x0802FBFF` except the final page).

**Earlier notes that loaded the framed 117140-byte file at `0x08000000`
were using file offsets, not flash VAs.** Prefer the `*_flash.bin`
image for disassembly, unicorn, and Ghidra (`-loader-baseAddr 0x08000000`).

## Implication for a patch

Feature Thumb is already built this way (`build_patch.py` → page
`0x0801F400`). Rebuild path:

1. Decode hex-ASCII → framed bin, **or** edit the flash extract.
2. Patch Thumb in unused `0xFF` (the 66 KiB FF-fill at `0x0801F400`, or
   a hole inside a data page).
3. If editing the flash extract, cut 1 KiB pages back into the framed
   segments (offset 64 + 4n) and run `retarget`.
4. Encode uppercase hex-ASCII → `.led`.
5. Enter updater with Rec+Stop+Play (Hold/Shift alternate). Leave `0291`
   on Windows. Live send is `./scripts/flash-win.sh` → Windows
   `flash_win.py`, which imports this `led_codec.py`. Do not use
   `ks37_flash.py` / `flash_bl_wsl.sh`. Do not send app-mode `productKey`
   from WSL. Abort / recover with MCC + local
   `firmware-re/recovery/keystep37_1.1.6.579_stock.led` (clockwise LEDs).

12-byte data footers carry a BE24 flash offset at bytes `[1:4]`
(`0x004000` = `0x08004000`). `implant_page` must keep that field (or
write `flash_addr & 0xFFFFFF` when converting a fill). Copying the
page-0 footer onto a later page overwrites the vector table; Huaxin
u16s still verify. `verify` now fails that mismatch.
