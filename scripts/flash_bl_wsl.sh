#!/usr/bin/env bash
# Blocked. WSL ALSA .led send stalls. Use the Windows winmm sender instead.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "refuse: flash_bl_wsl.sh is blocked (usbipd/ALSA stall)."
echo "use:    $ROOT/scripts/flash-win.sh --dry-run"
echo "live:   Rec+Stop+Play, AutoAttach off, then:"
echo "        $ROOT/scripts/flash-win.sh --already-bootloader --confirm YES-FLASH <file.led>"
exit 2
