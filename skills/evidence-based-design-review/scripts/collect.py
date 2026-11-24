#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# ///
"""Collect the standard SCC and codebase-memory evidence for a design review.

Prints one compact summary of both evidence lanes. Metrics select candidates
for source inspection; they are not findings.
"""

import argparse
import json
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

CBM = "codebase-memory-mcp"
TEST = re.compile(
    r"(^|/)(tests?|benches|__tests__|spec|testdata|fixtures)/"
    r"|(^|/)test_[^/]*$|_test\.[^/]+$|\.(test|spec)\.[^/]+$"
)
EXCLUDED = re.compile(
    r"(^|/)(node_modules|vendor|third_party|dist|build|target|coverage)/"
    r"|\.min\.[^/]+$|\.generated\.[^/]+$"
    r"|(^|/)(package-lock\.json|pnpm-lock\.yaml|yarn\.lock|uv\.lock|Cargo\.lock|poetry\.lock|go\.sum)$"
)
NON_CODE = re.compile(
    r"\.(md|mdx|rst|txt|adoc|json|ya?ml|toml|ini|cfg|csv|xml|svg|png|jpe?g|gif|ico|ttf|otf|woff2?|lock)$"
    r"|(^|/)(LICEN[CS]E|COPYING|NOTICE)[^/]*$"
)
DEP_EDGES = "CALLS|USAGE|CALL_REFERENCE|INHERITS|IMPLEMENTS|READS|WRITES|OVERRIDE"
FUNCS = "f:Function|Method"


def fail(message):
    sys.exit(f"collect.py: {message}")


def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)


def scc(args, path):
    out = run(["scc", *args, "--format", "json", "."], cwd=path)
    if out.returncode:
        raise RuntimeError(out.stderr.strip() or out.stdout.strip())
    return json.loads(out.stdout)


def cbm(tool, *args):
    out = run([CBM, "cli", "--quiet", tool, "--format", "json", *args])
    if out.returncode:
        raise RuntimeError(out.stderr.strip() or out.stdout.strip())
    return json.loads(out.stdout)


def query(project, cypher):
    """All rows of a Cypher query, following cursors."""
    args = ["--project", project, "--max-rows", "5000", "--query", cypher]
    rows, page = [], cbm("query_graph", *args)
    while True:
        rows += page.get("rows", [])
        if not page.get("has_more") or not page.get("next_cursor"):
            return rows
        page = cbm("query_graph", *args, "--cursor", page["next_cursor"])


def find_project(repo):
    projects = cbm("list_projects", "--limit", "500").get("projects", [])
    owners = [
        p
        for p in projects
        if repo == Path(p["root_path"]) or Path(p["root_path"]) in repo.parents
    ]
    return max(owners, key=lambda p: len(p["root_path"]), default=None)


def history(repo, depth, base_dir):
    """Hotspots and coupling, from a --no-local clone when SCC cannot open the checkout."""
    source = repo
    try:
        hot = scc(["--hotspots", "--depth", str(depth)], repo)
    except RuntimeError as error:
        if "extension" not in str(error):
            raise
        source = Path(base_dir) / "clone"
        cloned = run(["git", "clone", "--quiet", "--no-local", str(repo), str(source)])
        if cloned.returncode:
            raise RuntimeError(cloned.stderr.strip()) from error
        hot = scc(["--hotspots", "--depth", str(depth)], source)
    coupling = scc(["--coupling", "--depth", str(depth)], source)
    return hot, coupling, source


def commit_breadth(repo, depth):
    log = run(
        ["git", "log", "-n", str(depth), "--format=%x00", "--name-only"], cwd=repo
    ).stdout
    sizes = sorted(
        len([f for f in c.split("\n") if f.strip()]) for c in log.split("\0")[1:]
    )
    if not sizes:
        return None
    return {
        "commits": len(sizes),
        "median": statistics.median(sizes),
        "p90": sizes[int(0.9 * (len(sizes) - 1))],
        "max": sizes[-1],
        "over_10": sum(s > 10 for s in sizes),
    }


