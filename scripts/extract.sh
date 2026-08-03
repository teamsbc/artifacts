#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

usage() {
	echo "Usage: $0 <image.raw> <name>" >&2
	exit 1
}

[ $# -eq 2 ] || usage

IMAGE="$1"
NAME="$2"

"$SCRIPT_DIR/extract-uki.sh" "$IMAGE" "${NAME}.efi"
"$SCRIPT_DIR/extract-usr.sh" "$IMAGE" "${NAME}.img"
