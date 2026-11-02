"""End-to-End integration test simulating user workflows in MINDSPACE."""

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
from mindspace.ui.main_window import MainWindow
from mindspace.ui.themes.theme_manager import ThemeManager


class TestEndToEndWorkflow(unittest.TestCase):
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
        self.db_path = Path(self.temp_dir.name) / "e2e_mindspace.db"
        self.conn = DatabaseConnection(str(self.db_path))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_complete_user_flow(self):
        # 1. Initialize MainWindow
        window = MainWindow(db_conn=self.conn)
        self.assertIsNotNone(window)

        # 2. Verify Initial Seed Data
        notes = window.note_service.list_notes()
        self.assertGreaterEqual(len(notes), 1)
        self.assertIn("Welcome to MINDSPACE", notes[0].title)

        tasks = window.task_service.list_tasks()
        self.assertGreaterEqual(len(tasks), 1)

        categories = window.category_service.list_categories()
        self.assertGreaterEqual(len(categories), 4)

        # 3. Create Note via UI Action
        window._create_new_note()
        self.assertEqual(window.view_stack.currentWidget(), window.editor_view)
        active_note = window.editor_view.current_note
        self.assertIsNotNone(active_note)

        # Edit note in editor
        window.editor_view.title_input.setText("Q4 Architecture Plan")
        window.editor_view.editor_content.setPlainText(
            "# Architecture\n\n- [ ] Database migration\n- [x] PySide6 UI\n- [ ] Deploy"
        )
        window.editor_view.save_immediately()

        # Check that note is saved in DB
        reloaded = window.note_service.get_note(active_note.id)
        self.assertEqual(reloaded.title, "Q4 Architecture Plan")
        self.assertIn("PySide6 UI", reloaded.content)

        # Test Markdown Preview toggle
        window.editor_view._on_preview_toggled(True)
        self.assertEqual(window.editor_view._mode, "preview")
        self.assertFalse(window.editor_view.preview_browser.isHidden())
        self.assertIn("Architecture", window.editor_view.preview_browser.toHtml())
        window.editor_view._on_preview_toggled(False)
        self.assertEqual(window.editor_view._mode, "write")
        self.assertFalse(window.editor_view.editor_content.isHidden())

        # Pin and Favorite
        window.editor_view._toggle_pin()
        window.editor_view._toggle_favorite()
        self.assertTrue(window.editor_view.current_note.is_pinned)
        self.assertTrue(window.editor_view.current_note.is_favorite)

        # Go back to notes view
        window.editor_view.back_requested.emit()
        self.assertEqual(window.view_stack.currentWidget(), window.notes_view)

        # 4. Test Favorites View
        window._on_navigation_changed("favorites")
        self.assertEqual(window.view_stack.currentWidget(), window.favorites_view)
        fav_notes = window.note_service.list_notes(is_favorite=True)
        self.assertTrue(any(n.title == "Q4 Architecture Plan" for n in fav_notes))

        # 5. Quick Notes Flow
        window._on_navigation_changed("quick")
        self.assertEqual(window.view_stack.currentWidget(), window.quick_view)
        window.quick_view.input_box.setPlainText("Call John regarding API specs at 3pm")
        window.quick_view._on_capture()

        quick_notes = window.note_service.list_notes(is_quick=True)
        self.assertTrue(any("Call John" in n.content for n in quick_notes))

        # Convert quick note to regular note
        target_quick = [n for n in quick_notes if "Call John" in n.content][0]
        window.quick_view._convert_to_full(target_quick.id)
        self.assertEqual(window.view_stack.currentWidget(), window.editor_view)
        self.assertFalse(window.editor_view.current_note.is_quick)

        # 6. Tasks Flow
        window._on_navigation_changed("tasks")
        self.assertEqual(window.view_stack.currentWidget(), window.tasks_view)

        initial_pending = window.task_service.count_pending()
        window.tasks_view.quick_input.setText("Write unit tests for UI views")
        window.tasks_view._on_quick_add()

        self.assertEqual(window.task_service.count_pending(), initial_pending + 1)

        # Find created task and toggle complete
        created_task = [t for t in window.task_service.list_tasks() if "Write unit tests" in t.title][0]
        window.tasks_view._on_toggle_status(created_task.id)
        self.assertEqual(window.task_service.count_pending(), initial_pending)

        # 7. Category Management
        new_cat = window.category_service.create_category(name="Mobile App", color="#0984E3")
        self.assertIsNotNone(new_cat.id)
        window._refresh_categories()

        # 8. Theme Switcher
        ThemeManager.instance().apply_theme("dark")
        self.assertTrue(ThemeManager.instance().is_dark)
        ThemeManager.instance().apply_theme("light")
        self.assertFalse(ThemeManager.instance().is_dark)

        # 9. Search Flow
        window._on_navigation_changed("notes")
        window.notes_view._on_search("Architecture")
        self.assertEqual(len(window.notes_view._cards), 1)

        window.notes_view._on_search("")
        self.assertGreaterEqual(len(window.notes_view._cards), 2)

        # 10. Clean close
        window.close()


if __name__ == "__main__":
    unittest.main()

