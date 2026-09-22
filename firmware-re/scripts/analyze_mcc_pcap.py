#!/usr/bin/env python3
"""List host SysEx from a KeyStep USBPcap (Identity / GET / productKey)."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

TSHARK = Path("/mnt/c/Program Files/Wireshark/tshark.exe")
PRODUCT_KEY = bytes.fromhex("f05a576e283c4e51f7")


def recon(ev: str) -> bytes:
    raw = bytes.fromhex(ev.replace(",", "").replace(":", "").replace(" ", ""))
    if 0xF7 in raw:
        raw = raw[: raw.index(0xF7) + 1]
    return raw


def classify(raw: bytes) -> str:
    if raw.startswith(bytes.fromhex("f07e7f0601")):
        return "IDENT"
    if raw == PRODUCT_KEY:
        return "PRODUCTKEY"
    if raw.startswith(bytes.fromhex("f000206b7f42010041")) and len(raw) >= 11:
        return f"GET {raw[9]:02x}"
    if raw.startswith(b"\xf0"):
        return f"OTHER {raw.hex()}"
    return f"RAW {raw.hex()}"


def tshark_host_out(pcap: Path) -> list[tuple[int, float, bytes]]:
    cmd = [
        str(TSHARK),
        "-r",
        str(pcap),
        "-Y",
        "usbaudio.midi.event && usb.endpoint_address == 0x02",
        "-T",
        "fields",
        "-e",
        "frame.number",
        "-e",
        "frame.time_relative",
        "-e",
        "usbaudio.midi.event",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        return []
    rows = []
    for line in r.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) < 3 or not parts[2].strip():
            continue
        rows.append((int(parts[0]), float(parts[1]), recon(parts[2])))
    return rows


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("pcap")
    args = p.parse_args()
    path = Path(args.pcap)
    if not path.is_file():
        print(f"missing {path}", file=sys.stderr)
        return 1
    rows = tshark_host_out(path)
    print(f"=== {path}  host OUT SysEx: {len(rows)} ===")
    gets: list[int] = []
    last_t = None
    for fn, t, raw in rows:
        kind = classify(raw)
        gap = ""
        if last_t is not None and t - last_t > 1.0:
            gap = f"  (+{t - last_t:.2f}s gap)"
        print(f"  {fn:6d}  {t:10.3f}  {kind:16s}  {raw.hex()}{gap}")
        if kind.startswith("GET "):
            gets.append(int(kind.split()[1], 16))
        last_t = t
    print(f"GET count {len(gets)} unique {len(set(gets))}")
    print("GET ids:", " ".join(f"{i:02x}" for i in gets))
    return 0


if __name__ == "__main__":
    sys.exit(main())
