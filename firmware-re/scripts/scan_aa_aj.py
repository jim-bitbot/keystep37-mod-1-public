#!/usr/bin/env python3
"""Capstone dumps for tickets AA–AJ. Writes scans/*.txt. Cursor-owned."""
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
md.detail = False

STAMP = "2026-09-23T21:45+01:00"


def word(va: int) -> int:
    return int.from_bytes(FLASH[va - BASE : va - BASE + 4], "little")


def half(va: int) -> int:
    return int.from_bytes(FLASH[va - BASE : va - BASE + 2], "little")


def show(va: int, n: int = 16, nb: int = 80) -> list[str]:
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


def bl_imm(pc: int, target: int) -> bytes | None:
    """Thumb BL encoding from pc to target. Returns 4 bytes or None if out of range."""
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
    imm10 = (imm >> 11) & 0x3FF
    imm11 = imm & 0x7FF
    hi = 0xF000 | (s << 10) | imm10
    lo = 0xF800 | (j1 << 13) | (j2 << 11) | imm11
    return struct.pack("<HH", hi, lo)


def find_bl_to(target: int) -> list[int]:
    hits = []
    for off in range(APP0, APP1 - 4, 2):
        enc = bl_imm(BASE + off, target)
        if enc and FLASH[off : off + 4] == enc:
            hits.append(BASE + off)
    return hits


def find_ptr(target: int) -> list[int]:
    """Word == target or target|1."""
    hits = []
    t0 = target & ~1
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


def imm_hits(needles: set[int], mnemonics: set[str] | None = None) -> list[tuple[int, str, str]]:
    hits = []
    for off in range(APP0, APP1, 2):
        ins = list(md.disasm(FLASH[off : off + 6], BASE + off))
        if not ins or ins[0].address != BASE + off:
            continue
        insn = ins[0]
        if mnemonics and insn.mnemonic.split(".")[0] not in mnemonics:
            continue
        for m in re.finditer(r"#(-?0x[0-9a-fA-F]+|-?\d+)", insn.op_str):
            v = int(m.group(1), 0) & 0xFFFFFFFF
            if v in needles or (v & 0xFF) in needles:
                hits.append((insn.address, insn.mnemonic, insn.op_str))
                break
    return hits


def stores_near_pcrel(obj: int, window: int = 24) -> list[tuple[int, str, str]]:
    """After each pc-rel load of obj, dump following stores in window insns."""
    out = []
    for va, mn, op in pc_rel(obj):
        ins = list(md.disasm(FLASH[va - BASE : va - BASE + 80], va))[:window]
        for insn in ins:
            if insn.mnemonic.startswith("str"):
                out.append((insn.address, insn.mnemonic, insn.op_str, va))
    return out


def containing_push(va: int, back: int = 0x200) -> int | None:
    """Walk back for a push that includes lr."""
    start = max(APP0, va - BASE - back)
    best = None
    for off in range(va - BASE, start, -2):
        ins = list(md.disasm(FLASH[off : off + 8], BASE + off))
        if not ins or ins[0].address != BASE + off:
            continue
        insn = ins[0]
        if insn.mnemonic.startswith("push") and "lr" in insn.op_str:
            best = insn.address
            # keep walking a bit; last push before va
    # take the nearest push-lr before va
    nearest = None
    for off in range(va - BASE, start, -2):
        ins = list(md.disasm(FLASH[off : off + 8], BASE + off))
        if not ins or ins[0].address != BASE + off:
            continue
        insn = ins[0]
        if insn.mnemonic.startswith("push") and "lr" in insn.op_str:
            nearest = insn.address
            break
        if insn.mnemonic in ("bx", "pop") and ("pc" in insn.op_str or insn.op_str == "lr"):
            break
    return nearest


def hdr(ticket: str, title: str, inp: str) -> str:
    return (
        f"STATUS: done\n"
        f"AGENT: cursor\n"
        f"TICKET: {ticket}\n"
        f"UPDATED: {STAMP}\n"
        f"INPUT: {inp}\n\n"
        f"# {title}\n"
    )


def write(name: str, body: str) -> None:
    p = OUT / name
    p.write_text(body, encoding="utf-8")
    print(f"wrote {p} ({len(body)} bytes)")


