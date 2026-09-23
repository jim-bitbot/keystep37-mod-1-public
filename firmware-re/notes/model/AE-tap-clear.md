STATUS: done
AGENT: claude
TICKET: AE
UPDATED: 2026-09-24T00:20+01:00
INPUT: firmware-re/notes/scans/AE-tap-clear.txt

# AE-tap-clear — Tap reconfirmed absent from dispatch; hold-length-clear still not found

Read-only pass over `scans/AE-tap-clear.txt` only.

## 1. Tap (0x67) — no new dispatch site found

All `0x67` immediates trace to already-known places: `id_to_index`/
`index_to_id` (F), a couple of unrelated `strb [r0,#0x67]` struct-field
writes on other objects (not control-ID related — offsets, not
immediates), and one `adds r1,#0x67` (pointer arithmetic, not a
compare). **No additional Tap-handling code found beyond what F/N
already mapped.** **S** — reinforces `N-sync.md`'s conclusion, doesn't
change it.

## 2. B's sites 07/17, full bodies — matches my own independent capstone spot-check exactly

This scan's dump of `0x08016982` (site 07) and `0x0801a288` (site 17)
is **byte-for-byte consistent** with `lead-oct-combo.md`'s own
independent capstone investigation: site 17 arms `0x200010b4=6` when
Shift is **not** held; site 07's containing function gates on Shift
**held** plus `[r4,#0xb]` plus `0x200010b4` nonzero, incrementing a
counter capped near 3. **Cross-validates that side investigation** —
two independently-run analyses (Cursor's scripted scan, my own ad hoc
capstone) agree exactly on the instruction sequence. **S.**

## 3. Simultaneous Oct−/Oct+ check — not found, same as the side investigation

Per the ticket's own stated goal (find a function checking Oct− and
Oct+ compact-ID state **together**): none of the sites this scan
covers (mode/timediv skip-apply, sites 07/17, the two shifted-TBH
button cases at `0x08017cac`/`0x08017cf0`, key_scan's site 05/06,
`panel_button_dispatch`'s unshifted TBH, Shift press/release) reads
both Oct states at once. **S for the negative** — this is now the
*third* independent pass (Y's sites-15/16 check, my own side
investigation, and this scripted scan) that fails to find a
simultaneous-both-held check anywhere in the Shift-RAM/button-dispatch
territory this project has mapped.

## 4. Rec+keys / Rec+Tap combo confirmation — already known, reconfirms X

The `0x08017298` (Stop, unshifted index 6) double-publish with codes
`7` and `5` shown here matches `X-selectors.md` exactly. No new
information; consistent cross-check.

## Net — hold-length-clear remains genuinely unmapped, now more thoroughly ruled out

Three independent searches (Y, my own side investigation, this ticket)
have now covered: B's sites 07/08/15/16/17, the shifted button-dispatch
TBH, the `r2==0` table, mode/timediv skip-apply, and Tap's own
handling — **none contain a simultaneous Oct−+Oct+ check.** This is a
strong, multiply-confirmed negative, not an unexplored gap. Whoever
picks this up next should look **outside** the button-dispatch/Shift-RAM
territory entirely — candidate: inside `key_scan` itself (§05/06's
containing function, `0x0800cc48`) on a path this project hasn't
walked, since that function already reads Shift RAM for unrelated
reasons (ticket F).

STATUS: done
