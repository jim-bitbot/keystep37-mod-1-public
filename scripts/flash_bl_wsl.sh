#!/usr/bin/env bash
# Hardware Rec+Stop+Play updater, then WSL .led send.
# Does not send app-mode productKey. Requires an explicit file argument.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LED="${1:-}"

if [ -z "$LED" ] || [ ! -f "$LED" ]; then
    echo "usage: $0 <file.led>"
    echo "stock first:"
    echo "  $0 firmware-re/recovery/keystep37_1.1.6.579_stock.led"
    echo "then E0:"
    echo "  $0 firmware-re/firmware-images/rebuild/e0_euclid_3in8.led"
    exit 1
fi

echo "=== WSL bootloader flash ==="
echo "file: $LED"
echo "Jim: unplug, hold Rec+Stop+Play, plug USB (no hub)."
echo "Expect Hold/Shift alternate. Abort = MCC stock .led."
echo

"$ROOT/scripts/attach_bootloader.sh" || exit 1
exec python3 "$ROOT/firmware-re/scripts/ks37_flash.py" \
    --already-bootloader --confirm YES-FLASH "$LED"
