# Address catalog — KeyStep 37 firmware 1.1.6.579

**Current work (2026-09-23, parked):** A–AS rows copied. AT/AU–BA scans
exist; wait for Claude proposed files before new names. Coverage: hot
path mapped; function-count guess 10–15%. Feature patches are **future**.
See [`docs/HANDOFF.md`](../../docs/HANDOFF.md).

**Use the stripped flash extract**, not the framed `.led` decode:

`firmware-re/firmware-images/keystep37_1.1.6.579_flash.bin`

File offset 0 = `0x08000000`. Application pages start at **`0x08004000`**
(vector table + Thumb). The framed 117140-byte file is a Huaxin segment
stream; loading it as flat Thumb gives **file offsets, not flash VAs**.
Old catalog numbers in parentheses are those framed-file VAs.

Provenance: P = live protocol + code match, S = structure from
disassembly / unicorn, H = hypothesis, X = ruled out.

## Boot / ownership (Ticket A, 2026-09-22)

From `scans/A-boot.txt`. `0x08014416` vs `seq_step_store` `0x08014418`
is **X** (Ticket G): `0x08014416` is `bx lr`, and the nearby store
belongs to `seq_step_store`.

| Flash VA | Framed (obsolete) | Name | What | P |
|---|---|---|---|---|
| `0x0801d310` | | Reset_Handler | `.data` copy `0x0801ef78`→`0x20000000`..`0x200001f4`; `.bss` zero `0x200001f8`..`0x20005eac`; then `bl 0x08006e20`, `bl 0x0801d8c8`, `bl 0x08016838`, `bx lr` | S |
| `0x08006e20` | | clock_rcc_init | First Reset `bl`. Literal `0x40021000` RCC | S |
| `0x20005eac` | | bss_end | End of Reset zero-fill. `0x20005f00` is `0x54` past this — not BSS-zeroed | S |
| `0x0801d8c8` | | libc_init_array | Two array sweeps; first empty; second **6** Thumb ptrs `0x0801ef58`–`0x0801ef6c`. Slot 4 is `0x080150b4`. Slots 1/6 are C++ static-init guards | S |
| `0x080150b4` | | ctor_sweep_wrapper_live | init_array slot 4. `r0=1, r1=0xffff`, `bl 0x08014d08` — only static call that passes the gate | S |
| `0x080150c2` | | ctor_sweep_wrapper_dead | Not in init_array. `r0=0` then `bl 0x08014d08`; gate requires `r0==1` so this site is a no-op. Only other static caller | S |
| `0x08005e74` | | init_array_slot2_wrapper | Same gate. `bl 0x08005da8`. Target is a small init of `0x20000218`, not a second sweep (AR) | S |
| `0x08011528` | | init_array_slot3_wrapper | Same gate. `bl 0x08010f40`. Target zeroes `0x200002b0` (AR) | S |
| `0x0801611a` | | init_array_slot5_wrapper | Same gate. `bl 0x08015f74` `shared_block_init`. Dead sibling `0x08016128` (`r0=0`) not copied as a name | S |
| `0x08015f74` | | shared_block_init | Slot 5 target. Defaults on `0x200051cc` including `+0x44=3`. Name tentative | S |
| `0x08005da8` | | | Slot 2 target. Inits `0x20000218`. Existence only | S |
| `0x08010f40` | | | Slot 3 target. 4-byte zero of `0x200002b0` | S |
| `0x08014d08` | | ctor_sweep | Gate `r0==1 && r1==0xffff`. 53 `bl`s, one hand-written init table | S |
| `0x08004768` | | analog_knob_ctor | vptr `0x0801dee4` at `+0`; `r1` → `+0x58`; zero `+0x59/+0x5a/+0x5c/+0x5e`; `+0x60=7`. Five objects: kind 0 `0x20000468`, 1 `0x2000121c`, 2 `0x20001294`, 3 `0x2000130c`, 4 `0x20001384` | S |
| `0x08004224` | | strip_b_ctor | Object `0x2000039c`. Distinct from analog kind-0 `0x20000468`. Only static `bl` to `strip_process_b` (`0x08004388`) is `0x080157d0` | S |
| `0x08013e40` | | play_time_step_obj_ctor | Ctor-sweep site 39, RAM `0x20004ed4`. **Existence S.** Role still external H | S |
| `0x0801306c` | | seq_block_ptrs_ctor | Site 37, RAM `0x20002c4c`. **Existence S.** Field roles still external H | S |
| `0x0801161c` | | arp_note_pool_ctor | Site 44, RAM `0x2000063c`. Ticket Q: ctor-sweep `bl` target, so a function start even without a push. **Existence S.** Role still external H | S |
| `0x08013c9a` | | note_pool_pair_ctor | Same ctor for `0x20002dfc` and `0x20002d0c` (sites 42, 43). Ticket Q: ctor-sweep `bl` target, leaf with no push. Pairing S. Primary/deferred labels still external H | S |

## Shift RAM (Ticket B, 2026-09-22)

From `scans/B-shift-ram.txt` (18 pc-rel sites of `0x200010d2`) +
`model/B-proposed-catalog.md`. Rejected H: `0x0801d76c` as subscribe
publish (shape only). Gesture names for Mode/TimeDiv skip-apply are
**H**; function structure is **S**. Unmapped sites 05/06/08/15/16 stay
in the model file. Ticket F: sites 05 and 06 are inside `key_scan`
(**S**). Ticket Y: `0x08016ac0` is the function; `0x08016afc` is an
internal target (fallthrough and an `r1==1` branch), not a separate
callable start. Sites 15 and 16 are the `0x200010d0`/`0x200010d6`
combo pair, not hold-length-clear.

| Flash VA | Framed (obsolete) | Name | What | P |
|---|---|---|---|---|
| `0x0801a032` | | shift_press_write | `strb #1` to `0x200010d2`. Inside `0x08019fc4`. Then `bl 0x0800dad4` (`r0=0x200013fc`, `r1=2`) | S |
| `0x0801a5a0` | | shift_release_write | `strb #0` to `0x200010d2`. Inside `0x0801a53c`. Then `bl 0x0800dad4` (`r0=0x200013fc`, `r1=1`) | S |
| `0x08019fc4` | | shift_press_fn | Containing function for sites 14–17 | S |
| `0x0801a53c` | | shift_release_fn | Containing function for site 18 | S |
| `0x0800dad4` | | notify_013fc | `(r0=0x200013fc, r1=code)`. Reused Shift press/release and site 09. Distinct from `cc_notify`. Role of `code` / sink object **H** | S |
| `0x08005a20` | | mode_skip_apply | Shift-held early `pop`. Else `mode_byte_get`, `strb` `+0x6d`, AutoTest `0x200051cc+0xb9`. Candidate §2 Shift+Mode skip-apply (**H** gesture) | S |
| `0x08005ab8` | | timediv_skip_apply | Object `0x20001000`. Field `+0x6d` is the Time Div byte (**S**, Ticket I). Gesture name for Shift+Time Div still **H**. Also uses `0x20001098` | S |

