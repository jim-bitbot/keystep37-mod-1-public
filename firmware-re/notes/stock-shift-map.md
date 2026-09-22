# Stock panel / Shift map — KeyStep 37 1.1

Source: Arturia *KeyStep 37 User Manual 1.1* EN, especially §3.6 and
the Shift chart §3.6.6. **Not** the KeyStep 37 **mk2** manual (encoder,
Spice, Shift+pitch-strip Gate — different product).

Keyboard is C2–C5 = MIDI 36–72 = keys **1–37** left to right.

This project mapped **raw Test-20 CCs** for most physical controls.
It did **not** map the **Shift secondary** firmware handlers. E3b stole
Shift+key 1/2, which the manual already assigns to Keyboard MIDI CH.

## 1. Shift + keys (all 37 keys are taken)

Silkscreen bands use every key. 16 + 5 + 9 + 2 + 5 = 37.

| Keys | MIDI | Silk | Shift function | Firmware handler | Notes |
|---|---|---|---|---|---|
| 1–16 | 36–51 (C2–D♯3) | Keyboard MIDI CH 1–16 | User MIDI channel **and** reset Kbd Play channel | **never mapped** | **E3b collision.** Key 1 = C2 = 36 = ch 1. Key 2 = C♯2 = 37 = ch 2. |
| 17–21 | 52–56 (E3–G♯3) | Gate | Gate 10 / 25 / 50 / 75 / 90 % | never mapped | Per-seq; Arp has its own |
| 22–30 | 57–65 (A3–F4) | Swing | Off, 52, 54, 57, 60, 63, 67, 71, 75 | never mapped | Chart OCR “22–32” is noisy; 9 printed values fit 22–30 |
| 31 | 66 (F♯4) | Sequence Mono | Poly ↔ Mono toggle | never mapped | Chart “Key 40” is copy-paste junk |
| 32 | 67 (G4) | Sequence Overdub | Overdub on/off | never mapped | Chart “Key 41” |
| 33–36 | 68–71 (G♯4–B4) | Scale Chrom / Major / Minor / Blues | Scale select. Minor = Shift+C4 (third C) | never mapped | |
| 37 | 72 (C5) | Scale User | User scale; hold + lower octave toggles pitch classes | never mapped | |

Shift + Oct+ **and** keys 1–16: separate **Kbd Play** MIDI channel
(§3.2.2). Same keys, extra modifier. Also unmapped in firmware.

There is **no free Shift+key**. A latch cannot live on C2/C♯2/D2.

## 2. Shift + panel (every printed combo is taken)

| Gesture | Stock function | Raw CC we have | Firmware handler |
|---|---|---|---|
| Shift + Hold | Chord mode on/off (§3.1.1) | Shift 86, Hold 85 | never mapped (Chord ON is CC 105 / `0x08005df8`) |
| Shift + Rec | Record-append | Rec 87 | never mapped |
| Shift + Stop | Clear last step (Seq only) | Stop 89 | never mapped |
| Shift + Play | Restart Seq/Arp from step 1 | Play 90 | never mapped |
| Shift + Oct− | Seq: Transpose mode. Arp: octave down | Oct− 16 | never mapped |
| Shift + Oct+ | Seq: Kbd Play. Arp: octave up | Oct+ 17 | never mapped |
| Shift + Mode knob | Skip Seq/Arp positions; apply on release | Mode 21 | `mode_knob_apply` `0x08016a26` is the unshifted path |
| Shift + Time Div | Skip Time Div; apply on release | TimeDiv 104 | never mapped |
| Shift + Rate | BPM fine (internal sync only) | Rate 102 | never mapped |
| Shift + Chord | Control/CC mode; repeat = banks 1–4 | Chord (no JSON id; live CC 105) | never mapped |

## 3. Unshifted panel (mapped at CC, not always as firmware)

| Control | Stock | CC | Firmware |
|---|---|---|---|
| Seq/Arp switch | Seq vs Arp | 18 | P |
| Mode knob | 8 detents, Pattern = 7 = internal 6 | 21 | `set_arp_mode` `0x08011794`, TBH `0x08011a38` |
| Time Div | time division | 104 | not named |
| Rate | tempo | 102 | not named |
| Hold | hold arp/seq | 85 | not named |
| Shift | modifier | 86 | patch reads EVENT `+0x25`; stock Shift router **never named** |
| Rec | step/realtime rec | 87 | not named |
| Stop | stop | 89 | not named |
| Play | play/pause | 90 | not named |
| Tap | tap tempo; **Rest/Tie** in rec | 103 | not named |
| Oct− / Oct+ | octave | 16 / 17 | not named |
| Chord button | toggle Chord knobs vs CC knobs | 105 | `chord_test_dispatch` `0x08005df8` |
| Type / Notes / Vel>Notes / Strum | chord params; **turning Type also enters Chord mode** | 98 / 99 / 100 / 101 | Type stores `0x0800f4b8` / `0x0800f54e` / `0x0800f6fc` |
| Pitch / Mod strips | bend / mod | 65 / 64 | not named |
| Sync DIP | clock source | 19 | JSON only, not live-confirmed |
| DC in | power sense | 96 | JSON only |

## 4. Other occupied combos (not in the Shift chart, still stock)

| Gesture | Stock |
|---|---|
| Rec + keys 1–16 (channel keys) | Empty sequence length (§4.2.1) |
| Tap while step-recording | Rest / Tie |
| Chord held + play keys | User Chord from those pitches (§3.1.1) |
| Type knob without Shift | Enters Chord mode |

MCC-only (no panel Shift): MIDI In CH, MIDI Thru, User Channel, curves,
sync clock format, tempo jump/pickup, tap average, Next Seq, Transpose
latch / port / channel, velocity as-recorded vs fixed, CC bank values.

## 5. Not in the 1.1 Shift chart (candidate novel gestures)

These are the only panel-adjacent holes. **None are firmware-proven
no-ops yet.** Do not steal a silkscreened Shift+key.

| Candidate | Why it looks free | Risk |
|---|---|---|
| **Chord held, then Rec** (no Shift) | KS37 1.1 never assigns it. Other-repo GEN already uses this pair; Rec still needs both press **and** release ownership so stock Record does not fire | Must swallow Rec, not piggyback |
| **Shift + Tap** | Tap is Rest/Tie only in rec; Shift+Tap is absent from §3.6.6 | Firmware might still do something; must disassemble `0x08004930` router |
| Shift + Mod strip | Not listed (mk2 uses Shift+pitch for Gate — **we are not mk2**) | Unknown |
| C2’s Shift + Type | Not in the Shift chart; Type still does chord Type | Piggyback, not a steal. Type-without-Shift already enters Chord mode. **Do not use this for E3 latch** if C2 still wants it |

**Ruled out:** Shift+C2 / C♯2 / D2 / keys 1–16 (MIDI CH). Any other
Shift+key in the five silkscreen bands.

## 6. Why e3b “off” could not work

`shift_note_hook` watches Shift + MIDI 36/37 on the **note** path
(`0x0801b75a`). Stock treats those keys as **Keyboard MIDI CH**. Two
failures, both expected from the manual:

1. The combo is already owned. Hear-tests that “did nothing” were
   changing User Channel (and resetting Kbd Play CH).
2. Shift+channel keys may never appear as Note-On on that hook, so
   `FLAG_RAM` stays at whatever unused SRAM had at boot (often 1 →
   Euclidean already on).

Do not rebuild e3b on MIDI 36/37. Pick a gesture from §5, then map
that pair in the button router before writing Thumb.
