STATUS: done
AGENT: claude
TICKET: AG
UPDATED: 2026-09-24T00:10+01:00
INPUT: firmware-re/notes/scans/AG-persist-wrap.txt

# AG-proposed-catalog — rows for Cursor to review

Reasoning in `model/AG-commit.md`. Format per `two-agent-protocol.md` §6.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (annotate `0x0800ddf6`) | | | **Direction correction**: this is the slot **load** path (flash→RAM, 258-word copy), not a commit/save candidate as `V-commit.md` implicitly left open | S |
| `0x08008290` | | flash_unlock (tentative) | Writes the real STM32 FLASH_KEYR unlock sequence (`0x45670123` then `0xCDEF89AB`) — independently verified against the documented key pair. The actual flash-write trigger this project's persistence chain has been looking for since ticket O | S |
| `0x08008338` | | flash_busy_guard (tentative) | Busy-flag + timeout (`0xc350`) wrapper around flash operations, called from the same region as `flash_unlock` | S |

## Explicit note (per ticket instruction — correctly stopped at the HAL boundary)

Not walking `0x08008290`/`0x08008338` any deeper — that would mean
reversing ST's own flash-program HAL routine, out of scope per this
project's own rules. The unlock sequence itself is confirmed; what
happens after unlock (the actual program/erase cycle) is intentionally
left unexamined.

STATUS: done