def dump_block(va: int, n: int = 16, nb: int = 64) -> str:
    return "\n".join(show(va, n, nb)) + "\n"


# ---------------------------------------------------------------------------
# AA
# ---------------------------------------------------------------------------
def ticket_aa() -> None:
    lines = [
        hdr(
            "AA",
            "AA-swing-tempo — tick stores, occupancy swing values, TIM2 ARR writers",
            "scans/I-time.txt; scans/N-05534.txt; scans/T-clock-source.txt; firmware bin",
        ),
        "# Slot +0x401 name stays H until a reader in this file.\n",
        "## 1. pc-rel of tick object 0x20002bec\n",
    ]
    rel = pc_rel(0x20002BEC)
    lines.append(f"count {len(rel)}\n")
    for va, mn, op in rel:
        lines.append(f"  {va:#010x}  {mn:8} {op}")
        lines.extend(show(va, 8, 32))
        lines.append("")
    lines.append("\n## 2. stores in windows after those loads (any offset)\n")
    for va, mn, op in rel:
        ins = list(md.disasm(FLASH[va - BASE : va - BASE + 96], va))[:20]
        stores = [i for i in ins if i.mnemonic.startswith("str")]
        if not stores:
            continue
        lines.append(f"from load {va:#010x}")
        for i in stores:
            lines.append(f"  {i.address:#010x}  {i.mnemonic:8} {i.op_str}")
        lines.append("")
    lines.append("\n## 3. occupancy swing values as cmp/mov/strb imm\n")
    swing = {52, 54, 57, 60, 63, 67, 71, 75, 0x34, 0x36, 0x39, 0x3C, 0x3F, 0x43, 0x47, 0x4B}
    hits = imm_hits(swing, {"cmp", "cmpw", "movs", "mov", "movw", "strb", "strb.w"})
    lines.append(f"count {len(hits)} (cmp/mov/strb only)\n")
    for va, mn, op in hits[:80]:
        lines.append(f"  {va:#010x}  {mn:8} {op}")
    if len(hits) > 80:
        lines.append(f"  ... {len(hits) - 80} more")
    lines.append("\n## 4. +0x401 (0x401 / 1025) immediates near slot / store\n")
    hits401 = imm_hits({0x401})
    lines.append(f"count {len(hits401)}\n")
    for va, mn, op in hits401:
        lines.append(f"  {va:#010x}  {mn:8} {op}")
        lines.extend(show(va, 6, 24))
        lines.append("")
    lines.append("\n## 5. TIM2 ARR [r0,#0x2c] after load of 0x20005534, besides 0x08012084\n")
    rel55 = pc_rel(0x20005534)
    arr = []
    for va, mn, op in rel55:
        ins = list(md.disasm(FLASH[va - BASE : va - BASE + 128], va))[:32]
        for i in ins:
            if i.mnemonic.startswith("str") and "#0x2c" in i.op_str:
                arr.append((va, i.address, i.mnemonic, i.op_str))
    lines.append(f"ARR stores in 32-insn windows after 0x20005534 loads: {len(arr)}\n")
    for src, va, mn, op in arr:
        lines.append(f"  load {src:#010x}  store {va:#010x}  {mn} {op}")
    lines.append("\n0x08012084 window (known):\n")
    lines.append(dump_block(0x08012070, 16, 56))
    # also any str ..., #0x2c in app near tim
    lines.append("## 6. any str* #0x2c in app (noisy; filter later)\n")
    str2c = []
    for off in range(APP0, APP1, 2):
        ins = list(md.disasm(FLASH[off : off + 8], BASE + off))
        if not ins or ins[0].address != BASE + off:
            continue
        i = ins[0]
        if i.mnemonic.startswith("str") and "#0x2c" in i.op_str:
            str2c.append((i.address, i.mnemonic, i.op_str))
    lines.append(f"count {len(str2c)}\n")
    for va, mn, op in str2c:
        lines.append(f"  {va:#010x}  {mn:8} {op}")
    write("AA-swing-tempo.txt", "\n".join(lines) + "\n")


