#!/usr/bin/env python3
"""Keep the newest build versions in the artifact, update, and extension buckets."""

import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import subprocess
import tempfile


BUCKETS = ("teamsbc-artifacts", "teamsbc-updates", "teamsbc-extensions")
OBJECT = re.compile(
    r"(?P<prefix>.+/(?P<major>[0-9]+)/[^/]+/(?P<type>teamsbc-[^/]+)/)"
    r"(?P<meta>meta/)?(?P=type)-"
    r"(?P<version>(?P=major)\.[0-9]{8}\.[0-9]+)"
    r"(?P<suffix>\.[^/]+)"
)
PAYLOADS = {
    "teamsbc-artifacts": r"\.raw\.xz",
    "teamsbc-updates": r"\.(?:usr\.raw\.xz|efi)",
    "teamsbc-extensions": r"\.[a-zA-Z0-9_.-]+\.sysext\.erofs",
}


def aws_json(*args):
    output = subprocess.check_output([
        "aws", "s3api", *args, "--output", "json", "--no-cli-pager",
    ])
    # A successful quiet DeleteObjects response can produce no CLI output.
    # Listings must still return valid JSON before any deletion is attempted.
    if args[0] == "delete-objects" and not output.strip():
        return {}
    return json.loads(output)


def list_keys(bucket):
    # AWS CLI automatically fetches all pages before producing JSON output.
    listing = aws_json("list-objects-v2", "--bucket", bucket)
    return [item["Key"] for item in listing.get("Contents", [])]


def retention_plan(bucket, keys, keep=3):
    """Group only known published files, including metadata and sidecars."""
    if keep < 1:
        raise ValueError("At least one build version must be retained")
    groups = defaultdict(lambda: defaultdict(list))
    for key in keys:
        match = OBJECT.fullmatch(key)
        if not match:
            continue
        suffix = r"\.json" if match["meta"] else PAYLOADS[bucket]
        if not re.fullmatch(f"(?:{suffix})(?:\\.sha256)?", match["suffix"]):
            continue
        groups[match["prefix"]][match["version"]].append(key)

    retained, deleted = {}, []
    for prefix, versions in sorted(groups.items()):
        newest = sorted(versions, key=lambda v: tuple(map(int, v.split("."))), reverse=True)
        retained[prefix] = newest[:keep]
        for version in newest[keep:]:
            deleted.extend(versions[version])
    return retained, sorted(deleted)


def delete_keys(bucket, keys):
    # DeleteObjects accepts at most 1,000 keys and may report individual errors
    # even when the request itself succeeds.
    with tempfile.TemporaryDirectory() as directory:
        request = Path(directory) / "delete.json"
        for start in range(0, len(keys), 1000):
            request.write_text(json.dumps({
                "Objects": [{"Key": key} for key in keys[start:start + 1000]],
                "Quiet": True,
            }))
            result = aws_json("delete-objects", "--bucket", bucket,
                              "--delete", f"file://{request}")
            if result.get("Errors"):
                raise RuntimeError(f"Deletion failed in {bucket}: {json.dumps(result['Errors'])}")


def cleanup(buckets, keep=3, apply=False):
    # Finish listing and planning every bucket before deleting anything.
    plans = {}
    for bucket in buckets:
        retained, deleted = retention_plan(bucket, list_keys(bucket), keep)
        plans[bucket] = deleted
        for prefix, versions in retained.items():
            print(f"Keep s3://{bucket}/{prefix}: {', '.join(versions)}")
        for key in deleted:
            print(f"{'Delete' if apply else 'Would delete'} s3://{bucket}/{key}")
        print(f"{bucket}: {len(deleted)} objects selected for deletion")
    if apply:
        for bucket, keys in plans.items():
            delete_keys(bucket, keys)
    else:
        print("Dry run; pass --apply to delete the selected objects.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keep", type=int, default=3)
    parser.add_argument("--bucket", choices=BUCKETS, action="append",
                        help="Bucket to clean (repeatable; default: all three)")
    parser.add_argument("--apply", action="store_true", help="Delete objects; default is a dry run")
    args = parser.parse_args()
    if args.keep < 1:
        parser.error("--keep must be at least 1")
    cleanup(args.bucket or BUCKETS, args.keep, args.apply)


if __name__ == "__main__":
    main()
