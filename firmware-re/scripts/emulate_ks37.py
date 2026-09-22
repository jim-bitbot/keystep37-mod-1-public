#!/usr/bin/env python3
"""Bounded unicorn / static checks for KeyStep 37 1.1.6.579 (flash extract).

Load the stripped image (`*_flash.bin`, base 0x08000000). Do not use the
framed 117140-byte decode as a flat Thumb image.

Usage:
    python3 emulate_ks37.py interval
    python3 emulate_ks37.py pattern
    python3 emulate_ks37.py play
    python3 emulate_ks37.py euclid
    python3 emulate_ks37.py all
"""
from __future__ import annotations

import argparse
import pathlib
import struct
import sys

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
from unicorn.arm_const import (
    UC_ARM_REG_LR,
    UC_ARM_REG_R0,
    UC_ARM_REG_R1,
    UC_ARM_REG_R2,
    UC_ARM_REG_R3,
    UC_ARM_REG_R4,
    UC_ARM_REG_R7,
    UC_ARM_REG_SP,
)

ROOT = pathlib.Path(__file__).resolve().parents[2]
FLASH_PATH = ROOT / "firmware-re" / "firmware-images" / "keystep37_1.1.6.579_flash.bin"
BASE = 0x08000000

# Live Pattern 16-step index cycle on hold {0x34, 0x3C, 0x48, 0x52}.
# Sequence-data-dependent; the mode-7 *builder* does not produce this.
# The pitches below are the same capture, as MIDI notes. The player stores
# those bytes in the slot (16-byte stride); the index cycle is hold-pool
# position, not a second encoding.
HOLD_POOL = (0x34, 0x3C, 0x48, 0x52)
PATTERN_PITCHES = (
    0x34, 0x48, 0x34, 0x48, 0x3C, 0x34, 0x3C, 0x48,
    0x3C, 0x3C, 0x48, 0x52, 0x3C, 0x3C, 0x3C, 0x48,
)
PATTERN_CYCLE = (0, 2, 0, 2, 1, 0, 1, 2, 1, 1, 2, 3, 1, 1, 1, 2)

MODE_TBH = 0x08011A38
MODE_SETTER = 0x08011794
PLAY_TIME_STEP = 0x08013E8C
SEQ_STEP_NOTE = 0x080130E8
GET_ARP_MODE = 0x08011874
ORDER_HOLD_WALK = 0x08011878
ARP_SEQ_TICK = 0x080129CC
INTERVAL_LDR = 0x0801BAA4
NOTEVAL = 0x0801C3CA
VOICE_OBJ = 0x200051CC
TRANSPOSE_RAM = 0x200000C8
STEP_STRIDE = 16
VOICES_PER_STEP = 8


def load_flash() -> bytes:
    if not FLASH_PATH.exists():
        raise SystemExit(
            f"missing {FLASH_PATH} — run led_codec.py extract-flash first"
        )
    return FLASH_PATH.read_bytes()


def word(flash: bytes, va: int) -> int:
    return struct.unpack_from("<I", flash, va - BASE)[0]


def cmd_pattern(flash: bytes) -> int:
    """Decode the 8-way mode TBH. Case 6 is Pattern's semi-random builder
    (0x08011cca -> 0x0801196c -> scale-quantizing pitch generator
    0x08013de8, confirmed 2026-09-22); case 7 shares code with Order (5),
    no randomization. Was previously mislabeled 6=Walk/7=Pattern."""
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    print("=== arp mode TBH @ 0x08011a38 (object+0x10, values 0..7) ===")
    names = ["Up", "Down", "Incl", "Excl", "Random", "Order", "Pattern", "Order-twin?"]
    table = MODE_TBH + 4
    cases = []
    for i in range(8):
        off = struct.unpack_from("<H", flash, table - BASE + i * 2)[0]
        target = table + off * 2
        cases.append(target)
        print(f"  {i} {names[i]:8} -> {target:#010x}")
    print(f"  case 5 and 7 share code: {cases[5] == cases[7]}")
    print(f"  set_arp_mode            {MODE_SETTER:#010x}  (strb r1,[r0,#0x10])")
    print("  +0x214 is a single event-handler vtable (slot +8 = 0x0800e3e8),")
    print("  not eight mode vtables. Semi-random Pattern is TBH case 6, not")
    print("  case 7 (corrected 2026-09-22). CC21 = internal+1: panel")
    print("  Pattern CC21=7 is this case 6; Walk CC21=6 is case 5.")
    print(f"  live 16-step cycle {PATTERN_CYCLE} is sequencer-data-dependent")
    print("  and is not produced by the case-7 (Order-twin) note-list builder.")
    print(f"  play-time reader        {PLAY_TIME_STEP:#010x}  (tick {ARP_SEQ_TICK:#010x})")
    # sanity: TBH insn is present
    insn = next(md.disasm(flash[MODE_TBH - BASE : MODE_TBH - BASE + 4], MODE_TBH))
    ok = insn.mnemonic == "tbh" and cases[7] == 0x08011C88
    print(f"  check                  {'OK' if ok else 'FAIL'}")
    return 0 if ok else 1


