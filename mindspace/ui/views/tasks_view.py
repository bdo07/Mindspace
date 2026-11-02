"""Tasks view with interactive checklist, modal creation, and separated status sections."""

from typing import Dict, List, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from mindspace.models.category import Category
from mindspace.models.task import Task
from mindspace.services.category_service import CategoryService
from mindspace.services.task_service import TaskService
from mindspace.ui.assets.icons import get_icon, render_svg_pixmap
from mindspace.ui.components.task_item import TaskItem
from mindspace.ui.dialogs.confirm_dialog import ConfirmDialog
from mindspace.ui.dialogs.task_dialog import TaskDialog
from mindspace.ui.themes.theme_manager import ThemeManager


class TasksView(QWidget):
    """View managing tasks with proper modal dialogs, status separation, and progress tracking."""

    counts_changed = Signal()

    def __init__(
        self,
        task_service: TaskService,
        category_service: CategoryService,
        parent=None,
    ):
        super().__init__(parent)
        self.task_service = task_service
        self.category_service = category_service
        self.current_filter: Optional[bool] = None  # None = All, False = Pending, True = Completed

        self._task_items: List[TaskItem] = []

        self._setup_ui()
        self._update_icons()
        ThemeManager.instance().theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self, theme_name: str = ""):
        try:
            self._update_icons()
            self.refresh()
        except RuntimeError:
            pass

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(14)

        # 1. Header (Title, Subtitle, + Add Task Button)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        title = QLabel("Tasks", self)
        title.setObjectName("pageTitle")
        title_col.addWidget(title)

        self.subtitle = QLabel("Organize your daily priorities and actions.", self)
        self.subtitle.setObjectName("pageSubtitle")
        title_col.addWidget(self.subtitle)

        header_layout.addLayout(title_col, 1)

        self.new_task_btn = QPushButton("Add Task", self)
        self.new_task_btn.setProperty("class", "primaryBtn")
        self.new_task_btn.setFixedHeight(34)
        self.new_task_btn.setCursor(Qt.PointingHandCursor)
        self.new_task_btn.clicked.connect(self._open_new_task_dialog)
        header_layout.addWidget(self.new_task_btn)

        main_layout.addLayout(header_layout)

        # 2. Quick Add Bar
        add_bar = QFrame(self)
        add_bar.setObjectName("quickAddBar")
        add_bar_layout = QHBoxLayout(add_bar)
        add_bar_layout.setContentsMargins(10, 6, 10, 6)
        add_bar_layout.setSpacing(8)

        self.quick_input = QLineEdit(add_bar)
        self.quick_input.setProperty("class", "standardInput")
        self.quick_input.setPlaceholderText("Quick add task title... (Press Enter)")
        self.quick_input.returnPressed.connect(self._on_quick_add)
        add_bar_layout.addWidget(self.quick_input, 1)

        self.cat_select = QComboBox(add_bar)
        self.cat_select.setProperty("class", "standardInput")
        self.cat_select.setFixedHeight(34)
        self.cat_select.setMinimumWidth(120)
        add_bar_layout.addWidget(self.cat_select)

        self.quick_add_btn = QPushButton("Add", add_bar)
        self.quick_add_btn.setProperty("class", "secondaryBtn")
        self.quick_add_btn.setFixedHeight(34)
        self.quick_add_btn.setCursor(Qt.PointingHandCursor)
        self.quick_add_btn.clicked.connect(self._on_quick_add)
        add_bar_layout.addWidget(self.quick_add_btn)

        main_layout.addWidget(add_bar)

        # 3. Filter Segmented Tabs & Progress Stats
        filter_row = QHBoxLayout()
        filter_row.setSpacing(10)

        tab_container = QFrame(self)
        tab_container.setStyleSheet("background-color: transparent;")
        tab_layout = QHBoxLayout(tab_container)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(4)

        self.tab_all = QPushButton("All", tab_container)
        self.tab_all.setProperty("class", "segmentedTab")
        self.tab_all.setCursor(Qt.PointingHandCursor)
        self.tab_all.clicked.connect(lambda: self._set_filter(None))
        tab_layout.addWidget(self.tab_all)

        self.tab_pending = QPushButton("Pending", tab_container)
        self.tab_pending.setProperty("class", "segmentedTab")
        self.tab_pending.setCursor(Qt.PointingHandCursor)
        self.tab_pending.clicked.connect(lambda: self._set_filter(False))
        tab_layout.addWidget(self.tab_pending)

        self.tab_completed = QPushButton("Completed", tab_container)
        self.tab_completed.setProperty("class", "segmentedTab")
        self.tab_completed.setCursor(Qt.PointingHandCursor)
        self.tab_completed.clicked.connect(lambda: self._set_filter(True))
        tab_layout.addWidget(self.tab_completed)

        filter_row.addWidget(tab_container)
        filter_row.addStretch()

        self.progress_lbl = QLabel("0/0 completed (0%)", self)
        self.progress_lbl.setStyleSheet("font-size: 11px; font-weight: 600; color: #8E8E93;")
        filter_row.addWidget(self.progress_lbl)

        main_layout.addLayout(filter_row)

        # 4. Scroll Area for task items
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.tasks_container = QWidget()
        self.tasks_container.setStyleSheet("background: transparent;")
        self.tasks_layout = QVBoxLayout(self.tasks_container)
        self.tasks_layout.setContentsMargins(0, 2, 0, 16)
        self.tasks_layout.setSpacing(8)
        self.tasks_layout.addStretch()

        self.scroll_area.setWidget(self.tasks_container)
        main_layout.addWidget(self.scroll_area, 1)

        # 5. Empty State
        self.empty_state = QWidget(self)
        empty_layout = QVBoxLayout(self.empty_state)
        empty_layout.setAlignment(Qt.AlignCenter)
        empty_layout.setSpacing(8)

        self.empty_icon = QLabel(self.empty_state)
        self.empty_icon.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(self.empty_icon)

        empty_title = QLabel("No tasks here", self.empty_state)
        empty_title.setProperty("class", "emptyStateTitle")
        empty_title.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(empty_title)

        empty_desc = QLabel("You're all caught up! Add a new task to stay organized.", self.empty_state)
        empty_desc.setProperty("class", "emptyStateText")
        empty_desc.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(empty_desc)

        self.empty_btn = QPushButton("Create Task", self.empty_state)
        self.empty_btn.setProperty("class", "primaryBtn")
        self.empty_btn.setFixedHeight(34)
        self.empty_btn.setCursor(Qt.PointingHandCursor)
        self.empty_btn.clicked.connect(self._open_new_task_dialog)
        empty_layout.addWidget(self.empty_btn, 0, Qt.AlignCenter)

        self.empty_state.setVisible(False)
        main_layout.addWidget(self.empty_state, 1)

    def _set_filter(self, is_completed: Optional[bool]):
        self.current_filter = is_completed
        self.refresh()

    def _update_tab_styles(self):
        for btn, val in [(self.tab_all, None), (self.tab_pending, False), (self.tab_completed, True)]:
            is_active = (self.current_filter == val)
            btn.setProperty("active", "true" if is_active else "false")
            btn.style().polish(btn)

    def _open_new_task_dialog(self):
        """Opens modal task creation dialog with full validation."""
        categories = self.category_service.list_categories()
        dlg = TaskDialog(task=None, categories=categories, parent=self)
        if dlg.exec():
            data = dlg.get_data()
            self.task_service.create_task(
                title=data["title"],
                description=data["description"],
                due_date=data["due_date"],
                priority=data["priority"],
                category_id=data["category_id"],
            )
            self.refresh()
            self.counts_changed.emit()

    def refresh(self):
        self._update_tab_styles()
        self._populate_categories()

        # Clear existing items
        for item in self._task_items:
            self.tasks_layout.removeWidget(item)
            item.deleteLater()
        self._task_items.clear()

        while self.tasks_layout.count():
            widget_item = self.tasks_layout.takeAt(0)
            if widget_item.widget():
                widget_item.widget().deleteLater()

        # Fetch all tasks for progress computation
        all_tasks = self.task_service.list_tasks()
        total_count = len(all_tasks)
        completed_count = sum(1 for t in all_tasks if t.is_completed)
        pending_count = total_count - completed_count

        pct = int((completed_count / total_count * 100)) if total_count > 0 else 0
        self.progress_lbl.setText(f"{completed_count}/{total_count} completed ({pct}%)")

        # Determine visible tasks based on filter
        pending_tasks = [t for t in all_tasks if not t.is_completed]
        done_tasks = [t for t in all_tasks if t.is_completed]

        if self.current_filter is False:
            display_pending = pending_tasks
            display_done = []
        elif self.current_filter is True:
            display_pending = []
            display_done = done_tasks
        else:
            display_pending = pending_tasks
            display_done = done_tasks

        has_any = bool(display_pending or display_done)

        if not has_any:
            self.scroll_area.setVisible(False)
            self.empty_state.setVisible(True)
            return

        self.scroll_area.setVisible(True)
        self.empty_state.setVisible(False)

        # Section: Pending Tasks
        if display_pending:
            if self.current_filter is None:
                pending_header = QLabel(f"PENDING ({len(display_pending)})", self.tasks_container)
                pending_header.setProperty("class", "sectionHeader")
                self.tasks_layout.addWidget(pending_header)

            for task in display_pending:
                item = TaskItem(task, self.tasks_container)
                item.status_toggled.connect(self._on_toggle_status)
                item.edit_requested.connect(self._on_edit_task)
                item.delete_requested.connect(self._on_delete_task)
                self.tasks_layout.addWidget(item)
                self._task_items.append(item)

        # Section: Completed Tasks
        if display_done:
            if self.current_filter is None:
                completed_header = QLabel(f"COMPLETED ({len(display_done)})", self.tasks_container)
                completed_header.setProperty("class", "sectionHeader")
                self.tasks_layout.addWidget(completed_header)

            for task in display_done:
                item = TaskItem(task, self.tasks_container)
                item.status_toggled.connect(self._on_toggle_status)
                item.edit_requested.connect(self._on_edit_task)
                item.delete_requested.connect(self._on_delete_task)
                self.tasks_layout.addWidget(item)
                self._task_items.append(item)

        self.tasks_layout.addStretch()

    def _populate_categories(self):
        current_data = self.cat_select.currentData()
        self.cat_select.blockSignals(True)
        self.cat_select.clear()
        self.cat_select.addItem("No Category", userData=None)
        for cat in self.category_service.list_categories():
            self.cat_select.addItem(cat.name, userData=cat.id)
        for i in range(self.cat_select.count()):
            if self.cat_select.itemData(i) == current_data:
                self.cat_select.setCurrentIndex(i)
                break
        self.cat_select.blockSignals(False)

    def _on_quick_add(self):
        title = self.quick_input.text().strip()
        if not title:
            # If user clicked Add without typing, open full creation dialog!
            self._open_new_task_dialog()
            return

        cat_id = self.cat_select.currentData()
        self.task_service.create_task(title=title, category_id=cat_id)
        self.quick_input.clear()
        self.refresh()
        self.counts_changed.emit()

    def _on_toggle_status(self, task_id: int):
        self.task_service.toggle_completed(task_id)
        self.refresh()
        self.counts_changed.emit()

    def _on_edit_task(self, task_id: int):
        task = self.task_service.get_task(task_id)
        if not task:
            return
        categories = self.category_service.list_categories()
        dlg = TaskDialog(task=task, categories=categories, parent=self)
        if dlg.exec():
            data = dlg.get_data()
            self.task_service.update_task(
                task_id=task_id,
                title=data["title"],
                description=data["description"],
                due_date=data["due_date"],
                priority=data["priority"],
                category_id=data["category_id"],
            )
            self.refresh()
            self.counts_changed.emit()

    def _on_delete_task(self, task_id: int):
        confirmed = ConfirmDialog.ask(
            self,
            title="Delete Task",
            message="Are you sure you want to delete this task? This action cannot be undone.",
            confirm_label="Delete",
            is_danger=True,
        )
        if confirmed:
            self.task_service.delete_task(task_id)
            self.refresh()
            self.counts_changed.emit()

    def _update_icons(self):
        try:
            theme = ThemeManager.instance()
            self.new_task_btn.setIcon(get_icon("plus", color="#FFFFFF", size=14))
            self.empty_btn.setIcon(get_icon("plus", color="#FFFFFF", size=14))
            self.empty_icon.setPixmap(render_svg_pixmap("tasks", color=theme.get_color("accent"), size=44))
        except RuntimeError:
            pass
