#!/usr/bin/env bash
# Hand a Euclidean / scale-chord .led to MIDI Control Center.
# Does not send productKey from WSL. Recovery is always the stock .led.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
USBIPD="/mnt/c/Program Files/usbipd-win/usbipd.exe"
BUSID="${USBIPD_BUSID:-2-6}"
WIN_DIR="/mnt/c/Users/jimcu/KeystepFlash"
LEVEL="${1:-e0}"

case "$LEVEL" in
    e0) SRC="$ROOT/firmware-re/firmware-images/rebuild/e0_euclid_3in8.led" ;;
    e1) SRC="$ROOT/firmware-re/firmware-images/rebuild/e1_euclid_hits.led" ;;
    e3) SRC="$ROOT/firmware-re/firmware-images/rebuild/e3_euclid_shift.led" ;;
    c1) SRC="$ROOT/firmware-re/firmware-images/rebuild/c1_scale_chord.led" ;;
    c2) SRC="$ROOT/firmware-re/firmware-images/rebuild/c2_shift_type.led" ;;
    stock) SRC="$ROOT/firmware-re/recovery/keystep37_1.1.6.579_stock.led" ;;
    *) echo "usage: $0 e0|e1|e3|c1|c2|stock"; exit 1 ;;
esac

if [ ! -f "$SRC" ]; then
    echo "missing $SRC — run firmware-re/scripts/build_patch.py $LEVEL"
    exit 1
fi

mkdir -p "$WIN_DIR"
cp -f "$SRC" "$WIN_DIR/$(basename "$SRC")"
cp -f "$ROOT/firmware-re/recovery/keystep37_1.1.6.579_stock.led" \
    "$WIN_DIR/keystep37_1.1.6.579_stock.led"

echo "=== MCC flash $LEVEL ==="
echo "file : C:\\Users\\jimcu\\KeystepFlash\\$(basename "$SRC")"
echo "abort: C:\\Users\\jimcu\\KeystepFlash\\keystep37_1.1.6.579_stock.led"
echo
echo "Stopping usbipd auto-attach, detaching $BUSID..."
"/mnt/c/Windows/System32/schtasks.exe" /End /TN "\\KeystepAutoAttach-USBIP" >/dev/null 2>&1 || true
"$USBIPD" detach --busid "$BUSID" || true
sleep 1
"$USBIPD" list
echo
echo "MCC: Apparaat → Firmware-update → Bestand selecteren → $(basename "$SRC")"
echo "If USB/Identity dies, flash the stock file immediately."
echo "Afterward: ./scripts/wait_wsl_reattach.sh && ./scripts/keystep-see.sh"
