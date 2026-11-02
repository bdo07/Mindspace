"""Service layer for Task operations."""

from datetime import datetime
from typing import List, Optional

from mindspace.database.repository import MindspaceRepository
from mindspace.models.task import Task


class TaskService:
    """Business logic for tasks and to-dos."""

    def __init__(self, repo: MindspaceRepository):
        self.repo = repo

    def get_task(self, task_id: int) -> Optional[Task]:
        return self.repo.get_task(task_id)

    def create_task(
        self,
        title: str,
        description: str = "",
        due_date: Optional[str] = None,
        priority: str = "normal",
        category_id: Optional[int] = None,
    ) -> Task:
        title = title.strip()
        if not title:
            raise ValueError("Task title cannot be empty")

        now = datetime.now().isoformat()
        task = Task(
            title=title,
            description=description.strip(),
            is_completed=False,
            due_date=due_date if due_date else None,
            priority=priority or "normal",
            category_id=category_id if category_id != 0 else None,
            completed_at=None,
            created_at=now,
            updated_at=now,
        )
        task_id = self.repo.create_task(task)
        task.id = task_id
        return self.repo.get_task(task_id) or task

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        is_completed: Optional[bool] = None,
        due_date: Optional[str] = None,
        priority: Optional[str] = None,
        category_id: Optional[int] = None,
    ) -> Optional[Task]:
        task = self.repo.get_task(task_id)
        if not task:
            return None

        if title is not None:
            clean_title = title.strip()
            if clean_title:
                task.title = clean_title
        if description is not None:
            task.description = description
        if is_completed is not None:
            task.is_completed = is_completed
            task.completed_at = datetime.now().isoformat() if is_completed else None
        if due_date is not None:
            task.due_date = due_date if due_date else None
        if priority is not None:
            task.priority = priority
        if category_id is not None:
            task.category_id = category_id if category_id != 0 else None

        self.repo.update_task(task)
        return self.repo.get_task(task_id)

    def toggle_completed(self, task_id: int) -> Optional[Task]:
        task = self.repo.get_task(task_id)
        if not task:
            return None
        return self.update_task(task_id, is_completed=not task.is_completed)

    def delete_task(self, task_id: int) -> bool:
        return self.repo.delete_task(task_id)

    def list_tasks(
        self,
        is_completed: Optional[bool] = None,
        category_id: Optional[int] = None,
        search_query: Optional[str] = None,
    ) -> List[Task]:
        return self.repo.list_tasks(
            is_completed=is_completed,
            category_id=category_id,
            search_query=search_query,
        )

    def count_pending(self) -> int:
        return self.repo.count_pending_tasks()