def ticket_ab() -> None:
    lines = [
        hdr(
            "AB",
            "AB-sync-dip — #0x13 / GPIO vs clock leaves",
            "scans/T-clock-source.txt; scans/N-sync.txt; firmware bin",
        ),
        "## 1. immediates #0x13 / #19 in app (cmp/mov/strb/ands/orrs)\n",
    ]
    hits = imm_hits({0x13, 19}, {"cmp", "cmpw", "movs", "mov", "movw", "strb", "strb.w", "ands", "and", "orrs", "orr", "tst", "teq"})
    lines.append(f"count {len(hits)}\n")
    for va, mn, op in hits:
        lines.append(f"  {va:#010x}  {mn:8} {op}")
        lines.extend(show(va, 8, 32))
        lines.append("")
    lines.append("\n## 2. GPIO bases near 0x20005534 / clock leaves\n")
    gpios = [0x40010800, 0x40010C00, 0x40011000, 0x40011400, 0x40011800, 0x40011C00]
    for g in gpios:
        rel = pc_rel(g)
        if not rel:
            continue
        lines.append(f"pc-rel {g:#010x} count {len(rel)}")
        for va, mn, op in rel[:12]:
            lines.append(f"  {va:#010x}  {mn:8} {op}")
        lines.append("")
    for leaf in (0x0800B0C6, 0x0800B0AE, 0x0800B2AE, 0x08011EE4):
        lines.append(f"## leaf {leaf:#010x}\n")
        lines.append(dump_block(leaf, 16, 56))
    # transport_cmd
    lines.append("## 3. transport_cmd 0x0800fa64 first 16 (clock bytes already N)\n")
    lines.append(dump_block(0x0800FA64, 16, 56))
    write("AB-sync-dip.txt", "\n".join(lines) + "\n")


def ticket_ac() -> None:
    lines = [
        hdr(
            "AC",
            "AC-analog-names — knob_index_to_cc / test20_cc_value callers",
            "scans/D-analog.txt; scans/S-ctor-readers.txt; firmware bin",
        ),
        "## 1. bl-to knob_index_to_cc 0x080060a2\n",
    ]
    for va in find_bl_to(0x080060A2):
        lines.append(f"### {va:#010x}")
        lines.append(dump_block(va - 16 if va > BASE + 16 else va, 16, 56))
    lines.append("## 2. bl-to test20_cc_value 0x080068c8\n")
    for va in find_bl_to(0x080068C8):
        lines.append(f"### {va:#010x}")
        lines.append(dump_block(va - 16 if va > BASE + 16 else va, 16, 56))
    lines.append("## 3. pc-rel analog objects\n")
    for obj, name in (
        (0x2000121C, "kind1"),
        (0x20001294, "kind2"),
        (0x2000130C, "kind3"),
        (0x20001384, "kind4"),
        (0x20000468, "kind0?"),
        (0x2000058C, "site17 Rate cand"),
        (0x2000039C, "strip_b"),
    ):
        rel = pc_rel(obj)
        lines.append(f"### {name} {obj:#010x}  loads {len(rel)}")
        for va, mn, op in rel[:16]:
            lines.append(f"  {va:#010x}  {mn:8} {op}")
        lines.append("")
    lines.append("## 4. knob_index_to_cc body\n")
    lines.append(dump_block(0x080060A2, 20, 64))
    lines.append("## 5. test20_cc_value body\n")
    lines.append(dump_block(0x080068C8, 20, 64))
    write("AC-analog-names.txt", "\n".join(lines) + "\n")


def ticket_ad() -> None:
    lines = [
        hdr(
            "AD",
            "AD-key-r2 — 20 insns before each bl 0x0801b750 and sb reads",
            "scans/E-keys.txt; firmware bin",
        ),
        "## 1. 20 insns before each bl\n",
    ]
    for va in find_bl_to(0x0801B750):
        start = va - 40
        lines.append(f"### bl {va:#010x}")
        lines.append(dump_block(start, 22, 72))
    lines.append("## 2. 0x0801b750 entry + first sb reads\n")
    lines.append(dump_block(0x0801B750, 20, 64))
    lines.append("sb / r2 uses inside the function (scan 0x0801b750–0x0801bb00):\n")
    for off in range(0x0801B750 - BASE, 0x0801BB00 - BASE, 2):
        ins = list(md.disasm(FLASH[off : off + 8], BASE + off))
        if not ins or ins[0].address != BASE + off:
            continue
        i = ins[0]
        if "sb" in i.op_str.split(",")[0] or i.op_str.startswith("sb") or ", sb" in i.op_str or i.op_str.endswith("sb"):
            lines.append(f"  {i.address:#010x}  {i.mnemonic:8} {i.op_str}")
    lines.append("\n## 3. first sb read region 0x0801b8b0\n")
    lines.append(dump_block(0x0801B8A8, 20, 64))
    write("AD-key-r2.txt", "\n".join(lines) + "\n")


