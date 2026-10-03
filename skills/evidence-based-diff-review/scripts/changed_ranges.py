#!/usr/bin/env python3
"""Extract old and new line ranges from a zero-context Git patch."""

from __future__ import annotations

import argparse
import ast
import json
import re
import shlex
import sys
from pathlib import Path
from typing import TextIO


HUNK = re.compile(
    r"^@@ -(?P<old_start>\d+)(?:,(?P<old_count>\d+))?"
    r" \+(?P<new_start>\d+)(?:,(?P<new_count>\d+))? @@"
)
SIMILARITY = re.compile(r"^similarity index (?P<value>\d+)%$")


def git_path(value: str, prefix: str | None = None) -> str | None:
    value = value.rstrip("\n").split("\t", 1)[0]
    if value == "/dev/null":
        return None
    if value.startswith('"'):
        value = ast.literal_eval(value)
    if prefix and value.startswith(prefix):
        value = value[len(prefix) :]
    return value


def merge_ranges(ranges: list[list[int]]) -> list[list[int]]:
    merged: list[list[int]] = []
    for start, end in sorted(ranges):
        if merged and start <= merged[-1][1] + 1:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged


def parse_patch(stream: TextIO) -> list[dict[str, object]]:
    files: list[dict[str, object]] = []
    current: dict[str, object] | None = None

    def finish() -> None:
        nonlocal current
        if current is None:
            return
        current["old_ranges"] = merge_ranges(current["old_ranges"])  # type: ignore[arg-type]
        current["new_ranges"] = merge_ranges(current["new_ranges"])  # type: ignore[arg-type]
        current["deletion_anchors"] = sorted(set(current["deletion_anchors"]))  # type: ignore[arg-type]
        current["old_changed_lines"] = sum(
            end - start + 1 for start, end in current["old_ranges"]  # type: ignore[union-attr]
        )
        current["new_changed_lines"] = sum(
            end - start + 1 for start, end in current["new_ranges"]  # type: ignore[union-attr]
        )
        files.append(current)
        current = None

    for line in stream:
        if line.startswith("diff --git "):
            finish()
            parts = shlex.split(line)
            old_path = git_path(parts[2], "a/") if len(parts) >= 4 else None
            new_path = git_path(parts[3], "b/") if len(parts) >= 4 else None
            current = {
                "old_path": old_path,
                "new_path": new_path,
                "status": "modified",
                "similarity": None,
                "old_ranges": [],
                "new_ranges": [],
                "deletion_anchors": [],
            }
            continue

        if current is None:
            continue

        if line.startswith("new file mode "):
            current["status"] = "added"
        elif line.startswith("deleted file mode "):
            current["status"] = "deleted"
        elif line.startswith("rename from "):
            current["status"] = "renamed"
            current["old_path"] = git_path(line.removeprefix("rename from "))
        elif line.startswith("rename to "):
            current["status"] = "renamed"
            current["new_path"] = git_path(line.removeprefix("rename to "))
        elif line.startswith("--- "):
            current["old_path"] = git_path(line.removeprefix("--- "), "a/")
        elif line.startswith("+++ "):
            current["new_path"] = git_path(line.removeprefix("+++ "), "b/")
        elif match := SIMILARITY.match(line.rstrip("\n")):
            current["similarity"] = int(match.group("value"))
        elif match := HUNK.match(line):
            old_start = int(match.group("old_start"))
            old_count = int(match.group("old_count") or 1)
            new_start = int(match.group("new_start"))
            new_count = int(match.group("new_count") or 1)

            if old_count:
                current["old_ranges"].append(  # type: ignore[union-attr]
                    [old_start, old_start + old_count - 1]
                )
            if new_count:
                current["new_ranges"].append(  # type: ignore[union-attr]
                    [new_start, new_start + new_count - 1]
                )
            else:
                current["deletion_anchors"].append(max(1, new_start))  # type: ignore[union-attr]

    finish()
    return files


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert `git diff --unified=0` output to JSON line ranges."
    )
    parser.add_argument("patch", nargs="?", help="Patch file; omit or use - for stdin")
    args = parser.parse_args()

    if not args.patch or args.patch == "-":
        files = parse_patch(sys.stdin)
    else:
        with Path(args.patch).open(encoding="utf-8", errors="replace") as stream:
            files = parse_patch(stream)

    summary = {
        "files": len(files),
        "old_changed_lines": sum(int(item["old_changed_lines"]) for item in files),
        "new_changed_lines": sum(int(item["new_changed_lines"]) for item in files),
        "deleted_file_lines": sum(
            int(item["old_changed_lines"]) for item in files if item["status"] == "deleted"
        ),
        "added_file_lines": sum(
            int(item["new_changed_lines"]) for item in files if item["status"] == "added"
        ),
        "renamed_files": sum(item["status"] == "renamed" for item in files),
    }
    json.dump(
        {"schema_version": 2, "summary": summary, "files": files},
        sys.stdout,
        indent=2,
    )
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
