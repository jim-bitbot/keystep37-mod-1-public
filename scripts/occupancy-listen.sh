#!/usr/bin/env bash
# Prompted occupancy pass. You press each gesture; amidi -d logs MIDI.
# Fill firmware-re/notes/stock-shift-map.md Live MIDI after this log.
# Skip Rec+Stop+Play and factory rST (known, destructive / updater).
#
#   ./scripts/occupancy-listen.sh           # stock MIDI (note-on / CH / silence)
#   ./scripts/occupancy-listen.sh --test20  # MCC Test-20 raw CC telemetry
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROMPTS="$ROOT/firmware-re/notes/occupancy-prompts.txt"
CAP="$ROOT/firmware-re/captures/occupancy"
STAMP="$(date +%Y%m%d-%H%M%S)"
CCPY="$ROOT/firmware-re/scripts/occupancy_cc.py"
PYTHON="$ROOT/.venv/bin/python3"
if [[ ! -x "$PYTHON" ]]; then
    PYTHON=python3
fi

TEST20=0
while [[ $# -gt 0 ]]; do
    case "$1" in
        --test20) TEST20=1; shift ;;
        -h|--help)
            echo "usage: $0 [--test20]"
            echo "  --test20  arm MCC Test-20 (02 00 70 00 7F) so every button dumps CC"
            exit 0
            ;;
        *)
            echo "unknown argument: $1" >&2
            exit 2
            ;;
    esac
done

LOG="$CAP/occupancy-$STAMP$([ "$TEST20" -eq 1 ] && echo -test20).txt"

if [[ ! -f "$PROMPTS" ]]; then
    echo "missing $PROMPTS" >&2
    exit 2
fi

mkdir -p "$CAP"

AMIDI=(amidi)
if ! amidi -l >/dev/null 2>&1; then
    AMIDI=(sudo amidi)
fi

PORT="$("${AMIDI[@]}" -l 2>/dev/null | awk '/KeyStep 37|A37|hw:/ {for (i=1;i<=NF;i++) if ($i ~ /^hw:/) {print $i; exit}}')"
if [[ -z "${PORT:-}" ]]; then
    echo "no amidi port — attach the KeyStep (stock or e3b) to WSL" >&2
    echo "  ./scripts/keystep-see.sh" >&2
    exit 1
fi

if [[ -e /dev/snd/midiC0D0 ]]; then
    sudo fuser -k /dev/snd/midiC0D0 >/dev/null 2>&1 || true
    sleep 0.2
fi

ARM_GATE="F0 00 20 6B 7F 42 02 7D 7D 09 7F F7"
ARM_TEST="F0 00 20 6B 7F 42 02 00 70 00 7F F7"
DISARM_TEST="F0 00 20 6B 7F 42 02 00 70 00 00 F7"
DISARM_GATE="F0 00 20 6B 7F 42 02 7D 7D 09 00 F7"

sysex() {
    "${AMIDI[@]}" -p "$PORT" -S "$1" >/dev/null 2>&1 || true
}

arm_test20() {
    sysex "$ARM_GATE"
    sysex "$ARM_TEST"
}

disarm_test20() {
    sysex "$DISARM_TEST"
    sysex "$DISARM_GATE"
}

{
    echo "=== occupancy $STAMP port=$PORT test20=$TEST20 ==="
    echo "device: stock or e3b, attached to WSL"
    echo "fill Live MIDI in firmware-re/notes/stock-shift-map.md after this log"
    echo "occupied = MIDI CH change, Rec start, sequence-note clear, or Note-On suppressed"
    if [[ "$TEST20" -eq 1 ]]; then
        echo "Test-20 armed each step (MCC MIDI check 02 00 70 00 7F)"
    fi
    echo
} | tee "$LOG"

AMIDI_PID=""
cleanup() {
    if [[ "$TEST20" -eq 1 ]]; then
        disarm_test20
    fi
    if [[ -n "${AMIDI_PID:-}" ]]; then
        kill "$AMIDI_PID" 2>/dev/null || sudo -n kill "$AMIDI_PID" 2>/dev/null || true
        wait "$AMIDI_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

"${AMIDI[@]}" -p "$PORT" -d -T realtime >>"$LOG" 2>&1 &
AMIDI_PID=$!
sleep 0.3
if ! kill -0 "$AMIDI_PID" 2>/dev/null; then
    echo "amidi -d failed — is the rawmidi free?" >&2
    exit 1
fi

echo "Listening on $PORT → $LOG"
if [[ "$TEST20" -eq 1 ]]; then
    echo "Test-20 ON — raw CCs for every physical control. Re-armed before each step."
else
    echo "Stock MIDI. For button CCs: $0 --test20"
fi
echo "Do each gesture, then Enter. Ctrl-C aborts (log is kept)."
echo "Skipped: Rec+Stop+Play, factory rST, MCC clockwise chase."
echo

while IFS=$'\t' read -r id prompt || [[ -n "${id:-}" ]]; do
    [[ -z "${id:-}" || "$id" =~ ^# ]] && continue
    if [[ "$id" == "SKIP" ]]; then
        msg="SKIP (do not perform): $prompt"
        echo "$msg"
        printf '\n===== %s =====\n' "$msg" >>"$LOG"
        continue
    fi
    msg="STEP $id: $prompt"
    echo
    echo "$msg"
    printf '\n===== %s =====\n' "$msg" >>"$LOG"
    if [[ "$TEST20" -eq 1 ]]; then
        arm_test20
        echo "  Test-20 armed — do the gesture now"
    fi
    printf '  do it, then Enter (s = skip this step): '
    reply=""
    if ! read -r reply </dev/tty; then
        echo
        echo "EOF — stopping. log $LOG"
        break
    fi
    if [[ "$reply" == [sS] ]]; then
        echo "  skipped by operator" | tee -a "$LOG"
    else
        echo "  done" >>"$LOG"
        if [[ -f "$CCPY" ]]; then
            summary="$("$PYTHON" "$CCPY" last "$LOG" 2>/dev/null || true)"
            if [[ -n "$summary" ]]; then
                echo "  $summary"
                echo "  # $summary" >>"$LOG"
            fi
        fi
    fi
done < "$PROMPTS"

echo
echo "PASS log $LOG"
if [[ -f "$CCPY" ]]; then
    echo "=== CC report ==="
    "$PYTHON" "$CCPY" report "$LOG" || true
fi
echo "Fill Live MIDI in firmware-re/notes/stock-shift-map.md from this capture."
echo "Empty cells only are latch candidates."
