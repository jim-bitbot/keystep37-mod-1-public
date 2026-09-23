#!/usr/bin/env python3
"""Capstone dumps for tickets AK–AQ. Cursor-owned."""
from __future__ import annotations

import re
import struct
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[2]
FLASH = (ROOT / "firmware-re/firmware-images/keystep37_1.1.6.579_flash.bin").read_bytes()
BASE = 0x08000000
APP0, APP1 = 0x4000, 0x1F400
OUT = ROOT / "firmware-re/notes/scans"
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
STAMP = "2026-09-23T22:00+01:00"


def word(va: int) -> int:
    return int.from_bytes(FLASH[va - BASE : va - BASE + 4], "little")


def show(va: int, n: int = 16, nb: int = 64) -> list[str]:
    lines = []
    ins = list(md.disasm(FLASH[va - BASE : va - BASE + nb], va))[:n]
    for insn in ins:
        extra = ""
        if "[pc" in insn.op_str:
            m = re.search(r"#(-?0x[0-9a-fA-F]+|-?\d+)", insn.op_str)
            if m:
                imm = int(m.group(1), 0)
                lit = ((insn.address + 4) & ~3) + imm
                if 0 <= lit - BASE < len(FLASH) - 3:
                    extra = f"  ; {word(lit):#010x}"
        lines.append(f"  {insn.address:#010x}  {insn.mnemonic:8} {insn.op_str}{extra}")
    return lines


def dump(va: int, n: int = 16, nb: int = 64) -> str:
    return "\n".join(show(va, n, nb)) + "\n"


def bl_imm(pc: int, target: int) -> bytes | None:
    off = target - (pc + 4)
    if off % 2:
        return None
    imm = off // 2
    if not (-0x800000 <= imm <= 0x7FFFFF):
        return None
    s = (imm >> 23) & 1
    i1 = (imm >> 22) & 1
    i2 = (imm >> 21) & 1
    j1 = ((1 - i1) ^ s) & 1
    j2 = ((1 - i2) ^ s) & 1
    hi = 0xF000 | (s << 10) | ((imm >> 11) & 0x3FF)
    lo = 0xF800 | (j1 << 13) | (j2 << 11) | (imm & 0x7FF)
    return struct.pack("<HH", hi, lo)


def find_bl_to(target: int) -> list[int]:
    hits = []
    for off in range(APP0, APP1 - 4, 2):
        enc = bl_imm(BASE + off, target)
        if enc and FLASH[off : off + 4] == enc:
            hits.append(BASE + off)
    return hits


def find_ptr(thumb: int) -> list[int]:
    hits = []
    t0 = thumb & ~1
    for off in range(APP0, APP1 - 4, 4):
        w = int.from_bytes(FLASH[off : off + 4], "little")
        if (w & ~1) == t0 and w != 0:
            hits.append(BASE + off)
    return hits


def pc_rel(value: int) -> list[tuple[int, str, str]]:
    hits = []
    for off in range(APP0, APP1, 2):
        ins = list(md.disasm(FLASH[off : off + 4], BASE + off))
        if not ins or ins[0].address != BASE + off:
            continue
        insn = ins[0]
        if "[pc" not in insn.op_str:
            continue
        m = re.search(r"#(-?0x[0-9a-fA-F]+|-?\d+)", insn.op_str)
        if not m:
            continue
        imm = int(m.group(1), 0)
        lit = ((insn.address + 4) & ~3) + imm
        if 0 <= lit - BASE < len(FLASH) - 3 and word(lit) == value:
            hits.append((insn.address, insn.mnemonic, insn.op_str))
    return hits


def hdr(ticket: str, title: str, inp: str) -> str:
    return (
        f"STATUS: done\nAGENT: cursor\nTICKET: {ticket}\n"
        f"UPDATED: {STAMP}\nINPUT: {inp}\n\n# {title}\n"
    )


def write(name: str, body: str) -> None:
    p = OUT / name
    p.write_text(body, encoding="utf-8")
    print(f"wrote {p} ({len(body)} bytes)")


def ticket_ak() -> None:
    lines = [
        hdr(
            "AK",
            "AK-emit-seq-slots — stores to +0x18 / +0x1c on port objects",
            "scans/Z-usbdin-emu.txt; scans/R-usbdin.txt; firmware bin",
        ),
        "# Do not invent a callee if no store.\n",
    ]
    for obj, name in (
        (0x20001D60, "vtable 0x20001d60"),
        (0x20001E04, "mid 0x20001e04"),
        (0x20001EB8, "root 0x20001eb8"),
    ):
        rel = pc_rel(obj)
        lines.append(f"## {name}  pc-rel {len(rel)}\n")
        n = 0
        for va, mn, op in rel:
            dest = mn.startswith("ldr") and op.split(",")[0].strip()
            ins = list(md.disasm(FLASH[va - BASE : va - BASE + 96], va))[:20]
            hits = [
                i
                for i in ins
                if i.mnemonic.startswith("str")
                and ("#0x18" in i.op_str or "#0x1c" in i.op_str)
            ]
            if not hits:
                continue
            n += 1
            lines.append(f"from {va:#010x}  {mn} {op}  dest={dest}")
            lines.extend(show(va, 16, 56))
            lines.append("")
        lines.append(f"windows with +0x18/+0x1c store: {n}\n")
    # any str of a known thunk into memory — list str [r,#0x18]/#0x1c
    # that sit inside 0x0801acb0 / 0x0801b02c / 0x0801b572
    lines.append("## ctor bodies (known)\n")
    lines.append("### 0x0801acb0\n")
    lines.append(dump(0x0801ACB0, 20, 64))
    lines.append("### 0x0801b02c stores of +0x18-ish\n")
    lines.append(dump(0x0801B02C, 24, 80))
    write("AK-emit-seq-slots.txt", "\n".join(lines) + "\n")


