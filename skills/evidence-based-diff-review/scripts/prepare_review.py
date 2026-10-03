#!/usr/bin/env python3
"""Prepare pinned Git snapshots and patch artifacts for a diff review."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


MARKER = ".evidence-based-diff-review.json"


def run(*args: str, cwd: Path | None = None, stdout=None) -> str:
    result = subprocess.run(
        args,
        cwd=cwd,
        check=True,
        text=stdout is None,
        stdout=stdout or subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.strip() if stdout is None else ""


def remove_worktree(repo: Path, path: Path) -> None:
    subprocess.run(
        ["git", "-C", str(repo), "worktree", "remove", "--force", str(path)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo")
    parser.add_argument("base")
    parser.add_argument("head")
    parser.add_argument("--output", help="new or empty artifact directory")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    if args.output:
        root = Path(args.output).resolve()
        if root.exists() and any(root.iterdir()):
            parser.error(f"output directory is not empty: {root}")
        root.mkdir(parents=True, exist_ok=True)
    else:
        root = Path(tempfile.mkdtemp(prefix="diff-review-"))

    base_dir = root / "base"
    head_dir = root / "head"
    history_dir = root / "head-history"
    evidence = root / "evidence"
    evidence.mkdir()

    try:
        base_sha = run("git", "-C", str(repo), "rev-parse", f"{args.base}^{{commit}}")
        head_sha = run("git", "-C", str(repo), "rev-parse", f"{args.head}^{{commit}}")
        run("git", "-C", str(repo), "worktree", "add", "--detach", str(base_dir), base_sha)
        run("git", "-C", str(repo), "worktree", "add", "--detach", str(head_dir), head_sha)
        run("git", "clone", "--no-local", "--no-checkout", str(repo), str(history_dir))
        run("git", "-C", str(history_dir), "checkout", "--detach", head_sha)

        patch = evidence / "change.patch"
        hunks = evidence / "change.hunks.patch"
        with patch.open("w", encoding="utf-8") as stream:
            run(
                "git",
                "-C",
                str(head_dir),
                "diff",
                "--find-renames",
                f"{base_sha}..{head_sha}",
                stdout=stream,
            )
        with hunks.open("w", encoding="utf-8") as stream:
            run(
                "git",
                "-C",
                str(head_dir),
                "diff",
                "--find-renames",
                "--unified=0",
                f"{base_sha}..{head_sha}",
                stdout=stream,
            )

        scripts = Path(__file__).resolve().parent
        with (evidence / "change.ranges.json").open("w", encoding="utf-8") as stream:
            run(sys.executable, str(scripts / "changed_ranges.py"), str(hunks), stdout=stream)
        with (evidence / "change.hunk-kinds.json").open("w", encoding="utf-8") as stream:
            run(
                sys.executable,
                str(scripts / "classify_hunks.py"),
                str(hunks),
                "--base-root",
                str(base_dir),
                "--head-root",
                str(head_dir),
                stdout=stream,
            )

        manifest = {
            "schema_version": 1,
            "kind": "evidence-based-diff-review",
            "root": str(root),
            "repo": str(repo),
            "base": base_sha,
            "head": head_sha,
            "paths": {
                "base": str(base_dir),
                "head": str(head_dir),
                "history": str(history_dir),
                "evidence": str(evidence),
            },
            "shortstat": run(
                "git", "-C", str(head_dir), "diff", "--shortstat", f"{base_sha}..{head_sha}"
            ),
            "name_status": run(
                "git",
                "-C",
                str(head_dir),
                "diff",
                "--name-status",
                "--find-renames",
                f"{base_sha}..{head_sha}",
            ).splitlines(),
        }
        marker = root / MARKER
        marker.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(manifest, indent=2))
        return 0
    except Exception:
        remove_worktree(repo, base_dir)
        remove_worktree(repo, head_dir)
        shutil.rmtree(root, ignore_errors=True)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