def _bl_targets(flash: bytes, va: int, nbytes: int) -> set[int]:
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    out: set[int] = set()
    for insn in md.disasm(flash[va - BASE : va - BASE + nbytes], va):
        if insn.mnemonic != "bl":
            continue
        try:
            out.add(int(insn.op_str.replace("#", ""), 16))
        except ValueError:
            continue
    return out


def cmd_play(flash: bytes) -> int:
    """Name the Pattern play-time reader and unicorn a synthetic 16-step slot."""
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    print("=== play-time step 0x08013e8c (Pattern reads the current slot) ===")
    insn = next(md.disasm(flash[PLAY_TIME_STEP - BASE : PLAY_TIME_STEP - BASE + 4], PLAY_TIME_STEP))
    print(f"  entry                   {PLAY_TIME_STEP:#010x}  {insn.mnemonic} {insn.op_str}")
    print(f"  clock tick              {ARP_SEQ_TICK:#010x}  bl @ 0x08012ec0")
    print(f"  seq_step_note           {SEQ_STEP_NOTE:#010x}  slot[(step*8+voice)*2]")
    print(f"  stride                  {STEP_STRIDE} bytes ({VOICES_PER_STEP} voices x 2)")
    print(f"  get_arp_mode            {GET_ARP_MODE:#010x}  ldrb [engine,#0x10]")
    print("  Order overlay           0x08013f46  cmp #5 then bl 0x08011878")
    print("  Mode 7 (Order-twin, panel CC21=8) keeps the")
    print("  tick's sequencer step; it does not take the Order remap. Mode 6")
    print("  is the real semi-random Pattern generator (0x08011cca), a")
    print("  different code path not exercised by this reader directly.")
    print("  0x08014418 is the recorder, not this path.")

    targets = _bl_targets(flash, PLAY_TIME_STEP, 0x2D0)
    static_ok = (
        insn.mnemonic == "push.w"
        and SEQ_STEP_NOTE in targets
        and GET_ARP_MODE in targets
        and ORDER_HOLD_WALK in targets
    )

    # 0x080130e8: ldr r3,[r0]; note = *(uint8*)(*r0 + (voice + step*8)*2)
    slot = 0x20006000
    obj = 0x20005000
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    size = (len(flash) + 0xFFF) & ~0xFFF
    mu.mem_map(BASE, size)
    mu.mem_write(BASE, flash)
    mu.mem_map(0x20000000, 0x10000)
    mu.mem_map(0x20010000, 0x2000)
    mu.reg_write(UC_ARM_REG_SP, 0x20011F00)
    mu.mem_write(obj, struct.pack("<I", slot))
    planted = bytearray(64 * STEP_STRIDE)
    for step, pitch in enumerate(PATTERN_PITCHES):
        planted[step * STEP_STRIDE] = pitch
    mu.mem_write(slot, bytes(planted))

    notes: list[int] = []
    for step in range(len(PATTERN_PITCHES)):
        mu.reg_write(UC_ARM_REG_R0, obj)
        mu.reg_write(UC_ARM_REG_R1, step)
        mu.reg_write(UC_ARM_REG_R2, 0)
        mu.emu_start(SEQ_STEP_NOTE | 1, 0x080130F2)  # stop before bx lr
        notes.append(mu.reg_read(UC_ARM_REG_R0) & 0xFF)

    hold = {pitch: i for i, pitch in enumerate(HOLD_POOL)}
    cycle = tuple(hold[n] for n in notes)
    print(f"  planted pitches         {tuple(f'{n:02X}' for n in notes)}")
    print(f"  hold {tuple(f'{n:02X}' for n in HOLD_POOL)} -> {cycle}")
    print(f"  live cycle              {PATTERN_CYCLE}")
    emu_ok = notes == list(PATTERN_PITCHES) and cycle == PATTERN_CYCLE
    print(f"  static                  {'OK' if static_ok else 'FAIL'}")
    print(f"  unicorn slot            {'OK' if emu_ok else 'FAIL'}")
    print("  floor: on-device slot bytes are at 0x0803B000 (not in the .led);")
    print("  this run uses the captured pitch string as a synthetic slot.")
    return 0 if static_ok and emu_ok else 1


