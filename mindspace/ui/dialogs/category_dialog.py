"""Dialog for creating and editing categories."""

from typing import List, Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QColorDialog,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from mindspace.models.category import Category
from mindspace.ui.themes.theme_manager import ThemeManager

PALETTE: List[str] = [
    "#8B79D9",  # Mindspace Lavender
    "#6C5CE7",  # Deep Purple
    "#0984E3",  # Ocean Blue
    "#00B894",  # Mint Green
    "#00CEC9",  # Turquoise
    "#E17055",  # Terracotta Orange
    "#FD79A8",  # Rose Pink
    "#E84393",  # Magenta
    "#FDCB6E",  # Marigold
    "#636E72",  # Slate
]


class CategoryDialog(QDialog):
    """Dialog to create or edit category details."""

    def __init__(self, category: Optional[Category] = None, parent=None):
        super().__init__(parent)
        self.category = category
        self.selected_color = category.color if category else PALETTE[0]

        is_edit = category is not None
        self.setWindowTitle("Edit Category" if is_edit else "New Category")
        self.setFixedSize(360, 280)
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
        layout.setSpacing(14)

        # Title
        title_lbl = QLabel("Edit Category" if is_edit else "Create Category", self)
        title_lbl.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {text_color};")
        layout.addWidget(title_lbl)

        # Name input
        name_lbl = QLabel("Category Name", self)
        name_lbl.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {theme.get_color('text_secondary')};")
        layout.addWidget(name_lbl)

        self.name_input = QLineEdit(self)
        self.name_input.setProperty("class", "standardInput")
        self.name_input.setPlaceholderText("e.g. Work, Ideas, Research")
        if category:
            self.name_input.setText(category.name)
        layout.addWidget(self.name_input)

        # Color picker
        color_lbl = QLabel("Accent Color", self)
        color_lbl.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {theme.get_color('text_secondary')};")
        layout.addWidget(color_lbl)

        palette_layout = QGridLayout()
        palette_layout.setSpacing(8)
        self.color_buttons: List[QPushButton] = []

        for idx, color in enumerate(PALETTE):
            row = idx // 5
            col = idx % 5
            btn = QPushButton(self)
            btn.setFixedSize(28, 28)
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
        cancel_btn.setFixedHeight(34)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        save_btn = QPushButton("Save", self)
        save_btn.setProperty("class", "primaryBtn")
        save_btn.setFixedHeight(34)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

    def _style_color_btn(self, btn: QPushButton, color: str, is_selected: bool):
        border_style = "2px solid #202020" if is_selected else "1px solid rgba(0,0,0,0.15)"
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border-radius: 14px;
                border: {border_style};
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
            self.name_input.setFocus()
            return
        self.accept()

    def get_data(self) -> tuple:
        """Returns (name, color)."""
        return self.name_input.text().strip(), self.selected_color

