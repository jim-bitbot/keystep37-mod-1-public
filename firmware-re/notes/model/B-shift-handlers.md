STATUS: done
AGENT: claude
TICKET: B
UPDATED: 2026-09-22T21:42:49+01:00
INPUT: firmware-re/notes/scans/B-shift-ram.txt; firmware-re/notes/stock-shift-map.md; firmware-re/notes/address-catalog.md

# B-shift-handlers — mapping the 18 `0x200010d2` sites onto stock gestures

Cursor found 18 load sites (2 of them writes: "Shift ON" / "Shift OFF").
Job: tie each to a `stock-shift-map.md` gesture. Confidence is marked
per site — **S** (confirmed by this disassembly), **H** (plausible,
not confirmed), or **unknown stock secondary** (no reasonable candidate
found this ticket, per the ticket instruction). Nothing here is a live
test — no MIDI was sent, this is static reasoning over the scan only.

## Cross-cutting finding first: `0x200051cc` is a large shared object, not a voice object

Before the per-site table — this matters for whoever does layer-1 object
work next. The existing catalog has `0x200051cc` as `voice_obj` with
fields `+0x4d/+0x4e/+0x4f`. `A-objects.md` already added `+0xb9`
(AutoTest flag, confirmed from `analog_knob_process`). **This scan adds
three more confirmed field reads on the exact same address**, from three
more unrelated code paths:

- `+0x59` (sites 03, 04 — compared against `2`, gates a branch, read
  right after each calls `mode_byte_get`)
- `+0x49` (site 12 — a shifted-panel-button case body)
- `+0x5c`, bit 0 (site 17 — right after writing `0x200010b4`, see below)

That's six unrelated field offsets on one address, touched by boot-time
config code, analog processing, mode-knob logic, and panel-button
dispatch. **This is not "the voice object with some extra flags" — it's
a large shared global-state block that a lot of unrelated subsystems
each own one field of.** Worth its own object-layout ticket rather than
folding further fields into the existing `voice_obj` entry quietly.

## Two generic "notify" utilities, reused across most of these sites

- **`0x800dad4`**, called as `(r0=0x200013fc, r1=code)`. Seen at sites
  09 (r1=1 or 2, Shift-dependent), 14 (r1=2, on Shift press), 18 (r1=1,
  on Shift release). `0x200013fc` is a fixed pointer across all calls —
  looks like a display/LED-state or event-code sink, not per-button
  RAM. **Not the same function as `cc_notify`** (`0x08016bc4`, whose
  real push is `0x08016bd4` per the existing catalog) — different
  address entirely, a second, distinct notify path.
- **`0x801d76c`**, called as `(r0 = *0x20001120, r1=code, r2=code)` —
  `0x20001120` is the existing catalog's `subscribe`
  (`0x0801cc5c`) 3-slot subscriber table. Seen at sites 08, 11, 12, 18
  (trailing, possibly-unreached block — see site 18 note). This one
  **is** plausibly `subscribe`'s actual publish call, since it dereferences
  the same table address the existing `subscribe` entry already names.

Neither is proposed as a full catalog row with high confidence on *name*
— proposing both as **S** for "this address is a real function reused
across ≥3 unrelated call sites with a (code) argument," **H** for what
the code values mean.

## Per-site mapping

