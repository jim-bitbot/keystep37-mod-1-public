STATUS: done
AGENT: claude
TICKET: AR
UPDATED: 2026-09-24T01:20+01:00
INPUT: firmware-re/notes/scans/AR-init-sweeps.txt

# AR-proposed-catalog — rows for Cursor to review

Reasoning in `model/AR-init-sweeps.md`. Format per `two-agent-protocol.md` §6.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| `0x08015f74` | | shared_block_init (tentative) | init_array slot 5's target — initializes `0x200051cc` directly. Confirmed defaults for `+0x34/+0x38/+0xbc/+0x3d-0x48` (table in model file), plus a literal pointer at `+0` | S |
| `0x08005da8` | | (unnamed, existence only) | init_array slot 2's target — initializes `0x20000218`, a ~100-entry byte object. No role beyond existence | S existence |
| `0x08010f40` | | (unnamed, existence only) | init_array slot 3's target — trivial 4-byte zero of `0x200002b0` | S |

## Correction row

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (correction to `AI-objects.md`) | | | The "could mean dozens of uncatalogued objects" framing was too strong — all three targets are single-object initializers, not `ctor_sweep`-style tables. Structure was right to check; scale estimate was wrong | S |

STATUS: done
