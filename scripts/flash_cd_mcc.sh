#!/usr/bin/env bash
# Flash C then D via MIDI Control Center on Windows, with USBPcap running.
# Does not send productKey from WSL.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NOOP="$ROOT/firmware-re/firmware-images/rebuild/noop_1f400.led"
STOCK="$ROOT/firmware-re/recovery/keystep37_1.1.6.579_stock.led"
USBIPD="/mnt/c/Program Files/usbipd-win/usbipd.exe"
BUSID="${USBIPD_BUSID:-2-6}"
WIN_DIR="/mnt/c/Users/jimcu/KeystepFlash"

if [ ! -f "$NOOP" ] || [ ! -f "$STOCK" ]; then
    echo "missing noop or stock .led"
    exit 1
fi

mkdir -p "$WIN_DIR"
cp -f "$NOOP" "$WIN_DIR/noop_1f400.led"
cp -f "$STOCK" "$WIN_DIR/keystep37_1.1.6.579_stock.led"

echo "=== Flash C then D — MCC on Windows ==="
echo "C  noop : C:\\Users\\jimcu\\KeystepFlash\\noop_1f400.led"
echo "D  stock: C:\\Users\\jimcu\\KeystepFlash\\keystep37_1.1.6.579_stock.led"
echo
echo "Stopping usbipd auto-attach, detaching $BUSID..."
"/mnt/c/Windows/System32/schtasks.exe" /End /TN "\\KeystepAutoAttach-USBIP" >/dev/null 2>&1 || true
"$USBIPD" detach --busid "$BUSID" || true
sleep 1
"$USBIPD" list
echo
echo "MCC (Dutch menus): Apparaat → Firmware-update."
echo "1. Close MCC if it is already open, then reopen so the GET loop is captured."
echo "2. Flash C: Bestand selecteren → noop_1f400.led  (236352 bytes)."
echo "3. Wait until the KeyStep is back in normal mode."
echo "4. Flash D: same dialog → keystep37_1.1.6.579_stock.led"
echo "5. After D, say so — we reattach WSL and retry Flash B with the GET prelude."