def ticket_ae() -> None:
    lines = [
        hdr(
            "AE",
            "AE-tap-clear — #0x67 besides id tables; Shift+Oct combo",
            "scans/F-buttons.txt; scans/Y-record-rest.txt; firmware bin",
        ),
        "## 1. #0x67 / #103 immediates\n",
    ]
    hits = imm_hits({0x67, 103})
    lines.append(f"count {len(hits)}\n")
    for va, mn, op in hits:
        lines.append(f"  {va:#010x}  {mn:8} {op}")
        lines.extend(show(va, 8, 32))
        lines.append("")
    lines.append("## 2. id_to_index 0x08006024 (skip-compare)\n")
    lines.append(dump_block(0x08006024, 20, 64))
    lines.append("## 3. compact 2/3 (Oct) held-together: cmp #2 / #3 near Shift RAM 0x200010d2\n")
    rel = pc_rel(0x200010D2)
    lines.append(f"Shift RAM loads {len(rel)}\n")
    for va, mn, op in rel:
        ins = list(md.disasm(FLASH[va - BASE : va - BASE + 64], va))[:16]
        interesting = [i for i in ins if any(x in i.op_str for x in ("#2", "#3", "#0x2", "#0x3", "#4", "#0x4"))]
        if interesting:
            lines.append(f"from {va:#010x}")
            for i in ins:
                lines.append(f"  {i.address:#010x}  {i.mnemonic:8} {i.op_str}")
            lines.append("")
    lines.append("## 4. bl-to seq_step_store 0x08014418\n")
    for va in find_bl_to(0x08014418):
        lines.append(f"### {va:#010x}")
        lines.append(dump_block(va - 12, 14, 48))
    write("AE-tap-clear.txt", "\n".join(lines) + "\n")


def ticket_af() -> None:
    lines = [
        hdr(
            "AF",
            "AF-set-alt — SET without TBB; param_field_dispatch write path",
            "scans/U-set-protocol.txt; scans/X-selectors.txt; firmware bin",
        ),
        "## 1. param_field_dispatch 0x0800f054 + callers\n",
    ]
    lines.append(dump_block(0x0800F054, 24, 80))
    for va in find_bl_to(0x0800F054):
        lines.append(f"### caller {va:#010x}")
        lines.append(dump_block(va - 16, 16, 56))
    lines.append("## 2. get_param family entries (write-shaped stores in first 32)\n")
    for va, name in (
        (0x08005E84, "get_param"),
        (0x0800614C, "get_param_b"),
        (0x080060C4, "get_param_c"),
        (0x0800EE92, "GET TBB"),
        (0x0800EF38, "sibling"),
    ):
        lines.append(f"### {name} {va:#010x}")
        lines.append(dump_block(va, 20, 64))
        ins = list(md.disasm(FLASH[va - BASE : va - BASE + 128], va))[:32]
        stores = [i for i in ins if i.mnemonic.startswith("str")]
        lines.append(f"stores in first 32: {len(stores)}")
        for i in stores:
            lines.append(f"  {i.address:#010x}  {i.mnemonic:8} {i.op_str}")
        lines.append("")
    write("AF-set-alt.txt", "\n".join(lines) + "\n")


