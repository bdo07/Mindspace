"""Service layer for Note operations."""

from datetime import datetime
from typing import List, Optional

from mindspace.database.repository import MindspaceRepository
from mindspace.models.note import Note


class NoteService:
    """Business logic for notes."""

    def __init__(self, repo: MindspaceRepository):
        self.repo = repo

    def get_note(self, note_id: int) -> Optional[Note]:
        return self.repo.get_note(note_id)

    def create_note(
        self,
        title: str = "Untitled Note",
        content: str = "",
        category_id: Optional[int] = None,
        is_pinned: bool = False,
        is_favorite: bool = False,
        is_quick: bool = False,
    ) -> Note:
        title = title.strip() or "Untitled Note"
        now = datetime.now().isoformat()
        note = Note(
            title=title,
            content=content,
            category_id=category_id,
            is_pinned=is_pinned,
            is_favorite=is_favorite,
            is_archived=False,
            is_quick=is_quick,
            created_at=now,
            updated_at=now,
        )
        note_id = self.repo.create_note(note)
        note.id = note_id
         
        return self.repo.get_note(note_id) or note

    def update_note(
        self,
        note_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        category_id: Optional[int] = None,
        is_pinned: Optional[bool] = None,
        is_favorite: Optional[bool] = None,
        is_archived: Optional[bool] = None,
    ) -> Optional[Note]:
        note = self.repo.get_note(note_id)
        if not note:
            return None

        if title is not None:
            note.title = title.strip() or "Untitled Note"
        if content is not None:
            note.content = content
        if category_id is not None:
            note.category_id = category_id if category_id != 0 else None
        if is_pinned is not None:
            note.is_pinned = is_pinned
        if is_favorite is not None:
            note.is_favorite = is_favorite
        if is_archived is not None:
            note.is_archived = is_archived

        self.repo.update_note(note)
        return self.repo.get_note(note_id)

    def delete_note(self, note_id: int) -> bool:
        return self.repo.delete_note(note_id)

    def toggle_pin(self, note_id: int) -> Optional[Note]:
        note = self.repo.get_note(note_id)
        if not note:
            return None
        return self.update_note(note_id, is_pinned=not note.is_pinned)

    def toggle_favorite(self, note_id: int) -> Optional[Note]:
        note = self.repo.get_note(note_id)
        if not note:
            return None
        return self.update_note(note_id, is_favorite=not note.is_favorite)

    def archive_note(self, note_id: int) -> Optional[Note]:
        return self.update_note(note_id, is_archived=True)

    def restore_note(self, note_id: int) -> Optional[Note]:
        return self.update_note(note_id, is_archived=False)

    def list_notes(
        self,
        category_id: Optional[int] = None,
        is_favorite: Optional[bool] = None,
        is_archived: bool = False,
        is_quick: Optional[bool] = None,
        search_query: Optional[str] = None,
        sort_by: str = "updated_at",
        sort_desc: bool = True,
    ) -> List[Note]:
        return self.repo.list_notes(
            category_id=category_id,
            is_favorite=is_favorite,
            is_archived=is_archived,
            is_quick=is_quick,
            search_query=search_query,
            sort_by=sort_by,
            sort_desc=sort_desc,
        )

    def create_quick_note(self, content: str) -> Note:
        """Create a quick note from text snippet."""
        clean_content = content.strip()
        first_line = clean_content.splitlines()[0] if clean_content else "Quick Thought"
        if len(first_line) > 60:
            title = first_line[:57] + "..."
        else:
            title = first_line
        return self.create_note(title=title, content=clean_content, is_quick=True)

    def convert_quick_to_regular(self, note_id: int) -> Optional[Note]:
        note = self.repo.get_note(note_id)
        if not note:
            return None
        note.is_quick = False
        self.repo.update_note(note)
        return self.repo.get_note(note_id)

    def get_counts(self) -> dict:
        return {
            "all": self.repo.count_notes(is_archived=False, is_quick=False),
            "quick": self.repo.count_notes(is_archived=False, is_quick=True),
            "favorites": self.repo.count_notes(is_archived=False, is_favorite=True),
            "archived": self.repo.count_notes(is_archived=True),
        }

