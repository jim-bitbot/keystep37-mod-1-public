STATUS: done
AGENT: claude
TICKET: A
UPDATED: 2026-09-22T21:38:02+01:00
INPUT: firmware-re/notes/scans/A-boot.txt; firmware-re/ghidra/recreate.py; firmware-re/notes/address-catalog.md

# A-objects — boot/ownership narrative from `scans/A-boot.txt`

Read-only pass over Cursor's raw disassembly. Every claim below cites the
address in `A-boot.txt` it comes from. Tags follow catalog convention:
**S** = structure from disassembly, **H** = hypothesis, existing **P**
rows are not re-tagged here. Nothing in this file is from `other repo/`
without saying so explicitly.

## 1. Boot sequence, now fully confirmed (was: name only)

`Reset_Handler` (`0x0801d310`) is fully disassembled in the scan. It:

1. Copies `.data`: flash `0x0801ef78` → RAM `0x20000000`..`0x200001f4`
   (0x1f4 = 500 bytes).
2. Zeroes `.bss`: RAM `0x200001f8`..`0x20005eac` (0x58b4 = 22708 bytes).
3. Calls, in order: clock/RCC init (`0x08006e20`, sets RCC bit 0, masks a
   config register with `0xf8ff0000`), `libc_init_array` (`0x0801d8c8`),
   then `bl 0x08016838` (falls straight through to `bx lr` after — this
   is effectively the last thing `Reset_Handler` does, i.e. `main`/
   post-init; not disassembled this ticket).

**This closes the single biggest open item from `prep-islands.md` §3**
(no `.bss` range existed anywhere in the catalog). **S.**

### The finding this unlocks: `FLAG_RAM` is provably outside `.bss`

