#!/usr/bin/env bash
set -euo pipefail

usage() {
	echo "Usage: $0 <image.raw> <usr-name>" >&2
	exit 1
}

[ $# -eq 2 ] || usage

IMAGE="$1"
USR_NAME="$2"

if [ ! -f "$IMAGE" ]; then
	echo "error: $IMAGE: no such file" >&2
	exit 1
fi

USR_X86_64="8484680c-9521-48c6-9c11-b0720656f69e"
USR_AARCH64="b0e01050-ee5f-4390-949a-9101b17104e9"

PARTITIONS=$(sfdisk --json "$IMAGE")

USR=$(echo "$PARTITIONS" | jq -r \
	--arg x86 "$USR_X86_64" \
	--arg arm "$USR_AARCH64" \
	'.partitiontable.partitions[] | select((.type | ascii_downcase) == $x86 or (.type | ascii_downcase) == $arm)')

if [ -z "$USR" ]; then
	echo "error: no usr partition found in $IMAGE" >&2
	exit 1
fi

if [ "$(echo "$USR" | jq -s 'length')" -gt 1 ]; then
	echo "error: multiple usr partitions found in $IMAGE" >&2
	exit 1
fi

START=$(echo "$USR" | jq -r '.start')
SIZE=$(echo "$USR" | jq -r '.size')

dd if="$IMAGE" of="$USR_NAME" bs=512 skip="$START" count="$SIZE" status=progress

echo "$USR_NAME"
