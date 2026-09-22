#!/usr/bin/env python3
"""Send a KeyStep 37 .led over the stock USB-MIDI update path.

Wire format (from keystep37_firmware_update.pcap):

  1. App PID 1c75:0219:  productKey  F0 5A 57 6E 28 3C 4E 51 F7
  2. Device re-enumerates as bootloader 1c75:0291
  3. productKey again; device replies F0 51 F7
  4. Stream the .led hex-ASCII as F0 + slice + F7 (22-byte slices)
  5. Device replies F0 77 F7 and returns to 1c75:0219

Do not use --confirm unless a full stock (or intended) image will follow
the first productKey. A probe-only unlock can leave the unit in the
bootloader.

Usage:
    python3 ks37_flash.py --dry-run <file.led>
    python3 ks37_flash.py --already-bootloader --confirm YES-FLASH <file.led>
"""
from __future__ import annotations

import argparse
import os
import select
import subprocess
import sys
import threading
import time
from pathlib import Path

from mcc_unlock_prelude import GET_IDS, IDENT, PRODUCT_KEY, get_sysex
ACK_UNLOCK = bytes.fromhex("F051F7")
ACK_DONE = bytes.fromhex("F077F7")
VID_APP = "1c75:0219"
VID_BL = "1c75:0291"
CHUNK = 22
USBIPD = Path("/mnt/c/Program Files/usbipd-win/usbipd.exe")
USBIPD_HINT = """
Bootloader 1c75:0291 is not in this WSL. On Windows (elevated PowerShell):
  usbipd list
  usbipd bind --busid <BUSID_0291>
  usbipd attach --wsl --busid <BUSID_0291> --auto-attach
Then re-run. Do not send productKey again if the unit is already 0291 —
use --already-bootloader.
"""
PRODUCT_KEY_AMIDI = "F0 5A 57 6E 28 3C 4E 51 F7"


