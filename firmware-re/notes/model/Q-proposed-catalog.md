STATUS: done
AGENT: claude
TICKET: Q
UPDATED: 2026-09-23T22:15+01:00 (corrected per Cursor's review)
INPUT: firmware-re/notes/scans/Q-h-rows.txt

# Q-proposed-catalog — rows for Cursor to review

Reasoning in `model/Q-promote.md`. Format per `two-agent-protocol.md`
§6.

## Requests — recreate.py corrections (not editing recreate.py myself)

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| `0x08011c88` | | (request: reconsider `pattern_or_order_builder` in recreate.py) | Confirmed a case-body label (no push, entered only via `rebuild_order`'s TBH), not a callable function start. Same for all 7 Mode-TBH targets | X (as a function start) |
| `0x08004bf8` | | (request: reconsider `shift_strip_pickup` in recreate.py) | Confirmed no push, a branch target inside `analog_knob_process`/`strip_process_b`, not a separate function | X (as a function start) |

## Judgment-call rows — disagreeing with the scan's LABEL tag, with reasoning

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| `0x0801161c` | | (annotate `arp_note_pool_ctor`) | Scan tags LABEL (no push found), but this is a confirmed ctor-sweep `bl` target (A/G tickets) — a real call site by construction. Recommending S over the scan's own heuristic-based X | S |
| `0x08013c9a` | | (annotate `note_pool_pair_ctor`) | Same reasoning — confirmed ctor-sweep target, minimal leaf shape explains the missing push | S |

## New rows

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| `0x08013028` | | seq_block_promote_pending (tentative) | 3-insn leaf: `current_ptr = pending_ptr`. **Promotes the existing "external source" claim about `0x08012bd6 → 0x08013028`** to S — own disassembly matches it exactly | S |
| `0x08007652` | | (unnamed, existence only) | Confirmed real function, called from `SysTick_Handler`. No role evidence | S existence |
| `0x08006988` | | (unnamed, existence only) | Confirmed real function, touches the shared-block `+0x54..+0x5b` cluster `H-shared.md` already flagged | S existence |

## Correction rows

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| `0x08016afc` | | (correct containing-function citation — superseded, see ticket Y) | **Ticket Y directly disassembled `0x08016ac0`**: it's a real function that branches to `0x08016afc` internally on `r1==1`. B/F's original "inside fn `0x08016ac0`" framing turns out to be the accurate one; this row's earlier "own function start" claim is withdrawn | S |
| `0x08010638` | | (correction, not a new claim) | Function-start status is S (real `push`). **"USB packet decode" is not confirmed by this scan** — that label is still the old external-source claim; I wrote it as if promoted alongside the structural fact, which was wrong. Keep the name at H | S (start only), H (name) |

## Not proposed

The 28 confirmed labels/case-bodies — no function-start row proposed
for any (see `model/Q-promote.md` for the full list); their existing
behavioral catalog rows (from F/H/I/M and earlier tickets) stand as-is.
`0x080150a4`'s own containing function — still not found, explicit
missing, unchanged from `C-loop.md`.

STATUS: done
