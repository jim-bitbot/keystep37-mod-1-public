STATUS: done
AGENT: claude
TICKET: AQ
UPDATED: 2026-09-24T01:55+01:00
INPUT: firmware-re/notes/scans/AQ-sites-08-11.txt

# AQ-sites-08-11 — a shared "publish pointer" pattern, roles stay H

Read-only pass over `scans/AQ-sites-08-11.txt` only.

## Finding: four objects, each published to a dedicated global slot

Sites 08/09/10/11 (`0x20002cdc`/`0x20002cf8`/`0x20002dbc`/`0x20002e80`)
each have exactly 2 readers: the ctor sweep itself, and **one more
site**, all sitting in sequence (`0x0801510c`-`0x0801513c`), each
following the identical shape: call a per-object accessor function
(`0x8006b7c`/`0x8006cf0`/`0x8006da8`/`0x8006a0c`), then **store that
object's own pointer into a dedicated global slot**
(`0x200010ec`/`0x2000111c`/`0x200010f8`/`0x2000107c` respectively).
**S** — this is a real, consistent pattern: four small ctor-built
objects, each "published" to its own named global pointer slot, one
right after another in the same function.

## Not resolved

The accessor functions (`0x8006b7c` etc.) aren't walked, so what each
object actually represents stays **H**. The four destination slots
(`0x200010ec`, `0x2000111c`, `0x200010f8`, `0x2000107c`) are new
addresses this scan surfaces but doesn't explain — worth noting for
whoever eventually maps this cluster, not guessed here.

## Net

Existence and a real structural pattern (publish-to-global-slot)
confirmed for all 4 leftover sites AI's first pass skipped. No role
closure — consistent with the ticket's own scope (leftover readers,
not a deep dive).

STATUS: done
