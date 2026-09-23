STATUS: done
AGENT: claude
TICKET: AS
UPDATED: 2026-09-24T01:15+01:00
INPUT: firmware-re/notes/scans/AS-sync-idr.txt

# AS-proposed-catalog — rows for Cursor to review

Reasoning in `model/AS-sync-idr.md`. Format per `two-agent-protocol.md` §6.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| `0x20004f00` | | sync_gpio_pins (tentative) | 4-pin GPIOD I/O object, all fields point at `0x40011400`, masks `1/8/2/4` = pins 0/3/1/2. Pointer published to `0x20001128` | S |
| `0x08008804` | | gpio_idr_test (tentative) | Generic IDR-bit test leaf, offset `+8` on any GPIO base | S |
| (annotate `0x0800b0c6`, TIM2 disable) | | | Reachable from `0x080183cc`, gated on a GPIOD pin read via `0x8019244` — external pin state can disable TIM2 | S |
| (annotate `transport_cmd`, `0x08012334`) | | | Reachable from `0x08018522`, gated on a GPIOD pin read via `0x8019234` — external pin state can trigger MIDI-Start | S |

## Explicit caveat (per ticket instruction — strong lead, not hardware-confirmed)

The "this is the Sync DIP / sync jack" identification is H — the
mechanism (GPIOD pins gating TIM2/transport) is directly shown, but
matching specific pins to the physical schematic needs hardware access
this method doesn't have. Not overclaiming past what's shown.

STATUS: done
