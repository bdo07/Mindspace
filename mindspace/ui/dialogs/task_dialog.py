"""Dialog for creating and editing tasks."""

from datetime import date
from typing import List, Optional
from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from mindspace.models.category import Category
from mindspace.models.task import Task
from mindspace.ui.themes.theme_manager import ThemeManager


class TaskDialog(QDialog):
    """Dialog to create or edit task details."""

    def __init__(
        self,
        task: Optional[Task] = None,
        categories: Optional[List[Category]] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.task = task
        self.categories = categories or []
        is_edit = task is not None

        self.setWindowTitle("Edit Task" if is_edit else "New Task")
        self.setFixedSize(420, 380)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        theme = ThemeManager.instance()
        bg_color = theme.get_color("surface")
        text_color = theme.get_color("text")
        border_color = theme.get_color("border")

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 12px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        title_lbl = QLabel("Edit Task" if is_edit else "New Task", self)
        title_lbl.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {text_color};")
        layout.addWidget(title_lbl)

        # Title input
        self.title_input = QLineEdit(self)
        self.title_input.setProperty("class", "standardInput")
        self.title_input.setPlaceholderText("What needs to be done?")
        if task:
            self.title_input.setText(task.title)
        layout.addWidget(self.title_input)

        # Description input
        self.desc_input = QTextEdit(self)
        self.desc_input.setProperty("class", "standardInput")
        self.desc_input.setPlaceholderText("Add notes or details (optional)...")
        self.desc_input.setMaximumHeight(80)
        if task:
            self.desc_input.setText(task.description)
        layout.addWidget(self.desc_input)

        # Due Date & Priority row
        row1 = QHBoxLayout()
        row1.setSpacing(12)

        # Due Date
        due_col = QVBoxLayout()
        due_col.setSpacing(4)
        due_lbl = QLabel("Due Date", self)
        due_lbl.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {theme.get_color('text_secondary')};")
        due_col.addWidget(due_lbl)

        self.due_date_edit = QDateEdit(self)
        self.due_date_edit.setCalendarPopup(True)
        self.due_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.due_date_edit.setDate(QDate.currentDate())
        self.due_date_edit.setProperty("class", "standardInput")

        self.has_due_date = QPushButton("Set Date", self)
        self.has_due_date.setCheckable(True)
        self.has_due_date.setProperty("class", "secondaryBtn")
        self.has_due_date.setFixedHeight(30)
        self.has_due_date.toggled.connect(self._on_due_toggle)

        due_row = QHBoxLayout()
        due_row.addWidget(self.due_date_edit, 1)
        due_row.addWidget(self.has_due_date)
        due_col.addLayout(due_row)
        row1.addLayout(due_col)

        # Priority
        prio_col = QVBoxLayout()
        prio_col.setSpacing(4)
        prio_lbl = QLabel("Priority", self)
        prio_lbl.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {theme.get_color('text_secondary')};")
        prio_col.addWidget(prio_lbl)

        self.prio_combo = QComboBox(self)
        self.prio_combo.setProperty("class", "standardInput")
        self.prio_combo.addItems(["Low", "Normal", "High"])
        self.prio_combo.setCurrentText("Normal")
        prio_col.addWidget(self.prio_combo)
        row1.addLayout(prio_col)

        layout.addLayout(row1)

        # Category Row
        cat_col = QVBoxLayout()
        cat_col.setSpacing(4)
        cat_lbl = QLabel("Category", self)
        cat_lbl.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {theme.get_color('text_secondary')};")
        cat_col.addWidget(cat_lbl)

        self.cat_combo = QComboBox(self)
        self.cat_combo.setProperty("class", "standardInput")
        self.cat_combo.addItem("No Category", userData=None)
        for cat in self.categories:
            self.cat_combo.addItem(cat.name, userData=cat.id)

        cat_col.addWidget(self.cat_combo)
        layout.addLayout(cat_col)

        # Initialize values if editing
        if task:
            if task.due_date:
                try:
                    qdate = QDate.fromString(task.due_date, "yyyy-MM-dd")
                    if qdate.isValid():
                        self.due_date_edit.setDate(qdate)
                        self.has_due_date.setChecked(True)
                except Exception:
                    pass
            else:
                self.has_due_date.setChecked(False)
                self.due_date_edit.setEnabled(False)

            self.prio_combo.setCurrentText(task.priority.capitalize())

            if task.category_id:
                for idx in range(self.cat_combo.count()):
                    if self.cat_combo.itemData(idx) == task.category_id:
                        self.cat_combo.setCurrentIndex(idx)
                        break
        else:
            self.has_due_date.setChecked(False)
            self.due_date_edit.setEnabled(False)

        layout.addStretch()

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel", self)
        cancel_btn.setProperty("class", "secondaryBtn")
        cancel_btn.setFixedHeight(34)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save Task", self)
        save_btn.setProperty("class", "primaryBtn")
        save_btn.setFixedHeight(34)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _on_due_toggle(self, checked: bool):
        self.due_date_edit.setEnabled(checked)
        self.has_due_date.setText("Remove" if checked else "Set Date")

    def _on_save(self):
        if not self.title_input.text().strip():
            self.title_input.setFocus()
            return
        self.accept()

    def get_data(self) -> dict:
        due = self.due_date_edit.date().toString("yyyy-MM-dd") if self.has_due_date.isChecked() else None
        return {
            "title": self.title_input.text().strip(),
            "description": self.desc_input.toPlainText().strip(),
            "due_date": due,
            "priority": self.prio_combo.currentText().lower(),
            "category_id": self.cat_combo.currentData(),
        }