## Main loop / IRQs (Ticket C, 2026-09-23)

From `scans/C-loop-irq.txt` + `model/C-proposed-catalog.md`. Not copied:
`0x080150a4`, `0x0800fa16`, two early `button_debounce` calls, three
off-path `panel_button_dispatch` calls, `0x08005d68`, `r2=0`/`r2=1`.
`0x0800fd5c` stays unnamed.

| Flash VA | Framed (obsolete) | Name | What | P |
|---|---|---|---|---|
| `0x080150d0` | | app_main_loop | Entered once from `0x08016838`. Never returns. Inner `b` `0x08015912` → `0x080157c8`. One-shot head registers `0x20002d90` into subscriber table `0x20001120` | S |
| `0x0801d358` | | default_irq_stub | Unhandled vectors spin: `b 0x0801d358`. Not a fault reporter | S |
| `0x08018200` | | SysTick_Handler | Calls unnamed `0x08007652` (Ticket Q: real function start after `bx`; existence **S**, no role). Increments `0x20001090` and byte `0x2000528d` (cycles `0..8`). Role of that byte **H**. Ticket I: no pc-rel of `0x20002bec` in `0x08018200`–`0x08018300` | S |
| `0x08009662` | | usb_isr_common | Shared body for USB_HP (IRQ19) and USB_LP (IRQ20). Both pass object `0x20005888`. Thunk + object only | S |
| `0x08018624` | | USART1_IRQ | RXNE-style check, gated on `0x200010e0`, then `bl 0x0800fd5c` with the received byte. Callee unnamed | S |
| `0x08018584` | | TIM2_IRQ | `bl 0x0800b2ae(0x20005534)`; then `*0x20001098` through gate `0x08012330`. If not gated, increments `0x200010de` and calls `0x08011ee4(*0x20001098)`. AU: `0x08011ee4` is `ldrh [r0,#0x2a]; bx lr` (not tick). No `0x20002bec` in this IRQ. Role still **H** | S |
| `0x0800cc48` | | key_scan | Once per main-loop pass, `r0=0x20000674`. Reaches `0x0801b750` at `0x0800cdfa` and `0x0800cf30`. Name tentative. B sites 05/06 live inside this function. AT: no `cmp #2/#3`; `strb #2` to `0x200010d3` only (fourth X on hold-length-clear) | S |
| `0x08019f8c` | | small_indexed_obj_ctor | Nine objects, kinds 0–8. `strb r1,[r0,#0xd]` is the compact-ID tag. `app_main_loop` calls `button_debounce` on all nine once per pass. Ctor + reader + tag **S**. Which RAM address is which control still **H** | S |

## Analog knobs (Ticket D, 2026-09-23)

From `scans/D-analog.txt` + `model/D-proposed-catalog.md`. No immediate
`0x62`–`0x66` in either function, so no panel name. Kind targets are
inside `analog_knob_process`, not new function starts (no `recreate.py`
names). `0x2000039c` stays a different object from kind 0 `0x20000468`.

| Flash VA | Framed (obsolete) | Name | What | P |
|---|---|---|---|---|
| `0x0800498c` | | analog_kind0_strip | `cbz` when `+0x58==0`. Not a TBH slot. Loads `0x200010d2`. Panel name unknown | S |
| `0x0800527c` | | analog_kind1 | TBH `r3=0` (kind 1). `bl 0x0801b246`, then `bl 0x080048f8` with `r1=0xd`. Panel name unknown | S |
| `0x080054c6` | | analog_kind2 | TBH `r3=1`. `bl 0x0801b250`, `r1=0xf`, then `adds #2`. Panel name unknown | S |
| `0x080056cc` | | analog_kind3 | TBH `r3=2`. `bl 0x0801b278`, `r1=0x80`. Panel name unknown | S |
| `0x080058cc` | | analog_kind4 | TBH `r3=3`. No `0x0801bxxx` call. Compares raw `+0x59` with `#0x77` / `#0x88`. Panel name unknown | S |
| `0x08004930` | | analog_raw_latch | Only `strb` of `+0x5a` in the window. Copies `+0x59` when they differ, before the kind dispatch | S |
| `0x08004bf8` | | | Shift-held branch of the `+0x58==0` strip. Label inside `analog_knob_process` / `strip_process_b`, not a function start | S |

## Keys (Ticket E, 2026-09-23)

From `scans/E-keys.txt` + `model/E-proposed-catalog.md`. Four static
callers, no others. Ticket AD: `sb` is `1<<sb` before `bl 0x0801b460`
(mechanism **S**). `r2=0` / `r2=1` as physical vs MIDI stays **H**.
Call sites are not function starts (no new `recreate.py` names).
Site 04’s containing function is unnamed.

| Flash VA | Framed (obsolete) | Name | What | P |
|---|---|---|---|---|
| `0x0801b750` | | | Incoming `r2` copied to `sb` at `0x0801b75a`. First read `0x0801b8b2`: `lsls r2,#1,sb` then `bl 0x0801b460`. Bitmask mechanism **S**. Physical vs MIDI **H** | S |
| `0x0800cdfa` | | key_scan call site 01 | Inside `key_scan`. `movs r2, #0` then `bl 0x0801b750` | S |
| `0x0800cf30` | | key_scan call site 02 | Inside `key_scan`. `movs r2, #0` | S |
| `0x0800d064` | | key_scan call site 03 | Inside `key_scan`. `movs r2, #0` | S |
| `0x08010326` | | call site 04 | Previous push `0x0800fa64`, unnamed. `movs r2, #1` | S |

## Buttons (Ticket F, 2026-09-23)

Case labels sit inside `panel_button_dispatch`. Gesture names on the
shifted cases are **H**. Not copied: unshifted Hold, Stop, Play
(window incomplete); B sites 15, 16; what passes `r2==0`.
Site 08 is inside `0x08016ac0` at `0x08016afc` (internal target).

