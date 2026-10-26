import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from qaw_tasks.cli import main


class CliTest(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.file = str(Path(self.directory.name) / "tasks.json")

    def tearDown(self) -> None:
        self.directory.cleanup()

    def run_cli(self, *args: str) -> tuple[int, str]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            code = main(["--file", self.file, *args])
        return code, output.getvalue()

    def test_add_list_done(self) -> None:
        self.assertEqual(self.run_cli("add", "Book the offsite", "--tag", "planning"),
                         (0, "Added task 1: Book the offsite\n"))
        code, listing = self.run_cli("list", "--tag", "planning")
        self.assertEqual(code, 0)
        self.assertIn("[ ]   1  Book the offsite", listing)
        self.assertEqual(self.run_cli("done", "1"), (0, "Finished task 1: Book the offsite\n"))
        self.assertEqual(self.run_cli("list"), (0, "No tasks.\n"))

    def test_stats(self) -> None:
        self.run_cli("add", "One", "--priority", "high")
        self.run_cli("add", "Two")
        code, output = self.run_cli("stats")
        self.assertEqual(code, 0)
        self.assertTrue(output.startswith("2 open, 0 done, 0 overdue\n"))

    def test_unknown_id_fails(self) -> None:
        self.assertEqual(self.run_cli("remove", "9"), (1, "qaw-tasks: No task with id 9.\n"))


if __name__ == "__main__":
    unittest.main()
