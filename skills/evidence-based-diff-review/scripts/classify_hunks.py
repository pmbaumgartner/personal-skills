#!/usr/bin/env python3
"""Classify Git patch hunks for review routing, not semantic safety."""

from __future__ import annotations

import argparse
import ast
import io
import json
import re
import shlex
import sys
import tokenize
from pathlib import Path
from typing import Any


HUNK = re.compile(
    r"^@@ -(?P<old_start>\d+)(?:,(?P<old_count>\d+))?"
    r" \+(?P<new_start>\d+)(?:,(?P<new_count>\d+))? @@"
)
IGNORED_TOKENS = {
    tokenize.ENCODING,
    tokenize.ENDMARKER,
    tokenize.INDENT,
    tokenize.DEDENT,
    tokenize.NEWLINE,
    tokenize.NL,
}


def git_path(value: str, prefix: str | None = None) -> str | None:
    value = value.rstrip("\n").split("\t", 1)[0]
    if value == "/dev/null":
        return None
    if value.startswith('"'):
        value = ast.literal_eval(value)
    if prefix and value.startswith(prefix):
        value = value[len(prefix) :]
    return value


def parse_patch(path: Path) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    active: dict[str, Any] | None = None

    def finish_file() -> None:
        nonlocal current, active
        if current is not None:
            files.append(current)
        current = None
        active = None

    with path.open(encoding="utf-8", errors="replace") as stream:
        for line in stream:
            if line.startswith("diff --git "):
                finish_file()
                parts = shlex.split(line)
                current = {
                    "old_path": git_path(parts[2], "a/"),
                    "new_path": git_path(parts[3], "b/"),
                    "hunks": [],
                }
            elif current is None:
                continue
            elif line.startswith("--- "):
                current["old_path"] = git_path(line.removeprefix("--- "), "a/")
            elif line.startswith("+++ "):
                current["new_path"] = git_path(line.removeprefix("+++ "), "b/")
            elif match := HUNK.match(line):
                old_count = int(match.group("old_count") or 1)
                new_count = int(match.group("new_count") or 1)
                active = {
                    "old_start": int(match.group("old_start")),
                    "old_count": old_count,
                    "new_start": int(match.group("new_start")),
                    "new_count": new_count,
                    "removed": [],
                    "added": [],
                }
                current["hunks"].append(active)
            elif active is not None and line.startswith("-") and not line.startswith("---"):
                active["removed"].append(line[1:].rstrip("\n"))
            elif active is not None and line.startswith("+") and not line.startswith("+++"):
                active["added"].append(line[1:].rstrip("\n"))
    finish_file()
    return files


def tokens(lines: list[str], *, ignore_comments: bool = False) -> list[tuple[int, str]]:
    source = "\n".join(lines) + "\n"
    result: list[tuple[int, str]] = []
    try:
        generated = tokenize.generate_tokens(io.StringIO(source).readline)
        for token in generated:
            if token.type in IGNORED_TOKENS:
                continue
            if ignore_comments and token.type == tokenize.COMMENT:
                continue
            result.append((token.type, token.string))
    except (IndentationError, tokenize.TokenError):
        # Zero-context hunks commonly contain incomplete indented expressions.
        # Tokens emitted before EOF are still useful for conservative routing.
        pass
    return result


def same_shape(
    before: list[tuple[int, str]],
    after: list[tuple[int, str]],
    replaceable: set[int],
) -> bool:
    if len(before) != len(after):
        return False
    for left, right in zip(before, after):
        if left == right:
            continue
        if left[0] != right[0] or left[0] not in replaceable:
            return False
    return True


def import_spans(path: Path | None) -> list[tuple[int, int]]:
    if path is None or not path.is_file() or path.suffix != ".py":
        return []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return []
    return [
        (node.lineno, getattr(node, "end_lineno", node.lineno))
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
    ]


def inside_import(start: int, count: int, spans: list[tuple[int, int]]) -> bool:
    if count == 0:
        return False
    end = start + count - 1
    return any(span_start <= start and end <= span_end for span_start, span_end in spans)


def classify(
    hunk: dict[str, Any],
    old_imports: list[tuple[int, int]],
    new_imports: list[tuple[int, int]],
) -> str:
    before = tokens(hunk["removed"])
    after = tokens(hunk["added"])
    before_code = tokens(hunk["removed"], ignore_comments=True)
    after_code = tokens(hunk["added"], ignore_comments=True)

    if before == after and hunk["removed"] != hunk["added"]:
        return "formatting_only"
    if before_code == after_code and before != after:
        return "comment_only"
    if inside_import(hunk["old_start"], hunk["old_count"], old_imports) and inside_import(
        hunk["new_start"], hunk["new_count"], new_imports
    ):
        return "import_only"
    if before and before != after and same_shape(before, after, {tokenize.NAME}):
        return "identifier_only"
    if before and before != after and same_shape(before, after, {tokenize.STRING}):
        return "string_only"
    if before and before != after and same_shape(
        before, after, {tokenize.NAME, tokenize.STRING, tokenize.NUMBER, tokenize.COMMENT}
    ):
        return "lexical_only"
    return "structural"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("patch", help="zero-context Git patch")
    parser.add_argument("--base-root", required=True)
    parser.add_argument("--head-root", required=True)
    args = parser.parse_args()

    base_root = Path(args.base_root)
    head_root = Path(args.head_root)
    files = parse_patch(Path(args.patch))
    totals: dict[str, int] = {}

    for item in files:
        old_path = item["old_path"]
        new_path = item["new_path"]
        old_file = base_root / old_path if old_path else None
        new_file = head_root / new_path if new_path else None
        old_imports = import_spans(old_file)
        new_imports = import_spans(new_file)
        counts: dict[str, int] = {}
        for hunk in item["hunks"]:
            kind = classify(hunk, old_imports, new_imports)
            hunk["kind"] = kind
            del hunk["removed"]
            del hunk["added"]
            counts[kind] = counts.get(kind, 0) + 1
            totals[kind] = totals.get(kind, 0) + 1
        item["kinds"] = counts
        item["structural_hunks"] = counts.get("structural", 0)

    json.dump(
        {
            "schema_version": 1,
            "warning": "Routing hints only; lexical classifications do not prove semantic safety.",
            "summary": {"files": len(files), "hunks": sum(totals.values()), "kinds": totals},
            "files": files,
        },
        fp=sys.stdout,
        indent=2,
    )
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