| Flash VA | Framed (obsolete) | Name | What | P |
|---|---|---|---|---|
| `0x0801780c` | | btn_rec_press | Unshifted r1=5. Stores 1 to `0x200010b6`. If `*0x20001124+0xf==1`, `bl 0x0801d7b6` and `0x0801d76c` with r1=5. Ticket AP: `0x0801d76c` is CLZ bitmask→index, not Rec LED | S |
| `0x08017856` | | btn_chord_press | Unshifted r1=8. `strb #1` to `+0xd`, then clears a second field. Gesture name **H** | S |
| `0x0801787e` | | btn_shift_hold | Shifted r1=0. Reads `+0xc`, conditional `bl 0x08017180`. Gesture **H** | S |
| `0x080178c8` | | btn_shift_rec | Shifted r1=5. Reads `+0xf`, then `0x200051cc+0x49`. Gesture **H** | S |
| `0x080178a8` | | btn_shift_stop | Shifted r1=6. `+0xf==1`, then `bl 0x08013788`. Gesture **H** | S |
| `0x08017a34` | | btn_shift_play | Shifted r1=7. Sets r1=4, `bl 0x08012334`. Gesture **H** | S |
| `0x08017a40` | | btn_shift_chord | Shifted r1=8. Reads `+0x15`, `cmp #2`, `bl 0x08006ec8`. Gesture **H** | S |
| `0x0800cd62` | | | B site 05. Inside `key_scan`. Shift, then `0x200010b6`, then `0x20001084` | S |
| `0x0800cfd8` | | | B site 06. Inside `key_scan`. `get_arp_mode()==6`, then `0x20001084`, then Shift | S |
| `0x08017cac` | | | Inside r2==0 TBH index 2, not a shifted case | S |
| `0x08017cf0` | | | Inside r2==0 TBH index 3 | S |
| `0x08016ac0` | | | Function start. B site 08 at `0x08016afc` is an internal target (fallthrough / `r1==1`), not its own callable | S |
| `0x08016982` | | | B site 07. Countdown/repeat. Not hold-length-clear (Ticket AE) | S |
| `0x0801a288` | | | B site 17. Same countdown/repeat family. Not hold-length-clear | S |
| `0x08017298` | | | Unshifted r1=6 (Stop). When `+0x12==2` publishes codes 7 and 5 (5 is Rec’s code) | S |
| `0x0801743e` | | | Unshifted r1=7 (Play). Reads `0x200051cc+0x63` then `+0x51` | S |
| `0x08017834` | | | Unshifted r1=0 (Hold). Multi-object notify via `bl 0x08014a8e`. Effect **H** | S |

## Ctors (Ticket G, 2026-09-23)

Five function starts. The other leftover ctor sites stay in
`model/G-objects.md` (existence only, not copied).

| Flash VA | Framed (obsolete) | Name | What | P |
|---|---|---|---|---|
| `0x0801d6e4` | | subscriber_obj_ctor | `str r1,[r0]; bx lr`. RAM `0x20002d90`, the object the main loop registers | S |
| `0x0800c7f0` | | key_scan_obj_ctor | Ctor of `0x20000674`, `key_scan`'s r0 | S |
| `0x08011d7c` | | tick_obj_ctor | Ctor of `0x20002bec`, passed to `arp_seq_tick` | S |
| `0x08005a08` | | mode_obj_ctor | Ctor of `0x200004f4`. Stores 8 to `+0x6d` and `+0x6e`. Name tentative | S |
| `0x08005aa4` | | timediv_obj_ctor | Ctor of `0x20001000`. Stores 8 to `+0x6d`. Name tentative | S |

## Shared block fields (Ticket H, 2026-09-23)

Example load sites. Role of each new offset is **H**. The long tail of
one- and two-site offsets was not copied.

| Flash VA | Framed (obsolete) | Name | What | P |
|---|---|---|---|---|
| `0x08012b48` | | | `0x200051cc+0x44`. 19 load sites. Boot default `3` (AR). AW: only tracked writer is that boot `#3` via `0x08015d6c`. Role still **H** | S |
| `0x08006a10` | | | `+0x34`. 16 sites. Role **H** | S |
| `0x08012d56` | | | `+0x51`. 12 sites. Role **H** | S |
| `0x0801557c` | | | `+0xbc`. 10 sites, paired with `+0x3f`. Role **H** | S |
| `0x0801b910` | | | `+0x4a`. 4 sites, paired with `+0x4f`. Role **H** | S |
| `0x08006988` | | | Function start after `bx`. Cluster `+0x54` through `+0x57` and `+0x5b`. Existence **S**. Role **H** | S |

## Voice port (Ticket J, 2026-09-23)

Ticket Z Unicorn: `emit_key` `+4` writes USART1 CR1. USB is not a
slot on this object (`0x08010e46` is a mid-fn USB send, not walked).

| Flash VA | Framed (obsolete) | Name | What | P |
|---|---|---|---|---|
| `0x0801acb0` | | port_vtable_ctor | After `bx`. Copies **eight** words `+0`–`+0x1c` into `0x20001d60` (AK; was six). BA: `+0x18` is tick `0x20002bec`; `+0x1c` is Thumb `0x08014b74` | S |
| `0x0801b02c` | | | Ctor of `0x20001e04`. Stores `0x20001d60` at `+0` | S |
| `0x0801b572` | | | Ctor of `0x20001eb8`. Stores `0x20001e04` at `+0`. Key and seq both pass this root | S |
| `0x0801b384` | | port_switch | Incoming r0 is `0x20001e04`; `[r0]` is `0x20001d60`. r3==0 or r3==2 → `0x0801ad20`. r3==1 → `0x0801ae56`. Not USB-vs-DIN (Ticket Z) | S |
| `0x0801ad20` | | port_emit_key | `+4` → `0x08014b7c` → `0x08010c10` → `0x08010b14` writes USART1 CR1 `0x4001380c \|= 0x80` (Unicorn). `+0x14` → `0x08014b6c` display, not USB | S |
| `0x0801ae56` | | port_emit_seq | `blx [obj+0xc]`. Note-On uses `+0x18`/`+0x1c` (tick `0x20002bec` / Thumb `0x08014b74`, BA). No USART/USB MMIO in the Z run | S |
| `0x08010e46` | | | Mid-function site: loads `0x20005888`, `bl 0x080091ca`. USB send entry, not a function start. AV: containing start `0x08010db0`; poller `0x08010e5c` callers `0x0800663e`/`0x08006648`/`0x08015840`. No `bl` to the mid-fn | S |
| `0x0801b6c4` | | seq_send | Forces r3=1 into `port_switch`. Six callers, all in `play_time_step`. Name tentative | S |

## GET table (Ticket K, 2026-09-23)

`0x0800ee92` is a TBB inside a function, not a new function start.
Mode, Time Div, Type, Notes, and the button IDs are not cases of it.
Vel/Strum/Rate and Seq/Arp stay **H** (not copied). `chord_test_dispatch`
still has no static caller.

| Flash VA | Framed (obsolete) | Name | What | P |
|---|---|---|---|---|
| `0x0800ee92` | | get_global_param_tbb | TBB on `([r1] as signed)−1`, only when r2==0. Three targets; the rest pop. r2!=0 is `bx lr` | S |
| `0x0800ef38` | | | Label. Short pre-check then `param_field_dispatch`. Not a SET TBB. Ticket AF: first-32 stores are stack/reply only | S |
| `0x0800614c` | | get_param_b | Same prologue shape as `get_param`. TBB bytes `0x2, 0xc, 0x21, 0x23, 0x25, 0x26`. Name tentative | S |
| `0x080060c4` | | get_param_c | Third sibling. Compares `[r1,#2]` with `0x40`. Name tentative | S |