def ticket_ag() -> None:
    lines = [
        hdr(
            "AG",
            "AG-persist-wrap — 16 insns of 0x0800ddf6 / 0x08008290 / 0x08008338",
            "scans/V-persist-commit.txt; firmware bin",
        ),
        "# Stop at first 0x40022000 FLASH store. Do not reverse HAL.\n",
        "## 1. 0x0800ddf6\n",
    ]
    lines.append(dump_block(0x0800DDF6, 20, 72))
    lines.append("## 2. 0x08008290\n")
    lines.append(dump_block(0x08008290, 20, 72))
    lines.append("## 3. 0x08008338\n")
    lines.append(dump_block(0x08008338, 20, 72))
    lines.append("## 4. FLASH 0x40022000 pc-rel in those windows\n")
    for va in (0x0800DDF6, 0x08008290, 0x08008338):
        ins = list(md.disasm(FLASH[va - BASE : va - BASE + 96], va))[:24]
        for i in ins:
            extra = ""
            if "[pc" in i.op_str:
                m = re.search(r"#(-?0x[0-9a-fA-F]+|-?\d+)", i.op_str)
                if m:
                    imm = int(m.group(1), 0)
                    lit = ((i.address + 4) & ~3) + imm
                    if 0 <= lit - BASE < len(FLASH) - 3:
                        extra = f"  ; {word(lit):#010x}"
                        if word(lit) == 0x40022000:
                            extra += "  FLASH"
            if "40022000" in extra or "#0x40022000" in i.op_str:
                lines.append(f"  HIT {i.address:#010x}  {i.mnemonic} {i.op_str}{extra}")
    lines.append("\n## 5. bl-to 0x0800de90 / 0x0800de10 / container of 0x0800e21a\n")
    for t in (0x0800DE90, 0x0800DE10, 0x0800DDF6, 0x08008290, 0x08008338):
        hits = find_bl_to(t)
        lines.append(f"bl-to {t:#010x}: {[hex(h) for h in hits]}")
    start = containing_push(0x0800E21A, 0x400)
    lines.append(f"\ncontaining push of 0x0800e21a: {start:#010x}" if start else "\ncontaining push of 0x0800e21a: not in 0x400")
    if start:
        lines.append(dump_block(start, 16, 56))
    write("AG-persist-wrap.txt", "\n".join(lines) + "\n")


def ticket_ah() -> None:
    lines = [
        hdr(
            "AH",
            "AH-10638 — containing start of 0x080150a4; Thumb ptrs to 0x08010638",
            "scans/C-loop-irq.txt; scans/Q-h-rows.txt; firmware bin",
        ),
        "## 1. walk back from 0x080150a4\n",
    ]
    lines.append(dump_block(0x08015090, 16, 56))
    start = containing_push(0x080150A4, 0x800)
    lines.append(f"nearest push-lr before 0x080150a4 (stop at bx/pop): {hex(start) if start else 'none'}\n")
    if start:
        lines.append(dump_block(start, 16, 56))
    # keep walking for earlier pushes
    lines.append("pushes with lr in 0x08014800–0x080150a4:\n")
    for off in range(0x08014800 - BASE, 0x080150A4 - BASE, 2):
        ins = list(md.disasm(FLASH[off : off + 8], BASE + off))
        if not ins or ins[0].address != BASE + off:
            continue
        i = ins[0]
        if i.mnemonic.startswith("push") and "lr" in i.op_str:
            lines.append(f"  {i.address:#010x}  {i.mnemonic} {i.op_str}")
    lines.append("\n## 2. bl-to 0x08010638\n")
    hits = find_bl_to(0x08010638)
    lines.append(f"count {len(hits)} {[hex(h) for h in hits]}\n")
    for va in hits:
        lines.append(dump_block(va - 8, 10, 40))
    lines.append("## 3. Thumb pointers word == 0x08010639\n")
    ptrs = find_ptr(0x08010639)
    lines.append(f"count {len(ptrs)}\n")
    for va in ptrs:
        lines.append(f"  table {va:#010x} = {word(va):#010x}")
        lines.append(dump_block(va, 4, 16))
    lines.append("## 4. 0x08010638 start (Q already)\n")
    lines.append(dump_block(0x08010638, 16, 56))
    write("AH-10638.txt", "\n".join(lines) + "\n")


