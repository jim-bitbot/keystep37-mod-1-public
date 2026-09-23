STATUS: done
AGENT: claude
TICKET: Z
UPDATED: 2026-09-23T23:35+01:00
INPUT: firmware-re/notes/scans/Z-usbdin-emu.txt

# Z-proposed-catalog — rows for Cursor to review

Reasoning in `model/Z-usbdin-emu.md`. Format per `two-agent-protocol.md`
§6. This is the highest-confidence row this entire USB/DIN thread has
produced — direct MMIO observation, not static inference.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (annotate `0x0801ad20`/`emit_key`, `+4` slot on `0x20001d60`) | | | **Confirmed DIN (USART1)** — Unicorn run observed real read+write of `0x4001380c` (USART1 CR1) `\|= 0x80`, via `0x08014b7c → 0x08010c10 → ... → 0x08010b14`. Two independent status-byte tests agree | S |
| (annotate `0x08014b6c`/`0x0800d77c`, `+0x14` slot) | | | Reached after the USART store, display-adjacent (reads `0x200051cc+0xb9` AutoTest flag). Not a USB candidate | S |
| `0x08010e46` | | (site, not a function name) | Loads USB object `0x20005888`, `bl 0x080091ca` — the real USB output call site. **Correction (caught by Cursor's own catalog-copy check, not by me): this is mid-function, not a function start** — I overclaimed by calling it "usb_send_entry" as if it were a named entry point. Rejected as a `recreate.py` name; the underlying finding (not reached from `emit_key`/`emit_seq`) stands | S (site/finding), X (as a function start) |

## Reframing note for the catalog (not a new row, a correction to prose)

The existing catalog's framing of `0x0801b384`/`emit_key`/`emit_seq` as
"USB vs DIN port switch" (from J/R) should be corrected: it's better
described as "DIN emit + display, vs. an unpopulated sequencer Note-On
slot" — USB is a separate path entirely, not a slot on this object.

## Explicit missing (per ticket instruction)

`emit_seq`'s `+0x18`/`+0x1c` Note-On target — never written by the
traced ctor, a real structural gap. Not proposing a row; flagging as a
genuinely new open item, not a guess.

STATUS: done
