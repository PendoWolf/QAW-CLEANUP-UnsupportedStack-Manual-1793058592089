"""Reads and writes the task list as a JSON file."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

from qaw_tasks.models import PRIORITIES, Task

DEFAULT_FILE = Path.home() / ".qaw-tasks.json"


class TaskNotFound(LookupError):
    pass


class TaskStore:
    def __init__(self, path: Optional[Path] = None) -> None:
        env_path = os.environ.get("QAW_TASKS_FILE")
        self.path = Path(path or env_path or DEFAULT_FILE)
        self.tasks: list[Task] = []
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            self.tasks = []
            return
        with self.path.open(encoding="utf-8") as handle:
            data = json.load(handle)
        self.tasks = [Task.from_dict(item) for item in data.get("tasks", [])]

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"version": 1, "tasks": [task.to_dict() for task in self.tasks]}
        # Write to a temporary file first so a crash never leaves a half-written list.
        fd, tmp_name = tempfile.mkstemp(dir=self.path.parent, prefix=".qaw-tasks-")
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
        os.replace(tmp_name, self.path)

    def _next_id(self) -> int:
        return max((task.id for task in self.tasks), default=0) + 1

    def add(self, title: str, priority: str = "normal", due: Optional[str] = None,
            tags: Iterable[str] = ()) -> Task:
        title = title.strip()
        if not title:
            raise ValueError("A task needs a title.")
        if priority not in PRIORITIES:
            raise ValueError(f"Priority must be one of: {', '.join(PRIORITIES)}.")
        task = Task(id=self._next_id(), title=title, priority=priority, due=due,
                    tags=sorted({tag.strip().lower() for tag in tags if tag.strip()}))
        self.tasks.append(task)
        self.save()
        return task

    def get(self, task_id: int) -> Task:
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise TaskNotFound(f"No task with id {task_id}.")

    def complete(self, task_id: int) -> Task:
        task = self.get(task_id)
        if not task.done:
            task.done_at = datetime.now().isoformat(timespec="seconds")
            self.save()
        return task

    def remove(self, task_id: int) -> Task:
        task = self.get(task_id)
        self.tasks.remove(task)
        self.save()
        return task

    def query(self, include_done: bool = False, tag: Optional[str] = None) -> list[Task]:
        rank = {name: index for index, name in enumerate(reversed(PRIORITIES))}
        found = [
            task for task in self.tasks
            if (include_done or not task.done) and (tag is None or tag.lower() in task.tags)
        ]
        return sorted(found, key=lambda task: (task.done, rank[task.priority], task.due or "9999", task.id))

    def stats(self) -> dict:
        open_tasks = [task for task in self.tasks if not task.done]
        return {
            "total": len(self.tasks),
            "open": len(open_tasks),
            "done": len(self.tasks) - len(open_tasks),
            "overdue": sum(1 for task in open_tasks if task.is_overdue()),
            "by_priority": {name: sum(1 for task in open_tasks if task.priority == name) for name in PRIORITIES},
        }
