"""Note card component for grid/list display."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from mindspace.models.note import Note
from mindspace.ui.assets.icons import get_icon
from mindspace.ui.themes.theme_manager import ThemeManager
from mindspace.utils.date_utils import format_relative_date


class NoteCard(QFrame):
    """Interactive card displaying a note preview."""

    clicked = Signal(int)
    favorite_toggled = Signal(int)
    archive_requested = Signal(int)
    delete_requested = Signal(int)

    def __init__(self, note: Note, parent=None):
        super().__init__(parent)
        self.note = note
        self.setCursor(Qt.PointingHandCursor)

        self._setup_ui()
        self._update_icons()

    def _setup_ui(self):
        self.setProperty("class", "noteCardPinned" if self.note.is_pinned else "noteCard")
        self.setMinimumHeight(120)
        self.setMaximumHeight(160)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 12, 14, 12)
        main_layout.setSpacing(6)

        # Header: Pin indicator + Title + Favorite Button
        header_layout = QHBoxLayout()
        header_layout.setSpacing(6)

        if self.note.is_pinned:
            self.pin_label = QLabel(self)
            self.pin_label.setFixedSize(16, 16)
            header_layout.addWidget(self.pin_label)

        self.title_label = QLabel(self.note.title or "Untitled Note", self)
        self.title_label.setProperty("class", "cardTitle")
        self.title_label.setWordWrap(False)
        header_layout.addWidget(self.title_label, 1)

        self.fav_btn = QPushButton(self)
        self.fav_btn.setProperty("class", "iconBtn")
        self.fav_btn.setFixedSize(24, 24)
        self.fav_btn.setCursor(Qt.PointingHandCursor)
        self.fav_btn.clicked.connect(self._on_fav_clicked)
        header_layout.addWidget(self.fav_btn)

        main_layout.addLayout(header_layout)

        # Body: Snippet preview
        self.preview_label = QLabel(self.note.preview, self)
        self.preview_label.setProperty("class", "cardPreview")
        self.preview_label.setWordWrap(True)
        self.preview_label.setMaximumHeight(44)
        main_layout.addWidget(self.preview_label, 1)

        # Footer: Category Pill + Date
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(8)

        if self.note.category_name:
            color = self.note.category_color or "#8B79D9"
            self.category_pill = QLabel(f" {self.note.category_name} ", self)
            self.category_pill.setProperty("class", "categoryPill")
            # Soft pastel background with category color border
            self.category_pill.setStyleSheet(f"""
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
            footer_layout.addWidget(self.category_pill)

        self.date_label = QLabel(format_relative_date(self.note.updated_at), self)
        self.date_label.setProperty("class", "cardDate")
        footer_layout.addWidget(self.date_label)

        footer_layout.addStretch()
        main_layout.addLayout(footer_layout)

    def _update_icons(self):
        theme = ThemeManager.instance()
        gold_color = theme.get_color("icon_gold")
        muted_color = theme.get_color("icon")

        if self.note.is_pinned and hasattr(self, "pin_label"):
            accent_color = theme.get_color("accent")
            self.pin_label.setPixmap(
                get_icon("pin", color=accent_color, fill=accent_color, size=14).pixmap(14, 14)
            )

        if self.note.is_favorite:
            self.fav_btn.setIcon(get_icon("favorites", color=gold_color, fill=gold_color, size=15))
        else:
            self.fav_btn.setIcon(get_icon("favorites", color=muted_color, fill="none", size=15))

    def _on_fav_clicked(self):
        if self.note.id:
            self.favorite_toggled.emit(self.note.id)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Check if clicked on fav_btn or its area
            child = self.childAt(event.pos())
            if child != self.fav_btn and not self.fav_btn.isAncestorOf(child):
                if self.note.id:
                    self.clicked.emit(self.note.id)
        super().mousePressEvent(event)
