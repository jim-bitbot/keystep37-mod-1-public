# KeyStep 37 — handoff

Read this first in a new session. Addresses:
[../firmware-re/notes/address-catalog.md](../firmware-re/notes/address-catalog.md).
Image packaging: [../firmware-re/notes/led-header.md](../firmware-re/notes/led-header.md).
MCU / holes: [../firmware-re/notes/flash-map.md](../firmware-re/notes/flash-map.md).
Panel occupancy: [../firmware-re/notes/stock-shift-map.md](../firmware-re/notes/stock-shift-map.md).
Narrative log: [../firmware-re/notes/findings-2026-09-20.md](../firmware-re/notes/findings-2026-09-20.md)
(chronological; do not take mid-file “not yet” as current).
General method: [ARTURIA-FIRMWARE-RE-GUIDE.md](ARTURIA-FIRMWARE-RE-GUIDE.md).
Repo overview: [../README.md](../README.md).
**Two agents, same repo:** [two-agent-protocol.md](two-agent-protocol.md)
(Cursor writes `notes/scans/`; Claude writes `notes/model/`; catalog is
Cursor-only).

## Resume here — 2026-09-22 — understand stock 1.1.6.579

**Current goal:** a machine model of application 1.1.6.579, not a new
feature. Euclidean restripe, latch, and scale-chord (e0b…c2) are
**future work** — packaged, partially hear-tested, frozen. Do not rebuild
them. Do not live-flash them. Do not occupancy-listen again.

**Flash without MCC is closed.** Rec+Stop+Play, leave `0291` on Windows,
`./scripts/flash-win.sh` (parser is this repo’s `led_codec.py`). MCC is
recovery only. Do not attach `0291` to WSL. Do not resurrect
`flash_bl_wsl.sh`. Do not reverse the bootloader. Optional later: on-device
read-back vs the `.led` — not required to study the extract.

Analyze
`firmware-re/firmware-images/keystep37_1.1.6.579_flash.bin`
(base `0x08000000`). App Thumb `0x08004000`–`0x0801F400`. ~40 named
functions in `ghidra/recreate.py` are **islands**, not a map.

Build the model in this order (wire constant → `cmp` imm → correct
function boundary → callers). Occupancy CCs **are** firmware control IDs
(§10 of `stock-shift-map.md`).

1. **Boot and ownership** — `Reset_Handler` `.data`/`.bss`, ctor sweep
   (~`0x08014d08`). Objects, vtables, RAM bases. No “free SRAM” until
   `.bss` is catalogued (`0x20005F00` leftover is why e3b default-off
   was fake).
2. **Main loop and IRQs** — who calls analog process, debounce, tick, USB
   parse. Test-20 is object `+0xb9`, not “how MIDI works.”
3. **Three input buses** — keys (`0x0801b750`), buttons (compact IDs +
   Shift RAM `0x200010d2`), analog (`0x08004918` / strip `0x08004388`).
   Walk each ID to its **stock handler**. Occupancy named the panel;
   firmware still has not named most Shift secondaries (18 Shift-RAM
   loads).
4. **Time** — `arp_seq_tick` until clock, Time Div, swing, and current
   step are one diagram.
5. **Voice out** — step cell → pitch/vel/tie → Note-On/Off → USB/DIN.
   Pitch-gate at `0x08013ebc` is the emission check; `seq_step_gate` bit 7
   is retention. Write this as architecture, not as a hook target.
6. **Protocol overlay** — GET/SET `globalParamId` on top of (3)–(5).

Deliverable of this phase: catalog rows with P/S/H/X, growing
`recreate.py` **only** for confirmed names, a current-state map — not a
`.led`. `findings-2026-09-20.md` stays a log.

Do not steal Shift+keys 1–16. Chart holes that looked free and are not:
Shift+Tap (tempo), Chord-then-Rec (Rec LED). Shift+Mod strip is the
surviving latch **candidate for later**, not a patch to write now.

Older “Resume here” sections below are history.

**Start work:** both agents Wave 1 in [two-agent-protocol.md](two-agent-protocol.md)
§5. Cursor: `firmware-re/notes/scans/A-boot.txt`. Claude:
`firmware-re/notes/model/prep-islands.md`. Do not both edit the catalog.

## Resume here — 2026-09-22 — cycle harness + occupancy map

**Superseded the same day** by “understand stock 1.1.6.579”. Occupancy
**did** complete (MCC Test-20 pastes + eyes-on): map is
`stock-shift-map.md`. Shift+Tap and Chord-then-Rec are **occupied**, not
holes. Cycle leftover-FLAG FAIL is intended until a **future** BSS-init.

Inner loop was Unicorn. Outer loop was Rec+Stop+Play. **No live flash
in that occupancy work.** Do **not** paste a feature `--live` cycle.
`cycle.sh` refuses feature levels and `--live` unless
`KS37_FEATURE_FLASH=YES-FEATURE-FLASH`.

Allowed this phase:

```
./scripts/cycle.sh
```

Historical (FUTURE — not a command to run; `cycle.sh` exits 3):
`cycle.sh` with a feature level (`e0b` … `c2`) and/or `--live`.

`emulate_ks37.py all` now plants leftover `0xFF` at `FLAG_RAM`
`0x20005F00` (e3b miss: unused SRAM, not BSS-zeroed). That test FAILs
until a future patch BSS-inits the flag. Cycle **aborts** on unicorn
FAIL — no MIDI, no flash. Do not resurrect `flash_bl_wsl.sh`. Do not
attach `0291` to WSL. `--live` waits for `0291`, stops AutoAttach,
`diag_unlock.py` then `flash-win.sh --already-unlocked`, waits
`0219`/`1c76:0219`, starts AutoAttach, prints “Hold F, Hold on”,
`listen_ks37.py`. Default is no `--live`.

