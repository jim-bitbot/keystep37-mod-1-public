STATUS: done
AGENT: claude
TICKET: H
UPDATED: 2026-09-23T20:30+01:00
INPUT: firmware-re/notes/scans/H-shared.txt

# H-proposed-catalog — rows for Cursor to review

Reasoning in `model/H-shared.md`. Format per `two-agent-protocol.md`
§6. No rename proposed — the scan doesn't supply one (see model file).

## Annotate existing `0x200051cc` row — scale confirmed

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (existing `voice_obj`/shared-state row) | | | **197 pc-rel load sites, ~40 unique offsets** — exhaustive count, not the partial 6-offset picture prior tickets had. Confirms this is a large multi-subsystem shared block. Full offset table in `model/H-shared.md`. Recommend the catalog stop implying single-subsystem ownership in prose | S |

## New offsets, existence only (H role)

| Flash VA (example site) | | Name | What | P |
|---|---|---|---|---|
| `0x08012b48` | | `+0x44` field | 19 sites total, heavily used inside `arp_seq_tick`'s window per I-time.txt cross-reference | S existence, H role |
| `0x08006a10` | | `+0x34` field | 16 sites, several as a two-register (r3 then r2) paired read | S existence, H role |
| `0x08012d56` | | `+0x51` field | 12 sites, one inside `arp_seq_tick` (I-time.txt) | S existence, H role |
| `0x0801557c` | | `+0xbc` field | 10 sites, always paired with `+0x3f` where both appear | S existence, H role |
| `0x0801b910` | | `+0x4a` field | 4 sites, paired with `+0x4f` at all three multi-offset sites | S existence, H role |
| `0x08006988` | | `+0x54`/`+0x55`/`+0x56`/`+0x57`/`+0x5b` cluster | Adjacent byte fields read in a repeating pattern across several nearby call sites — candidate small state machine | S existence, H role |

## Not proposed

The remaining ~25 offsets with 1-2 sites each, and the 25 "offset not
in window" sites — existence-only, no role evidence, left in the model
file's table rather than proposed as individual rows.

STATUS: done
