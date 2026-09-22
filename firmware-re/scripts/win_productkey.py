"""Send KeyStep 37 MCC unlock prelude via Windows winmm (native USB)."""
from __future__ import annotations

import ctypes
import sys
import time
from ctypes import wintypes
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mcc_unlock_prelude import GET_IDS, IDENT, PRODUCT_KEY, get_sysex

winmm = ctypes.windll.winmm


class MIDIOUTCAPS(ctypes.Structure):
    _fields_ = [
        ("wMid", wintypes.WORD),
        ("wPid", wintypes.WORD),
        ("vDriverVersion", wintypes.DWORD),
        ("szPname", ctypes.c_wchar * 32),
        ("wTechnology", wintypes.WORD),
        ("wVoices", wintypes.WORD),
        ("wNotes", wintypes.WORD),
        ("wChannelMask", wintypes.WORD),
        ("dwSupport", wintypes.DWORD),
    ]


class MIDIHDR(ctypes.Structure):
    _fields_ = [
        ("lpData", ctypes.c_void_p),
        ("dwBufferLength", wintypes.DWORD),
        ("dwBytesRecorded", wintypes.DWORD),
        ("dwUser", ctypes.POINTER(ctypes.c_ulong)),
        ("dwFlags", wintypes.DWORD),
        ("lpNext", ctypes.c_void_p),
        ("reserved", ctypes.c_void_p),
        ("dwOffset", wintypes.DWORD),
        ("dwReserved", ctypes.c_void_p * 8),
    ]


def find_dev() -> int:
    n = winmm.midiOutGetNumDevs()
    caps = MIDIOUTCAPS()
    for i in range(n):
        winmm.midiOutGetDevCapsW(i, ctypes.byref(caps), ctypes.sizeof(caps))
        name = caps.szPname
        print(f"  midi out {i}: {name}")
        if "KeyStep" in name or "A37" in name or "Updater" in name:
            return i
    return -1


def send_on(handle, payload: bytes) -> int:
    buf = ctypes.create_string_buffer(payload)
    hdr = MIDIHDR()
    hdr.lpData = ctypes.cast(buf, ctypes.c_void_p)
    hdr.dwBufferLength = len(payload)
    rc = winmm.midiOutPrepareHeader(handle, ctypes.byref(hdr), ctypes.sizeof(hdr))
    if rc != 0:
        print(f"midiOutPrepareHeader rc={rc}")
        return rc
    rc = winmm.midiOutLongMsg(handle, ctypes.byref(hdr), ctypes.sizeof(hdr))
    for _ in range(50):
        if hdr.dwFlags & 0x00000001:  # MHDR_DONE
            break
        time.sleep(0.02)
    winmm.midiOutUnprepareHeader(handle, ctypes.byref(hdr), ctypes.sizeof(hdr))
    print(f"midiOutLongMsg rc={rc} len={len(payload)}")
    return rc


def send(dev: int, payload: bytes) -> int:
    handle = wintypes.HANDLE()
    rc = winmm.midiOutOpen(ctypes.byref(handle), dev, 0, 0, 0)
    if rc != 0:
        print(f"midiOutOpen failed {rc}")
        return rc
    rc = send_on(handle, payload)
    winmm.midiOutClose(handle)
    return rc


def send_many(dev: int, payloads: list[bytes], gap_s: float = 0.01) -> int:
    handle = wintypes.HANDLE()
    rc = winmm.midiOutOpen(ctypes.byref(handle), dev, 0, 0, 0)
    if rc != 0:
        print(f"midiOutOpen failed {rc}")
        return rc
    for i, payload in enumerate(payloads):
        rc |= send_on(handle, payload)
        if i + 1 < len(payloads):
            time.sleep(gap_s)
    winmm.midiOutClose(handle)
    return rc


def main() -> int:
    print("=== win_productkey ===")
    dev = find_dev()
    if dev < 0:
        print("no KeyStep MIDI out (is the device on Windows, not WSL?)")
        return 2
    short = "--short" in sys.argv
    if short:
        print(f"sending Identity + productKey on one handle, dev {dev} (MCC D shape)")
        rc = send_many(dev, [IDENT, PRODUCT_KEY], gap_s=0.003)
        return 0 if rc == 0 else 3
    print(f"sending Identity x2 + {len(GET_IDS)} GETs + productKey on dev {dev}")
    rc = send(dev, IDENT)
    time.sleep(0.15)
    rc |= send(dev, IDENT)
    time.sleep(0.15)
    for pid in GET_IDS:
        rc |= send(dev, get_sysex(pid))
        time.sleep(0.012)
    time.sleep(0.3)
    rc |= send(dev, PRODUCT_KEY)
    return 0 if rc == 0 else 3


if __name__ == "__main__":
    sys.exit(main())
