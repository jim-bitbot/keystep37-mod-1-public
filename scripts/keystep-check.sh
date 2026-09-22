#!/usr/bin/env bash
# Compatibility wrapper. Gate 0 lives in keystep-see.sh.
exec "$(cd "$(dirname "$0")" && pwd)/keystep-see.sh"
