"""Main application window for MINDSPACE — Your Personal Space."""

from typing import Optional
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QCloseEvent, QKeySequence, QResizeEvent, QShortcut
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QStackedWidget,
    QWidget,
)

from mindspace.database.connection import DatabaseConnection
from mindspace.database.repository import MindspaceRepository
from mindspace.services.backup_service import BackupService
from mindspace.services.category_service import CategoryService
from mindspace.services.note_service import NoteService
from mindspace.services.settings_service import SettingsService
from mindspace.services.task_service import TaskService
from mindspace.ui.components.sidebar import Sidebar
from mindspace.ui.components.toast import Toast
from mindspace.ui.dialogs.category_dialog import CategoryDialog
from mindspace.ui.themes.theme_manager import ThemeManager
from mindspace.ui.views.editor_view import EditorView
from mindspace.ui.views.notes_view import NotesView
from mindspace.ui.views.quick_notes_view import QuickNotesView
from mindspace.ui.views.settings_view import SettingsView
from mindspace.ui.views.tasks_view import TasksView


class MainWindow(QMainWindow):
    """Primary application window connecting all services, views, and navigation with responsive layout."""

    def __init__(self, db_conn: Optional[DatabaseConnection] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MINDSPACE — Your Personal Space")
        # Ensure application fits 800x600 and larger screens comfortably
        self.setMinimumSize(780, 520)

        # Initialize Data & Services Layer
        self.db = db_conn or DatabaseConnection()
        self.repo = MindspaceRepository(self.db)
        self.note_service = NoteService(self.repo)
        self.task_service = TaskService(self.repo)
        self.category_service = CategoryService(self.repo)
        self.settings_service = SettingsService(self.repo)
        self.backup_service = BackupService(self.db)

        self._user_manually_collapsed = False

        # Restore window geometry
        settings = self.settings_service.get_settings()
        self.resize(max(800, settings.window_width), max(600, settings.window_height))

        # Build UI
        self._setup_ui()
        self._setup_global_shortcuts()
        self._load_initial_state()

    def _setup_ui(self):
        central_widget = QWidget(self)
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)

        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. Left Sidebar with Collapse Support
        self.sidebar = Sidebar(self)
        self.sidebar.nav_changed.connect(self._on_navigation_changed)
        self.sidebar.add_category_clicked.connect(self._on_add_category)
        self.sidebar.theme_toggle_clicked.connect(self._on_toggle_theme)
        self.sidebar.collapse_toggled.connect(self._on_sidebar_collapse_toggled)
        root_layout.addWidget(self.sidebar)

        # 2. Main Content Area with View Stack
        self.view_stack = QStackedWidget(self)
        self.view_stack.setObjectName("mainContentArea")

        # Views
        self.notes_view = NotesView(self.note_service, self.category_service, view_mode="notes", parent=self)
        self.notes_view.note_selected.connect(self._open_note_in_editor)
        self.notes_view.new_note_requested.connect(self._create_new_note)
        self.notes_view.note_updated.connect(self._update_sidebar_counts)

        self.editor_view = EditorView(self.note_service, self.category_service, parent=self)
        self.editor_view.back_requested.connect(self._on_editor_back)
        self.editor_view.note_saved.connect(self._on_note_saved)
        self.editor_view.note_deleted.connect(self._on_note_deleted)

        self.quick_view = QuickNotesView(self.note_service, parent=self)
        self.quick_view.open_in_editor_requested.connect(self._open_note_in_editor)
        self.quick_view.counts_changed.connect(self._update_sidebar_counts)

        self.tasks_view = TasksView(self.task_service, self.category_service, parent=self)
        self.tasks_view.counts_changed.connect(self._update_sidebar_counts)

        self.favorites_view = NotesView(self.note_service, self.category_service, view_mode="favorites", parent=self)
        self.favorites_view.note_selected.connect(self._open_note_in_editor)
        self.favorites_view.new_note_requested.connect(self._create_new_note)
        self.favorites_view.note_updated.connect(self._update_sidebar_counts)

        self.archived_view = NotesView(self.note_service, self.category_service, view_mode="archived", parent=self)
        self.archived_view.note_selected.connect(self._open_note_in_editor)
        self.archived_view.note_updated.connect(self._update_sidebar_counts)

        self.settings_view = SettingsView(self.settings_service, self.backup_service, parent=self)
        self.settings_view.theme_changed_signal.connect(self._on_theme_changed_from_settings)
        self.settings_view.database_restored.connect(self._on_database_restored)

        self.category_notes_view = NotesView(self.note_service, self.category_service, view_mode="category", parent=self)
        self.category_notes_view.note_selected.connect(self._open_note_in_editor)
        self.category_notes_view.new_note_requested.connect(self._create_new_note)
        self.category_notes_view.note_updated.connect(self._update_sidebar_counts)

        # Add to stack in index order
        self.view_indices = {
            "notes": self.view_stack.addWidget(self.notes_view),
            "editor": self.view_stack.addWidget(self.editor_view),
            "quick": self.view_stack.addWidget(self.quick_view),
            "tasks": self.view_stack.addWidget(self.tasks_view),
            "favorites": self.view_stack.addWidget(self.favorites_view),
            "archived": self.view_stack.addWidget(self.archived_view),
            "settings": self.view_stack.addWidget(self.settings_view),
            "category": self.view_stack.addWidget(self.category_notes_view),
        }

        root_layout.addWidget(self.view_stack, 1)

        # 3. Toast Notifications Overlay
        self.toast = Toast(self)

    def _setup_global_shortcuts(self):
        # Ctrl/Cmd+N: Smart New (Note or Task depending on view)
        sc_new = QShortcut(QKeySequence.New, self)
        sc_new.activated.connect(self._on_shortcut_new)

        # Ctrl/Cmd+F: Search focus
        sc_search = QShortcut(QKeySequence.Find, self)
        sc_search.activated.connect(self._focus_search)

        # Ctrl/Cmd+Q: Quit
        sc_quit = QShortcut(QKeySequence.Quit, self)
        sc_quit.activated.connect(self.close)

    def _on_shortcut_new(self):
        current_w = self.view_stack.currentWidget()
        if current_w == self.tasks_view:
            self.tasks_view._open_new_task_dialog()
        else:
            self._create_new_note()

    def _load_initial_state(self):
        settings = self.settings_service.get_settings()
        ThemeManager.instance().apply_theme(settings.theme)

        # Refresh sidebar categories and badges
        self._refresh_categories()
        self._update_sidebar_counts()

        # Open default view
        target_view = settings.default_view or "notes"
        self._on_navigation_changed(target_view)

        # Check initial width for sidebar collapse
        if self.width() < 860:
            self.sidebar.set_collapsed(True)

    def _on_sidebar_collapse_toggled(self, collapsed: bool):
        self._user_manually_collapsed = collapsed

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        w = self.width()
        # Automatically collapse sidebar on compact windows if user hasn't explicitly expanded
        if w < 860 and not self.sidebar.is_collapsed:
            self.sidebar.set_collapsed(True)
        elif w >= 1020 and self.sidebar.is_collapsed and not self._user_manually_collapsed:
            self.sidebar.set_collapsed(False)

    def _on_navigation_changed(self, nav_key: str):
        self.sidebar.set_active(nav_key)

        if nav_key.startswith("category:"):
            cat_id = int(nav_key.split(":")[1])
            self.category_notes_view.category_id = cat_id
            self.category_notes_view.refresh()
            self.view_stack.setCurrentIndex(self.view_indices["category"])
        elif nav_key == "notes":
            self.notes_view.refresh()
            self.view_stack.setCurrentIndex(self.view_indices["notes"])
        elif nav_key == "quick":
            self.quick_view.refresh()
            self.view_stack.setCurrentIndex(self.view_indices["quick"])
        elif nav_key == "tasks":
            self.tasks_view.refresh()
            self.view_stack.setCurrentIndex(self.view_indices["tasks"])
        elif nav_key == "favorites":
            self.favorites_view.refresh()
            self.view_stack.setCurrentIndex(self.view_indices["favorites"])
        elif nav_key == "archived":
            self.archived_view.refresh()
            self.view_stack.setCurrentIndex(self.view_indices["archived"])
        elif nav_key == "settings":
            self.settings_view.refresh()
            self.view_stack.setCurrentIndex(self.view_indices["settings"])

    def _open_note_in_editor(self, note_id: int):
        self.editor_view.load_note(note_id)
        self.view_stack.setCurrentIndex(self.view_indices["editor"])

    def _create_new_note(self):
        category_id = None
        current_w = self.view_stack.currentWidget()
        if current_w == self.category_notes_view and self.category_notes_view.category_id:
            category_id = self.category_notes_view.category_id

        note = self.note_service.create_note(title="Untitled Note", content="", category_id=category_id)
        self._open_note_in_editor(note.id)
        self._update_sidebar_counts()
        self.toast.show_message("Created new note")

    def _on_editor_back(self):
        self._update_sidebar_counts()
        self._on_navigation_changed("notes")

    def _on_note_saved(self, note_id: int):
        self._update_sidebar_counts()

    def _on_note_deleted(self, note_id: int):
        self._update_sidebar_counts()
        self.toast.show_message("Note deleted")

    def _on_add_category(self):
        dlg = CategoryDialog(parent=self)
        if dlg.exec():
            name, color = dlg.get_data()
            try:
                self.category_service.create_category(name=name, color=color)
                self._refresh_categories()
                self.toast.show_message(f"Category '{name}' created")
            except Exception as e:
                self.toast.show_message(f"Error: {str(e)}", is_error=True)

    def _refresh_categories(self):
        categories = self.category_service.list_categories()
        counts = self.category_service.get_note_counts()
        self.sidebar.set_categories(categories, counts)

    def _update_sidebar_counts(self):
        counts = self.note_service.get_counts()
        counts["tasks"] = self.task_service.count_pending()
        self.sidebar.update_counts(counts)
        self._refresh_categories()

    def _on_toggle_theme(self):
        new_theme = ThemeManager.instance().toggle_theme()
        self.settings_service.set_theme(new_theme)
        self.toast.show_message(f"Switched to {new_theme.capitalize()} Mode")

    def _on_theme_changed_from_settings(self, theme_val: str):
        self.toast.show_message(f"Switched to {theme_val.capitalize()} Mode")

    def _on_database_restored(self):
        self._update_sidebar_counts()
        self.notes_view.refresh()
        self.tasks_view.refresh()
        self.toast.show_message("Database restored successfully!")

    def _focus_search(self):
        current_w = self.view_stack.currentWidget()
        if hasattr(current_w, "search_bar"):
            current_w.search_bar.set_focus()

    def closeEvent(self, event: QCloseEvent):
        # Persist window geometry
        self.settings_service.set_window_geometry(self.width(), self.height())
        if hasattr(self, "editor_view"):
            self.editor_view.save_immediately()
        super().closeEvent(event)