`.bss` ends at `0x20005eac`. The address-catalog's `0x20005f00`
(`FLAG_RAM`, Euclidean-armed latch) is `0x54` bytes **past** that. SRAM
past `.bss` end is not touched by `Reset_Handler` at all — there is no
third loop, no second zero-fill range, nothing. This is not new *as a
conclusion* (HANDOFF already said "no 'free SRAM' until `.bss` is
catalogued... `0x20005F00` leftover is why e3b default-off was fake",
and `emulate_ks37.py`'s regression check already encodes it) — but it
was a hypothesis before this scan and is now a directly-read fact with
an exact byte offset. **S.**

## 2. `init_array` — 1 of 5 entries understood, 4 are a real gap

`libc_init_array` (`0x0801d8c8`) walks two `bl`-pointer arrays; the
first is empty (0 entries), the second is 5 words at
`0x0801ef58`..`0x0801ef6c`:

| Slot | Target (Thumb bit stripped) | Status |
|---|---|---|
| 1 | `0x08004208` | **Not examined.** |
| 2 | `0x08005e74` | **Not examined.** Six bytes before `chord_test_dispatch` (`0x08005df8`)? No — not adjacent, different region. Just noting proximity was checked and ruled out. |
| 3 | `0x08011528` | **Not examined.** |
| 4 | `0x080150b4` | Wrapper: `r0=1, r1=0xffff`, `bl 0x08014d08` — see §3. **S.** |
| 5 | `0x0801611a` | **Not examined.** |

Four of five top-level C++/C static initializers are completely
unwalked. Whatever they do happens **before** any code that depends on
`.bss` being zero can rely on it being *fully* initialized in the
app-level sense (the memory itself is zeroed by `Reset_Handler` before
`libc_init_array` runs, but these 5 calls are free to write into it
however they want, in whatever order they run). If a future object
ctor's RAM base doesn't show up anywhere in the 53-entry sweep in §3,
one of these four is the next place to look — not a sign the object
doesn't exist.

## 3. Ctor sweep `0x08014d08` — architecture, not per-object C++ init

One gated function, not a chain of individual static constructors.
Gate: `r0==1 && r1==0xffff`, else immediate return. Two static callers
exist:

- `0x080150b4` (init_array slot 4, `r0=1`) — **the only call that can
  reach the body.** **S.**
- `0x080150c2` — **not in `init_array`**, hardcodes `r0=0` via `movs
  r0,#0` immediately before the `bl`. Since the gate requires `r0==1`,
  this call, as coded, is a guaranteed no-op — it reaches the epilogue
  and returns without touching anything. I can't rule out some other
  caller reaching `0x08014d08` with a different `r0` that this scan
  didn't find, but the two *known* static call sites are "the real
  sweep" and "a dead stub." Worth a second pair of eyes before treating
  `0x080150c2` as meaningful. **S** (for what's shown), flagged
  uncertain beyond that.

Body is one flat sequence of 53 `bl`s, each preceded by literal/register
loads for `r0` (object base, almost always a fresh RAM address) and
sometimes `r1` (a kind byte, a peripheral base, or a previously-`bl`'d
object's address — a few sites chain: site 3's `r1` is site 2's `r0`,
etc.). This is a **single hand-written init table**, not compiler-
generated per-global-constructor calls (those would each get their own
`init_array` slot). **S.**

Three sites pass a GPIO peripheral base as `r1` (`0x40011800` GPIOE
site 1, `0x40010800` GPIOA site 9, `0x40011400` GPIOD site 12) —
hardware/pin setup, not application objects. Not walked further this
ticket; excluded from the object table below.

## 4. Objects identified with confidence (own disassembly, S)

### 4a. Five analog-knob objects, one shared ctor (`0x08004768`)

Ctor stores: vptr `0x0801dee4` at `+0`, kind byte (the `r1` arg) at
`+0x58`, zeroes `+0x59`/`+0x5a`/`+0x5c`/`+0x5e`, writes `7` to `+0x60`.
`analog_knob_process` (`0x08004918`) reads the kind back from `+0x58`
(not from a register — the existing catalog's phrasing "kind from +0x58,
not r1" is confirmed exactly).

| RAM | Kind | Ctor-sweep site | TBH target (if kind ≠ 0) |
|---|---|---|---|
| `0x20000468` | 0 | site 14, `0x08014dd2` | none — kind 0 is the "strip" branch at `0x0800498c` |
| `0x2000121c` | 1 | site 19, `0x08014df2` | `0x0800527c` |
| `0x20001294` | 2 | site 20, `0x08014dfa` | `0x080054c6` |
| `0x2000130c` | 3 | site 21, `0x08014e02` | `0x080056cc` |
| `0x20001384` | 4 | site 22, `0x08014e0a` | `0x080058cc` |

The existing catalog already says "`+0x58==0` = strip; `1..4` =
Type/Notes/Vel/Strum" for `analog_knob_process`. That ordering (Type=1,
Notes=2, Vel=3, Strum=4) is *not itself re-derived in this scan* — I'm
repeating the existing catalog claim, not confirming it independently,
so I'm not promoting it past what it already was. What *is* new here:
the five concrete RAM addresses, the shared ctor and its field layout,
and that kind 0's dedicated logic path (`0x0800498c`) checks the AutoTest
flag and Shift RAM before anything else (see §4c). **S** for the object/
kind/ctor structure; the CC-name assignment (Type/Notes/Vel/Strum)
stays exactly as confident as it already was (that catalog row is **P**).

Open gap: `knob_index_to_cc` names 5 CCs (98–102, Type/Notes/Vel/Strum/
**Rate**), but only 4 non-strip kinds (1–4) exist in this ctor family.
Rate (CC 102) is not one of these five objects — it's constructed
somewhere else, or handled differently. Not resolved this ticket.

### 4b. `strip_process_b`'s own object (`0x2000039c`)

Ctor `0x08004224` (sweep site 18), zeroes `+0x54`/`+0x55`/`+0x56`/`+0x58`/
`+0x5a`. The **only** static `bl` to `strip_process_b` (`0x08004388`) is
from `0x080157d0` — a separate call site from the five analog objects'
processing calls. This is a **distinct object from the kind-0 "strip"
analog object** (`0x20000468`) above, despite both being informally
"the strip" in prose elsewhere. Two different strip-shaped things exist
in this firmware; don't conflate them in later layers. **S.**

### 4c. Shared object `0x200051cc` confirmed to serve two roles

`analog_knob_process`, inside the kind-0 branch, reads
`ldr r2,[pc]; =0x200051cc; ldrb r2,[r2,#0xb9]` for the AutoTest flag
(`0x08004936`) before falling through to a Shift-RAM check
(`0x200010d2`, branches to `shift_strip_pickup` at `0x08004bf8` if
Shift held). The existing catalog already has `0x200051cc` as `voice_obj`
with fields `+0x4d`/`+0x4e`/`+0x4f`. Same exact address, now confirmed
from an independent code path (analog processing, not the voice/chord
code the existing entry came from) to also hold the AutoTest flag at
`+0xb9`. **One shared object with at least two unrelated-looking field
groups, not two separate objects that happen to share a name.** **S.**

### 4d. Three externally-claimed RAM addresses: existence now confirmed, role still not

`address-catalog.md`'s "Note-pool builder and sequence double-buffering"
section is filed entirely as "external source ... unverified by us."
Three of those addresses turn out to have real, own-disassembly-visible
ctors in this sweep:

| RAM | External-claimed name/role | Ctor (this scan) | Sweep site |
|---|---|---|---|
| `0x20004ed4` | `play_time_step_obj` — "consumes a step through, retains output pitches" | `0x08013e40` | 39 |
| `0x20002c4c` | `seq_block_ptrs` — `+0` current-block ptr, `+4` pending-block ptr | `0x0801306c` | 37 |
| `0x2000063c` | `arp_note_pool_builder` target | `0x0801161c` | 44 |
| `0x20002dfc` + `0x20002d0c` | primary pool / deferred-release pool | **same ctor**, `0x08013c9a` | 42, 43 |

The last row is the most useful independent corroboration: the external
source describes these two addresses as a matched pair (primary vs.
deferred pool of the same kind of thing), and this scan shows, with zero
reference to the external claim, that **both are built by the identical
ctor function** — exactly the pattern you'd expect for two instances of
one pool type. That's real evidence the *shape* of the external claim is
right, from a source that has nothing to do with it.

**Important distinction, don't blur it:** "an object exists at this RAM
address, built by this ctor" is now **S** for all four rows. "That
object does what the external source says it does" is still **H** —
none of the ctors themselves say what the object is *for*; that
interpretation is still 100% from the unverified external source (and
per `prep-islands.md` §0, that source's filenames don't even reliably
describe their own contents, so treat the semantic labels with real
caution even though the addresses now check out).

## 5. Candidate leads — H, not proposed as catalog rows yet

Flagging for whoever picks up layer 1/3 next; not confident enough to
propose to Cursor as catalog rows this ticket.

- **`0x20001e04`** (ctor `0x0801b02c`, sweep site 50) is loaded by name
  in three of the four analog TBH kind-handlers (kinds 1/2/3 call
  `0x0801b246`/`0x0801b250`/`0x0801b278` with `r0` = this address; kind 4
  stores directly to `+0x50` of it). The existing catalog's scale-mask
  entry, `0x20001e3a`, is `0x36` bytes past this base — plausibly the
  *same object*, scale mask at offset `+0x36`. Not confirmed — I have
  not traced the actual `ldrh` at `0x20001e3a` back to a base+offset
  computation, just noted the addresses are close and both touched by
  knob-kind code. **H.**
- **`0x20001180`** (ctor `0x08014be8`, site 52, `r1` = a function
  pointer `0x08006ec9`/Thumb `0x08006ec8`) is one of the five literals
  in `voice_interval_load`'s literal pool (`0x0801bd38`) per the
  existing catalog. Candidate for "the chord/voice settings object,"
  unconfirmed. **H.**
- Sweep site 38 (`dest 0x08014416`, RAM `0x200050c0`) is **2 bytes
  before** `recreate.py`'s `seq_step_store` (`0x08014418`). Either this
  is a distinct tiny ctor stub immediately preceding `seq_step_store` in
  flash for the same object, or one of the two addresses is slightly
  off. Worth Cursor double-checking the actual function boundary at
  `0x08014416` before anyone treats `0x200050c0` as "the recorder's
  object" with confidence. **H, flagging a possible off-by-a-couple-
  bytes discrepancy, not asserting which side is wrong.**

## 6. Sites not walked this ticket

Sweep sites 2–8, 10, 11, 13, 15–17, 23, 33–36, 45–49 (partially), 51, 53
and the nine `0x08019f8c` instances (sites 24–32, see below) are listed
raw in `scans/A-boot.txt` §2 with RAM addresses but no role assigned
here. Not claiming they're unimportant — just not walked yet.

One exception worth flagging as a strong lead for whoever does walk it:
**sites 24–32**, all the same ctor (`0x08019f8c`), store `r1` at object
`+0xd` and `r2` at `+0xe`; the nine instances use `r1 = 0..8` across
RAM `0x20000388`, `0x20000564`, `0x2000042c`, `0x20000440`, `0x200005e4`,
`0x200004e0`, `0x20000578`, `0x20000454`, `0x20000374` (in sweep order,
kind 0→8). The existing catalog's `id_to_index` is described as
"Control ID → compact 0–7 (hold/shift/octm/octp/tap/rec/stop/play); else
8" — **exactly nine categories, 0 through 8.** A ctor family of exactly
nine identically-shaped small objects tagged 0–8 is a strong-looking
match for "one object per compact button ID." **Not proposed as a
catalog row** because I have not traced any *reader* of these nine
objects back into `button_debounce` / `panel_button_dispatch` — the
match is structural (count + numbering), not a confirmed data-flow link.
**H**, but a good one for Wave 3.

STATUS: done
