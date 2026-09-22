#!/usr/bin/env python3
"""Name Test-20 / occupancy CCs from an amidi occupancy log.

    python3 occupancy_cc.py last LOG
    python3 occupancy_cc.py report LOG
"""
from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

# KeyStep37.json items[] ids + isolation-confirmed chord knobs.
CC_NAME = {
    16: "octm",
    17: "octp",
    18: "seqarp",
    19: "syncdip",
    21: "mode",
    64: "mod",
    65: "pitch",
    85: "hold",
    86: "shift",
    87: "rec",
    89: "stop",
    90: "play",
    96: "dcin",
    98: "type",
    99: "notes",
    100: "vel>notes",
    101: "strum",
    102: "rate",
    103: "tap",
    104: "timediv",
    105: "chord",
}

HEX = re.compile(r"\b([0-9A-Fa-f]{2})\b")


def hex_bytes(line: str) -> list[int]:
    s = line.strip()
    if s.startswith("#"):
        return []
    if ")" in line:
        line = line.split(")", 1)[1]
    return [int(x, 16) for x in HEX.findall(line)]


def parse_events(lines: list[str]) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(lines):
        raw = lines[i]
        bs = hex_bytes(raw)
        i += 1
        if not bs:
            continue
        st = bs[0]
        if st & 0xF0 == 0xB0 and len(bs) >= 3:
            cc, val = bs[1], bs[2]
            name = CC_NAME.get(cc, f"cc{cc}")
            ch = (st & 0x0F) + 1
            out.append(f"CC {cc} {name}={val} (ch{ch})")
        elif st & 0xF0 == 0x90 and len(bs) >= 3:
            note, vel = bs[1], bs[2]
            kind = "note-on" if vel else "note-off"
            out.append(f"{kind} {note} vel={vel} ch{(st & 0x0F) + 1}")
        elif st & 0xF0 == 0x80 and len(bs) >= 3:
            out.append(f"note-off {bs[1]} vel={bs[2]} ch{(st & 0x0F) + 1}")
        elif st == 0xF0:
            out.append("sysex " + " ".join(f"{b:02X}" for b in bs[:12]))
        elif st & 0xF0 == 0xC0 and len(bs) >= 2:
            out.append(f"program-change {bs[1]} ch{(st & 0x0F) + 1}")
    return out


def sections(text: str) -> list[tuple[str, list[str]]]:
    chunks: list[tuple[str, list[str]]] = []
    cur = "preamble"
    buf: list[str] = []
    for line in text.splitlines():
        if line.startswith("====="):
            if buf:
                chunks.append((cur, buf))
            cur = line.strip("= ").strip()
            buf = []
            continue
        buf.append(line)
    if buf:
        chunks.append((cur, buf))
    return chunks


def summarize(title: str, lines: list[str]) -> str:
    evs = parse_events(lines)
    if not evs:
        return f"{title}: no MIDI"
    counts = Counter(evs)
    # Keep first-seen order, collapse repeats.
    seen: list[str] = []
    for e in evs:
        if e not in seen:
            seen.append(e)
    parts = []
    for e in seen:
        n = counts[e]
        parts.append(e if n == 1 else f"{e} ×{n}")
    return f"{title}: " + "; ".join(parts)


def cmd_last(path: Path) -> int:
    secs = sections(path.read_text(errors="replace"))
    steps = [(t, b) for t, b in secs if t.startswith("STEP")]
    if not steps:
        print("no STEP yet")
        return 1
    title, buf = steps[-1]
    print(summarize(title, buf))
    return 0


def cmd_report(path: Path) -> int:
    secs = sections(path.read_text(errors="replace"))
    n = 0
    for title, buf in secs:
        if not title.startswith("STEP"):
            continue
        print(summarize(title, buf))
        n += 1
    if n == 0:
        print("no STEP sections")
        return 1
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("cmd", choices=["last", "report"])
    p.add_argument("log")
    args = p.parse_args()
    path = Path(args.log)
    if not path.exists():
        raise SystemExit(f"missing {path}")
    if args.cmd == "last":
        return cmd_last(path)
    return cmd_report(path)


if __name__ == "__main__":
    raise SystemExit(main())
