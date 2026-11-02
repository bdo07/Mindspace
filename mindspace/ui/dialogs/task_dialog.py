"""Dialog for creating and editing tasks with input validation."""

import sys
from datetime import date
from pathlib import Path
from typing import List, Optional

# Ensure project root is on sys.path if run standalone
_project_root = str(Path(__file__).resolve().parent.parent.parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

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


class TaskDialog(QDialog):
    """Dialog to create or edit task details with strict validation."""

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
        self.setFixedSize(440, 420)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)

        # Header Title
        title_lbl = QLabel("Edit Task" if is_edit else "Create New Task", self)
        title_lbl.setProperty("class", "dialogTitle")
        layout.addWidget(title_lbl)

        # Validation error label (hidden by default)
        self.error_label = QLabel("", self)
        self.error_label.setProperty("class", "dialogError")
        self.error_label.setVisible(False)
        layout.addWidget(self.error_label)

        # Title input
        title_tag = QLabel("Title *", self)
        title_tag.setProperty("class", "inputLabel")
        layout.addWidget(title_tag)

        self.title_input = QLineEdit(self)
        self.title_input.setProperty("class", "standardInput")
        self.title_input.setPlaceholderText("What needs to be done?")
        self.title_input.textChanged.connect(self._clear_error)
        if task:
            self.title_input.setText(task.title)
        layout.addWidget(self.title_input)

        # Description input
        desc_tag = QLabel("Description (Optional)", self)
        desc_tag.setProperty("class", "inputLabel")
        layout.addWidget(desc_tag)

        self.desc_input = QTextEdit(self)
        self.desc_input.setProperty("class", "standardInput")
        self.desc_input.setPlaceholderText("Add notes, checklist, or details...")
        self.desc_input.setMaximumHeight(70)
        if task:
            self.desc_input.setText(task.description)
        layout.addWidget(self.desc_input)

        # Row: Due Date & Priority
        row1 = QHBoxLayout()
        row1.setSpacing(12)

        # Due Date
        due_col = QVBoxLayout()
        due_col.setSpacing(4)
        due_lbl = QLabel("Due Date", self)
        due_lbl.setProperty("class", "inputLabel")
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
        prio_lbl.setProperty("class", "inputLabel")
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
        cat_lbl.setProperty("class", "inputLabel")
        cat_col.addWidget(cat_lbl)

        self.cat_combo = QComboBox(self)
        self.cat_combo.setProperty("class", "standardInput")
        self.cat_combo.addItem("No Category", userData=None)
        for cat in self.categories:
            self.cat_combo.addItem(cat.name, userData=cat.id)

        cat_col.addWidget(self.cat_combo)
        layout.addLayout(cat_col)

        # Initialize existing values if editing
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

    def _clear_error(self):
        self.error_label.setVisible(False)
        self.title_input.setProperty("hasError", False)
        self.title_input.style().unpolish(self.title_input)
        self.title_input.style().polish(self.title_input)

    def _on_due_toggle(self, checked: bool):
        self.due_date_edit.setEnabled(checked)
        self.has_due_date.setText("Remove" if checked else "Set Date")
        self.has_due_date.setProperty("active", "true" if checked else "false")
        self.has_due_date.style().unpolish(self.has_due_date)
        self.has_due_date.style().polish(self.has_due_date)

    def _on_save(self):
        title = self.title_input.text().strip()
        if not title:
            self.error_label.setText("Please enter a task title.")
            self.error_label.setVisible(True)
            self.title_input.setProperty("hasError", True)
            self.title_input.style().unpolish(self.title_input)
            self.title_input.style().polish(self.title_input)
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
