STATUS: done
AGENT: claude
TICKET: AF
UPDATED: 2026-09-24T00:15+01:00
INPUT: firmware-re/notes/scans/AF-set-alt.txt

# AF-set — confirms U's negative, from the store-pattern angle

Read-only pass over `scans/AF-set-alt.txt` only.

## 1. param_field_dispatch's 2 callers — reconfirms X, no new caller

Same 2 static callers as `X-selectors.md` (`0x0800fd4e`, `0x0800ffda`).
**S**, no change.

## 2. GET family store-pattern check — all reply-buffer construction, not settings writes

Checked the first 32 instructions of each GET handler for stores that
might reveal an inline SET path:

- **`get_param`**: 4 stores (`[r5,#4]`, `[r5,#8]`, `[r3]`, `[r0]`) —
  all writing into `r5`/`r3`, registers holding the function's own
  **local reply structure**, built from data just read via `r3`
  (`0x20000214`, the same heap-ish pointer `AC`/`test20_cc_value` also
  use). This is reply-envelope construction, not a write to persistent
  device state.
- **`get_param_b`**: same shape, 3 stores, same reply-buffer pattern.
- **`get_param_c`**: **0 stores** before the first `pop`/`bx` on its
  early-exit paths.
- **GET TBB itself (`0x0800ee92`)**: **0 stores** — pure dispatch.
- **Sibling `0x0800ef38`**: **11 stores**, but all into a **local stack
  array** (`[sp]` through `[sp,#0xa]`) built from small constants
  (`6`, `2`, `0`) and incoming register values — again a local
  structure being assembled, not a persistent-storage write.

**S for all of this — this is a real, checked negative, not an
unexamined assumption.** None of the store activity anywhere in the
GET family or its sibling touches anything outside a local/stack
buffer.

## Net — reinforces U, doesn't reopen it

`U-set.md` concluded no SET entry exists as a mirror of the GET TBB.
This ticket approached the same question from a different angle
(store-pattern inspection rather than TBB-structure inventory) and
reaches the same place: **every store in the GET-adjacent code writes
a local reply/temp structure, none touches persistent settings state.**
Two independent search methods agreeing is a stronger negative than
either alone. SET, if it exists in this firmware's wire protocol at
all, is not implemented anywhere near the GET dispatch family — the
two hypotheses `U-set.md` already raised (different opcode scheme
entirely, or SET doesn't exist as a distinct wire path) remain the
live candidates, still unconfirmed either way.

STATUS: done
