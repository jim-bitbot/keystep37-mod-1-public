# How to reverse-engineer an Arturia firmware update

A generalized method, distilled from working through the KeyStep 37's
`.led` firmware end to end — decoding it, mapping its code, and getting a
hand-assembled patch onto real hardware. This is written to transfer to
other Arturia products (or similar STM32-based MIDI gear) using the same
`.led` update format, not just this one device. Where a fact is
KeyStep-37-specific, it's marked as an example, not a universal constant.

**This repo's current use of the method** is understanding KeyStep 37
**1.1.6.579** as a machine model (see `docs/HANDOFF.md`). Feature
patching is future work; flash-without-MCC is already closed.

This document describes **method only** — it does not include Arturia's
firmware, binaries, or copyrighted manual content. Everything here is
about how to derive facts yourself from a device you own, for
interoperability/education, not how to reproduce Arturia's own code.

## 0. Before you start: the single biggest trap

**The decoded `.led` file is very likely not a flat memory image**, even
though naive disassembly at a guessed base address will often produce
some plausible-looking code and create false confidence that it is one.
Confirm the container format first (step 2) before doing *any* address
arithmetic, cross-referencing, or hours of disassembly. Getting this
wrong doesn't fail loudly — it produces code that mostly looks right,
with addresses that silently drift further from correct the deeper into
the file you go, and symptoms (garbage decodes, "no callers found",
literal pools that resolve to nonsense) that are easy to misdiagnose as
something else entirely. See "Lessons learned" at the end — this exact
mistake cost real time on this project.

## 1. Get the firmware

- Arturia distributes firmware as a `.led` file, either bundled with
  their MIDI Control Center installer or downloadable per-product. It's
  **uppercase hex-ASCII text** — two characters per payload byte. Decoding
  is one line: `bytes.fromhex(open(path).read().strip())`.
- If you don't have a `.led` file directly, you can also reconstruct one
  from a captured firmware-update USB session (see step 8) — every chunk
  sent over the wire during a real update is a literal slice of this same
  hex text, so reassembling captured chunks in order reproduces the file
  byte-for-byte. Useful as an independent cross-check that your decode is
  right.

## 2. Understand the container format before anything else

Do not assume the decoded bytes are one flat Thumb image starting at file
offset 0. On the KeyStep 37, the real structure was a **Huaxin/midiplus
segment stream** (a container format also seen in other MIDI-controller
firmware update tooling):

```
[18-byte big-endian header] [payload, record_length bytes] [12-byte footer]
...
[18-byte header] [payload] [24-byte footer]     <- last segment only
[18-byte header]                                <- "fill" record, no payload:
                                                    device writes 1KB of 0xFF itself
```

Header layout (`struct.Struct(">7sH7sH")`): 7 arbitrary bytes, a 16-bit
big-endian **offset** (in fixed-size units — 256 bytes on the KeyStep 37),
7 more arbitrary bytes, a 16-bit big-endian **record length**. The offset
field directly gives you the real flash address once you know the base
(`base + offset*unit`).

**How to confirm this before trusting it**: write a tiny parser that
walks the file using exactly this header/payload/footer structure and
checks that it consumes the *entire* file with zero bytes left over. If
it does, on the first try, you've very likely got the right format. If
you have to fudge lengths or skip bytes to make it work, you don't have
it right yet — don't paper over a parse error with a hack, find the real
structure.

Each footer typically ends in a 16-bit **additive checksum** over
`header[2:] + payload + footer[:-2]`, computed as
`(0x10000 - (sum(...) & 0xFFFF)) & 0xFFFF`, stored little-endian. There's
also often a second, whole-file **program checksum** stored in the final
payload's last two bytes, computed the same way but summed over every
segment's payload (fill segments count as N × `0xFF`). "Firmware file CRC
error" style messages from the vendor's own tooling are very likely this
kind of additive checksum, not a CRC16/CRC32 polynomial — don't burn time
brute-forcing CRC variants against a file trailer before checking the
simple additive-sum hypothesis first.

**Extra footer field worth checking**: some formats' footer also encodes
the segment's own target address (a few bytes, often 24-bit big-endian).
If present, **verify it matches the header's own offset-derived address
for every segment** — a mismatch here is a real, dangerous bug class if
you're building a patch (see step 9).

