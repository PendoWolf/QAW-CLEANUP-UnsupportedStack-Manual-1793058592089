"""The qaw-tasks command line: parses arguments and prints results to the terminal."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

from qaw_tasks import __version__
from qaw_tasks.models import PRIORITIES, Task, parse_due
from qaw_tasks.store import TaskNotFound, TaskStore


def _due_date(value: str) -> str:
    try:
        return parse_due(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a date like 2026-11-01")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="qaw-tasks", description="Track tasks from the terminal.")
    parser.add_argument("--file", type=Path, help="task file (default: ~/.qaw-tasks.json)")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    add = commands.add_parser("add", help="add a task")
    add.add_argument("title")
    add.add_argument("--priority", choices=PRIORITIES, default="normal")
    add.add_argument("--due", type=_due_date, help="due date, YYYY-MM-DD")
    add.add_argument("--tag", action="append", default=[], dest="tags", help="tag (repeatable)")

    show = commands.add_parser("list", help="list open tasks")
    show.add_argument("--all", action="store_true", help="include finished tasks")
    show.add_argument("--tag", help="only tasks with this tag")

    done = commands.add_parser("done", help="mark a task finished")
    done.add_argument("id", type=int)

    remove = commands.add_parser("remove", help="delete a task")
    remove.add_argument("id", type=int)

    commands.add_parser("stats", help="count tasks by state and priority")
    return parser


def format_task(task: Task) -> str:
    mark = "x" if task.done else " "
    parts = [f"[{mark}] {task.id:>3}  {task.title}"]
    if task.priority != "normal":
        parts.append(f"!{task.priority}")
    if task.due:
        parts.append(f"due {task.due}" + (" (overdue)" if task.is_overdue() else ""))
    if task.tags:
        parts.append(" ".join(f"#{tag}" for tag in task.tags))
    return "  ".join(parts)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    store = TaskStore(args.file)
    try:
        if args.command == "add":
            task = store.add(args.title, priority=args.priority, due=args.due, tags=args.tags)
            print(f"Added task {task.id}: {task.title}")
        elif args.command == "list":
            tasks = store.query(include_done=args.all, tag=args.tag)
            if not tasks:
                print("No tasks.")
            for task in tasks:
                print(format_task(task))
        elif args.command == "done":
            task = store.complete(args.id)
            print(f"Finished task {task.id}: {task.title}")
        elif args.command == "remove":
            task = store.remove(args.id)
            print(f"Removed task {task.id}: {task.title}")
        elif args.command == "stats":
            counts = store.stats()
            print(f"{counts['open']} open, {counts['done']} done, {counts['overdue']} overdue")
            for name in reversed(PRIORITIES):
                print(f"  {name:<7}{counts['by_priority'][name]}")
    except (TaskNotFound, ValueError) as error:
        print(f"qaw-tasks: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
