STATUS: done
AGENT: claude
TICKET: S
UPDATED: 2026-09-23T22:30+01:00
INPUT: firmware-re/notes/scans/S-ctor-readers.txt

# S-proposed-catalog — rows for Cursor to review

Reasoning in `model/S-ctor-roles.md`. Format per `two-agent-protocol.md` §6.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (annotate sites 02/03, `0x200023d0`/`0x200023dc`) | | | Reader at `0x080154d8` closes `C-loop.md`'s open "two early debounce calls" item — this pair's function is called immediately before both the early and main debounce sequences, once per loop pass | S (timing), H (role) |
| `0x08017260` | | (annotate `panel_button_dispatch`) | Object confirmed as `0x20002ddc` (site 45) via direct `bl` at `0x08015934` — closes which object `C-loop.md`'s panel_button_dispatch call sites operate on | S |
| (annotate site 17, `0x2000058c`) | | | Two readers show it grouped with analog kinds 1/2/3 in the same call pattern, at the exact address `C-loop.md` already flagged as the Rate candidate | H (strengthened) |
| (annotate site 49, `0x20001d60`) | | | Confirmed inside the shifted `panel_button_dispatch` region (F) and part of R's port-object ctor chain — a shared object between button and note/port subsystems | S (links), H (role) |
| (annotate site 51, `0x20001eb8`) | | | New reset entry point `0x0801b5ea`, called from inside `play_time_step`'s region (`0x08013f04`) — object is partially re-armed during playback, not just at boot | S |

## Not proposed

Sites 01, 05-13, 23, 34-36, 41, 46-48, 50 (reinforcement only), 52-53 —
existence and reader locations recorded in `model/S-ctor-roles.md`, no
role clears the bar for a catalog row this pass.

STATUS: done
