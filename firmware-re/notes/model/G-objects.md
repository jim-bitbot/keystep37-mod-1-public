STATUS: done
AGENT: claude
TICKET: G
UPDATED: 2026-09-23T20:20+01:00
INPUT: firmware-re/notes/scans/G-ctors.txt

# G-objects — leftover ctor-sweep objects (continuation of A)

Read-only pass over `scans/G-ctors.txt` only. Existence of each
object/ctor pair is **S** (directly shown). Role is **H** unless a
later ticket (B/C/D/F/I) already established it — noted per row.

## Object table

| Site | Ctor VA | RAM | First store | Role | Tag |
|---|---|---|---|---|---|
| 01 | `0x0800c70c` | `0x20000410` | `+0` vptr | Unknown object, vptr-bearing (like `analog_knob_ctor`'s shape) | S existence, H role |
| 02 | `0x0801d35a` | `0x200023d0` | `+7` | Small flag-bearing object; second function at same site does bit-clear on `r0[r3]` — bitmask-table shape | S existence, H role |
| 03 | `0x0801d680` | `0x200023dc` | `+0` (`str r1,[r0]`) | Followed by a 4-entry loop zeroing `+4/+0x11/+8` per index — array-of-4 struct | S existence, H role |
| 04 | `0x0801d6e4` | `0x20002d90` | `+0` | **Role known**: this is the object `C-loop.md` §3 confirmed `app_main_loop` registers into the subscriber table (`0x20001120`) at startup. Ctor VA now confirmed | S existence, S role (via C) |
| 05 | `0x0800d358` | `0x200013fc` | `+0x94c` | **Role partially known**: this is the same address `notify_013fc`/`notify_display` (B ticket) is called with as `r0` — this ctor is that object's initializer. Zeroes/sets several fields (`0x94c`,`0x948`,`0x950=0x30`,`0x951=0x55`,`0x952=1`,`0x95d=0xff`) | S existence, H (field roles) |
| 06 | `0x08019988` | `0x20002e88` | `+4` | Shape: zero `+4/+5/+8/+0`, then `r1`→`+6`, `r2`→`+7` — small 2-arg init, family shape (compare to 24-32 below) | S existence, H role |
| 07 | same ctor as 06 | `0x20002dd0` | — | Second instance of the 06 ctor | S existence |
| 08 | `0x08006b68` | `0x20002cdc` | `+0` | `0xff,0xff` then zero `+4`, `r1`→`+8`, `r2`→`+0xc` | S existence, H role |
| 09 | `0x08006bec` | `0x20002cf8` | `+0` vptr | vptr-bearing; `r1`→`+8`, `r2`→`+0xc` (halfword), `r3`→`+0xe` (halfword), stack args →`+0x10`/`+4` | S existence, H role |
| 10 | `0x08006d20` | `0x20002dbc` | `+0` vptr | vptr-bearing; zero `+4`(halfword)/`+0xc`; literal `0x319c`→`+6`; `r1`→`+0x10`, `r2`→`+8`(halfword) | S existence, H role |
| 11 | `0x080069f8` | `0x20002e80` | `+0` vptr | vptr-bearing; `r1`→`+4`, `r2`→`+5`, `r3`→`+6` (all bytes) — small 3-byte-arg init | S existence, H role |
| 12 | `0x08019178` | `0x20004f00` | `+0` | `r1`→`+0`, `r3`→`+4`, stack args→`+8/+0xc` (words), `r2`→`+0x10`, stack args→`+0x12/+0x14/+0x16` (halfwords) — wide multi-field struct | S existence, H role |
| 13 | `0x080044f4` | `0x200005f8` | `+0x38` | Zero `+0x38`; loop 0-8 zeroing a halfword array at `+2n` and a word array at `+(n+4)*4` — two parallel small arrays, 9 entries each (same 0-8 width as the compact-ID family) | S existence, H role |
| 15 | `0x08005a08` | `0x200004f4` | `+0x6d` | **Role known**: this is `mode_skip_apply`'s own object — the ctor writes `8` to both `+0x6d` and `+0x6e` before `mode_skip_apply` (`0x08005a20`) ever runs on it | S existence, S role (via B) |
| 16 | `0x08005aa4` | `0x20001000` | `+0x6d` | **Role known**: same shape, `timediv_skip_apply`'s object (confirmed by I-ticket: this exact address is what `0x08015782` passes to `0x08005ab8`) | S existence, S role (via I) |
| 17 | `0x08005cd2` | `0x2000058c` | `+0x54` | Zero `+0x54/+0x55/+0x56`. **Role known**: `C-loop.md` §3 item 6 already identified this object as the third detent-style handler called once per loop pass (`0x08005d68`) — candidate "Rate" object, unconfirmed | S existence, H role (per C) |
| 23 | `0x08019f4e` | `0x200011dc` | `+0` | `r1`→`+0`; separate 9-wide loop (`cmp r4,#8`) calling `0x0801d862` and `0x08019f3c` per index — another 0-8-width array structure | S existence, H role |
| 33 | `0x0800c7f0` | `0x20000674` | `+0` vptr | **Role known**: this is `key_scan`'s own object — the RAM `0x20000674` matches `C-loop.md`'s citation of `key_scan`'s `r0` argument exactly. Zeroes `+4`; `0xff`→`+0x121/+0x122`; `0x3c`→`+0x123`; zeroes a cluster of word fields `+0x108..+0x114` | S existence, S role (via C) |
| 34 | `0x0800c486` | `0x20000fec` | `+8` | `r3`→`+8`, `r6`(from a `ldrsb` stack read)→`+9`, zero `+0xa`, `+0xc` (word), `r5`→`+0x10`, `r2`→`+0x11` — 5-arg init | S existence, H role |
| 35 | same ctor as 34 | `0x20000654` | — | Second instance of the 34 ctor | S existence |
| 36 | `0x0800ecd4` | `0x20002cec` | `+0`/`+1` | `0x3c`→`+0`/`+1`; literal `0x2000`→`+4` (word); zero `+8/+9/+0xa` | S existence, H role |
| 38 | `0x08014416` | `0x200050c0` | none — `bx lr` | **Resolved, not a real ctor.** This site is a trivial `bx lr` — no store at all. The `strb.w r3,[r0,#0x403]` the earlier A-ticket flagged nearby (`0x0801442c`) is **inside a different function** (`0x08014418`, `seq_step_store`'s own push), not this site. The A-ticket's "2-byte gap" concern is closed: `0x08014416` does nothing; there is no distinct recorder-object ctor here | S (closed, X on the original hypothesis) |
| 40 | `0x08011d7c` | `0x20002bec` | `+0` vptr | **Role known**: this is the tick object `I-time.md` traces — `0x08015768` loads this exact address and passes it to `arp_seq_tick`. Ctor sets `+6=1`, `+0xe=0x2ee0` (halfword), `+0x10=1`, `+0x11=0xff`, zero `+4/+5/+8/+0xc/+0x12` | S existence, S role (via I) |
| 41 | `0x08019274` | `0x20004f18` | `+4` (per-index) | 32-wide loop (`cmp r3,#0x1f`) writing three parallel arrays at strides `+0x10*n+4`, `+0x8*n+0x88`, `+4*n+4` — a 32-entry table, width matches the "up to 32 unique pitches" note pool capacity already in `address-catalog.md`'s external-source section | S existence, H (matches note-pool claim, not re-derived as confirmation) |
| 45 | `0x080168e8` | `0x20002ddc` | `+0` vptr | vptr-bearing; zero `+0x17/+0x10/+0xc/+5/+0x11/+0x12/+4/+0x13/+6/+7/+8` — wide zero-init, no arg fields taken | S existence, H role |
| 46 | `0x0800dd04` | `0x200007dc` | `+0x800` | `2`→`+0x800`; zero `+0x801`(byte)/`+0x802`(halfword)/`+0x808`(word) — large offsets (`0x800`) suggest this object has a big buffer before these header fields, consistent with a ring-buffer-style object | S existence, H role |
| 47 | `0x08014758` | `0x20000668` | `+0` | Zero `+0`(word)/`+4..+0xa`(bytes, 7 entries) — small array init | S existence, H role |
| 48 | `0x08010748` | `0x200023f8` | `+0x1c` | Zero `+0x1c/+0x20`; then 5 pointer fields (`+0`,`+4`,`+8`,`+0xc`,`+0x10`) each set to `base+offset` (`+8`,`+0x2c`,`+0x38`,`+0x44`,`+0x50`) — a table of 5 sub-object pointers into one base | S existence, H role |
| 49 | `0x0801acb0` | `0x20001d60` | `+4` (`str r3,[r5,#4]!`) | Wide prologue moving several stack args into the object across multiple `stm`/`ldm` blocks — large multi-field struct, not fully resolved in 16 insns | S existence, H role |
| 50 | `0x0801b02c` | `0x20001e04` | `+0x44` | Calls two helpers (`0x801aa84`, `0x801c550`) before its own stores; literal→`+0x44`, zero `+0x48`. **Matches the A-ticket §5 lead** (candidate same object as the scale mask `0x20001e3a`, offset `+0x36` away) — this scan doesn't resolve that offset directly, so the lead stays **H**, now with more ctor detail | S existence, H role (lead not resolved) |
| 51 | `0x0801b572` | `0x20001eb8` | `+0` | Calls `0x801c432` three times on different sub-offsets (`+4`≈self, `+0x18a`, `+0x310`) before its own store — object contains at least 3 nested sub-structures | S existence, H role |
| 52 | `0x08014be8` | `0x20001180` | `+0` (`str r0,[r3],#4`) | **Matches the A-ticket §5 lead** (candidate chord/voice settings object, cited in `voice_interval_load`'s literal pool). A 2-iteration loop (`movs r5,#2`) zeroing `+0..+0xc` and `+0x12` per iteration — array-of-2 sub-records. Lead stays **H**, structure now clearer | S existence, H role |
| 53 | `0x08011536` | `0x20001204` | none in 16 insns (first store-like insn is `stm.w r4,{r0,r2}`) | Nested 0-3 loop inside a 0-3 loop (`cmp r1,#3`/`cmp r3,#3`) — a 4×4 or similar small matrix init | S existence, H role |
| 24-32 | `0x08019f8c` | 9 RAM addrs (A-boot) | `+0xd`=kind tag (`r1`), `+0xe`=`r2` | **Role now S, not H.** `C-loop.md` already supplied the reader (`button_debounce`, 9 calls). This scan supplies the write-side confirmation: `+0xd` is the compact-ID tag (`strb r1,[r0,#0xd]`), matching `F-buttons.md`'s closed compact-index table (0=Hold...8=Chord) exactly by count and order | S existence, S reader (via C), S tag semantics (via F) |

## Notes on two rejected/resolved leads

- Site 38 closes the A-ticket's flagged `0x08014416`/`seq_step_store`
  discrepancy cleanly: `0x08014416` is a trivial `bx lr`, not a second
  ctor. No action needed on that lead going forward.
- Sites 04, 33, 40 close three of A-ticket's "not walked" ctor sites by
  cross-reference to C and I — genuinely new since those tickets didn't
  themselves cite ctor VAs for `0x20002d90`/`0x20000674`/`0x20002bec`.

STATUS: done
