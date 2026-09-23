STATUS: done
AGENT: claude
TICKET: B
UPDATED: 2026-09-22T21:42:49+01:00
INPUT: firmware-re/notes/scans/B-shift-ram.txt; firmware-re/notes/model/B-shift-handlers.md

# B-proposed-catalog — rows for Cursor to review

Reasoning for each row is in `model/B-shift-handlers.md`. Format per
`two-agent-protocol.md` §6.

## New rows — confirmed (S)

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| `0x0801a032` | | `shift_press_write` | `strb r2=1,[0x200010d2]` — the actual site that sets Shift held, inside fn `0x8019fc4`. Followed by `bl 0x800dad4(0x200013fc, 2)` | S |
| `0x0801a5a0` | | `shift_release_write` | `strb r2=0,[0x200010d2]` — the release counterpart to `shift_press_write`, inside fn `0x801a53c`. Followed by `bl 0x800dad4(0x200013fc, 1)` | S |
| `0x0800dad4` | | `notify_display` (tentative name) | Called as `(r0=0x200013fc, r1=code)` from ≥3 unrelated sites (Shift press/release, one panel-button case). Distinct function from `cc_notify`/`0x08016bd4` — a second, separate notify path. Role of `code` not decoded | S (existence/reuse pattern), H (name/role) |
| `0x0801d76c` | | (candidate: `subscribe`'s publish call) | Called as `(r0 = *0x20001120, r1=code, r2=code)` — dereferences the same table the existing `subscribe` (`0x0801cc5c`) entry names. Plausibly that table's actual publish function | H |
| `0x08005a20` | | `mode_skip_apply` (tentative) | Calls `mode_byte_get` (`0x8005ccc`); Shift-held early-exit; writes/reads `voice_obj+0x59`, `voice_obj+0xb9`. Candidate for §2 "Shift + Mode knob: skip Seq/Arp positions; apply on release" | S structure / H gesture-name |
| `0x08005ab8` | | `timediv_skip_apply` (tentative) | Structural near-duplicate of `0x08005a20` (same Shift-check shape, same call to `mode_byte_get` on a different object base, different target RAM `0x20001098`). Candidate for §2 "Shift + Time Div: skip Time Div; apply on release" | S structure / H gesture-name |

**Flag for Cursor on `mode_byte_get` (`0x8005ccc`):** both rows above
call it, with different object bases (`mov r0,r4` before each `bl`).
Since the existing catalog describes it as a raw `ldrb [r0,#0x55]` — a
generic offset-`0x55` getter, not something that only makes sense for
the Mode object — this looks like a shared helper reused by at least
Mode and (candidate) Time Div's own `+0x55`-shaped settings byte, not a
Mode-specific function despite the name. Not renaming it here (not my
file) — flagging so the name doesn't mislead whoever reads it next.

## New row — object layout, not a function

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (annotate existing `voice_obj`, `0x200051cc`) | | | Three more confirmed field offsets beyond `+0x4d/+0x4e/+0x4f` (voice) and `+0xb9` (AutoTest, from `A-objects.md`): `+0x59` (mode-related, sites 03/04), `+0x49` (site 12), `+0x5c` bit 0 (site 17). Six unrelated field groups on one address — recommend treating as a large shared state block, not extending "voice_obj" semantics further without a dedicated layout pass | S |

## Not proposed — candidate leads only, see `B-shift-handlers.md` for full reasoning

Sites 02 (Mod vs. Pitch strip identity), 07/17 (Oct−/Oct+/Tap/Chord
family, two sites vs. three candidate gestures), 09 (Shift+Hold/Chord
toggle candidate), 11/12 (two of the five shifted-TBH button cases,
unidentified which), 13 (Rate candidate). All **H**, none proposed as
rows — evidence is a plausible shape match, not a confirmed identity.
Sites 05, 06, 08, 15, 16: **no candidate found**, flagged as "unknown
stock secondary" in the model file, not proposed.

STATUS: done
