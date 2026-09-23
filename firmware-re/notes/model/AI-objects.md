STATUS: done
AGENT: claude
TICKET: AI
UPDATED: 2026-09-24T01:20+01:00 (corrected per ticket AR — see note below)
INPUT: firmware-re/notes/scans/AI-ctors-init.txt

# AI-objects — three more gated sweeps found; leftover readers mostly reconfirm S

**Correction (ticket AR opened all three targets):** §1 below
speculated these could mean "dozens of uncatalogued objects." They
don't — AR found all three are single-object initializers, not
`ctor_sweep`-style tables. One of them turned out valuable anyway
(`0x08015f74` initializes `0x200051cc` directly — see `AR-init-sweeps.md`).
Leaving §1 as originally written below since the wrapper-shape
observation itself was correct and worth keeping, just flagging that
its scale estimate was wrong.

Read-only pass over `scans/AI-ctors-init.txt` only.

## 1. Major finding: init_array has 3 more gated dispatchers shaped exactly like ctor_sweep

`A-objects.md` flagged 4 of 5 `init_array` slots as "not examined." This
scan walks all of them — and finds the array actually has **6** entries
(`0x0801ef58` through `0x0801ef6c`, 4-byte stride), not 5 as originally
counted. Of those:

- **Slot 1** (`0x08004208`) and **slot 6** (`0x080041e4`): both a
  simple guard-flag-check-then-call shape (`cbz`/`cbnz` on a byte flag,
  conditional call using a literal that reads as `0x00000000` in this
  scan — likely an unresolved/weak-linked symbol). This is the standard
  compiler-generated C++ static-initialization-guard pattern, not
  application-specific. **S** for the shape; low priority.

- **Slots 2, 3, and 5** (`0x08005e74`→`0x8005da8`,
  `0x08011528`→`0x8010f40`, `0x0801611a`→`0x8015f74`): **each is a
  wrapper with the exact same gate shape as `ctor_sweep_wrapper_live`**
  — `push {r3,lr}; movw r1,#0xffff; movs r0,#1; bl <target>; pop {r3,pc}`.
  **Slot 5 even has a paired "dead" sibling** (`0x08016128`, `r0=0`
  instead of `1`) — the exact same live/dead wrapper pair pattern
  `ctor_sweep_wrapper_live`/`_dead` already established for slot 4's
  `0x08014d08`.

**This is a real, high-value structural finding, not walked further by
this scan**: `0x8005da8`, `0x8010f40`, and `0x8015f74` are, by shape,
strong candidates for **three more gated object-construction sweeps**,
structurally identical to `ctor_sweep` (`0x08014d08`) — the single
function that tickets A/C/G/S built the entire object-table picture
from. **None of these three has been opened.** **S** for the wrapper
shape (directly shown, unambiguous); **H** for "these are genuinely
more ctor sweeps" — the shape match is very strong but the targets
themselves are unexamined.

## 2. Leftover H-role readers — reconfirms S, no material new content

Section 2's single-window-per-site dumps for G's leftover sites (01,
05, 06, 07, 12, 13, 23, 34, 35, 36, 41, 46, 47, 48, 50, 52, 53) match
`S-ctor-roles.md`'s own findings exactly at every site checked — same
addresses, same call targets. This scan's per-site depth (first +
second reader only) is shallower than `S-ctor-readers.txt`'s full
listing, so it doesn't add new role evidence beyond what `S` already
extracted. **S** for consistency; no new rows from this section.

## Net — the real deliverable is the 3 unopened sweeps

The leftover-ctor-reader half of this ticket mostly reconfirms `S`.
The `init_array` half surfaces what's very likely the single largest
unexplored structural area in the whole application: three more
sweep-shaped functions, each a plausible sibling to `ctor_sweep`'s own
53-object table. If even one of them is real, it could mean dozens more
un-catalogued objects — this deserves its own dedicated ticket, not a
guess appended here.

STATUS: done
