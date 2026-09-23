STATUS: done
AGENT: claude
TICKET: J
UPDATED: 2026-09-23T20:40+01:00
INPUT: firmware-re/notes/scans/J-voice.txt

# J-voice — cell to port

Read-only pass over `scans/J-voice.txt` only. Per ticket instruction:
bit 7 = retention is already **S** from prior tickets, not reopened —
this scan doesn't contradict it.

## Cell → pitch/vel/tie → Note-On/Off → port

```
play_time_step (0x08013e8c)
  |
  |-- pitch_gate_check (0x08013ebc): seq_step_note -> (pitch+0x7f)&0xff
  |     <=1 -> early return (no note attempt). Confirms existing catalog
  |     exactly; re-derived here from this scan's own bytes. S.
  |
  |-- seq_step_note (0x080130e8): byte at (voice+step*8)*2. Callers:
  |     0x08013ec2 (the gate check above), 0x08013efe, 0x080140b6,
  |     0x080141a6 (three more call sites this scan locates but does
  |     not walk).
  |
  |-- seq_step_gate (0x080130f4): byte+1 of the same cell. Callers:
  |     0x08013f62, 0x08013fde, 0x080141d2 (matches existing catalog's
  |     three E0-hook sites exactly). Bit 7 extracted via ubfx at
  |     0x08013f66.
  |
  |-- seq_step_release (0x0801415c): its OWN push, i.e. not a direct
  |     bl from inside play_time_step. Callers: 0x08011f40, 0x0801200a,
  |     0x08012fcc — none of which are inside play_time_step's own
  |     0x08013e8c-range body. This narrows the existing catalog's
  |     description ("tie-scan fallback... inside play_time_step") —
  |     the call happens from elsewhere, not from play_time_step
  |     itself. S for the caller list; the existing "governs tie/
  |     Note-Off timing" characterization is not contradicted, just its
  |     specific caller was mis-stated as "inside play_time_step."
  |
  \-- bl 0x0801b6c4 (six sites inside play_time_step: 0x08013f7c,
        0x0801407c, 0x08014118, 0x0801421e, 0x080142a8, 0x08014326)
         |
         v
      0x0801b6c4 sets r6=1, passes as r3 to port switch 0x0801b384
         |
         v
      0x0801b384 (port switch, r3 selects callee, r0=object)
        r3==0 -> bl 0x0801ad20            (used by the KEY path, r3=0
                                            forced at 0x0801b992/0x0801b996,
                                            inside the SAME function as
                                            voice_interval_load/voice_note_on)
        r3==1 -> bl 0x0801ae56            (used by the SEQUENCER path,
                                            r3=1 forced by 0x0801b6c4)
        r3==2 -> bl 0x0801ad20 (r2|=0x10) (third case, not reached by
                                            either traced caller)

      0x0801ad20: two vtable-style calls via object+4/+0x14 pairs
                  (blx r3 after ldr r3,[r4,#4] / ldr r3,[r4,#0x14])
      0x0801ae56: one vtable-style call via object+0xc (blx r3 after
                  ldr r3,[r4,#0xc])
```

`voice_interval_load` and `voice_note_on` are **not separate functions
called from `play_time_step`** — they are labels inside the same
function block that starts at the previous `push` (`0x0801b750`, the
common note-processing entry `E-keys.md` already names). That function
also makes the `r3=0` call into the port switch. **This means the key
path and the chord/voice-output path are the same function**, not two
functions that converge — a real structural correction to how those
pieces were previously described as separate. **S.**

## USB vs DIN — still open, but the shape of the answer is narrower now

No `bl` reachable from either port-switch case (`0x0801ad20`,
`0x0801ae56`) loads USART1's base (`0x40013800`) or USB's base
(`0x40005C00`) directly — those calls go through `blx r3` on values
read from the **object's own fields** (`+4`/`+0x14` for case 0, `+0xc`
for case 1), i.e. through a vtable-style indirect call, not a static
address. **This is why static disassembly alone can't resolve which
slot is USB and which is DIN** — the answer lives in whatever
initializes those object fields (a ctor, not found by this ticket's
scan window), not in the port-switch code itself. `0x08018a58`
(USART1 base → `0x200055e4`) and `0x08018b26` (USB base comparison) are
named as the two real hardware-touching sites, but this scan doesn't
trace either back to which object field feeds them. **Explicit missing
per ticket instruction, not a guess.**

What **is** now known: the sequencer emits through port-switch slot
`+0xc` (`0x0801ae56`, one indirect call) and the key path emits through
slot `+4`/`+0x14` (`0x0801ad20`, two indirect calls — plausibly one for
Note-On, one for a second action, not resolved). That asymmetry (one
call vs two) is itself worth keeping: the sequencer's output path is
structurally simpler than the key path's.

## Net for HANDOFF layer 5

Cell reader chain (`seq_step_note`/`seq_step_gate`) is fully confirmed
by this scan's own bytes, matching the existing catalog exactly — no
correction needed there. `seq_step_release`'s caller list is narrowed
(not inside `play_time_step` as such). The genuinely new structural
finding is that voice/chord output and physical-key note processing
share one function, and that both paths end at the same indirect
port-switch mechanism, whose USB/DIN assignment is a real, specific,
not-yet-closed gap — not a general "not done," but "look at the ctor
that fills object fields `+4`/`+0xc`/`+0x14`, not the switch itself."

STATUS: done