## Recorder (Ticket L, 2026-09-23)

`0x08014416` is the ctor-sweep target for `0x200050c0` and is `bx lr`.
Not copied: TBB case 5 role, flags `0x200010d5` / `0x200010a9`. Rec LED
absent (W).

| Flash VA | Framed (obsolete) | Name | What | P |
|---|---|---|---|---|
| `0x200010b6` | | rec_armed_flag | Set at unshifted Rec `0x0801780c`, cleared at r2==0 index 5 `0x08017b1a`. Read in `key_scan` and `play_time_step` `0x08013f1c`. Name tentative | S |
| `0x080065e4` | | | Sole `bl` to `seq_step_store`. `r0=*0x200010b8`, `r1=r6` | S |
| `0x0801446a` | | | `seq_step_store` TBB case 3. 32-entry loop; writes bit 7 on match | S |
| `0x080144c2` | | | Case 6. Voice-0 pitch: empty+past-length `0x82`, empty+in-length `0x81`, else raw pitch | S |
| `0x200010d0` | | | Combo byte. Pair with `0x200010d6`. Not hold-length-clear | S |
| `0x200010d6` | | | Combo byte. Pair with `0x200010d0` | S |

## Chord / scale (Ticket M, 2026-09-23)

Which byte family is base knobs vs Chord-bank knobs stays **H**.

| Flash VA | Framed (obsolete) | Name | What | P |
|---|---|---|---|---|
| `0x20001e04` | | scale_mask_base | Mask halfword `0x20001e3a` = this base `+0x30`, then `ldrh [r0,#6]` at `0x0801c670`. Caller `0x0800d950` tests bits 0..11. Ctor `0x0801b02c` stores `0x20001d60` at `+0` | S |

## Clock (Ticket N, 2026-09-23)

Internal tempo is tick `+0xe` (AA). Ticket AB: no Sync DIP GPIO in
the `#0x13` search. AS: GPIOD object `0x20004f00` via `0x20001128`.
Jack-vs-DIP name stays **H**.

| Flash VA | Framed (obsolete) | Name | What | P |
|---|---|---|---|---|
| `0x0800ffe0` | | midi_realtime_dispatch | Compares the incoming byte with `0xFA` / `0xFC` / `0xFB` / `0xF8`. Name tentative | S |
| `0x20005534` | | tim2_wrapper | `+0`=TIM2. MIDI `0xF8`, `transport_cmd`, EXTI0, `TIM2_IRQ`. No source-select byte in the leaves. Name tentative | S |
| `0x200054bc` | | | TIM4 sibling. `TIM4_IRQ` only | S |
| `0x08012334` | | transport_cmd | `r1=1` from MIDI `0xFA`. `r1=4` from Shift+Play `0x08017a34`. Zeros TIM2 CNT. AN/AS: same fn also writes GPIOD via `0x20001128`. Name tentative | S |
| `0x20004f00` | | sync_gpio_pins | Four GPIOD fields, masks `1/8/2/4`. Pointer at `0x20001128`. Jack vs DIP **H**. Name tentative | S |
| `0x08008804` | | gpio_idr_test | `ldr [r0,#8]; tst r1`. Generic IDR bit. Name tentative | S |

## Persist (Ticket O, 2026-09-23)

No flash-slot `+0x400` load or store in `0x0800dd30`–`0x0800e400`.
Ticket AG: `0x0800ddf6` is flash→RAM copy (258 words), not commit.
`0x08008290` unlocks FLASH; stop there (HAL).

| Flash VA | Framed (obsolete) | Name | What | P |
|---|---|---|---|---|
| `0x080186d4` | | | FLASH IRQ entry. Zero static `bl`. `bl 0x08008140`, then `bl 0x0800dd8c` with `*0x20001154`. Callee uses `+0x800/+0x802/+0x804`. Object identity **H** | S |
| `0x0800de90` | | | `seq_slot_base` caller. Stores slot base at `[r4,#0x808]`, zeros `+0x802`, writes `0x203` to `+0x804`. Shape matches G site 46 | S |
| `0x0800ddf6` | | | 0x102-word copy `ldr [r2,r3,lsl #2]` → `str [r1,r3,lsl #2]`. Slot **load**, not commit | S |
| `0x08008290` | | flash_unlock | `bl` target. Writes FLASH_KEYR `0x45670123` / `0xCDEF89AB`. HAL boundary. Name tentative | S |
| `0x08008338` | | flash_busy_guard | `push`. Busy-flag + `0xc350` timeout. Name tentative | S |

## LED / DMA (Ticket P, 2026-09-23)

Key vs other LEDs not split. Rec LED absent from Rec-press and from
the 33 `led_write` callers. DMA1_CH3 `0x080186c4` reads no buffer
(not copied).

| Flash VA | Framed (obsolete) | Name | What | P |
|---|---|---|---|---|
| `0x0800d26e` | | led_write | Index r1, `cmp #0x28`. 33 callers in `0x0800d2f2`–`0x0800daac`. Name tentative | S |
| `0x0800d1f8` | | led_refresh | Compares `[r0,#0x944]` with `[r0,#0x946]`, then `bl 0x0800b6ec` with `0x200055a8`. Name tentative | S |
| `0x080185e8` | | | DMA1_CH1. Tail `0x080045b6` → `0x08004566` → `0x0800781c`. Not `led_write` / `led_refresh` | S |
| `0x08018a40` | | | DMA1_CH2. Calls `0x0800d1f4`, which is `bx lr`. Does not reach `led_refresh` | S |

## Leftover H (Ticket Q, 2026-09-23)

Mode-TBH targets and `0x08004bf8` are labels, not function starts.
`0x080150a4` still has no containing-function start.

| Flash VA | Framed (obsolete) | Name | What | P |
|---|---|---|---|---|
| `0x08013028` | | seq_block_promote_pending | After `bx`. `ldr [r0,#4]; str [r0]; bx lr` — current pointer = pending pointer. Name tentative | S |
| `0x08007652` | | | After `bx`. Called from `SysTick_Handler`. Existence only. No name | S |
| `0x08004bf8` | | | Branch target inside `analog_knob_process` / `strip_process_b`. Not a function start. `recreate.py` name removed | S |

## Round 2 (Tickets R–Y, 2026-09-23)

No letter after Y. Not copied: SET entry (none), persist commit trigger,
hold-length-clear, USB vs DIN slot, site-17 Rate (still H), TBB case 5
role, family selector.

