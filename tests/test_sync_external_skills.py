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

        anthropic = self.root / "anthropic" / cli.ANTHROPIC_PATH
        (anthropic / "scripts").mkdir(parents=True)
        (anthropic / "SKILL.md").write_bytes(
            b"---\nname: skill-creator\ndescription: Claude skill creator.\n---\n\nBody.\n"
        )
        (anthropic / "LICENSE.txt").write_bytes(b"Anthropic license\n")
        (anthropic / "scripts/run_eval.py").write_bytes(b"print('eval')\n")

        codex = self.root / "codex" / cli.CODEX_PATH
        (codex / "agents").mkdir(parents=True)
        (codex / "SKILL.md").write_bytes(
            b"---\nname: skill-creator\ndescription: Codex skill creator.\n---\n\nCodex.\n"
        )
        (codex / "license.txt").write_bytes(b"Codex license\n")
        (codex / "agents/openai.yaml").write_bytes(
            b'interface:\n  display_name: "Skill Creator"\n'
        )

        humanlayer = self.root / "humanlayer"
        show_me = humanlayer / cli.HUMANLAYER_PATH
        (show_me / "agents").mkdir(parents=True)
        show_me_skill = b"---\nname: show-me\ndescription: Show it.\n---\n\nDraw.\n"
        (show_me / "SKILL.md").write_bytes(show_me_skill)
        (show_me / "agents/openai.yaml").write_bytes(b"policy: {}\n")
        (humanlayer / "LICENSE").write_bytes(b"HumanLayer license\n")

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
        reference = "skills/tncqr2/references/thermo-nuclear-code-quality-review"
        self.assertEqual(files[f"{reference}.md"], original)
        self.assertEqual(files[f"{reference}.LICENSE.txt"], b"Cursor license\n")
        for kind in ("api-design", "new-analysis"):
            name = f"roborev-analyze-{kind}"
            text = files[f"skills/{name}/SKILL.md"].decode()
            self.assertIn(f"\nname: {name}\n", text)
            description = text.split("\ndescription: ", 1)[1].splitlines()[0]
            self.assertTrue(json.loads(description))
            self.assertEqual(text.split("## Instructions\n\n", 1)[1], prompt)
            self.assertIn("/blob/abc123/internal/prompt/analyze/", text)
            self.assertEqual(files[f"skills/{name}/LICENSE.txt"], b"Roborev license\n")
        self.assertEqual(
            files["skills/skill-creator-claude/SKILL.md"],
            b"---\nname: skill-creator-claude\ndescription: Claude skill creator.\n---\n\nBody.\n",
        )
        self.assertEqual(
            files["skills/skill-creator-claude/scripts/run_eval.py"],
            b"print('eval')\n",
        )
        self.assertIn(
            "https://github.com/anthropics/skills/tree/abc123/skills/skill-creator",
            files["skills/skill-creator-claude/SOURCE.md"].decode(),
        )
        self.assertEqual(
            files["skills/skill-creator-codex/SKILL.md"],
            b"---\nname: skill-creator-codex\ndescription: Codex skill creator.\n---\n\nCodex.\n",
        )
        self.assertEqual(
            files["skills/skill-creator-codex/agents/openai.yaml"],
            b'interface:\n  display_name: "Skill Creator"\n',
        )
        self.assertIn(
            "https://github.com/openai/codex/tree/abc123/codex-rs/skills/src/assets/samples/skill-creator",
            files["skills/skill-creator-codex/SOURCE.md"].decode(),
        )
        self.assertEqual(files["skills/show-me/SKILL.md"], show_me_skill)
        self.assertEqual(
            files["skills/show-me/agents/openai.yaml"], b"policy: {}\n"
        )
        self.assertEqual(
            files["skills/show-me/LICENSE.txt"], b"HumanLayer license\n"
        )
        self.assertIn(
            "https://github.com/humanlayer/skills/tree/abc123/plugins/show-me/skills/show-me",
            files["skills/show-me/SOURCE.md"].decode(),
        )
        self.assertEqual(len(files), 21)
        self.assertEqual(sources["roborev"]["revision"], "abc123")
        self.assertEqual(sources["anthropic"]["revision"], "abc123")
        self.assertEqual(sources["codex"]["revision"], "abc123")

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
        nested = "skills/example/scripts/helper.py"
        cli.sync(self.root, self.sources, {self.name: b"original\n", nested: b"pass\n"})
        notes = self.root / "skills/example/notes.md"
        notes.write_bytes(b"local notes\n")
        cli.sync(self.root, self.sources, {})
        self.assertFalse((self.root / self.name).exists())
        self.assertFalse((self.root / nested).exists())
        self.assertFalse((self.root / "skills/example/scripts").exists())
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
