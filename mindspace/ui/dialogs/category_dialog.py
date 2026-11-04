"""Dialog for creating and editing categories."""

import sys
from pathlib import Path
from typing import List, Optional

# Ensure project root is on sys.path if run standalone
_project_root = str(Path(__file__).resolve().parent.parent.parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from mindspace.models.category import Category
from mindspace.ui.themes.theme_manager import ThemeManager

PALETTE: List[str] = [
    "#15370D",  # Forest Green (Brand Primary)
    "#F1A344",  # Warm Amber (Brand Secondary)
    "#97D7FF",  # Soft Sky Blue (Brand Soft Accent)
    "#6C9B59",  # Green Accent / Sage
    "#2D6A4F",  # Deep Foliage Green
    "#D97706",  # Golden Ochre
    "#0284C7",  # Ocean Blue
    "#0D9488",  # Pine Teal
    "#E05252",  # Terracotta Red
    "#777E73",  # Olive Slate
]


class CategoryDialog(QDialog):
    """Dialog to create or edit category details with color swatches."""

    def __init__(self, category: Optional[Category] = None, parent=None):
        super().__init__(parent)
        self.category = category
        self.selected_color = category.color if category else PALETTE[0]

        is_edit = category is not None
        self.setWindowTitle("Edit Category" if is_edit else "New Category")
        self.setFixedSize(360, 270)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        # Title
        title_lbl = QLabel("Edit Category" if is_edit else "Create Category", self)
        title_lbl.setProperty("class", "dialogTitle")
        layout.addWidget(title_lbl)

        # Name input
        name_lbl = QLabel("Category Name *", self)
        name_lbl.setProperty("class", "inputLabel")
        layout.addWidget(name_lbl)

        self.name_input = QLineEdit(self)
        self.name_input.setProperty("class", "standardInput")
        self.name_input.setPlaceholderText("e.g. Work, Ideas, Research")
        self.name_input.textChanged.connect(self._clear_error)
        if category:
            self.name_input.setText(category.name)
        layout.addWidget(self.name_input)

        # Color picker
        color_lbl = QLabel("Accent Color", self)
        color_lbl.setProperty("class", "inputLabel")
        layout.addWidget(color_lbl)

        palette_layout = QGridLayout()
        palette_layout.setSpacing(8)
        self.color_buttons: List[QPushButton] = []

        for idx, color in enumerate(PALETTE):
            row = idx // 5
            col = idx % 5
            btn = QPushButton(self)
            btn.setFixedSize(26, 26)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setProperty("color_val", color)
            self._style_color_btn(btn, color, is_selected=(color.lower() == self.selected_color.lower()))
            btn.clicked.connect(lambda checked=False, c=color: self._select_color(c))
            palette_layout.addWidget(btn, row, col)
            self.color_buttons.append(btn)

        layout.addLayout(palette_layout)
        layout.addStretch()

        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel", self)
        cancel_btn.setProperty("class", "secondaryBtn")
        cancel_btn.setFixedHeight(32)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save", self)
        save_btn.setProperty("class", "primaryBtn")
        save_btn.setFixedHeight(32)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _clear_error(self):
        self.name_input.setProperty("hasError", False)
        self.name_input.style().unpolish(self.name_input)
        self.name_input.style().polish(self.name_input)

    def _style_color_btn(self, btn: QPushButton, color: str, is_selected: bool):
        theme = ThemeManager.instance()
        if is_selected:
            sel_border = theme.get_color("swatch_border")
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border-radius: 13px;
                    border: 2.5px solid {sel_border};
                }}
            """)
        else:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border-radius: 13px;
                    border: 1px solid rgba(128, 128, 128, 0.35);
                }}
            """)

    def _select_color(self, color: str):
        self.selected_color = color
        for btn in self.color_buttons:
            c = btn.property("color_val")
            self._style_color_btn(btn, c, is_selected=(c.lower() == color.lower()))

    def _on_save(self):
        name = self.name_input.text().strip()
        if not name:
            self.name_input.setProperty("hasError", True)
            self.name_input.style().unpolish(self.name_input)
            self.name_input.style().polish(self.name_input)
            self.name_input.setFocus()
            return
        self.accept()

    def get_data(self) -> tuple:
        """Returns (name, color)."""
        return self.name_input.text().strip(), self.selected_color