| Flash VA | Framed (obsolete) | Name | What | P |
|---|---|---|---|---|
| `0x20002ddc` | | | G site 45. `panel_button_dispatch` object (`bl` at `0x08015934`) | S |
| `0x200023d0` | | | G site 02. Reader `0x080154d8` sits before debounce (timing **S**, role **H**) | S |
| `0x200023dc` | | | G site 03. Same reader pair as site 02 | S |
| `0x0801b5ea` | | | Reset of `0x20001eb8`. Called from `play_time_step` region `0x08013f04` | S |

## Round 3 (Tickets Z–AD, 2026-09-23)

Z catalog-copied earlier. AA/AC/AH/AD this pass. Rejected: `usb_send_entry`
as a function start (`0x08010e46` mid-fn). Kind 1–4 closed by AM.
Physical vs MIDI **H**. Swing flash table copied from AO.

| Flash VA | Framed (obsolete) | Name | What | P |
|---|---|---|---|---|
| `0x0801509a` | | ring_consume | Sole caller of `0x08010638`. Ticket AL: 0 `bl` / 0 Thumb ptr to this start. Name tentative | S |
| `0x0801ec64` | | swing_value_table | 9 bytes `32 34 36 39 3c 3f 43 47 4b`. Occupancy Swing set. Reader `0x08016f80` uses `r1-0x15` when `0x15≤r1≤0x1d` | P |
| `0x200010ec` | | | G site 08 published here (AQ). Role **H** | S |
| `0x2000111c` | | | G site 09 published here (AQ). Role **H** | S |
| `0x200010f8` | | | G site 10 published here (AQ). Role **H** | S |
| `0x2000107c` | | | G site 11 published here (AQ). Role **H** | S |

## Protocol / control

| Flash VA | Framed (obsolete) | Name | What | P |
|---|---|---|---|---|
| `0x08005e84` | `0x08001f68` | get_param | GET `globalParamId` | P |
| `0x08005df8` | `0x08001edc` | chord_test_dispatch | Control `0x69` (CC 105) ON/OFF | P |
| `0x08005ccc` | | mode_byte_get | `ldrb [r0,#0x55]` — generic `+0x55` getter. Callers include `set_arp_mode` path and Shift-skip applies at `0x08005a20` / `0x08005ab8` (different `r0` bases). Not Mode-only despite the name | S |
| `0x08006024` | | id_to_index | `0x55`→0 Hold, `0x56`→1 Shift, `0x10`→2 Oct−, `0x11`→3 Oct+, `0x67`→4 Tap, `0x57`→5 Rec, `0x59`→6 Stop, `0x5a`→7 Play, else 8. Occupancy CCs **are** these IDs | P |
| `0x0800606c` | | index_to_id | Inverse of `id_to_index`, plus index 8 → `0x69` Chord. Chord is not in the forward table. Debounce uses this before Test-20 emit | P |
| `0x080060a2` | | knob_index_to_cc | Knob compact → CC `0x62`–`0x66`. One static caller `0x08004978` (AutoTest). TBB `0a040608` (AM): kind1→`0x62` Type, 2→`0x63` Notes, 3→`0x64` Vel, 4→`0x65` Strum; kind 0/`≥5`→`0x66` Rate | P |
| `0x080067f4` | | test20_cc_press | Builds `B0 <id> 01`. Called from debounce `0x0801a7f6` after `index_to_id` | P |
| `0x080068c8` | | test20_cc_value | Builds `B0 <id> <val>`. Analog Test-20 path `0x08004974` | P |
| `0x08006914` | | test20_cc_value2 | Same `B0` shape; Shift+Mode emits id `0x15`, Shift+TimeDiv id `0x68` when AutoTest `+0xb9` | P |
| `0x08016bc4` | `0x08013482` | cc_notify | Catalog name; real `push` is `0x08016bd4`. Test-20 occupancy CCs come from `0x080067f4` / `0x080068c8` | S |
| `0x0801cc5c` | `0x08019808` | subscribe | 3-slot × 20-byte callback table at `0x20001120` | S |

## Arp / mode (Pattern)

There are **not** eight mode vtables at `object+0x214`. That slot holds
one event-handler table (`.data` at RAM `0x20000004`, flash
`0x0801ef7c`). Slot `+8` is `0x0800e3e8` (event dispatcher).

Pattern is **arp-engine `+0x10` == 6** (panel CC21 = 7; CC21 = internal + 1).

| Flash VA | Framed (obsolete) | Name | What | P |
|---|---|---|---|---|
| `0x08011794` | | set_arp_mode | `if (*obj+0x10 != r1) { *+0x10 = r1; notify }` | S |
| `0x08011a1c` | | rebuild_order | 8-way **TBH** on `ldrb [obj,#0x10]`; `cmp #7` | S |
| `0x08011a38` | | mode_tbh | Manual / panel / CC21 (1-based): Up Down Incl Excl Random **Walk=6 Pattern=7 Order=8**. Internal `+0x10` is CC21−1. Case 5 = Walk (hold-order list + play-time walk helper); case 6 = Pattern (semi-random); case 7 = Order (same list builder as 5, no walk dice) | S |
| `0x08011c88` | | | TBH cases **5 and 7** (Walk and Order share the hold-order list build). Pattern is case 6. Case-body label inside `rebuild_order`, not a function start. `recreate.py` name removed | S |
| `0x08016a26` | | mode_knob_apply | `mode_byte_get` then `set_arp_mode`. Settings ptr `*0x20001170`, engine `*0x20001094` | S |
| `0x08017f20` | | set_mode_alt | Second `bl` to `set_arp_mode` | S |
| `0x0800e4d2` | `0x0800a9b2` | vtable_init | Clears `+0x214`, stores `+0x210` callback | S |
| `0x0800e4fe` | `0x0800a9de` | vtable_assign | `str.w r1,[r0,#0x214]`. Only static `bl` is ctor `0x08018b0a` (installs RAM vtable `0x20000004`) | S |
| `0x0800e3e8` | | vtable_slot8 | Event dispatcher, not a note-index generator | S |
| `0x0800ea7e` | `0x0800af7c` | msg_tbb | 10-way message TBB. **Not arp modes** | X/S |
| `0x0800dd30` | `0x0800a1d4` | seq_slot_base | `0x0803B000 + n*0x800` | S |
| `0x080129cc` | | arp_seq_tick | Object `0x20002bec` (ctor `0x08011d7c`). `+0x38` step, `+0x10` length, `+0xe` tempo halfword (Ticket AA), `+0x55` signed byte. Then `bl 0x08013e8c` at `0x08012ec0`. Swing **table** is `0x0801ec64` (AO). AX: `0x0801312e` `strb` to `+0x401` via `*0x20001150` | S |
| `0x08012048` | | tempo_clamp | Clamps r1 to 3000–24000, `strh [r0,#0xe]`, then TIM2 ARR via `0x08012084`. Tick object `0x20002bec`. Name tentative | S |
| `0x08013e8c` | | play_time_step | **Pattern player.** Reads the current slot step and emits. Callers: tick `0x08012ec0` (Arp, once per step change), dispatch `0x08012028` via `0x08011ff0` (gated on `*(0x20001124)+0x10==2`). AZ: sole static `bl` to `0x08011ff0` is EXTI0 `0x080183c6`. When `engine+0xf==0` and `+0x10==5` (Walk) remaps the step through `0x08011878`; **mode 6 (Pattern) and mode 7 (Order) keep the sequencer step** | S |
| `0x080130e8` | | seq_step_note | `*(uint8*)(*obj + (voice + step*8)*2)` — 16-byte stride, 8 voices × 2 bytes. Voice 0 is the Pattern pitch byte | S |
| `0x080130f4` | | seq_step_gate | Byte +1 of the same cell. `0x82` at step 0 is the empty-slot magic from `0x080137c4`. Callers (all inside `play_time_step`): `0x08013f62`, `0x08013fde`, `0x080141d2` — E0+ retarget these to `euclid_wrap` | S |
| `0x08011874` | | get_arp_mode | `ldrb r0,[r0,#0x10]` | S |
| `0x08011878` | | order_hold_walk | Order-only index into the rebuilt hold list | S |
| `0x08014418` | `0x08010bc8` | seq_step_store | **Recorder**, not the player. Sole caller `0x080065e4` (`r0=*0x200010b8`, `r1=r6`). TBB writes `+0x400` / `+0x401` / `+0x402` (Length / Swing / Gate, **S**) | S |
| `0x0801415c` | | seq_step_release | Release/tie handling. Static callers: `0x08011f40`, `0x0801200a`, `0x08012fcc`. None of those is inside `play_time_step`. Tie-scan behavior itself not reopened | S |
| `0x08013ebc`–`0x08013ecc` | | pitch_gate_check | Inside `play_time_step`. Reads voice 0's pitch via `seq_step_note`, computes `(pitch+0x7f)&0xff`, early-returns (no note attempted) if `<=1` — true exactly for `pitch==0x81`/`0x82`. **The actual note-emission gate.** Confirmed by direct disassembly, 2026-09-22. Candidate hook point for a rhythmic/Euclidean patch, in place of `seq_step_gate`. | S |

