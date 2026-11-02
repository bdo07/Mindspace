"""Task item card component with completion toggle, due date, and actions."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from mindspace.models.task import Task
from mindspace.ui.assets.icons import get_icon
from mindspace.ui.themes.theme_manager import ThemeManager
from mindspace.utils.date_utils import format_due_date


class TaskItem(QFrame):
    """Component representing a single task in the task list."""

    status_toggled = Signal(int)
    edit_requested = Signal(int)
    delete_requested = Signal(int)

    def __init__(self, task: Task, parent=None):
        super().__init__(parent)
        self.task = task
        self._setup_ui()
        self._update_icons()

    def _setup_ui(self):
        is_done = self.task.is_completed
        self.setProperty("class", "taskItemCompleted" if is_done else "taskItem")

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(12, 10, 12, 10)
        main_layout.setSpacing(12)

        # Checkbox Button (Custom circular check)
        self.check_btn = QPushButton(self)
        self.check_btn.setFixedSize(22, 22)
        self.check_btn.setCursor(Qt.PointingHandCursor)
        self._style_check_btn()
        self.check_btn.clicked.connect(self._on_check_clicked)
        main_layout.addWidget(self.check_btn)

        # Content: Title & optional description
        text_layout = QVBoxLayout()
        text_layout.setSpacing(3)

        self.title_label = QLabel(self.task.title, self)
        self.title_label.setProperty("class", "taskTitleCompleted" if is_done else "taskTitle")
        self.title_label.setWordWrap(True)
        text_layout.addWidget(self.title_label)

        if self.task.description:
            self.desc_label = QLabel(self.task.description, self)
            self.desc_label.setProperty("class", "cardPreview")
            self.desc_label.setWordWrap(True)
            text_layout.addWidget(self.desc_label)

        main_layout.addLayout(text_layout, 1)

        # Badges layout
        badge_layout = QHBoxLayout()
        badge_layout.setSpacing(8)

        # Due Date Badge
        if self.task.due_date and not is_done:
            due_text, due_status = format_due_date(self.task.due_date)
            self.due_badge = QLabel(due_text, self)
            self.due_badge.setProperty("class", f"dueBadge dueBadge_{due_status}")
            badge_layout.addWidget(self.due_badge)

        # Category Pill
        if self.task.category_name:
            color = self.task.category_color or "#8B79D9"
            self.cat_pill = QLabel(f" {self.task.category_name} ", self)
            self.cat_pill.setStyleSheet(f"""
                QLabel {{
                    background-color: {color}22;
                    color: {color};
                    border: 1px solid {color}55;
                    border-radius: 9px;
                    padding: 1px 6px;
                    font-size: 11px;
                    font-weight: 600;
                }}
            """)
            badge_layout.addWidget(self.cat_pill)

        main_layout.addLayout(badge_layout)

        # Action Buttons
        self.edit_btn = QPushButton(self)
        self.edit_btn.setProperty("class", "iconBtn")
        self.edit_btn.setFixedSize(26, 26)
        self.edit_btn.setToolTip("Edit task")
        self.edit_btn.setCursor(Qt.PointingHandCursor)
        self.edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.task.id))
        main_layout.addWidget(self.edit_btn)

        self.del_btn = QPushButton(self)
        self.del_btn.setProperty("class", "iconBtn")
        self.del_btn.setFixedSize(26, 26)
        self.del_btn.setToolTip("Delete task")
        self.del_btn.setCursor(Qt.PointingHandCursor)
        self.del_btn.clicked.connect(lambda: self.delete_requested.emit(self.task.id))
        main_layout.addWidget(self.del_btn)

    def _style_check_btn(self):
        theme = ThemeManager.instance()
        accent = theme.get_color("accent")
        border = theme.get_color("border")
        if self.task.is_completed:
            self.check_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {accent};
                    border: 1.5px solid {accent};
                    border-radius: 11px;
                }}
            """)
            self.check_btn.setIcon(get_icon("check", color="#FFFFFF", size=13))
        else:
            self.check_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: 1.5px solid {border};
                    border-radius: 11px;
                }}
                QPushButton:hover {{
                    border-color: {accent};
                }}
            """)
            self.check_btn.setIcon(get_icon("check", color="transparent", size=13))

    def _update_icons(self):
        theme = ThemeManager.instance()
        icon_color = theme.get_color("icon")
        self.edit_btn.setIcon(get_icon("edit", color=icon_color, size=14))
        self.del_btn.setIcon(get_icon("trash", color=icon_color, size=14))
        self._style_check_btn()

    def _on_check_clicked(self):
        if self.task.id:
            self.status_toggled.emit(self.task.id)
