STATUS: done
AGENT: claude
TICKET: F
UPDATED: 2026-09-23T20:15+01:00
INPUT: firmware-re/notes/scans/F-buttons.txt

# F-buttons — compact IDs, dispatch TBHs, leftover Shift sites

Read-only pass over `scans/F-buttons.txt` only. Tags: **S** = shown
directly, **H** = plausible not shown.

## 1. Compact index — the missing piece from B and C, now closed

`id_to_index` (`0x08006024`) and `index_to_id` (`0x0800606c`) together
give an exact, closed 0-8 compact-index table:

| Index | Control ID | Control (from `stock-shift-map.md` §10) |
|---|---|---|
| 0 | `0x55` | Hold |
| 1 | `0x56` | Shift |
| 2 | `0x10` | Oct− |
| 3 | `0x11` | Oct+ |
| 4 | `0x67` | Tap |
| 5 | `0x57` | Rec |
| 6 | `0x59` | Stop |
| 7 | `0x5a` | Play |
| 8 | `0x69` | Chord |

**S** — every entry is a literal `cmp`/`movs` in the scan. This is
**exactly** the 9-category range (`0`-`8`) `A-objects.md` §6 flagged as
a structural match for the `0x08019f8c` nine-object ctor family, and
`C-loop.md` §3 confirmed `button_debounce` reads all nine once per main
loop pass. Those two tickets could only say "nine objects, nine
category count, no semantic reader." This scan supplies the actual
category names — closing that lead to **S** for "one debounce object per
one of these nine controls," though the specific object-to-control
assignment (which of the nine RAM addresses is Hold vs Shift vs ...)
is still not traced index-by-index and stays **H**.

## 2. panel_button_dispatch — every compact ID, unshifted and shifted

`r1` (0-8, `cmp #8`/`bhi`→pop) is this same compact index. `r2==0`
takes a third table (§3c below); `r2!=0` and Shift-RAM held takes the
shifted table; otherwise the unshifted table.

### Unshifted (`0x08017282`)

| Index | Control | What the scan shows | Tag |
|---|---|---|---|
| 0 | Hold | Loads several objects into stack slots; call site cut off in the 12-insn window, not resolved | H (incomplete) |
| 1 | Shift | `pop` — no-op in this table | S |
| 2 | Oct− | `pop` — no-op in this table | S |
| 3 | Oct+ | `pop` — no-op in this table | S |
| 4 | Tap | `pop` — no-op in this table | S |
| 5 | Rec | Writes `0x200010b6=1`; if `*0x20001124+0xf==1`, `bl 0x0801d7b6(r0=*r4, r1=5)` | S structure, H "arms Rec" semantic |
| 6 | Stop | Reads `+0x12`; on one value branches away, on `2` sets `r1=7` and `bl 0x0801d7b6` | S structure, H semantic |
| 7 | Play | Reads `+0x12`, then `+0x10`, gated comparisons, no target resolved in window | S structure, H semantic |
| 8 | Chord | `strb #1,[+0xd]`, then clears another byte via a second pointer — matches stock's "toggle Chord knobs vs CC knobs" (§3, `stock-shift-map.md`) | S structure, H (toggle) semantic — plausible P given the exact match to documented behavior, not tagging P without a live check |

Indices 1-4 being no-ops here is consistent, not a gap: Shift's own
state lives in `0x200010d2` (ticket B), and Oct/Tap are handled by the
18 Shift-RAM sites from ticket B, not this dispatcher.

### Shifted (`0x08017868`)

