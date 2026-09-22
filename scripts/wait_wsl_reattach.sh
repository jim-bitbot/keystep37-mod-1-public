#!/usr/bin/env bash
# Poll usbipd until busid is Attached to WSL again.
set -u
USBIPD="/mnt/c/Program Files/usbipd-win/usbipd.exe"
BUSID="${1:-2-6}"
for i in $(seq 1 180); do
    STATE="$("$USBIPD" list 2>/dev/null | awk -v b="$BUSID" '$1==b {print $0}')"
    echo "$(date +%H:%M:%S) $STATE"
    if echo "$STATE" | grep -q "Attached"; then
        echo "REATTACHED $BUSID"
        exit 0
    fi
    sleep 5
done
echo "TIMEOUT waiting for $BUSID Attached"
exit 1