class Scope:
    def __init__(self, roots, exclude):
        self.roots = [r.rstrip("/") + "/" if r else "" for r in roots] or [""]
        self.exclude = re.compile(exclude) if exclude else None

    def kind(self, path):
        if EXCLUDED.search(path) or (self.exclude and self.exclude.search(path)):
            return "excluded"
        if NON_CODE.search(path) or not any(path.startswith(r) for r in self.roots):
            return "other"
        return "test" if TEST.search(path) else "prod"

    def cypher(self, var):
        if self.roots == [""]:
            return ""
        roots = " OR ".join(
            f"{var}.file_path STARTS WITH '{r.replace("'", "\\'")}'" for r in self.roots
        )
        return f" AND ({roots})"

    def component(self, path):
        root = max((r for r in self.roots if path.startswith(r)), key=len, default="")
        rest = path[len(root) :]
        return root + rest.split("/")[0] if "/" in rest else root.rstrip("/") or rest


def graph_evidence(project, scope, top):
    w = scope.cypher("f")
    queries = {
        "cognitive": f"MATCH ({FUNCS}) WHERE f.is_test = false{w} RETURN f.qualified_name, "
        "f.file_path, f.start_line, f.complexity, f.cognitive, f.lines "
        f"ORDER BY f.cognitive DESC, f.complexity DESC, f.qualified_name ASC LIMIT {top}",
        "all": f"MATCH ({FUNCS}) WHERE f.is_test = false{w} "
        "RETURN sum(f.complexity), sum(f.lines), count(f)",
        "high": f"MATCH ({FUNCS}) WHERE f.is_test = false AND f.complexity > 10{w} "
        "RETURN sum(f.complexity), sum(f.lines), count(f)",
        "files": f"MATCH ({FUNCS}) WHERE f.is_test = false{w} RETURN f.file_path, "
        "count(f) AS n, sum(f.complexity) AS cx ORDER BY cx DESC, f.file_path ASC",
        "exported": f"MATCH ({FUNCS}) WHERE f.is_test = false AND f.is_exported = true{w} "
        "RETURN f.file_path, count(f)",
        "writes": f"MATCH (f:Function|Method)-[:WRITES]->(v) WHERE f.is_test = false{w} "
        "RETURN v.qualified_name AS state, v.file_path, count(DISTINCT f) AS writers, "
        "count(DISTINCT f.file_path) AS writer_files "
        "ORDER BY writer_files DESC, writers DESC, state ASC "
        f"LIMIT {top}",
        "similar": f"MATCH (f)-[r:SIMILAR_TO]->(b) WHERE f.is_test = false AND b.is_test = false{w} "
        "RETURN f.qualified_name, f.file_path, b.qualified_name, b.file_path, r.jaccard "
        "ORDER BY r.jaccard DESC LIMIT 200",
        "related": f"MATCH (f:Function|Method)-[r:SEMANTICALLY_RELATED]->(b:Function|Method) "
        f"WHERE f.is_test = false AND b.is_test = false{w} RETURN f.qualified_name, f.file_path, "
        "b.qualified_name, b.file_path, r.p ORDER BY r.p DESC LIMIT 200",
        "edges": f"MATCH (f)-[:{DEP_EDGES}]->(b) WHERE f.is_test = false AND b.is_test = false "
        "AND f.file_path <> '' AND NOT b.file_path STARTS WITH '<' "
        "RETURN DISTINCT f.file_path, b.file_path",
    }
    with ThreadPoolExecutor(8) as pool:
        futures = {k: pool.submit(query, project, q) for k, q in queries.items()}
    out = {}
    for key, future in futures.items():
        try:
            out[key] = future.result()
        except (RuntimeError, json.JSONDecodeError) as error:
            out[key] = f"query failed: {error}"
    return out


def num(value):
    try:
        return float(value)
    except TypeError, ValueError:
        return 0.0


def short(name, project):
    return name.removeprefix(project + ".")


