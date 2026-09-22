# Stock panel / Shift map — KeyStep 37 1.1

Validated 2026-09-22 against:

- Arturia *KeyStep 37 User Manual 1.1* EN (17 Dec 2020), local
  `arturia_manual/keystep-37_Manual_1_1_EN.pdf` and
  [dl.arturia.net 1.1 EN](https://dl.arturia.net/products/keystep-37/manual/keystep-37_Manual_1_1_EN.pdf)
  — especially §1.6, §2.1.6–2.1.7, §3.1, §3.2, §3.6 / chart §3.6.6, §4.2–4.3, §5.4–5.5.
- **Not** the KeyStep 37 **mk2** manual (encoder, Spice, Shift+pitch-strip Gate).
- Original KeyStep firmware 1.1.0.18 / 1.1.0.28 notes and
  [Arturia KeyStep Shift FAQ](https://support.arturia.com/hc/en-us/articles/4405748002706-KeyStep-Shift-functions)
  (25 Jan 2022) for shortcuts KS37 1.1 **inherited but omitted from §3.6.6**.
  Edouard (Arturia): Shift + both Octave buttons **clears all steps, keeps length**.

Keyboard is C2–C5 = MIDI 36–72 = keys **1–37** left to right.

§3.6.6 copies original KeyStep **32-key** numbering (Swing “22–32”,
“Key 40/41/46”). **Silk on this box wins:** Swing is 9 values on keys
22–30 (§3.6.3: Off, 52, 54, 57, 60, 63, 67, 71, 75); Mono = 31;
Overdub = 32; User scale = 37.

This project mapped **raw Test-20 CCs** for most physical controls and
tied them to firmware control IDs (`stock-shift-map.md` §10). Occupancy
is **done enough**. Euclidean / chord latch work is **future** — do not
steal Shift+keys 1–16 (Keyboard MIDI CH). E3b stole that combo.

**Live MIDI** column is filled from MCC Test-20 pastes (2026-09-22) plus
eyes-on stock (Test-20 off) for chart holes. Values: `note-on` / `CC` /
`channel-change` / `no MIDI` / `stock LED`. Anything that changes MIDI
CH, starts Rec, **clears sequence notes**, or suppresses Note-On is
**occupied**. Test-20 CC numbers **are** firmware control IDs (see §10).
A **future** latch only from empty/surviving cells; then `0x08004930` /
`0x08004388` / Shift RAM `0x200010d2`. EVENT `+0x25` is note-release on
a different object, not this CC map. Current work is understanding 1.1.6,
not writing that latch.

Live script: [`scripts/occupancy-listen.sh`](../../scripts/occupancy-listen.sh)
→ `firmware-re/captures/occupancy/`. Prompt order is §7.

## 1. Shift + keys (all 37 keys are taken)

Silkscreen bands use every key. 16 + 5 + 9 + 2 + 5 = 37.

| Keys | MIDI | Silk | Shift function | Source | Live MIDI |
|---|---|---|---|---|---|
| 1–16 | 36–51 (C2–D♯3) | Keyboard MIDI CH 1–16 | User MIDI channel **and** reset Kbd Play channel | KS37 §3.6.1 / §3.6.6 | **CC 86 + note-on ch3** (MCC Test-20 2026-09-22). Occupied |
| 17–21 | 52–56 (E3–G♯3) | Gate | Gate 10 / 25 / 50 / 75 / 90 % | KS37 §3.6.2 | **CC 86 + note-on** (same pass). Occupied |
| 22–30 | 57–65 (A3–F4) | Swing | Off, 52, 54, 57, 60, 63, 67, 71, 75 | KS37 §3.6.3 (nine values). Chart “22–32” is 32-key leftover | **CC 86 + note-on**. Occupied |
| 31 | 66 (F♯4) | Sequence Mono | Poly ↔ Mono toggle | KS37 §3.6.4.1. Chart “Key 40” is junk | **CC 86 + note-on 66**. Occupied |
| 32 | 67 (G4) | Sequence Overdub | Overdub on/off | KS37 §3.6.4.2. Chart “Key 41” | **CC 86 + note-on 67**. Occupied |
| 33–36 | 68–71 (G♯4–B4) | Scale Chrom / Major / Minor / Blues | Scale select. Minor = Shift+C4 (third C) | KS37 §3.6.5 / §2.4 | **CC 86 + note-on**. Occupied |
| 37 | 72 (C5) | Scale User | User scale; hold + lower octave toggles pitch classes | KS37 §3.6.5.3. Chart “Key 46” | **CC 86 + note-on 72**. Occupied |

Shift + Oct+ **and** keys 1–16: separate **Kbd Play** MIDI channel
(§3.2.2). Same keys, extra modifier. See §4.

There is **no free Shift+key**. A latch cannot live on C2/C♯2/D2.

## 2. Shift + panel (every printed combo is taken)

| Gesture | Stock function | Source | Raw CC | Live MIDI |
|---|---|---|---|---|
| Shift + Hold | Chord mode on/off | KS37 §3.1.1 | Shift 86, Hold 85 | **CC 86 + CC 85** (MCC Test-20) |
| Shift + Rec | Record-append (seq must be **playing** or append **erases**) | KS37 §4.3.1 / §3.6.6 | Rec 87 | **CC 86 + CC 87** |
| Shift + Stop | Clear last step (Seq only; playing or stopped) | KS37 §4.3.2 | Stop 89 | **CC 86 + CC 89** |
| Shift + Play | Restart Seq/Arp from step 1 | KS37 §3.5 | Play 90 | **CC 86 + CC 90** |
| Shift + Oct− | Seq: Transpose mode. Arp: octave down (repeat = more octaves) | KS37 §3.2.1 / §5.5 | Oct− 16 | **CC 86 + CC 16** |
| Shift + Oct+ | Seq: Kbd Play. Arp: octave up | KS37 §3.2.2 / §5.5 | Oct+ 17 | **CC 86 + CC 17** |
| Shift + Mode knob | Skip Seq/Arp positions; apply on release | KS37 §3.3 | Mode 21 | **CC 86 + CC 21** (values 2–6 in this pass). Occupied |
| Shift + Time Div | Skip Time Div; apply on release | KS37 §3.4 | TimeDiv 104 | **CC 86 + CC 104** (values 2–6). Occupied |
| Shift + Rate | BPM fine (internal sync only) | KS37 §2.2.4 / §3.6.6 | Rate 102 | **CC 86 + CC 102** (0–0x6C sweep). Occupied |
| Shift + Chord | Control/CC mode; repeat = banks 1–4 | KS37 §1.4.3 / §3.6.6 | Chord / CC 105 | **CC 86 + CC 105** |
| Shift + Tap | **Tap tempo** (display shows the tempo you tap). Not a hole | Eyes-on 2026-09-22 (Test-20 off). Manual only lists Tap as Rest/Tie in rec | Tap 103 | **Occupied.** Shift does not block Tap. Display = tapped tempo |
| Shift + Type / Notes / Vel>Notes / Strum | Not in §3.6.6. Type-without-Shift still enters Chord mode | KS37 §3.1.1 | 98 / 99 / 100 / 101 | **CC 86 + 98 / 99 / 100 / 101** (MCC Test-20). Occupied on the wire; not a proven Shift+knob stock function |

**Shift + Tap** is occupied as **tap tempo** (2026-09-22, Test-20 off). The
chart omits it; the box still does it. A latch cannot live there without
stealing tempo.

## 3. Unshifted panel (mapped at CC, not always as firmware)

| Control | Stock | Source | CC | Live MIDI |
|---|---|---|---|---|
| Seq/Arp switch | Seq vs Arp | §2.2.1 | 18 | **CC 18** = 0 (MCC Test-20 combo pass) |
| Mode knob | 8 detents, Pattern = 7 = internal 6 | §2.2.2 | 21 | **CC 21** (this paste: 2–6 unshifted, then Shift+same) |
| Time Div | time division | §2.2.5 | 104 | **CC 104** (2–6) |
| Rate | tempo | §2.2.4 | 102 | **CC 102** (0–0x6C; MCC dumps every tick twice) |
| Hold | hold arp/seq; add notes while ≥1 key down | §2.1.4 / §5.4 | 85 | **CC 85** |
| Shift | modifier | §1.6.6 | 86 | **CC 86** |
| Rec | step/realtime rec. First Rec in step mode **erases** the sequence | §4.2.1 | 87 | **CC 87** |
| Stop | stop | §2.2.3 | 89 | **CC 89** |
| Play | play/pause | §2.2.3 | 90 | **CC 90** |
| Tap | tap tempo; Rest/Tie in rec | §1.6.2 / §4.2.1 | 103 | **CC 103** |
| Oct− / Oct+ | octave (±4). Next note only | §2.1.6 | 16 / 17 | **CC 16 / 17** |
| Chord button | toggle Chord knobs vs CC knobs (does **not** turn Chord mode off) | §3.1.1 | 105 | **CC 105** |
| Type / Notes / Vel>Notes / Strum | chord params; **turning Type also enters Chord mode** | §3.1.1 | 98 / 99 / 100 / 101 | **CC 98 / 99 / 100 / 101** (MCC names them NRPN/RPN; they are the four knobs) |
| Pitch / Mod strips | bend / mod | §2.1.3 | 65 / 64 | **CC 65** pitch (0–0x6E), **CC 64** mod (0–0x7F). MCC names them Portamento / Sustain |
| Sync DIP | clock source | §1.7.7 | 19 | TBD |
| DC in | power sense | JSON | 96 | TBD |

## 4. Combos — three (or more) held together

Do not steal any of these for a latch.

| Gesture | Stock | Source | Live MIDI |
|---|---|---|---|
| Rec + Stop + Play on plug | updater `1c75:0291` (Hold/Shift alternate) | hardware force-update (not in §3.6.6) | **skip live pass** (updater) |
| Shift + Oct+ + keys 1–16 | Kbd Play MIDI CH | KS37 §3.2.2 | **CC 86 + 17 + note-on ch3** (keys 1–6, 8, 10 in this pass; Hold 85 often also down). Occupied |
| **Shift + Oct− + Oct+ (Seq, stopped or running)** | **Clear all notes, keep sequence length** | Original KeyStep 1.1.0.28 / Arturia Shift FAQ. **Missing from KS37 §3.6.6.** **Confirmed on this box 2026-09-22** | **Clears the sequence** (eyes-on, Test-20 off). Occupied |
| Shift + Oct− + Oct+ (Arp) | limit multi-octave arp to held notes | KS37 §5.5 | **CC 86 + 16 + 17** (after CC 18 flip). Buttons occupied. No held-key notes in that cluster |
| Power-off, hold Oct− + Oct+, power-on | factory `rST` | KS37 §2.1.7 | **skip live pass** (destructive) |
| Hold / Shift / Oct+ / Oct− clockwise chase | MCC software-update | MCC `productKey` | **skip live pass** (updater) |

Same three buttons, three stock jobs: factory reset (power cycle), Seq
clear-notes, Arp collapse-range. Occupied.

## 5. Two held, third is a tap

| Gesture | Stock | Source | Live MIDI |
|---|---|---|---|
| Rec held + Play (seq **stopped**) | realtime rec over a looping seq | KS37 §4.2.2 | **CC 87 + CC 90** (end of combo paste). Occupied |
| Rec (already on) while seq looping | same realtime rec | KS37 §4.2.2 | TBD (same CCs as Rec+Play) |
| Rec held + keys 1–16 (repeat to add) | sequence / Pattern length 1–64 | KS37 §4.2.3 / §5.3 Pattern | **CC 87 + note-on ch3 36–51** (keys 1–16), then Rec-per-key on 37–41, 42, 41, 45. Occupied |
| Rec on, Tap | rest (repeat for longer rest) | KS37 §4.2.1.1 | **CC 87 + CC 103** (Hold 85 also in this cluster; no notes). Occupied |
| Rec on, hold keys, Tap | tie into next step | KS37 §4.2.1.2 | **note-on, CC 103, note-off** (key 45 / 48 / 50 / 45 / 43 / 41 / 45). Occupied |
| Rec on, **hold Tap**, play keys | legato; **erases existing sequence** | KS37 §4.2.1.3 | **CC 103 then note-on** (47, then Rec+Tap+48, then Tap-before-notes). Occupied |
| Oct− + Oct+ together (no Shift) | reset keyboard octave **and** arp insert point | KS37 §2.1.6 / §5.4 | **CC 17 + CC 16**, no 86. Occupied |
| Shift + Hold, then keys | original KeyStep: edit chord memory (Hold blinks). KS37 User Chord is Chord+keys | orig. FAQ vs KS37 §3.1.1 | **CC 86 + 85 + note-on** (often also Oct+ 17). Occupied on the wire |
| Shift + Hold / Rec / Stop / Play / Oct± | already in §2 | KS37 §3.6.6 | **CC 86 + 85/87/89/90/16/17** (same as §2) |

Unofficial (forum, original KeyStep; one KS37 user): Rec + Tap + Stop
while stopped → 1-step rest. Unreliable. Live pass may skip; still not
a latch.

## 6. Not a chord of buttons, still occupancy

| Gesture | Stock | Source | Live MIDI |
|---|---|---|---|
| Stop ×3 | All Notes Off | KS37 §1.6.3.1 | **CC 89 ×3**. Occupied |
| Chord held + keys | User Chord from those pitches | KS37 §3.1.1 | **CC 105 + note-on ch3**. Occupied |
| Type knob | enters Chord mode | KS37 §3.1.1 | **CC 98** (this pass after Shift; same CC unshifted) |

MCC-only (no panel Shift): MIDI In CH, MIDI Thru, User Channel, curves,
sync clock format, tempo jump/pickup, tap average, Next Seq, Transpose
latch / port / channel, velocity as-recorded vs fixed, CC bank values,
Tie Mode.

## 7. Live occupancy pass (prompt order)

You at the panel. Stock or e3b. Device attached to WSL. **Test-20**
so every physical control dumps its CC (MCC MIDI check
`F0 00 20 6B 7F 42 02 00 70 00 7F F7`). Re-armed before each step.

```
./scripts/occupancy-listen.sh --test20
```

Stock MIDI only (note-on / channel-change / silence), no Test-20:

```
./scripts/occupancy-listen.sh
```

Skip factory `rST` and Rec+Stop+Play. Skip the MCC clockwise chase.
Prompt 50 **clears the current sequence** (keeps length) if stock
inherited the 1.1.0.28 shortcut — use a throwaway seq. After the log,
fill Live MIDI in §§1–6 and §8. Occupied = MIDI CH change, Rec start,
sequence-note clear, or Note-On suppressed.

1. Shift + key 1 (C2 / MIDI 36) — Keyboard MIDI CH 1
2. Shift + key 2 (C♯2 / 37) — Keyboard MIDI CH 2
3. Shift + key 3 (D2 / 38) — Keyboard MIDI CH 3
4. Shift + key 4 (D♯2 / 39) — Keyboard MIDI CH 4
5. Shift + key 5 (E2 / 40) — Keyboard MIDI CH 5
6. Shift + key 6 (F2 / 41) — Keyboard MIDI CH 6
7. Shift + key 7 (F♯2 / 42) — Keyboard MIDI CH 7
8. Shift + key 8 (G2 / 43) — Keyboard MIDI CH 8
9. Shift + key 9 (G♯2 / 44) — Keyboard MIDI CH 9
10. Shift + key 10 (A2 / 45) — Keyboard MIDI CH 10
11. Shift + key 11 (A♯2 / 46) — Keyboard MIDI CH 11
12. Shift + key 12 (B2 / 47) — Keyboard MIDI CH 12
13. Shift + key 13 (C3 / 48) — Keyboard MIDI CH 13
14. Shift + key 14 (C♯3 / 49) — Keyboard MIDI CH 14
15. Shift + key 15 (D3 / 50) — Keyboard MIDI CH 15
16. Shift + key 16 (D♯3 / 51) — Keyboard MIDI CH 16
17. Shift + key 17 (E3 / 52) — Gate 10 %
18. Shift + key 18 (F3 / 53) — Gate 25 %
19. Shift + key 19 (F♯3 / 54) — Gate 50 %
20. Shift + key 20 (G3 / 55) — Gate 75 %
21. Shift + key 21 (G♯3 / 56) — Gate 90 %
22. Shift + key 22 (A3 / 57) — Swing Off
23. Shift + key 23 (A♯3 / 58) — Swing 52
24. Shift + key 24 (B3 / 59) — Swing 54
25. Shift + key 25 (C4 / 60) — Swing 57
26. Shift + key 26 (C♯4 / 61) — Swing 60
27. Shift + key 27 (D4 / 62) — Swing 63
28. Shift + key 28 (D♯4 / 63) — Swing 67
29. Shift + key 29 (E4 / 64) — Swing 71
30. Shift + key 30 (F4 / 65) — Swing 75
31. Shift + key 31 (F♯4 / 66) — Sequence Mono
32. Shift + key 32 (G4 / 67) — Sequence Overdub
33. Shift + key 33 (G♯4 / 68) — Scale Chromatic
34. Shift + key 34 (A4 / 69) — Scale Major
35. Shift + key 35 (A♯4 / 70) — Scale Minor
36. Shift + key 36 (B4 / 71) — Scale Blues
37. Shift + key 37 (C5 / 72) — Scale User
38. Shift + Hold
39. Shift + Rec
40. Shift + Stop
41. Shift + Play
42. Shift + Oct−
43. Shift + Oct+
44. Shift + Mode knob (turn a detent, release)
45. Shift + Time Div (turn, release)
46. Shift + Rate (turn, release)
47. Shift + Chord
48. Shift + Tap *(chart hole)*
49. Shift + Oct+ held, tap keys 1–16 — Kbd Play MIDI CH
50. **Seq, stopped:** Shift + Oct− + Oct+ — clear all notes, keep length (throwaway seq)
51. **Arp, playing, keys held:** Shift + Oct− + Oct+ — limit multi-octave arp to held notes
52. Rec held + Play, seq stopped — realtime rec over looping seq
53. Rec held + keys 1–16 (tap a few, repeat to add) — seq / Pattern length
54. Rec on: Tap — rest
55. Rec on: hold keys, Tap — tie
56. Rec on: hold Tap, play keys — legato (**erases seq**)
57. Oct− + Oct+ together — reset keyboard octave / arp insert point
58. Stop ×3 — All Notes Off
59. Chord held + keys — User Chord
60. Type knob (no Shift) — enters Chord mode
61. Chord held, then Rec *(chart hole)*
62. Shift + Hold, then keys — orig. KeyStep chord-memory (KS37 may no-op)

Skipped (do not perform): Rec+Stop+Play on plug; factory `rST`; MCC
Hold/Shift/Oct+/Oct− clockwise chase.

## 8. Chart holes (candidate novel gestures)

These are the only panel-adjacent holes. **None are firmware-proven
no-ops yet.** Do not steal a silkscreened Shift+key. Latch later only
from **empty** Live MIDI cells after §7.

| Candidate | Why it looks free | Risk | Live MIDI |
|---|---|---|---|
| **Chord held, then Rec** (no Shift) | KS37 1.1 never assigns it. Other-repo GEN already uses this pair | Rec LED **does** come on (2026-09-22). No extra Chord+Rec function seen, but stock Record still fires and can erase | **Occupied.** Rec light on. Not a no-op |
| **Shift + Tap** | Looked free on the chart | **Tap tempo** — display shows tapped BPM | **Occupied.** Not a hole |
| Shift + Mod strip | Not listed (mk2 uses Shift+pitch for Gate — **we are not mk2**) | Eyes-on 2026-09-22: **seems to do nothing** (no extra panel function). Test-20 still **CC 86 + CC 64**. Firmware: `0x08004388` bails when Shift RAM `0x200010d2` ≠ 0 (`bne 0x08004428`) — no extra handler. Stock may still send Mod CC with Test-20 off | **Candidate.** Confirm stock Mod MIDI on the wire with Test-20 off |
| Shift + Pitch strip | Not listed on KS37 1.1 (mk2 Shift+pitch = Gate) | Unknown | **CC 86 + CC 65**. Occupied on the wire |
| C2’s Shift + Type | Not in the Shift chart; Type still does chord Type | Piggyback, not a steal. Type-without-Shift already enters Chord mode. Test-20 still sees **CC 86 + CC 98**. **Do not use this for E3 latch** | **CC 86 + CC 98** (MCC Test-20). Occupied on the wire |

**Ruled out:** Shift+C2 / C♯2 / D2 / keys 1–16 (MIDI CH). Any other
Shift+key in the five silkscreen bands. Rec+Stop+Play, factory `rST`,
MCC clockwise chase, Rec+Play, Rec+keys 1–16, Rec+Tap (rest/tie/legato),
Oct−+Oct+, Stop×3, Chord+keys, Type knob, Shift+Oct++keys 1–16,
**Shift+Oct−+Oct+ (Seq clear-notes — confirmed on this box — and Arp
limit-range)**. **Shift+Tap (tap tempo)**. **Chord then Rec (Rec LED on)**.

## 9. Why e3b “off” could not work

`shift_note_hook` watches Shift + MIDI 36/37 on the **note** path
(`0x0801b75a`). Stock treats those keys as **Keyboard MIDI CH**. Two
failures, both expected from the manual:

1. The combo is already owned. Hear-tests that “did nothing” were
   changing User Channel (and resetting Kbd Play CH).
2. Shift+channel keys may never appear as Note-On on that hook, so
   `FLAG_RAM` stays at whatever unused SRAM had at boot (often 1 →
   Euclidean already on). `emulate_ks37.py euclid` now plants leftover
   `0xFF` at `0x20005F00` to catch this (e3b currently FAILs until
   BSS-init).

Do not rebuild e3b on MIDI 36/37. Pick a gesture from **empty** cells
in §8 after the occupancy pass, then map that pair in the button router
before writing Thumb.

## 10. Firmware: occupancy CCs are control IDs

MCC Test-20 `B0 nn vv` uses the same `nn` as `KeyStep37.json` `controls[].items[].id` and as immediates in `id_to_index` (`0x08006024`). That is why every physical control we touched showed a stable CC, including Shift+combos (CC 86 plus the second control).

| CC | ID | Control | Firmware |
|---|---|---|---|
| 85 | `0x55` | Hold | compact 0 |
| 86 | `0x56` | Shift | compact 1; held flag `*(uint8*)0x200010d2` |
| 16 | `0x10` | Oct− | compact 2 |
| 17 | `0x11` | Oct+ | compact 3 |
| 103 | `0x67` | Tap | compact 4 |
| 87 | `0x57` | Rec | compact 5 |
| 89 | `0x59` | Stop | compact 6 |
| 90 | `0x5a` | Play | compact 7 |
| 105 | `0x69` | Chord | `chord_test_dispatch` `0x08005df8`; shifted TBH case 8 |
| 18 | `0x12` | Seq/Arp switch | not in the 8-button table (encoder group) |
| 21 | `0x15` | Mode | `mode_knob_apply`; Shift+Mode skip-apply then `test20_cc_value2` |
| 104 | `0x68` | Time Div | same skip-apply pattern |
| 102 | `0x66` | Rate | knob reverse default |
| 98–101 | `0x62`–`0x65` | Type / Notes / Vel>Notes / Strum | `knob_index_to_cc`; analog `+0x58` = 1..4 |
| 64 | `0x40` | Mod strip | Test-20 via analog emit; stock path `0x08004388` |
| 65 | `0x41` | Pitch strip | Test-20 via analog emit; kind `+0x58==0` on `0x08004918` (H: Pitch vs Mod assignment) |

**Paths**

1. **Buttons (Test-20):** debounce `0x0801a7ac` → `index_to_id` → `test20_cc_press` (`B0 id 01`).
2. **Knobs/strips (Test-20):** `analog_knob_process` `0x08004918`; if AutoTest `+0xb9`, `knob_index_to_cc` then `test20_cc_value`. That flag is why MCC AutoTest 20 must be exited before a stock-MIDI hole check.
3. **Shift secondaries (stock):** not the CC numbers. `panel_button_dispatch` `0x08017260` reads Shift RAM, then a **shifted** TBH (`0x08017868`) for Hold/Rec/Stop/Play/Chord. Shift+Oct / Shift+Tap live on other objects (18 Shift-RAM load sites). Shift+keys are the **note** path (`0x0801b750` / e3b hook), not this button TBH.
4. **Shift+Mod candidate:** `0x08004388` loads Shift RAM at `0x080043be`; non-zero skips the MIDI emit and returns. No extra panel function in that function. The other strip’s Shift branch (`0x08004bf8`) is pickup math on `+0x58==0`. Confirm which object is Mod vs Pitch with Test-20 **off** (stock Mod is typically CC 1, not CC 64).
