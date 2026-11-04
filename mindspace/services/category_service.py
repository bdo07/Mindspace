"""Service layer for Category operations."""

from datetime import datetime
from typing import Dict, List, Optional

from mindspace.database.repository import MindspaceRepository
from mindspace.models.category import Category


class CategoryService:
    """Business logic for Categories."""

    def __init__(self, repo: MindspaceRepository):
        self.repo = repo

    def list_categories(self) -> List[Category]:
        return self.repo.list_categories()

    def get_category(self, category_id: int) -> Optional[Category]:
        return self.repo.get_category(category_id)

    def create_category(self, name: str, color: str = "#15370D", icon: str = "folder") -> Category:
        name = name.strip()
        if not name:
            raise ValueError("Category name cannot be empty")
        now = datetime.now().isoformat()
        category = Category(name=name, color=color, icon=icon, created_at=now)
        cat_id = self.repo.create_category(category)
        category.id = cat_id
        return category

    def update_category(
        self,
        category_id: int,
        name: Optional[str] = None,
        color: Optional[str] = None,
        icon: Optional[str] = None,
    ) -> Optional[Category]:
        cat = self.repo.get_category(category_id)
        if not cat:
            return None
        if name is not None:
            clean_name = name.strip()
            if clean_name:
                cat.name = clean_name
        if color is not None:
            cat.color = color
        if icon is not None:
            cat.icon = icon

        self.repo.update_category(cat)
        return self.repo.get_category(category_id)

    def delete_category(self, category_id: int) -> bool:
        return self.repo.delete_category(category_id)

    def get_note_counts(self) -> Dict[int, int]:
        return self.repo.get_category_note_counts()

