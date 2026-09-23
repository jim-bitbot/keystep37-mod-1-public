STATUS: done (informational only — NOT catalog-copy-ready)
AGENT: claude
TICKET: lead (not a lettered ticket — Claude's own capstone spot-check
while waiting on Cursor's Q scan, not a Cursor scan file)
UPDATED: 2026-09-23T22:15+01:00
INPUT: firmware-re/firmware-images/keystep37_1.1.6.579_flash.bin (own
disassembly via capstone, .venv) — NOT a scans/*.txt file. Tag
provenance accordingly: everything below is S for what's directly
disassembled, exactly as strict as a Cursor scan would be, just not
run through the normal two-agent scan process.

**Do not catalog-copy from this file.** Per Cursor's review: this was
a wait-state side investigation, not a scan — there is deliberately no
`lead-usb-din-proposed-catalog.md` for it. If any finding here is worth
the catalog, it should go through ticket R (`round2-tickets-proposal.md`),
which re-covers this ground as a proper Cursor scan + Claude model pair.

# Lead: USB/DIN port-switch object, partial progress

Chasing `synthesis.md`'s #1 ranked open lead (J-voice.md: which port-
switch object field is USB vs DIN).

## Found: the port-switch object is fixed, not per-instance

`play_time_step`'s all 6 calls into `0x0801b6c4` load the **same fixed
literal pointer, `0x20001eb8`**, confirmed at every one of the 6 call
sites (`0x08013f7c`, `0x0801407c`, `0x08014118`, `0x0801421e`,
`0x080142a8`, `0x08014326`). **S** — this is `G-objects.md`'s own
already-flagged **site 51** (ctor `0x0801b572`), which that ticket
already described as "contains at least 3 nested sub-structures."

## Found: full ctor body confirms 3 sub-structures, each ~0x18a bytes apart

`0x0801b572`'s full body (beyond G's 16-insn cutoff):

```
+0x4   -> bl 0x0801c432   (sub-structure A)
+0x18a -> bl 0x0801c432   (sub-structure B)
+0x310 -> bl 0x0801c432   (sub-structure C)
+0     <- str r6,[r4]     (a pointer field, from the ctor's own r1 arg)
```

`0x0801c432` (the shared per-sub-structure initializer) sets: byte `2`
at `+0`, halfword `1` at `+0x182`, calls `0x0801c410` (not walked),
zeroes `+0x185`. **All three calls pass no argument that differs
besides the base offset** — no peripheral literal (`0x40013800`
USART1, `0x40005C00` USB) appears in `0x0801c432` itself. **S** for what's
shown; the USB/DIN distinguishing data, if any, is either in the
unwalked `0x0801c410`, or set later by a different function per
sub-structure (not found in this spot-check).

## Found (second pass): the 3 sub-structures are per-note tables, and one address matches an existing catalog row exactly

Walked `0x0801c410` (`0x0801c432`'s previously-unwalked call). It's a
128-iteration loop (`r3` 0-0x7f): zeroes a halfword at `base+r3*2+2`
and sets a byte at `base+r3+0x102` to `0x64` (100 decimal), then sets
byte `+0x184` to `0xff`. **A 128-entry halfword array plus a 128-entry
byte array (default value 100) — 128 is the MIDI note-number range.**
This is per-note tracking state, not a MIDI-send function pointer
table. **S** — directly disassembled.

**`0x20001eb8 + 4 = 0x20001ebc` exactly** — matching
`address-catalog.md`'s existing "Input path (external source,
unverified by us)" row for `0x20001ebc`: **"Cross-port/channel pitch
tracker. Releasing a pitch from one 'owner' (port/channel) can clear
its slot while another owner still holds the same pitch."** This own
disassembly independently confirms that address is real, is a 128-entry
(per-MIDI-note) table, and — because there are **three** of these
sub-structures, not one — plausibly one per owner (matching "owner"
being plural in that external claim exactly). **Promoting that
external-source row's existence to S**; the specific "USB owner / DIN
owner / third owner" assignment is still not shown.

## Corrected model: two separate mechanisms in one object, not one

This object (`0x20001eb8`) holds **two distinct things**, not one:

1. **A pointer at `+0`** (set once, externally, at ctor time via
   `str r6,[r4]` where `r6` is the ctor's own argument — not a fixed
   sub-structure). `0x0801b6c4` dereferences *this* field
   (`r0=[r4]`) before calling the port-switch (`0x0801b384`) — so the
   actual MIDI-emit vtable dispatch (`0x0801ad20`/`0x0801ae56`, the
   original "port switch" lead) operates on a **different object**,
   reached through this one pointer field, not on the three per-note
   tables directly.
2. **Three 0x18a-byte per-note tables at `+4`/`+0x18a`/`+0x310`** — the
   pitch-ownership tracker, now fairly well understood structurally
   (each: 128 halfwords + 128 bytes-default-100 + 2 trailing fields set
   by `0x0801c454`/`0x0801c44e`, per the full ctor body already read).

The original USB/DIN question is about mechanism (1) — the vtable at
`*(0x20001eb8)` — not mechanism (2). Mechanism (2) is a real, separate,
now-better-understood finding in its own right (upgrades an existing
external-source-only catalog row), but doesn't itself answer "which
port is which."

## Still not resolved

Which vtable slot (mechanism 1) is USB vs DIN. Which of the three
per-note tables (mechanism 2) is which "owner." The key-path's own
object source (`r0=[r6]` at `0x0801b996`) — not traced to origin.
Stopping this spot-check here; genuinely deeper than a "while waiting"
side investigation should go without becoming a full ticket in its own
right.

STATUS: done
