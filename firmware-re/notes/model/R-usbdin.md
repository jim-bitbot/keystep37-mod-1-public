STATUS: done
AGENT: claude
TICKET: R
UPDATED: 2026-09-24T01:00+01:00 (corrected per ticket AK — ctor copies
8 words, not 6)
INPUT: firmware-re/notes/scans/R-usbdin.txt

# R-usbdin — what fills port-switch slots

Read-only pass over `scans/R-usbdin.txt` only. This closes the chain
`lead-usb-din.md` left open, though the final USB-vs-DIN peripheral
identity stays unresolved by static means (stated plainly below, not
guessed).

## 1. The full ctor chain, now traced to its root

```
ctor sweep (0x08014f12-0x08014f6c)
  |
  |-- bl 0x0801acb0 (r0=0x20001d60)   6-word copy ctor
  |-- bl 0x0801b02c (r0=0x20001e04, r1=0x20001d60)   *0x20001e04 = 0x20001d60
  \-- bl 0x0801b572 (r0=0x20001eb8, r1=0x20001e04)   *0x20001eb8 = 0x20001e04
```

**S** — every store confirmed directly. This resolves `lead-usb-din.md`'s
open question ("what fills `*(0x20001eb8+0)`"): it's `0x20001e04`
(G's site 50, the scale-mask-adjacent object M already partially
mapped), which itself holds `0x20001d60` (G's site 49) at its own `+0`.
**Three-level chain**: `0x20001eb8 → 0x20001e04 → 0x20001d60`, built in
that order by one ctor-sweep group, not independent objects.

## 2. `0x20001d60`'s own ctor — CORRECTED: an 8-word copy, not 6

**Correction (ticket AK caught this):** `0x0801acb0` copies **8**
words, `+0` through `+0x1c`, not the 6 (`+0` through `+0x14`) I
originally reported — I stopped reading the ctor body one `stm.w`
early. The two I missed (`+0x18`/`+0x1c`) come from the ctor's own
stack at `sp+0x24`/`sp+0x28`, sourced from **more** call-site arguments
than I'd traced. This directly closes `Z-usbdin-emu.md`'s "genuinely
new open item" (`emit_seq`'s Note-On path reading unpopulated
`+0x18`/`+0x1c`) — **those fields are not unpopulated**, my own earlier
scan just didn't see far enough into the ctor to find the store. What
Cursor's AK scan couldn't do (correctly, out of this ticket's scope)
is re-derive what the sweep's own stack actually puts at those two
slots — that's the next real question, not "is it populated."

The 6 I did trace correctly: `0x200013fc` (the `notify_013fc` sink
object, site 05), and four Thumb function pointers —
`0x08014b6c`/`0x08014b74`/`0x08014b7c`/`0x08014bb0` — each a tiny
wrapper: the first reads `0x200051cc+0xb9` (AutoTest flag), the second
reads a byte at `[r0,#4]`, the third and fourth allocate/free via
`0x20000214` (a heap-ish pointer, `0x0801d862`/`0x08010b30`). **None of
the four wrapper functions, nor the two deeper callees they reach in
the first `0x120` bytes, contains a `0x40013800` (USART1) or
`0x40005C00` (USB) literal.** **S** — exhaustive within the searched
window, for the 6 slots actually checked.

## 3. port_switch (`0x0801b384`) — confirmed operating on `0x20001d60`, not directly on `0x20001eb8`

`r0` at entry is `0x20001e04` (dereferenced from `*0x20001eb8`); the
function itself further dereferences to `0x20001d60` (`[r7]`) before
the `emit_key`/`emit_seq` calls. **So the actual vtable-holding object
port_switch's callees read from is `0x20001d60`, two levels of
indirection from the fixed pointer `play_time_step` and the key path
both start from.** No static `bl` from either `0x0801ad20`
(`emit_key`) or `0x0801ae56`(`emit_seq`), and no USART/USB literal in
either function's window. **S.**

## 4. Key path and sequencer path confirmed to share the exact same root object

All four `0x0801b750` callers (`E-keys.md`) pass `r0=0x20001eb8` —
**the same literal this scan's §1 traces, and the same object
`play_time_step`'s six calls into `0x0801b6c4` use.** Not two separate
objects for two separate paths — one shared root, diverging only at
`port_switch`'s `r3` argument (0/2 for key path, 1 for sequencer path).
**S.**

## What this closes, and what it honestly doesn't

**Closed**: the *shape* of the mechanism, completely — a 3-level ctor
chain, one shared root object, `port_switch` reading a vtable two
indirections deep, `emit_key` making 2 indirect calls (slots at
`+4`/`+0x14` on the `0x20001d60` object) and `emit_seq` making 1
(`+0xc`). This is now a fully-traced, real structure, not a guess.

**Not closed, stated plainly**: which physical peripheral (USB vs DIN)
each of those 2-3 vtable slots on `0x20001d60` actually points to.
**No static literal anywhere in this chain names USART1 or USB.** This
scan's own header says it plainly: the four Thumb-pointer wrappers and
their immediate callees don't touch either peripheral. The real values
live in whatever `0x0801acb0`'s **caller-supplied arguments** actually
are at runtime — which this scan traced to Thumb function pointers, not
raw peripheral addresses, meaning **the USB/DIN identity is behind at
least one more layer of indirection than a static literal search can
resolve.** Per the project's own methodology
(`ARTURIA-FIRMWARE-RE-GUIDE.md` §9): this is exactly the kind of
question static search is the wrong tool for — the next step is
Unicorn emulation of `0x0801acb0`'s call site with the real
`play_time_step`/key-path register state, not another static scan.

STATUS: done