### Correction (external source, 2026-09-22): bit 7 is retention, not a gate

**Revises the `seq_step_gate` entry above.** An independently-developed
external repo studying the same firmware (same version, 1.1.6.579)
describes the byte at `step*16 + voice*2 + 1` more precisely: bits 0-6
are velocity; **bit 7, voice 0 only, "participates in retention"** (i.e.
tie/hold-over-from-previous-step), not a direct "should this step
produce a Note-On" flag. This directly explains the E0 hear-test
failures logged in `findings-2026-09-20.md` and `docs/HANDOFF.md`:
clearing bit 7 on a Euclidean "miss" (what `euclid_wrap` does) most
likely changes whether the step is treated as a tied continuation versus
a fresh articulation, not whether a note sounds at all — consistent with
every hear-test showing a Note-On on every step regardless.

**Update, 2026-09-22: independently confirmed**, not just an external
claim anymore. Disassembled `play_time_step` and `seq_step_release`
directly. The real "does this step attempt a note" gate is voice 0's
**pitch byte** checked at `0x08013ebc`-`0x08013ecc`
(`(pitch+0x7f)&0xff <= 1`, true exactly for `pitch==0x81` or `0x82`,
verified by hand) — an early function return, nothing to do with
`seq_step_gate` at all. `seq_step_gate`'s bit 7 is consumed by
`seq_step_release` (tie-scan fallback) and by a local flag inside
`play_time_step` that gates writing a cached previous output pitch into
a retention-tracking array — real, but unrelated to note emission. See
`findings-2026-09-20.md`'s "Root cause ... confirmed" entry for the full
trace. Treat the old "gate / `0x80` flags" wording above as superseded.

### Header fields (external source, 2026-09-22, unverified by us)

| Block offset | Meaning |
|---|---|
| `0x400` | Length, max 64 |
| `0x401` | Swing (slot-global) |
| `0x402` | Gate (slot-global) — distinct from the per-step byte above |
| `0x403` | Partially-understood flags; preserve unknown bits |
| `0x404` | Retention-source selector, read by `seq_step_release` (`0x0801415c`) |
| `0x405–0x407` | Unknown |

### Pitch/marker sentinels (external source, 2026-09-22, unverified by us)

Sharper than the earlier "`0x82` = empty-slot magic" phrasing:

- `0xFF` — terminates a voice
- `0x81` — retains the preceding note (tie start)
- `0x82` — starts no new note, but is **not** an unconditional Note-Off
  (a held/tied note can still be sounding)

Mode TBH targets (1.1.6.579). Ticket Q: all seven are case-body labels
inside `rebuild_order`, not function starts.

| Value | Name | Builder |
|---|---|---|
| 0 | Up | `0x08011a9e` |
| 1 | Down | `0x08011ae0` |
| 2 | Incl | `0x08011b2c` |
| 3 | Excl | `0x08011bb6` |
| 4 | Random | `0x08011c46` |
| 5 | **Walk** (panel CC21=6). Builder is the hold-order list; play-time uses `0x08011878` | `0x08011c88` |
| 6 | **Pattern** (panel CC21=7). Semi-random builder | `0x08011cca` |
| 7 | **Order** (panel CC21=8). Same list builder as Walk, no walk dice | `0x08011c88` (same as 5) |

**Resolved, 2026-09-22, by our own disassembly** (not just the external
source): `0x08011cca` is a 2-instruction trampoline into `0x0801196c`,
which calls a scale-quantizing pitch generator (`0x08013de8`) in a loop
to build bounded semi-random pitches — this is the manual's §5.3.8
"Pattern" behavior (semi-random, "optional octave movement"), not Walk's
simple 50/25/25 next/repeat/previous dice. Internal mode 7 shares its
builder with mode 5 (Order) — no randomization at all. **The `names`
table in `emulate_ks37.py` and this catalog had Walk and Pattern swapped
at the internal-mode-index level** — corrected above. This was flagged
as an open discrepancy days before 2026-09-22's hardware testing and
wasn't resolved before that testing started. **CC21-to-internal mapping
is now confirmed (2026-09-22, from the flash extract, not from a GET):**
the CC-transmit path at `0x08005a72` does `adds r1, r0, #1` then
`movs r0, #0x15` (`bl 0x08006914`) — outbound CC21 = `settings+0x55` + 1,
except when `+0x55==8` (no CC). `mode_byte_get` is a raw
`ldrb [r0,#0x55]`; `set_arp_mode` stores that byte raw to `engine+0x10`.
Panel **Walk=6 / Pattern=7 / Order=8** (CC21, manual §5.3 / encoder
legend: Up Down Incl Excl Random Walk Pattern Order) are correct.
Internal is CC21−1, so those are TBH cases 5 / 6 / 7. Walk and Order
share the hold-order list builder; Walk adds the play-time helper
`0x08011878`. Pattern (internal 6) is the semi-random builder.