Occupancy (all buttons including 3-at-once) lives in
[`firmware-re/notes/stock-shift-map.md`](../firmware-re/notes/stock-shift-map.md),
checked against KS37 1.1 EN and the original KeyStep 1.1.0.28 Shift FAQ.
**Shift + Oct− + Oct+** while Seq is stopped is **clear all notes, keep
length** (missing from the KS37 chart; **confirmed live** 2026-09-22).
Same chord in Arp limits multi-octave range to held notes (§5.5). Live
column is filled (MCC Test-20 + eyes-on). Historical occupancy command
(do not re-run as current work):

```
./scripts/occupancy-listen.sh --test20
```

That arms MCC Test-20 each step so Shift/Oct/Rec/combos dump raw CCs.
Log: `firmware-re/captures/occupancy/`. **Done 2026-09-22** (Jim pasted
MCC Test-20; eyes-on stock for holes). Do not re-run as current work.

## Resume here — 2026-09-22 — flash-win.sh live PASS (e3b, same image)

WSL `./scripts/flash-win.sh --already-bootloader --already-unlocked --confirm YES-FLASH` dumped `e3b_pitchgate_shift.led` via Windows `py.exe` / `flash_win.py` / this repo’s `led_codec.py`. Unlock `F0 51 F7`, 176 segments, `1A`×175, **`F0 77 F7`**, 71.8 s, `longerror=0`. Re-enum **`1c76:0219`** Shared (VID quirk). AutoAttach was stopped. ALSA `flash_bl_wsl.sh` stays refused. Next live dump is the same wrapper; MCC still recovery.

## Resume here — 2026-09-22 — flash from WSL via Windows py.exe

Claude rewired PC_1 `flash_win.py` to import WSL `led_codec.py`
(`\\wsl$\Ubuntu\home\jimcu\dev\KeyStep37_Mod_1\firmware-re\scripts`).
`led_records.py` is gone. Dry-run segment counts match the old parser
(stock 176 / 110 data / 66 fill).

From this repo, no ALSA send. Parser + rebuild stay here; WinMM stays
Windows:

```
./scripts/flash-win.sh
./scripts/flash-win.sh /mnt/c/Users/jimcu/KeystepFlash/e0b_pitchgate_3in8.led
```

Default is `--dry-run`. Live still needs Rec+Stop+Play, AutoAttach off,
device on Windows, then `--already-bootloader --confirm YES-FLASH`.
`flash_bl_wsl.sh` now refuses.

## Resume here — 2026-09-22 — Shift+C/D is stock MIDI CH; e3b latch is wrong

Jim is right. Manual 1.1 §3.6.1 / §3.6.6: **Shift + keys 1–16 =
Keyboard MIDI CH** (and reset Kbd Play CH). Key 1 = C2 = MIDI 36 =
channel 1. Key 2 = C♯2 = MIDI 37 = channel 2. e3b stole that combo.
Hear-tests that looked like “latch ignored” were changing MIDI channel.
The HANDOFF line “MIDI CH stays MCC / User Channel. Shift+1/2 are free”
is **false** — delete that assumption.

All 37 Shift+keys are silkscreened (MIDI CH, Gate, Swing, Mono/Overdub,
Scale). Every Shift+button in the chart is taken too. Full inventory:
[`firmware-re/notes/stock-shift-map.md`](../firmware-re/notes/stock-shift-map.md).
Firmware handlers for those secondaries were **never mapped** (we only
had raw Test-20 CCs).

e3b is not done. Do not reflash it. Next latch needs a **novel unused**
gesture (candidates: Chord-then-Rec, or Shift+Tap if the router is a
no-op). Do not build until that pair is mapped in the button path.

## Resume here — 2026-09-22 (e3b hear-test) — latch not off at boot

`e3-off` dump `e3-off-20260922-165641.txt`: scorer said PASS every-step
(93%) using 2T as 1 step. Wall IOI is **95% 3-in-8** at T≈157 ms.
`FLAG_RAM` `0x20005F00` is unused SRAM, not BSS-zeroed — default-off is
not guaranteed after reset. `e3-on` dump `e3-on-20260922-165803.txt`: **100% 3-in-8**, 0% every-step.
Euclidean path confirmed. `e3-off` retry `e3-off-20260922-165902.txt`: scorer PASS is bogus
(`eu<0.4` on the 2T grid). Wall IOI still **99% 3-in-8**. Shift+D did
not disarm this capture (gesture likely missed during the explanation).
Shift+D (MIDI 38) was the wrong key. Patch KEY_OFF is MIDI **37** =
C# next to lowest C, not D. `e3-off` C# retry `e3-off-20260922-170241.txt`: still **92% 3-in-8**
(13 hits, late play). Shift-off gesture not proven. Next is patch:
why `shift_note_hook` may not see panel Shift+C# (MIDI 37), and
`FLAG_RAM` boot value.

## Resume here — 2026-09-22 (e3b built, not flashed)