def ticket_ai() -> None:
    leftover = [
        (1, 0x20000410),
        (5, 0x200013FC),
        (6, 0x20002E88),
        (7, 0x20002DD0),
        (12, 0x20004F00),
        (13, 0x200005F8),
        (23, 0x200011DC),
        (34, 0x20000FEC),
        (35, 0x20000654),
        (36, 0x20002CEC),
        (41, 0x20004F18),
        (46, 0x200007DC),
        (47, 0x20000668),
        (48, 0x200023F8),
        (50, 0x20001E04),
        (52, 0x20001180),
        (53, 0x20001204),
    ]
    lines = [
        hdr(
            "AI",
            "AI-ctors-init — init_array five ptrs + leftover H-role readers",
            "scans/A-boot.txt; scans/S-ctor-readers.txt; firmware bin",
        ),
        "## 1. init_array 0x0801ef58–0x0801ef6c\n",
    ]
    for va in range(0x0801EF58, 0x0801EF70, 4):
        w = word(va)
        lines.append(f"  {va:#010x}  {w:#010x}  fn {w & ~1:#010x}")
        lines.append(dump_block(w & ~1, 14, 48))
    lines.append("## 2. leftover H-role RAM: one reader window each (first outside-ctor pc-rel)\n")
    for site, ram in leftover:
        rel = pc_rel(ram)
        lines.append(f"### site {site:02d} {ram:#010x}  pc-rel {len(rel)}")
        if not rel:
            lines.append("  no reader found")
            lines.append("")
            continue
        va, mn, op = rel[0]
        # skip if first is likely ctor-adjacent; still dump first + one later if any
        lines.append(f"  first {va:#010x}  {mn} {op}")
        lines.extend(show(va, 10, 40))
        if len(rel) > 1:
            va2, mn2, op2 = rel[min(1, len(rel) - 1)]
            if va2 != va:
                lines.append(f"  second {va2:#010x}  {mn2} {op2}")
                lines.extend(show(va2, 8, 32))
        lines.append("")
    lines.append("## 3. Rate candidate 0x2000058c (if AC open)\n")
    rel = pc_rel(0x2000058C)
    lines.append(f"pc-rel count {len(rel)}")
    for va, mn, op in rel:
        lines.append(f"  {va:#010x}  {mn:8} {op}")
        lines.extend(show(va, 8, 32))
        lines.append("")
    write("AI-ctors-init.txt", "\n".join(lines) + "\n")


def ticket_aj() -> None:
    lines = [
        hdr(
            "AJ",
            "AJ-leftovers — +0x50, store case 5, Time Div #8",
            "scans/H-shared.txt; scans/Y-record-rest.txt; scans/I-time.txt; firmware bin",
        ),
        "## 1. 0x200051cc+0x50 readers (strb/ldrb #0x50 after pc-rel of object)\n",
    ]
    rel = pc_rel(0x200051CC)
    n50 = 0
    for va, mn, op in rel:
        ins = list(md.disasm(FLASH[va - BASE : va - BASE + 96], va))[:20]
        hits = [i for i in ins if "#0x50" in i.op_str or ", #80" in i.op_str]
        if hits:
            n50 += 1
            lines.append(f"from load {va:#010x}")
            for i in ins[:16]:
                lines.append(f"  {i.address:#010x}  {i.mnemonic:8} {i.op_str}")
            lines.append("")
    lines.append(f"windows with #0x50 after a 0x200051cc load: {n50}\n")
    # also any ldrb/strb [rx,#0x50] in app — too noisy; keep windows
    lines.append("## 2. case 5 0x08014494 + callers of seq_step_store\n")
    lines.append(dump_block(0x08014494, 20, 64))
    for va in find_bl_to(0x08014418):
        lines.append(f"### bl seq_step_store {va:#010x}")
        lines.append(dump_block(va - 12, 14, 48))
    lines.append("## 3. Time Div #8 at 0x08005ae8 / 0x08005af0 (I rewrite, for remodel)\n")
    lines.append(dump_block(0x08005AB8, 28, 96))
    write("AJ-leftovers.txt", "\n".join(lines) + "\n")


def main() -> None:
    ticket_aa()
    ticket_ab()
    ticket_ac()
    ticket_ad()
    ticket_ae()
    ticket_af()
    ticket_ag()
    ticket_ah()
    ticket_ai()
    ticket_aj()


if __name__ == "__main__":
    main()
