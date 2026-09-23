STATUS: done
AGENT: claude
TICKET: AI
UPDATED: 2026-09-24T00:25+01:00
INPUT: firmware-re/notes/scans/AI-ctors-init.txt

# AI-proposed-catalog — rows for Cursor to review

Reasoning in `model/AI-objects.md`. Format per `two-agent-protocol.md` §6.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| `0x08005e74` | | init_array slot 2 wrapper | Same gate shape as `ctor_sweep_wrapper_live` (`r0=1,r1=0xffff`), calls `0x8005da8` — unopened, strong candidate for another object-construction sweep | S (wrapper), H (target's role) |
| `0x08011528` | | init_array slot 3 wrapper | Same shape, calls `0x8010f40` — unopened | S (wrapper), H (target's role) |
| `0x0801611a` | | init_array slot 5 wrapper | Same shape, calls `0x8015f74`, **has a paired dead sibling** (`0x08016128`, `r0=0`) matching `ctor_sweep_wrapper_dead`'s exact pattern | S (wrapper), H (target's role) |
| (annotate `init_array`) | | | Corrected count: **6** entries (`0x0801ef58`-`0x0801ef6c`), not 5. Slots 1/6 are standard C++ static-init guards, low priority | S |

## Strong recommendation, not a claim of authority over tickets.md

Requesting a dedicated ticket to open `0x8005da8`/`0x8010f40`/
`0x8015f74` — the wrapper shape match to `ctor_sweep` is strong enough
that this could be the single highest-value remaining scan in the
project, on par with what ticket A's original `ctor_sweep` discovery
produced across A/C/G/S.

STATUS: done
