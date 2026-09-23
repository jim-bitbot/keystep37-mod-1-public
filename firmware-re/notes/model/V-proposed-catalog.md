STATUS: done
AGENT: claude
TICKET: V
UPDATED: 2026-09-23T22:50+01:00
INPUT: firmware-re/notes/scans/V-persist-commit.txt

# V-proposed-catalog — rows for Cursor to review

Reasoning in `model/V-commit.md`. Format per `two-agent-protocol.md` §6.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (annotate FLASH IRQ4, `0x080186d4`) | | | Zero static callers — purely hardware-triggered, never software-invoked. Confirms it's a real ISR, not a callable commit function | S |
| (annotate `seq_slot_base` caller `0x0800de96`) | | | Stores the slot base into a caller object at `+0x808`, zeroes `+0x802`, writes `0x203` to `+0x804` — same field shape as G-ticket site 46 (`0x200007dc`) | S |

## Explicit missing (per ticket instruction — the deliverable, not a gap)

No RAM-to-flash commit trigger found within the application-level
boundary (`seq_slot_base`'s three callers, stopping before
`0x0800ddf6`/`0x08008290`/`0x08008338`, which may already be ST HAL
territory). Not proposing a commit-path row — genuinely not found in
scope.

STATUS: done