def lsusb_has(vid_pid: str) -> bool:
    r = subprocess.run(
        ["lsusb", "-d", vid_pid],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return r.returncode == 0


def amidi_bin() -> list[str]:
    r = subprocess.run(["amidi", "-l"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return ["amidi"] if r.returncode == 0 else ["sudo", "amidi"]


def amidi_port() -> str | None:
    r = subprocess.run(amidi_bin() + ["-l"], capture_output=True, text=True)
    for line in r.stdout.splitlines():
        if "hw:" in line:
            return line.split()[1]
    return None


def amidi_send(port: str, hex_msg: str) -> None:
    subprocess.run(amidi_bin() + ["-p", port, "-S", hex_msg], check=False)


def usbipd_attach_vid(vid_pid: str) -> bool:
    if not USBIPD.is_file():
        return False
    r = subprocess.run([str(USBIPD), "list"], capture_output=True, text=True)
    for line in r.stdout.splitlines():
        if vid_pid not in line:
            continue
        busid = line.split()[0]
        if "Attached" in line:
            return True
        subprocess.run([str(USBIPD), "bind", "--busid", busid], capture_output=True)
        a = subprocess.run(
            [str(USBIPD), "attach", "--wsl", "--busid", busid],
            capture_output=True,
            text=True,
        )
        print(f"  usbipd attach {busid} rc={a.returncode} {a.stderr.strip()}")
        return a.returncode == 0
    return False


def find_rawmidi() -> Path | None:
    cards = Path("/proc/asound/cards")
    if not cards.exists():
        return None
    text = cards.read_text(errors="replace")
    if "KeyStep" not in text and "A37" not in text:
        # bootloader may still bind as a generic Arturia / midiplus card
        pass
    for p in sorted(Path("/dev/snd").glob("midiC*D*")):
        return p
    return None


def sysex_wrap(inner: bytes) -> bytes:
    return b"\xf0" + inner + b"\xf7"


def plan_chunks(led: bytes) -> list[bytes]:
    if not led:
        raise ValueError("empty .led")
    out = []
    for i in range(0, len(led), CHUNK):
        out.append(sysex_wrap(led[i : i + CHUNK]))
    return out


def midi_open(path: Path) -> int:
    return os.open(path, os.O_RDWR | os.O_NONBLOCK)


def midi_write(fd: int, data: bytes) -> None:
    view = memoryview(data)
    while view:
        try:
            n = os.write(fd, view)
        except BlockingIOError:
            r, w, _ = select.select([], [fd], [], 2.0)
            if not w:
                raise TimeoutError("rawmidi write stalled (device not draining)")
            continue
        if n == 0:
            raise TimeoutError("rawmidi write returned 0")
        view = view[n:]


def midi_read(fd: int, timeout: float) -> bytes:
    deadline = time.monotonic() + timeout
    buf = bytearray()
    while time.monotonic() < deadline:
        remain = deadline - time.monotonic()
        r, _, _ = select.select([fd], [], [], remain)
        if not r:
            break
        try:
            chunk = os.read(fd, 256)
        except BlockingIOError:
            continue
        if not chunk:
            break
        buf += chunk
        if b"\xf7" in buf:
            break
    return bytes(buf)


def wait_pid(vid_pid: str, timeout: float, label: str) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if lsusb_has(vid_pid):
            print(f"  {label} {vid_pid} present")
            return True
        time.sleep(0.25)
    print(f"  TIMEOUT waiting for {vid_pid} ({label})")
    return False


def wait_rawmidi(timeout: float) -> Path | None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        p = find_rawmidi()
        if p is not None:
            return p
        time.sleep(0.25)
    return None


def cmd_dry_run(led_path: Path) -> int:
    led = led_path.read_bytes()
    chunks = plan_chunks(led)
    print("=== ks37_flash dry-run (no USB writes) ===")
    print(f"  file          {led_path}")
    print(f"  size          {len(led)} bytes")
    print(f"  chunks        {len(chunks)}  (inner {CHUNK}, last inner {len(led) % CHUNK or CHUNK})")
    print(f"  first inner   {chunks[0][1:-1][:16].hex()}...")
    print(f"  last inner    {chunks[-1][1:-1].hex()}")
    print(f"  prelude       Identity x2 + {len(GET_IDS)} GETs then productKey")
    print(f"  productKey    {PRODUCT_KEY.hex()}")
    print(f"  expect unlock {ACK_UNLOCK.hex()}")
    print(f"  expect done   {ACK_DONE.hex()}")
    print(f"  app PID       {VID_APP}   bootloader {VID_BL}")
    print(f"  now USB app   {lsusb_has(VID_APP)}  bl {lsusb_has(VID_BL)}")
    midi = find_rawmidi()
    print(f"  rawmidi       {midi or '(none)'}")
    return 0


def cmd_flash(led_path: Path, already_bl: bool) -> int:
    led = led_path.read_bytes()
    chunks = plan_chunks(led)
    print("=== ks37_flash LIVE ===")
    print(f"  {led_path}  {len(led)} bytes  {len(chunks)} chunks")

    if already_bl:
        if not lsusb_has(VID_BL):
            print("  --already-bootloader set but 0291 is not attached")
            print(USBIPD_HINT)
            return 2
        midi_path = wait_rawmidi(8)
        if midi_path is None:
            print("  no rawmidi on bootloader")
            return 2
        print(f"  bootloader midi {midi_path}")
        fd = midi_open(midi_path)
        stop = threading.Event()
        inbox: list[bytes] = []
        reader = threading.Thread(
            target=_inbox_loop, args=(fd, stop, inbox), daemon=True
        )
        reader.start()
        try:
            midi_write(fd, PRODUCT_KEY)
            print("  sent bootloader productKey (IN kept open)")
            if not _wait_ack(inbox, ACK_UNLOCK, 4.0):
                print("  missing F0 51 F7 — abort, no chunks sent")
                return 3
            print("  unlock reply F0 51 F7")
            return _stream(fd, chunks, inbox)
        except TimeoutError as e:
            print(f"  {e}")
            return 6
        finally:
            stop.set()
            reader.join(timeout=1.5)
            os.close(fd)

    if not lsusb_has(VID_APP):
        print(f"  app {VID_APP} not visible. Run ./scripts/keystep-see.sh")
        return 2

    midi_path = find_rawmidi()
    if midi_path is None:
        print("  no rawmidi in app mode")
        return 2
    port = amidi_port()
    if not port:
        print("  no amidi port in app mode")
        return 2
    print(f"  app amidi {port} — Identity + {len(GET_IDS)} GETs + productKey")
    fd_pre = midi_open(midi_path)
    try:
        n_ok = _send_app_prelude(fd_pre)
    finally:
        os.close(fd_pre)
    print(f"  GET replies {n_ok}/{len(GET_IDS)}")
    if n_ok == 0:
        print("  prelude got no GET replies — abort, no productKey")
        return 4
    print("  sending productKey (device will leave 0219)")
    amidi_send(port, PRODUCT_KEY_AMIDI)

    print("  waiting for bootloader 0291 (usbipd attach)...")
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        usbipd_attach_vid(VID_BL)
        if lsusb_has(VID_BL):
            print(f"  bootloader {VID_BL} present")
            break
        time.sleep(0.4)
    else:
        print(f"  TIMEOUT waiting for {VID_BL}")
        print(USBIPD_HINT)
        return 4

    midi_path = wait_rawmidi(15)
    if midi_path is None:
        print("  0291 is on USB but has no rawmidi")
        print(USBIPD_HINT)
        return 4

    print(f"  bootloader midi {midi_path} — productKey again")
    opened = _unlock_and_open_stream(midi_path)
    if opened is None:
        return 3
    fd, reply = opened
    print(f"  unlock reply {reply.hex()}")
    if ACK_UNLOCK not in reply:
        os.close(fd)
        print("  missing F0 51 F7 — abort, no chunks sent")
        return 3
    try:
        rc = _stream(fd, chunks)
    except TimeoutError as e:
        print(f"  {e}")
        rc = 6
    finally:
        os.close(fd)

    if rc != 0:
        return rc
    print("  waiting for app 0219...")
    if not wait_pid(VID_APP, 30, "app"):
        return 5
    return 0


def _send_app_prelude(fd: int) -> int:
    """Identity x2 + GET loop. Returns how many GETs got a 0x02 value reply."""
    midi_write(fd, IDENT)
    midi_read(fd, 0.4)
    midi_write(fd, IDENT)
    midi_read(fd, 0.4)
    ok = 0
    for pid in GET_IDS:
        midi_write(fd, get_sysex(pid))
        got = False
        deadline = time.monotonic() + 0.35
        while time.monotonic() < deadline:
            reply = midi_read(fd, min(0.12, deadline - time.monotonic()))
            if not reply:
                continue
            if bytes.fromhex("020041") + bytes([pid]) in reply:
                got = True
                break
        if got:
            ok += 1
    return ok


def _unlock_and_open_stream(midi_path: Path) -> tuple[int, bytes] | None:
    """Send productKey via amidi; return open rawmidi fd + reply bytes."""
    port = amidi_port()
    reply_path = Path("/tmp/ks37_unlock_reply.log")
    dump = subprocess.Popen(
        amidi_bin() + ["-p", port or "hw:0,0,0", "-d"],
        stdout=open(reply_path, "w"),
        stderr=subprocess.STDOUT,
    )
    time.sleep(0.2)
    amidi_send(port or "hw:0,0,0", PRODUCT_KEY_AMIDI)
    time.sleep(0.8)
    dump.terminate()
    dump.wait(timeout=2)
    reply = reply_path.read_bytes() if reply_path.exists() else b""
    # hex text from amidi -d, not raw
    text = reply.decode("utf-8", errors="replace")
    raw = b""
    if "F0 51 F7" in text or "F0 51" in text:
        raw = ACK_UNLOCK
    fd = midi_open(midi_path)
    return fd, raw if raw else reply


def _inbox_loop(fd: int, stop: threading.Event, inbox: list[bytes]) -> None:
    # Keep USB-MIDI IN URBs posted for the whole transfer (MCC holds midiIn).
    while not stop.is_set():
        data = midi_read(fd, 0.15)
        if data:
            inbox.append(data)


def _wait_ack(inbox: list[bytes], needle: bytes, timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if needle in b"".join(inbox):
            return True
        time.sleep(0.04)
    return False


def _stream(
    fd: int,
    chunks: list[bytes],
    inbox: list[bytes] | None = None,
    pace_s: float = 0.002,
) -> int:
    print(f"  streaming {len(chunks)} chunks (pace {pace_s*1000:.1f} ms)...", flush=True)
    t0 = time.monotonic()
    for i, ch in enumerate(chunks):
        midi_write(fd, ch)
        if pace_s:
            time.sleep(pace_s)
        if i and i % 1000 == 0:
            print(f"    {i}/{len(chunks)}", flush=True)
    dt = time.monotonic() - t0
    if inbox is not None:
        ok = _wait_ack(inbox, ACK_DONE, 8.0)
        blob = b"".join(inbox)
        print(f"  inbox {blob.hex()}  ({dt:.1f}s)")
        if not ok:
            print("  missing F0 77 F7 — transfer may have failed; recover with MCC stock")
            return 6
        return 0
    done = midi_read(fd, 8.0)
    print(f"  done reply {done.hex()}  ({dt:.1f}s)")
    if ACK_DONE not in done:
        print("  missing F0 77 F7 — transfer may have failed; recover with MCC stock")
        return 6
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("led")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument(
        "--confirm",
        help="must be YES-FLASH to send anything",
    )
    p.add_argument(
        "--already-bootloader",
        action="store_true",
        help="device is already 1c75:0291; skip the app-mode unlock",
    )
    args = p.parse_args()
    path = Path(args.led)
    if not path.is_file():
        print(f"missing {path}", file=sys.stderr)
        return 1
    if args.dry_run:
        return cmd_dry_run(path)
    if args.confirm != "YES-FLASH":
        print("refusing to send: pass --dry-run, or --confirm YES-FLASH")
        return 1
    return cmd_flash(path, args.already_bootloader)


if __name__ == "__main__":
    sys.exit(main())
