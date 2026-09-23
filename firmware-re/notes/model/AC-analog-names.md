STATUS: done
AGENT: claude
TICKET: AC
UPDATED: 2026-09-24T01:05+01:00 (§3 closed per ticket AM's raw table decode)
INPUT: firmware-re/notes/scans/AC-analog-names.txt; scans/AM-kind-tbb.txt

# AC-analog-names — kind-0/strip maps to Rate's CC; kind 1-4 order still H

Read-only pass over `scans/AC-analog-names.txt` only.

## 1. knob_index_to_cc has exactly one static caller — closes a real gap

`0x08004978` (inside `analog_knob_process`'s AutoTest emit path,
`0x08004974`-`0x08004982`) is the **only** static call to
`knob_index_to_cc`. This means the kind-byte-to-CC mapping happens in
exactly one place, always fed the raw `+0x58` kind byte — not five
separate hardcoded call sites as might be assumed. **S.**

## 2. The default case — S, unambiguous regardless of table-byte decode

`knob_index_to_cc`'s body: `subs r0,#1; cmp r0,#3; bhi #0x80060b0`
(out-of-range) `→ movs r0,#0x66; bx lr` (**CC 102, Rate**). This branch
doesn't depend on decoding the TBB's table bytes — it's a direct,
unambiguous comparison. **Kind byte `0` (the strip/AutoTest path) and
any kind `≥5` map to Rate's CC (`0x66`) as the fallback.** This is a
genuine, concrete finding: kind 0 was previously left "unknown" for
panel name (`D-analog.md`); it isn't Pitch or Mod as might be assumed
from "it's a strip" — **on this specific AutoTest path, it returns
Rate's own CC.** **S.**

## 3. Kind 1-4 → CC mapping — CLOSED by ticket AM, confirms the old order exactly

**Correction/closure**: I was right to flag this as unresolved without
the raw table bytes, and right that it shouldn't be asserted as S — but
my own guess at the likely mapping was wrong. Ticket AM decoded the
actual table (`0x080060ac`: bytes `0a 04 06 08`) and verified every
target address by arithmetic (`table_base + byte*2`):

| Kind | Table byte | Target | CC |
|---|---|---|---|
| 1 | `0x0a` | `0x080060c0` | `0x62` **Type** |
| 2 | `0x04` | `0x080060b4` | `0x63` **Notes** |
| 3 | `0x06` | `0x080060b8` | `0x64` **Vel** |
| 4 | `0x08` | `0x080060bc` | `0x65` **Strum** |
| 0 / ≥5 | (default) | `0x080060b0` | `0x66` **Rate** |

**S — this confirms the old assumed order exactly** (Type=1, Notes=2,
Vel=3, Strum=4), which `A-objects.md` had flagged as "not re-derived
independently." My own speculative alternative ordering in the
original version of this section was wrong; removing it rather than
leaving it as a live hypothesis.

## 4. test20_cc_value's body — confirms heap-backed reply path, not new

Fully disassembled: checks `0x20000214` (heap-ish pointer, seen
elsewhere), allocates via `0x801d862`/`0x8010b30` if needed. Matches
existing catalog description of the Test-20 CC emit mechanism. **S,**
no correction.

## 5. Object pc-rel counts — confirms D/S's picture, no new objects

Kinds 1-4, kind-0/strip, the Rate candidate (`0x2000058c`), and
`strip_b` all show 4-5 pc-rel load sites each, consistent with
`app_main_loop`'s known once-per-pass polling plus ctor-sweep
references. No new object found. **S.**

## Net

Closes the "is kind 0 Pitch/Mod or something else" question with a
real, unambiguous negative-then-positive: it's not directly named, but
its AutoTest CC fallback is Rate's own code, not Pitch's or Mod's.
Leaves the specific kind1-4 ordering as a strengthened-but-not-closed
hypothesis, honestly flagged as needing proper TBB table-byte
extraction, not guessed here.

STATUS: done
