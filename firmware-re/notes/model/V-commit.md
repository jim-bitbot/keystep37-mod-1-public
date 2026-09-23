STATUS: done
AGENT: claude
TICKET: V
UPDATED: 2026-09-23T22:50+01:00
INPUT: firmware-re/notes/scans/V-persist-commit.txt

# V-commit — application-level RAM to flash, stopped at the ST HAL boundary

Read-only pass over `scans/V-persist-commit.txt` only. Per ticket
instruction: application-level only, not reversing ST HAL internals.

## 1. FLASH IRQ4 has no static caller at all

`0x080186d4` — zero static `bl`/`b` call sites found anywhere in the
image. Its **only** path in is the vector table entry (`C-loop.md`,
`[20] 0x08004050 = 0x080186d5`). **S.** This means the FLASH IRQ is
purely hardware-triggered (a real flash-controller interrupt firing),
never software-invoked — consistent with it being a genuine ISR, not a
callable "commit now" function. Whatever triggers an actual flash write
must arm the flash controller itself (via the ST HAL, correctly out of
scope) rather than calling this IRQ handler directly.

## 2. seq_slot_base's three callers — none is a flash-write trigger

All three (`0x0800de16`, `0x0800de96`, `0x0800e21a`, from O) now fully
disassembled:

- **`0x0800de16`**: gets the slot base, loads `*0x200010fc[r5]` (the
  same RAM staging-block array `seq_step_store` (L) indexes), then
  `bl 0x0800ddf6`. Shape: read slot base, read a RAM pointer, pass both
  onward — looks like a **read/compare** path, not a write.
- **`0x0800de96`**: gets the slot base, **stores it into a caller
  object at `+0x808`**, zeroes `+0x802`, writes `0x203` to `+0x804`,
  then calls `0x0800ddf6` and `0x08008290`. This is the first
  genuinely write-shaped site — but it writes the *slot base address*
  and two small config halfwords into a RAM object, not slot content
  into flash.
- **`0x0800e21a`**: computes `slot_base + (halfword<<4)`, then
  `bl 0x08008338` — an address-arithmetic + call pattern, consistent
  with indexing into a slot's sub-records, still not confirmed as a
  flash-write trigger.

**S** for all three bodies; **none of them is confirmed to trigger an
actual flash program/erase operation** — `0x0800ddf6`, `0x08008290`,
and `0x08008338` are the next functions to check, and per the ticket's
own scope boundary, that's exactly where "application level" ends and
"ST HAL" begins.

## 2a. `0x200007dc` reappears — ties O and L together

`0x0800de96`'s `+0x808` store target is the **same object shape** (and
plausibly the same object) G-ticket's site 46 (`0x200007dc`) already
showed has a `+0x808` word field. This links O's slot-base caller
directly to a previously-flagged G object — worth noting even though
it doesn't itself close the commit-path question.

## 3. Honest conclusion

**No RAM-to-flash commit trigger found at the application level.** All
three `seq_slot_base` callers do read/setup/indexing work around the
slot base; none contains a visible flash-program call before this
scan's boundary. Per the ticket's own scope, the next step is
`0x0800ddf6`/`0x08008290`/`0x08008338` — but those may already be past
the "application vs. ST HAL" line this ticket was told to respect. This
is a real, bounded negative result: the commit path, if it exists in
software at all (vs. e.g. a save-on-idle timer this ticket didn't
search for), is not visible from `seq_slot_base`'s three known callers
alone.

STATUS: done
