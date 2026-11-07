#!/usr/bin/env bash
set -u

source_dir=$1
destination=$2

# A failed multipart completion needs a new upload, not just another complete
# request. Repeat the copy so aws starts new uploads for failed objects.
for attempt in 1 2 3; do
  if aws s3 cp --recursive "$source_dir" "$destination" --no-progress; then
    exit 0
  fi
  if [ "$attempt" -eq 3 ]; then
    echo "Upload failed after $attempt attempts: $destination" >&2
    exit 1
  fi
  delay=$((attempt * 10))
  echo "Upload failed; retrying in $delay seconds (attempt $((attempt + 1))/3)." >&2
  sleep "$delay"
done
