"""Task data model."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    """Represents a to-do task in Mindspace."""

    id: Optional[int] = None
    title: str = ""
    description: str = ""
    is_completed: bool = False
    due_date: Optional[str] = None
    priority: str = "normal"
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    category_color: Optional[str] = None
    completed_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        now = datetime.now().isoformat()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "is_completed": int(self.is_completed),
            "due_date": self.due_date,
            "priority": self.priority,
            "category_id": self.category_id,
            "completed_at": self.completed_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_row(cls, row) -> Optional["Task"]:
        if row is None:
            return None
        keys = row.keys()
        return cls(
            id=row["id"],
            title=row["title"],
            description=row["description"] or "",
            is_completed=bool(row["is_completed"]),
            due_date=row["due_date"],
            priority=row["priority"] if "priority" in keys else "normal",
            category_id=row["category_id"],
            category_name=row["category_name"] if "category_name" in keys else None,
            category_color=row["category_color"] if "category_color" in keys else None,
            completed_at=row["completed_at"] if "completed_at" in keys else None,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

