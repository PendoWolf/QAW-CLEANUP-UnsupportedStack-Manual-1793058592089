# qaw-tasks

A small command-line task tracker written in Python. It keeps tasks in a JSON file
(`~/.qaw-tasks.json` by default) and has no dependencies outside the standard library.

## Install

```
pip install .
```

## Use

```
qaw-tasks add "Write the release notes" --priority high --due 2026-11-01
qaw-tasks add "Book the team offsite" --tag planning
qaw-tasks list
qaw-tasks list --all --tag planning
qaw-tasks done 1
qaw-tasks remove 2
qaw-tasks stats
```

Use `--file PATH` (or the `QAW_TASKS_FILE` environment variable) to keep tasks somewhere else.
Run without installing with `python -m qaw_tasks` from the `src` folder.

## Test

```
PYTHONPATH=src python -m unittest discover -s tests
```
