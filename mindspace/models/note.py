"""Note data model."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Note:
    """Represents a note in Mindspace."""

    id: Optional[int] = None
    title: str = ""
    content: str = ""
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    category_color: Optional[str] = None
    is_pinned: bool = False
    is_favorite: bool = False
    is_archived: bool = False
    is_quick: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        now = datetime.now().isoformat()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = now

    @property
    def preview(self) -> str:
        """Returns a clean plain-text snippet of the note content."""
        if not self.content:
            return "No additional text"
        
        lines = [line.strip() for line in self.content.splitlines() if line.strip()]
        
        clean_lines = []
        for line in lines:
            cleaned = line.lstrip("# \t-*+>").replace("**", "").replace("*", "").replace("`", "")
            if cleaned:
                clean_lines.append(cleaned)
        return " — ".join(clean_lines[:2]) if clean_lines else "Empty note"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "category_id": self.category_id,
            "is_pinned": int(self.is_pinned),
            "is_favorite": int(self.is_favorite),
            "is_archived": int(self.is_archived),
            "is_quick": int(self.is_quick),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_row(cls, row) -> Optional["Note"]:
        if row is None:
            return None
        keys = row.keys()
        return cls(
            id=row["id"],
            title=row["title"],
            content=row["content"] or "",
            category_id=row["category_id"],
            category_name=row["category_name"] if "category_name" in keys else None,
            category_color=row["category_color"] if "category_color" in keys else None,
            is_pinned=bool(row["is_pinned"]),
            is_favorite=bool(row["is_favorite"]),
            is_archived=bool(row["is_archived"]),
            is_quick=bool(row["is_quick"]) if "is_quick" in keys else False,
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

