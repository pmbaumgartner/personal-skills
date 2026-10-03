#!/usr/bin/env python3
"""Remove filesystem artifacts created by prepare_review.py."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


MARKER = ".evidence-based-diff-review.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("review_root")
    args = parser.parse_args()

    root = Path(args.review_root).resolve()
    marker = root / MARKER
    if not marker.is_file():
        parser.error(f"refusing to remove unmarked directory: {root}")
    manifest = json.loads(marker.read_text(encoding="utf-8"))
    if (
        manifest.get("kind") != "evidence-based-diff-review"
        or Path(manifest.get("root", "")).resolve() != root
        or root == Path(root.anchor)
    ):
        parser.error("invalid review manifest")

    repo = Path(manifest["repo"])
    for key in ("base", "head"):
        path = Path(manifest["paths"][key])
        subprocess.run(
            ["git", "-C", str(repo), "worktree", "remove", "--force", str(path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    shutil.rmtree(root)
    print(f"removed {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