### How a Pattern step becomes a hold index

`play_time_step` does **not** store indices. Each step is 16 bytes
(`8 × uint16`): voice 0's first byte is a MIDI note. Unicorn
(`emulate_ks37.py play`) planted the live pitch string

`34 48 34 48 3C 34 3C 48 3C 3C 48 52 3C 3C 3C 48`

at a synthetic slot and ran `seq_step_note`; mapping those pitches onto
hold `{0x34, 0x3C, 0x48, 0x52}` reproduces

`(0, 2, 0, 2, 1, 0, 1, 2, 1, 1, 2, 3, 1, 1, 1, 2)`.

On-device bytes live at `0x0803B000+n*0x800` (not in the `.led`). A live
dump would need an existing SysEx/GET or watching MIDI — not SWD.
`+0x400` in a slot is length; `+0x403` is flags.

## Chord / note output

| Flash VA | Framed (obsolete) | Name | What | P |
|---|---|---|---|---|
| `0x0801ba9c` | `0x080185b2` | voice_interval_load | Label inside `0x0801b750`, not a function `play_time_step` calls. Loads `0x200051cc+0x4f` and `0x200000c8`, then `bl noteval` | S |
| `0x0801c3ca` | (`0x08018ee0` was a mid-fn entry) | noteval | `note + interval - transpose`, octave-wrap 0–127 | S |
| `0x0801bab8` | `0x080185ce` | voice_note_on | Label inside `0x0801b750`. If `0x200051cc+0x4d` nonzero, builds `0x90\|ch` with vel `+0x4e` | S |
| `0x0800f054` | | param_field_dispatch | TBH on `[r0,#0x3c]−1`. Bytes `0x08`–`0x0e` and `0x16`–`0x1b` write `+0x4d/+0x4e/+0x4f`. Disable path also zeros `+0x50` (role **H**). Ticket AJ: no tracked path from a `0x200051cc` load to `+0x50` | S |
| `0x200051cc` | | voice_obj | 197 pc-rel loads, about 40 offsets. Not one subsystem. Kept name: the scan did not supply a replacement. `+0x4d/+0x4e/+0x4f` voice; `+0x50` not reached from this object’s pc-rel loads (Ticket AJ); `+0xb9` AutoTest; `+0x59`; `+0x49`; `+0x5c` bit 0 | S |
| `0x200000c8` | | transpose_ram | Subtracted operand of `noteval` | S |

The voice loop is **generic poly** (`cbz` on `+0x4d`), not chord-only.
Chord ON still sets `+0x4d`; that is a usable seam.

Literal pool at `0x0801bd38` (was framed `0x0801886c`):

- `0x20001150`
- `0x200000C8` ← loaded by the interval snippet (transpose)
- `0x200010D4`
- `0x2000112C`
- `0x20001180`

## RAM

| VA | What |
|---|---|
| `0x20000000`–`0x200001f4` | `.data` (flash load `0x0801ef78`) |
| `0x200001f8`–`0x20005eac` | `.bss` (Reset_Handler zero-fill) |
| `0x20000004` | Event-handler vtable installed at `object+0x214` |
| `0x20001094` | Pointer to arp engine (mode byte at engine `+0x10`) |
| `0x20001120` | CC subscriber table |
| `0x20001170` | Pointer. The one store writes `0x200004f4` (Mode object). **S** (Ticket O) |
| `0x20000468` | analog kind 0 (strip path of `analog_knob_process`) |
| `0x2000121c` | analog kind 1 |
| `0x20001294` | analog kind 2 |
| `0x2000130c` | analog kind 3 |
| `0x20001384` | analog kind 4 |
| `0x2000039c` | strip_b object (`strip_process_b`) |
| `0x200051cc` | Shared state (`voice_obj` name is narrow): `+0x4d/+0x4e/+0x4f`, AutoTest `+0xb9`, `+0x59`, `+0x49`, `+0x5c` bit 0 |
| `0x20005624` | Ctor object for `vtable_init` / `vtable_assign` |
| `0x20001e04` | Scale-mask object. Halfword at `+0x36` is `0x20001e3a`. **S** (Ticket M) |
| `0x20001e3a` | Scale pitch-class mask (`ldrh` via `0x0801c670`). Chromatic = `0x0FFF` |
| `0x20005f00` | Patch latch: Euclidean armed (E3+; default 0). **Not in `.bss`** (`bss_end` `0x20005eac` + `0x54`) |
| `0x20005f01` | Patch flavour: Shift+Type value (C2) |
| `0x20005f02` | `STEP_CTR_RAM` — e0b's own free-running Euclidean step counter, decoupled from the native step-position field (see below); advances only on a real (non-tie/rest) `pitch_gate_wrap` call |

## Patch page (`0x0801F400`)

| VA | Name | What |
|---|---|---|
| `0x0801F400` | euclid_wrap | Same args as `seq_step_gate` (`r0` obj, `r1` step, `r2` voice). Calls stock gate, then clears bit 7 on a Euclidean miss |
| | euclid_gate | `(step % n) * k % n < k` → 0\|1 |
| | shift_note_hook | Replaces `mov sb,r2; mov r4,r3` at `0x0801b75a`. Shift+MIDI 36/37 sets/clears `0x20005F00`. **Collision:** those keys are stock Keyboard MIDI CH (manual 1.1 §3.6.1). See `stock-shift-map.md`. |
| | noteval_then_snap | After `noteval`; snaps if Chord ON and mask ≠ chromatic |
| | type_strb_hook | Replaces `strb.w r1,[r0,#0x4f]` at Type stores `0x0800f4b8` / `0x0800f54e` / `0x0800f6fc` |

## Note-pool builder and sequence double-buffering (external source, 2026-09-22)

**Existence of these RAM objects + their ctors is now S** (ctor sweep
A, sites 37/39/42–44). Semantic roles below remain **H** (external,
unverified). Ctor VAs: `arp_note_pool_ctor` `0x0801161c`,
`seq_block_ptrs_ctor` `0x0801306c`, `play_time_step_obj_ctor`
`0x08013e40`, `note_pool_pair_ctor` `0x08013c9a` (builds both pools).

| VA | Name | What |
|---|---|---|
| `0x2000063c` | arp_note_pool_builder | Builds voice-0 data for the mode TBH above. Uses `0x20002dfc` (primary pool, up to 32 unique pitches + velocity, insertion order and ascending-pitch order tracked separately) and `0x20002d0c` (deferred-release pool — held notes pending release, not a physical-key ledger). Duplicate pitch does not update velocity. |
| `0x20002c4c` | seq_block_ptrs | `+0` current-block pointer, `+4` pending-block pointer. Sequence data is double-buffered, not a single live block. |
| `0x20004ed4` | play_time_step_obj | RAM object `play_time_step` (`0x08013e8c`) consumes a step through; retains actual output pitches for release. |

