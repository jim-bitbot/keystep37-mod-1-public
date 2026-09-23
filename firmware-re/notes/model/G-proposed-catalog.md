STATUS: done
AGENT: claude
TICKET: G
UPDATED: 2026-09-23T20:20+01:00
INPUT: firmware-re/notes/scans/G-ctors.txt

# G-proposed-catalog — rows for Cursor to review

Reasoning in `model/G-objects.md`. Format per `two-agent-protocol.md`
§6. Proposing `recreate.py` names only for the function starts the
ticket instruction calls for (ctor VAs), not for role-guessed names.

## Function starts with a now-confirmed role (S)

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| `0x0801d6e4` | | subscriber_obj_ctor | Ctor of `0x20002d90`, the object `app_main_loop` registers into the CC subscriber table at startup (confirmed in `C-loop.md`) | S |
| `0x0800c7f0` | | key_scan_obj_ctor | Ctor of `0x20000674`, `key_scan`'s own `r0` object (confirmed in `C-loop.md`) | S |
| `0x08011d7c` | | tick_obj_ctor | Ctor of `0x20002bec`, the tick object passed to `arp_seq_tick` (confirmed in `I-time.md`) | S |
| `0x08005a08` | | mode_obj_ctor (tentative) | Ctor of `0x200004f4`, `mode_skip_apply`'s object — writes `8` to `+0x6d`/`+0x6e` before first use | S |
| `0x08005aa4` | | timediv_obj_ctor (tentative) | Ctor of `0x20001000`, `timediv_skip_apply`'s object — same shape as above | S |

## Existing row to close (resolves an A-ticket flagged discrepancy)

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (existing flagged lead: `0x08014416` vs `seq_step_store` `0x08014418`) | | | **Resolved.** `0x08014416` is `bx lr`, no store, not a second ctor. The nearby `strb.w [r0,#0x403]` belongs to `seq_step_store`'s own body, not this address. No further action needed on this lead | X (on the original "distinct ctor" hypothesis) |

## Existing row to strengthen — reader confirmed

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (existing `0x08019f8c` ctor family, 9 objects) | | | Write-side tag confirmed: `strb r1,[r0,#0xd]` is the compact-ID tag, matching `F-buttons.md`'s closed 0-8 compact-index table (Hold...Chord) by count and order. Combined with `C-loop.md`'s reader (`button_debounce`, 9 calls), "one debounce object per compact button ID" is now **S** for existence+reader+tag; which of the nine RAM addresses is which specific control is still not traced address-by-address (**H**) | S |

## Existence-only rows (new objects, role not yet known)

Ctor VA, RAM base, first-store offset for the remaining 24 leftover
sites (01, 02, 03, 05, 06/07 shared, 08, 09, 10, 11, 12, 13, 17, 23, 34/35
shared, 36, 41, 45, 46, 47, 48, 49, 50, 51, 52, 53) are recorded in
`model/G-objects.md`'s table. Not proposing individual catalog rows for
these — no role evidence beyond "an object exists here, built by this
ctor," which the ticket instruction tags **H** and doesn't ask to be
promoted to a named catalog row without a later ticket's confirmation.
Two are flagged as live leads worth remembering: site 50 (`0x0801b02c`,
`0x20001e04`) for the unresolved scale-mask-offset question from A §5,
and site 52 (`0x08014be8`, `0x20001180`) for the unresolved chord/voice
settings-object question from the same section.

STATUS: done
