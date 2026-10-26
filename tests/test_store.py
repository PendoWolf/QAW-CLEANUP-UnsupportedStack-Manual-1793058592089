import tempfile
import unittest
from datetime import date
from pathlib import Path

from qaw_tasks.store import TaskNotFound, TaskStore


class TaskStoreTest(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / "tasks.json"

    def tearDown(self) -> None:
        self.directory.cleanup()

    def test_add_saves_and_reloads(self) -> None:
        store = TaskStore(self.path)
        task = store.add("Write the release notes", priority="high", tags=["Docs", "docs"])
        reloaded = TaskStore(self.path).get(task.id)
        self.assertEqual(reloaded.title, "Write the release notes")
        self.assertEqual(reloaded.priority, "high")
        self.assertEqual(reloaded.tags, ["docs"])

    def test_ids_keep_counting_after_a_remove(self) -> None:
        store = TaskStore(self.path)
        first = store.add("One")
        second = store.add("Two")
        store.remove(first.id)
        self.assertEqual(store.add("Three").id, second.id + 1)

    def test_complete_and_query(self) -> None:
        store = TaskStore(self.path)
        low = store.add("Low", priority="low")
        high = store.add("High", priority="high")
        store.complete(low.id)
        self.assertEqual([task.id for task in store.query()], [high.id])
        self.assertEqual([task.id for task in store.query(include_done=True)], [high.id, low.id])

    def test_unknown_task(self) -> None:
        with self.assertRaises(TaskNotFound):
            TaskStore(self.path).complete(42)

    def test_rejects_an_empty_title(self) -> None:
        with self.assertRaises(ValueError):
            TaskStore(self.path).add("   ")

    def test_overdue(self) -> None:
        store = TaskStore(self.path)
        task = store.add("Late", due="2020-01-01")
        self.assertTrue(task.is_overdue(today=date(2026, 1, 1)))
        self.assertEqual(store.stats()["overdue"], 1)


if __name__ == "__main__":
    unittest.main()