**Three competing update paths** (their phrasing, useful framing even
before we re-derive it ourselves): `0x08012b62 → 0x08011a1c` rebuilds
voice 0 in the *current* block in place; `0x08012bd6 → 0x08013028`
replaces the current pointer with the pending pointer (**S**, Ticket Q:
`ldr [r0,#4]; str [r0]`); `0x0801415c`
(`seq_step_release` above) reads current-block retention metadata and
releases saved output pitches. Swing is read before rebuild/pointer
publication; length and gate are read later — a pointer swap alone can
expose mixed timing metadata mid-transition. Relevant to any future patch
that touches sequence timing, not just Pattern specifically.

## Input path (external source, 2026-09-22, unverified by us — we never mapped this)

| VA | What |
|---|---|
| `0x08010638` | USB packet decode, writes a byte ring. Ticket AH: sole `bl` is inside `0x0801509a`. Not `usb_isr_common`. Who calls `0x0801509a` not found |
| `0x0800fa64` | Main-loop MIDI parser. Two `bl`s from `app_main_loop` `0x080150d0` are **S**. “≤50 bytes per invocation” still unverified |
| `0x08018624` → `0x0800fd5c` | USART1 IRQ calls unnamed `0x0800fd5c` with the received byte, gated on `0x200010e0`. **S** (Ticket C) |
| `0x08010310` | Parsed MIDI path still distinguishes USB/DIN before channel filtering |
| `0x0801b750` | Note entry. Ticket E: four callers. `key_scan` sites pass `r2=0`; `0x08010326` passes `r2=1`. Ticket AD: `sb` is a shift for a one-hot mask, not a boolean. Physical vs MIDI stays **H** |
| `0x20001ebc` | Cross-port/channel pitch tracker. Releasing a pitch from one "owner" (port/channel) can clear its slot while another owner still holds the same pitch. |
| `0x08004918` | Analog/knob process. Store new raw at `+0x5a` (`0x08004930`). AutoTest `0x200051cc+0xb9` → emit CC via `0x080060a2`+`0x080068c8`. `+0x58==0` = strip path; kinds 1–4 TBH. Five objects from `analog_knob_ctor` |
| `0x08004930` | Raw `+0x5a` store inside `analog_knob_process`. Ticket D names it `analog_raw_latch` (**S**). Other-repo `ks37_control_hook` patches this STRB |
| `0x08004bf8` | Shift-held branch of the `+0x58==0` strip: pickup/scale math. Label, not a function start (Ticket Q) |
| `0x08004388` | Strip processor for `0x2000039c`. Ticket D: `bne` at `0x080043c4` when `*0x200010d2 != 0` lands at `0x08004428`, which stores `4` to `0x200010dc`. Redirect **S**. A MIDI-emit skip is not in that window |
| `0x0801a7ac` | Button debounce wrapper. Stable → `index_to_id` then `test20_cc_press` |
| `0x08017260` | Panel button dispatch. Object `0x20002ddc` (Ticket S). Reads Shift RAM; unshifted TBH `0x08017282`, shifted TBH `0x08017868` (hold/rec/stop/play/chord). Shift/oct/tap in this table are the common exit |
| `0x200010d2` | Shift-held byte. 18 pc-rel sites (`scans/B-shift-ram.txt`). Writes: `0x0801a032` set 1, `0x0801a5a0` set 0 |
| `0x0800d26e` / `0x0800d1f8` | `led_write` / `led_refresh` (**S**, Ticket P). Index `cmp #0x28`. DMA1_CH2 does not call the refresh. Frame atomicity still not claimed |

## Step-counter object fields, confirmed by our own disassembly — 2026-09-22

Traced directly (not from the external repo) to explain why the `e0b`
pitch-gate hook (`docs/HANDOFF.md`, findings log) produced different
rhythms on real hardware depending on which sequence slot was active.
Independently corroborates and refines the external repo's
`seq_block_ptrs`/`play_time_step_obj` framing above with exact field
offsets on the block `play_time_step` (`0x08013e8c`) operates on (the
pointer at block `+0x50`, i.e. the *content* of whichever slot
`seq_block_ptrs` currently designates current/pending):

| VA / offset | What |
|---|---|
| block `+0x38` | Live step-position counter. Both callers of `play_time_step` write this field before calling it. |
| block `+0x10` | Length field. Checked as `if step >= length-1: wrap` at the one caller (`0x08011ff0`) that increments `+0x38`. |
| `0x08013e94` | `play_time_step` spills its own incoming `r1` (the step arg) to the stack immediately — it does not compute step itself, a caller does. |
| `0x08011ff0`–`0x08012028` | Caller taking a mode flag in `r1`. `r1==0`: advances `+0x38` (wrap-checked against `+0x10`), calls `seq_step_release`, does **not** call `play_time_step`. `r1!=0`: reloads `+0x38` unincremented (clamped ≥0), calls `play_time_step` with it. |
| `0x08012e56`–`0x08012ec0` | Second caller; computes a new step value via separate logic (compared against the previous value and a signed byte at block `+0x55`, suggesting a possible fixed/held-step override), stores it to `+0x38`, calls `play_time_step`. |

**Conclusion**: the `step` value our `pitch_gate_wrap` hook feeds into
`euclid_gate(step, 8, 3)` is the native engine's real, persistent
step-position state for whichever sequence block is currently active —
bounded by that block's own length field — not an independent 0–7
counter under our control. This directly explains the hardware
hear-test results being slot-dependent (see findings log, "Root cause of
the slot-dependence, confirmed by direct disassembly"). Fix proposed
there: maintain our own free-running counter in patch RAM instead of
reusing this native value.

## USB / off-limits (flash VAs)

Search the extract for the same byte sequences if a framed number is
cited in older notes. Do not patch USB (`0x40005C00` literals), SysEx
GET, or Huaxin footers.

## Still useful, not blocking

- Which ADC/encoder path writes settings `+0x55` (the 8 detents). Closed
  from the other direction: CC21 outbound is `+0x55 + 1` at `0x08005a72`.
  `set_arp_mode` is enough of a hook without that store.
- Independently re-verify (disassembly or emulation, our own tooling)
  the highest-value external claims above before designing any new
  patch on top of them: the bit-7-is-retention correction, the
  `0x0801415c` release/look-ahead behavior, and the mode-6 discrepancy.
  Everything in this catalog marked `H (external)` or "unverified by us"
  is a claim from a separate research effort, not yet re-derived here —
  same evidentiary bar this project has always used for any relayed
  claim.
