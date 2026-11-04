"""Database repository performing parameterized SQL operations for Mindspace."""

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

from mindspace.database.connection import DatabaseConnection
from mindspace.database.schema import initialize_schema
from mindspace.models.category import Category
from mindspace.models.note import Note
from mindspace.models.task import Task


class MindspaceRepository:
    """Data Access Object for Notes, Tasks, Categories, and Settings."""

    def __init__(self, db: DatabaseConnection):
        self.db = db
        # Ensure schema is initialized
        with self.db.session() as conn:
            initialize_schema(conn)

    
    def get_note(self, note_id: int) -> Optional[Note]:
        """Fetch a single note by ID with its category information."""
        with self.db.session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT n.*, c.name AS category_name, c.color AS category_color
                FROM notes n
                LEFT JOIN categories c ON n.category_id = c.id
                WHERE n.id = ?
                """,
                (note_id,),
            )
            row = cursor.fetchone()
            return Note.from_row(row) if row else None

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
        """List notes matching various filter criteria."""
        with self.db.session() as conn:
            cursor = conn.cursor()
            conditions = ["n.is_archived = ?"]
            params: list = [1 if is_archived else 0]

            if category_id is not None:
                conditions.append("n.category_id = ?")
                params.append(category_id)

            if is_favorite is not None:
                conditions.append("n.is_favorite = ?")
                params.append(1 if is_favorite else 0)

            if is_quick is not None:
                conditions.append("n.is_quick = ?")
                params.append(1 if is_quick else 0)

            if search_query and search_query.strip():
                term = f"%{search_query.strip()}%"
                conditions.append("(n.title LIKE ? OR n.content LIKE ?)")
                params.extend([term, term])

            valid_sort_columns = {
                "updated_at": "n.updated_at",
                "created_at": "n.created_at",
                "title": "n.title",
                "is_pinned": "n.is_pinned",
            }
            order_col = valid_sort_columns.get(sort_by, "n.updated_at")
            order_dir = "DESC" if sort_desc else "ASC"

            where_clause = " AND ".join(conditions)
            sql = f"""
                SELECT n.*, c.name AS category_name, c.color AS category_color
                FROM notes n
                LEFT JOIN categories c ON n.category_id = c.id
                WHERE {where_clause}
                ORDER BY n.is_pinned DESC, {order_col} {order_dir}
            """
            cursor.execute(sql, params)
            return [Note.from_row(row) for row in cursor.fetchall() if row]

    def create_note(self, note: Note) -> int:
        """Insert a new note and return its generated ID."""
        with self.db.session() as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            cursor.execute(
                """
                INSERT INTO notes (
                    title, content, category_id, is_pinned, is_favorite,
                    is_archived, is_quick, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    note.title,
                    note.content,
                    note.category_id,
                    1 if note.is_pinned else 0,
                    1 if note.is_favorite else 0,
                    1 if note.is_archived else 0,
                    1 if note.is_quick else 0,
                    note.created_at or now,
                    now,
                ),
            )
            note.id = cursor.lastrowid
            return note.id

    def update_note(self, note: Note) -> bool:
        """Update an existing note."""
        if not note.id:
            return False
        with self.db.session() as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            cursor.execute(
                """
                UPDATE notes
                SET title = ?, content = ?, category_id = ?,
                    is_pinned = ?, is_favorite = ?, is_archived = ?,
                    is_quick = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    note.title,
                    note.content,
                    note.category_id,
                    1 if note.is_pinned else 0,
                    1 if note.is_favorite else 0,
                    1 if note.is_archived else 0,
                    1 if note.is_quick else 0,
                    now,
                    note.id,
                ),
            )
            note.updated_at = now
            return cursor.rowcount > 0

    def delete_note(self, note_id: int) -> bool:
        """Delete note permanently."""
        with self.db.session() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            return cursor.rowcount > 0

    def count_notes(
        self,
        is_archived: bool = False,
        is_favorite: Optional[bool] = None,
        is_quick: Optional[bool] = None,
        category_id: Optional[int] = None,
    ) -> int:
        """Count notes meeting criteria."""
        with self.db.session() as conn:
            cursor = conn.cursor()
            conditions = ["is_archived = ?"]
            params: list = [1 if is_archived else 0]

            if is_favorite is not None:
                conditions.append("is_favorite = ?")
                params.append(1 if is_favorite else 0)
            if is_quick is not None:
                conditions.append("is_quick = ?")
                params.append(1 if is_quick else 0)
            if category_id is not None:
                conditions.append("category_id = ?")
                params.append(category_id)

            where_clause = " AND ".join(conditions)
            cursor.execute(f"SELECT COUNT(*) FROM notes WHERE {where_clause}", params)
            return cursor.fetchone()[0]

    

    def get_task(self, task_id: int) -> Optional[Task]:
        """Fetch a single task by ID."""
        with self.db.session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT t.*, c.name AS category_name, c.color AS category_color
                FROM tasks t
                LEFT JOIN categories c ON t.category_id = c.id
                WHERE t.id = ?
                """,
                (task_id,),
            )
            row = cursor.fetchone()
            return Task.from_row(row) if row else None

    def list_tasks(
        self,
        is_completed: Optional[bool] = None,
        category_id: Optional[int] = None,
        search_query: Optional[str] = None,
    ) -> List[Task]:
        """List tasks ordered by completion and due date."""
        with self.db.session() as conn:
            cursor = conn.cursor()
            conditions = []
            params: list = []

            if is_completed is not None:
                conditions.append("t.is_completed = ?")
                params.append(1 if is_completed else 0)

            if category_id is not None:
                conditions.append("t.category_id = ?")
                params.append(category_id)

            if search_query and search_query.strip():
                term = f"%{search_query.strip()}%"
                conditions.append("(t.title LIKE ? OR t.description LIKE ?)")
                params.extend([term, term])

            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
            sql = f"""
                SELECT t.*, c.name AS category_name, c.color AS category_color
                FROM tasks t
                LEFT JOIN categories c ON t.category_id = c.id
                {where_clause}
                ORDER BY
                    t.is_completed ASC,
                    CASE WHEN t.due_date IS NULL THEN 1 ELSE 0 END,
                    t.due_date ASC,
                    t.id DESC
            """
            cursor.execute(sql, params)
            return [Task.from_row(row) for row in cursor.fetchall() if row]

    def create_task(self, task: Task) -> int:
        """Insert a task and return its ID."""
        with self.db.session() as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            cursor.execute(
                """
                INSERT INTO tasks (
                    title, description, is_completed, due_date, priority,
                    category_id, completed_at, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task.title,
                    task.description,
                    1 if task.is_completed else 0,
                    task.due_date,
                    task.priority,
                    task.category_id,
                    task.completed_at,
                    task.created_at or now,
                    now,
                ),
            )
            task.id = cursor.lastrowid
            return task.id

    def update_task(self, task: Task) -> bool:
        """Update existing task."""
        if not task.id:
            return False
        with self.db.session() as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            cursor.execute(
                """
                UPDATE tasks
                SET title = ?, description = ?, is_completed = ?,
                    due_date = ?, priority = ?, category_id = ?,
                    completed_at = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    task.title,
                    task.description,
                    1 if task.is_completed else 0,
                    task.due_date,
                    task.priority,
                    task.category_id,
                    task.completed_at,
                    now,
                    task.id,
                ),
            )
            task.updated_at = now
            return cursor.rowcount > 0

    def delete_task(self, task_id: int) -> bool:
        """Delete task permanently."""
        with self.db.session() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            return cursor.rowcount > 0

    def count_pending_tasks(self) -> int:
        """Count non-completed tasks."""
        with self.db.session() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE is_completed = 0")
            return cursor.fetchone()[0]

    

    def list_categories(self) -> List[Category]:
        """List all categories ordered by name."""
        with self.db.session() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categories ORDER BY name ASC")
            return [Category.from_row(row) for row in cursor.fetchall() if row]

    def get_category(self, category_id: int) -> Optional[Category]:
        """Fetch single category by ID."""
        with self.db.session() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categories WHERE id = ?", (category_id,))
            row = cursor.fetchone()
            return Category.from_row(row) if row else None

    def create_category(self, category: Category) -> int:
        """Create a new category."""
        with self.db.session() as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            cursor.execute(
                "INSERT INTO categories (name, color, icon, created_at) VALUES (?, ?, ?, ?)",
                (category.name, category.color, category.icon, category.created_at or now),
            )
            category.id = cursor.lastrowid
            return category.id

    def update_category(self, category: Category) -> bool:
        """Update category attributes."""
        if not category.id:
            return False
        with self.db.session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE categories SET name = ?, color = ?, icon = ? WHERE id = ?",
                (category.name, category.color, category.icon, category.id),
            )
            return cursor.rowcount > 0

    def delete_category(self, category_id: int) -> bool:
        """Delete category; references in notes and tasks become NULL via ON DELETE SET NULL."""
        with self.db.session() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            return cursor.rowcount > 0

    def get_category_note_counts(self) -> Dict[int, int]:
        """Returns mapping of category_id -> unarchived note count."""
        with self.db.session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT category_id, COUNT(*) AS cnt
                FROM notes
                WHERE is_archived = 0 AND category_id IS NOT NULL
                GROUP BY category_id
                """
            )
            return {row["category_id"]: row["cnt"] for row in cursor.fetchall()}

    

    def get_settings(self) -> Dict[str, str]:
        """Fetch all key-value settings."""
        with self.db.session() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM settings")
            return {row["key"]: row["value"] for row in cursor.fetchall()}

    def update_setting(self, key: str, value: str) -> None:
        """Insert or replace a setting."""
        with self.db.session() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, str(value)),
            )

    def update_settings(self, settings_dict: Dict[str, str]) -> None:
        """Batch update settings."""
        with self.db.session() as conn:
            cursor = conn.cursor()
            for key, val in settings_dict.items():
                cursor.execute(
                    "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                    (key, str(val)),
                )

