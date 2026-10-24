#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["lizard==1.24.1"]
# ///
"""Report per-function lizard complexity before and after a Git change.

Diffs from the merge base of BASE and HEAD, like `git diff BASE...HEAD`.
Metrics select review attention; they are not findings.
"""

import argparse
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass

import lizard

# Switch/case counts as one decision, so adding dispatch cases is not growth.
EXTENSIONS = lizard.get_extensions(["modified", "cognitive"])
GROWN_CCN, GROWN_CCN_DELTA = 10, 3
GROWN_COGNITIVE, GROWN_COGNITIVE_DELTA = 15, 5
TINY_NLOC = 3
ANONYMOUS = "(anonymous)"
EXCLUDED = re.compile(
    r"(^|/)(node_modules|vendor|third_party|dist|build|coverage|fixtures|__fixtures__|testdata)/"
    r"|\.min\.[^/]+$|\.generated\.[^/]+$|_pb2\.py$|\.pb\.go$"
    r"|(^|/)(package-lock\.json|pnpm-lock\.yaml|yarn\.lock|uv\.lock|Cargo\.lock|poetry\.lock)$",
    re.IGNORECASE,
)
TEST = re.compile(
    r"(^|/)(tests?|__tests__|specs?)/|[._-](test|spec)\.[^/]+$|(^|/)test_[^/]+$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Fn:
    path: str
    name: str
    long_name: str
    line: int
    end: int
    nloc: int
    ccn: int
    cognitive: int
    params: int


def git(repo: str, *args: str) -> bytes:
    return subprocess.run(
        ["git", "-C", repo, *args], check=True, capture_output=True
    ).stdout


def resolve(repo: str, rev: str) -> str:
    return (
        git(repo, "rev-parse", "--verify", "--end-of-options", f"{rev}^{{commit}}")
        .decode()
        .strip()
    )


def changes(repo: str, base: str, head: str) -> list[tuple[str | None, str | None]]:
    """Return (base path, head path) pairs; None marks an added or deleted side."""
    fields = (
        git(repo, "diff", "--name-status", "-z", "--find-renames", base, head)
        .decode()
        .split("\0")
    )
    pairs: list[tuple[str | None, str | None]] = []
    i = 0
    while i < len(fields) - 1:
        status = fields[i][0]
        if status == "R":
            pairs.append((fields[i + 1], fields[i + 2]))
            i += 3
            continue
        path = fields[i + 1]
        pairs.append((None if status == "A" else path, None if status == "D" else path))
        i += 2
    return pairs


def measure(repo: str, sha: str, path: str) -> list[Fn]:
    try:
        data = git(repo, "show", f"{sha}:{path}")
    except subprocess.CalledProcessError:
        return []  # Submodule or other non-blob entry.
    if b"\0" in data:
        return []
    info = lizard.FileAnalyzer(EXTENSIONS).analyze_source_code(
        path, data.decode(errors="replace")
    )
    return [
        Fn(
            path,
            f.name,
            f.long_name,
            f.start_line,
            f.end_line,
            f.nloc,
            f.cyclomatic_complexity,
            f.cognitive_complexity,
            f.parameter_count,
        )
        for f in info.function_list
    ]


def pair(
    before: list[Fn], after: list[Fn], key
) -> tuple[list[tuple[Fn, Fn]], list[Fn], list[Fn]]:
    """Pair functions with equal keys in source order; return pairs and leftovers."""
    pending: dict[str, list[Fn]] = defaultdict(list)
    for fn in sorted(before, key=lambda f: f.line):
        pending[key(fn)].append(fn)
    pairs, unmatched = [], []
    for fn in sorted(after, key=lambda f: f.line):
        candidates = pending.get(key(fn))
        if candidates:
            pairs.append((candidates.pop(0), fn))
        else:
            unmatched.append(fn)
    return pairs, [fn for group in pending.values() for fn in group], unmatched


def nested(fn: Fn, functions: list[Fn]) -> bool:
    return any(
        o is not fn
        and o.line <= fn.line
        and o.end >= fn.end
        and (o.line, o.end) != (fn.line, fn.end)
        for o in functions
    )


def delta(old: int | None, new: int) -> str:
    return f"{new} (new)" if old is None else f"{old}→{new}"


def tag(path: str) -> str:
    return " [test]" if TEST.search(path) else ""


def portable(name: str) -> str:
    """Cross-file key that also pairs ports between naming styles (fooBar, foo_bar)."""
    return name.replace("_", "").lower()


def match(files, before, after):
    """Match within a file by signature, then by name; across files only by a name unique on both sides."""
    matched: list[tuple[Fn, Fn]] = []
    removed: list[Fn] = []
    added: list[Fn] = []
    for old, new in files:
        exact, rest_before, rest_after = pair(
            before.get(old, []), after.get(new, []), lambda f: f.long_name
        )
        loose, rest_before, rest_after = pair(rest_before, rest_after, lambda f: f.name)
        matched += exact + loose
        removed += rest_before
        added += rest_after
    names_before, names_after = defaultdict(list), defaultdict(list)
    for fn in removed:
        names_before[portable(fn.name)].append(fn)
    for fn in added:
        names_after[portable(fn.name)].append(fn)
    moved = [
        (names_before[key][0], fns[0])
        for key, fns in names_after.items()
        if key != ANONYMOUS and len(fns) == 1 and len(names_before[key]) == 1
    ]
    moved_ids = {id(fn) for pair_ in moved for fn in pair_}
    removed = [fn for fn in removed if id(fn) not in moved_ids]
    added = [fn for fn in added if id(fn) not in moved_ids]
    return matched + moved, removed, added, moved


def grown(old: Fn | None, new: Fn) -> bool:
    old_ccn, old_cognitive = (old.ccn, old.cognitive) if old else (0, 0)
    return (new.ccn >= GROWN_CCN and new.ccn - old_ccn >= GROWN_CCN_DELTA) or (
        new.cognitive >= GROWN_COGNITIVE
        and new.cognitive - old_cognitive >= GROWN_COGNITIVE_DELTA
    )


def section(title: str, lines: list[str], limit: int | None) -> None:
    print(f"\n{title}: {len(lines)}")
    for line in lines[:limit]:
        print(f"  {line}")
    if limit is not None and len(lines) > limit:
        print(f"  … {len(lines) - limit} more (--all shows every line)")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("base")
    parser.add_argument("head", nargs="?", default="HEAD")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--all", action="store_true", help="do not cap list sections")
    args = parser.parse_args()
    limit = None if args.all else 25
    try:
        head = resolve(args.repo, args.head)
        base = (
            git(args.repo, "merge-base", resolve(args.repo, args.base), head)
            .decode()
            .strip()
        )
        pairs = changes(args.repo, base, head)
    except subprocess.CalledProcessError as error:
        print(f"git failed: {error.stderr.decode().strip()}", file=sys.stderr)
        return 1

    excluded = unmeasured = 0
    files: list[tuple[str | None, str | None]] = []
    for old, new in pairs:
        path = new or old
        if EXCLUDED.search(path):
            excluded += 1
        elif not lizard.get_reader_for(path):
            unmeasured += 1
        else:
            files.append((old, new))
    before = {old: measure(args.repo, base, old) for old, _ in files if old}
    after = {new: measure(args.repo, head, new) for _, new in files if new}
    matched, removed, added, moved = match(files, before, after)
    moved_to = {id(new): old.path for old, new in moved}

    candidates = [(old, new) for old, new in matched if grown(old, new)]
    candidates += [(None, fn) for fn in added if grown(None, fn)]
    # Cognitive growth first: flat CCN (Rust `?`, guard chains) costs a reader little.
    candidates.sort(
        key=lambda p: (
            p[1].cognitive - (p[0].cognitive if p[0] else 0),
            p[1].ccn - (p[0].ccn if p[0] else 0),
        ),
        reverse=True,
    )
    grown_lines = []
    for old, new in candidates:
        params = (
            f"  params {old.params}→{new.params}"
            if old and old.params != new.params
            else ""
        )
        origin = f"  (moved from {moved_to[id(new)]})" if id(new) in moved_to else ""
        grown_lines.append(
            f"{new.path}:{new.line} {new.name}  CCN {delta(old and old.ccn, new.ccn)}  "
            f"cognitive {delta(old and old.cognitive, new.cognitive)}{params}{origin}{tag(new.path)}"
        )
    tiny = sorted(
        (
            fn
            for fn in added
            if fn.name != ANONYMOUS
            and fn.nloc <= TINY_NLOC
            and not TEST.search(fn.path)
            and not nested(fn, after[fn.path])
        ),
        key=lambda f: (f.path, f.line),
    )
    reduced = [
        (
            old.ccn - new.ccn,
            f"{new.path}:{new.line} {new.name}  CCN {old.ccn}→{new.ccn}  "
            f"cognitive {old.cognitive}→{new.cognitive}{tag(new.path)}",
        )
        for old, new in matched
        if old.ccn - new.ccn >= GROWN_CCN_DELTA
        or old.cognitive - new.cognitive >= GROWN_COGNITIVE_DELTA
    ]
    reduced += [
        (
            fn.ccn,
            f"{fn.path}:{fn.line} {fn.name}  removed (CCN {fn.ccn}, cognitive {fn.cognitive}){tag(fn.path)}",
        )
        for fn in removed
        if fn.ccn >= GROWN_CCN or fn.cognitive >= GROWN_COGNITIVE
    ]
    rows = []
    for old, new in files:
        fns_before, fns_after = before.get(old, []), after.get(new, [])
        n_added = sum(fn.path == new for fn in added)
        n_removed = sum(fn.path == old for fn in removed)
        ccn_before, ccn_after = (
            sum(f.ccn for f in fns_before),
            sum(f.ccn for f in fns_after),
        )
        if (len(fns_before), ccn_before) == (len(fns_after), ccn_after) and not (
            n_added or n_removed
        ):
            continue
        path = new or old
        rename = f" (from {old})" if old and new and old != new else ""
        rows.append(
            (
                abs(ccn_after - ccn_before),
                f"{path}{rename}  {len(fns_before)}→{len(fns_after)} (+{n_added}/-{n_removed})  "
                f"CCN {ccn_before}→{ccn_after}{tag(path)}",
            )
        )

    print(
        f"Complexity delta {base[:12]}..{head[:12]} (merge base of {args.base} and {args.head})"
    )
    print(
        f"Measured {len(files)} changed files; excluded {excluded} vendored/generated/lock; "
        f"{unmeasured} not a lizard language"
    )
    print(
        "CCN uses modified counting (a switch is one decision); cognitive weights nesting."
    )
    section(
        f"Grown (CCN ≥{GROWN_CCN} and +{GROWN_CCN_DELTA}, or cognitive ≥{GROWN_COGNITIVE} "
        f"and +{GROWN_COGNITIVE_DELTA})",
        grown_lines,
        limit,
    )
    section(
        f"Tiny new helpers (≤{TINY_NLOC} NLOC, named, not nested, non-test)",
        [f"{fn.path}:{fn.line} {fn.name}  {fn.nloc} NLOC" for fn in tiny],
        limit,
    )
    section(
        "Reduced or removed", [line for _, line in sorted(reduced, reverse=True)], limit
    )
    section(
        "Moved across files (matched by unique name)",
        [
            f"{new.name}  {old.path}:{old.line} → {new.path}:{new.line}"
            for old, new in moved
        ],
        limit,
    )
    section(
        "Files (functions before→after, new/removed, total CCN before→after)",
        [line for _, line in sorted(rows, reverse=True)],
        limit,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
