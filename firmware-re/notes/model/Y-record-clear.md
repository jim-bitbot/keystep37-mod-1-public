STATUS: done
AGENT: claude
TICKET: Y
UPDATED: 2026-09-23T23:05+01:00
INPUT: firmware-re/notes/scans/Y-record-rest.txt

# Y-record-clear — seq_step_store's remaining cases; hold-length-clear

Read-only pass over `scans/Y-record-rest.txt` only.

## 1. Case 3 — the real recording write, now fully shown

A 32-entry loop (`cmp r3,#0x1f`, i.e. 0-31, not the 0-127 note range
seen elsewhere) scanning `[r1+r3, #0xd]` for a match (`cmp r4,#1`) and,
on a hit, writing `0x80` into a cell at `(matched_index<<4)+1` — **the
same cell-plus-1 offset `J-voice.md` already identified as
`seq_step_gate`'s byte** (`(voice+step*8)*2+1`, 16-byte stride). Writing
literal `0x80` there sets **bit 7** — the retention/tie bit
`address-catalog.md`'s corrected understanding already covers (not the
old "gate" reading). **S** — this is genuinely the record-write path,
and it writes the retention bit directly, consistent with recording a
"hold/tie" state into a step. Not-matched path writes `0` instead (bit
clear). **S** for both branches.

## 2. Case 5 — a running accumulator, not a direct write

Reads `[r1,#0xb]` (the same "matched index" style field as case 3),
then in an 8-iteration loop (`cmp r2,#7`) **adds a delta** (`[r1,#0xd]`)
into an existing cell byte (`+1` offset again) rather than overwriting
it, then in a second pass copies from `[r1,#0xd]` into a second target
array at a different stride (`(r2*8+r2)*1`-ish addressing via `add.w`).
**S** for the accumulate-then-copy shape; role (velocity accumulation
across a repeated key? tie-chain building?) stays **H** — genuinely
more complex than a single-field store, not resolved further here.

## 3. Case 6 — writes voice-0 pitch, with tie/rest sentinels

Reads the target cell's gate byte (`+1`), masks off bit 7
(`tst.w r2,#0x7f`), and if the remaining bits are **zero** (empty
slot), compares the step index against the block's own `+0x400`
(Length field — **still H for the name**, per the L correction) — if
past length, writes `0x82`; if within length, writes `0x81`. **These
are exactly the tie/rest sentinel values `address-catalog.md` already
documents** (`0x81` = retains preceding note, `0x82` = starts no new
note). If the gate byte's low bits are **nonzero**, writes the raw
pitch value (`[r1,#0xd]`) instead. **S** — this is a clean, fully
confirmed write of the pitch-sentinel scheme directly from the
recorder, independently matching the existing catalog's external-source
sentinel table exactly.

## 4. `0x08016ac0` — resolved: it's a real function, `0x08016afc` is a case inside it

Q's finding stands, sharpened: `0x08016ac0` **is** a genuine function
start (`push {r4,r5,lr}`), and **`0x08016afc` is one of its own internal
targets** — reached when the function's own `r1==1` (`cmp r1,#1; beq
0x8016afc`). **So both were right in part**: `0x08016ac0` is real (B/F's
original citation), and `0x08016afc` is *also* a real entry in the
sense that the function branches there directly on `r1==1` — but it is
**not** independently callable from outside (no other static `bl`
targets `0x08016afc` directly; Q's "start-after-pop" reading was of a
different code path reaching that address by fallthrough after another
function's `pop`, not a `bl`). **Correcting Q's `Q-promote.md` claim**:
`0x08016afc` is best described as an internal branch target of
`0x08016ac0`, reached both by fallthrough (the case Q found) and by
`0x08016ac0`'s own `r1==1` branch — not a wholly separate function.
**S.**

## 5. Sites 15/16 and the `0x200010d0`/`0x200010d6` bookkeeping — closed, not hold-length-clear

Full reader lists for both RAM bytes (7 and 6 sites respectively) show
a consistent pattern: each is set to `1` on a press, read/cleared on a
release-adjacent path, and — critically — **each triggers a call to
`0x0800c5ee`** (already seen in F's sites 15/16) **when the *other*
byte is already set**. This is a genuine **two-button chord detector**:
`0x200010d0` tracks one key, `0x200010d6` tracks a second, and
`0x0800c5ee` fires when both are down together. **This is not the
Oct−+Oct+ hold-length-clear gesture** — nothing in either reader list
touches an Oct-related compact ID or `seq_step_store`. **S** for the
two-button-chord mechanism; **explicitly ruling out** this being
hold-length-clear, which stays unmapped. Worth noting for a future
ticket: `0x0800c5ee` itself is the next thing to walk if this mechanism
matters later.

## Net

Case 3 (real record write) and case 6 (pitch/sentinel write) are now
fully confirmed, both consistent with — and independently corroborating
— the existing catalog's sentinel table. Case 5 stays structurally
shown but semantically open. The `0x08016ac0`/`0x08016afc` relationship
is corrected from Q's read. Hold-length-clear (Shift+Oct−+Oct+) is
**not** at sites 15/16 — that gesture remains genuinely unmapped, now
with one less plausible location to re-check.

STATUS: done
