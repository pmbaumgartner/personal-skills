#!/usr/bin/env python3
"""Conservatively verify candidate non-Git symbol relocations."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


def normalized_source(path: Path, start: int, end: int) -> str:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if start < 1 or end < start or end > len(lines):
        raise ValueError(f"invalid span {start}-{end} for {path}")
    selected = [line.rstrip() for line in lines[start - 1 : end]]
    while selected and not selected[0]:
        selected.pop(0)
    while selected and not selected[-1]:
        selected.pop()
    return "\n".join(selected)


def verify(item: dict[str, Any], base: Path, head: Path) -> dict[str, Any]:
    required = (
        "old_path",
        "new_path",
        "old_start",
        "old_end",
        "new_start",
        "new_end",
        "old_signature",
        "new_signature",
    )
    missing = [key for key in required if key not in item]
    if missing:
        return {**item, "relocated": False, "reason": f"missing: {', '.join(missing)}"}

    if item["old_signature"].strip() != item["new_signature"].strip():
        return {**item, "relocated": False, "reason": "signature_mismatch"}

    try:
        old = normalized_source(
            base / item["old_path"], int(item["old_start"]), int(item["old_end"])
        )
        new = normalized_source(
            head / item["new_path"], int(item["new_start"]), int(item["new_end"])
        )
    except (OSError, ValueError) as error:
        return {**item, "relocated": False, "reason": str(error)}

    digest = hashlib.sha256(old.encode()).hexdigest()
    same = old == new
    return {
        **item,
        "relocated": same,
        "reason": "exact_normalized_match" if same else "body_mismatch",
        "sha256": digest if same else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidates", help="JSON array or object with a candidates array")
    parser.add_argument("--base-root", required=True)
    parser.add_argument("--head-root", required=True)
    args = parser.parse_args()

    with Path(args.candidates).open(encoding="utf-8") as stream:
        payload = json.load(stream)
    candidates = payload.get("candidates", []) if isinstance(payload, dict) else payload
    if not isinstance(candidates, list):
        raise SystemExit("candidates must be a JSON array")

    results = [
        verify(item, Path(args.base_root), Path(args.head_root)) for item in candidates
    ]
    json.dump({"schema_version": 1, "candidates": results}, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