def cmd_interval(flash: bytes) -> int:
    """Unicorn 0x0801ba9c through the bl to noteval; record r3/r1/r2/r0."""
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    size = (len(flash) + 0xFFF) & ~0xFFF
    mu.mem_map(BASE, size)
    mu.mem_write(BASE, flash)
    mu.mem_map(0x20000000, 0x10000)
    mu.mem_map(0x20010000, 0x2000)
    mu.reg_write(UC_ARM_REG_SP, 0x20011F00)
    mu.mem_write(TRANSPOSE_RAM, struct.pack("<b", 5))  # global transpose
    mu.mem_write(VOICE_OBJ + 0x4F, struct.pack("<b", 7))  # per-voice interval
    mu.mem_write(VOICE_OBJ + 0x4D, bytes([0x10]))
    mu.mem_write(VOICE_OBJ + 0x4E, bytes([0x64]))
    mu.reg_write(UC_ARM_REG_R7, 0x3C)

    got: dict[str, int] = {}

    def hook(uc, addr, _size, _):
        if addr == 0x0801BAAC:
            got["r0"] = uc.reg_read(UC_ARM_REG_R0)
            got["r1"] = uc.reg_read(UC_ARM_REG_R1)
            got["r2"] = uc.reg_read(UC_ARM_REG_R2)
            got["r3"] = uc.reg_read(UC_ARM_REG_R3)
            uc.emu_stop()

    mu.hook_add(UC_HOOK_CODE, hook)
    mu.emu_start(0x0801BA9D, 0x0801BAB0)
    print("=== interval snippet 0x0801ba9c .. bl 0x0801c3ca ===")
    print(f"  r3 (ptr)   {got.get('r3', 0):#010x}  expect {TRANSPOSE_RAM:#010x}")
    print(f"  r1 (sub)   {got.get('r1', 0):#x}  *(int8*){TRANSPOSE_RAM:#x} transpose")
    print(f"  r2 (add)   {got.get('r2', 0):#x}  voice+0x4f interval")
    print(f"  r0 (note)  {got.get('r0', 0):#x}  held note")
    print("  noteval    0x0801c3ca  computes note + r2 - r1, octave-wrap")
    ok = (
        got.get("r3") == TRANSPOSE_RAM
        and got.get("r1") == 5
        and got.get("r2") == 7
        and got.get("r0") == 0x3C
    )
    print(f"  check      {'OK' if ok else 'FAIL'}")
    return 0 if ok else 1


def _load_rebuilt(name: str) -> bytes:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from led_codec import LedImage, decode_led  # noqa: WPS433

    path = ROOT / "firmware-re" / "firmware-images" / "rebuild" / name
    if not path.exists():
        raise SystemExit(f"missing {path} — run build_patch.py first")
    return LedImage.parse(decode_led(path.read_bytes())).extract_flash()


def _emu(flash: bytes) -> Uc:
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    size = (len(flash) + 0xFFF) & ~0xFFF
    mu.mem_map(BASE, size)
    mu.mem_write(BASE, flash)
    mu.mem_map(0x20000000, 0x10000)
    mu.mem_map(0x20010000, 0x2000)
    mu.reg_write(UC_ARM_REG_SP, 0x20011F00)
    return mu


