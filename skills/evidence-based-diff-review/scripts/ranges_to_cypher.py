#!/usr/bin/env python3
"""Render hunk-intersection Cypher predicates from changed_ranges.py JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def quote(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'") + "'"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ranges", help="JSON emitted by changed_ranges.py")
    parser.add_argument("--path", action="append", dest="paths", default=[])
    parser.add_argument("--variable", default="f", help="Cypher node variable")
    parser.add_argument(
        "--deletion-anchors",
        action="store_true",
        help="include surviving-head deletion anchors; source validation is still required",
    )
    args = parser.parse_args()

    with Path(args.ranges).open(encoding="utf-8") as stream:
        files = json.load(stream)["files"]

    selected = set(args.paths)
    clauses: list[str] = []
    for change in files:
        path = change.get("new_path")
        if not path or (selected and path not in selected):
            continue
        ranges = [list(item) for item in change.get("new_ranges", [])]
        if args.deletion_anchors:
            ranges.extend([anchor, anchor] for anchor in change.get("deletion_anchors", []))
        if not ranges:
            continue
        spans = " OR ".join(
            f"({args.variable}.start_line <= {end} AND "
            f"{args.variable}.end_line >= {start})"
            for start, end in ranges
        )
        clauses.append(
            f"({args.variable}.file_path = {quote(path)} AND ({spans}))"
        )

    if not clauses:
        print("false")
        return 0
    print("(\n  " + "\n  OR ".join(clauses) + "\n)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