`e3b_pitchgate_shift.led` is in KeystepFlash. Pitch-gate + `STEP_CTR_RAM`,
default **off** (stock). Shift+C2 (MIDI 36) arms fixed 3-in-8; Shift+D2
(37) disarms. Not hits-from-slot — Pattern one-key would hide the latch.
Unicorn: latch-off every-step, latch-on 3-in-8, Shift FLAG set/clear OK.
**Do not flash old `e3_euclid_shift.led`.** Windows PC_1: Rec+Stop+Play,
`flash_win.py` `C:\Users\jimcu\KeystepFlash\e3b_pitchgate_shift.led`.
Then WSL `listen_ks37.py e3-off --clocks` (every-step) then Shift+1 and
`e3-on --clocks` (3,3,2). MIDI CH stays MCC / User Channel.

## Resume here — 2026-09-22 (e1b live listen) — OK-ish every-step k=n

Live `listen_ks37.py e1 --clocks` after PC_1 flash: **97% every-step, 0%
3-in-8.** Dump `e1-20260922-164745.txt`. This is the Pattern one-key A/B
vs e0b's 3,3,2 — slot fully gated, k=n. e1b is live. Do not reflash.
Next: E3 latch on the same pitch-gate path, or a Seq-slot rest test if
you want an audible 4-in-8 from e1b.

## Resume here — 2026-09-22 (e1b built, not flashed)

`e1b_pitchgate_hits.led` is in KeystepFlash. Same pitch-gate hook as e0b
(`0x08013ec2`, `STEP_CTR_RAM`); `length` = slot `+0x400`, `hits` = count
of voice-0 pitches that are not `0x81`/`0x82`/`0xFF`. Unicorn: 4-in-8
and 8-in-8 OK; `emulate_ks37.py all` OK. **Do not flash old
`e1_euclid_hits.led`.** Windows PC_1: Rec+Stop+Play, `flash_win.py`
`C:\Users\jimcu\KeystepFlash\e1b_pitchgate_hits.led`. Then WSL
`listen_ks37.py e1 --clocks`. Pattern + one held key is likely
**every-step** (k=n, all pitches real) — that is the A/B vs e0b's 3,3,2,
not a fail. A Seq slot with rests is the 4-in-8 hear-test.

## Resume here — 2026-09-22 (live listen) — e0b PASS 99% 3-in-8

Live `listen_ks37.py e0 --seconds 40 --clocks` on WSL app `1c75:0219`,
Arp/Pattern, one held F after a setup gap: **99% 3-in-8, 0% every-step.**
Dump `firmware-re/captures/listen/e0-20260922-163130.txt` (1301 events,
F8 clocks present). First 3.7 s is the key-hold before the arp locked;
from then IOI is `3,3,2` at T≈155 ms. **e0b is done on hardware, not
just from re-scored dumps.** Do not reflash e0b. Do not flash old e1/e3
(those still hook `seq_step_gate`). Next feature: rebuild E1
(hits-from-slot) on `pitch_gate_wrap` + `STEP_CTR_RAM`.

## Resume here — 2026-09-22 (verification) — e0b 3-in-8 was real; the scorer lied

**Do not flash a new patch for the density contradiction.** Same image,
same dumps as last night. The `1,2,2` captures and the ~90% every-step
capture are the same 3-in-8 grid (`3,3,2` at T≈155 ms). `listen_ks37.py`
took the 2T gap (~310 ms) as one step, then `round(3T/2T)` of 1.49
became 1. Re-scored with that fixed: `e0-20260922-151333.txt` (the "90%"
file) is 100% 3-in-8; `e0-20260922-141812.txt` / `142418` / `150355` /
`155849` are 100% 3-in-8. The only true every-step dump is
`e0-20260922-141445.txt` (pre-counter-fix slot-B, native step domain).

Also closed tonight, from the flash extract:

- Writer `0x080130cc` has no 0x81/0x82 branch. Pattern's loop does not
  emit native rests for a held key.
- CC21 = internal mode + 1 (`adds r1,r0,#1` then `movs r0,#0x15` at
  `0x08005a72`). Panel Pattern (CC21=7) is TBH case 6, the semi-random
  builder. That mapping is no longer unconfirmed.
- `play_time_step` has two call sites. Arp uses `0x08012ec0` once per
  step change. `0x08011ff0` is a different object, gated on
  `*(0x20001124)+0x10==2` — not a second Arp tick.

Scorer is fixed in `listen_ks37.py` (`_e0_grid`). Next live listen can
use `--clocks` if you want F8 as the grid; the flashed e0b image does
not need rebuilding for this.

## Resume here — 2026-09-21 (night) — E0 flashes and boots clean, but has ZERO audible effect

**Do not re-flash anything before reading this.** The packaging bug from
the earlier "Resume here" section below is genuinely fixed and
re-verified twice (once by Claude statically, once live by Windows/Cursor)
— the *transport and boot* problem is solved. There is a **second,
separate, still-open problem**: the patch has no observable effect on the
device's actual behavior.

**What's now confirmed working, independently, twice over:**

- Windows dump lab flashed the rebuilt `e0_euclid_3in8.led` (Rec+Stop+Play
  entry, `flash_win.py`, one-shot `productKey` unlock). Got `F0 77 F7`,
  device re-enumerated to app mode. (It shows as `1c76:0219` right after
  this specific flash path — confirmed benign: the *identical* stock file,
  flashed the same way, produces the same `1c76` quirk, verified via
  `usbipd list` naming it "Arturia KeyStep 37" correctly. Not a different
  device, not corruption.)
