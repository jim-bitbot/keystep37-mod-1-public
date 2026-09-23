STATUS: done
AGENT: claude
TICKET: L
UPDATED: 2026-09-23T22:15+01:00 (corrected per Cursor's review)
INPUT: firmware-re/notes/scans/L-record.txt

# L-proposed-catalog — rows for Cursor to review

Reasoning in `model/L-record.md`. Format per `two-agent-protocol.md` §6.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (annotate `0x08014416`) | | | Confirmed real ctor-sweep call target (`r0=0x200050c0`), just an inert `bx lr` ctor. Closes the A/G flagged gap fully | S |
| (annotate slot header fields `+0x400`/`+0x401`/`+0x402`) | | | **Correction to my earlier proposal**: the *stores* to these three fields are confirmed S (own disassembly, TBB cases 0/1/2). The names Length/Swing/Gate are **not** shown by this scan — those stay H, still the old external-source table. Case 2's selector byte (`0x62`) collides with the Type knob's own CC immediate — worth caution, not proof either way | S (stores only), H (names) |
| `0x200010b6` | | rec_armed_flag (tentative) | Set to `1` on unshifted Rec press (`0x0801780c`), cleared to `0` on the `r2==0` table's index-5 case (`0x08017b1a`). Read by `key_scan` (F's site 05) and `play_time_step` (`0x08013f1c`) | S |
| `0x080065e4` | | (annotate as `seq_step_store`'s sole caller) | `r0 = *0x200010b8`, `r1 = r6` | S |

## Not proposed

The per-step cell-write case (TBB case 3), the two tail flags
(`0x200010d5`, `0x200010a9`), and Rec LED — no role evidence beyond
existence/gating shown in this scan.

STATUS: done
