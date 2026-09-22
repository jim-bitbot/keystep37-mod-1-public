#!/usr/bin/env bash
# Live-query a KeyStep 37 global parameter over MIDI, read-only.
# Confirmed working: session bytes 7F 42 are a fixed device/firmware
# constant, not per-connection random (see findings-2026-09-20.md).
#
# Usage: ./get_param.sh <globalParamId decimal>
# Example: ./get_param.sh 1   (MIDI Input Channel)

set -euo pipefail

if [ $# -ne 1 ]; then
    echo "Usage: $0 <globalParamId decimal>" >&2
    exit 1
fi

GPID_HEX=$(printf "%02X" "$1")
PORT="hw:0,0,0"

sudo timeout 3 amidi -p "$PORT" -d > /tmp/get_param_reply.log 2>&1 &
LISTENER_PID=$!
sleep 0.3
sudo amidi -p "$PORT" -S "F0 00 20 6B 7F 42 01 00 41 $GPID_HEX F7"
wait "$LISTENER_PID" 2>/dev/null || true
cat /tmp/get_param_reply.log
rm -f /tmp/get_param_reply.log