| Index | Control | What the scan shows | Tag | B site this may close |
|---|---|---|---|---|
| 0 | Shift+Hold | Reads `+0xc`; `0`→branch, `1`→`bl 0x08017180`, else pop | S structure, H "Chord on/off" semantic | B site 09 (same H candidate, same shape) |
| 1 | Shift+Shift | `pop` (nonsensical combo) | S |
| 2 | Shift+Oct− | `pop` — handled elsewhere (B's 18 Shift-RAM sites, not here) | S |
| 3 | Shift+Oct+ | `pop` — same | S |
| 4 | Shift+Tap | `pop` — same | S |
| 5 | Shift+Rec | Reads `+0xf`; if set, reads `voice_obj+0x49` (`0x200051cc+0x49`) | S structure, H "Record-append" semantic | — |
| 6 | Shift+Stop | Reads `+0xf`; if `==1`, `bl 0x08013788(r0=*r4)` | S structure, H "Clear last step" semantic | — |
| 7 | Shift+Play | Sets `r1=4`, `bl 0x08012334` | S structure, H "Restart from step 1" semantic | — |
| 8 | Shift+Chord | Reads `+0x15`, `cmp #2`, conditional `bl 0x08006ec8` | S structure, H "Control/CC bank cycle" semantic | — |

The H semantic tags above line up one-for-one with `stock-shift-map.md`
§2's stock-function descriptions for these same gestures — a plausible
match, not a live-verified one. Not promoting to P: no immediate here
matches a *known control ID*, only the shape matches a documented
behavior.

## 3. B unknowns — closed, partially closed, or still unknown

Per ticket instruction: close or mark "unknown stock secondary."

| B site | Containing fn | Resolution |
|---|---|---|
| 05 | `0x0800cd62`, inside `key_scan` | **Closed (structure).** Gated on Shift RAM (`0x200010d2`), then `0x200010b6` — the **same RAM the unshifted Rec case above writes** — then `0x20001084`. Reads as: key-scan behavior changes while Rec is armed and Shift is not held. **S** structure; exact behavior (Pattern-length record? realtime record gating?) stays **H** |
| 06 | `0x0800cfd8`, inside `key_scan` | **Closed (structure).** Gated on `get_arp_mode()==6` (Pattern mode specifically), then `0x20001084`, then Shift RAM. Pattern-mode-specific key-scan branch. **S** structure; semantic (Pattern length recording, per §5 "Rec held + keys 1-16... Pattern length") stays **H** |
| 08 | `0x08016afc`, fn `0x08016ac0` | **Still unknown stock secondary**, but structurally notable: Shift-gated, multi-field-checked shape similar in *family* to `mode_skip_apply`/`timediv_skip_apply` (Shift-held early exit, then several field checks). Not the same function as the C-ticket's third detent-object call (`0x08005d68`) — different address, don't conflate. **H** at most |
| 15 | `0x0801a078`, inside `shift_press_fn` | **Still unknown as a specific gesture**, but a role is now plausible: writes to `0x200010d6`, checked against Shift RAM (`cbnz`→skip) and `0x200010d0`. Reads as bookkeeping for "which other button is also down while Shift is held" — a plausible mechanism for detecting Shift+Oct−+Oct+ style multi-button combos (`stock-shift-map.md` §4). **H**, not confirmed which combo |
| 16 | `0x0801a11a`, inside `shift_press_fn` | Same shape as 15, different RAM slot (`0x200010d0` written, `0x200010d6` read). Same "multi-button bookkeeping" candidate. **H** |

Net: 2 of 5 (05, 06) move from "unknown" to "structurally closed" (gate
conditions fully shown); 08, 15, 16 stay unknown-as-a-named-gesture but
15/16 now have a plausible *mechanism* (H), not just a blank.

## 4. r2==0 table (§3c of the scan) — B sites 11/12 resolved

The scan's own note is explicit: **B's sites `0x08017cac` and
`0x08017cf0` sit inside this table's index 2 and index 3 bodies**, not
inside the shifted table B originally guessed at. Both gate on
`*0x20001124+0xf==1`, Shift RAM, and `0x2000116c`, then publish via
`0x0801d76c` with codes `(2,0)` then `(3,1)` (index 2) or `(3,0)` then
`(2,1)` (index 3) — matching B's own description exactly, just now with
confirmed containing context (this is the `r2==0` table, reached when
`panel_button_dispatch` is called with `r2==0` — a third calling
convention, not "shifted"). **S** for location; which physical gesture
calls with `r2==0` is not shown in this scan — **H**.

STATUS: done
