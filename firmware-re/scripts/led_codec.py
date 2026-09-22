#!/usr/bin/env python3
"""Decode / re-encode Arturia KeyStep 37 .led update files.

The distributed file is uppercase hex-ASCII. After hex-decode, the payload
is a Gruss / auduchinok Huaxin (midiplus) segment stream, not a flat
Thumb image:

    [18-byte BE header] [record_length bytes] [12-byte footer]
    …
    [18-byte BE header] [record_length bytes] [24-byte last footer]
    plus 18-byte-only ``00 10 68 74`` fill records (1 KiB of 0xFF on device)

Each footer ends with a 16-bit additive checksum:

    (0x10000 - (sum(header[2:]) + sum(payload) + sum(footer[:-2])) & 0xFFFF)

The last payload's final two bytes are a second 16-bit checksum over
*every* segment payload (fill records count as 1024 × 0xFF), excluding
those two bytes themselves:

    (0x10000 - (sum(all_payloads[:-2]) & 0xFFFF))

Those two u16s are the bytes previously described as the ".led trailer"
(``95c4`` / ``65fe`` on 1.1.6.579; ``8777`` / ``c0fe`` on 1.0.4.179).
``65fe`` is the last footer's checksum; ``95c4`` is the program checksum
stored in the last payload.

Flash placement: header field ``offset`` is in 256-byte units. First
KS37 record is offset 64 → ``0x08004000``. Subsequent offsets step by 4
(1 KiB). The bootloader is not in this file.

Usage:
    python3 led_codec.py decode <in.led> <out.bin>
    python3 led_codec.py encode <in.bin> <out.led>
    python3 led_codec.py inspect <file.led-or-bin> [<file2> ...]
    python3 led_codec.py compare <a> <b>
    python3 led_codec.py roundtrip <in.led>
    python3 led_codec.py retarget <in.bin-or.led> <out.bin>
    python3 led_codec.py extract-flash <in.led-or-bin> <out.bin>
    python3 led_codec.py implant-page <in.led> <flash_va> <out.led>
    python3 led_codec.py mutate-test <in.led-or-bin>
"""
from __future__ import annotations

import argparse
import pathlib
import struct
import sys

HEADER_STRUCT = struct.Struct(">7sH7sH")
HEADER_LEN = 18
FOOTER12_LEN = 12
FOOTER24_LEN = 24
PAGE = 1024
FF_FILL_MAGIC = bytes.fromhex("00106874")
FLASH_BASE = 0x08000000
FLASH_UNIT = 256  # offset field is in this many bytes


class Segment:
    __slots__ = ("header", "payload", "footer", "is_fill")

    def __init__(
        self,
        header: bytes,
        payload: bytes,
        footer: bytes | None,
        is_fill: bool,
    ) -> None:
        if len(header) != HEADER_LEN:
            raise ValueError(f"header must be {HEADER_LEN} bytes")
        self.header = header
        self.payload = payload
        self.footer = footer
        self.is_fill = is_fill

    @property
    def offset(self) -> int:
        return HEADER_STRUCT.unpack(self.header)[1]

    @property
    def record_length(self) -> int:
        return HEADER_STRUCT.unpack(self.header)[3]

    @property
    def flash_addr(self) -> int:
        return FLASH_BASE + self.offset * FLASH_UNIT

    def checksum_input(self) -> bytes:
        if self.footer is None:
            return b""
        return self.header[2:] + self.payload + self.footer[:-2]

    def stored_checksum(self) -> int | None:
        if not self.footer or len(self.footer) < 2:
            return None
        return struct.unpack_from("<H", self.footer, len(self.footer) - 2)[0]

    def computed_checksum(self) -> int | None:
        if self.footer is None:
            return None
        return (0x10000 - (sum(self.checksum_input()) & 0xFFFF)) & 0xFFFF

    def with_recomputed_footer(self) -> Segment:
        if self.footer is None:
            return self
        csum = self.computed_checksum()
        assert csum is not None
        foot = self.footer[:-2] + struct.pack("<H", csum)
        return Segment(self.header, self.payload, foot, self.is_fill)


