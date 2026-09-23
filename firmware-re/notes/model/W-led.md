STATUS: done
AGENT: claude
TICKET: W
UPDATED: 2026-09-23T22:55+01:00
INPUT: firmware-re/notes/scans/W-led-confirm.txt

# W-led — DMA1_CH1 ruled out for LEDs; Rec LED confirmed absent

Read-only pass over `scans/W-led-confirm.txt` only.

## 1. DMA1_CH1's tail — NOT the LED path, a real negative result

`0x080045b6` tail-calls `0x08004566`, whose own body was fully
disassembled here: it checks a flag at `[r0,#0x24]`, and its `bl`s go
to `0x0800781c` and further object field manipulation (`+0x28`,
`+0x20`) — **neither `led_write` (`0x0800d26e`) nor `led_refresh`
(`0x0800d1f8`) appears anywhere in this chain.** **S** — direct,
confirmed negative. This **corrects `P-led.md`'s framing**: DMA1_CH1
was called the "best candidate" there on structural grounds (it reads
an indirect buffer pointer, unlike the other two channels) — this
scan shows that candidacy doesn't pan out. Whatever `*0x200010f0`'s
object is, it's not LED-related by this evidence. Correcting, not just
adding: DMA1_CH1 should be considered **ruled out** for LEDs now, same
confidence tier as DMA1_CH2 already was.

## 2. Rec LED — confirmed absent, now from the write side too

Rec press (`0x0801780c`) calls exactly two functions:
`0x0801d7b6(r1=5)` and `0x0801d76c(r1=5)` — the same
notify/subscriber-publish pair every other button case uses (F, L).
**Neither is `led_write`.** Cross-checked from the other direction too:
searched `led_write`'s full 33-caller range (`0x0800d2f2`-`0x0800daac`)
against the button-dispatch window (`0x08017700`-`0x08017c00`) — **zero
overlap.** **S, from both directions** — this isn't "not found in one
search," it's two independent negative confirmations (from the Rec
press site outward, and from the LED writer's caller list inward)
agreeing. `L-record.md` and `P-led.md`'s "Rec LED not found" is now a
settled negative, not an open search.

## Net for HANDOFF layer (LED/DMA) — closes W's stop condition

**DMA1_CH1's LED role: ruled out** (corrected from P's "best
candidate" framing). **Rec LED: confirmed absent from the direct
notify path and the writer's caller list both** — if a Rec LED exists
at all, it's driven through a mechanism neither this ticket nor P
found (candidate: an indirect path through `0x0801d7b6`/`0x0801d76c`'s
own downstream code, not walked here — those are generic
notify/publish functions used by many buttons, so tracing "what do
they eventually do with code 5" would need its own ticket, not a
guess here).

STATUS: done
