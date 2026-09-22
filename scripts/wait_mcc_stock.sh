#!/usr/bin/env bash
# Watch Windows usbipd for a bootloader then app re-enum (MCC stock flash).
set -u
USBIPD="/mnt/c/Program Files/usbipd-win/usbipd.exe"
SAW_BL=0
for i in $(seq 1 180); do
    LIST="$("$USBIPD" list 2>/dev/null)"
    echo "$(date +%H:%M:%S)"
    echo "$LIST" | awk '/1c75:/{print}'
    if echo "$LIST" | grep -q "1c75:0291"; then
        SAW_BL=1
        echo "MCC_BOOTLOADER"
    elif [ "$SAW_BL" -eq 1 ] && echo "$LIST" | grep -q "1c75:0219"; then
        echo "MCC_DONE"
        exit 0
    fi
    sleep 5
done
echo "TIMEOUT no MCC bootloader seen"
exit 1