def _expect_euclid(step: int, length: int, hits: int) -> int:
    if length == 0:
        return 1
    if hits == 0:
        return 0
    if hits >= length:
        return 1
    return int(((step % length) * hits) % length < hits)


def _plant_slot(mu: Uc, obj: int, data: int, pitches: list[int], length: int) -> None:
    mu.mem_write(obj, struct.pack("<I", data))
    blob = bytearray(0x408)
    for i, p in enumerate(pitches):
        blob[i * STEP_STRIDE] = p
    blob[0x400] = length & 0xFF
    mu.mem_write(data, bytes(blob))


def _run_pitch_gate(
    flash: bytes,
    wrap: int,
    pitches: list[int],
    length: int,
    n: int,
    *,
    pitch_at: int | None = None,
    call_step: int | None = None,
    flag: int = 0,
    leftover: bytes | None = None,
) -> list[int]:
    """n consecutive wrap calls. Returns pitch bytes.

    call_step: if set, seq_step_note always reads that slot index (so the
    count loop can see mixed rests while every CALL is a real note).
    leftover: if set, write these bytes at FLAG_RAM instead of planting
    ``flag``. Simulates unused SRAM after reset (not BSS-zeroed).
    """
    obj, data = 0x20005000, 0x20004000
    out: list[int] = []
    mu = _emu(flash)
    _plant_slot(mu, obj, data, pitches, length)
    mu.mem_write(0x20005F02, bytes([0]))
    if leftover is not None:
        mu.mem_write(0x20005F00, leftover)
    else:
        mu.mem_write(0x20005F00, bytes([flag & 1]))
    for i in range(n):
        step = call_step if call_step is not None else i % max(length, 1)
        mu.reg_write(UC_ARM_REG_LR, 0x20010001)
        mu.reg_write(UC_ARM_REG_R0, obj)
        mu.reg_write(UC_ARM_REG_R1, step)
        mu.reg_write(UC_ARM_REG_R2, 0)
        if pitch_at is not None:
            blob = bytearray(mu.mem_read(data, 0x408))
            blob[step * STEP_STRIDE] = pitch_at
            mu.mem_write(data, bytes(blob))
        mu.emu_start(wrap | 1, 0x20010000)
        out.append(mu.reg_read(UC_ARM_REG_R0) & 0xFF)
    return out


