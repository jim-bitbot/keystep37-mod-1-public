STATUS: done
AGENT: claude
TICKET: A
UPDATED: 2026-09-22T21:38:02+01:00
INPUT: firmware-re/notes/scans/A-boot.txt; firmware-re/notes/model/A-objects.md

# A-proposed-catalog — rows for Cursor to review

Full reasoning for each row is in `model/A-objects.md`. Format per
`two-agent-protocol.md` §6. Cursor: promote at will, drop with a
one-liner, or ask — do not silently reclassify H rows to P.

## New section: Boot / ownership

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| `0x0801d310` | | `Reset_Handler` (body) | `.data` copy `0x0801ef78`→`0x20000000`..`0x200001f4`; `.bss` zero `0x200001f8`..`0x20005eac`; then `bl` clock init `0x08006e20`, `bl libc_init_array 0x0801d8c8`, `bl 0x08016838` (falls to `bx lr` — post-init/main, not walked) | S |
| `0x20005eac` | | `bss_end` | Confirmed end of zero-initialized `.bss`. `FLAG_RAM` (`0x20005f00`) is `0x54` bytes past this — provably not zero-guaranteed at reset, not just suspected | S |
| `0x0801d8c8` | | `libc_init_array` | Two ctor-array sweeps; array 1 empty, array 2 is 5 words at `0x0801ef58`-`0x0801ef6c`. Only slot 4 (`0x080150b4`) is understood so far | S |
| `0x080150b4` | | `ctor_sweep_wrapper_live` | `init_array` slot 4. `r0=1, r1=0xffff`, `bl 0x08014d08` — the only call that reaches the ctor-sweep body | S |
| `0x080150c2` | | `ctor_sweep_wrapper_dead` | Not in `init_array`. Hardcodes `r0=0` before `bl 0x08014d08`; gate there requires `r0==1`, so as coded this call is a no-op. Flagging, not fully ruled out (unknown caller) | S |
| `0x08014d08` | | `ctor_sweep` | Gated (`r0==1 && r1==0xffff`) monolithic table of 53 `bl` object-constructor calls. One hand-written init table, not per-object C++ static init (only 5 `init_array` entries exist total) | S |

## New section: Object ctors (analog / strip)

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| `0x08004768` | | `analog_knob_ctor` | vptr `0x0801dee4` at `+0`; kind byte (`r1` arg) at `+0x58`; zeroes `+0x59/+0x5a/+0x5c/+0x5e`; `+0x60=7`. 5 instances, kind 0-4, RAM `0x20000468/0x2000121c/0x20001294/0x2000130c/0x20001384` | S |
| `0x08004224` | | `strip_b_ctor` | Object at `0x2000039c`; zeroes `+0x54/+0x55/+0x56`, halfword-zeroes `+0x58/+0x5a`. Only static caller of `strip_process_b` (`0x08004388`) uses this object — distinct from the analog kind-0 strip object above | S |
| `0x08019f8c` | | `small_indexed_obj_ctor` | Stores `r1` at `+0xd`, `r2` at `+0xe`. 9 instances, `r1=0..8`, RAM `0x20000388/0x20000564/0x2000042c/0x20000440/0x200005e4/0x200004e0/0x20000578/0x20000454/0x20000374`. Count/numbering (0-8) matches `id_to_index`'s compact-ID range exactly, but no reader of these objects has been traced back to button dispatch — structural match only | H |

## Existing rows to strengthen (not rename) — external-source addresses now have confirmed ctors

These already exist in `address-catalog.md` under "Note-pool builder and
sequence double-buffering," tagged as entirely external/unverified.
Proposing a provenance upgrade for **existence only** — the semantic
role stays exactly as unverified as before.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| `0x08013e40` | | ctor of `play_time_step_obj` (`0x20004ed4`) | Object existence + this ctor confirmed by our own disassembly (ctor-sweep site 39). Role ("consumes a step through, retains output pitches") is still the external source's claim, not re-derived | S (existence) |
| `0x0801306c` | | ctor of `seq_block_ptrs` (`0x20002c4c`) | Object existence + this ctor confirmed (site 37). Field roles (`+0` current/`+4` pending) still external/unverified | S (existence) |
| `0x0801161c` | | ctor of `arp_note_pool_builder` target (`0x2000063c`) | Object existence + this ctor confirmed (site 44). Role still external/unverified | S (existence) |
| `0x08013c9a` | | ctor shared by `0x20002dfc` and `0x20002d0c` | Same ctor function builds both addresses (sites 42, 43) — independently confirms the external source's "matched pair" framing structurally. "Primary"/"deferred" labels still external/unverified | S (pairing only) |

## Existing row to annotate — shared object, two field groups

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (no new address — annotate existing `voice_obj` row, `0x200051cc`) | | | Confirmed from `analog_knob_process` (`0x08004936`, independent code path from the voice/chord code the original entry came from): the same address also holds the AutoTest flag at `+0xb9`. One shared object with ≥2 unrelated field groups, not a coincidence of two objects at the same address | S |

## Not proposed — flagging only, see `A-objects.md` §5 for reasoning

`0x20001e04`/`0x20001e3a` possible same-object scale-mask offset;
`0x20001180` possible chord/voice settings object; `0x08014416` vs.
`seq_step_store` (`0x08014418`) 2-byte discrepancy worth a function-
boundary check. All **H**, none proposed as rows — not enough evidence
yet, listed in the model file so the lead isn't lost.

STATUS: done
