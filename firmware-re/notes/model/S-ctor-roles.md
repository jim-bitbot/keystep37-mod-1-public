STATUS: done
AGENT: claude
TICKET: S
UPDATED: 2026-09-23T22:30+01:00
INPUT: firmware-re/notes/scans/S-ctor-readers.txt

# S-ctor-roles — readers of G's leftover ctor objects

Read-only pass over `scans/S-ctor-readers.txt` only. 26 sites covered
(G's list minus already-S sites 04/15/16/33/40/24-32/38). Per ticket
instruction: S wherever a reader plus its behavior makes the role
unambiguous, H with reasoning otherwise. Given the scan's size, sites
with a clear, closable finding get full treatment; the rest get
existence-confirmed-only notes.

## Strong findings — role closed or substantially narrowed

### Sites 02/03 (`0x200023d0`/`0x200023dc`) — closes a C-ticket open item

Reader `0x080154d8` calls into this pair's function family
(`0x0801d69c`) **immediately before the two "early" `button_debounce`
calls** (`0x0801d69c` itself falls through into the calls at
`0x080154e0`/`0x080154e6`) that `C-loop.md` flagged as unexplained —
"two objects, not among the nine [main debounce family]." A second
reader (`0x080158ce`) shows the **same function called again,
immediately before the real nine-object debounce loop begins**
(`0x080158dc` onward). **This closes the open item**: sites 02/03 are
read/reset once per main-loop pass, structurally bracketing both the
early and main debounce sequences — a plausible per-pass scan-state
reset, not named debounce objects themselves. **S** for the timing
relationship; **H** for the specific role (reset vs. counter vs.
something else).

### Site 17 (`0x2000058c`) — strengthens C's "Rate" candidate

Two readers (`0x0801553e`, `0x08015788`) show this object processed in
the **same call group** as analog kind objects 1/2/3
(`0x2000121c`/`0x20001294`/`0x2000130c`), in the same order, right
before/after `analog_knob_process` calls on those same three objects.
`0x08015788`'s call (`bl 0x8005d68`) is the **exact address** `C-loop.md`
already flagged as the "third detent-object" candidate. This is tight
structural correlation, not proof — **H, but meaningfully strengthened**
from "flagged once" to "consistently grouped with the analog kind
family across two independent call sites."

### Site 45 (`0x20002ddc`) — this is panel_button_dispatch's own object

Reader `0x08015934` (`ldr r0,[pc]; bl 0x08017260`) is a **direct static
call into `panel_button_dispatch` with this object as `r0`** — this is
one of the three `panel_button_dispatch` call sites `C-loop.md` cited
by address (`0x08015936`, off by the `ldr`+`bl` pair) without knowing
what object they operated on. **Closes that gap: `0x20002ddc` is
`panel_button_dispatch`'s object.** Also confirmed: this object holds
the AutoTest-adjacent flags `+0xb9`/`+0xbc` (zeroed together at
`0x0801558c`/`0x08015592`, same shape as `H-shared.md`'s AutoTest
cluster, but on this address, not `0x200051cc`) — a **second, separate**
AutoTest-flag pair, not the shared block's own. **S** for the
panel_button_dispatch link (direct `bl`); **H** for the AutoTest-pair
relationship to the shared block's own `+0xb9`.

### Site 49 (`0x20001d60`) — ties into R's port object family and button dispatch

Three readers (`0x08017f84`, `0x08017ff2`, `0x08018048`) sit **inside
the shifted `panel_button_dispatch` TBH region** F already mapped
(indices 7/8 territory). This is the same object `R-usbdin.txt`
identified as part of the port-switch ctor chain (`0x0801acb0`, built
alongside `0x20001e04` and `0x20001eb8` from the same ctor-sweep
group). **S** for both link facts (button-dispatch region, R's ctor
chain); **H** for what the object actually represents — it now looks
like a genuinely shared object between the button and note/port
subsystems, not confined to one.

### Site 51 (`0x20001eb8`) — a second reset entry point, tied to playback

Confirms all four `E-keys.md` callers exactly (`0x0800cdf8`,
`0x0800cf2e`, `0x0800d062`, `0x08010324` → `0x0801b750`). **New**:
reader `0x08013f04` (inside `play_time_step`'s region, near the
pitch-gate check) calls `0x0801b5ea` — the same reset-shaped function
(`strb #0,[r0,#0x516]`, `bl 0x0801c460`) already visible in this
object's own ctor body (`lead-usb-din.md`). **This means the object
gets partially re-armed during playback, not just at boot.** **S** for
the call site and function identity; **H** for why playback re-arms it.

## Reinforcing findings — existing role, more evidence

### Site 50 (`0x20001e04`) — confirmed touched by all four analog kinds

Already established (M ticket) as the scale-mask object base. This
scan shows it's read inside **every one of the four non-strip analog
TBH cases** (kinds 1-4: `0x0800527c`, `0x080054c6`, `0x080056cc`, plus
`0x08005476`/`0x0800569a`/`0x0800589a`/`0x080058d2`), not just the
scale-specific path M walked. **S** — extends, doesn't change, the
existing finding.

### Sites 52/53 (`0x20001180`, `0x20001204`) — calibration-table family

66 and 4 outside-ctor readers respectively, both showing the same
shape: call `0x801cd5a`-family functions, branch to the shared exit
`0x8004986` (`analog_knob_process`'s own common-exit label). Site 52's
readers repeatedly compare against `0x8000` (signed 16-bit half-range)
— consistent with a per-kind calibration/curve table (candidate:
`KeyStep37.json`'s "Knob Catchup = 2 (Scale)" setting, not confirmed).
**S** for existence and the shared-exit call pattern; **H** for the
calibration-table interpretation.

## Existence-confirmed only (readers found, role not resolvable this pass)

- **Site 01** (`0x20000410`) — grouped at every call site with sites
  02/03 (same three-ctor cluster). One reader (`0x08015246`) stores
  this object into `0x20001160` right before loading GPIOE
  (`0x40011800`) — candidate hardware pin/scan object, **H**.
- **Site 05** (`0x200013fc`) — 34 outside-ctor readers, confirms this
  is a heavily shared notify sink (readers include `chord_test_dispatch`'s
  `0x69` handler, per K). Mostly reinforces already-known role.
- **Sites 06/07** (`0x20002e88`/`0x20002dd0`) — readers show a shared
  ctor-adjacent function family (`0x8019b5c`, `0x8019d34`, `0x8019999c`,
  `0x8019b78`); role not resolvable from shape alone.
- **Sites 08/09/10/11** — chained construction (each ctor's reader is
  mostly the next site's ctor call in the sweep); genuinely little
  outside-sweep reader evidence (2 sites each).
- **Site 12** (`0x20004f00`) — readers tied to `0x20001128`,
  `0x200052d0`; not resolved.
- **Site 13** (`0x200005f8`, `key_scan`'s own analog-adjacent object per
  earlier tickets) — readers confirm it's read right alongside
  `mode_skip_apply`/`timediv_skip_apply`/`analog_knob_process` calls in
  `app_main_loop`'s body (`0x08015770`-`0x08015784`) — consistent with
  its already-known role, not new.
- **Site 23** (`0x200011dc`) — reader `0x080151d2`-`0x08015218` shows
  it paired with each of the nine debounce-family objects
  (`0x20000388`...`0x20000578`) via `0x8019fac` — a per-debounce-object
  companion table, **H** role.
- **Sites 34/35/36** (`0x20000fec`/`0x20000654`/`0x20002cec`) — chained
  construction, readers mostly further ctor calls in the same sweep
  region.
- **Site 41** (`0x20004f18`) — reader ties it to `0x200010d8`,
  `0x200010c0`; not resolved.
- **Sites 46/47/48** (`0x200007dc`/`0x20000668`/`0x200023f8`) —
  readers show cross-reads of `0x200051cc+0x3f`, `0x20001150`,
  `0x20001098` (settings-adjacent addresses from I/O) near site 46's
  reader `0x08015890` — loose tie to settings machinery, **H**.

## Net

2 real open-item closures (sites 02/03 → C's debounce mystery; site 45
→ panel_button_dispatch's object), one meaningfully strengthened H
(site 17 → Rate candidate), two new structural ties (site 49 → button
dispatch + R's object family; site 51 → playback re-arm). The remaining
~18 sites have reader evidence recorded but no role beyond existence —
consistent with the ticket's own expectation that not everything
resolves this pass.

STATUS: done
