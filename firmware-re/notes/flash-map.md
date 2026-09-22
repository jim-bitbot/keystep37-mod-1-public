# Flash / MCU map — KeyStep 37

## Part

Confirmed STM32F1 map from literals in the **stripped** image:

- `0x40010800` GPIOA … **`0x40011800` GPIOE**
- `0x40005C00` USB FS, `0x40013800` USART1
- **`0x40013C00` TIM8**
- SRAM used through `0x20005eac` (`.bss` end in Reset_Handler)

GPIOE + TIM8 + USB ⇒ **STM32F103Vx** high-density. Sequence slots
`0x0803B000 + n*0x800` need **≥256KB**. Best fit: **STM32F103VC**.

## How the `.led` lands on flash

Huaxin records: `offset` is in 256-byte units. First data record is
offset 64 → **`0x08004000`**. Pages are 1 KiB (offset += 4).

```
0x08000000  bootloader (NOT in this .led; 16 KiB erased in the extract)
0x08004000  app vector table (SP 0x2000C000, Reset 0x0801d311)
0x08004014  Thumb-2 application
…
0x0801F400  FF-fill records (66 × 1 KiB) through 0x0802FBFF
0x0802FC00  last data page (1022 × 0xFF + program checksum u16)
0x08030000  end of extract

            (on-device only — not in the .led)
0x0803B000  sequence slot 0 (2KB)
…           step 0x800
0x0803E800  slot 7
```

`.data` copy (Reset_Handler `0x0801d310`): flash `0x0801ef78` → RAM
`0x20000000`–`0x200001f4`. `.bss` `0x200001f8`–`0x20005eac`.

## Holes a future patch may use

- **Preferred:** `0x0801F400`–`0x0802FBFF` (66 KiB of `0xFF` from
  fill records). After a patch, `led_codec.py retarget` must rebuild
  program + per-segment checksums. Replacing a fill header with a real
  1 KiB data record is the clean way to place new Thumb there.
- Last page `0x0802FC00` is **not** free: its final two bytes are the
  program checksum.
- The 16 KiB below `0x08004000` is bootloader. Off-limits.

## Off-limits

- Vector table `0x08004000`–`0x0800403F` and Reset_Handler / `.data` copy
- USB register uses and SysEx GET / receive
- Huaxin headers/footers (edit via `led_codec`, not by hand)
- Sequence flash `0x0803B000`–`0x0803EFFF`

## Ghidra

```
analyzeHeadless <project> <name> \
  -import firmware-re/firmware-images/keystep37_1.1.6.579_flash.bin \
  -processor "ARM:LE:32:Cortex" -loader BinaryLoader \
  -loader-baseAddr 0x08000000 \
  -postScript firmware-re/ghidra/recreate.py
```
