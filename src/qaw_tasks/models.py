"""The task record and the values its fields can take."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Optional

PRIORITIES = ("low", "normal", "high")


@dataclass
class Task:
    id: int
    title: str
    priority: str = "normal"
    due: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    done_at: Optional[str] = None

    @property
    def done(self) -> bool:
        return self.done_at is not None

    def is_overdue(self, today: Optional[date] = None) -> bool:
        if self.done or not self.due:
            return False
        return date.fromisoformat(self.due) < (today or date.today())

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            id=int(data["id"]),
            title=str(data["title"]),
            priority=data.get("priority", "normal"),
            due=data.get("due"),
            tags=list(data.get("tags", [])),
            created_at=data.get("created_at", ""),
            done_at=data.get("done_at"),
        )


def parse_due(value: str) -> str:
    """Accept YYYY-MM-DD and return it unchanged, or raise ValueError."""
    return date.fromisoformat(value).isoformat()
