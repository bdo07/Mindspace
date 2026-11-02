"""Unit tests for DatabaseConnection, schema initialization, and repository operations."""

import tempfile
import unittest
from pathlib import Path

from mindspace.database.connection import DatabaseConnection
from mindspace.database.repository import MindspaceRepository
from mindspace.models.category import Category
from mindspace.models.note import Note
from mindspace.models.task import Task


class TestDatabaseLayer(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_mindspace.db"
        self.conn = DatabaseConnection(str(self.db_path))
        self.repo = MindspaceRepository(self.conn)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_schema_initialization_and_seeds(self):
        """Verifies default categories and welcome note are seeded."""
        categories = self.repo.list_categories()
        self.assertGreaterEqual(len(categories), 4)
        cat_names = [c.name for c in categories]
        self.assertIn("Personal", cat_names)
        self.assertIn("Work", cat_names)

        notes = self.repo.list_notes()
        self.assertGreaterEqual(len(notes), 1)
        welcome_note = notes[0]
        self.assertIn("Welcome to MINDSPACE", welcome_note.title)

        tasks = self.repo.list_tasks()
        self.assertGreaterEqual(len(tasks), 1)

    def test_notes_crud(self):
        """Tests note creation, retrieval, updating, and deletion."""
        note = Note(title="Project Roadmap", content="Step 1: Planning\nStep 2: Execution")
        note_id = self.repo.create_note(note)
        self.assertIsNotNone(note_id)

        fetched = self.repo.get_note(note_id)
        self.assertEqual(fetched.title, "Project Roadmap")
        self.assertEqual(fetched.content, "Step 1: Planning\nStep 2: Execution")

        # Update
        fetched.title = "Updated Roadmap"
        fetched.is_favorite = True
        self.assertTrue(self.repo.update_note(fetched))

        updated = self.repo.get_note(note_id)
        self.assertEqual(updated.title, "Updated Roadmap")
        self.assertTrue(updated.is_favorite)

        # Delete
        self.assertTrue(self.repo.delete_note(note_id))
        self.assertIsNone(self.repo.get_note(note_id))

    def test_tasks_crud(self):
        """Tests task lifecycle and completion toggle."""
        task = Task(title="Buy milk", priority="high", due_date="2026-12-01")
        task_id = self.repo.create_task(task)
        self.assertIsNotNone(task_id)

        fetched = self.repo.get_task(task_id)
        self.assertEqual(fetched.title, "Buy milk")
        self.assertFalse(fetched.is_completed)

        fetched.is_completed = True
        self.assertTrue(self.repo.update_task(fetched))

        updated = self.repo.get_task(task_id)
        self.assertTrue(updated.is_completed)

        self.assertTrue(self.repo.delete_task(task_id))
        self.assertIsNone(self.repo.get_task(task_id))

    def test_search_notes(self):
        """Tests live searching by title and content."""
        self.repo.create_note(Note(title="Quantum Physics", content="Entanglement and superposition"))
        self.repo.create_note(Note(title="Cooking Recipe", content="Pasta and olive oil"))

        results = self.repo.list_notes(search_query="quantum")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Quantum Physics")

        results2 = self.repo.list_notes(search_query="olive oil")
        self.assertEqual(len(results2), 1)
        self.assertEqual(results2[0].title, "Cooking Recipe")


if __name__ == "__main__":
    unittest.main()

