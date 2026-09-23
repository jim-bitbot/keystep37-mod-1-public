STATUS: done
AGENT: claude
TICKET: P
UPDATED: 2026-09-23T21:10+01:00
INPUT: firmware-re/notes/scans/P-led.txt

# P-led — key writer and three DMA entries

Read-only pass over `scans/P-led.txt` only. Per ticket instruction: no
frame-atomicity claim (none made below).

## 1. Writer 0x0800d26e — one general LED writer, 33 callers, not split by ticket

Indexes by `r1` (0-40, `bhi` above `0x28`), computes a destination
offset into the **caller's own `r0`** and stores `1`. **33 static
callers**, all clustered in `0x0800d2f2`-`0x0800daac`. One caller is
`M-chord.md`'s scale-bit loop (`0x0800d966`). **S** for the writer
itself and the caller cluster; this scan does **not** split "key LEDs"
from "other LEDs" — the ticket's own fallback applies: not splitting
without evidence, not asserting a split that isn't shown.

**Concrete narrowing for L's still-missing Rec LED**: if a Rec LED
write exists via this writer (not confirmed), it is one of these 33
callers inside `0x0800d2f2`-`0x0800daac` — a bounded 2KB region to check
next, not the whole 196KB image. Stated as a lead, not a finding.

## 2. Refresh 0x0800d1f8 — dirty-check-then-flush, not a blind re-push

One static caller (`0x0800d6c4`). Compares two bytes of the same
object (`+0x944` vs `+0x946`); only on a difference does it update
`+0x946` and call `0x0800b6ec(r0=0x200055a8)`. **A real architecture
finding**: LED refresh is diffed against a cached copy, not re-pushed
every call. **S.**

## 3. Three DMA entries — one plausible LED-DMA candidate, two ruled out

| IRQ | VA | What it touches | LED candidate? |
|---|---|---|---|
| DMA1_CH1 (11) | `0x080185e8` | Clears `0x20005300`, then `bl 0x080045b6(*0x200010f0)` — the only one of the three that dereferences an **indirect buffer pointer** and does further work (zeroes `[r0,#0x40]`, tail-calls through `[r0,#0x38]`) | **Best candidate.** S for the buffer-pointer read; H for "this is LEDs" |
| DMA1_CH2 (12) | `0x08018a40` | Clears `0x20005570`, calls `0x0800d1f4` — which is a bare `bx lr`. **The scan states plainly this IRQ does not `bl` the key refresh (`0x0800d1f8`)** | **Ruled out** as the key-refresh path — S, negative result |
| DMA1_CH3 (13) | `0x080186c4` | Clears `0x20005484` only, no buffer read at all | Weakest candidate — S (no evidence either way) |

This is a genuine, useful narrowing: two of the three channels are
either ruled out or show no LED-shaped evidence; one shows the right
shape (indirect buffer pointer + further dispatch).

## 4. Missing

Rec LED writer: still not found (matches L's own conclusion — two
independent tickets, same negative result, which is itself
corroborating). No frame-atomicity guarantee is claimed anywhere above,
per instruction.

## Net for HANDOFF layer (LED/DMA)

Key LEDs vs "other" LEDs: not split by this scan — the general writer
and its 33 callers are one undifferentiated pool as far as this ticket
goes. DMA source RAM is now narrowed to one strong candidate
(`0x080185e8`/`*0x200010f0`) with two channels structurally ruled out
or unevidenced. Both the writer and the refresh function are named and
their shapes (index-based store; dirty-check-then-flush) are confirmed.

STATUS: done
