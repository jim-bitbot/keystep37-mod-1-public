#!/usr/bin/env python3
"""
Sweep all 128 globalParamId values via the confirmed live GET-parameter
protocol and save the results to a JSON file, for later diffing across
different device states (arp mode, chord mode, etc).

Usage: sudo .venv/bin/python3 sweep_params.py <output.json>
"""
import subprocess
import sys
import time
import json
import re

PORT = "hw:0,0,0"

def send_and_read(gpid):
    hex_gpid = f"{gpid:02X}"
    msg = f"F0 00 20 6B 7F 42 01 00 41 {hex_gpid} F7"
    # start listener
    listener = subprocess.Popen(
        ["timeout", "1.2", "amidi", "-p", PORT, "-d"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    time.sleep(0.05)
    subprocess.run(["amidi", "-p", PORT, "-S", msg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    out, _ = listener.communicate()
    # look for the full reply: F0 00 20 6B 7F 42 02 00 41 <gpid> <value> F7
    for line in out.splitlines():
        line = line.strip()
        m = re.match(r"F0 00 20 6B 7F 42 02 00 41 ([0-9A-F]{2}) ([0-9A-F]{2}) F7", line)
        if m and int(m.group(1), 16) == gpid:
            return int(m.group(2), 16)
    return None

def main():
    out_path = sys.argv[1]
    results = {}
    for gpid in range(128):
        val = send_and_read(gpid)
        results[gpid] = val
        print(f"gpid {gpid:3d} (0x{gpid:02x}) = {val}")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nwrote {out_path}")

if __name__ == "__main__":
    main()
