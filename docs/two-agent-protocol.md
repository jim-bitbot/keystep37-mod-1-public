# Two-agent protocol — understand 1.1.6.579

**Read this before writing any file.** Cursor (this WSL repo session) and
Claude work **in the same repo at the same time**. Conflicts are avoided
by **file ownership**, not by hoping git merges.

Jim is merge gate and the only person who commits. Agents do not `git
commit` / `git push` unless Jim asked in that message.

Current goal: machine model of stock 1.1.6.579. No `.led`, no
`build_patch.py`, no live flash, no occupancy re-run. Method:
[ARTURIA-FIRMWARE-RE-GUIDE.md](ARTURIA-FIRMWARE-RE-GUIDE.md). Layers:
[HANDOFF.md](HANDOFF.md) resume items 1–6.

---

## 1. Who you are

| Agent | Identity in this repo |
|---|---|
| **Cursor** | Local WSL tree. Capstone scans, catalog rows, `recreate.py`. |
| **Claude** | Same tree (or a clone Jim keeps in sync). Decompile narrative, object/handler stories, **proposed** catalog rows only. |

If you are not sure which you are: Cursor owns `firmware-re/notes/scans/`.
Claude owns `firmware-re/notes/model/`. If you would edit the other
directory, **stop**.

---

## 2. File ownership (hard)

**You may write only files in your column.** Reading anything is allowed.

| Path | Cursor | Claude |
|---|---|---|
| `firmware-re/notes/scans/**` | **WRITE** | read |
| `firmware-re/scripts/scan_firmware.py` | **WRITE** | read |
| `firmware-re/scripts/scan_*.py` (new scanners) | **WRITE** | read |
| `firmware-re/ghidra/recreate.py` | **WRITE** | read |
| `firmware-re/notes/address-catalog.md` | **WRITE** | read |
| `docs/HANDOFF.md` (ticket-close, 3–6 lines max) | **WRITE** | read |
| `firmware-re/notes/model/**` | read | **WRITE** |
| `docs/two-agent-protocol.md` | neither, unless Jim asked | neither |
| `firmware-re/notes/findings-2026-09-20.md` | **neither** | **neither** |
| `firmware-re/patches/**`, `build_patch.py`, E0–C2 `.led` | **neither** | **neither** |
| `README.md`, other `docs/*` | **neither** this phase | **neither** |
| `stock-shift-map.md` | **neither** (occupancy done) | **neither** |

**Shared files that both used to edit (`HANDOFF`, catalog, `recreate.py`)
are Cursor-only.** Claude never patches them. Claude puts proposed rows
in `firmware-re/notes/model/<ticket>-proposed-catalog.md`. Cursor copies
accepted rows across.

If you need a change in a file you do not own: write a request at the
**bottom** of **your** ticket file (`## Request to Cursor` / `## Request
to Claude`). Do not edit their tree.

---

## 3. Same-tree rules (both sessions open)

Assume Jim has **two editors on one working copy**. Autosave will
overwrite. Therefore:

1. Never open-and-save a file you do not own (even a “tiny typo”).
2. Never format-on-save a foreign file.
3. Never run a repo-wide formatter / `git add -A`.
4. New files go **only** under your directory, named with the ticket
   letter: `scans/A-boot.txt`, `model/A-objects.md`.
5. Do not create files at repo root except if Jim asked.

If Jim uses **two clones** (WSL + Windows): same ownership. Pull before
you start; do not push; Jim copies or commits.

---

## 4. Ticket file header (required)

Every ticket file starts with:

```
STATUS: in-progress | done | blocked
AGENT: cursor | claude
TICKET: A
UPDATED: 2026-09-22T21:00+01:00
INPUT: (path you read, or "none")
```

`STATUS: done` means the other agent may consume it. Do not consume
`in-progress` files — wait.

---

## 5. Waves (what to do when both start at once)

Do **not** both start catalog rows. Follow the wave. If the other agent
has not finished their input, work the **parallel** column in the same
wave, or stop.

### Wave 1 — start here, both at once

| Agent | Write only | Job |
|---|---|---|
| **Cursor** | `firmware-re/notes/scans/A-boot.txt` | Reset_Handler `.data`/`.bss` ranges; every `bl` in ctor sweep ~`0x08014d08`; analog `r1` kinds; literal RAM bases if obvious. Raw addresses + 8–20 insns. No prose novel. |
| **Claude** | `firmware-re/notes/model/prep-islands.md` | Inventory of names already in `recreate.py` + catalog. What is still missing for layers 1 and 3. Claims from `other repo/` listed as **claims**, not facts. |

Cursor must `STATUS: done` on `A-boot.txt` before Claude starts Wave 2
objects. Claude must not wait idle: `prep-islands.md` does not need the
scan.

### Wave 2 — after `scans/A-boot.txt` is `done`

