import importlib.machinery
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

loader = importlib.machinery.SourceFileLoader(
    "sync_external_skills",
    str(Path(__file__).resolve().parents[1] / "bin" / "sync-external-skills"),
)
spec = importlib.util.spec_from_loader(loader.name, loader)
cli = importlib.util.module_from_spec(spec)
loader.exec_module(cli)


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.sources = {"example": {"revision": "abc123"}}
        self.name = "skills/example/SKILL.md"
        self.files = {self.name: b"original\n"}

    def test_collect_wraps_all_prompts_and_preserves_sources_and_licenses(self):
        cursor = self.root / "cursor"
        cursor_skill = cursor / cli.CURSOR_PATH / "SKILL.md"
        cursor_skill.parent.mkdir(parents=True)
        original = b"---\nname: thermo-nuclear-code-quality-review\n---\n\nReview.\n"
        cursor_skill.write_bytes(original)
        (cursor / "cursor-team-kit/LICENSE").write_bytes(b"Cursor license\n")
        roborev = self.root / "roborev"
        prompts = roborev / cli.ROBOREV_PATH
        prompts.mkdir(parents=True)
        prompt = "Analyze the code: keep quotes and Unicode — intact.\n\n- Output findings.\n"
        for stem in ("api_design", "new_analysis"):
            (prompts / f"{stem}.txt").write_text(prompt, encoding="utf-8")
        (prompts / "analyze.go").write_text("package analyze\n")
        (roborev / "LICENSE").write_bytes(b"Roborev license\n")

        def snapshot(_parent, name, repository, path):
            return self.root / name, {
                "repository": repository,
                "path": path,
                "revision": "abc123",
            }

        with patch.object(cli, "snapshot", side_effect=snapshot):
            sources, files = cli.collect()
        self.assertEqual(
            files["skills/thermo-nuclear-code-quality-review/SKILL.md"], original
        )
        self.assertEqual(
            files["skills/thermo-nuclear-code-quality-review/LICENSE.txt"],
            b"Cursor license\n",
        )
        for kind in ("api-design", "new-analysis"):
            name = f"roborev-analyze-{kind}"
            text = files[f"skills/{name}/SKILL.md"].decode()
            self.assertIn(f"\nname: {name}\n", text)
            description = text.split("\ndescription: ", 1)[1].splitlines()[0]
            self.assertTrue(json.loads(description))
            self.assertEqual(text.split("## Instructions\n\n", 1)[1], prompt)
            self.assertIn("/blob/abc123/internal/prompt/analyze/", text)
            self.assertEqual(files[f"skills/{name}/LICENSE.txt"], b"Roborev license\n")
        self.assertEqual(len(files), 7)
        self.assertEqual(sources["roborev"]["revision"], "abc123")

    def test_sync_is_repeatable_and_tracks_content(self):
        self.assertTrue(cli.sync(self.root, self.sources, self.files))
        manifest = json.loads((self.root / cli.LOCK).read_text())
        self.assertEqual(manifest["sources"], self.sources)
        self.assertEqual(manifest["files"][self.name], cli.digest(b"original\n"))
        self.assertFalse(cli.sync(self.root, self.sources, self.files))
        self.assertTrue(cli.sync(self.root, self.sources, {self.name: b"updated\n"}))
        self.assertEqual((self.root / self.name).read_bytes(), b"updated\n")

    def test_conflicts_block_all_writes_until_forced(self):
        cli.sync(self.root, self.sources, self.files)
        target = self.root / self.name
        target.write_bytes(b"local edit\n")
        other = "skills/another/SKILL.md"
        desired = {other: b"new skill\n", self.name: b"upstream edit\n"}
        lock = (self.root / cli.LOCK).read_bytes()
        with self.assertRaisesRegex(ValueError, "Local edits"):
            cli.sync(self.root, self.sources, desired)
        self.assertEqual(target.read_bytes(), b"local edit\n")
        self.assertFalse((self.root / other).exists())
        self.assertEqual((self.root / cli.LOCK).read_bytes(), lock)
        cli.sync(self.root, self.sources, desired, force=True)
        self.assertEqual(target.read_bytes(), b"upstream edit\n")

    def test_check_reports_changes_without_writing(self):
        self.assertTrue(cli.sync(self.root, self.sources, self.files, check=True))
        self.assertFalse((self.root / cli.LOCK).exists())
        self.assertFalse((self.root / self.name).exists())
        cli.sync(self.root, self.sources, self.files)
        self.assertFalse(cli.sync(self.root, self.sources, self.files, check=True))

    def test_sync_removes_obsolete_managed_files_but_preserves_unmanaged_files(self):
        cli.sync(self.root, self.sources, self.files)
        notes = self.root / "skills/example/notes.md"
        notes.write_bytes(b"local notes\n")
        cli.sync(self.root, self.sources, {})
        self.assertFalse((self.root / self.name).exists())
        self.assertEqual(notes.read_bytes(), b"local notes\n")

    def test_unmanaged_content_and_symlinks_are_protected(self):
        target = self.root / self.name
        target.parent.mkdir(parents=True)
        target.write_bytes(b"personal skill\n")
        with self.assertRaisesRegex(ValueError, "unmanaged"):
            cli.sync(self.root, self.sources, self.files)
        target.unlink()
        elsewhere = self.root / "keep.md"
        elsewhere.write_bytes(b"keep\n")
        target.symlink_to(elsewhere)
        with self.assertRaisesRegex(ValueError, "symlink"):
            cli.sync(self.root, self.sources, self.files, force=True)
        self.assertEqual(elsewhere.read_bytes(), b"keep\n")
        with self.assertRaisesRegex(ValueError, "Invalid managed path"):
            cli.sync(
                self.root,
                self.sources,
                {"skills/../../keep.md": b"overwrite"},
                force=True,
            )


if __name__ == "__main__":
    unittest.main()
