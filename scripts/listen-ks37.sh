#!/usr/bin/env bash
# Score KeyStep MIDI against Euclidean / scale-chord flashes.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$ROOT/firmware-re/scripts/listen_ks37.py" "$@"
