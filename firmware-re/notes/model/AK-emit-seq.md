STATUS: done
AGENT: claude
TICKET: AK
UPDATED: 2026-09-24T01:25+01:00
INPUT: firmware-re/notes/scans/AK-emit-seq-slots.txt

# AK-emit-seq — the ctor writes +0x18/+0x1c after all

Read-only pass over `scans/AK-emit-seq-slots.txt` only. This is the
scan that caught my own under-reading of `0x0801acb0`'s body — full
detail and the correction to `R-usbdin.md`/`Z-usbdin-emu.md` is
written up in those files; this is the ticket-native record.

## 1. The ctor is an 8-word copy, not 6

`0x0801acb0` copies `+0` through `+0x1c` (8 words total) from its
call-site stack, not the 6 words (`+0`-`+0x14`) `R-usbdin.md`
originally traced. The two extra words (`+0x18`/`+0x1c` — exactly the
fields `emit_seq`'s Note-On path reads) come from the ctor's own stack
at `sp+0x24`/`sp+0x28`. **S** — directly shown
(`stm.w r3,{r0,r1}` at `0x0801acee`, `r0`/`r1` loaded from
`sp+0x24`/`sp+0x28` just before).

## 2. What still isn't known: the actual values

This scan correctly stopped short of re-deriving what the ctor-sweep's
own stack setup puts at `sp+0x24`/`sp+0x28` at the call site — that
would mean walking further back into the sweep's own argument
preparation, not attempted here. **Explicit missing, stated by the
scan itself**: "Sweep stack contents for those slots were not
re-derived here." So while the *fields exist and get written*, *what*
gets written into them (a real function pointer, a null, a sentinel)
is still open.

## 3. The two other hits were red herrings, correctly ruled out

The scan also checked `0x20001e04` and `0x20001eb8` for `+0x18`/`+0x1c`
activity and found some — but explicitly identified both as unrelated
(a `strb [r4,#0x1c]` on a different object, and a stack slot
`[sp,#0x1c]`, not the emit_seq vtable fields). **S** — good, careful
disambiguation on the scan's part, not a false lead.

## Net

Closes the "is this dead code" question `Z-usbdin-emu.md` raised: no,
the fields are populated, my own earlier ctor trace just stopped one
`stm.w` short. Narrows the remaining question to "what specific values"
rather than "populated or not."

STATUS: done
