#!/usr/bin/env bash
set -euo pipefail

usage() {
	echo "Usage: $0 <image.raw> <uki-name>" >&2
	exit 1
}

[ $# -eq 2 ] || usage

IMAGE="$1"
UKI_NAME="$2"

if [ ! -f "$IMAGE" ]; then
	echo "error: $IMAGE: no such file" >&2
	exit 1
fi

MOUNTPOINT=$(mktemp -d)

cleanup() {
	sudo systemd-dissect --umount "$MOUNTPOINT" 2>/dev/null || true
	rmdir "$MOUNTPOINT" 2>/dev/null || true
}
trap cleanup EXIT

sudo systemd-dissect --mount "$IMAGE" "$MOUNTPOINT"

UKI_DIR="$MOUNTPOINT/boot/EFI/Linux"
UKI=$(sudo find "$UKI_DIR" -maxdepth 1 -name '*.efi' -type f)

if [ -z "$UKI" ]; then
	echo "error: no UKI found in $UKI_DIR" >&2
	exit 1
fi

if [ "$(echo "$UKI" | wc -l)" -gt 1 ]; then
	echo "error: multiple UKIs found in $UKI_DIR" >&2
	exit 1
fi

sudo mv "$UKI" "$UKI_DIR/$UKI_NAME"
sudo cp "$UKI_DIR/$UKI_NAME" "$UKI_NAME"

echo "$UKI_NAME"
