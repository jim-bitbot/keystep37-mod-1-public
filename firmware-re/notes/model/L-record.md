STATUS: done
AGENT: claude
TICKET: L
UPDATED: 2026-09-23T22:15+01:00 (corrected per Cursor's review — field
names had been overclaimed to S alongside their confirmed store sites)
INPUT: firmware-re/notes/scans/L-record.txt

# L-record — store entry and the Rec flag

Read-only pass over `scans/L-record.txt` only.

## 1. Entry — the A/G "2-byte gap" is fully closed, not just resolved

`0x08014416` (`bx lr`) **is a real ctor-sweep call target** — this
scan shows its one static caller: the ctor sweep itself, `r0 =
0x200050c0`. It just does nothing (a no-op ctor for that object). This
confirms `G-objects.md`'s "site 38... trivial `bx lr`, no store" and adds
the missing half: it's not a stray address, it's a genuinely-called,
genuinely-inert ctor. **S.** `seq_step_store` starts at the next
halfword (`0x08014418`) as already known; its one static caller is
`0x080065e4`, now dumped: `r0 = *0x200010b8`, `r1 = r6` (source of `r6`
not shown).

## 2. seq_step_store body — CORRECTED: stores are S, the field names are still H

**Correction (Cursor's review caught this — my original wording was
wrong):** The function indexes a pointer array at `0x200010fc` by
`[r1,#0xa]-1`, loads the target block, then a **TBB on
`([r1,#1]-0x60)`** with cases 0-6. **The stores themselves are S** —
this scan directly shows three `strb`s to `+0x400`/`+0x401`/`+0x402`.
**The names Length/Swing/Gate are not shown anywhere in this scan** —
those names are still `address-catalog.md`'s old "external source,
unverified by us" table. I incorrectly wrote "promoted to S" for the
*names*, when only the *store sites* were promoted. Reverting the
names to H.

| Case | Byte value (index+0x60) | Target field | Store | Name |
|---|---|---|---|---|
| 0 | `0x60` | `[r0,#0x400]` | S | H (was called "Length") |
| 1 | `0x61` | `[r0,#0x401]` | S | H (was called "Swing") |
| 2 | `0x62` | `[r0,#0x402]` | S | H (was called "Gate") |
| 3 | `0x63` | loop on `[r1,#0xb]` | S (site), role not resolved | — |
| 4 | `0x64` | (no cell store) | falls to common tail | — |

**Worth flagging explicitly, not glossing over**: case 2's selector
byte is `0x62` — **the same immediate as the Type knob's CC**
(`knob_index_to_cc`'s `0x62`-`0x66` = Type/Notes/Vel/Strum/Rate,
existing catalog). That's not proof the "Gate" name is wrong, but it's
a real reason for caution beyond just "unconfirmed" — this dispatch
may share an ID namespace with the knob CCs rather than being a
distinct Length/Swing/Gate scheme. Not resolved here.

Common tail (cases 0-2 and 4): writes `1` to `0x200010d5` and `0xa` to
`0x200010a9` — two flags, not otherwise named. **S** existence, **H**
role.

## 3. Rec — compact index 5, now a closed story

Unshifted Rec press (`0x0801780c`, from ticket F): `0x200010b6 = 1`,
then `bl 0x0801d7b6(r1=5)` and `bl 0x0801d76c(r1=5)`. The `r2==0` table's
own index-5 case (`0x08017b1a`, already in F's scan) clears the same
byte to `0`. **This makes `0x200010b6` a confirmed Rec-armed flag, not
just structurally gated** — F's B-site-05 finding ("gated on Shift +
`0x200010b6`") is **promoted from H to S**: that byte's identity is now
directly tied to Rec press/release, not merely "some flag."

**Shift+Rec is a genuinely different path**, confirmed structurally:
the shifted-table Rec case (`0x080178c8`) does **not** touch
`0x200010b6` and does **not** `bl seq_step_store` in its first 12
insns — consistent with `stock-shift-map.md`'s Shift+Rec being
"Record-append," a different function from plain Rec's Pattern-length
behavior, not the same handler with a Shift-gated branch.

**New cross-reference**: `play_time_step` itself reads `0x200010b6`
(`0x08013f1c`, branches on it) — the player's own step logic changes
behavior while Rec is armed. This is the mechanism side of "Rec held +
keys 1-16 = Pattern length" (`stock-shift-map.md` §5): Rec-armed state
feeds both the key-scan gating (F's site 05) and the player itself.
**S** for the read sites; the exact behavioral difference isn't walked
in this scan.

## 4. Missing

Rec LED write: not found in this scan's windows. Hold-length-clear
(Shift + both Oct, per `stock-shift-map.md` §4) is not in this scan —
left for whoever revisits, not modeled here as absent-from-firmware.

## Net for HANDOFF layer 3/5 (recorder)

Record path: `seq_step_store` entry confirmed, one caller confirmed,
header field *store sites* `+0x400/+0x401/+0x402` confirmed S — their
Length/Swing/Gate *names* stay H, corrected from an earlier overclaim.
Rec-armed flag
(`0x200010b6`) identity confirmed via press/release symmetry, and its
read sites in both `key_scan` and `play_time_step` are now known,
narrowing "how Rec changes playback" to two concrete places to walk
next, rather than an open question.

STATUS: done
