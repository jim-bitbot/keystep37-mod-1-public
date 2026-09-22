#!/usr/bin/env bash
# Flash A: hand the KeyStep to Windows so MIDI Control Center can send stock.
# Does not send productKey from WSL.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STOCK="$ROOT/firmware-re/recovery/keystep37_1.1.6.579_stock.led"
USBIPD="/mnt/c/Program Files/usbipd-win/usbipd.exe"
BUSID="${USBIPD_BUSID:-2-6}"

if [ ! -f "$STOCK" ]; then
    echo "missing recovery stock: $STOCK"
    exit 1
fi

WIN_LED="$(wslpath -w "$STOCK")"
echo "=== Flash A — stock via MIDI Control Center ==="
echo "Use ONLY this file (1.1.6.579, bit-identical vendor copy):"
echo "  $WIN_LED"
echo
echo "Steps on Windows:"
echo "  1. This script detaches busid $BUSID from WSL."
echo "  2. Open MIDI Control Center, Firmware Update, pick the file above."
echo "  3. Let it finish until the KeyStep is back in normal mode."
echo "  4. usbipd will auto-attach, or run:"
echo "       usbipd attach --wsl --busid $BUSID"
echo

if [ ! -x "$USBIPD" ]; then
    echo "usbipd.exe not found at $USBIPD"
    exit 1
fi

echo "Detaching $BUSID from WSL..."
"$USBIPD" detach --busid "$BUSID" || true
sleep 1
"$USBIPD" list
echo
echo "Waiting for $BUSID to show Attached again (MCC flash + usbipd attach)..."
