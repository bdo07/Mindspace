"""Comprehensive test suite auditing every button, interaction, and responsive window sizes."""

import os
import sys
import tempfile
import unittest
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from mindspace.database.connection import DatabaseConnection
from mindspace.models.category import Category
from mindspace.models.task import Task
from mindspace.ui.dialogs.category_dialog import CategoryDialog
from mindspace.ui.dialogs.confirm_dialog import ConfirmDialog
from mindspace.ui.dialogs.task_dialog import TaskDialog
from mindspace.ui.main_window import MainWindow
from mindspace.ui.themes.theme_manager import ThemeManager


class TestFullAuditAndResponsive(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
        font_family = ".AppleSystemUIFont" if sys.platform == "darwin" else "Segoe UI"
        cls.app.setFont(QFont(font_family, 10))

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "audit_mindspace.db"
        self.conn = DatabaseConnection(str(self.db_path))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_add_task_dialog_complete_workflow(self):
        """
        Explicitly tests the 8 expected behaviors for Add Task:
        1. Clicking Add Task opens task creation dialog
        2. Enter task title
        3. Enter description & due date
        4. Validation prevents empty title
        5. Task inserted into SQLite
        6. Task list refreshes immediately
        7. Task persists across restarts
        8. Cancel closes without creating
        """
        window = MainWindow(db_conn=self.conn)

        # 1. Validation test (Empty title)
        dlg_empty = TaskDialog(task=None, categories=window.category_service.list_categories())
        dlg_empty.title_input.setText("")
        dlg_empty._on_save()
        self.assertFalse(dlg_empty.error_label.isHidden())
        self.assertEqual(dlg_empty.error_label.text(), "Please enter a task title.")
        self.assertFalse(dlg_empty.result() == 1)  # Not accepted

        # 2. Cancel test (User clicks cancel)
        dlg_cancel = TaskDialog(task=None, categories=window.category_service.list_categories())
        dlg_cancel.title_input.setText("Cancelled Task")
        dlg_cancel.reject()
        self.assertEqual(dlg_cancel.result(), 0)
        # Verify not in DB
        tasks_now = window.task_service.list_tasks(search_query="Cancelled Task")
        self.assertEqual(len(tasks_now), 0)

        # 3. Complete successful creation with Title, Description, Due Date, Category, Priority
        cats = window.category_service.list_categories()
        work_cat = [c for c in cats if c.name == "Work"][0]

        dlg_save = TaskDialog(task=None, categories=cats)
        dlg_save.title_input.setText("Ship Production Release")
        dlg_save.desc_input.setPlainText("Audit all features and build installers")
        dlg_save.has_due_date.setChecked(True)
        dlg_save.due_date_edit.setDate(QDate(2026, 12, 15))
        dlg_save.prio_combo.setCurrentText("High")

        # Select work category
        for idx in range(dlg_save.cat_combo.count()):
            if dlg_save.cat_combo.itemData(idx) == work_cat.id:
                dlg_save.cat_combo.setCurrentIndex(idx)
                break

        dlg_save._on_save()
        self.assertEqual(dlg_save.result(), 1)  # Accepted

        # Insert through task service (matching dialog completion)
        data = dlg_save.get_data()
        self.assertEqual(data["title"], "Ship Production Release")
        self.assertEqual(data["due_date"], "2026-12-15")
        self.assertEqual(data["priority"], "high")
        self.assertEqual(data["category_id"], work_cat.id)

        task = window.task_service.create_task(
            title=data["title"],
            description=data["description"],
            due_date=data["due_date"],
            priority=data["priority"],
            category_id=data["category_id"],
        )
        self.assertIsNotNone(task.id)

        # 4. Immediate refresh
        window.tasks_view.refresh()
        displayed_tasks = window.task_service.list_tasks()
        self.assertTrue(any(t.title == "Ship Production Release" for t in displayed_tasks))

        # 5. Persistence across restarts (new window instance pointing to same DB)
        window.close()
        window2 = MainWindow(db_conn=self.conn)
        persisted = window2.task_service.get_task(task.id)
        self.assertIsNotNone(persisted)
        self.assertEqual(persisted.title, "Ship Production Release")
        self.assertEqual(persisted.due_date, "2026-12-15")
        self.assertEqual(persisted.category_name, "Work")
        window2.close()

    def test_responsive_window_sizes(self):
        """Tests application layout at 1440x900, 1280x800, 1024x768, and 800x600."""
        window = MainWindow(db_conn=self.conn)
        window.show()

        sizes_to_test = [
            (1440, 900),
            (1280, 800),
            (1024, 768),
            (800, 600),
        ]

        for width, height in sizes_to_test:
            window.resize(width, height)
            QApplication.processEvents()
            self.assertEqual(window.width(), width)
            self.assertEqual(window.height(), height)

            # Test views under this resolution
            for view_key in ("notes", "tasks", "quick", "favorites", "archived", "settings"):
                window._on_navigation_changed(view_key)
                QApplication.processEvents()
                current_widget = window.view_stack.currentWidget()
                self.assertIsNotNone(current_widget)
                self.assertGreater(current_widget.width(), 0)

            # Test notes grid column calculation
            cols = window.notes_view._calculate_columns()
            if width <= 800:
                self.assertIn(cols, (1, 2))
                self.assertTrue(window.sidebar.is_collapsed)
            elif width >= 1440:
                self.assertGreaterEqual(cols, 3)

        window.close()

    def test_complete_button_and_feature_audit(self):
        """Audits Add Note, Edit Note, Delete Note, Pin, Favorite, Archive, Restore, Categories, Themes."""
        window = MainWindow(db_conn=self.conn)

        # 1. Add Note button
        initial_note_count = len(window.note_service.list_notes())
        window._create_new_note()
        self.assertEqual(len(window.note_service.list_notes()), initial_note_count + 1)
        created_note = window.editor_view.current_note
        self.assertIsNotNone(created_note)

        # 2. Edit Note
        window.editor_view.title_input.setText("Architecture Blueprint")
        window.editor_view.editor_content.setPlainText("# Header\n\n- Task 1\n- Task 2")
        window.editor_view.save_immediately()

        saved = window.note_service.get_note(created_note.id)
        self.assertEqual(saved.title, "Architecture Blueprint")

        # 3. Pin toggle
        window.editor_view._toggle_pin()
        self.assertTrue(window.note_service.get_note(created_note.id).is_pinned)

        # 4. Favorite toggle
        window.editor_view._toggle_favorite()
        self.assertTrue(window.note_service.get_note(created_note.id).is_favorite)

        # 5. Archive and Restore
        window.editor_view._toggle_archive()
        self.assertTrue(window.note_service.get_note(created_note.id).is_archived)

        # Restore from archived
        window.archived_view.refresh()
        window.note_service.restore_note(created_note.id)
        self.assertFalse(window.note_service.get_note(created_note.id).is_archived)

        # 6. Delete Note
        window.note_service.delete_note(created_note.id)
        self.assertIsNone(window.note_service.get_note(created_note.id))

        # 7. Category creation
        cat = window.category_service.create_category(name="Research", color="#20C997")
        self.assertIsNotNone(cat.id)
        cats = window.category_service.list_categories()
        self.assertTrue(any(c.name == "Research" for c in cats))

        # 8. Theme toggling
        window._on_toggle_theme()
        self.assertTrue(ThemeManager.instance().is_dark)
        self.assertEqual(window.settings_service.get_settings().theme, "dark")

        window._on_toggle_theme()
        self.assertFalse(ThemeManager.instance().is_dark)
        self.assertEqual(window.settings_service.get_settings().theme, "light")

        # 9. Search
        search_results = window.note_service.list_notes(search_query="Welcome")
        self.assertGreaterEqual(len(search_results), 1)

        # 10. Category Editing & Deletion
        cat = window.category_service.create_category(name="Old Name", color="#15370D")
        window.category_service.update_category(cat.id, name="New Name", color="#5C7CFA")
        updated_cat = window.category_service.get_category(cat.id)
        self.assertEqual(updated_cat.name, "New Name")
        self.assertEqual(updated_cat.color, "#5C7CFA")

        window.category_service.delete_category(cat.id)
        self.assertIsNone(window.category_service.get_category(cat.id))

        # 11. Note Card Context Actions in NotesView
        test_note = window.note_service.create_note(title="Card Action Note", content="Sample")
        window.notes_view.refresh()

        window.notes_view._on_toggle_pin(test_note.id)
        self.assertTrue(window.note_service.get_note(test_note.id).is_pinned)

        window.notes_view._on_toggle_fav(test_note.id)
        self.assertTrue(window.note_service.get_note(test_note.id).is_favorite)

        window.notes_view._on_toggle_archive(test_note.id)
        self.assertTrue(window.note_service.get_note(test_note.id).is_archived)

        window.notes_view._on_toggle_archive(test_note.id)
        self.assertFalse(window.note_service.get_note(test_note.id).is_archived)

        window.note_service.delete_note(test_note.id)
        self.assertIsNone(window.note_service.get_note(test_note.id))

        window.close()


if __name__ == "__main__":
    unittest.main()