def _footer12_for_addr(flash_addr: int, template: bytes) -> bytes:
    """12-byte data footer with BE24 flash offset matching stock pages."""
    if len(template) != FOOTER12_LEN:
        raise ValueError("need a 12-byte footer template")
    foot = bytearray(template)
    foot[1:4] = (flash_addr & 0xFFFFFF).to_bytes(3, "big")
    return bytes(foot)


class LedImage:
    """Parsed Huaxin/midiplus .led payload (already hex-decoded)."""

    def __init__(self, segments: list[Segment]) -> None:
        if not segments:
            raise ValueError("empty image")
        self.segments = segments

    @classmethod
    def parse(cls, raw: bytes) -> LedImage:
        i = 0
        segs: list[Segment] = []
        n = len(raw)
        while i < n:
            if i + HEADER_LEN > n:
                raise ValueError(f"truncated header at {i}")
            hdr = raw[i : i + HEADER_LEN]
            if raw[i : i + 4] == FF_FILL_MAGIC:
                _p1, _off, _p2, rec = HEADER_STRUCT.unpack(hdr)
                segs.append(Segment(hdr, bytes([0xFF]) * PAGE, None, True))
                i += HEADER_LEN
                continue
            _p1, _off, _p2, rec = HEADER_STRUCT.unpack(hdr)
            i += HEADER_LEN
            if i + rec > n:
                raise ValueError(f"truncated payload at {i} rec={rec}")
            payload = raw[i : i + rec]
            i += rec
            # Last footer is 24 bytes when footer[6] == 0x0D (Gruss / gist).
            if i + 6 < n and raw[i + 6] == 0x0D:
                foot_len = min(FOOTER24_LEN, n - i)
            else:
                foot_len = min(FOOTER12_LEN, n - i)
            if i + foot_len > n:
                raise ValueError(f"truncated footer at {i}")
            foot = raw[i : i + foot_len]
            i += foot_len
            segs.append(Segment(hdr, payload, foot, False))
        if i != n:
            raise ValueError(f"unparsed tail {n - i} bytes")
        return cls(segs)

    def to_bytes(self) -> bytes:
        out = bytearray()
        for s in self.segments:
            out += s.header
            if s.is_fill:
                continue
            out += s.payload
            if s.footer:
                out += s.footer
        return bytes(out)

    def all_payloads(self) -> bytes:
        return b"".join(s.payload for s in self.segments)

    def stored_program_checksum(self) -> int:
        last = self._last_data()
        return last.payload[-2] | (last.payload[-1] << 8)

    def computed_program_checksum(self) -> int:
        blob = self.all_payloads()
        return (0x10000 - (sum(blob[:-2]) & 0xFFFF)) & 0xFFFF

    def _last_data(self) -> Segment:
        for s in reversed(self.segments):
            if not s.is_fill:
                return s
        raise ValueError("no data segments")

    def recompute(self) -> LedImage:
        """Rewrite program checksum + every footer checksum. Headers copied."""
        segs = [Segment(s.header, s.payload, s.footer, s.is_fill) for s in self.segments]
        last_i = next(i for i in range(len(segs) - 1, -1, -1) if not segs[i].is_fill)
        last = segs[last_i]
        body = last.payload[:-2]
        # Temporary last-2 so all_payloads() length is unchanged while we
        # sum; the formula excludes those two bytes.
        segs[last_i] = Segment(last.header, body + b"\x00\x00", last.footer, False)
        prog = (0x10000 - (sum(b"".join(s.payload for s in segs)[:-2]) & 0xFFFF)) & 0xFFFF
        last = segs[last_i]
        segs[last_i] = Segment(
            last.header,
            last.payload[:-2] + struct.pack("<H", prog),
            last.footer,
            False,
        )
        segs = [s.with_recomputed_footer() for s in segs]
        return LedImage(segs)

    def flash_map(self) -> dict[int, bytes]:
        """flash_addr → 1 KiB (or record_length) page."""
        pages: dict[int, bytes] = {}
        for s in self.segments:
            pages[s.flash_addr] = s.payload
        return pages

    def extract_flash(self, base: int = FLASH_BASE, fill: int = 0xFF) -> bytes:
        pages = self.flash_map()
        if not pages:
            return b""
        end = max(addr + len(data) for addr, data in pages.items())
        if end < base:
            raise ValueError("flash pages sit below base")
        out = bytearray([fill]) * (end - base)
        for addr, data in pages.items():
            off = addr - base
            out[off : off + len(data)] = data
        return bytes(out)

    def verify(self) -> list[str]:
        errors: list[str] = []
        for i, s in enumerate(self.segments):
            if s.is_fill:
                continue
            stored = s.stored_checksum()
            calc = s.computed_checksum()
            if stored != calc:
                errors.append(
                    f"seg[{i}] @ {s.flash_addr:#x} footer "
                    f"stored={stored:04X} calc={calc:04X}"
                )
        stored_p = self.stored_program_checksum()
        calc_p = self.computed_program_checksum()
        if stored_p != calc_p:
            errors.append(f"program checksum stored={stored_p:04X} calc={calc_p:04X}")
        for i, s in enumerate(self.segments):
            if s.is_fill or not s.footer or len(s.footer) < 4:
                continue
            foot_off = int.from_bytes(s.footer[1:4], "big")
            want = s.flash_addr & 0xFFFFFF
            if foot_off != want:
                errors.append(
                    f"seg[{i}] @ {s.flash_addr:#x} footer addr "
                    f"{foot_off:#x} != {want:#x}"
                )
        return errors

    def implant_page(self, flash_addr: int, page: bytes) -> LedImage:
        """Replace the 1 KiB page at flash_addr. Converts an FF-fill record
        into a real data segment (file grows). Checksums are not recomputed.

        Keep an existing data record's footer address fields. Copying the
        page-0 footer (``0b004000…``) onto a later page makes the bootloader
        program that payload over the app vector table at ``0x08004000``:
        Huaxin checksums still verify, the unit stays in ``0291``.
        """
        if len(page) != PAGE:
            raise ValueError(f"page must be {PAGE} bytes, got {len(page)}")
        template = next(s for s in self.segments if not s.is_fill)
        p1, _off, p2, _rec = HEADER_STRUCT.unpack(template.header)
        offset = (flash_addr - FLASH_BASE) // FLASH_UNIT
        header = HEADER_STRUCT.pack(p1, offset, p2, PAGE)
        foot_src = next(
            s for s in self.segments if s.footer and len(s.footer) == FOOTER12_LEN
        )
        segs: list[Segment] = []
        found = False
        for s in self.segments:
            if s.flash_addr != flash_addr:
                segs.append(s)
                continue
            found = True
            if s.is_fill:
                footer = _footer12_for_addr(flash_addr, foot_src.footer)
            else:
                footer = s.footer
            segs.append(Segment(header, page, footer, False))
        if not found:
            raise ValueError(f"no segment at {flash_addr:#x}")
        return LedImage(segs)