- Claude independently re-parsed the exact file that got flashed (own
  from-scratch parser, not reusing `led_codec.py`): 176/176 segments,
  zero checksum errors, zero footer-address mismatches (the specific bug
  class that caused the earlier brick). Diffed extracted flash against
  known-good stock: exactly 5 changed regions (3× 4-byte hook redirects +
  the 92-byte patch page + the 2-byte program checksum), **vector table
  byte-identical to stock**. Disassembled the patch page: matches
  `ks37_patch.S` source exactly, unconditional (this is genuinely the
  E0/"always-on" build, not an accidentally-latched variant).

**But the live hear-test (`listen_ks37.py e0`) fails clean, three times,
under three different conditions:**

1. Arp/Pattern, **one held key**: 24 hits, IOI all `1` (every step),
   0% match to 3-in-8. `VERDICT FAIL — still stock density`.
2. Arp/Pattern, **3-4 held keys (chord)**: same result, 0% match. This
   rules out the "single note bypasses per-voice gating" hypothesis
   Claude had proposed after test 1 — multiple voices genuinely cycling,
   still zero gating effect.
3. **Sequence mode** (same shared `play_time_step`/`seq_step_gate` code
   path per the address catalog): mixed IOI pattern (`2,1,2,2,1,...`),
   tool verdict `UNCLEAR`. **Not a clean test** — factory sequences are
   already known (from months-old testing in this same project) to have
   their own programmed rests/ties, so a mixed pattern here doesn't
   distinguish "our patch did something" from "the sequence already had
   gaps." Don't treat this result as evidence either way without first
   confirming the specific slot's content has zero built-in rests.

**Mechanics check done (Claude, static, this session) — the redirect
itself looks correct on paper:** disassembled the *original stock*
instructions at all three hook sites. All three do `bl` to the exact same
address, a clean 5-instruction leaf function (no stack frame, no side
effects: reads one byte from `obj[voice+step*8) *2 + 1]` and returns it in
`r0`). Each site does something different with that return value
afterward — one isolates bit 7 into a separate register, one masks bit 7
away, one directly tests bit 7 and branches — all consistent with bit 7
being a real "populated/should-play" flag, which is exactly the bit our
patch clears on a Euclidean miss. Nothing about the call/return contract
looks violated by the redirect.

**Open question — resolved, 2026-09-22.** Root cause confirmed by direct
disassembly (not just the external cross-check): the real "does this
step attempt a note" gate is voice 0's **pitch byte**, checked inside
`play_time_step` at `0x08013ebc`-`0x08013ecc`
(`(pitch+0x7f)&0xff <= 1`, true exactly for `pitch==0x81`/`0x82`,
verified by hand) — an early function return. `seq_step_gate`, the
function our E0 patch redirects, is real but unrelated to this: its bit
7 feeds `seq_step_release`'s tie-scan fallback and a cached-pitch
retention flag inside `play_time_step`, never the note-start decision.
Full trace in `firmware-re/notes/findings-2026-09-20.md`'s "Root cause
... confirmed" entry and `firmware-re/notes/address-catalog.md`'s
`pitch_gate_check` entry.

**Update, 2026-09-22 (later same day): designed and emulated, not
flashed.** Added `pitch_gate_wrap` to `ks37_patch.S` (`FEAT_PITCH_GATE`,
not wired into any build level yet) — replaces the single
`seq_step_note` call at `0x08013ec2` instead of the three
`seq_step_gate` sites. Calls the original function, and only for a
pitch that isn't already a native tie/rest, substitutes `0x82` on a
Euclidean miss. Unicorn-tested directly (8 synthetic steps, every
combination of hit/miss × real-note/native-tie/native-rest): all 8
matched intended behavior exactly. Full detail and caveats in
`firmware-re/notes/findings-2026-09-20.md`'s "Revised patch designed and
Unicorn-emulated" entry — importantly, this is **not yet confirmed on
real hardware**, and doesn't account for the double-buffered
current/pending block mechanism or the release/look-ahead function.
**Not built into a `.led` image, not flashed.** Decide the strategy
question below before wiring this into `build_patch.py` and testing on
hardware.

**Update, 2026-09-22 (evening): built as `e0b`, flashed, hardware-tested
— mixed, but the reason is now understood.** Wired `pitch_gate_wrap` into
a new isolated build level `e0b` (`build_patch.py e0b`,
`USE_GATE_HOOK=0` so the old `seq_step_gate` sites stay untouched).
Built and verified clean (111 segments, vector table + old hook sites
byte-identical to stock), flashed by Cursor/PowerShell, confirmed clean
ack. Two clean, single-key, confirmed-Pattern-mode hear-tests (two
others were invalidated during the session — one was accidentally in
Walk mode, one had a Hold-latch double-key artifact):

- One sequence slot: a clean, stable, periodic pattern — not the
  intended `(3,3,2)`, but a different repeating period.
- A different slot, same patch: reverted to the original "every step
  fires" failure.

**Root cause of this slot-dependence, confirmed by direct disassembly
(not just inferred from the test results):** the `step` value our hook
feeds into `euclid_gate(step, 8, 3)` is not a counter our patch controls
— `play_time_step` receives it as an argument from its caller, and both
of its callers write that same value into a real object field (block
`+0x38`) that's range-checked against a length field (block `+0x10`)
belonging to whichever sequence block is currently active. So the
rhythm we get is a mechanical consequence of the *native* step-position
domain for whichever slot happens to be loaded, not an independent 0–7
Euclidean counter. Full trace in `firmware-re/notes/findings-2026-09-20.md`
("Root cause of the slot-dependence...") and
`firmware-re/notes/address-catalog.md` ("Step-counter object fields").