| Site | VA | Containing fn | Best candidate | Confidence | Why |
|---|---|---|---|---|---|
| 01 | `0x080043be` | `strip_process_b` (`0x08004388`) | §8 "Shift + Mod strip" candidate | **S** (address match) | `stock-shift-map.md` §8 already cites this exact address for the Mod-strip candidate; scan confirms Shift-held skips the MIDI emit here, plus three more early-exit checks (`0x20001084`, `voice_obj+0x59==2`, `*0x20001124+0xf==1`) not previously documented |
| 02 | `0x08004998` | `analog_knob_process` kind 0 (`0x08004918`) | Other strip (Pitch or Mod, whichever isn't site 01) | **S** two-paths exist / **H** which is which | Confirms exactly two distinct Shift-checking strip code paths — one per physical strip — matching §10's own "H: Pitch vs Mod assignment" unresolved note. Does not resolve it |
| 03 | `0x08005a36` | `0x8005a20` | §2 "Shift + Mode knob — skip Seq/Arp positions; apply on release" | **S** | Calls `mode_byte_get` (`0x8005ccc`) directly; this region is adjacent to the confirmed CC21-outbound formula (`0x08005a72`) already in the catalog |
| 04 | `0x08005ace` | `0x8005ab8` | §2 "Shift + Time Div — skip Time Div; apply on release" | **S** | Near-identical structure to site 03 (same shape, same `mode_byte_get` call, different target RAM `0x20001098` vs `0x20001124`). See note below — `mode_byte_get` is evidently a generic getter, not Mode-specific |
| 05 | `0x0800cd62` | `0x800cc48` | — | **unknown stock secondary** | Touches `0x200010b6`, `0x20001084`, writes `0x200010d3=2`; no confident tie to a §1–§6 gesture this ticket |
| 06 | `0x0800cfd8` | `0x800cc48` (same fn as 05) | — | **unknown stock secondary** | Same function as site 05; this branch does a per-index bitmask lookup (`+0x108` array), unrelated-looking to Shift beyond the initial check |
| 07 | `0x08016982` | `0x8016968` | §2 "Shift + Chord" (repeat=banks) or Oct/Tap family | **H**, weak | 2–3-state counter gated on Shift + `0x200010b4`, resets via pointer at `0x20001150`. Shape (count, cap, reset) fits a "repeat" gesture but doesn't cleanly match any single §2 row's described range |
| 08 | `0x08016afc` | `0x8016ac0` | — | **unknown stock secondary**, structurally notable | Proceeds only when Shift is **not** held; uses the subscriber table (`0x20001120`) via `0x801d76c`. Real function, unidentified gesture |
| 09 | `0x080170ac` | `0x8017038` | §2 "Shift + Hold — Chord mode on/off" | **H** | Binary Shift-dependent dispatch (`r1=1` unshifted / `r1=2` shifted) to `0x800dad4`, in the same flash page as `panel_button_dispatch`/shifted-TBH. A clean on/off toggle shape fits Chord-mode-on/off better than any other §2 row, but not confirmed |
| 10 | `0x08017272` | `panel_button_dispatch` (`0x08017260`) | §10 Paths item 3 (already documented) | **S** | This **is** the function the catalog already describes: unshifted TBH at `0x08017282`, shifted branch to (approx.) `0x08017868` |
| 11 | `0x08017cac` | inside `panel_button_dispatch` (no fresh prologue — a TBH case body) | One of Hold/Rec/Stop/Play/Chord shifted cases | **S** it's a TBH case / **unknown** which button | Reads `0x2000116c`, then double-publishes via `0x20001120`/`0x801d76c` with codes `(2,0)` then `(3,1)` |
| 12 | `0x08017cf0` | inside `panel_button_dispatch`, same as 11 | Another of Hold/Rec/Stop/Play/Chord | **S** it's a TBH case / **unknown** which button | Same double-publish shape as 11 but codes `(3,0)` then `(2,1)` and an extra `voice_obj+0x49` check — a different case body, not the same button as 11 |
| 13 | `0x08017d9c` | inside `panel_button_dispatch`, same region | §2 "Shift + Rate — BPM fine" | **H** | 3-way dispatch on an object's `+0x15` field (same offset pattern as site 02's `*0x20001124+0x15` check — possibly the same field reused); increments a counter at `+0x16` with wraparound and calls `0x800d39c` with `r0=0x200013fc`. Incrementing-counter shape fits "fine" adjustment, not confirmed |
| 14 | `0x0801a032` | `0x8019fc4` | **Shift press handler itself** | **S** | `strb r2=1,[0x200010d2]` — this is a write site, not a read. Confirms exactly where the firmware sets Shift held, immediately followed by `0x800dad4(0x200013fc, 2)` |
| 15 | `0x0801a078` | `0x8019fc4` (same fn as 14) | Another compact-ID's handler in the same dispatch cluster | **unknown stock secondary** | Branches on Shift-**not**-held into a 2-way choice keyed by `0x200010d0`, calling one of two near-identical small functions (`0x800c5c8`/`0x800c5ee`) |
| 16 | `0x0801a11a` | `0x8019fc4` (same fn as 14/15) | Another compact-ID's handler, same cluster | **unknown stock secondary** | Same shape as 15, keyed by `0x200010d6` instead, third variant function `0x800c5a2` |
| 17 | `0x0801a288` | `0x8019fc4` (same fn) | §2 "Shift + Oct−" or "Shift + Oct+" (Arp/Seq-mode-dependent) | **H**, moderate | Writes `0x200010b4=6` on first Shift+press, then branches on `voice_obj+0x5c` bit 0 — a mode-dependent branch right after an Oct-shaped button matches §2's Oct−/Oct+ rows, both of which are explicitly described as behaving differently in Arp vs. Seq |
| 18 | `0x0801a5a0` | `0x801a53c` | **Shift release handler itself** | **S** | `strb r2=0,[0x200010d2]` — the release counterpart to site 14. Followed by `0x800dad4(0x200013fc, 1)`. Trailing bytes after the unconditional `b` at `0x801a5b4` look like unreached linear-sweep artifacts (further `0x801d76c` calls at `+2`/`+3`,`1`) — not confidently part of this handler's live path |

## Summary against `stock-shift-map.md`

- **Confirmed, address-level:** site 01 (Mod-strip candidate, §8),
  sites 03/04 (Mode knob / Time Div skip-apply, §2), sites 14/18 (the
  actual Shift press/release RAM writes), site 10 (panel_button_dispatch
  itself, already documented in §10).
- **Plausible, not confirmed:** sites 02 (which strip is which), 07 and
  17 (Oct/Tap/Chord family — two candidate sites, three candidate
  gestures, not resolved), 09 (Shift+Hold/Chord toggle), 11/12 (two of
  the five shifted-TBH button cases, un-identified which), 13 (Rate).
- **Unknown stock secondary** (no candidate found this ticket): sites
  05, 06, 08, 15, 16.

That leaves **5 of 18 sites genuinely unmapped** and **6 more mapped to
a gesture family but not a single confirmed gesture** — down from 18
completely uncharacterized load sites at the start of this ticket. Every
site's containing function and RAM neighbours are recorded above so the
next pass doesn't have to re-disassemble to pick up where this left off.

Nothing here touches Shift+keys 1–16 (note path, `0x0801b750`, not this
RAM byte's button-side callers) — consistent with the existing
"Shift+keys are the note path, not this button TBH" note in §10.

STATUS: done