## 3. Extract a flat flash image for analysis

Once the container format is confirmed, write an extractor: for every
non-fill segment, write its payload at `flash_addr - base` into a
byte array pre-filled with `0xFF` (matching erased flash), sized to
cover the full address range you find segments at. Do this
independently twice if you can (e.g. once by hand, once via whatever
tool script you're building) and diff the two outputs — byte-identical
independent implementations is strong, cheap evidence you got the format
right.

**Always analyze the extracted flat image, not the raw framed file.**
Every disassembler, cross-reference search, and literal-pool computation
from here on assumes a flat address space.

## 4. Find the base address and vector table

- Standard STM32 convention: flash starts at `0x08000000`. Confirm by
  disassembling a chunk of the extracted image and checking it produces
  clean, sensible Thumb-2 code (real prologues, sane branch targets), not
  by pure assumption.
- A genuine Cortex-M vector table (initial SP in `0x2000_xxxx` RAM range,
  Reset handler in `0x0800_xxxx` flash range, both with the Thumb bit set)
  may or may not be present in the update file itself — on the KeyStep
  37, the first ~16KB (a protected bootloader region) isn't included in
  the `.led` at all, and the *application's own* vector table starts
  right where the first real data segment lands. Search systematically
  (a plausible SP followed by a long run of plausible Thumb-bit-set flash
  addresses) rather than only checking file offset 0 — if a vector table
  exists, it might not be exactly where you first guess.
- If no vector table is found anywhere by an exhaustive scan, that's a
  real, informative negative result (not a failure) — it tells you the
  bootloader region is separate and not in this file, which matters later
  when you're ruling out hypotheses like "is this function an interrupt
  handler."

## 5. Static analysis: Ghidra, with mandatory manual correction

- Import the flat extract with `analyzeHeadless`, `-processor
  "ARM:LE:32:Cortex"`, `-loader BinaryLoader -loader-baseAddr 0x08000000`
  (or whatever base you confirmed).
- **Ghidra's default function-boundary detection will be wrong often
  enough that you must check for it, every time a decompile looks
  strange.** The reliable tell: `unaff_r4`/`unaff_r6`-style
  "unaffected register" variables in the decompile, or (worse) register
  names that turn out to alias ARM exception-vector symbol names
  (`NMI`, `Reset`, `UsageFault`) at implausibly low addresses. Both mean
  Ghidra's stack-frame recovery started from the wrong entry point.
- **Fix**: don't trust Ghidra's guess. Do a genuine control-flow trace
  from a real `push {..., lr}` a bit earlier in the file (raw disassembly
  with a library like `capstone`, following every branch/call target and
  fallthrough — not just linear byte-by-byte disassembly, which is easily
  fooled by data that happens to decode into plausible-looking
  instructions). Once you find the address that's genuinely reachable
  and starts with a sane prologue, delete Ghidra's wrong function object,
  recreate it at the correct address, and re-run analysis. This single
  technique resolved most of the "corrupted decompile" cases on this
  project.
- Leaf functions (no calls, so no need to push `lr`) can still confuse a
  naive "find the nearest `push {..., lr}`" search — broaden it to any
  `push`, not just ones that include `lr`.

## 6. The most reliable way to find real code: cross-reference from confirmed protocol constants

Don't explore the disassembly blind. Instead:

1. Reverse-engineer the wire protocol first (or as far as you can) by
   capturing real MIDI/SysEx traffic (step 8). You'll end up with
   confirmed numeric constants — control IDs, parameter indices, CC
   numbers, opcode bytes.
2. Search the *entire* binary for immediate comparisons (`cmp`, `subs`
   against that literal value) using a disassembler library, not just
   Ghidra's UI. A single, unambiguous hit is usually the real dispatcher
   or handler for that protocol feature.
3. Decompile the containing function properly (correcting its boundary
   per step 5 if needed) and read what it actually does.

This worked far better than searching for named-sounding functions or
guessing likely addresses. Every solid, confirmed finding on this project
came from tracing forward *from* a wire-protocol fact *into* the code,
never the reverse.

## 7. Finding every dispatch/switch table, not just what Ghidra notices

Ghidra's automatic switch-statement recognizer misses real switches
fairly often in Thumb-2 code. Two techniques that catch what it misses:

- **Scan for `TBB`/`TBH` instructions directly** (Thumb-2's dedicated
  table-branch opcodes) across the whole binary with a disassembler
  library. Parse the preceding bounds-check (`cmp Rn, #N`) to get the
  real case count, and read the table data as raw bytes (not as
  further disassembly) to get every case target — this exhaustively
  finds every genuine switch statement in the binary, not just the ones
  a specific tool's heuristics happened to flag.
- **Scan for `ldr pc, [table + index*4]`-style computed jumps** — a
  different, non-`TBB`/`TBH` dispatch mechanism some compiled code uses.
  Look for an `adr`/`ldr`-then-branch-to-pc sequence right after a bounds
  check.

## 8. Live hardware verification (do this in parallel with static analysis, not after)

- Capture real USB-MIDI traffic (native Linux `usbmon`/Wireshark, or
  Windows-side USBPcap if the vendor's own software only runs there —
  e.g. an actual firmware update session usually only runs from the
  vendor's Windows/Mac app).
- Send safe, standard MIDI/SysEx probes directly to the device
  (`amidi -S`/`-d` on Linux is enough) to test hypotheses about the
  vendor's own custom SysEx envelope — manufacturer ID, session bytes,
  opcode bytes, payload structure.
- **Check for a hidden diagnostic/factory-test mode in the vendor's own
  control software.** On this project, unlocking one (a documented
  config-file change plus a password) turned out to be the single most
  productive source of ground truth: arming a built-in self-test put the
  firmware into a state where the *next* physical control touched got
  echoed back as a raw MIDI CC message in the software's own console,
  even for controls with no CC mapping in normal operation. If a vendor's
  tooling has a "QA"/"repair"/"test" mode field or similar in its own
  config files, it's worth investigating.
- **Verify every static hypothesis against live behavior wherever
  possible**, and treat a mismatch as informative, not an annoyance to
  explain away. A live capture directly contradicting a static guess is
  usually the static guess being wrong.

## 9. Dynamic verification: emulate the specific code, don't just guess statically

When static analysis hits a wall — an indirect/computed call with no
discoverable static caller, a literal-pool value that doesn't resolve to
a sane address, a runtime-computed value you can't pin down by reading
bytes — **the fix is real CPU emulation, and it's cheaper than it
sounds.** A minimal, targeted harness (a couple hundred lines with a
library like Unicorn) that:

1. Loads the flat flash extract into emulated memory at the real base
   address,
2. Sets up a plausible stack pointer and any RAM values the function
   under test reads (plant known, recognizable values at the struct
   offsets you've identified),
3. Sets argument registers, runs from the function's entry to just
   before its return (not the whole program — a bounded window is fine
   and much easier to reason about),
4. Reads back result registers/memory,

...will resolve in minutes what static literal-pool arithmetic can spend
hours failing to pin down, because it doesn't require you to correctly
guess where a literal pool lives or which code/data boundary is right —
the CPU just executes the real bytes and you observe the real result.
**Don't downgrade this to "too big an investment" and settle for a
weaker technique** just because a full framework's built-in emulation
support (e.g. a symbolic-execution framework's bundled CPU emulator)
fails to load in your environment — a minimal, purpose-built harness
aimed at exactly the one or two functions you're stuck on is a much
smaller lift than it looks, and was the single highest-leverage tool
change on this project.

## 10. Cross-version and cross-device diffing (cheap, worth doing early)

- If you have two firmware versions for the **same device**, compare
  them at the content level, not by raw byte offset (a version bump
  typically re-links the whole binary, shifting most addresses by a
  small, smoothly-growing amount — a flat byte diff will show almost
  everything as "different" even when nothing meaningfully changed).
  Search for exact byte sequences from a function you've mapped, cut
  short *before* any embedded `bl`/branch-immediate encoding (those
  literally re-encode to a different value when the callee's address
  shifts, even if the calling function's logic is completely unchanged) —
  this survives re-linking and tells you, cheaply, whether a specific
  piece of code actually changed between releases.
- If you have firmware for a **different but related product** from the
  same vendor, the same technique tells you quickly whether they share a
  compiled codebase at the binary level (worth checking before assuming
  it, and worth checking before investing serious time cross-referencing
  between them) — don't assume shared source implies shared compiled
  bytes; verify it directly and cheaply first.

## 11. If you get to actually building and flashing a patch

- **Recompute every checksum the container format uses** after any edit
  — both the per-segment footer checksum and any whole-file program
  checksum. Write one function that does this correctly and route every
  edit through it; never hand-edit a checksum byte.
- **If a segment's footer independently encodes its own target address,
  verify it after every edit that touches segment structure** (splicing
  a new page in, converting a "fill" placeholder into real data). A stale
  or copied-from-elsewhere footer address is a genuine bricking risk: a
  bootloader that validates the segment's *checksum* but not its
  *address* field will happily program a patch payload over completely
  the wrong region of flash — including the vector table — while still
  reporting success. This is not a hypothetical: it happened on this
  project, and the fix (checking the footer's address field against the
  segment's own header-derived address on every build) is now a
  mandatory step here.
- **Before ever flashing anything, independently re-verify the built
  file yourself** — reparse it, re-check every checksum and address
  field, and byte-diff the extracted flash against known-good stock to
  confirm the change set is *exactly* what you intended (nothing outside
  the specific bytes you meant to touch, and specifically confirm the
  vector table and any other off-limits region is untouched). Do this
  even if — especially if — a tool already reports "verify: OK"; an
  independent, from-scratch re-check catches bugs in the tool itself,
  which is exactly what caught the footer-address bug above.
- **Always keep a known-good, read-only stock image on hand for
  recovery**, and know the vendor's own software recovery path (usually
  "upgrade from file" pointed at the stock file) before attempting a
  custom flash.
- **Learn to distinguish the device's different low-level entry
  states by their LED behavior** before doing any live work — a
  hardware-forced firmware-update mode, a vendor-software-triggered
  update mode, and a factory-reset mode can look deceptively similar at
  a glance but do very different things. Write down the exact LED
  pattern for each once you've confirmed it, and don't proceed on a
  guess.
- **Never force-remove a device that's stuck mid-update** (e.g. never a
  forced USB detach of a device sitting in bootloader mode) — a physical
  unplug is the safe reset; a forced detach at the OS/driver level was
  observed to leave the host unable to see the device at all until a
  physical replug.
- A firmware transfer completing successfully (a "done"/ack status code,
  checksums verifying) and the device **booting back to its normal
  identity** are both necessary but **not sufficient** evidence that a
  patch works as intended. Confirm the actual intended *behavior change*
  live, separately, after confirming the device boots — "it flashed and
  didn't brick" and "it does what I designed" are two different claims
  and need two different checks.

## Lessons learned the hard way (worth reading even in a hurry)

- **A recurring anomaly is a systemic signal, not a local curiosity.**
  If the same "this looks like garbage" symptom shows up more than once
  in unrelated places, stop and ask whether there's one shared,
  structural cause (like a misunderstood container format) before
  patching around each occurrence individually. On this project, the
  exact same "garbage before real code" pattern showed up repeatedly and
  was explained away locally each time; it was actually the periodic
  overhead of the container format from step 2, and noticing the pattern
  once would have saved hours.
- **An early partial confirmation isn't validation of the whole
  assumption.** Finding *some* clean code at *one* location under a
  simplifying assumption (e.g. "this is one flat image") is not the same
  as confirming that assumption holds for the *entire* file. Stress-test
  a foundational assumption against the whole dataset before building
  hours of work on top of it.
- **Verify a relayed claim independently before trusting it, especially
  from a different tool, session, or person** — even (especially) when
  it sounds authoritative and specific. This project hit two separate
  cases where a relayed technical claim from another analysis session
  turned out to need direct, independent re-derivation before it could
  be trusted — once it held up, once it didn't. The discipline of
  re-deriving rather than accepting is what makes either outcome
  trustworthy.
- **"It transmitted successfully" and "it works as designed" are
  different claims.** Keep them separate in your own head and in your
  notes, and check both, every time.

## Legal/ethical note

Everything above is about deriving facts yourself from hardware you own,
for interoperability and modification of your own device — never about
redistributing a vendor's firmware, software, or documentation. Keep your
own notes, tools, and patches separate from the vendor's copyrighted
material, and don't publish the latter.