def cmd_euclid(_flash: bytes) -> int:
    """Unicorn euclid_gate / wrap on rebuilt E0, E1, E3, C1, e0b, e1b pages."""
    rc = 0
    print("=== euclid_gate 3-in-8 (E0 page) ===")
    e0 = _load_rebuilt("e0_euclid_3in8.led")
    mu = _emu(e0)
    mu.reg_write(UC_ARM_REG_LR, 0x20010001)
    got: list[int] = []
    for step in range(8):
        mu.reg_write(UC_ARM_REG_R0, step)
        mu.reg_write(UC_ARM_REG_R1, 8)
        mu.reg_write(UC_ARM_REG_R2, 3)
        mu.emu_start(0x0801F425, 0x20010000)
        got.append(mu.reg_read(UC_ARM_REG_R0) & 1)
    exp = [_expect_euclid(s, 8, 3) for s in range(8)]
    print(f"  got {got}  expect {exp}")
    ok = got == exp == [1, 0, 0, 1, 0, 0, 1, 0]
    print(f"  gate      {'OK' if ok else 'FAIL'}")
    rc |= 0 if ok else 1

    print("=== euclid_wrap (stock gate 0x81, 3-in-8) ===")
    wrapped: list[int] = []
    for step in range(8):
        mu = _emu(e0)
        mu.mem_write(0x080130F4, bytes.fromhex("81207047"))  # movs r0,#0x81; bx lr
        mu.reg_write(UC_ARM_REG_LR, 0x20010001)
        mu.reg_write(UC_ARM_REG_R0, 0x20005000)
        mu.reg_write(UC_ARM_REG_R1, step)
        mu.reg_write(UC_ARM_REG_R2, 0)
        mu.emu_start(0x0801F401, 0x20010000)
        wrapped.append(mu.reg_read(UC_ARM_REG_R0) & 0xFF)
    wexp = [0x81 if bit else 0x01 for bit in exp]
    print(f"  got {[hex(x) for x in wrapped]}  expect {[hex(x) for x in wexp]}")
    wok = wrapped == wexp
    print(f"  wrap      {'OK' if wok else 'FAIL'}")
    rc |= 0 if wok else 1

    print("=== E3 latch off → stock pass ===")
    e3 = _load_rebuilt("e3_euclid_shift.led")
    mu = _emu(e3)
    mu.mem_write(0x080130F4, bytes.fromhex("81207047"))
    mu.mem_write(0x20005F00, bytes([0]))
    mu.reg_write(UC_ARM_REG_LR, 0x20010001)
    mu.reg_write(UC_ARM_REG_R0, 0x20005000)
    mu.reg_write(UC_ARM_REG_R1, 1)  # miss in 3-in-8
    mu.reg_write(UC_ARM_REG_R2, 0)
    mu.emu_start(0x0801F401, 0x20010000)
    passthru = mu.reg_read(UC_ARM_REG_R0) & 0xFF
    lok = passthru == 0x81
    print(f"  step1 latch-off {passthru:#x} expect 0x81  {'OK' if lok else 'FAIL'}")
    rc |= 0 if lok else 1

    print("=== C1 snap_scale C major ===")
    c1 = _load_rebuilt("c1_scale_chord.led")
    mu = _emu(c1)
    mu.reg_write(UC_ARM_REG_LR, 0x20010001)
    mask = 0x0AB5  # C D E F G A B
    mu.reg_write(UC_ARM_REG_R0, 61)  # C#4
    mu.reg_write(UC_ARM_REG_R1, mask)
    # snap_scale symbol: after noteval_then_snap (~0x50 into page when FEAT_CHORD)
    # find by scanning for sdiv (0xfb90 f1f2 pattern) — call exported VA
    from build_patch import assemble, LEVELS  # noqa: WPS433

    _page, syms = assemble(LEVELS["c1"])
    snap = syms["snap_scale"]
    mu.emu_start(snap | 1, 0x20010000)
    snapped = mu.reg_read(UC_ARM_REG_R0) & 0xFF
    sok = snapped in (60, 62)
    print(f"  C#4 {61} + mask {mask:#x} -> {snapped}  {'OK' if sok else 'FAIL'}")
    rc |= 0 if sok else 1

    print("=== e0b pitch_gate_wrap 3-in-8 (STEP_CTR_RAM) ===")
    e0b = _load_rebuilt("e0b_pitchgate_3in8.led")
    _page, syms = assemble(LEVELS["e0b"])
    wrap = syms["pitch_gate_wrap"]
    filled = [0x40] * 8
    got = _run_pitch_gate(e0b, wrap, filled, 8, 8)
    exp_p = [0x40 if _expect_euclid(s, 8, 3) else 0x82 for s in range(8)]
    e0bok = got == exp_p
    print(f"  got {[hex(x) for x in got]}  expect {[hex(x) for x in exp_p]}")
    print(f"  e0b      {'OK' if e0bok else 'FAIL'}")
    rc |= 0 if e0bok else 1
    rest = _run_pitch_gate(e0b, wrap, filled, 8, 1, pitch_at=0x82)
    restok = rest == [0x82]
    print(f"  native rest pass-through {rest}  {'OK' if restok else 'FAIL'}")
    rc |= 0 if restok else 1

    print("=== e1b pitch_gate hits-from-slot ===")
    e1b = _load_rebuilt("e1b_pitchgate_hits.led")
    _page, syms = assemble(LEVELS["e1b"])
    wrap = syms["pitch_gate_wrap"]
    four_prefix = [0x40, 0x40, 0x40, 0x40, 0x82, 0x82, 0x82, 0x82]
    got = _run_pitch_gate(e1b, wrap, four_prefix, 8, 8, call_step=0)
    exp4 = [0x40 if _expect_euclid(s, 8, 4) else 0x82 for s in range(8)]
    e1bok = got == exp4
    print(f"  4-in-8 got {[hex(x) for x in got]}  expect {[hex(x) for x in exp4]}")
    print(f"  e1b 4/8  {'OK' if e1bok else 'FAIL'}")
    rc |= 0 if e1bok else 1
    full = [0x40] * 8
    got = _run_pitch_gate(e1b, wrap, full, 8, 8)
    fullok = got == [0x40] * 8
    print(f"  8-in-8 every-step {[hex(x) for x in got]}  {'OK' if fullok else 'FAIL'}")
    rc |= 0 if fullok else 1

    print("=== e3b latch off = stock, on = 3-in-8 ===")
    e3b = _load_rebuilt("e3b_pitchgate_shift.led")
    _page, syms = assemble(LEVELS["e3b"])
    wrap = syms["pitch_gate_wrap"]
    filled = [0x40] * 8
    got = _run_pitch_gate(e3b, wrap, filled, 8, 8, flag=0)
    offok = got == [0x40] * 8
    print(f"  latch-off { [hex(x) for x in got] }  {'OK' if offok else 'FAIL'}")
    rc |= 0 if offok else 1
    got = _run_pitch_gate(e3b, wrap, filled, 8, 8, flag=1)
    exp_p = [0x40 if _expect_euclid(s, 8, 3) else 0x82 for s in range(8)]
    onok = got == exp_p
    print(f"  latch-on  {[hex(x) for x in got]}  expect {[hex(x) for x in exp_p]}")
    print(f"  e3b on   {'OK' if onok else 'FAIL'}")
    rc |= 0 if onok else 1

    # Unicorn maps SRAM to 0, which hid the live e3b miss: FLAG_RAM
    # 0x20005F00 is unused SRAM, not BSS-zeroed. Leftover 0xFF is
    # truthy, so pitch_gate_wrap arms Euclidean with no Shift. Default
    # off after reset requires BSS-init (or an explicit store of 0).
    print("=== e3b leftover SRAM must not arm Euclidean ===")
    got = _run_pitch_gate(e3b, wrap, filled, 8, 8, leftover=bytes([0xFF]))
    leftover_ok = got == [0x40] * 8
    print(f"  FLAG=0xFF (reset leftover) {[hex(x) for x in got]}")
    print("  expect every-step 0x40 unless the patch BSS-inits FLAG_RAM")
    print(f"  leftover {'OK' if leftover_ok else 'FAIL'}")
    rc |= 0 if leftover_ok else 1

    print("=== e3b Shift+C2/D2 FLAG_RAM ===")
    mu = _emu(e3b)
    ev = 0x20003000
    mu.mem_write(0x20001120, struct.pack("<I", ev))
    mu.mem_write(ev + 0x25, bytes([1]))
    mu.mem_write(0x20005F00, bytes([0]))
    mu.reg_write(UC_ARM_REG_LR, 0x20010001)
    mu.reg_write(UC_ARM_REG_R1, 0x90 | (36 << 8))
    mu.reg_write(UC_ARM_REG_R2, 0)
    mu.reg_write(UC_ARM_REG_R3, 0)
    mu.emu_start(syms["shift_note_hook"] | 1, 0x20010000)
    on = mu.mem_read(0x20005F00, 1)[0]
    mu.reg_write(UC_ARM_REG_LR, 0x20010001)
    mu.reg_write(UC_ARM_REG_R1, 0x90 | (37 << 8))
    mu.emu_start(syms["shift_note_hook"] | 1, 0x20010000)
    off = mu.mem_read(0x20005F00, 1)[0]
    shok = on == 1 and off == 0
    print(f"  Shift+36 -> {on}  Shift+37 -> {off}  {'OK' if shok else 'FAIL'}")
    rc |= 0 if shok else 1
    return rc


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("cmd", choices=["interval", "pattern", "play", "euclid", "all"])
    args = p.parse_args()
    flash = load_flash()
    rc = 0
    if args.cmd in ("pattern", "all"):
        rc |= cmd_pattern(flash)
    if args.cmd in ("play", "all"):
        rc |= cmd_play(flash)
    if args.cmd in ("interval", "all"):
        rc |= cmd_interval(flash)
    if args.cmd in ("euclid", "all"):
        rc |= cmd_euclid(flash)
    return rc


if __name__ == "__main__":
    sys.exit(main())
