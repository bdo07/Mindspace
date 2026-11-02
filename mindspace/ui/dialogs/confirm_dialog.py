"""Confirmation dialog for destructive and warning actions."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from mindspace.ui.themes.theme_manager import ThemeManager


class ConfirmDialog(QDialog):
    """Clean confirmation dialog."""

    def __init__(
        self,
        title: str = "Confirm Action",
        message: str = "Are you sure you want to proceed?",
        confirm_label: str = "Confirm",
        is_danger: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(380, 160)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        theme = ThemeManager.instance()
        bg_color = theme.get_color("surface")
        text_color = theme.get_color("text")
        sec_color = theme.get_color("text_secondary")
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

        title_lbl = QLabel(title, self)
        title_lbl.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {text_color};")
        layout.addWidget(title_lbl)

        msg_lbl = QLabel(message, self)
        msg_lbl.setStyleSheet(f"font-size: 13px; color: {sec_color}; line-height: 1.4;")
        msg_lbl.setWordWrap(True)
        layout.addWidget(msg_lbl, 1)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel", self)
        cancel_btn.setProperty("class", "secondaryBtn")
        cancel_btn.setFixedHeight(34)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        confirm_btn = QPushButton(confirm_label, self)
        confirm_btn.setProperty("class", "dangerBtn" if is_danger else "primaryBtn")
        confirm_btn.setFixedHeight(34)
        confirm_btn.setCursor(Qt.PointingHandCursor)
        confirm_btn.clicked.connect(self.accept)
        btn_layout.addWidget(confirm_btn)

        layout.addLayout(btn_layout)

    @classmethod
    def ask(
        cls,
        parent,
        title: str,
        message: str,
        confirm_label: str = "Delete",
        is_danger: bool = True,
    ) -> bool:
        dlg = cls(title, message, confirm_label, is_danger, parent)
        return dlg.exec() == QDialog.Accepted

