"""Smoke and UI integration tests for MINDSPACE PySide6 components."""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Run Qt offscreen without requiring a physical display
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from mindspace.database.connection import DatabaseConnection
from mindspace.ui.main_window import MainWindow
from mindspace.ui.themes.theme_manager import ThemeManager


class TestUISmoke(unittest.TestCase):
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
        self.db_path = Path(self.temp_dir.name) / "test_ui.db"
        self.conn = DatabaseConnection(str(self.db_path))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_main_window_instantiation_and_views(self):
        """Verifies MainWindow, all views, and sidebar initialize without error."""
        window = MainWindow(db_conn=self.conn)
        self.assertIsNotNone(window)

        # Verify views exist in stack
        self.assertIsNotNone(window.notes_view)
        self.assertIsNotNone(window.editor_view)
        self.assertIsNotNone(window.quick_view)
        self.assertIsNotNone(window.tasks_view)
        self.assertIsNotNone(window.favorites_view)
        self.assertIsNotNone(window.archived_view)
        self.assertIsNotNone(window.settings_view)

        # Test view transitions
        window._on_navigation_changed("quick")
        self.assertEqual(window.view_stack.currentWidget(), window.quick_view)

        window._on_navigation_changed("tasks")
        self.assertEqual(window.view_stack.currentWidget(), window.tasks_view)

        window._on_navigation_changed("settings")
        self.assertEqual(window.view_stack.currentWidget(), window.settings_view)

        window._on_navigation_changed("notes")
        self.assertEqual(window.view_stack.currentWidget(), window.notes_view)

        # Test new note creation
        window._create_new_note()
        self.assertEqual(window.view_stack.currentWidget(), window.editor_view)
        self.assertIsNotNone(window.editor_view.current_note)

        # Test theme toggle
        initial_theme = ThemeManager.instance().current_theme
        window._on_toggle_theme()
        toggled_theme = ThemeManager.instance().current_theme
        self.assertNotEqual(initial_theme, toggled_theme)

        window.close()


if __name__ == "__main__":
    unittest.main()

