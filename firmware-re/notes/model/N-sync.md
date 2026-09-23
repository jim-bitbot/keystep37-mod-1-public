STATUS: done
AGENT: claude
TICKET: N
UPDATED: 2026-09-23T21:02+01:00
INPUT: firmware-re/notes/scans/N-sync.txt; firmware-re/notes/model/I-time.md

# N-sync — realtime bytes, Tap, extending I with source selection

Read-only pass over `scans/N-sync.txt` only.

## 1. Realtime-byte compares live in a different function from the parser itself

`0x0800fa64` (main-loop MIDI parser) does its own `0xF8` range check
(`cmp r6,#0xf8`/`blo`) as part of general byte filtering, but the actual
**Start/Stop/Continue/Clock dispatch is in `0x0800ffe0`**, not
`0x0800fa64` itself:

| Byte | Meaning (standard MIDI) | Target | Action |
|---|---|---|---|
| `0xFA` | Start | `0x08010116` | `r1=1`, `bl 0x08012334` |
| `0xF8` | Clock | `0x080100d6` | `r0 = 0x20005534`, `bl 0x0800b0c6` |
| `0xFC` | Stop | `0x08010170` | different shape, reads `[sp,#0x2c]+0x10` |
| `0xFB` | Continue | `0x080101ac` | not walked |

**S** — every byte and target is a literal in the scan.

## 2. The clock-convergence finding: 0x20005534

**`0x08F8` (Clock) loads `0x20005534` — the exact same object
`I-time.md`'s TIM2 finding loads** (`TIM2_IRQ`'s first `bl`,
`0x08018586`). This is real, direct evidence that **incoming MIDI Clock
bytes and the internal hardware timer converge on the same RAM
object**, which is the natural place HANDOFF layer 4's "internal vs
MIDI clock is one diagram" question would resolve. **S** for the shared
address; **H** for "this is the clock-source-selection point" — this
scan doesn't show what happens after either write, just that both
sources feed the same object.

## 3. Transport-command function shared across two unrelated triggers

`0x08012334` — called here with `r1=1` for MIDI Start — is **the same
function `J-voice.md` found called with `r1=4` from the Shift+Play
button case** (`0x08017a34`). One function taking a numeric transport
command, fed from both a MIDI realtime byte and a panel button. **S**
for the shared callee; **H** for the full code table (only `1` and `4`
are pinned to a known trigger).

## 4. No USB/DIN split visible here either

No USART1 (`0x40013800`) or USB (`0x40005C00`) peripheral literal
appears in `0x0800ffe0`, `0x08010254`, or their compare windows — by
the time a realtime byte reaches this dispatch, the source is already
merged, consistent with `J-voice.md`'s finding that USB/DIN selection
happens through object-field indirection elsewhere, not visible in the
transport-command code itself. Source-selection (the rear-panel Sync
DIP, `stock-shift-map.md`'s unshifted-panel ID `0x13`) is **not**
covered by this scan — explicit missing, not solved.

## 5. Tap — confirmed absent from all three dispatch tables

Compact index 4 (`id 0x67`, Tap) lands at the same common `pop`
(`0x08017b0e`) in **all three** `panel_button_dispatch` tables
(unshifted, shifted, `r2==0`). **A clean, confirmed negative result**:
Tap tempo is definitively not handled inside `panel_button_dispatch` —
per the ticket instruction ("Tap = tempo, not a hole"), this matches
`stock-shift-map.md`'s live-verified finding, and now has a structural
reason why button-dispatch tickets (B, F) never found a Tap case: there
isn't one there. The actual tap-tempo logic must live in the
debounce/key-scan path itself, not traced by this scan. **S** for the
negative result.

## Net for HANDOFF layer 4 (extends I)

Internal tempo RAM: **not found**, per ticket instruction, stated
explicitly rather than left silent. Clock **source selection** itself
(internal vs MIDI, and the Sync DIP) is still open, but this scan
narrows it usefully: `0x20005534` is now a concrete, cross-validated
candidate for where both sources land, and `0x08012334` is a concrete
candidate for the shared transport-command sink. Neither is a name yet
— both are strong leads for whoever picks up clock-source work next,
not guesses invented here.

STATUS: done
