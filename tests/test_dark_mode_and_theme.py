"""Tests for Dark Mode coverage, centralized theme manager, dialogs, and persistence."""

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QLabel

from mindspace.database.connection import DatabaseConnection
from mindspace.database.repository import MindspaceRepository
from mindspace.models.category import Category
from mindspace.models.note import Note
from mindspace.models.task import Task
from mindspace.services.category_service import CategoryService
from mindspace.services.note_service import NoteService
from mindspace.services.settings_service import SettingsService
from mindspace.services.task_service import TaskService
from mindspace.ui.dialogs.about_dialog import AboutDialog
from mindspace.ui.dialogs.category_dialog import CategoryDialog
from mindspace.ui.dialogs.confirm_dialog import ConfirmDialog
from mindspace.ui.dialogs.task_dialog import TaskDialog
from mindspace.ui.main_window import MainWindow
from mindspace.ui.themes.theme_manager import ThemeManager
from mindspace.utils.markdown_utils import markdown_to_html


class TestDarkModeAndTheme(unittest.TestCase):
    """Verifies complete Dark Mode support, style centralization, and live switching."""

    @classmethod
    def setUpClass(cls):
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
        cls.app = QApplication.instance() or QApplication([])
        font_family = ".AppleSystemUIFont" if sys.platform == "darwin" else "Segoe UI"
        cls.app.setFont(QFont(font_family, 10))

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_path = Path(self.test_dir) / "test_theme.db"
        self.db = DatabaseConnection(self.db_path)
        self.repo = MindspaceRepository(self.db)
        self.note_service = NoteService(self.repo)
        self.task_service = TaskService(self.repo)
        self.category_service = CategoryService(self.repo)
        self.settings_service = SettingsService(self.repo)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_theme_manager_tokens_and_stylesheets(self):
        """Verifies ThemeManager loads both light and dark QSS and tokens."""
        tm = ThemeManager.instance()
        tm.apply_theme("light")
        self.assertEqual(tm.current_theme, "light")
        self.assertFalse(tm.is_dark)
        self.assertEqual(tm.get_color("background"), "#F7F8F4")
        self.assertEqual(tm.get_color("surface"), "#FFFFFF")
        self.assertEqual(tm.get_color("swatch_border"), "#15370D")
        self.assertEqual(tm.get_color("accent"), "#15370D")
        self.assertEqual(tm.get_color("secondary_accent"), "#F1A344")

        tm.apply_theme("dark")
        self.assertEqual(tm.current_theme, "dark")
        self.assertTrue(tm.is_dark)
        self.assertEqual(tm.get_color("background"), "#11170F")
        self.assertEqual(tm.get_color("surface"), "#202B1D")
        self.assertEqual(tm.get_color("swatch_border"), "#FFFFFF")
        self.assertEqual(tm.get_color("accent"), "#97D7FF")
        self.assertEqual(tm.get_color("secondary_accent"), "#F1A344")
        self.assertEqual(tm.get_color("green_accent"), "#6C9B59")

        # Verify QSS contains critical selectors in dark mode
        dark_qss = tm._cache.get("dark", "")
        self.assertIn("QDialog", dark_qss)
        self.assertIn("QCalendarWidget", dark_qss)
        self.assertIn("QMenu", dark_qss)
        self.assertIn("QToolTip", dark_qss)
        self.assertIn("QPushButton.primaryBtn", dark_qss)
        self.assertIn("QLabel.dialogTitle", dark_qss)
        self.assertIn("QLabel.prioBadgeHigh", dark_qss)
        self.assertIn("QLineEdit[hasError=\"true\"]", dark_qss)

    def test_markdown_dark_mode_rendering(self):
        """Verifies markdown renderer outputs dark mode styles."""
        md = "# Heading\nThis is **bold** text and `inline code`.\n- [ ] Todo item\n- [x] Done item"
        light_html = markdown_to_html(md, theme="light")
        dark_html = markdown_to_html(md, theme="dark")

        self.assertIn("#202B1D", dark_html)
        self.assertIn("#F2F5ED", dark_html)
        self.assertIn("#FFFFFF", light_html)

    def test_dialogs_dark_mode_instantiation_and_classes(self):
        """Verifies dialogs instantiate and apply classes without inline overriding."""
        ThemeManager.instance().apply_theme("dark")

        # TaskDialog
        dlg_task = TaskDialog(parent=None)
        self.assertIn("dialogTitle", dlg_task.findChild(QLabel).property("class"))
        dlg_task._on_save()
        self.assertTrue(dlg_task.title_input.property("hasError"))
        dlg_task.title_input.setText("Testing task")
        self.assertFalse(dlg_task.title_input.property("hasError"))
        dlg_task.close()

        # CategoryDialog
        dlg_cat = CategoryDialog(parent=None)
        self.assertEqual(len(dlg_cat.color_buttons), 10)
        # Select another color and ensure swatch styles update
        dlg_cat._select_color("#F1A344")
        self.assertEqual(dlg_cat.selected_color, "#F1A344")
        dlg_cat.close()

        # ConfirmDialog
        dlg_confirm = ConfirmDialog(title="Delete Note", message="Are you sure?", parent=None)
        self.assertEqual(dlg_confirm.windowTitle(), "Delete Note")
        dlg_confirm.close()

        # AboutDialog
        dlg_about = AboutDialog(parent=None)
        self.assertEqual(dlg_about.windowTitle(), "About MINDSPACE")
        dlg_about.close()

    def test_main_window_live_theme_toggle_and_persistence(self):
        """Verifies theme toggle updates settings, UI elements, and restores on restart."""
        # Initial state light
        self.settings_service.set_theme("light")
        win = MainWindow(db_conn=self.db)
        win.show()

        tm = ThemeManager.instance()
        self.assertEqual(tm.current_theme, "light")

        # Toggle to dark
        win._on_toggle_theme()
        self.assertEqual(tm.current_theme, "dark")
        self.assertEqual(self.settings_service.get_settings().theme, "dark")
        self.assertEqual(win.settings_view.theme_combo.currentIndex(), 1)

        # Toggle back to light
        win._on_toggle_theme()
        self.assertEqual(tm.current_theme, "light")
        self.assertEqual(self.settings_service.get_settings().theme, "light")
        self.assertEqual(win.settings_view.theme_combo.currentIndex(), 0)

        # Switch to dark via settings combo
        win.settings_view.theme_combo.setCurrentIndex(1)
        self.assertEqual(tm.current_theme, "dark")
        self.assertEqual(self.settings_service.get_settings().theme, "dark")

        win.close()

        # Reopen window to verify persistence from database
        win2 = MainWindow(db_conn=self.db)
        win2.show()
        self.assertEqual(tm.current_theme, "dark")
        self.assertEqual(win2.settings_view.theme_combo.currentIndex(), 1)
        win2.close()

    def test_brand_palette_integrity_and_no_purple(self):
        """Verifies no purple hex colors remain and brand palette tokens are strictly enforced."""
        tm = ThemeManager.instance()

        # 1. Light Mode Brand Tokens
        tm.apply_theme("light")
        self.assertEqual(tm.get_color("background"), "#F7F8F4")
        self.assertEqual(tm.get_color("sidebar"), "#F0F2EB")
        self.assertEqual(tm.get_color("surface"), "#FFFFFF")
        self.assertEqual(tm.get_color("text"), "#20251E")
        self.assertEqual(tm.get_color("text_secondary"), "#777E73")
        self.assertEqual(tm.get_color("accent"), "#15370D")
        self.assertEqual(tm.get_color("secondary_accent"), "#F1A344")
        self.assertEqual(tm.get_color("soft_accent"), "#97D7FF")
        self.assertEqual(tm.get_color("border"), "#E4E8DF")

        # 2. Dark Mode Brand Tokens
        tm.apply_theme("dark")
        self.assertEqual(tm.get_color("background"), "#11170F")
        self.assertEqual(tm.get_color("sidebar"), "#182116")
        self.assertEqual(tm.get_color("surface"), "#202B1D")
        self.assertEqual(tm.get_color("elevated"), "#293725")
        self.assertEqual(tm.get_color("text"), "#F2F5ED")
        self.assertEqual(tm.get_color("text_secondary"), "#A7B29F")
        self.assertEqual(tm.get_color("accent"), "#97D7FF")
        self.assertEqual(tm.get_color("secondary_accent"), "#F1A344")
        self.assertEqual(tm.get_color("green_accent"), "#6C9B59")
        self.assertEqual(tm.get_color("border"), "#354331")

        # 3. Check for absence of purple hex codes in stylesheets
        purple_hexes = [
            "#8B79D9", "#7865CD", "#6B56C7", "#9D8DE6",
            "#A899E8", "#5A45B5", "#6C5CE7", "#7059C8", "#BE4BDB"
        ]
        for theme_name in ("light", "dark"):
            qss = tm._cache.get(theme_name, "")
            for p in purple_hexes:
                self.assertNotIn(p.lower(), qss.lower(), f"Found old purple hex {p} in {theme_name}.qss")
