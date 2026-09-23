STATUS: done
AGENT: claude
TICKET: E
UPDATED: 2026-09-23T19:20+01:00
INPUT: firmware-re/notes/scans/E-keys.txt

# E-keys — callers of 0x0801b750 and the r2 each one passes

Read-only pass over `scans/E-keys.txt` only. `noteval` (`0x0801c3ca`) is
explicitly not walked, per the ticket instruction. Tags: **S** = shown
directly in this scan, **H** = plausible, not shown.

## 1. One diagram

```
key_scan (0x0800cc48)
  |-- site 01  0x0800cdfa  bl 0x0801b750   r2=0  (S: r2 literal shown)
  |-- site 02  0x0800cf30  bl 0x0801b750   r2=0  (S: r2 literal shown)
  |-- site 03  0x0800d064  bl 0x0801b750   r2=0  (S: r2 literal shown)

fn @ push 0x0800fa64 (not named in the catalog or recreate.py)
  \-- site 04  0x08010326  bl 0x0801b750   r2=1  (S: r2 literal shown)
                                            |
                                            v
                                   0x0801b750 (common entry, 20 insns
                                   shown; incoming r2 copied to sb at
                                   0x0801b75a, no further read of sb
                                   inside those 20)
```

All four static callers of `0x0801b750` in the whole image are these
four sites — confirmed by the scan's exhaustive `bl`-to search (§1: "4
hits. No others."). **S.**

## 2. Sites 01-03: inside key_scan, r2=0, S not H

The scan's own push-boundary evidence (§1: "Pushes: `0x0800cc48`
(key_scan) then next push `0x0800d152`. Sites 01-03 sit between those
two pushes") places all three calls inside the single function that
starts at `0x0800cc48` — the same function `model/C-loop.md` already
names `key_scan` (tentative), called once per main-loop pass with
`r0=0x20000674`. That naming is carried over from ticket C, not
re-derived by this scan. **S** for the containment (shown directly in
the scan's push-boundary trace).

Each of the three sites' twelve preceding instructions (§4) shows an
identical shape: pack a status/index byte pair into a stack buffer
(`orr r2,r0,#0x90` then `strb.w` at two adjacent stack offsets), then
`movs r2,#0` immediately before the `bl` — **r2=0 is a literal `movs`
two instructions before the call at all three sites, shown directly in
the scan**, not inferred. **S**, not H, for r2=0 at sites 01-03.

## 3. Site 04: r2=1, S, but containing function unnamed

Site 04 (`0x08010326`) sits after the previous `push 0x0800fa64` — that
push address has no name in the catalog or `recreate.py` (scan §2 states
this explicitly: "containing fn not named"). This model file does not
invent one; it stays "unnamed" here as well, per the ticket instruction
not to name a containing function the scan left unnamed.

The immediately-preceding instructions (`0x08010320  movs r2,#1`) show
`r2=1` as a literal `movs`, two instructions before the `bl` — same
directness as sites 01-03. **S** for r2=1 at site 04.

## 4. The r2=0-is-physical / r2=1-is-MIDI interpretation: H, not S

The scan shows **which literal each site passes**, not **what that
literal means**. Nothing in `scans/E-keys.txt`'s disassembled windows
contains an immediate, string, or comment establishing that `r2=0`
means "physical key scan" or `r2=1` means "MIDI input" — that mapping is
carried over from the address-catalog's "Input path (external source...
unverified by us)" note (`0x0801b750`: "r2=0 from physical key scanner,
r2=1 from either MIDI port"), which is explicitly an unverified external
claim, not something this scan independently confirms.

What this scan *does* newly support, structurally: three calls sharing
one containing function (`key_scan`) all pass the same literal (0), and
a fourth call from a different, unnamed containing function passes a
different literal (1) — a clean split that is *consistent* with a
physical-scan-vs-something-else story, but the scan supplies no evidence
for what "something else" is. **Tag this interpretation H.**

## 5. Entry point `0x0801b750` — confirmed shape, no further branch shown

Common entry, prologue through `push/sub/mov` chain, incoming `r2` moved
to `sb` at `0x0801b75a` (first use of the argument). The scan's 20-insn
window ends before any conditional branch reads `sb`; the scan notes the
first later read of that saved value is at `0x0801b8b2`
(`lsl.w r2,r2,sb`) — far outside this window, not walked. **S** for the
shape shown; no claim about what happens once `sb` is read, since that
is not in this scan.

## Net for HANDOFF layer 3 (keys bus)

Four callers into `0x0801b750`, three inside a named function
(`key_scan`, carried from ticket C), one inside an unnamed function.
Each call's literal `r2` value is directly confirmed (**S**); the
physical/MIDI meaning of that literal is not (**H**, external claim,
unchanged in confidence by this ticket). `noteval` and anything past
`sb`'s first real read remain out of scope, per instruction.

STATUS: done