| Agent | Write only | Job |
|---|---|---|
| **Claude** | `model/A-objects.md` and `model/A-proposed-catalog.md` | Object table: name, ctor VA, RAM base, vtable, `+0x58` / kind. Every row tagged P/S/H/X. Proposed catalog markdown **only** in the proposed file. |
| **Cursor** | `scans/B-shift-ram.txt` | All loads of `0x200010d2` (expect ~18). VA + 20 insns context each. Number them 1…N. |

These two files are in **different directories** — safe in parallel.

### Wave 3 — after `scans/B-shift-ram.txt` **and** `model/A-proposed-catalog.md` are `done`

| Agent | Write only | Job |
|---|---|---|
| **Cursor** | `address-catalog.md`, `ghidra/recreate.py`, 3–6 lines at top of HANDOFF resume | Copy **accepted** A rows (P or S only). Add Ghidra names for confirmed function **starts** only. HANDOFF: “Ticket A closed: objects N.” |
| **Claude** | `model/B-shift-handlers.md` and `model/B-proposed-catalog.md` | Map scan sites 1…N onto `stock-shift-map.md` gestures. Unmapped = “unknown stock secondary”. |

### Wave 4+

Same pattern:

- Cursor: `scans/<letter>-*.txt`
- Claude: `model/<letter>-*.md` + `model/<letter>-proposed-catalog.md`
- Cursor (next wave): catalog + `recreate.py` + short HANDOFF

**Queue (parked 2026-09-22):** [`../firmware-re/notes/scans/tickets.md`](../firmware-re/notes/scans/tickets.md).
That file is the letter list. It splits old D–G and adds L–Q.
Do not invent a letter that is not in it.

Letter sequence: **A** boot, **B** Shift-RAM, **C** main loop/IRQs,
**D** analog knobs, **E** keys, **F** button TBHs, **G** remaining ctors,
**H** shared `0x200051cc`, **I** time, **J** voice, **K** protocol,
**L** recorder, **M** chord/scale, **N** sync, **O** persist, **P** LED/DMA,
**Q** promote H. USB stack and bootloader stay out.

---

## 6. Catalog row rules

Claude proposes; Cursor commits to `address-catalog.md`.

```
| `0x0800xxxx` | | short_name | one-line what | P or S or H or X |
```

- **P** = live protocol or occupancy CC matched an immediate in code
- **S** = disassembly structure (prologue, TBB, callers)
- **H** = hypothesis (including anything from `other repo/` not re-traced)
- **X** = ruled out

Raw Thumb wins. Ghidra `unaff_r*` / `NMI` / `UsageFault` in a decompile
= wrong function start → **X** or fix the entry, do not story-tell.

Cursor must **not** promote H → P without a scan or live fact. Cursor
may drop a proposed row and leave a one-liner in HANDOFF ticket-close
(“rejected H: …”).

---

## 7. What each agent must not do

**Both**

- No `git commit` / `push` / `add -A` unless Jim’s message says so
- No live flash, no `--live`, no MCC Test-20, no occupancy prompts
- No edits under `firmware-re/patches/`
- No “while I’m here” README cleanup
- No rewriting `findings-2026-09-20.md`

**Cursor**

- Do not write under `firmware-re/notes/model/`
- Do not invent object names in the catalog that Claude has not proposed
  (except scan-only rows: `ctor_bl_0x08014dd2` style, tag **S**)
- Ticket-close HANDOFF edit: **append 3–6 lines under the current resume**,
  do not rewrite the whole file

**Claude**

- Do not write `address-catalog.md`, `recreate.py`, `HANDOFF.md`, `scans/`
- Do not add Thumb names to `recreate.py`
- Do not treat occupancy CCs as stock MIDI (they are control IDs)

---

## 8. Blocked / conflict

If the file you need is `STATUS: in-progress` by the other agent: **stop
that ticket**. Switch to your other Wave column, or reply to Jim:
`blocked on scans/A-boot.txt (in-progress)`.

If you accidentally edited a foreign file: revert that file only
(`git checkout -- <file>` if Jim allows; otherwise tell Jim the path).
Do not “fix forward” on their file.

---

## 9. First messages (copy-paste)

**To Cursor, Wave 1:**
“Follow `docs/two-agent-protocol.md`. You are Cursor. Wave 1: write
`firmware-re/notes/scans/A-boot.txt` only. Stop when STATUS: done.”

**To Claude, Wave 1:**
“Follow `docs/two-agent-protocol.md`. You are Claude. Wave 1: write
`firmware-re/notes/model/prep-islands.md` only. Do not edit
address-catalog, HANDOFF, recreate.py, or scans/. Stop when STATUS: done.”

**To Claude, Wave 2:**
“`scans/A-boot.txt` is done. Write `model/A-objects.md` and
`model/A-proposed-catalog.md` only.”

**To Cursor, Wave 2:**
“Wave 2: write `scans/B-shift-ram.txt` only. Do not touch catalog yet.”