def is_hex_ascii(data: bytes) -> bool:
    if not data or len(data) % 2:
        return False
    return all(c in b"0123456789abcdefABCDEF" for c in data)


def decode_led(text: bytes) -> bytes:
    if not is_hex_ascii(text):
        raise ValueError("input is not hex-ASCII .led text")
    return bytes.fromhex(text.decode("ascii"))


def encode_led(raw: bytes) -> bytes:
    return raw.hex().upper().encode("ascii")


def load_any(path: pathlib.Path) -> tuple[bytes, str]:
    data = path.read_bytes()
    if is_hex_ascii(data):
        return decode_led(data), "led"
    return data, "bin"


def inspect(raw: bytes, label: str) -> None:
    img = LedImage.parse(raw)
    errs = img.verify()
    last = img._last_data()
    print(f"== {label} ==")
    print(f"  size              {len(raw)} bytes")
    print(f"  segments          {len(img.segments)} "
          f"({sum(1 for s in img.segments if not s.is_fill)} data, "
          f"{sum(1 for s in img.segments if s.is_fill)} ff-fill)")
    print(f"  first_header      {img.segments[0].header.hex()}")
    print(f"  first_flash       {img.segments[0].flash_addr:#010x}")
    print(f"  last_flash        {last.flash_addr:#010x}")
    print(f"  last_payload_tail {last.payload[-8:].hex()}")
    print(f"  last_footer       {last.footer.hex() if last.footer else '(none)'}")
    print(f"  program_u16       stored=0x{img.stored_program_checksum():04X}  "
          f"calc=0x{img.computed_program_checksum():04X}  "
          f"(on-wire bytes {last.payload[-2:].hex()})")
    if last.footer:
        print(f"  last_footer_u16   stored=0x{last.stored_checksum():04X}  "
              f"calc=0x{last.computed_checksum():04X}  "
              f"(on-wire bytes {last.footer[-2:].hex()})")
    print(f"  verify            {'OK' if not errs else 'FAIL'}")
    for e in errs[:12]:
        print(f"    {e}")


