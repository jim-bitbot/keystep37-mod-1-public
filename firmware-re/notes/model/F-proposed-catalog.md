STATUS: done
AGENT: claude
TICKET: F
UPDATED: 2026-09-23T20:15+01:00
INPUT: firmware-re/notes/scans/F-buttons.txt

# F-proposed-catalog — rows for Cursor to review

Reasoning in `model/F-buttons.md`. Format per `two-agent-protocol.md` §6.

## Compact-index table (P — every entry a literal in the scan)

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| `0x08006024` | | (existing `id_to_index` row — annotate) | Full closed table confirmed: `0x55`→0 Hold, `0x56`→1 Shift, `0x10`→2 Oct−, `0x11`→3 Oct+, `0x67`→4 Tap, `0x57`→5 Rec, `0x59`→6 Stop, `0x5a`→7 Play, else→8 | P |
| `0x0800606c` | | (existing `index_to_id` row — annotate) | Inverse confirmed, plus index 8→`0x69` Chord (not present in `id_to_index`'s own forward table — Chord is dispatch-only) | P |

## panel_button_dispatch cases

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| `0x0801780c` | | btn_rec_press (unshifted, tentative) | Writes `0x200010b6=1`; conditional `bl 0x0801d7b6(r1=5)` | S |
| `0x08017856` | | btn_chord_press (unshifted, tentative) | `strb #1,[+0xd]` then clears a second field — matches documented Chord-knob-toggle | S structure, H name |
| `0x0801787e` | | btn_shift_hold (shifted, tentative) | Reads `+0xc`, conditional `bl 0x08017180` | S structure, H "Chord on/off" |
| `0x080178c8` | | btn_shift_rec (shifted, tentative) | Reads `+0xf`, then `voice_obj+0x49` | S structure, H "Record-append" |
| `0x080178a8` | | btn_shift_stop (shifted, tentative) | Reads `+0xf==1`, `bl 0x08013788` | S structure, H "Clear last step" |
| `0x08017a34` | | btn_shift_play (shifted, tentative) | `r1=4`, `bl 0x08012334` | S structure, H "Restart from step 1" |
| `0x08017a40` | | btn_shift_chord (shifted, tentative) | Reads `+0x15`, `cmp #2`, `bl 0x08006ec8` | S structure, H "Control/CC bank cycle" |

## B unknowns — structural closes

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (annotate B site 05, `0x0800cd62`) | | | Gated on Shift RAM then `0x200010b6` (same RAM the Rec-press case above writes) then `0x20001084`, inside `key_scan` — Rec-armed-dependent key-scan branch, not a distinct Shift secondary | S |
| (annotate B site 06, `0x0800cfd8`) | | | Gated on `get_arp_mode()==6` (Pattern only), then `0x20001084`, then Shift RAM, inside `key_scan` — Pattern-mode-specific branch | S |
| (annotate B sites 11/12, `0x08017cac`/`0x08017cf0`) | | | Confirmed location: inside the `r2==0` table (index 2 and 3), not the shifted table. Gate conditions and publish codes match B's original description exactly | S (location) |

## Not proposed

Unshifted index 0 (Hold) — call target cut off in the scan window, not
resolved. Unshifted 6/7 (Stop/Play) target addresses not fully shown.
B sites 08, 15, 16 stay unknown-as-a-gesture (15/16 have a plausible
mechanism, tagged H in the model file, not proposed as a named row).
Which physical gesture invokes `panel_button_dispatch` with `r2==0` —
not shown in this scan.

STATUS: done