**The wrapper's own logic is not in question** — it's confirmed correct
in both emulation and by this hardware behavior being exactly what its
(flawed) input assumption predicts. **Concrete next step, not yet
built:** maintain our own free-running counter in patch RAM, incremented
once per real (non-tie/rest) `pitch_gate_wrap` call, and gate on *that*
instead of the native step value — makes the rhythm self-contained
regardless of which slot is active.

**Update, 2026-09-22 (later): fix built and re-emulated, not yet
flashed.** `pitch_gate_wrap` now gates on its own free-running counter
(`STEP_CTR_RAM`, `0x20005F02`) instead of the native step argument —
still passes the native step through unchanged to the wrapped
`seq_step_note` call (needed to fetch the right pitch), only the
Euclidean gate's own input changed. The counter advances only on a real
(non-tie/rest) call, so ties/rests stay phase-neutral. Unicorn-tested
against a mocked `seq_step_note` (27 synthetic cases: 16 consecutive
real-note calls confirming hits at counter-phase `0,3,6`; 11 more with
native tie/rest interleaved, confirming pass-through and that those
calls don't advance the counter) — all passed. Rebuilt
`e0b_pitchgate_3in8.led`, re-verified clean (same diff shape as before:
one hook redirect, the patch page, the checksum; vector table and old
`seq_step_gate` sites untouched), copied to
`/mnt/c/Users/jimcu/KeystepFlash/`. **Not yet flashed.** Next: same
flash/hear-test round-trip as before, same file name (the old build is
superseded in place).

**Update, 2026-09-22 (late): flashed and hardware-tested — mixed again,
but with a real explanation this time, plus one doc bug fixed.** Four
single-key hear-tests: two clean, reproducible `1,2,2`-gapped captures
right after flashing; one inconclusive (dominated by raw key-hold
before Hold engaged); one clean 20-second capture at 90% every-step
(the original failure shape), same flashed file as the good captures
minutes before.

Ruled out by direct disassembly (not more live retries): a permanent
`play_time_step` bypass (checked the resync branch — it's a one-time
self-re-arming step, not a bypass) and a multi-voice bypass (confirmed
our early-return-on-miss correctly blocks the downstream chord/voice
call on a miss).

**Real finding**: re-checking the external repo's mode table (prompted
by the user) turned up a genuine bug in our own tooling — `emulate_ks37.py`
and `address-catalog.md` had **Walk and Pattern swapped** at the
internal-mode-index level. Internal mode 6 (not 7) is the real
semi-random generator (confirmed by our own disassembly: it calls a
scale-quantizing pitch generator in a loop). This exact discrepancy was
flagged as unresolved days before tonight's testing started and should
have been closed out first — noted for next time. Fixed in both files
now.

This likely doesn't change what the physical device actually did
(the panel's Mode encoder, not a CC message, was what got turned), so
the leading explanation for tonight's density inconsistency remains the
manual's own description: Pattern regenerates its rest/tie content on
every key touch, and our gate's output compounds with whichever
regeneration happened to be live for that capture. Not independently
confirmed — see findings log entry "`e0b` (counter fix) hardware-tested;
mode-label swap found and fixed" for full detail and caveats.

## Strategy note (2026-09-22): native hook vs. an independent mode

The external repo above took a materially different approach to the same
problem: instead of hooking the native arp/sequencer's own step logic (our
approach), it built a **fully independent mode**, entered via a dedicated
gesture (hold Chord, then Record), that interacts with the native firmware
only through an explicit, carefully-bounded adapter contract (defined
entry/admission/prepare/publish/runtime/exit boundaries) — it never edits
the native arp's own step-generation code.

- **Our approach (hook the native engine)**: reuses all existing native
  timing/voice/LED plumbing for free, but last night's result plus the
  external repo's own "builder and consumer together" caveat suggest the
  native engine's internal state (retention, double-buffered
  current/pending sequence blocks, look-ahead release) is more
  interconnected than a single-hook patch can safely account for — real
  risk of "boots fine, silently wrong," which is close to what happened.
- **Their approach (independent mode)**: sidesteps that fragility
  entirely — the native arp/sequencer stays provably untouched — at the
  cost of more upfront engineering (own state machine, own note pool, own
  display feedback). Their own repo is explicit that even their working
  build is feasibility-only, tested on one device, not proven stable.
- **Not deciding yet.** Recording this as a live, credible alternative for
  the next patch-design session, specifically because it was arrived at
  independently by another team hitting similar native-engine fragility
  concerns — not defaulting silently back into more hook-patching. Their
  repo is MIT-licensed, so its structure (not necessarily its code
  verbatim) could legally be reused with attribution if that's the
  direction chosen later.

**Update, 2026-09-22 (verification pass): the density contradiction is a scorer bug, not a live one.** The counter-fix captures that were logged as `1,2,2` vs ~90% every-step are the same 3-in-8 grid (`3,3,2` at T≈155 ms). `listen_ks37.py` treated the 2T gap (~310 ms) as one step, then `round(3T/2T)` of 1.49 became 1, so a clean restripe printed as every-step. Re-scored: `151333` (the "90%" file) is 100% 3-in-8; `141445` is the only true every-step dump (pre-counter-fix slot-B). CC21 = internal mode + 1 (`0x08005a72`); panel Pattern (CC21=7) is TBH case 6. Writer `0x080130cc` still has no rest branch. `play_time_step` is one Arp tick call (`0x08012ec0`); the second caller is gated off a different object. Scorer fixed in `listen_ks37.py`. **Do not flash a new patch for this.** Next live listen: `e0 --clocks` if you want F8 as the grid; otherwise the existing e0b image already does 3-in-8.