def compare(a: bytes, a_label: str, b: bytes, b_label: str) -> None:
    ia, ib = LedImage.parse(a), LedImage.parse(b)
    print(f"== compare {a_label} vs {b_label} ==")
    print(f"  sizes             {len(a)} vs {len(b)}  (delta {len(b) - len(a):+d})")
    print(f"  segments          {len(ia.segments)} vs {len(ib.segments)}")
    print(f"  first_header_same {ia.segments[0].header == ib.segments[0].header}")
    la, lb = ia._last_data(), ib._last_data()
    print(f"  program_u16       {ia.stored_program_checksum():04X} vs "
          f"{ib.stored_program_checksum():04X}")
    print(f"  last_footer_u16   {la.stored_checksum():04X} vs {lb.stored_checksum():04X}")
    print(f"  last_footer_mid   "
          f"{(la.footer[:-2].hex() if la.footer else '')} vs "
          f"{(lb.footer[:-2].hex() if lb.footer else '')}")


def recompute_trailer(raw: bytes) -> bytes:
    """Parse framed image, rewrite both checksum u16s, serialize."""
    return LedImage.parse(raw).recompute().to_bytes()


# Kept as a named alias so older notes that import TRAILER_ALGO still work.
TRAILER_ALGO = recompute_trailer


def _first_payload_byte_offset(img: LedImage) -> int:
    """File offset of byte 0 of the first data payload (after its header)."""
    return HEADER_LEN


