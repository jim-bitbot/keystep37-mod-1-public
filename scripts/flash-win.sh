#!/usr/bin/env bash
# Call the Windows winmm sender from WSL. Does not use ALSA / ks37_flash.py.
#
# Parser is WSL firmware-re/scripts/led_codec.py (PC_1 flash_win.py imports it).
# Default is --dry-run. Live send still needs Rec+Stop+Play, AutoAttach off,
# device on Windows, --already-bootloader --confirm YES-FLASH.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WIN_FLASH='C:\Users\jimcu\Documents\my apps\Keystep_Mod_PC_1\flash\flash_win.py'
DROP_WIN='C:\Users\jimcu\KeystepFlash'
DROP_MNT='/mnt/c/Users/jimcu/KeystepFlash'

usage() {
  cat <<EOF
usage: $0 [--dry-run] [--already-bootloader] [--already-unlocked]
          [--confirm YES-FLASH] [--max-pages N] [file.led]

file.led may be a WSL path or C:\\... Default: KeystepFlash stock.
Without --confirm YES-FLASH this is always a dry-run.

dry-run:
  $0
  $0 $DROP_MNT/e0b_pitchgate_3in8.led

live (device already 0291 on Windows, AutoAttach off):
  $0 --already-bootloader --already-unlocked --confirm YES-FLASH \\
     $DROP_MNT/e0b_pitchgate_3in8.led

Do not use flash_bl_wsl.sh (ALSA stall).
EOF
}

to_win_path() {
  local p="$1"
  if [[ "$p" == [A-Za-z]:\\* || "$p" == [A-Za-z]:/* ]]; then
    printf '%s' "$p"
    return
  fi
  if [[ ! -e "$p" ]]; then
    echo "missing $p" >&2
    exit 2
  fi
  wslpath -w "$p"
}

LED=""
PASSTHRU=()
HAVE_CONFIRM=0
HAVE_DRY=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    --dry-run)
      HAVE_DRY=1
      PASSTHRU+=("$1")
      shift
      ;;
    --confirm)
      HAVE_CONFIRM=1
      PASSTHRU+=("$1" "${2:-}")
      shift 2
      ;;
    --already-bootloader|--already-unlocked)
      PASSTHRU+=("$1")
      shift
      ;;
    --max-pages)
      PASSTHRU+=("$1" "${2:-}")
      shift 2
      ;;
    --)
      shift
      PASSTHRU+=("$@")
      break
      ;;
    -*)
      echo "unknown flag: $1" >&2
      usage >&2
      exit 2
      ;;
    *)
      if [[ -n "$LED" ]]; then
        echo "extra argument: $1" >&2
        exit 2
      fi
      LED="$1"
      shift
      ;;
  esac
done

if [[ -z "$LED" ]]; then
  LED="$DROP_MNT/keystep37_1.1.6.579_stock.led"
fi

WIN_LED="$(to_win_path "$LED")"

if [[ "$HAVE_CONFIRM" -eq 0 && "$HAVE_DRY" -eq 0 ]]; then
  PASSTHRU+=(--dry-run)
fi

echo "=== flash-win (py.exe → flash_win.py) ==="
echo "  led     $WIN_LED"
echo "  sender  $WIN_FLASH"
echo "  parser  $ROOT/firmware-re/scripts/led_codec.py"
echo

exec py.exe -3 -u "$WIN_FLASH" "${PASSTHRU[@]}" "$WIN_LED"
