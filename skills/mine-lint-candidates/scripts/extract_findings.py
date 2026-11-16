#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# ///
"""Extract review findings from agent sessions through the agentsview CLI.

Finds sessions whose messages mention any PATTERN (review vocabulary by
default, or a review skill's name),
keeps the long assistant messages that look like review output after the first
mention, and writes OUT as JSONL: one deduplicated finding per line, with its
project, excerpt, session ID, message ordinal, and excerpt truncation status.
Prints each project's item count and checkout directory.
"""

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

PAGE = 500
DEFAULT_PATTERNS = ["Findings", "Severity", "code review"]
WINDOW = 12  # review messages kept per session
MIN_LENGTH = 1200
# A message counts as review output when it has enough of these markers.
FINDING_MARKER = re.compile(
    r"(?im)finding|severity|blocker|\bP[0-3]\b|\bhigh\b|\bmedium\b|[\w/.-]+\.\w{1,5}:\d+"
)
# Items start at headings, numbered bold items, or bold bullets.
ITEM_START = re.compile(r"\n(?=#{2,4} |\d+\. \*\*|\*\*\d+[.)]|- \*\*|\d+\. `)")


def agentsview(*args: str) -> dict:
    result = subprocess.run(
        ["agentsview", *args, "--json"], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        sys.exit(f"agentsview {' '.join(args)} failed:\n{result.stderr}")
    return json.loads(result.stdout or "{}")


def find_sessions(patterns: list[str], since: str, excluded: set[str]) -> dict:
    sessions: dict[str, dict] = {}
    for pattern in patterns:
        cursor = 0
        while True:
            found = agentsview(
                "session", "search", pattern, "--in", "messages", "--since", since,
                "--limit", str(PAGE), "--cursor", str(cursor), "--include-children",
            )  # fmt: skip
            for match in found.get("matches", []):
                if match.get("project") in excluded:
                    continue
                ordinal = int(match.get("ordinal") or 0)
                session = sessions.setdefault(
                    match["session_id"],
                    {"project": match.get("project") or "unknown", "first": ordinal},
                )
                session["first"] = min(session["first"], ordinal)
            cursor = found.get("next_cursor") or 0
            if not cursor:
                break
    return sessions


def review_messages(session_id: str, first: int) -> list[dict]:
    kept: list[dict] = []
    start = first
    while len(kept) < WINDOW:
        page = agentsview(
            "session", "messages", session_id, "--from", str(start),
            "--limit", str(PAGE), "--role", "assistant",
        ).get("messages", [])  # fmt: skip
        for message in page:
            content = message.get("content") or ""
            if len(content) >= MIN_LENGTH and len(FINDING_MARKER.findall(content)) >= 4:
                kept.append(message)
                if len(kept) == WINDOW:
                    break
        if len(page) < PAGE:
            break
        start = int(page[-1]["ordinal"]) + 1
    return kept


def split_items(text: str) -> list[dict]:
    items = []
    for chunk in ITEM_START.split(text):
        chunk = chunk.strip()
        if 150 < len(chunk) < 2500 and "`" in chunk:
            text = " ".join(chunk.split())
            items.append({"text": text[:700], "truncated": len(text) > 700})
    return items


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "patterns",
        nargs="*",
        default=DEFAULT_PATTERNS,
        help=f"text marking a review, e.g. a skill name (default: {DEFAULT_PATTERNS})",
    )
    parser.add_argument(
        "--out", type=Path, required=True, help="JSONL items file to write"
    )
    parser.add_argument("--since", default="1y")
    parser.add_argument(
        "--exclude-project", action="append", default=[],
        help="skip sessions in this project, e.g. where the review skills are edited",
    )  # fmt: skip
    args = parser.parse_args()

    sessions = find_sessions(args.patterns, args.since, set(args.exclude_project))
    items: dict[tuple[str, str], dict] = {}
    checkouts: dict[str, str] = {}
    for session_id, session in sessions.items():
        project = session["project"]
        messages = review_messages(session_id, session["first"])
        if messages and project not in checkouts:
            checkouts[project] = agentsview("session", "get", session_id).get("cwd", "")
        for message in messages:
            for item in split_items(message["content"]):
                items.setdefault(
                    (project, item["text"][:160]),
                    {
                        "project": project,
                        **item,
                        "session_id": session_id,
                        "ordinal": int(message["ordinal"]),
                    },
                )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        "".join(json.dumps(item, ensure_ascii=False) + "\n" for item in items.values()),
        encoding="utf-8",
    )
    per_project = Counter(item["project"] for item in items.values())
    print(f"{len(sessions)} sessions matched; {len(items)} items in {args.out}")
    for project, count in per_project.most_common():
        print(f"{count:5d}  {project}  {checkouts.get(project, '')}")


if __name__ == "__main__":
    main()
