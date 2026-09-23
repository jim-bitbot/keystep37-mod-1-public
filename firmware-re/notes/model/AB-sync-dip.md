STATUS: done
AGENT: claude
TICKET: AB
UPDATED: 2026-09-24T00:35+01:00
INPUT: firmware-re/notes/scans/AB-sync-dip.txt

# AB-sync-dip — broad search, honest negative on the DIP read itself

Read-only pass over `scans/AB-sync-dip.txt` only.

## 1. #0x13 immediate search — mostly noise, no Sync DIP read identified

66 hits for the literal `0x13`/`19` across the image. Sampling shows
the overwhelming majority are **unrelated uses** of the same numeric
value — loop bounds, struct field offsets (`[r4,#0x13]` appears
dozens of times across clearly-unrelated functions, e.g. `0x08011cec`
through `0x08011964`'s dense cluster, which per the surrounding context
is arp-engine/mode-table bookkeeping, not I/O), and instruction
encodings that happen to contain `0x13`. **None of the sampled hits
sit in a shape consistent with "read a GPIO input pin, compare against
a control ID."** **S** for the negative — this specific search method
(bare-immediate scan) doesn't surface the Sync DIP read, if one exists
as GPIO-level code at all.

## 2. GPIO base references — confirms pervasive use, not source-selection-specific

`0x40010800`(GPIOA)/`0x40010c00`(GPIOB)/`0x40011000`(GPIOC)/
`0x40011400`(GPIOD)/`0x40011800`(GPIOE) all show many references
(3-20 each) scattered across boot/init, key-scan, and LED code —
expected given this device's panel/key/LED hardware, not narrowed to
anything clock-source-specific. **S** — confirms GPIO is used
extensively, doesn't isolate the Sync DIP pin.

## 3. Three TIM2-adjacent leaves — all already known

`0x0800b0c6`/`0x0800b0ae`/`0x0800b2ae` fully match `T-clock.md`/
`Z-usbdin-emu.txt`'s (no relation — coincidental naming overlap since
Z reused one of these for a different lead) existing bodies exactly.
No new information. **S**, reconfirms only.

## Net — a real negative, needs a sharper search method

This ticket's search methodology (bare `#0x13` immediate scan, GPIO
base reference counting) was too broad to isolate a specific GPIO pin
read tied to clock-source selection — the signal is drowned in
unrelated `0x13`/GPIO uses elsewhere in the image. **Sync DIP source
selection remains unmapped**, consistent with `T-clock.md`'s own
conclusion that no software arbitration flag was found. A sharper
follow-up would search specifically for a GPIO **IDR** (input data
register, offset `+0x08` on any GPIO base) read followed by a
single-bit test, in a function reachable from boot/init — not
attempted by this ticket's method.

STATUS: done
