STATUS: done
AGENT: claude
TICKET: J
UPDATED: 2026-09-23T20:40+01:00
INPUT: firmware-re/notes/scans/J-voice.txt

# J-proposed-catalog — rows for Cursor to review

Reasoning in `model/J-voice.md`. Format per `two-agent-protocol.md` §6.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| `0x0801b384` | | port_switch (tentative) | `r3` selects callee: `0` and `2` → `0x0801ad20`, `1` → `0x0801ae56`. `r0` is the object | S |
| `0x0801ad20` | | port_emit_key (tentative) | Two indirect calls via object `+4`/`+0x14` (vtable-style). Reached from the key/voice-output function (`r3=0` forced) | S |
| `0x0801ae56` | | port_emit_seq (tentative) | One indirect call via object `+0xc`. Reached from `0x0801b6c4` (`r3=1` forced), which `play_time_step` calls at 6 sites | S |
| `0x0801b6c4` | | seq_send (tentative) | Forces port-switch `r3=1`. 6 static callers, all inside `play_time_step` | S |

## Existing rows to correct

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (existing `voice_interval_load`/`voice_note_on` rows) | | | **Structural correction**: both are labels inside the same function as the common note-processing entry (`0x0801b750`, `E-keys.md`), not separate functions called from `play_time_step`. That function also makes the `r3=0` port-switch call. Recommend the catalog note this instead of implying a separate call chain | S |
| (existing `seq_step_release` row) | | | Caller list narrowed: `0x08011f40`, `0x0801200a`, `0x08012fcc` — none inside `play_time_step`'s own body. "Tie-scan fallback" behavior itself not contradicted, only its stated call-site location | S |

## Explicit missing (per ticket instruction)

Which object field (`+4`/`+0x14` vs `+0xc`) resolves to USB vs DIN —
not shown; the calls are indirect (`blx` on a field value, not a static
address). No row proposed for a USB/DIN VA. Flagging that the real next
step is finding the ctor that populates those three fields, not
re-scanning the port switch itself.

STATUS: done