def summarize(args, repo, project, scope, data):
    lines = []
    say = lines.append
    top = args.top
    say(f"# Evidence: {repo}")
    say(f"HEAD {data['head']} on {data['branch']}; dirty files: {len(data['dirty'])}")
    for path in data["dirty"][:10]:
        say(f"  dirty: {path}")
    say(
        f"Roots: {', '.join(scope.roots) if scope.roots != [''] else '(whole repository)'}"
    )

    status = data["index_status"]
    watch = status.get("watch", {}).get("watched")
    gaps = {k: status.get(k, {}).get("count", 0) for k in ("skipped", "parse_partial")}
    say(
        f"Graph: {project} indexed_at {status.get('indexed_at')} watched={watch} "
        f"skipped={gaps['skipped']} parse_partial={gaps['parse_partial']}"
    )
    window = data["hotspots"].get("window", {})
    say(
        f"SCC history: {window.get('commits')} commits, {window.get('from')} to {window.get('to')}, "
        f"depth {args.depth}, from {'a --no-local clone' if data['cloned'] else 'the checkout'}"
    )
    breadth = data["breadth"]
    if breadth:
        say(
            f"Commit breadth (files per commit): median {breadth['median']}, p90 {breadth['p90']}, "
            f"max {breadth['max']}; {breadth['over_10']} of {breadth['commits']} touch >10 files."
            " Discount co-change that broad commits explain."
        )

    files = data["files"]
    prod = sorted((f for f in files if f["kind"] == "prod"), key=lambda f: -f["cx"])
    say("")
    say(
        f"## SCC file complexity ({len(prod)} production files, "
        f"{sum(f['code'] for f in prod)} code lines)"
    )
    for f in prod[:top]:
        say(f"- {f['path']}: cx {f['cx']}, cognitive {f['cog']}, code {f['code']}")

    say("")
    say("## SCC hotspots (production)")
    hot = [
        h for h in data["hotspots"].get("files", []) if scope.kind(h["file"]) == "prod"
    ]
    for h in hot[:top]:
        say(
            f"- {h['file']}: score {h['score']}, commits {h['commits']}, cx {h['complexity']}, "
            f"code churn {h['codeChurn']}, comment churn {h['commentChurn']}, authors {h['authors']}"
        )

    edges = data["graph"]["edges"]
    linked = set()
    if isinstance(edges, list):
        linked = {frozenset((a, b)) for a, b in edges if a != b}
    say("")
    say("## SCC co-change pairs (static = graph dependency edge between the files)")
    pairs = data["coupling"].get("pairs", [])
    code = [
        p for p in pairs if "prod" in (scope.kind(p["fileA"]), scope.kind(p["fileB"]))
    ]
    for p in code[:top]:
        static = "yes" if frozenset((p["fileA"], p["fileB"])) in linked else "no"
        say(
            f"- {p['fileA']} <> {p['fileB']}: shared {p['shared']}, degree {p['degree']}, "
            f"static {static}"
        )
    others = [
        p
        for p in pairs
        if p not in code
        and "excluded" not in (scope.kind(p["fileA"]), scope.kind(p["fileB"]))
    ]
    for p in others[:5]:
        say(f"- (non-production) {p['fileA']} <> {p['fileB']}: shared {p['shared']}")

    if data.get("diff"):
        diff = data["diff"]
        say("")
        say(f"## Diff against {args.base}: {len(diff['changed'])} changed files")
        for path in diff["changed"][:40]:
            say(f"- {path} ({scope.kind(path)})")
        for path, partners in diff["partners"].items():
            missing = [p for p in partners if p["file"] not in diff["changed"]]
            listed = (
                ", ".join(f"{p['file']} ({p['shared']})" for p in missing[:5]) or "none"
            )
            say(f"- usual partners of {path} missing from the diff: {listed}")

    g = data["graph"]

    def rows(key):
        value = g[key]
        if isinstance(value, str):
            say(f"- {value}")
            return []
        return value

    say("")
    say("## Graph: dependency edges between components")
    say(
        "Edges a component cannot have (check the manifests) mean calls are resolved by name: "
        "then fan-in, cycles, traces, WRITES counts and static edges are unreliable there; "
        "confirm callers and writers with source search."
    )
    components = Counter(
        (scope.component(a), scope.component(b))
        for a, b in (edges if isinstance(edges, list) else [])
        if scope.kind(a) == "prod" and scope.kind(b) == "prod"
    )
    for (a, b), n in sorted(components.items(), key=lambda kv: (-kv[1], kv[0])):
        if a != b:
            say(f"- {a} -> {b}: {n} file pairs")

    say("")
    say("## Graph: complexity concentration")
    totals, high = rows("all"), rows("high")
    if totals and high:
        all_cx, all_lines, all_n = (num(v) for v in totals[0])
        hi_cx, hi_lines, hi_n = (num(v) for v in high[0])
        say(
            f"- functions over cyclomatic 10: {int(hi_n)} of {int(all_n)} hold "
            f"{int(hi_cx)} of {int(all_cx)} cyclomatic ({hi_cx / max(all_cx, 1):.0%}) and "
            f"{int(hi_lines)} of {int(all_lines)} lines ({hi_lines / max(all_lines, 1):.0%})"
        )
    for name, path, line, cx, cog, _lines in rows("cognitive"):
        say(
            f"- {short(name, project)} ({path}:{line}): cognitive {cog}, cyclomatic {cx}"
        )

    say("")
    say("## Graph: interface size (functions, exported, cyclomatic per file)")
    exported = {path: int(num(n)) for path, n in rows("exported")}
    for path, n, cx in rows("files")[:top]:
        say(
            f"- {path}: {n} functions, {exported.get(path, 0)} exported, cyclomatic {cx}"
        )

    say("")
    say("## Graph: state written from several files (field names can collide)")
    for name, path, writers, writer_files in rows("writes"):
        if num(writer_files) >= 2:
            say(
                f"- {short(name, project)} ({path}): {writers} writers in {writer_files} files"
            )

    say("")
    say(
        "## Graph: similar pairs across files (token SIMILAR_TO, vocabulary SEMANTICALLY_RELATED)"
    )
    for key, label in (("similar", "jaccard"), ("related", "p")):
        shown = 0
        for a, fa, b, fb, score in rows(key):
            if fa != fb and shown < 10:
                say(f"- {short(a, project)} ~ {short(b, project)}: {label} {score}")
                shown += 1
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo", type=Path)
    parser.add_argument(
        "--root", action="append", default=[], help="production root prefix, e.g. src/"
    )
    parser.add_argument("--exclude", help="regex of repo-relative paths to leave out")
    parser.add_argument(
        "--project", help="codebase-memory project; found from the repo by default"
    )
    parser.add_argument(
        "--depth", type=int, default=1000, help="SCC history depth in commits"
    )
    parser.add_argument(
        "--base", help="review a diff: changes from the merge base with BASE"
    )
    parser.add_argument("--top", type=int, default=15, help="rows per section")
    parser.add_argument("--json", type=Path, help="also write all collected data here")
    args = parser.parse_args()

    for tool in ("scc", CBM, "git"):
        if not shutil.which(tool):
            fail(f"{tool} is not on PATH")
    repo = args.repo.resolve()
    git = lambda *a: run(["git", *a], cwd=repo).stdout.strip()  # noqa: E731
    if not git("rev-parse", "--git-dir"):
        fail(f"{repo} is not a Git repository")
    project = args.project or (find_project(repo) or {}).get("name")
    if not project:
        fail(
            f"no codebase-memory project covers {repo}; index it with index_repository first"
        )
    scope = Scope(args.root, args.exclude)

    with tempfile.TemporaryDirectory() as tmp, ThreadPoolExecutor(6) as pool:
        files_job = pool.submit(scc, ["--by-file", "--cognitive", "--no-min-gen"], repo)
        history_job = pool.submit(history, repo, args.depth, tmp)
        breadth_job = pool.submit(commit_breadth, repo, args.depth)
        status_job = pool.submit(cbm, "index_status", "--project", project)
        graph_job = pool.submit(graph_evidence, project, scope, args.top)

        files = [
            {
                "path": f["Location"].removeprefix("./"),
                "lang": lang["Name"],
                "code": f["Code"],
                "cx": f["Complexity"],
                "cog": f.get("Cognitive", 0),
            }
            for lang in files_job.result()
            for f in lang.get("Files", [])
        ]
        for f in files:
            f["kind"] = scope.kind(f["path"])
        hot, coupling, source = history_job.result()
        data = {
            "head": git("rev-parse", "--short", "HEAD"),
            "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
            "dirty": [
                line[3:]
                for line in run(
                    ["git", "status", "--porcelain"], cwd=repo
                ).stdout.splitlines()
            ],
            "files": files,
            "hotspots": hot,
            "coupling": coupling,
            "cloned": source != repo,
            "breadth": breadth_job.result(),
            "index_status": status_job.result(),
            "graph": graph_job.result(),
        }
        if args.base:
            changed = git("diff", "--name-only", f"{args.base}...HEAD").splitlines()
            ranked = sorted(
                (f for f in files if f["path"] in changed and f["kind"] == "prod"),
                key=lambda f: -f["cx"],
            )[:8]
            jobs = {
                f["path"]: pool.submit(
                    scc,
                    ["--coupling-for", f["path"], "--depth", str(args.depth)],
                    source,
                )
                for f in ranked
            }
            data["diff"] = {
                "changed": changed,
                "partners": {
                    p: j.result().get("partners", []) for p, j in jobs.items()
                },
            }

    if args.json:
        args.json.write_text(json.dumps(data, indent=1))
    print(summarize(args, repo, project, scope, data))


if __name__ == "__main__":
    main()
