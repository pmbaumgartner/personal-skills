#!/usr/bin/env python3
"""Validate the single-path agentic-project-delivery skill package."""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote


REQUIRED_FILES = {
    "SKILL.md",
    "agents/openai.yaml",
    "assets/acceptance-contract.md",
    "assets/project-charter.md",
    "assets/work-packet.md",
    "evals/quality-cases.md",
    "evals/trigger-queries.json",
    "references/evaluation-and-forecasting.md",
    "references/kata-ledger.md",
    "references/oracle-construction.md",
    "references/research-basis.md",
    "references/risk-and-autonomy.md",
    "references/scaling-controls.md",
    "scripts/validate_skill.py",
}
FORBIDDEN_FILES = {
    "README.md",
    "assets/decision-gate.md",
    "assets/evidence-bundle.md",
    "assets/pilot-report.md",
    "references/delivery-profiles.md",
}

MAIN_PHRASES = (
    "First decide whether APD is needed",
    "Exit to the repository's normal workflow",
    "Use one bounded workflow",
    "Do not instantiate the complete workflow again inside every child",
    "Ceremony budget",
    "zero to three initially open implementation packets",
    "zero standalone gate issues",
    "zero standalone audit issues",
    "One durable record per fact",
    "Frame the outcome",
    "executable definition of done",
    "Choose the three topologies and bounded packets",
    "Use one representative implementation packet as the pilot",
    "human attention and decision-waiting time",
    "Release progressively",
    "Human control plane",
    "One human authorization may cover the contract",
    "blocks at least two independently executable packets",
    "Create a separate audit only for high-risk work",
    "A fresh agent session provides reviewer separation and provenance",
    "Classify the action at its current boundary",
    "Scientific uncertainty and operational delivery risk are different",
    "Do not automatically expand the ledger into a generic larger workflow",
    "Create JSON only when executable tooling consumes it",
)
KATA_PHRASES = (
    "kata version --json",
    "kata quickstart",
    "kata init --with-agents",
    "search before creating",
    "kata claim",
    "--blocked-by",
    "kata close",
    "work.attention",
    "primary work ledger",
    "Do not create or maintain a parallel",
    "kata <command> --help",
    "stable actor identity",
)
SOLO_AND_CAPACITY_PHRASES = (
    "Accountability separation",
    "Personnel separation",
    "Temporal separation",
    "Tool separation",
    "defines and freezes the oracle before implementation",
    "cannot modify protected acceptance material without explicit authorization",
    "cap or reduce implementation launches",
    "first reassign existing capacity to the constraint",
    "Do not increase total agent count during the initial diagnosis and enablement pilot",
    "do not add agents merely because generated-work demand exists",
    "specialized capacity increase as a separate bounded pilot",
)
RISK_PHRASES = (
    "sensitive personal data",
    "separate implementation and acceptance authority",
    "recovery rehearsals",
    "least-privilege",
    "dual control",
)
ORACLE_PHRASES = (
    "Falsifiable",
    "Model/implementation-neutral",
    "Reproducible",
    "Sensitive to representative defects",
    "Protected from self-certification",
    "Fast enough for its intended feedback tier",
    "Explicit about uncertainty and uncovered failures",
)
EVAL_PHRASES = (
    "Unmeasured implementation demonstration",
    "Isolated research experiment",
    "Genuine program boundary",
    "no more than three open packets",
    "does not apply the full APD workflow recursively",
)

FORBIDDEN_PROFILE_RE = re.compile(
    r"\b(?:Core|Extended)\b|delivery[- ]profile", re.IGNORECASE
)
FORBIDDEN_LEDGER_TEXT = (
    ".agentic-project",
    "work-ledger.md",
    "queued → ready → claimed",
    "stage:implemented",
)
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skill-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    return parser.parse_args()


def parse_frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER_RE.search(text)
    if not match:
        return {}
    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if line and not line[0].isspace() and ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip("\"'")
    return result


def require_phrases(
    errors: list[str], scope: str, text: str, phrases: tuple[str, ...]
) -> None:
    lowered = text.lower()
    for phrase in phrases:
        if phrase.lower() not in lowered:
            errors.append(f"{scope}: missing required concept {phrase!r}")


def link_errors(root: Path, paths: list[Path]) -> list[str]:
    errors: list[str] = []
    for path in paths:
        for raw_target in LINK_RE.findall(path.read_text(encoding="utf-8")):
            target = raw_target.strip()
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = unquote(target.split("#", 1)[0])
            if not target:
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(root)
            except ValueError:
                errors.append(f"{path.relative_to(root)}: link escapes package")
                continue
            if not resolved.exists():
                errors.append(
                    f"{path.relative_to(root)}: missing link target {raw_target!r}"
                )
    return errors


def duplicate_paragraphs(root: Path, paths: list[Path]) -> dict[str, list[str]]:
    seen: dict[str, list[str]] = defaultdict(list)
    for path in paths:
        text = CODE_FENCE_RE.sub("", FRONTMATTER_RE.sub("", path.read_text()))
        for paragraph in re.split(r"\n\s*\n", text):
            lines = [line.strip() for line in paragraph.splitlines()]
            if not lines or any(line.startswith("#") for line in lines):
                continue
            normalized = re.sub(r"\s+", " ", " ".join(lines)).lower().strip()
            if len(normalized.split()) >= 25:
                seen[normalized].append(str(path.relative_to(root)))
    return {text: places for text, places in seen.items() if len(places) > 1}


