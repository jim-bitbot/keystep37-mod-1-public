#!/usr/bin/env python3
"""Assemble ks37_patch.S, implant at 0x0801F400, retarget, encode .led."""
from __future__ import annotations

import argparse
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from led_codec import PAGE, LedImage, decode_led, encode_led  # noqa: E402

ASM = ROOT / "firmware-re" / "patches" / "ks37_patch.S"
STOCK = ROOT / "firmware-re" / "recovery" / "keystep37_1.1.6.579_stock.led"
OUT_DIR = ROOT / "firmware-re" / "firmware-images" / "rebuild"
PAGE_VA = 0x0801F400
FLASH_BASE = 0x08000000

SITES = {
    "gate": (0x08013F62, 0x08013FDE, 0x080141D2),
    "pitch_gate": (0x08013EC2,),
    "noteval": (0x0801BAAC, 0x0801B9F2, 0x0801BB24),
    "shift": (0x0801B75A,),
    "type": (0x0800F4B8, 0x0800F54E, 0x0800F6FC),
}

LEVELS = {
    "e0": dict(FEAT_LATCH=0, FEAT_HITS_SLOT=0, FEAT_SHIFT=0, FEAT_CHORD=0, FEAT_FLAVOUR=0),
    "e1": dict(FEAT_LATCH=0, FEAT_HITS_SLOT=1, FEAT_SHIFT=0, FEAT_CHORD=0, FEAT_FLAVOUR=0),
    "e3": dict(FEAT_LATCH=1, FEAT_HITS_SLOT=1, FEAT_SHIFT=1, FEAT_CHORD=0, FEAT_FLAVOUR=0),
    "c1": dict(FEAT_LATCH=1, FEAT_HITS_SLOT=1, FEAT_SHIFT=1, FEAT_CHORD=1, FEAT_FLAVOUR=0),
    "c2": dict(FEAT_LATCH=1, FEAT_HITS_SLOT=1, FEAT_SHIFT=1, FEAT_CHORD=1, FEAT_FLAVOUR=1),
    # 2026-09-22: isolated test of the pitch-byte gate (voice-0 master gate
    # inside play_time_step, 0x08013ec2), NOT the seq_step_gate redirect the
    # levels above use. USE_GATE_HOOK=0 means the three seq_step_gate call
    # sites are left as stock for this level, so this is a clean test of
    # exactly one mechanism, not stacked with the earlier (confirmed
    # ineffective for note-gating) approach.
    "e0b": dict(
        FEAT_LATCH=0, FEAT_HITS_SLOT=0, FEAT_SHIFT=0, FEAT_CHORD=0,
        FEAT_FLAVOUR=0, FEAT_PITCH_GATE=1, USE_GATE_HOOK=0,
    ),
    # E1 on the working pitch-byte gate. Old "e1" still redirects
    # seq_step_gate (no audible note gate). Do not flash that image.
    "e1b": dict(
        FEAT_LATCH=0, FEAT_HITS_SLOT=1, FEAT_SHIFT=0, FEAT_CHORD=0,
        FEAT_FLAVOUR=0, FEAT_PITCH_GATE=1, USE_GATE_HOOK=0,
    ),
    # Latch on the working pitch-gate. Armed = e0b 3-in-8, not e1b
    # hits-from-slot (Pattern one-key is k=n, so latch would be silent).
    "e3b": dict(
        FEAT_LATCH=1, FEAT_HITS_SLOT=0, FEAT_SHIFT=1, FEAT_CHORD=0,
        FEAT_FLAVOUR=0, FEAT_PITCH_GATE=1, USE_GATE_HOOK=0,
    ),
}

NAMES = {
    "e0": "e0_euclid_3in8.led",
    "e1": "e1_euclid_hits.led",
    "e3": "e3_euclid_shift.led",
    "c1": "c1_scale_chord.led",
    "c2": "c2_shift_type.led",
    "e0b": "e0b_pitchgate_3in8.led",
    "e1b": "e1b_pitchgate_hits.led",
    "e3b": "e3b_pitchgate_shift.led",
}


def thumb_bl(src: int, dst: int) -> bytes:
    off = dst - (src + 4)
    if off % 2:
        raise ValueError(f"unaligned bl {src:#x}->{dst:#x}")
    imm32 = off
    if not (-(1 << 24) <= imm32 < (1 << 24)):
        raise ValueError(f"bl out of range {src:#x}->{dst:#x}")
    s = (imm32 >> 24) & 1
    i1 = (imm32 >> 23) & 1
    i2 = (imm32 >> 22) & 1
    imm10 = (imm32 >> 12) & 0x3FF
    imm11 = (imm32 >> 1) & 0x7FF
    j1 = ((~i1) & 1) ^ s
    j2 = ((~i2) & 1) ^ s
    hw1 = 0xF000 | (s << 10) | imm10
    hw2 = 0xD000 | (j1 << 13) | (1 << 12) | (j2 << 11) | imm11
    return struct.pack("<HH", hw1, hw2)


def verify_bl_encoder() -> None:
    got = thumb_bl(0x0801BAAC, 0x0801C3CA)
    exp = bytes.fromhex("00f08dfc")
    if got != exp:
        raise SystemExit(f"bl encoder mismatch {got.hex()} != {exp.hex()}")


