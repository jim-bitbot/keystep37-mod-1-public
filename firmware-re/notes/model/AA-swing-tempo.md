STATUS: done
AGENT: claude
TICKET: AA
UPDATED: 2026-09-23T23:45+01:00
INPUT: firmware-re/notes/scans/AA-swing-tempo.txt

# AA-swing-tempo — internal tempo found; swing still not

Read-only pass over `scans/AA-swing-tempo.txt` only.

## 1. Internal tempo RAM — closed, with the full hardware write path

**Tick object `+0xe` (halfword) is the internal tempo field.** Full
chain, all directly disassembled:

```
some input value (r1)
  -> 0x08012048: clamp between 3000 and 24000
  -> strh r1, [r0, #0xe]              (tick object, same offset the
                                        ctor defaults to 0x2ee0 = 12000)
  -> 0x080120ac (caller, r0=0x20002bec): also writes +0x4c, +0x50, +0x48
  -> 0x08012084: str r3,[r0,#0x2c]    (TIM2 ARR register, verified
                                        against the real STM32F1 timer
                                        register map — 0x2c is ARR)
  -> 0x08012086: str r3,[r2,#0xc]     (also overwrites the wrapper
                                        object's own +0xc, per T-clock.md)
```

**S** — every link in this chain is a directly-shown instruction, and
the clamp range (3000-24000) plus the default (12000, dead center) is
exactly the shape of a BPM-derived timer period, not a coincidence.
This **closes `I-time.md`'s explicit "internal tempo RAM: not found"**
gap. Recommending the tick object's `+0xe` field be named
`internal_tempo_period` (tentative) in the catalog.

## 2. Six pc-rel sites of the tick object — four are genuinely new

`I-time.md` only had one confirmed caller (`0x08015768`, into
`arp_seq_tick`). This scan finds **five more**: the ctor-sweep site
(`0x08014ed8`, expected), plus four real new ones —
`0x08015304` (→ `0x080120ac`, the tempo-write path above), `0x080154c6`
(→ `0x0800fa16`, the "sibling parser" `C-loop.md` flagged and never
traced), `0x08015768` (already known), `0x080157e6` (→ `0x08012330`,
the same "busy" gate `analog_knob_process`/TIM2 share, per C/I), and
`0x08015802` (→ `0x08012330` again, different call site). **S** — this
substantially expands the tick object's known touch points beyond the
single site prior tickets had.

## 3. Swing — still not found, and this scan makes the negative stronger

Searched `+0x401` (the slot header field ticket L left as H) across 6
sites — all are inside `seq_step_store`'s own TBB (already fully
mapped in `L-record.md`/`Y-record-clear.md`, cases 0/2/3 reading or
writing `+0x401`/`+0x402`), **none reveal a "swing" role**, just
confirm the field exists and is read/written by the recorder. Section
3's occupancy-value search (218 raw `cmp`/`mov`/`strb` hits against
swing's known panel values) is explicitly too noisy to use as-is — no
single site stands out as *the* swing reader among 218 candidates.
**S** for the negative: swing RAM is not findable by this scan's
methods. The field at `+0x401` remains **H** for its name (per L's
correction — "Swing" was never independently confirmed, only that
something gets written there).

## Net for HANDOFF layer 4

Internal tempo: **closed**, with a real hardware register write
confirmed. Swing: **still open**, and this ticket's negative result
is itself useful — it rules out both obvious places (the slot header
field, the tick object's window) without finding it, meaning swing
either lives on a third object not yet traced, or is computed inline
at note-timing time rather than stored as a discrete RAM value.

STATUS: done