def main() -> int:
    root = parse_args().skill_root.expanduser().resolve()
    if not root.is_dir():
        print(f"error: skill directory does not exist: {root}", file=sys.stderr)
        return 2

    errors: list[str] = []
    warnings: list[str] = []
    existing = {
        str(path.relative_to(root))
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }
    errors.extend(
        f"missing required file: {path}" for path in sorted(REQUIRED_FILES - existing)
    )
    errors.extend(
        f"forbidden package file: {path}" for path in sorted(FORBIDDEN_FILES & existing)
    )

    def read(relative: str) -> str:
        path = root / relative
        return path.read_text(encoding="utf-8") if path.exists() else ""

    skill = read("SKILL.md")
    kata = read("references/kata-ledger.md")
    risk = read("references/risk-and-autonomy.md")
    oracle = read("references/oracle-construction.md")
    evals = read("evals/quality-cases.md")

    frontmatter = parse_frontmatter(skill)
    if set(frontmatter) != {"name", "description"}:
        errors.append("SKILL.md: frontmatter keys must be exactly name and description")
    if frontmatter.get("name") != root.name:
        errors.append("SKILL.md: frontmatter name must match the directory")
    if "Kata" not in frontmatter.get("description", ""):
        errors.append("SKILL.md: description must identify Kata as the durable ledger")

    require_phrases(errors, "SKILL.md", skill, MAIN_PHRASES)
    require_phrases(errors, "SKILL.md", skill, SOLO_AND_CAPACITY_PHRASES)
    require_phrases(errors, "Kata contract", skill + "\n" + kata, KATA_PHRASES)
    require_phrases(errors, "risk guidance", skill + "\n" + risk, RISK_PHRASES)
    require_phrases(errors, "oracle guidance", oracle, ORACLE_PHRASES)
    require_phrases(errors, "quality cases", evals, EVAL_PHRASES)

    procedure_steps = re.findall(r"(?m)^\d+\. \*\*", oracle)
    if len(procedure_steps) != 10:
        errors.append(
            f"oracle construction must have exactly 10 steps; found {len(procedure_steps)}"
        )

    validation_command = (
        "uv run --with pyyaml python3 ~/.codex/skills/.system/skill-creator/"
        "scripts/quick_validate.py ."
    )
    if validation_command not in skill.lower():
        errors.append("SKILL.md: generic validation command is missing")
    if re.search(r"(?<![\w-])python(?!3)(?:\s|$)", skill):
        errors.append("SKILL.md: documented commands must use python3")

    openai_yaml = read("agents/openai.yaml")
    for key in ("display_name:", "short_description:", "default_prompt:"):
        if key not in openai_yaml:
            errors.append(f"agents/openai.yaml: missing {key[:-1]}")
    if "$agentic-project-delivery" not in openai_yaml:
        errors.append("agents/openai.yaml: default prompt must name the skill")

    package_text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in root.rglob("*")
        if path.is_file() and path.suffix in {".md", ".json", ".yaml"}
    )
    if match := FORBIDDEN_PROFILE_RE.search(package_text):
        errors.append(f"forbidden multi-profile language: {match.group(0)!r}")
    for phrase in FORBIDDEN_LEDGER_TEXT:
        if phrase in package_text:
            errors.append(f"forbidden parallel-ledger text: {phrase!r}")

    markdown = sorted(root.rglob("*.md"))
    errors.extend(link_errors(root, markdown))
    for directory in ("assets", "references"):
        for path in sorted((root / directory).glob("*.md")):
            relative = str(path.relative_to(root))
            if relative not in skill:
                warnings.append(f"resource not linked from SKILL.md: {relative}")

    duplicates = duplicate_paragraphs(root, markdown)
    for paragraph, locations in duplicates.items():
        errors.append(
            f"duplicate long paragraph in {', '.join(locations)}: {paragraph[:80]}…"
        )

    for path in sorted(root.rglob("*.json")):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path.relative_to(root)}: invalid JSON: {exc}")
    for path in sorted(root.rglob("*.py")):
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except (OSError, SyntaxError) as exc:
            errors.append(f"{path.relative_to(root)}: invalid Python: {exc}")

    limits = {"assets": 60, "references": 210, "evals": 240, "scripts": 350}
    for directory, limit in limits.items():
        for path in sorted((root / directory).glob("*")):
            if path.is_file():
                count = len(path.read_text(errors="replace").splitlines())
                if count > limit:
                    warnings.append(
                        f"{path.relative_to(root)}: {count} lines exceeds {limit}"
                    )

    skill_lines = len(skill.splitlines())
    skill_words = len(re.findall(r"\b\w+[\w’-]*\b", skill))
    if skill_lines > 360:
        errors.append(f"SKILL.md: {skill_lines} lines exceeds 360")
    if skill_words > 3600:
        warnings.append(f"SKILL.md: {skill_words} words exceeds 3600")

    total_lines = sum(
        len(path.read_text(errors="replace").splitlines())
        for path in root.rglob("*")
        if path.is_file() and path.suffix in {".md", ".py", ".json"}
    )
    if total_lines > 1600:
        errors.append(f"package: {total_lines} text lines exceeds 1600")
    if len(existing) > 14:
        errors.append(f"package: {len(existing)} files exceeds 14")

    for warning in warnings:
        print(f"warning: {warning}")
    for error in errors:
        print(f"error: {error}", file=sys.stderr)
    print(f"metric: SKILL.md lines={skill_lines}, words={skill_words}")
    print(f"metric: package text lines={total_lines}, files={len(existing)}")
    print(f"metric: internal markdown links checked={sum(map(len, map(LINK_RE.findall, (p.read_text() for p in markdown))))}")
    print(f"metric: duplicate long paragraphs={len(duplicates)}")

    if errors:
        print(f"failed: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"ok: single-path package passes parsimony checks; {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
