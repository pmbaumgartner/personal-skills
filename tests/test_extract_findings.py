import importlib.util
import io
import json
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "skills/mine-lint-candidates/scripts/extract_findings.py"
)
spec = importlib.util.spec_from_file_location("extract_findings", SCRIPT)
extract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extract)


class ExtractionTests(unittest.TestCase):
    def test_jsonl_keeps_source_ordinals_and_marks_shortened_excerpts(self):
        long_finding = (
            "## Findings\nSeverity: high. `module.py:10` hides the failure. "
            + "The caller cannot distinguish success from failure. " * 22
        )
        short_finding = (
            "## Second finding\nSeverity: medium. `module.py:30` loses the exit code. "
            "A failed command looks successful to its caller, so later steps run with "
            "incomplete results. Propagate the command's exit code instead."
        )
        review = long_finding + "\n" + short_finding
        sessions = {
            "first": ("alpha", 9),
            "duplicate": ("alpha", 17),
            "other-project": ("beta", 23),
        }

        def agentsview(command, **kwargs):
            action = command[2]
            if action == "search":
                result = {
                    "matches": [
                        {"session_id": sid, "project": project, "ordinal": 2}
                        for sid, (project, _) in sessions.items()
                    ],
                    "next_cursor": 0,
                }
            elif action == "messages":
                _, ordinal = sessions[command[3]]
                result = {
                    "messages": [
                        {"ordinal": 3, "content": "I'll review this now."},
                        {"ordinal": ordinal, "content": review},
                    ]
                }
            elif action == "get":
                project, _ = sessions[command[3]]
                result = {"cwd": f"/checkouts/{project}"}
            else:
                raise AssertionError(f"Unexpected agentsview command: {command}")
            return subprocess.CompletedProcess(command, 0, json.dumps(result), "")

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "items.jsonl"
            with (
                patch.object(extract.subprocess, "run", side_effect=agentsview),
                patch("sys.argv", [str(SCRIPT), "Findings", "--out", str(output)]),
                redirect_stdout(io.StringIO()),
            ):
                extract.main()
            records = [json.loads(line) for line in output.read_text().splitlines()]

        self.assertEqual(len(records), 4)
        for project, session_id, ordinal in [
            ("alpha", "first", 9),
            ("beta", "other-project", 23),
        ]:
            findings = [record for record in records if record["project"] == project]
            self.assertEqual(
                findings,
                [
                    {
                        "project": project,
                        "text": " ".join(long_finding.split())[:700],
                        "truncated": True,
                        "session_id": session_id,
                        "ordinal": ordinal,
                    },
                    {
                        "project": project,
                        "text": " ".join(short_finding.split()),
                        "truncated": False,
                        "session_id": session_id,
                        "ordinal": ordinal,
                    },
                ],
            )


if __name__ == "__main__":
    unittest.main()
