STATUS: done
AGENT: claude
TICKET: AS
UPDATED: 2026-09-24T01:15+01:00
INPUT: firmware-re/notes/scans/AS-sync-idr.txt

# AS-sync-idr — a real candidate for external sync detection, gating both TIM2 and transport start

Read-only pass over `scans/AS-sync-idr.txt` only. This is the
strongest lead this project has produced on the clock-source question
since ticket I opened it — genuinely new territory, not a rehash.

## 1. The object — a 4-pin GPIOD I/O abstraction

`0x20004f00` (G's site 12) is populated via `0x08019178` with **all
four** pointer-sized fields (`+0`/`+4`/`+8`/`+0xc`) set to the **same**
GPIO base, `0x40011400` — **GPIOD**. The four halfword fields
(`+0x10/+0x12/+0x14/+0x16`) hold `1`/`8`/`2`/`4` — bitmasks for pins
**0, 3, 1, 2** of GPIOD. Its pointer is published to `0x20001128`.
**S** — this is one object representing 4 distinct GPIOD pins, read and
written through a common small set of wrapper functions.

## 2. IDR read path — confirmed real GPIO input reads

`0x08008804` is a generic "test one IDR bit" leaf
(`ldr r3,[r0,#8]; tst r1,r3` — offset `0x08` is IDR on every STM32
GPIO port). Five thin wrappers (`0x08019058`, `0x0801919e`,
`0x080191b6`, `0x08019234`, `0x08019244`) each pull a bitmask and a
GPIO-base pointer from an object's fields and call it. **S.**

## 3. Two of those wrappers gate real, high-value actions

Tracing the **callers** of the wrappers on `0x20001128` specifically
(not the generic leaf's other uses elsewhere):

- **`0x080183cc`** (§7c): reads a GPIOD pin via `0x8019244`; if the
  result is `0`, calls `0x0800b0c6` on `0x20005534` — **the exact TIM2
  disable leaf** `T-clock.md` already confirmed (clears DIER/CR1 enable
  bits). **A specific GPIOD pin state directly gates disabling the
  internal timer.**
- **`0x08018522`** (§7d): reads a GPIOD pin via `0x8019234`; if the
  result is `0`, calls `transport_cmd(r1=1)` — **the confirmed MIDI
  Start command** (`N-sync.md`). **The same pin family directly
  triggers a transport Start action.**

Both **S** — directly shown call sequences, not inferred.

## 4. Reframes, doesn't contradict, T-clock.md's negative

`T-clock.md` searched the TIM2 **wrapper object's own fields** for a
software arbitration flag and correctly found none. **This explains
why**: the arbitration isn't a flag living on the TIM2 object — it's a
**separate GPIOD-pin read**, in different functions entirely
(`0x080183cc`/`0x08018522`, both reached from the interrupt/init
territory around `0x08018328`-`0x08018556`, adjacent to EXTI0
`C-loop.md` already named), that then *calls into* the TIM2 and
transport mechanisms from outside. T's search method couldn't have
found this — it was looking in the right object for the wrong kind of
evidence.

## 5. What this most likely is — H, a strong one, not confirmed against hardware

Four GPIOD pins, read as inputs, gating timer-disable and transport-
start — this is structurally exactly what external sync detection
looks like: a Sync In jack and/or the rear-panel sync source switches
`findings-2026-09-20.md` already documented from manual testing ("the
arp will not run unless the two rear-panel sync source slider switches
are both down"). Four pins fits a plausible mapping (2 slider switches
+ a sync-in/sync-out jack pair), but **I have not matched these
specific pins to the physical schematic or silkscreen** — that's
outside what static disassembly can confirm. **Tagging the mechanism
(GPIOD IDR reads gating TIM2/transport) as S; the "this is the Sync
DIP/jack" identification as H**, strong but not hardware-verified.

## 6. Output side exists too — not just input

`0x0801236a`-`0x08012378` (inside `transport_cmd` itself) **writes** to
the same object via `0x80191ce`/`0x80191e6` (BSRR-style, offset
`0x10`/output-set — different mechanism from the IDR reads). So at
least one of these 4 pins is also driven as an **output** by
`transport_cmd` — consistent with a combined sync-out/sync-in jack pair
sharing one GPIO port. **S** for the write existing; not resolved which
pin.

## Net for HANDOFF layer 4 — the strongest clock-source lead yet

Not a final closure (the physical pin-to-function mapping needs
hardware confirmation this project's method can't provide), but a real,
concrete, multi-site-confirmed mechanism: **external GPIOD pin state
directly gates both TIM2 disable and MIDI-Start transport action** —
exactly the shape of external-sync detection, found by tracing from
`AB`'s honest negative to a sharper GPIO-specific method, per `AB`'s
own recommendation.

STATUS: done
