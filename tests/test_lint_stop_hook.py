import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parents[1] / "lints" / "claude-stop-hook"


@unittest.skipUnless(shutil.which("ast-grep"), "ast-grep is not installed")
class LintStopHookTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.repo = Path(temporary.name) / "repo"
        self.state = Path(temporary.name) / "state"
        self.state.mkdir()
        (self.repo / "src").mkdir(parents=True)
        self.git("init", "-q")

    def git(self, *args):
        subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@t", *args],
            cwd=self.repo,
            check=True,
        )

    def stop(self):
        result = subprocess.run(
            [sys.executable, str(HOOK)],
            input=json.dumps({"cwd": str(self.repo), "session_id": "s1"}),
            capture_output=True,
            text=True,
            check=True,
            env={**os.environ, "TMPDIR": str(self.state)},
        )
        return json.loads(result.stdout)["reason"] if result.stdout.strip() else None

    def test_reports_findings_on_changed_lines_once_per_session(self):
        module = self.repo / "src" / "m.py"
        module.write_text("def old(timeout: int) -> None:\n    pass\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "init")
        module.write_text(
            module.read_text() + "\ndef new(delay: float) -> None:\n    pass\n"
        )
        (self.repo / "src" / "fresh.py").write_text(
            "def other(interval: int) -> None:\n    pass\n"
        )

        reason = self.stop()

        self.assertIn("src/m.py:4", reason)
        self.assertIn("src/fresh.py:1", reason)
        self.assertNotIn("src/m.py:1", reason)
        self.assertIsNone(self.stop())


if __name__ == "__main__":
    unittest.main()