Cursor (Windows) · Claude (WSL) · 2026-09-21 night · Claude (WSL) 2026-09-22

## Resume here — 2026-09-21 (evening)

**Hardware first:** E0 dump got `F0 77 F7` then stayed on `0291`
(LEDs looping). Not bricked. **MCC Upgrade from file** stock
`C:\Users\jimcu\KeystepFlash\keystep37_1.1.6.579_stock.led`. Unplug
when MCC finishes. Do not Rec+Stop+Play until app `0219` is back.

**Cause (packaging, not Thumb):** `implant_page` copied the page-0
footer `0b004000…` onto every spliced page. Headers still said
`0x08013C00` / `0x08014000`; footers said `0x08004000`. Bootloader
accepted Huaxin checksums then programmed those payloads over the
**vector table**. Noop-only Flash C booted because it never spliced
those pages. `led_codec.py verify` now checks footer addr; `implant_page`
keeps the existing footer (fill→data builds `0b01f400…`). E0–C2 and
noop rebuilt into KeystepFlash.

**After stock Identity 1.1.6:** PC_1 full send of the **new**
`e0_euclid_3in8.led` (no `--max-pages`). Then this repo
`listen_ks37.py e0` (IOI **3,3,2**).

**Dump is not this repo.** Do not retry WSL chunk send. Dump lab:
`C:\Users\jimcu\Documents\my apps\Keystep_Mod_PC_1`.

Two updater LED patterns (both work; not factory reset):

| Entry | LEDs | How |
|---|---|---|
| Hardware force-update | **Hold and Shift** alternate | Unplug, hold Rec+Stop+Play, plug USB |
| MCC software-update | Hold, Shift, Oct+, Oct− clockwise | MCC `productKey` / stuck `0291` |

Factory reset is Oct−+Oct+ until the display shows `rST`. Do not confuse
it with either updater. Do **not** send app-mode `productKey` from WSL.

**Do this next, in order:** *(historical 2026-09-21/22 feature ladder —
**superseded.** Current work is understand 1.1.6, no feature flash.)*

1. Open the Windows dump lab (PC_1). Rec+Stop+Play, device stays on
   Windows, first live send is KeystepFlash stock, then E0. Unplug after
   dump. Do not attach `0291` to WSL.
2. When the unit is back `0219`: `./scripts/keystep-see.sh` (Identity
   `00 06 01 01`).
3. Listen: `python3 firmware-re/scripts/listen_ks37.py e0 --seconds 25`
   — Arp, Mode=Pattern, Hold one key, Play solid. Pass = IOI steps
   **3,3,2** repeating (hits on 0,3,6). Fail = every-step (stock).
4. Then E1 → (E2 skip) → E3 off/on → C1 → C2
   (`e1`, `e3-off`, `e3-on`, `c1 --scale major`, `c2`).

Abort: stay in updater → MCC stock on Windows
(`C:\Users\jimcu\KeystepFlash\keystep37_1.1.6.579_stock.led`). Clockwise
LEDs are fine. Never `usbipd detach` a wedged updater — unplug.

**Already decided / do not redo:**

- Stock Chord extras **do not snap** to scale. Live dump
  `firmware-re/captures/listen/stock-chord-20260920-230828.txt`:
  bursts like B+D♯+F♯, D♯+F♯+A♯ against C major. C1 must snap after
  `noteval`. First listen run looked empty because `amidi -T realtime`
  prints `epoch) hex` — parser now accepts the `)`.
- Seq and Pattern share `play_time_step` / `seq_step_gate`. **E2 skip.**
- Thumb page `0x0801F400` (`firmware-re/patches/ks37_patch.S`).
  Rebuild: `python3 firmware-re/scripts/build_patch.py e0|e1|e3|c1|c2`.
  Unicorn `emulate_ks37.py euclid` PASS. Images already in KeystepFlash.
- **Do not use Shift+keys 1–16 for a patch.** Stock Keyboard MIDI CH.
  Latch needs a novel unused gesture (`stock-shift-map.md`).
- Do not write `0x0803B000`. Do not hook `set_arp_mode` / TBH case 7.
- WSL/winmm cannot *enter* the updater via app-mode `productKey`. Enter
  with Rec+Stop+Play (Hold/Shift alternate). Dump on Windows via PC_1
  (`flash_win.py`). Do not retry WSL chunk send. Recovery is MCC stock
  `firmware-re/recovery/keystep37_1.1.6.579_stock.led`.

Feature Thumb is written and packaged **as future work**. Flash A/C/D
succeeded. WSL chunk transfer on `0291` is **blocked**. Dump lab is
`flash-win.sh`; do not retry WSL ALSA. Do not run the E0→C2 ladder now.

Work on the **stripped flash extract**
(`firmware-re/firmware-images/keystep37_1.1.6.579_flash.bin`, base
`0x08000000`). The framed 117140-byte decode is a Huaxin segment stream,
not a flat Thumb image. App code begins at `0x08004000` (vector table +
Reset `0x0801d311`). Framed-file VAs in older notes are file offsets.

## Status

