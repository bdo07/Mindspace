"""Category data model."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Category:
    """Represents a category for notes and tasks."""

    id: Optional[int] = None
    name: str = ""
    color: str = "#15370D"
    icon: str = "folder"
    created_at: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "icon": self.icon,
            "created_at": self.created_at,
        }

    @classmethod
    def from_row(cls, row) -> "Category":
        if row is None:
            return None
        return cls(
            id=row["id"],
            name=row["name"],
            color=row["color"],
            icon=row["icon"] if "icon" in row.keys() else "folder",
            created_at=row["created_at"],
        )