def mutate_test(raw: bytes) -> int:
    """Flip one payload byte, rewrite checksums, prove both u16s and verify."""
    img = LedImage.parse(raw)
    before_p = img.stored_program_checksum()
    before_f = img._last_data().stored_checksum()
    framed = bytearray(raw)
    poke = _first_payload_byte_offset(img)
    framed[poke] ^= 0x01
    rebuilt = LedImage.parse(bytes(framed)).recompute()
    after_p = rebuilt.stored_program_checksum()
    after_f = rebuilt._last_data().stored_checksum()
    errs = rebuilt.verify()
    orig_rebuilt = img.recompute().to_bytes()
    identity = orig_rebuilt == raw
    print("== mutate-test ==")
    print(f"  poked file offset {poke} (first payload byte ^= 1)")
    print(f"  program_u16       {before_p:04X} -> {after_p:04X}  "
          f"({'changed' if after_p != before_p else 'UNCHANGED'})")
    print(f"  last_footer_u16   {before_f:04X} -> {after_f:04X}  "
          f"({'changed' if after_f != before_f else 'UNCHANGED — last page untouched'})")
    # The last footer only moves if the last payload (program checksum) moved,
    # which it always does when any payload byte changes.
    print(f"  verify_mutated    {'OK' if not errs else 'FAIL ' + '; '.join(errs)}")
    print(f"  identity_recompute {'OK' if identity else 'FAIL (recompute != original)'}")
    print("  meaning:")
    print("    program_u16     = last payload[-2:]  (Huaxin program checksum, LE)")
    print("    last_footer_u16 = last footer[-2:]   (per-segment additive checksum, LE)")
    return 0 if not errs and identity and after_p != before_p else 1


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("decode")
    d.add_argument("src")
    d.add_argument("dst")

    e = sub.add_parser("encode")
    e.add_argument("src")
    e.add_argument("dst")

    i = sub.add_parser("inspect")
    i.add_argument("files", nargs="+")

    c = sub.add_parser("compare")
    c.add_argument("a")
    c.add_argument("b")

    r = sub.add_parser("roundtrip")
    r.add_argument("src")

    t = sub.add_parser("retarget")
    t.add_argument("src")
    t.add_argument("dst")

    x = sub.add_parser("extract-flash")
    x.add_argument("src")
    x.add_argument("dst")

    imp = sub.add_parser("implant-page")
    imp.add_argument("src")
    imp.add_argument("flash_va")
    imp.add_argument("dst")
    imp.add_argument(
        "--poke",
        default="0:0xFE",
        help="offset:byte inside the 1 KiB page (default 0:0xFE)",
    )

    m = sub.add_parser("mutate-test")
    m.add_argument("src")

    args = p.parse_args()
    if args.cmd == "decode":
        raw = decode_led(pathlib.Path(args.src).read_bytes())
        pathlib.Path(args.dst).write_bytes(raw)
        print(f"wrote {len(raw)} bytes to {args.dst}")
        return 0
    if args.cmd == "encode":
        text = encode_led(pathlib.Path(args.src).read_bytes())
        pathlib.Path(args.dst).write_bytes(text)
        print(f"wrote {len(text)} bytes to {args.dst}")
        return 0
    if args.cmd == "inspect":
        for f in args.files:
            raw, _ = load_any(pathlib.Path(f))
            inspect(raw, f)
        return 0
    if args.cmd == "compare":
        a, _ = load_any(pathlib.Path(args.a))
        b, _ = load_any(pathlib.Path(args.b))
        compare(a, args.a, b, args.b)
        return 0
    if args.cmd == "roundtrip":
        src = pathlib.Path(args.src)
        original = src.read_bytes()
        raw = decode_led(original)
        back = encode_led(raw)
        ok = back == original
        print(f"hex roundtrip {'OK' if ok else 'FAIL'}: {src}")
        img = LedImage.parse(raw)
        rebuilt = img.recompute().to_bytes()
        print(f"checksum identity {'OK' if rebuilt == raw else 'FAIL'}")
        errs = img.verify()
        print(f"verify {'OK' if not errs else 'FAIL'}")
        if not ok:
            print(f"  case-insensitive match: {back.lower() == original.lower()}")
            return 0 if back.lower() == original.lower() and rebuilt == raw and not errs else 1
        return 0 if rebuilt == raw and not errs else 1
    if args.cmd == "retarget":
        raw, kind = load_any(pathlib.Path(args.src))
        out = recompute_trailer(raw)
        dst = pathlib.Path(args.dst)
        if kind == "led" or dst.suffix.lower() == ".led":
            dst.write_bytes(encode_led(out))
        else:
            dst.write_bytes(out)
        print(f"wrote {len(out)} framed bytes to {args.dst}")
        return 0
    if args.cmd == "extract-flash":
        raw, _ = load_any(pathlib.Path(args.src))
        flash = LedImage.parse(raw).extract_flash()
        pathlib.Path(args.dst).write_bytes(flash)
        print(f"wrote {len(flash)} bytes (base {FLASH_BASE:#x}) to {args.dst}")
        return 0
    if args.cmd == "implant-page":
        raw, _ = load_any(pathlib.Path(args.src))
        img = LedImage.parse(raw)
        va = int(args.flash_va, 0)
        pages = img.flash_map()
        if va not in pages:
            raise SystemExit(f"no page at {va:#x}")
        page = bytearray(pages[va])
        if len(page) != PAGE:
            page = (page + bytes([0xFF]) * PAGE)[:PAGE]
        off_s, byte_s = args.poke.split(":", 1)
        page[int(off_s, 0)] = int(byte_s, 0)
        out = img.implant_page(va, bytes(page)).recompute()
        errs = out.verify()
        dst = pathlib.Path(args.dst)
        if dst.suffix.lower() == ".led":
            dst.write_bytes(encode_led(out.to_bytes()))
        else:
            dst.write_bytes(out.to_bytes())
        print(f"implanted {va:#x}[{off_s}]={byte_s} -> {args.dst}")
        print(f"  segments {len(img.segments)} -> {len(out.segments)} "
              f"(fill converted to data if it was a hole)")
        print(f"  verify {'OK' if not errs else 'FAIL: ' + '; '.join(errs)}")
        return 0 if not errs else 1
    if args.cmd == "mutate-test":
        raw, _ = load_any(pathlib.Path(args.src))
        return mutate_test(raw)
    return 1


if __name__ == "__main__":
    sys.exit(main())