| Area | State |
|---|---|
| Current phase | **Understand 1.1.6.579.** No new patches, no live feature flash |
| USB/MIDI protocol, GET, bootloader `.led` transfer, front-panel CCs | Done (live-verified). Occupancy CCs = control IDs |
| `.led` encode/decode + checksums | Done. Huaxin segments; program u16 + per-footer u16. `led_codec.py retarget` |
| Flash without MCC | **Closed.** Rec+Stop+Play + `flash-win.sh`. MCC = recovery. ALSA dump refused |
| MCU / unused space | STM32F1 + GPIOE + TIM8 + USB; ≥256KB (F103VC). 66 KiB FF-fill at `0x0801F400` (**future** Thumb) |
| Pattern-mode generator | **Named (island).** Mode byte `engine+0x10 == 6` (CC21=7). TBH `0x08011a38` case 6. Play-time `0x08013e8c`. Pitch-gate `0x08013ebc` is emission; `seq_step_gate` bit 7 is retention |
| Machine model (boot, objects, loop, IRQs, three buses, time, voice) | **Not done.** Catalog + `recreate.py` are islands |
| Mode activation | **`set_arp_mode` `0x08011794`**. Knob path `0x08016a26` reads settings `+0x55` |
| Chord interval | Unicorn: interval = `*(int8*)(voice+0x4f)` on `0x200051cc`; transpose = `0x200000C8` |
| Panel occupancy | **Done enough.** `stock-shift-map.md`. Shift+keys 1–16 = MIDI CH. Shift+Mod = later latch candidate |
| Euclidean / chord images | **Future.** Packaged; e0b live 3-in-8; e3b latch wrong. Do not extend |
| Stock recovery image | `firmware-re/recovery/keystep37_1.1.6.579_stock.led` |
| WSL sender | **Live via `flash-win.sh`.** ALSA `ks37_flash.py` blocked |

## Protocol (do not redo)

- Normal USB `1c75:0219`, bootloader `1c75:0291`
- GET: `F0 00 20 6B 7F 42 01 00 41 <globalParamId> F7`
- Update: `F0 5A 57 6E 28 3C 4E 51 F7` (`productKey`) twice, then `F0` + hex-ASCII `.led` slices + `F7`
- Pattern = Mode knob CC 21 value **7** = internal `engine+0x10` **6** (CC21 = internal + 1). Chord knobs CC 98/99/100/101
- Arp ignores injected MIDI notes; physical keys only
- Mode knob is 8-detent. A future feature cannot be a 9th printed position

## Feature page (Euclidean then scale-chord) — **FUTURE**

Do not rebuild or flash these in the understand-1.1.6 phase. Facts below
are frozen from the 2026-09 experiment so a later session does not
re-derive them.

One implanted page at `0x0801F400` (`firmware-re/patches/ks37_patch.S`).
Rebuild (later): `python3 firmware-re/scripts/build_patch.py e0|e1|e3|c1|c2`.

**Keep pitches; rewrite gates only** was the experiment. Real emission
gate is pitch-gate at `0x08013ebc`, not `seq_step_gate` bit 7. E1/E3
images that hook `seq_step_gate` are dead. E3b latch on Shift+C2/C♯2 is
stock MIDI CH — wrong gesture.

| Level | Image | Behaviour |
|---|---|---|
| E0 | `e0_euclid_3in8.led` | Always-on **3-in-8**. Three `bl seq_step_gate` sites (`0x08013f62`, `0x08013fde`, `0x080141d2`) → `euclid_wrap` |
| E1 | `e1_euclid_hits.led` | **Dead hook** (`seq_step_gate`). Do not flash. |
| E1b | `e1b_pitchgate_hits.led` | Same pitch-gate as e0b. `hits` = real voice-0 pitches (skip `0x81`/`0x82`/`0xFF`); `length` = slot `+0x400`. **Built, not flashed.** |
| E2 | — | **Skip.** Same player as Pattern |
| E3 | `e3_euclid_shift.led` | **Dead hook.** Do not flash. |
| E3b | `e3b_pitchgate_shift.led` | Pitch-gate latch. **Wrong gesture** (Shift+C2/C♯2 = MIDI CH). Euclidean-on works; off unproven. Do not treat as done. |
| C1 | `c1_scale_chord.led` | Chord ON (`voice+0x4d`) + scale mask ≠ `0x0FFF` → snap after `noteval`. Chromatic = stock. Hooks at `0x0801baac`, `0x0801b9f2`, `0x0801bb24` |
| C2 | `c2_shift_type.led` | Shift+Type is **not** a free hole (Test-20 CC 86+98; Type still enters Chord). Piggyback flavour only. **Do not use for a latch** |

Stock listen (**live**, 2026-09-20): extras do **not** snap. Static
agrees (`0x0801ba9c` emits `r4` directly). C1 snaps after `noteval`.
Unicorn: `emulate_ks37.py euclid` — 3-in-8, wrap, E3 latch-off
passthrough, C major C♯→D.

Do **not** hook `set_arp_mode` / TBH case 7. Do **not** write `0x0803B000`.

### `.led` rebuild

```
python3 firmware-re/scripts/led_codec.py extract-flash <in.led> flash.bin
# patch Thumb in flash.bin (file offset = VA - 0x08000000)
# or convert one FF-fill hole to a real 1 KiB record:
python3 firmware-re/scripts/led_codec.py implant-page <in.led> 0x0801F400 out.led
# cut 1 KiB pages back into Huaxin records (offset 64 + 4n), then:
python3 firmware-re/scripts/led_codec.py retarget framed.bin framed_out.bin
python3 firmware-re/scripts/led_codec.py encode framed_out.bin out.led
```

