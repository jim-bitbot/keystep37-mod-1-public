#!/usr/bin/env python3
"""
Extract the firmware image from a USBPcap capture of a KeyStep 37 firmware
update session, by concatenating the raw SysEx payloads sent during the
bootloader-mode chunk transfer.

Usage:
    tshark -r <capture.pcap> \
        -Y "usb.device_address==<BOOTLOADER_ADDR> && usb.endpoint_address==0x01 && usbaudio.sysex.reassembled.data" \
        -T fields -e frame.number -e usbaudio.sysex.reassembled.data \
        > chunks.txt
    python3 extract_firmware_from_pcap.py chunks.txt output.led

Skips the productKey unlock message (7-byte payload) automatically.
"""
import sys

def main(chunks_path, out_path):
    payload = bytearray()
    with open(chunks_path) as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 2:
                continue
            _frame, hexstr = parts
            raw = bytes.fromhex(hexstr)
            if raw[0] != 0xF0 or raw[-1] != 0xF7:
                continue
            inner = raw[1:-1]
            if len(inner) == 7:
                # the productKey unlock payload, not a firmware chunk
                continue
            payload += inner
    with open(out_path, "wb") as f:
        f.write(payload)
    print(f"wrote {len(payload)} bytes to {out_path}")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