def ticket_al() -> None:
    lines = [
        hdr(
            "AL",
            "AL-1509a — callers of ring_consume 0x0801509a",
            "scans/AH-10638.txt; firmware bin",
        ),
        "## 1. bl-to 0x0801509a\n",
    ]
    hits = find_bl_to(0x0801509A)
    lines.append(f"count {len(hits)} {[hex(h) for h in hits]}\n")
    for va in hits:
        lines.append(dump(va - 12, 14, 48))
    lines.append("## 2. Thumb ptr word == 0x0801509b\n")
    ptrs = find_ptr(0x0801509B)
    lines.append(f"count {len(ptrs)}\n")
    for va in ptrs:
        lines.append(f"  {va:#010x} = {word(va):#010x}")
        lines.append(dump(max(va - 8, BASE + APP0), 6, 24))
    lines.append("## 3. bl-to 0x08010638 (AH already: only 0x080150a4)\n")
    lines.append(f"{[hex(h) for h in find_bl_to(0x08010638)]}\n")
    write("AL-1509a.txt", "\n".join(lines) + "\n")


def ticket_am() -> None:
    # TBB at 0x080060a8; table at tbb+4 = 0x080060ac
    tbb = 0x080060A8
    table = tbb + 4
    raw4 = FLASH[table - BASE : table - BASE + 4]
    lines = [
        hdr(
            "AM",
            "AM-kind-tbb — raw TBB bytes of knob_index_to_cc",
            "scans/AC-analog-names.txt; firmware bin",
        ),
        "## 1. function\n",
        dump(0x080060A2, 20, 48),
        f"## 2. TBB table at {table:#010x}  4 bytes {raw4.hex()}\n",
    ]
    for i, b in enumerate(raw4):
        tgt = (table + (b << 1)) & ~1
        kind = i + 1  # after subs r0,#1
        lines.append(f"  index {i}  kind {kind}  byte {b:#04x}  target {tgt:#010x}")
        lines.append(dump(tgt, 4, 16))
    lines.append("kind 0 and kind>=5 take bhi → 0x080060b0  movs r0,#0x66\n")
    write("AM-kind-tbb.txt", "\n".join(lines) + "\n")


def ticket_an() -> None:
    lines = [
        hdr(
            "AN",
            "AN-sync-13 — 0x0800f32a +0x3c=#0x13 and transport_cmd 0x08012334",
            "scans/AB-sync-dip.txt; firmware bin",
        ),
        "# AB labelled 0x0800fa64 as transport_cmd — wrong. This file uses 0x08012334.\n",
        "## 1. 0x0800f32a\n",
        dump(0x0800F318, 20, 64),
        "## 2. cmp #0x13 after a +0x3c load (param_field_dispatch object)\n",
    ]
    # search ldrb [r,#0x3c] then nearby cmp #0x13
    n = 0
    for off in range(APP0, APP1, 2):
        ins = list(md.disasm(FLASH[off : off + 8], BASE + off))
        if not ins or ins[0].address != BASE + off:
            continue
        i = ins[0]
        if not i.mnemonic.startswith("ldr") or "#0x3c" not in i.op_str:
            continue
        if "pc" in i.op_str:
            continue
        win = list(md.disasm(FLASH[off : off + 48], BASE + off))[:12]
        if any("cmp" in j.mnemonic and "#0x13" in j.op_str for j in win):
            n += 1
            lines.append(f"from {i.address:#010x}")
            lines.extend(f"  {j.address:#010x}  {j.mnemonic:8} {j.op_str}" for j in win)
            lines.append("")
    lines.append(f"ldrb/ldr +0x3c windows with cmp #0x13: {n}\n")
    lines.append("## 3. transport_cmd 0x08012334\n")
    lines.append(dump(0x08012334, 24, 80))
    # GPIO literals in that function — walk until next push after 0x100 bytes
    lines.append("## 4. pc-rel in 0x08012334–0x08012400\n")
    for off in range(0x08012334 - BASE, 0x08012400 - BASE, 2):
        ins = list(md.disasm(FLASH[off : off + 4], BASE + off))
        if not ins or ins[0].address != BASE + off:
            continue
        insn = ins[0]
        if "[pc" not in insn.op_str:
            continue
        m = re.search(r"#(-?0x[0-9a-fA-F]+|-?\d+)", insn.op_str)
        if not m:
            continue
        imm = int(m.group(1), 0)
        lit = ((insn.address + 4) & ~3) + imm
        if 0 <= lit - BASE < len(FLASH) - 3:
            lines.append(f"  {insn.address:#010x}  {insn.mnemonic} {insn.op_str}  ; {word(lit):#010x}")
    lines.append("")
    write("AN-sync-13.txt", "\n".join(lines) + "\n")


