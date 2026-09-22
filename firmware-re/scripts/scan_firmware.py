#!/usr/bin/env python3
"""Whole-binary scanners for the KeyStep 37 decoded app image.

Load base is 0x08000000. Prefers the stripped flash extract
(`keystep37_1.1.6.579_flash.bin`); falls back to the framed decode.

Usage:
    python3 scan_firmware.py stores-214
    python3 scan_firmware.py tbb
    python3 scan_firmware.py ptr-runs
    python3 scan_firmware.py bl-to <hex_addr>
    python3 scan_firmware.py cmp-imm
"""
from __future__ import annotations

import argparse
import pathlib
import struct
import sys

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

BASE = 0x08000000
ROOT = pathlib.Path(__file__).resolve().parents[2]
FLASH_PATH = ROOT / "firmware-re" / "firmware-images" / "keystep37_1.1.6.579_flash.bin"
FRAMED_PATH = ROOT / "firmware-re" / "firmware-images" / "keystep37_1.1.6.579_decoded.bin"
BIN_PATH = FLASH_PATH if FLASH_PATH.exists() else FRAMED_PATH


def load() -> bytes:
    return BIN_PATH.read_bytes()


def va(off: int) -> int:
    return BASE + off


def md() -> Cs:
    d = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    d.detail = False
    return d


def cmd_stores_214(raw: bytes) -> None:
    d = md()
    print("=== ldr/str imm 0x214 / 0x210 ===")
    for i in range(0, len(raw) - 4, 2):
        for insn in d.disasm(raw[i : i + 8], va(i)):
            if insn.address != va(i):
                continue
            if not (insn.mnemonic.startswith("str") or insn.mnemonic.startswith("ldr")):
                continue
            op = insn.op_str.lower()
            for imm in (0x214, 0x210, 532, 528):
                if f"#{imm}" in op or f"#0x{imm:x}" in op:
                    print(f"  {insn.address:#010x}  {insn.mnemonic:8} {insn.op_str}")
                    break


def cmd_tbb(raw: bytes) -> None:
    d = md()
    print("=== TBB / TBH ===")
    for i in range(0, len(raw) - 4, 2):
        for insn in d.disasm(raw[i : i + 6], va(i)):
            if insn.address != va(i):
                continue
            if insn.mnemonic in ("tbb", "tbh"):
                print(f"  {insn.address:#010x}  {insn.mnemonic:8} {insn.op_str}")


def cmd_ptr_runs(raw: bytes) -> None:
    end = BASE + len(raw)

    def is_thumb_ptr(w: int) -> bool:
        if w & 1 == 0:
            return False
        a = w & ~1
        return BASE + 0x20 <= a < end - 2

    print("=== Thumb-pointer runs (>=6) ===")
    i = 0
    while i < len(raw) - 4:
        if i % 4:
            i += 1
            continue
        run = []
        j = i
        while j + 4 <= len(raw):
            w = struct.unpack_from("<I", raw, j)[0]
            if not is_thumb_ptr(w):
                break
            run.append((va(j), w))
            j += 4
        if len(run) >= 6:
            print(f"\nrun @ {va(i):#010x}  n={len(run)}")
            for loc, w in run[:12]:
                print(f"  [{loc:#010x}] -> {w & ~1:#010x}")
        i = j if j > i else i + 4


def cmd_bl_to(raw: bytes, target: int) -> None:
    d = md()
    print(f"=== bl/b to {target:#010x} ===")
    n = 0
    for i in range(0, len(raw) - 4, 2):
        for insn in d.disasm(raw[i : i + 6], va(i)):
            if insn.address != va(i):
                continue
            if insn.mnemonic not in ("bl", "blx", "b", "b.w"):
                continue
            op = insn.op_str
            if not op.startswith("#"):
                continue
            try:
                dest = int(op[1:], 0)
            except ValueError:
                continue
            if dest == target or dest == target + 1:
                print(f"  {insn.address:#010x}  {insn.mnemonic} -> {dest:#x}")
                n += 1
    print(f"{n} hits")


def cmd_cmp_imm(raw: bytes) -> None:
    d = md()
    interesting = {7, 8, 9, 16, 0x12, 0x15, 21, 0x69, 98, 99, 100, 101}
    print("=== cmp/subs against interesting immediates ===")
    for i in range(0, len(raw) - 4, 2):
        for insn in d.disasm(raw[i : i + 6], va(i)):
            if insn.address != va(i):
                continue
            if insn.mnemonic not in ("cmp", "cmp.w", "subs", "sub.w"):
                continue
            tail = insn.op_str.split(",")[-1].strip().lower()
            for imm in interesting:
                if tail in (f"#{imm}", f"#0x{imm:x}"):
                    print(f"  {insn.address:#010x}  {insn.mnemonic:8} {insn.op_str}")
                    break


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "cmd",
        choices=["stores-214", "tbb", "ptr-runs", "bl-to", "cmp-imm"],
    )
    p.add_argument("addr", nargs="?")
    args = p.parse_args()
    raw = load()
    if args.cmd == "stores-214":
        cmd_stores_214(raw)
    elif args.cmd == "tbb":
        cmd_tbb(raw)
    elif args.cmd == "ptr-runs":
        cmd_ptr_runs(raw)
    elif args.cmd == "bl-to":
        if not args.addr:
            print("bl-to requires a hex address", file=sys.stderr)
            return 2
        cmd_bl_to(raw, int(args.addr, 0))
    else:
        cmd_cmp_imm(raw)
    return 0


if __name__ == "__main__":
    sys.exit(main())
