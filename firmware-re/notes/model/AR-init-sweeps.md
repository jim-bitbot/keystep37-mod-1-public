STATUS: done
AGENT: claude
TICKET: AR
UPDATED: 2026-09-24T01:20+01:00
INPUT: firmware-re/notes/scans/AR-init-sweeps.txt

# AR-init-sweeps — the three targets opened; not a repeat of ctor_sweep, but one hits the shared block

Read-only pass over `scans/AR-init-sweeps.txt` only. This closes
`AI-objects.md`'s flagged lead — with a correction to my own framing
of it.

## 1. Correction to AI: these are NOT more 53-object sweep tables

**All three targets are confirmed real, gated functions** (same
`r0==1 && r1==0xffff` check `ctor_sweep` uses), but **none walks a
repeated `bl`-to-fresh-object pattern** — `AR`'s own conclusion is
explicit: "these three are small object inits behind the same gate.
They do not walk a table of ctors." **I overstated the likely scale in
`AI-objects.md`** ("could mean dozens of uncatalogued objects") — the
shape match to `ctor_sweep_wrapper_live` was real and worth checking
(and it was right to check), but the targets turned out to be ordinary
single-object initializers, not sibling sweep tables. Correcting that
framing here rather than leaving it standing.

## 2. Slot 2 target (0x08005da8) — a sizable object, chord-adjacent by proximity

Initializes `0x20000218`: a handful of small fields (3 bytes, a
halfword set to `0xffff` — a "no value" sentinel shape), a 4-entry byte
loop, then a **100-entry** byte loop (`+0xd` through `+0x70`). No `bl`
calls at all. **The very next function in flash is
`chord_test_dispatch`** (`0x08005df8`) — proximity only, not proof of
relation, but worth noting given the size (a 100-entry table is
consistent with a per-note or per-step chord-adjacent structure). **S**
for the object/shape; **H** for any chord connection.

## 3. Slot 3 target (0x08010f40) — trivial

Zeroes 4 bytes of `0x200002b0`. No further structure. **S**, minor.

## 4. Slot 5 target (0x08015f74) — real find: this is 0x200051cc's own initializer

**This is the one that matters.** The function operates directly on
**`0x200051cc`** — the large shared block every other ticket (H, I, J,
M, and more) has been reading fields from without ever finding where
its defaults come from. Confirmed stores:

| Field | Default value |
|---|---|
| `+0` | pointer literal `0x0801ec54` |
| `+0x34` | `0` |
| `+0x38` | `0` |
| `+0xbc` | `0` |
| `+0x3d` | `0x41` |
| `+0x3e` | `0` |
| `+0x3f` | `0` |
| `+0x40` | `0x41` |
| `+0x41` | `2` |
| `+0x42` | `0` |
| `+0x43` | `0` |
| `+0x44` | `3` |
| `+0x45` | `0xf` |
| `+0x46` | `4` |
| `+0x47` | `0` |
| `+0x48` | `0` |

(the last 12 rows via a sub-call, `0x08015d6c`, only the first 20 of
its instructions shown — more fields likely follow, not walked here).
**S — this is the actual default-value source for a field this project
has cited constantly** (`+0x44` alone is read by `arp_seq_tick`, and
gates two of `AS-sync-idr.md`'s new external-pin-check sites). Knowing
its boot default (`3`) is immediately useful context for anyone
re-reading those sites.

## Net

`AI`'s lead is closed: two of the three targets are minor, but the
third is a genuine, useful find — the initializer for the field
project-wide tickets have treated as opaque. Correcting my own earlier
overstatement of scale in the same breath as reporting the real payoff.

STATUS: done