def nm_symbols(elf: Path) -> dict[str, int]:
    r = subprocess.run(
        ["arm-none-eabi-nm", str(elf)],
        capture_output=True,
        text=True,
        check=True,
    )
    out = {}
    for line in r.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 3:
            out[parts[2]] = int(parts[0], 16)
    return out


def assemble(feats: dict[str, int]) -> tuple[bytes, dict[str, int]]:
    defs = []
    for k, v in feats.items():
        defs += [f"--defsym", f"{k}={v}"]
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        obj = td / "p.o"
        elf = td / "p.elf"
        binp = td / "p.bin"
        ld = ROOT / "firmware-re" / "patches" / "ks37_patch.ld"
        subprocess.run(
            ["arm-none-eabi-as", "-mthumb", "-mcpu=cortex-m3", *defs, "-o", str(obj), str(ASM)],
            check=True,
        )
        subprocess.run(
            ["arm-none-eabi-ld", "-T", str(ld), "-o", str(elf), str(obj)],
            check=True,
        )
        subprocess.run(
            ["arm-none-eabi-objcopy", "-O", "binary", str(elf), str(binp)],
            check=True,
        )
        raw = binp.read_bytes()
        syms = nm_symbols(elf)
    if len(raw) > PAGE:
        raise SystemExit(f"patch {len(raw)} > {PAGE}")
    page = raw + bytes([0xFF]) * (PAGE - len(raw))
    return page, syms


def patch_flash(flash: bytearray, level: str, syms: dict[str, int]) -> None:
    if LEVELS[level].get("USE_GATE_HOOK", 1):
        wrap = syms["euclid_wrap"]
        for va in SITES["gate"]:
            flash[va - FLASH_BASE : va - FLASH_BASE + 4] = thumb_bl(va, wrap)
    if LEVELS[level].get("FEAT_PITCH_GATE"):
        hook = syms["pitch_gate_wrap"]
        for va in SITES["pitch_gate"]:
            flash[va - FLASH_BASE : va - FLASH_BASE + 4] = thumb_bl(va, hook)
    if LEVELS[level]["FEAT_SHIFT"]:
        hook = syms["shift_note_hook"]
        for va in SITES["shift"]:
            flash[va - FLASH_BASE : va - FLASH_BASE + 4] = thumb_bl(va, hook)
    if LEVELS[level]["FEAT_CHORD"]:
        hook = syms["noteval_then_snap"]
        for va in SITES["noteval"]:
            flash[va - FLASH_BASE : va - FLASH_BASE + 4] = thumb_bl(va, hook)
    if LEVELS[level]["FEAT_FLAVOUR"]:
        hook = syms["type_strb_hook"]
        for va in SITES["type"]:
            flash[va - FLASH_BASE : va - FLASH_BASE + 4] = thumb_bl(va, hook)


def build(level: str) -> Path:
    verify_bl_encoder()
    feats = LEVELS[level]
    page, syms = assemble(feats)
    print(f"=== {level} symbols ===")
    for n, a in sorted(syms.items(), key=lambda x: x[1]):
        print(f"  {a:#010x}  {n}")
    raw = decode_led(STOCK.read_bytes())
    img = LedImage.parse(raw)
    flash = bytearray(img.extract_flash())
    flash[PAGE_VA - FLASH_BASE : PAGE_VA - FLASH_BASE + PAGE] = page
    patch_flash(flash, level, syms)
    implanted = img.implant_page(PAGE_VA, bytes(page)).recompute()
    # implant_page only writes the hole; overlay hook bytes via extract, rebuild
    # Re-parse from a flash splice: write patched pages back through implant of 0x0801F400
    # plus direct overwrite of hook sites in the framed image.
    framed = bytearray(implanted.to_bytes())
    # Simpler path: extract-flash after implant, apply hooks on that flash, then
    # cut back is hard. Apply hooks on the framed stream by VA→segment.
    out_img = _splice_hooks(implanted, flash)
    errs = out_img.verify()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    dest = OUT_DIR / NAMES[level]
    dest.write_bytes(encode_led(out_img.to_bytes()))
    print(f"wrote {dest}  {dest.stat().st_size} bytes  verify {'OK' if not errs else errs}")
    if errs:
        raise SystemExit(1)
    return dest


def _splice_hooks(img: LedImage, flash: bytes) -> LedImage:
    """Copy hook-site bytes from patched flash into implanted image pages."""
    pages = img.flash_map()
    hook_pages = {PAGE_VA}
    for group in SITES.values():
        for va in group:
            hook_pages.add(va & ~0x3FF)
    dirty: dict[int, bytearray] = {}
    for page_va in hook_pages:
        if page_va not in pages:
            continue
        src = flash[page_va - FLASH_BASE : page_va - FLASH_BASE + PAGE]
        if src != pages[page_va]:
            dirty[page_va] = bytearray(src)
    out = img
    for pva, page in dirty.items():
        out = out.implant_page(pva, bytes(page))
        print(f"  spliced page {pva:#x}")
    return out.recompute()


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("level", choices=list(LEVELS))
    args = p.parse_args()
    dest = build(args.level)
    win = Path("/mnt/c/Users/jimcu/KeystepFlash")
    if win.is_dir():
        target = win / dest.name
        target.write_bytes(dest.read_bytes())
        print(f"copied {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
