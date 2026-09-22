#!/usr/bin/env bash
# When 1c75:0291 appears on Windows, bind+attach it to WSL.
set -u
USBIPD="/mnt/c/Program Files/usbipd-win/usbipd.exe"
for i in $(seq 1 120); do
    LINE="$("$USBIPD" list 2>/dev/null | awk '/1c75:0291/{print; exit}')"
    if [ -n "$LINE" ]; then
        BUSID="$(echo "$LINE" | awk '{print $1}')"
        echo "$(date +%H:%M:%S) found $LINE"
        if echo "$LINE" | grep -q "Attached"; then
            echo "BL_ATTACHED $BUSID"
            exit 0
        fi
        "$USBIPD" bind --busid "$BUSID" 2>/dev/null || true
        if "$USBIPD" attach --wsl --busid "$BUSID"; then
            echo "BL_ATTACHED $BUSID"
            exit 0
        fi
        echo "attach failed, retry"
    fi
    sleep 0.5
done
echo "TIMEOUT no 0291 attach"
exit 1
