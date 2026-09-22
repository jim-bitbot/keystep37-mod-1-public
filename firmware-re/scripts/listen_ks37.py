#!/usr/bin/env python3
"""Listen to the KeyStep 37 and score stock / Euclidean / scale-chord.

The arp ignores injected notes — you press keys, this script only reads.

    python3 listen_ks37.py stock-chord --seconds 25
    python3 listen_ks37.py e0 --seconds 25
    python3 listen_ks37.py e1 --seconds 25
    python3 listen_ks37.py e3-off --seconds 20
    python3 listen_ks37.py e3-on --seconds 20
    python3 listen_ks37.py c1 --scale major --seconds 25
    python3 listen_ks37.py dump --seconds 10
    python3 listen_ks37.py score PATH  # replay a saved dump

Needs amidi on hw:0,0,0. Saves every capture under firmware-re/captures/listen/.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import statistics
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAP_DIR = ROOT / "firmware-re" / "captures" / "listen"
NOTE_ON = 0x90
NOTE_OFF = 0x80
CLOCK = 0xF8

# Pitch-class masks, bit 0 = C. Chromatic = 0x0FFF.
SCALES = {
    "chromatic": 0x0FFF,
    "major": 0x0AB5,  # C D E F G A B
    "minor": 0x05AD,  # C D Eb F G Ab Bb
    "dorian": 0x06AD,
    "mixolydian": 0x09B5,
}

# E0 3-in-8: hits at 0,3,6 → inter-hit steps 3,3,2.
E0_IOI = (3, 3, 2)
STRUM_S = 0.085


def amidi_bin() -> list[str]:
    r = subprocess.run(["amidi", "-l"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return ["amidi"] if r.returncode == 0 else ["sudo", "amidi"]


def amidi_port() -> str:
    r = subprocess.run(amidi_bin() + ["-l"], capture_output=True, text=True)
    for line in r.stdout.splitlines():
        if "KeyStep" in line or "A37" in line or "hw:" in line:
            parts = line.split()
            for p in parts:
                if p.startswith("hw:"):
                    return p
    raise SystemExit("no amidi port — attach the KeyStep (keystep-see.sh)")


def free_rawmidi() -> None:
    if Path("/dev/snd/midiC0D0").exists():
        subprocess.run(
            ["sudo", "fuser", "-k", "/dev/snd/midiC0D0"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(0.15)


class Ev:
    __slots__ = ("t", "st", "data")

    def __init__(self, t: float, st: int, data: bytes):
        self.t = t
        self.st = st
        self.data = data

    @property
    def note(self) -> int:
        return self.data[1] if len(self.data) > 1 else 0

    @property
    def vel(self) -> int:
        return self.data[2] if len(self.data) > 2 else 0


# amidi -T realtime: "1789942138.159725976) 90 2F 3E"
_TS = re.compile(
    r"^(?:(\d{2}):(\d{2}):(\d{2}\.\d+)\s+)?(?:(\d+\.\d+)\)?\s+)?([0-9A-Fa-f]{2}(?:\s+[0-9A-Fa-f]{2})*)\s*$"
)


def parse_amidi_line(line: str, t0: list[float | None]) -> Ev | None:
    line = line.strip()
    if not line:
        return None
    m = _TS.match(line)
    if not m:
        if ")" in line:
            line = line.split(")", 1)[-1].strip()
            m = _TS.match(line)
        if not m:
            return None
    h, mi, hms, rawsec, hx = m.groups()
    raw = bytes(int(x, 16) for x in hx.split())
    if rawsec is not None:
        t = float(rawsec)
    elif hms is not None:
        t = int(h) * 3600 + int(mi) * 60 + float(hms)
    else:
        now = time.monotonic()
        if t0[0] is None:
            t0[0] = now
        t = now - t0[0]
    if t0[0] is None:
        t0[0] = t
    return _ev_from_raw(t - t0[0], raw)


def _ev_from_raw(t: float, raw: bytes) -> Ev | None:
    if not raw:
        return None
    return Ev(t, raw[0], raw)


def capture(seconds: float, clocks: bool, dest: Path) -> list[Ev]:
    port = amidi_port()
    free_rawmidi()
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = amidi_bin() + ["-p", port, "-d", "-T", "realtime"]
    if clocks:
        cmd.append("-c")
    print(f"listening {port} for {seconds:.0f}s → {dest}", flush=True)
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    evs: list[Ev] = []
    t0: list[float | None] = [None]
    deadline = time.monotonic() + seconds
    assert proc.stdout is not None
    raw_lines: list[str] = []
    try:
        while time.monotonic() < deadline:
            line = proc.stdout.readline()
            if not line:
                if proc.poll() is not None:
                    break
                continue
            raw_lines.append(line)
            ev = parse_amidi_line(line, t0)
            if ev is None:
                continue
            evs.append(ev)
            if ev.st & 0xF0 == NOTE_ON and ev.vel:
                print(f"  +{ev.t:7.3f}  note {ev.note:3d} vel {ev.vel:3d}", flush=True)
            elif ev.st & 0xF0 == NOTE_OFF or (ev.st & 0xF0 == NOTE_ON and ev.vel == 0):
                print(f"  +{ev.t:7.3f}  off  {ev.note:3d}", flush=True)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=1)
        except subprocess.TimeoutExpired:
            proc.kill()
        dest.write_text("".join(raw_lines))
    print(f"captured {len(evs)} events ({sum(1 for e in evs if e.st & 0xF0 == NOTE_ON and e.vel)} note-ons)", flush=True)
    return evs


def load_dump(path: Path) -> list[Ev]:
    t0: list[float | None] = [None]
    evs = []
    for line in path.read_text().splitlines():
        ev = parse_amidi_line(line, t0)
        if ev:
            evs.append(ev)
    return evs


def note_ons(evs: list[Ev]) -> list[Ev]:
    return [e for e in evs if e.st & 0xF0 == NOTE_ON and e.vel]


def chord_bursts(ons: list[Ev], window: float = STRUM_S) -> list[list[Ev]]:
    if not ons:
        return []
    bursts: list[list[Ev]] = [[ons[0]]]
    for e in ons[1:]:
        if e.t - bursts[-1][-1].t <= window:
            bursts[-1].append(e)
        else:
            bursts.append([e])
    return bursts


def pc(n: int) -> int:
    return n % 12


def in_scale(n: int, mask: int) -> bool:
    return bool(mask & (1 << pc(n)))


def fmt_notes(ns: list[int]) -> str:
    names = "C C# D D# E F F# G G# A A# B".split()
    return " ".join(f"{n}({names[n % 12]})" for n in ns)


def score_stock_chord(evs: list[Ev], scale: str) -> int:
    mask = SCALES[scale]
    ons = note_ons(evs)
    bursts = [b for b in chord_bursts(ons) if len(b) >= 2]
    print(f"=== stock-chord / {scale} mask {mask:#06x} ===")
    if not bursts:
        print("FAIL  no 2+ note burst. Chord ON (Shift+Hold, orange), play one key.")
        return 1
    rc = 0
    chromatic_extras = 0
    for i, b in enumerate(bursts, 1):
        notes = sorted({e.note for e in b})
        root = min(notes)
        iv = [n - root for n in notes]
        extras = [n for n in notes if n != root]
        out = [n for n in extras if not in_scale(n, mask)]
        print(f"  burst {i}: {fmt_notes(notes)}  iv {iv}")
        if scale != "chromatic" and out:
            print(f"           extras OFF scale: {fmt_notes(out)}  → stock intervals (no snap)")
            chromatic_extras += 1
        elif extras:
            print("           extras ON scale")
    if scale == "chromatic":
        print("  chromatic scale: snap test is inconclusive (everything is in-scale)")
        return 0
    if chromatic_extras:
        print("VERDICT  extras do NOT snap — C1 must hook after noteval")
    else:
        print("VERDICT  extras already in-scale (lucky Type/root, or already snapped)")
        print("         replay on C (MIDI 48/60) with Type = minor triad if this is stock")
    return rc


def _mono_hits(ons: list[Ev]) -> list[Ev]:
    """Collapse strum/poly same-step into one hit (first note of each burst)."""
    return [b[0] for b in chord_bursts(ons, window=STRUM_S)]


def _ioi_times(hits: list[Ev]) -> list[float]:
    return [hits[i + 1].t - hits[i].t for i in range(len(hits) - 1)]


def _ioi_steps(hits: list[Ev], base: float | None = None) -> tuple[list[int], float] | None:
    if len(hits) < 6:
        return None
    iois = _ioi_times(hits)
    # Step guess: smallest consistent IOI, ignoring tiny jitter.
    if base is None:
        compact = [x for x in iois if x >= 0.04]
        if not compact:
            return None
        base = statistics.median(sorted(compact)[: max(3, len(compact) // 3)])
    if base < 0.04:
        return None
    steps = [max(1, round(x / base)) for x in iois]
    return steps, base


def _e0_grid(hits: list[Ev]) -> tuple[list[int], float] | None:
    """Naive shortest-IOI as 1 step mis-scores 3-in-8 as 2,2,1 / every-step.

    Hits at 0,3,6 have wall IOIs 3T,3T,2T. Taking 2T as the unit yields
    2,2,1; 3T/2T ≈ 1.49 then rounds to 1, so a clean 3-in-8 dump can
    print as 90–100% every-step. If ≥20% of gaps sit in the 1.3–1.7×
    band, retry T = base/2 and base/3 and keep the best 3-in-8 grid.
    A true every-step dump has no 1.5× band, so it stays even.
    """
    parsed = _ioi_steps(hits)
    if parsed is None:
        return None
    steps0, naive = parsed
    iois = _ioi_times(hits)
    mid = sum(1 for x in iois if 1.3 <= x / naive <= 1.7) / len(iois)
    if mid < 0.2:
        return steps0, naive
    best = (steps0, naive)
    best_eu = _rotate_match(steps0, E0_IOI)
    for d in (2, 3):
        got = _ioi_steps(hits, naive / d)
        if got is None:
            continue
        eu = _rotate_match(got[0], E0_IOI)
        if eu > best_eu:
            best_eu = eu
            best = got
    return best


def _rotate_match(got: list[int], pat: tuple[int, ...]) -> float:
    if not got or not pat:
        return 0.0
    best = 0.0
    for off in range(len(pat)):
        rot = pat[off:] + pat[:off]
        ok = sum(1 for i, g in enumerate(got) if g == rot[i % len(rot)])
        best = max(best, ok / len(got))
    return best


def score_e0(evs: list[Ev]) -> int:
    hits = _mono_hits(note_ons(evs))
    print("=== E0 3-in-8 (expect IOI steps 3,3,2 repeating) ===")
    print(f"  hits {len(hits)}  notes {fmt_notes([h.note for h in hits[:24]])}")
    parsed = _e0_grid(hits)
    if parsed is None:
        print("FAIL  need ≥6 Pattern/Seq hits. Arp+Pattern, Hold a key, Play solid.")
        return 1
    steps, base = parsed
    eu = _rotate_match(steps, E0_IOI)
    even = sum(1 for s in steps if s == 1) / len(steps)
    iois = _ioi_times(hits)
    print(f"  IOI ms { [round(x * 1000) for x in iois[:24]] }")
    print(f"  step ≈ {base * 1000:.0f} ms   IOI-steps {steps[:24]}")
    print(f"  match 3-in-8 {eu:.0%}   match every-step {even:.0%}")
    if eu >= 0.7 and eu > even + 0.15:
        print("VERDICT  E0 PASS — 3-in-8 restripe is audible")
        return 0
    if even >= 0.7:
        print("VERDICT  E0 FAIL — still stock density (every step)")
        return 1
    print("VERDICT  E0 UNCLEAR — not 3-in-8 and not even. Check Mode=Pattern, Rate steady.")
    return 1


def score_e1(evs: list[Ev]) -> int:
    hits = _mono_hits(note_ons(evs))
    print("=== E1 hits-from-slot (expect even IOI, density ≠ 3/8 unless slot has 3 gates) ===")
    parsed = _ioi_steps(hits)
    if parsed is None:
        print("FAIL  need ≥6 hits.")
        return 1
    steps, base = parsed
    eu = _rotate_match(steps, E0_IOI)
    even = sum(1 for s in steps if s == 1) / len(steps)
    print(f"  step ≈ {base * 1000:.0f} ms   IOI-steps {steps[:24]}")
    print(f"  match 3-in-8 {eu:.0%}   match every-step {even:.0%}")
    # E1 still always-on Euclidean, but k = gated count. Factory Pattern
    # 16 gated steps → 16-in-16 = every step (same as stock). A slot with
    # 4 gates in 8 → 4-in-8 (2,2,2,2). Pass if we got a stable cycle.
    cyc = _guess_cycle(steps)
    print(f"  inferred cycle {cyc}")
    if cyc and len(cyc) >= 2:
        print("VERDICT  E1 PASS — stable restripe cycle (not random)")
        return 0
    if even >= 0.85:
        print("VERDICT  E1 OK-ish — every-step (slot fully gated, k=n)")
        return 0
    print("VERDICT  E1 UNCLEAR")
    return 1


def _guess_cycle(steps: list[int]) -> tuple[int, ...] | None:
    for n in range(2, min(9, len(steps) // 2 + 1)):
        pat = tuple(steps[:n])
        if _rotate_match(steps, pat) >= 0.8:
            return pat
    return None


def score_e3(evs: list[Ev], armed: bool) -> int:
    hits = _mono_hits(note_ons(evs))
    print(f"=== E3 {'ON (Shift+1)' if armed else 'OFF (default / Shift+2)'} ===")
    parsed = _e0_grid(hits) if armed else _ioi_steps(hits)
    if parsed is None:
        print("FAIL  need ≥6 hits.")
        return 1
    steps, base = parsed
    eu = _rotate_match(steps, E0_IOI)
    even = sum(1 for s in steps if s == 1) / len(steps)
    print(f"  step ≈ {base * 1000:.0f} ms   IOI-steps {steps[:24]}")
    print(f"  match 3-in-8 {eu:.0%}   match every-step {even:.0%}")
    if armed:
        if eu >= 0.65:
            print("VERDICT  E3 ON PASS — Euclidean after Shift+1")
            return 0
        print("VERDICT  E3 ON FAIL — not 3-in-8 (E1 density may differ; still should restripe)")
        return 1
    if even >= 0.7 or eu < 0.4:
        print("VERDICT  E3 OFF PASS — stock gates (boot / Shift+2)")
        return 0
    print("VERDICT  E3 OFF FAIL — still looks Euclidean")
    return 1


def score_c1(evs: list[Ev], scale: str) -> int:
    mask = SCALES[scale]
    ons = note_ons(evs)
    bursts = [b for b in chord_bursts(ons) if len(b) >= 2]
    print(f"=== C1 scale-chord / {scale} ===")
    if not bursts:
        print("FAIL  no chord burst. Chord ON, non-chromatic scale, one root.")
        return 1
    bad = 0
    for i, b in enumerate(bursts, 1):
        notes = sorted({e.note for e in b})
        out = [n for n in notes if not in_scale(n, mask)]
        print(f"  burst {i}: {fmt_notes(notes)}")
        if out:
            print(f"           OFF scale {fmt_notes(out)}")
            bad += 1
        else:
            print("           all in scale")
    if scale == "chromatic":
        print("VERDICT  C1 chromatic = stock (expected)")
        return 0
    if bad == 0:
        print("VERDICT  C1 PASS — extras stayed in scale")
        return 0
    print("VERDICT  C1 FAIL — extras still chromatic")
    return 1


def score_c2(evs: list[Ev]) -> int:
    ons = note_ons(evs)
    bursts = [b for b in chord_bursts(ons) if len(b) >= 2]
    print("=== C2 flavour (two voicings: Shift+Type low then high) ===")
    if len(bursts) < 2:
        print("FAIL  play the same root twice: once at Type/flavour 0, once above 64.")
        return 1
    shapes = [tuple(sorted({e.note - min(x.note for x in b) for e in b})) for b in bursts]
    print(f"  shapes {shapes}")
    uniq = list(dict.fromkeys(shapes))
    if len(uniq) >= 2:
        print("VERDICT  C2 PASS — voicing changed after Shift+Type")
        return 0
    print("VERDICT  C2 UNCLEAR — same shape both times (knob not moved, or combo ignored)")
    return 1


def prompt(cmd: str, scale: str) -> None:
    print()
    print("— you do this —")
    common = "KeyStep on USB, this WSL attached (Gate 0). I only listen."
    if cmd == "stock-chord":
        print(common)
        print("1. Seq/Arp = Arp. Chord ON (Shift+Hold, orange).")
        print(f"2. Scale = {scale} (Shift+33–37 / Shift+C4). Not Chromatic.")
        print("3. Type = minor triad if you can (root +3 +7).")
        print("4. Play C (lowest C or C4). Hold ~1s. Repeat once.")
    elif cmd == "e0":
        print(common)
        print("1. After MCC e0_euclid_3in8.led, Gate 0.")
        print("2. Arp, Mode = Pattern (panel label; internal mode 6, not 7 -")
        print("   corrected 2026-09-22, see address-catalog.md). Hold ON.")
        print("   Play solid (not blink).")
        print("3. Hold one key ~8 seconds. Do not change Rate.")
        print("   Optional: listen_ks37.py e0 --clocks  (F8 makes the step grid unambiguous).")
    elif cmd == "e1":
        print(common)
        print("1. After PC_1 flash of e1b_pitchgate_hits.led (not old e1).")
        print("   Pattern + one key is often every-step (k=n). That is OK.")
    elif cmd == "e3-off":
        print(common)
        print("1. After PC_1 flash of e3b_pitchgate_shift.led (not old e3).")
        print("2. Pattern + Hold one key ~6s. Should sound like stock (every-step).")
    elif cmd == "e3-on":
        print(common)
        print("1. After e3b: Hold Shift, tap the lowest key (C2). Release Shift.")
        print("2. Pattern + Hold one key ~6s. Should restripe 3,3,2.")
    elif cmd == "c1":
        print(common)
        print(f"1. After MCC c1. Chord ON. Scale = {scale}. Play C twice.")
    elif cmd == "c2":
        print(common)
        print("1. After MCC c2. Chord ON. Hold Shift, turn Type to 0, play C.")
        print("2. Hold Shift, turn Type past halfway, play C again.")
    elif cmd == "dump":
        print(common)
        print("Play anything.")
    print()


def score(cmd: str, evs: list[Ev], scale: str) -> int:
    if cmd == "stock-chord":
        return score_stock_chord(evs, scale)
    if cmd == "e0":
        return score_e0(evs)
    if cmd == "e1":
        return score_e1(evs)
    if cmd == "e3-off":
        return score_e3(evs, armed=False)
    if cmd == "e3-on":
        return score_e3(evs, armed=True)
    if cmd == "c1":
        return score_c1(evs, scale)
    if cmd == "c2":
        return score_c2(evs)
    ons = note_ons(evs)
    print(f"=== dump  {len(ons)} note-ons ===")
    for e in ons[:40]:
        print(f"  +{e.t:7.3f}  {e.note:3d}")
    return 0 if ons else 1


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "cmd",
        choices=["stock-chord", "e0", "e1", "e3-off", "e3-on", "c1", "c2", "dump", "score"],
    )
    p.add_argument("dump", nargs="?", help="saved dump for score")
    p.add_argument("--seconds", type=float, default=25)
    p.add_argument("--scale", default="major", choices=list(SCALES))
    p.add_argument("--clocks", action="store_true")
    args = p.parse_args()
    if args.cmd == "score":
        if not args.dump:
            raise SystemExit("score needs a dump path")
        path = Path(args.dump)
        evs = load_dump(path)
        # Infer cmd from filename prefix if possible.
        name = path.name
        guess = "dump"
        for key in ("stock-chord", "e3-off", "e3-on", "e0", "e1", "c1", "c2"):
            if name.startswith(key):
                guess = key
                break
        return score(guess, evs, args.scale)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    dest = CAP_DIR / f"{args.cmd}-{stamp}.txt"
    prompt(args.cmd, args.scale)
    evs = capture(args.seconds, args.clocks, dest)
    rc = score(args.cmd, evs, args.scale)
    print(f"dump {dest}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
