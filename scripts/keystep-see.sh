#!/usr/bin/env bash
# Gate 0: is the KeyStep 37 visible from this WSL repo?
# App PID 1c75:0219, updater 1c75:0291. Do not send app-mode productKey.
#
# Usage: ./scripts/keystep-see.sh
# Exit 0 only when app-mode USB + ALSA + Identity + GET all succeed.
# Updater 0291 + any hw: rawmidi prints ready for --already-bootloader
# and still exits 1 (Gate 0 is app-only).

set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VID_APP="1c75:0219"
VID_BL="1c75:0291"
IDENTITY="F0 7E 7F 06 01 F7"
GET_CH="F0 00 20 6B 7F 42 01 00 41 01 F7"
FAIL=0
MODE="none"
PORT=""

AMIDI=(amidi)
if ! amidi -l >/dev/null 2>&1; then
    AMIDI=(sudo amidi)
fi

amidi_cmd() {
    "${AMIDI[@]}" "$@"
}

echo "== USB =="
if lsusb -d "$VID_APP" >/dev/null 2>&1; then
    lsusb -d "$VID_APP"
    MODE="app"
elif lsusb -d "$VID_BL" >/dev/null 2>&1; then
    lsusb -d "$VID_BL"
    MODE="bootloader"
    echo "Updater PID $VID_BL is attached. Do not send app-mode productKey."
    echo "Hardware entry: Rec+Stop+Play (Hold/Shift alternate)."
    echo "Send: ./scripts/flash_bl_wsl.sh <file.led>  or recover with MCC stock."
else
    echo "NOT FOUND ($VID_APP or $VID_BL)."
    echo "On Windows (elevated PowerShell), bind BOTH personalities by PID:"
    echo "  usbipd list"
    echo "  usbipd bind --busid <BUSID_0219>"
    echo "  usbipd attach --wsl --busid <BUSID_0219> --auto-attach"
    echo "After Rec+Stop+Play the device re-enumerates as $VID_BL"
    echo "(name may be Updater / MiniLab / UNKNOWN):"
    echo "  usbipd bind --busid <BUSID_0291>   # when it appears"
    echo "  usbipd attach --wsl --busid <BUSID_0291> --auto-attach"
    FAIL=1
fi

if lsusb -d "$VID_BL" >/dev/null 2>&1 && [ "$MODE" = "app" ]; then
    echo "(also present) $(lsusb -d "$VID_BL")"
fi

echo
echo "== ALSA / MIDI =="
if [ -r /proc/asound/cards ]; then
    cat /proc/asound/cards
fi
if grep -qi "KeyStep 37" /proc/asound/cards 2>/dev/null; then
    :
elif [ "$MODE" = "bootloader" ]; then
    echo "No 'KeyStep 37' ALSA name (updater may bind as Updater / generic MIDI)."
elif [ "$MODE" = "app" ]; then
    echo "No KeyStep 37 ALSA card."
    FAIL=1
fi

PORT="$(amidi_cmd -l 2>/dev/null | awk '/KeyStep 37|A37|Updater|midiplus/ {print $2; exit}')"
if [ -z "${PORT:-}" ]; then
    PORT="$(amidi_cmd -l 2>/dev/null | awk '/hw:/ {print $2; exit}')"
fi
if [ -n "${PORT:-}" ]; then
    echo "amidi port: $PORT"
else
    echo "No amidi port."
    if ! groups | grep -qw audio; then
        echo "This shell may lack the live 'audio' group. New WSL terminal, or sudo."
    fi
    if [ "$MODE" = "app" ]; then
        FAIL=1
    fi
fi

if [ "$MODE" = "app" ] && [ -n "${PORT:-}" ]; then
    echo
    echo "== MIDI Identity + GET =="
    # leftover amidi -d from a prior run holds the rawmidi exclusively
    if [ -e /dev/snd/midiC0D0 ]; then
        sudo fuser -k /dev/snd/midiC0D0 >/dev/null 2>&1 || true
        sleep 0.2
    fi
    REPLY="$(mktemp)"
    timeout 3 "${AMIDI[@]}" -p "$PORT" -d >"$REPLY" 2>&1 &
    LISTEN=$!
    sleep 0.3
    "${AMIDI[@]}" -p "$PORT" -S "$IDENTITY" >/dev/null 2>&1 || true
    sleep 0.2
    "${AMIDI[@]}" -p "$PORT" -S "$GET_CH" >/dev/null 2>&1 || true
    wait "$LISTEN" 2>/dev/null || true
    echo "-- dump --"
    cat "$REPLY"
    if grep -q "F0 7E" "$REPLY" && grep -q "00 20 6B" "$REPLY"; then
        echo "OK Identity (Arturia 00 20 6B)"
        if grep -q "00 06 01 01" "$REPLY"; then
            echo "OK revision 00 06 01 01 (1.1.6.x)"
        else
            echo "Revision bytes not 00 06 01 01"
        fi
    else
        echo "FAIL Identity"
        FAIL=1
    fi
    if grep -q "F0 00 20 6B" "$REPLY"; then
        echo "OK GET answered"
    else
        echo "FAIL GET"
        FAIL=1
    fi
    rm -f "$REPLY"
fi

echo
if [ "$FAIL" -eq 0 ] && [ "$MODE" = "app" ]; then
    echo "Gate 0 PASS (app $VID_APP, port $PORT)."
elif [ "$MODE" = "bootloader" ]; then
    if [ -n "${PORT:-}" ]; then
        echo "0291 ready for --already-bootloader (port $PORT)."
        echo "  ./scripts/flash_bl_wsl.sh firmware-re/recovery/keystep37_1.1.6.579_stock.led"
    else
        echo "Updater $VID_BL visible but no hw: rawmidi yet. Wait for snd-usb-audio, or:"
        echo "  ./scripts/attach_bootloader.sh"
    fi
    FAIL=1
else
    echo "Gate 0 FAIL."
fi
exit "$FAIL"
