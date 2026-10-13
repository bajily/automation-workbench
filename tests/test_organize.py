import tempfile
import unittest
from pathlib import Path

from organize import apply, plan


class OrganizerTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.source, self.destination = self.root / "in", self.root / "out"
        self.source.mkdir()

    def test_dry_run_creates_nothing(self):
        (self.source / "report.pdf").write_bytes(b"sample")
        operations = plan(self.source, self.destination)
        self.assertEqual(operations[0]["category"], "documents")
        self.assertFalse(self.destination.exists())

    def test_apply_preserves_original_and_content(self):
        data = bytes(range(256))
        (self.source / "photo.PNG").write_bytes(data)
        copied = apply(plan(self.source, self.destination))
        self.assertEqual(len(copied), 1)
        self.assertEqual((self.destination / "images/photo.PNG").read_bytes(), data)
        self.assertEqual((self.source / "photo.PNG").read_bytes(), data)

    def test_all_categories(self):
        for name in ["a.txt", "b.jpg", "c.csv", "d.zip", "e.py", "f.unknown"]:
            (self.source / name).touch()
        self.assertEqual({x["category"] for x in plan(self.source, self.destination)},
                         {"documents", "images", "data", "archives", "code", "other"})

    def test_subdirectories_are_ignored(self):
        (self.source / "nested").mkdir()
        (self.source / "nested/file.txt").touch()
        self.assertEqual(plan(self.source, self.destination), [])

    def test_nested_destinations_rejected(self):
        for destination in [self.source, self.source / "out", self.root]:
            with self.subTest(destination=destination), self.assertRaises(ValueError):
                plan(self.source, destination)

    def test_collision_rejected_without_overwrite(self):
        (self.source / "a.txt").write_text("new")
        (self.destination / "documents").mkdir(parents=True)
        target = self.destination / "documents/a.txt"
        target.write_text("original")
        with self.assertRaises(FileExistsError):
            plan(self.source, self.destination)
        self.assertEqual(target.read_text(), "original")

    def test_collision_after_planning_rejected(self):
        (self.source / "a.txt").write_text("new")
        operations = plan(self.source, self.destination)
        (self.destination / "documents").mkdir(parents=True)
        target = self.destination / "documents/a.txt"
        target.write_text("original")
        with self.assertRaises(FileExistsError):
            apply(operations)
        self.assertEqual(target.read_text(), "original")

    def test_symlink_source_is_skipped(self):
        outside = self.root / "outside.txt"
        outside.write_text("content")
        try:
            (self.source / "link.txt").symlink_to(outside)
        except OSError:
            self.skipTest("symlinks unavailable")
        self.assertEqual(plan(self.source, self.destination), [])

    def test_symlink_category_is_rejected(self):
        (self.source / "a.txt").touch()
        self.destination.mkdir()
        try:
            (self.destination / "documents").symlink_to(self.source, target_is_directory=True)
        except OSError:
            self.skipTest("symlinks unavailable")
        with self.assertRaises(ValueError):
            plan(self.source, self.destination)

    def test_missing_source(self):
        with self.assertRaises(FileNotFoundError):
            plan(self.root / "missing", self.destination)


if __name__ == "__main__":
    unittest.main()