def ticket_ao() -> None:
    seq = bytes([0x34, 0x36, 0x39, 0x3C, 0x3F, 0x43, 0x47, 0x4B])
    lines = [
        hdr(
            "AO",
            "AO-swing-table — occupancy swing byte run and +0x401 users",
            "scans/AA-swing-tempo.txt; firmware bin",
        ),
        f"## 1. byte run {seq.hex()}\n",
    ]
    pos = APP0
    found = 0
    while True:
        i = FLASH.find(seq, pos, APP1)
        if i < 0:
            break
        found += 1
        va = BASE + i
        lines.append(f"  hit {va:#010x}")
        lines.append(dump(va, 4, 16))
        pos = i + 1
    lines.append(f"count {found}\n")
    lines.append("## 2. +0x401 load then use (not the store-only sites)\n")
    for off in range(APP0, APP1, 2):
        ins = list(md.disasm(FLASH[off : off + 8], BASE + off))
        if not ins or ins[0].address != BASE + off:
            continue
        i = ins[0]
        if not i.mnemonic.startswith("ldr") or "#0x401" not in i.op_str:
            continue
        lines.append(f"### {i.address:#010x}")
        lines.append(dump(i.address, 12, 40))
    write("AO-swing-table.txt", "\n".join(lines) + "\n")


def ticket_ap() -> None:
    lines = [
        hdr(
            "AP",
            "AP-rec-led — Rec press notify vs led_write / led_refresh",
            "scans/W-led-confirm.txt; scans/F-buttons.txt; firmware bin",
        ),
        "## 1. unshifted Rec 0x0801780c\n",
        dump(0x0801780C, 20, 64),
        "## 2. bl from that window\n",
    ]
    rec_ins = list(md.disasm(FLASH[0x0801780C - BASE : 0x0801780C - BASE + 80], 0x0801780C))[:24]
    for i in rec_ins:
        if i.mnemonic == "bl":
            m = re.search(r"#(0x[0-9a-fA-F]+)", i.op_str)
            tgt = int(m.group(1), 0) if m else None
            lines.append(f"  {i.address:#010x}  bl {tgt:#010x}" if tgt else f"  {i.address:#010x}  {i.mnemonic} {i.op_str}")
            if tgt:
                lines.append(dump(tgt, 12, 40))
    lines.append("## 3. led_write 0x0800d26e callers (count only + any in 0x08017800–0x08017900)\n")
    lw = find_bl_to(0x0800D26E)
    lr = find_bl_to(0x0800D1F8)
    lines.append(f"led_write bl count {len(lw)}")
    lines.append(f"led_refresh bl count {len(lr)}")
    near = [h for h in lw + lr if 0x08017800 <= h <= 0x08017980]
    lines.append(f"in Rec window: {[hex(h) for h in near] or 'none'}\n")
    write("AP-rec-led.txt", "\n".join(lines) + "\n")


def ticket_aq() -> None:
    sites = [
        (8, 0x20002CDC, 0x08006B68),
        (9, 0x20002CF8, 0x08006BEC),
        (10, 0x20002DBC, 0x08006D20),
        (11, 0x20002E80, 0x080069F8),
    ]
    lines = [
        hdr(
            "AQ",
            "AQ-sites-08-11 — leftover G objects AI skipped",
            "scans/G-ctors.txt; scans/S-ctor-readers.txt; firmware bin",
        )
    ]
    for site, ram, ctor in sites:
        rel = pc_rel(ram)
        lines.append(f"## site {site:02d} {ram:#010x} ctor {ctor:#010x}  pc-rel {len(rel)}\n")
        shown = 0
        for va, mn, op in rel:
            if ctor <= va <= ctor + 0x80:
                continue
            shown += 1
            lines.append(f"### reader {shown} {va:#010x}  {mn} {op}")
            lines.extend(show(va, 10, 40))
            lines.append("")
            if shown >= 3:
                break
        if shown == 0:
            lines.append("  no outside-ctor reader in first pass\n")
            if rel:
                va, mn, op = rel[0]
                lines.append(f"  first (may be ctor) {va:#010x}  {mn} {op}")
                lines.extend(show(va, 8, 32))
                lines.append("")
    write("AQ-sites-08-11.txt", "\n".join(lines) + "\n")


def main() -> None:
    ticket_ak()
    ticket_al()
    ticket_am()
    ticket_an()
    ticket_ao()
    ticket_ap()
    ticket_aq()


if __name__ == "__main__":
    main()
