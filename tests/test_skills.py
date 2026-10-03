import importlib.machinery
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


loader = importlib.machinery.SourceFileLoader(
    "skills_cli", str(Path(__file__).resolve().parents[1] / "bin" / "skills")
)
spec = importlib.util.spec_from_loader(loader.name, loader)
cli = importlib.util.module_from_spec(spec)
loader.exec_module(cli)


class ActivationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.sources = root / "sources"
        self.active = root / "active"
        self.target = self.sources / "example"
        self.target.mkdir(parents=True)
        (self.target / "SKILL.md").write_text("example skill\n")
        self.active.mkdir()
        self.patcher = patch.multiple(cli, SOURCES=self.sources, ACTIVE=self.active)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def test_enable_and_disable_preserve_source(self):
        cli.enable("example")
        cli.enable("example")
        self.assertEqual((self.active / "example").resolve(), self.target.resolve())
        cli.disable("example")
        cli.disable("example")
        self.assertFalse((self.active / "example").is_symlink())
        self.assertEqual((self.target / "SKILL.md").read_text(), "example skill\n")

    def test_existing_directory_is_never_overwritten_or_deleted(self):
        existing = self.active / "example"
        existing.mkdir()
        (existing / "keep").write_text("keep\n")
        for action in (cli.enable, cli.disable):
            with self.assertRaises(ValueError):
                action("example")
            self.assertEqual((existing / "keep").read_text(), "keep\n")

    def test_foreign_links_including_broken_links_are_protected(self):
        existing = self.active / "example"
        for destination in (self.sources, self.sources / "missing"):
            existing.symlink_to(destination)
            for action in (cli.enable, cli.disable):
                with self.assertRaises(ValueError):
                    action("example")
                self.assertEqual(existing.readlink(), destination)
            existing.unlink()

    def test_names_cannot_escape_the_activation_directory(self):
        for name in ("../example", "/tmp/example", "example/other"):
            for action in (cli.enable, cli.disable):
                with self.assertRaises(ValueError):
                    action(name)

    def test_update_does_not_pull_dirty_checkout(self):
        with patch.object(cli, "git", return_value=" M skills/example/SKILL.md"):
            with patch.object(cli.subprocess, "run") as run:
                with self.assertRaises(ValueError):
                    cli.update()
                run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
