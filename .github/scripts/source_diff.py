#!/usr/bin/env python3
"""Print a readable diff of fetched inputs in two osbuild manifests."""

import argparse
import difflib
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit


def sources_from_manifest(path):
    manifest = json.loads(Path(path).read_text())
    sources = manifest.get("sources")
    if not isinstance(sources, dict):
        raise ValueError(f"{path}: manifest sources must be an object")
    return sources


def source_label(item):
    """Put RPM filenames and container names ahead of checksums and options."""
    if isinstance(item, str):
        url = item
    elif isinstance(item, dict):
        url = item.get("url") or item.get("path", "")
    else:
        return ""
    if url:
        return unquote(urlsplit(url).path.rsplit("/", 1)[-1]) or url
    if isinstance(item, dict):
        return item.get("image", {}).get("name", "")
    return ""


def source_lines(sources):
    lines = []
    for kind, source in sorted(sources.items()):
        # Include source-wide options as well as items so every change used by
        # the build-skipping comparison is also visible in the report.
        options = {key: value for key, value in source.items() if key != "items"}
        if "items" not in source:
            options["items"] = "<absent>"
        lines.append(f"{kind}: {json.dumps(options, sort_keys=True)}\n")
        items = source.get("items", {})
        for checksum, item in sorted(items.items(), key=lambda pair: (source_label(pair[1]), pair[0])):
            label = json.dumps(source_label(item), ensure_ascii=True)
            details = json.dumps(item, sort_keys=True, ensure_ascii=True)
            lines.append(f"{kind} {label}: {checksum} {details}\n")
    return lines


def source_diff(published, current):
    if published == current:
        return "No source changes.\n"
    return "".join(difflib.unified_diff(
        source_lines(published), source_lines(current),
        fromfile="published sources", tofile="current sources", n=0,
    ))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("published", help="Previously published osbuild manifest")
    parser.add_argument("current", help="Newly generated osbuild manifest")
    args = parser.parse_args()
    print(source_diff(sources_from_manifest(args.published),
                      sources_from_manifest(args.current)), end="")


if __name__ == "__main__":
    main()
