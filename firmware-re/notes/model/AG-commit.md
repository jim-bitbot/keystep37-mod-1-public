STATUS: done
AGENT: claude
TICKET: AG
UPDATED: 2026-09-24T02:15+01:00 (corrected per Cursor's PR review — see
"Net" section: this found the HAL flash-unlock sequence, not the
application-level commit trigger V was looking for. That stays X.)
INPUT: firmware-re/notes/scans/AG-persist-wrap.txt

# AG-commit — the flash-unlock HAL sequence, found and verified against real STM32 keys

Read-only pass over `scans/AG-persist-wrap.txt` only. **This does not
close `V-commit.md`'s open item** — see the corrected "Net" section
below. It finds a real, adjacent HAL-level fact (the flash-unlock
sequence), not the application-level commit trigger.

## 1. 0x0800ddf6 is a load, not a save — a direction correction to V

Full body: a 258-word (`0x102`) copy loop, `ldr r0,[r2,r3<<2]; str
r0,[r1,r3<<2]`. At its one fully-shown caller (`0x0800de10`→`0x800de24`,
from V's own trace): `r2 = seq_slot_base(...)` (the **flash** address),
`r1 = *0x200010fc[r5]` (the RAM staging pointer `seq_step_store` also
uses). **The copy direction is flash → RAM**, not RAM → flash. **This
corrects an implicit assumption in `V-commit.md`** — `0x0800ddf6` is
the slot **load** path, not a candidate commit trigger. 258 words =
1032 bytes, close to a full slot's size — consistent with loading an
entire sequence slot into the RAM staging area. **S.**

## 2. 0x08008290 — the real flash-unlock sequence, verified against real STM32 keys

```
0x08008290  ldr r3,[pc]  ; 0x40022000        FLASH peripheral base
0x08008292  ldr r3,[r3,#0x10]                read CR-ish register
0x08008294  tst.w r3,#0x80                   check a lock/busy bit
0x08008298  beq  #0x80082aa                  -> return 1 (locked/busy)
0x0800829a  ldr r3,[pc]  ; 0x40022000
0x0800829c  ldr r2,[pc]  ; 0x45670123        FLASH_KEYR KEY1
0x0800829e  str r2,[r3,#4]
0x080082a0  add.w r2,r2,#-0x77777778         computes 0xCDEF89AB
0x080082a4  str r2,[r3,#4]                   FLASH_KEYR KEY2
0x080082a6  movs r0,#0
0x080082a8  bx lr                            return 0 (unlocked)
```

**`0x45670123` then `0xCDEF89AB` written to the same register is the
exact, documented STM32 FLASH_KEYR unlock sequence** (KEY1/KEY2) — I
independently verified the arithmetic (`0x45670123 + (-0x77777778) mod
2^32 = 0xCDEF89AB`) matches the real, public STM32 reference-manual
constant precisely, the same category of hard verification as `Z`'s
USART/USB register hits. **This is genuinely the flash-write unlock
function** — `AG`'s own scan correctly stopped here, per instruction
("do not reverse HAL"), exactly at the real ST-HAL boundary. **S.**

## 3. 0x08008338 — a busy/timeout-guarded wrapper around flash operations

Checks a state byte at `0x200052b0+0x18`; if already `1`, takes a
different path (`0x80083c8`, not walked). Otherwise sets that byte to
`1` (busy flag), calls `0x80082cc` with `r0=0xc350` (50000 — a timeout
count or microsecond budget), then branches on the caller's own `r4`
argument (`1`/`2` cases). **S** for the shape; this is a real
lock/timeout guard around whatever operation follows, consistent with
guarding a flash program/erase cycle specifically.

## 4. Both functions are called from within the persist code region — not orphaned

`bl-to` search: `0x08008290` has **4** static callers, `0x08008338`
has **4** more, **all** sitting inside `0x0800de00`-`0x0800e400` —
exactly `O-persist.md`'s own slot-base/settings territory, not some
unrelated part of the image. **S** — this isn't a coincidental HAL
function, it's genuinely wired into the persistence code path this
project has been tracing since ticket O.

## 5. Containing function of 0x0800e21a — found, checks magic values

`0x0800e15c` (push `{r4,lr}`): zeroes 4 stack halfwords, then compares
against literal words `0xa3a5`/`0xa4a5` — looks like a slot-header
magic/signature check before proceeding, consistent with validating a
slot's integrity before a write. **S** for the shape; the magic values'
exact role not resolved further here.

## Net for HANDOFF layer (persist) — corrected: the HAL unlock is found, the application trigger is still X

**Correction (Cursor's PR review caught this overclaim):** the
original version of this section said "the RAM→flash commit path
exists and is now located." That overstates it. What's actually
confirmed: `0x08008290` is the real STM32 FLASH_KEYR unlock sequence
(verified against the documented key pair), guarded by
`0x08008338`, both called from 4 sites inside the already-mapped
persist region (`0x0800de00`-`0x0800e400`). **That's a real HAL-level
primitive, correctly identified.** What is **not** shown: that any of
those 4 call sites is specifically the trigger that commits the
RAM-staged sequence data (`seq_step_store`'s `0x200010fc` buffer) to
flash, as opposed to unlocking flash for some other write in the same
region (settings, a different slot field, etc.). **The
application-level commit trigger — "what decides to write this RAM
buffer to that flash slot, and when" — stays X, unresolved.** This is
the correct, real stopping point per the project's "do not reverse
HAL" rule (going further into `0x08008290`'s own callers-of-callers
territory risks exactly that), but the ticket's original framing
claimed more closure than the evidence supports. `V-commit.md`'s "not
found" is **not** superseded — V's negative stands; this ticket adds a
real, adjacent HAL-level fact, not the answer V was looking for.

STATUS: done
