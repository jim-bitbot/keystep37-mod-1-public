STATUS: done
AGENT: claude
TICKET: K
UPDATED: 2026-09-23T20:45+01:00
INPUT: firmware-re/notes/scans/K-protocol.txt

# K-proposed-catalog — rows for Cursor to review

Reasoning in `model/K-protocol.md`. Format per `two-agent-protocol.md`
§6. No row is tagged P — no immediate in this scan matches a known §10
control ID as this TBB's own index; the two §10-adjacent bytes found
(`0x40`, `0x41`) are second/third-byte sub-selectors inside different
functions, not this dispatcher's index.

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| `0x0800ee92` | | get_global_param_tbb (tentative) | TBB on `([r1] as signed)-1`, gated `r2==0`. Three real targets (127-byte table, 3 populated regions, rest → pop). No SET body on the `r2!=0` branch | S |
| `0x0800614c` | | get_param_b (tentative) | Sibling of `get_param`: same prologue shape (`r5=r0,r6=r1`, `*0x20000214`→`[r5,#4]`). One of the TBB's three targets | S |
| `0x080060c4` | | get_param_c (tentative) | Third sibling, same family. Internally checks a second byte against `0x40` (`[r1,#2]`) | S |

## Negative-result rows (confirms exclusion, not presence)

| Flash VA | | Name | What | P |
|---|---|---|---|---|
| (annotate existing Mode/Time Div/Type/Notes/button rows) | | | Confirmed **not** special-cased in the `0x0800ee92` GET TBB — each stays on its already-mapped mechanism (D/F/I/B tickets, `param_field_dispatch`). Negative result from this scan, not new discovery | S |
| (annotate `chord_test_dispatch`/`0x08005df8`) | | | Re-confirmed: no static `bl`, no Thumb pointer anywhere in the image. Same "orphaned" status as before, not newly resolved | S |

## Not proposed

Which specific `globalParamId` each of the three TBB families' byte
values maps to — would need `KeyStep37.json` cross-reference, not done
this ticket. Vel/Strum/Rate (`0x64`/`0x65`/`0x66`) and Seq/Arp (`0x12`)
confirmed absent from this TBB but not otherwise traced — left **H**,
no row.

STATUS: done
