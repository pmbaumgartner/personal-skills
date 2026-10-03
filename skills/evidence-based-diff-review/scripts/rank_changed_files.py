#!/usr/bin/env python3
"""Join rename-aware SCC file metrics and rank changed files."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def unwrap_many(payload: Any) -> list[dict[str, Any]]:
    """Accept direct SCC JSON, common MCP envelopes, or batched call results."""
    if isinstance(payload, str):
        return unwrap_many(json.loads(payload))
    if isinstance(payload, list):
        reports: list[dict[str, Any]] = []
        for item in payload:
            reports.extend(unwrap_many(item))
        return reports
    if not isinstance(payload, dict):
        raise ValueError("expected a JSON object")
    if "languages" in payload or payload.get("report") == "hotspots":
        return [payload]
    if payload.get("ok") is True and "data" in payload:
        return unwrap_many(payload["data"])
    reports = []
    for key in ("base", "head", "result", "results"):
        if payload.get(key) is not None:
            try:
                reports.extend(unwrap_many(payload[key]))
            except ValueError:
                pass
    content = payload.get("content")
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                try:
                    reports.extend(unwrap_many(block["text"]))
                except (ValueError, json.JSONDecodeError):
                    pass
    if reports:
        return reports
    raise ValueError("could not find SCC JSON in payload")


def load_many(path: str) -> list[dict[str, Any]]:
    with Path(path).open(encoding="utf-8") as stream:
        return unwrap_many(json.load(stream))


def relative_path(location: str, root: Path) -> str:
    path = Path(location)
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        prefix = root.as_posix().rstrip("/") + "/"
        return location[len(prefix) :] if location.startswith(prefix) else location


def collect_analyses(paths: list[str], root: Path) -> dict[str, dict[str, Any]]:
    files: dict[str, dict[str, Any]] = {}
    for source in paths:
        for report in load_many(source):
            for language in report.get("languages", []):
                for item in language.get("fileList", []):
                    files[relative_path(item["location"], root)] = item
    return files


def metric(item: dict[str, Any] | None, name: str) -> int | None:
    return None if item is None or item.get(name) is None else int(item[name])


def delta(before: int | None, after: int | None) -> int | None:
    return None if before is None or after is None else after - before


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Join SCC analyses using changed_ranges.py rename mappings."
    )
    parser.add_argument("ranges", help="JSON emitted by changed_ranges.py")
    parser.add_argument("--base-root", required=True)
    parser.add_argument("--head-root", required=True)
    parser.add_argument("--base-analysis", nargs="*", default=[])
    parser.add_argument("--head-analysis", nargs="*", default=[])
    parser.add_argument("--hotspots")
    parser.add_argument("--hunk-kinds", help="JSON emitted by classify_hunks.py")
    parser.add_argument("--limit", type=int, default=0, help="0 emits every changed file")
    args = parser.parse_args()

    with Path(args.ranges).open(encoding="utf-8") as stream:
        changes = json.load(stream)["files"]
    base = collect_analyses(args.base_analysis, Path(args.base_root))
    head = collect_analyses(args.head_analysis, Path(args.head_root))
    hotspot_reports = load_many(args.hotspots) if args.hotspots else []
    hotspot_report = next(
        (report for report in hotspot_reports if report.get("report") == "hotspots"),
        {},
    )
    hotspots = {item["file"]: item for item in hotspot_report.get("files", [])}
    hunk_kinds: dict[str, dict[str, Any]] = {}
    if args.hunk_kinds:
        with Path(args.hunk_kinds).open(encoding="utf-8") as stream:
            classified = json.load(stream)
        hunk_kinds = {
            item.get("new_path") or item.get("old_path"): item
            for item in classified.get("files", [])
        }

    rows = []
    for change in changes:
        old_path = change.get("old_path")
        new_path = change.get("new_path")
        before = base.get(old_path) if old_path else None
        after = head.get(new_path) if new_path else None
        hotspot = hotspots.get(new_path or old_path, {})
        classified = hunk_kinds.get(new_path or old_path, {})
        before_cyc = metric(before, "complexity")
        after_cyc = metric(after, "complexity")
        before_cog = metric(before, "cognitive")
        after_cog = metric(after, "cognitive")
        hotspot_observed = (new_path or old_path) in hotspots
        rows.append(
            {
                "status": change["status"],
                "similarity": change.get("similarity"),
                "old_path": old_path,
                "new_path": new_path,
                "cyclomatic": {
                    "before": before_cyc,
                    "after": after_cyc,
                    "delta": delta(before_cyc, after_cyc),
                },
                "cognitive": {
                    "before": before_cog,
                    "after": after_cog,
                    "delta": delta(before_cog, after_cog),
                },
                "head_lines": metric(after, "lines"),
                "hunks": {
                    "kinds": classified.get("kinds"),
                    "structural": classified.get("structural_hunks"),
                },
                "hotspot": {
                    "status": (
                        "observed" if hotspot_observed else "unknown_not_returned"
                    ),
                    **{
                        key: hotspot.get(key)
                        for key in ("score", "commits", "linesChanged", "authors")
                    },
                },
            }
        )

    def rank(row: dict[str, Any]) -> tuple[Any, ...]:
        cog = row["cognitive"]
        cyc = row["cyclomatic"]
        cog_delta = cog["delta"]
        cyc_delta = cyc["delta"]
        return (
            -max(0, cog_delta or 0),
            -max(0, cyc_delta or 0),
            0 if row["hotspot"]["status"] == "observed" else 1,
            -(row["hotspot"]["score"] or 0),
            -(cog["after"] or 0),
            -max(0, -(cog_delta or 0)),
            row["new_path"] or row["old_path"] or "",
        )

    rows.sort(key=rank)
    if args.limit > 0:
        rows = rows[: args.limit]
    json.dump(
        {
            "schema_version": 2,
            "hotspots": {
                "returned_files": len(hotspots),
                "window": hotspot_report.get("window"),
            },
            "files": rows,
        },
        sys.stdout,
        indent=2,
    )
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
