"""Unit tests for services: NoteService, TaskService, CategoryService, SettingsService."""

import tempfile
import unittest
from pathlib import Path

from mindspace.database.connection import DatabaseConnection
from mindspace.database.repository import MindspaceRepository
from mindspace.services.category_service import CategoryService
from mindspace.services.note_service import NoteService
from mindspace.services.settings_service import SettingsService
from mindspace.services.task_service import TaskService


class TestServices(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_services.db"
        self.conn = DatabaseConnection(str(self.db_path))
        self.repo = MindspaceRepository(self.conn)

        self.note_service = NoteService(self.repo)
        self.task_service = TaskService(self.repo)
        self.category_service = CategoryService(self.repo)
        self.settings_service = SettingsService(self.repo)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_note_service_pin_and_favorite(self):
        note = self.note_service.create_note(title="Pin Test", content="Testing pin/favorite")
        self.assertFalse(note.is_pinned)
        self.assertFalse(note.is_favorite)

        # Pin
        pinned = self.note_service.toggle_pin(note.id)
        self.assertTrue(pinned.is_pinned)

        # Favorite
        favorited = self.note_service.toggle_favorite(note.id)
        self.assertTrue(favorited.is_favorite)

        # Archive
        archived = self.note_service.archive_note(note.id)
        self.assertTrue(archived.is_archived)

        # Restore
        restored = self.note_service.restore_note(note.id)
        self.assertFalse(restored.is_archived)

    def test_quick_notes_flow(self):
        """Tests quick note creation and conversion to regular note."""
        quick = self.note_service.create_quick_note("Remember to buy organic tea tomorrow")
        self.assertTrue(quick.is_quick)
        self.assertEqual(quick.title, "Remember to buy organic tea tomorrow")

        converted = self.note_service.convert_quick_to_regular(quick.id)
        self.assertFalse(converted.is_quick)

    def test_task_service_completion(self):
        task = self.task_service.create_task(title="Review PR", priority="high")
        self.assertFalse(task.is_completed)
        self.assertIsNone(task.completed_at)

        completed = self.task_service.toggle_completed(task.id)
        self.assertTrue(completed.is_completed)
        self.assertIsNotNone(completed.completed_at)

        # Toggle back
        reopened = self.task_service.toggle_completed(task.id)
        self.assertFalse(reopened.is_completed)
        self.assertIsNone(reopened.completed_at)

    def test_category_service(self):
        cat = self.category_service.create_category(name="Health & Fitness", color="#00B894")
        self.assertIsNotNone(cat.id)
        self.assertEqual(cat.name, "Health & Fitness")

        # Assign note to category
        note = self.note_service.create_note(title="Gym routine", content="3x weekly", category_id=cat.id)
        self.assertEqual(note.category_id, cat.id)

        counts = self.category_service.get_note_counts()
        self.assertEqual(counts.get(cat.id), 1)

    def test_settings_service_theme_persistence(self):
        settings = self.settings_service.get_settings()
        self.assertEqual(settings.theme, "light")

        self.settings_service.set_theme("dark")
        self.assertEqual(self.settings_service.get_settings().theme, "dark")

        # Reload from fresh service instance
        fresh_service = SettingsService(self.repo)
        self.assertEqual(fresh_service.get_settings().theme, "dark")


if __name__ == "__main__":
    unittest.main()

