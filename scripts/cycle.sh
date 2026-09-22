#!/usr/bin/env bash
# Unicorn-first cycle. Default never flashes and never attaches 0291.
#
#   ./scripts/cycle.sh              # emulate all, dry-run stock KeystepFlash
#   ./scripts/cycle.sh e0b          # build e0b, emulate all, dry-run that .led
#   ./scripts/cycle.sh e0b --live   # same, then wait 0291 / flash / listen
#
# --live still needs you: Rec+Stop+Play, then hold a key (Hold on).
# Do not inject notes. Do not attach 0291 to WSL. Do not use flash_bl_wsl.sh.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON="$ROOT/.venv/bin/python3"
if [[ ! -x "$PYTHON" ]]; then
  PYTHON=python3
fi
USBIPD="/mnt/c/Program Files/usbipd-win/usbipd.exe"
SCHTASKS="/mnt/c/Windows/System32/schtasks.exe"
DROP_MNT="/mnt/c/Users/jimcu/KeystepFlash"
WIN_DIAG='C:\Users\jimcu\Documents\my apps\Keystep_Mod_PC_1\flash\diag_unlock.py'
AUTOATTACH_TN='\\KeystepAutoAttach-USBIP'

LEVEL=""
LIVE=0
SKIP_BUILD=0

usage() {
  cat <<EOF
usage: $0 [level] [--live] [--skip-build]

  level        e0|e1|e3|c1|c2|e0b|e1b|e3b — build that image first
  --live       after unicorn + dry-run: wait 0291, flash-win, listen
  --skip-build do not run build_patch.py even if a level is given

Default is no --live. Abort if emulate_ks37.py all fails (no MIDI, no flash).
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    --live)
      LIVE=1
      shift
      ;;
    --skip-build)
      SKIP_BUILD=1
      shift
      ;;
    e0|e1|e3|c1|c2|e0b|e1b|e3b)
      if [[ -n "$LEVEL" ]]; then
        echo "extra level: $1" >&2
        exit 2
      fi
      LEVEL="$1"
      shift
      ;;
    *)
      echo "unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

led_name() {
  case "$1" in
    e0) echo e0_euclid_3in8.led ;;
    e1) echo e1_euclid_hits.led ;;
    e3) echo e3_euclid_shift.led ;;
    c1) echo c1_scale_chord.led ;;
    c2) echo c2_shift_type.led ;;
    e0b) echo e0b_pitchgate_3in8.led ;;
    e1b) echo e1b_pitchgate_hits.led ;;
    e3b) echo e3b_pitchgate_shift.led ;;
    *) echo keystep37_1.1.6.579_stock.led ;;
  esac
}

listen_cmd() {
  case "$1" in
    e0|e0b) echo e0 ;;
    e1|e1b) echo e1 ;;
    e3|e3b) echo e3-off ;;
    c1) echo c1 ;;
    c2) echo c2 ;;
    *) echo dump ;;
  esac
}

usbipd_has() {
  local pat="$1"
  "$USBIPD" list 2>/dev/null | grep -qiE "$pat"
}

wait_usbipd() {
  local pat="$1"
  local msg="$2"
  local i
  for i in $(seq 1 180); do
    if usbipd_has "$pat"; then
      echo "  saw $pat"
      return 0
    fi
    echo "$(date +%H:%M:%S) waiting $msg"
    sleep 2
  done
  echo "TIMEOUT waiting for $msg" >&2
  return 1
}

stop_autoattach() {
  "$SCHTASKS" /End /TN "$AUTOATTACH_TN" >/dev/null 2>&1 || true
  echo "AutoAttach stopped (0291 stays on Windows)"
}

start_autoattach() {
  "$SCHTASKS" /Run /TN "$AUTOATTACH_TN" >/dev/null 2>&1 || true
  echo "AutoAttach started"
}

echo "=== cycle ${LEVEL:-no-level} live=$LIVE ==="

if [[ -n "$LEVEL" && "$SKIP_BUILD" -eq 0 ]]; then
  echo "-- build $LEVEL --"
  "$PYTHON" "$ROOT/firmware-re/scripts/build_patch.py" "$LEVEL" || {
    echo "FAIL build $LEVEL" >&2
    exit 1
  }
fi

echo "-- emulate all --"
"$PYTHON" "$ROOT/firmware-re/scripts/emulate_ks37.py" all || {
  echo "FAIL unicorn — abort, no MIDI, no flash" >&2
  echo "  leftover FLAG_RAM at 0x20005F00 is the e3b miss until BSS-init" >&2
  exit 1
}

LED_FILE="$(led_name "${LEVEL:-}")"
LED_PATH="$DROP_MNT/$LED_FILE"
if [[ ! -f "$LED_PATH" ]]; then
  ALT="$ROOT/firmware-re/firmware-images/rebuild/$LED_FILE"
  if [[ -f "$ALT" ]]; then
    LED_PATH="$ALT"
  elif [[ -f "$ROOT/firmware-re/recovery/$LED_FILE" ]]; then
    LED_PATH="$ROOT/firmware-re/recovery/$LED_FILE"
  else
    echo "missing $LED_PATH — build or copy into KeystepFlash" >&2
    exit 1
  fi
fi

echo "-- dry-run $LED_PATH --"
"$ROOT/scripts/flash-win.sh" --dry-run "$LED_PATH" || {
  echo "FAIL dry-run" >&2
  exit 1
}

if [[ "$LIVE" -eq 0 ]]; then
  echo "PASS cycle (unicorn + dry-run). No flash. Occupancy: ./scripts/occupancy-listen.sh"
  exit 0
fi

echo "-- live flash (you: Rec+Stop+Play; never attach 0291 to WSL) --"
if ! usbipd_has '0291'; then
  echo "Rec+Stop+Play now"
fi
wait_usbipd '0291' 'updater 0291' || exit 1

stop_autoattach
if lsusb -d 1c75:0291 >/dev/null 2>&1; then
  echo "FAIL 0291 is attached to WSL — unplug, leave updater on Windows, do not usbipd attach" >&2
  exit 1
fi

echo "-- diag_unlock --"
py.exe -3 -u "$WIN_DIAG" || {
  echo "FAIL diag_unlock (want F0 51 F7)" >&2
  exit 1
}

echo "-- flash-win live --"
"$ROOT/scripts/flash-win.sh" --already-bootloader --already-unlocked --confirm YES-FLASH "$LED_PATH" || {
  echo "FAIL live flash" >&2
  exit 1
}

echo "-- wait app 0219 / 1c76:0219 --"
wait_usbipd '1c75:0219|1c76:0219' 'app 0219' || exit 1
start_autoattach
"$ROOT/scripts/wait_wsl_reattach.sh" || {
  echo "FAIL WSL reattach" >&2
  exit 1
}

LISTEN="$(listen_cmd "${LEVEL:-}")"
echo "Hold F, Hold on"
echo "-- listen $LISTEN --"
"$PYTHON" "$ROOT/firmware-re/scripts/listen_ks37.py" "$LISTEN" --clocks
RC=$?
if [[ "$RC" -eq 0 ]]; then
  echo "PASS cycle live ($LEVEL $LISTEN)"
else
  echo "FAIL listen $LISTEN (rc=$RC)" >&2
fi
exit "$RC"