## Flash ladder (derisk)

| Step | Image | Sender | Status |
|---|---|---|---|
| Gate 0 | — | `keystep-see.sh` | PASS after night stock restore (`1c75:0219`, Identity 1.1.6) |
| A | vendor stock | MCC on Windows | **Done.** |
| B | same stock | Rec+Stop+Play + `flash-win.sh` | **Done** (2026-09-22). ALSA WSL send blocked; do not reopen |
| C | `noop_1f400.led` (`0x0801F400[0]=FE`) | MCC | **Done.** `0219` → `0291` → `0219`. Packaging accepted. |
| D | vendor stock | MCC | **Done.** Restored 1.1.6. Capture: `firmware-re/captures/mcc_cd_2026-09-20.pcap` |
| E0 | `e0_euclid_3in8.led` | Rec+Stop+Play + PC_1 winmm | **Wire OK (`F0 77 F7`), did not boot.** Stolen page-0 footers on hook pages. Encoder fixed; images rebuilt. Redo after MCC stock. |
| E1 | `e1_euclid_hits.led` | MCC | **Packaged.** Same hook; hits from slot |
| E2 | — | — | **Skip.** Seq already uses `play_time_step` |
| E3 | `e3_euclid_shift.led` | MCC | **Packaged.** Default off; Shift+1/2 |
| C1 | `c1_scale_chord.led` | MCC | **Packaged.** Scale snap after `noteval` |
| C2 | `c2_shift_type.led` | MCC | **Packaged.** Shift+Type flavour |

Floor (app-mode unlock): the SysEx prelude is **not** the missing piece.
Live C+D capture: C is Identity×2 + 101 GETs + UI gap + one `productKey`.
D is Identity then `productKey` 3 ms later — **no GET**. WSL
`ks37_flash.py` got 101/101 GET replies then `productKey` and stayed
`0219`. Windows `winmm` `midiOutLongMsg` rc=0 (Identity + `productKey`)
also stayed `0219`. Do not keep sending app-mode `productKey` as a probe.
Enter with Rec+Stop+Play instead. Recovery = MCC +
`firmware-re/recovery/keystep37_1.1.6.579_stock.led`. Prelude ids:
`firmware-re/scripts/mcc_unlock_prelude.py`.

usbipd must bind **both** `1c75:0219` and `1c75:0291`. See [environment-setup.md](environment-setup.md). Abort = MCC + recovery `.led`.

`retarget` rewrites **both** u16s: program checksum (last payload `[-2:]`,
on-wire `95c4` on 1.1.6.579) and every footer checksum (last footer
`[-2:]`, on-wire `65fe`). Formula is Huaxin additive
`0x10000 - (sum & 0xFFFF)`, FF-fill pages count as `1024 × 0xFF` in the
program sum. `mutate-test` proves this on both stock images.

## Methodology that still holds

- Re-derive function starts from control-flow when Ghidra looks corrupted
- Live hardware beats static guesses
- SWD / opening the case stays out of scope
- Static `bl` searches miss vtable callees — this session the `+0x214`
  writer *does* have one `bl` (ctor). Mode is a byte, not a vtable swap

## Docs corrected this pass

- [led-header.md](../firmware-re/notes/led-header.md) — Huaxin segments, both u16s
- [flash-map.md](../firmware-re/notes/flash-map.md) — `0x08004000` app + vector table
- [address-catalog.md](../firmware-re/notes/address-catalog.md) — flash VAs; play-time `0x08013e8c`
- `led_codec.py`, `emulate_ks37.py play`, `scan_firmware.py`, `ghidra/recreate.py`

## Artifacts on disk

- `og_firmware/keystep37_Firmware_Update_1_1_6_579 (1).led`
- `og_firmware/keystep37_Firmware_Update_1_0_4_179.led`
- `firmware-re/recovery/keystep37_1.1.6.579_stock.led` (read-only recovery)
- `firmware-re/firmware-images/keystep37_1.1.6.579_flash.bin` (196608 bytes)
- `firmware-re/firmware-images/rebuild/noop_1f400.led` (unused-page poke)
- `firmware-re/firmware-images/rebuild/e0_euclid_3in8.led` … `c2_shift_type.led`
- `firmware-re/patches/ks37_patch.S` + `ks37_patch.ld`
- `firmware-re/scripts/build_patch.py`
- `firmware-re/scripts/listen_ks37.py` + `scripts/listen-ks37.sh`
- `firmware-re/captures/listen/stock-chord-20260920-230828.txt`
- `firmware-re/scripts/ks37_flash.py` (`--already-bootloader`) — **blocked** (ALSA stall)
- `scripts/cycle.sh` — unicorn `emulate all` then `flash-win.sh --dry-run`. Feature level / `--live` refused unless `KS37_FEATURE_FLASH=YES-FEATURE-FLASH`
- `scripts/occupancy-listen.sh` — prompted `amidi -d` pass → `firmware-re/captures/occupancy/`
- `scripts/flash-win.sh` — WSL → `py.exe` `flash_win.py` (default dry-run; parser is `led_codec.py`)
- `scripts/flash_bl_wsl.sh` / `scripts/attach_bootloader.sh` — **blocked**; dump is `flash-win.sh`
- `scripts/flash_euclid_mcc.sh` (MCC recovery on Windows)
- `firmware-re/captures/keystep37_firmware_update.pcap` (and pcba / testpanel)
