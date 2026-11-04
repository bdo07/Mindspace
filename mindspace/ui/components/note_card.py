"""Note card component for grid/list display with high visual polish."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from mindspace.models.note import Note
from mindspace.ui.assets.icons import get_icon, render_svg_pixmap
from mindspace.ui.themes.theme_manager import ThemeManager
from mindspace.utils.date_utils import format_relative_date


class NoteCard(QFrame):
    """Interactive card displaying a note preview with refined typography and states."""

    clicked = Signal(int)
    favorite_toggled = Signal(int)
    pin_toggled = Signal(int)
    archive_requested = Signal(int)
    delete_requested = Signal(int)

    def __init__(self, note: Note, parent=None):
        super().__init__(parent)
        self.note = note
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumWidth(220)
        self.setMinimumHeight(115)
        self.setMaximumHeight(150)

        self._setup_ui()
        self._update_icons()

    def _setup_ui(self):
        self.setProperty("class", "noteCardPinned" if self.note.is_pinned else "noteCard")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 12, 14, 12)
        main_layout.setSpacing(6)

        # Header: Pin icon (if pinned) + Title + Favorite Star
        header_layout = QHBoxLayout()
        header_layout.setSpacing(6)

        if self.note.is_pinned:
            self.pin_label = QLabel(self)
            self.pin_label.setFixedSize(14, 14)
            header_layout.addWidget(self.pin_label)

        self.title_label = QLabel(self.note.title or "Untitled Note", self)
        self.title_label.setProperty("class", "cardTitle")
        self.title_label.setWordWrap(False)
        self.title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        header_layout.addWidget(self.title_label, 1)

        self.fav_btn = QPushButton(self)
        self.fav_btn.setProperty("class", "iconBtn")
        self.fav_btn.setFixedSize(24, 24)
        self.fav_btn.setCursor(Qt.PointingHandCursor)
        self.fav_btn.setToolTip("Mark Favorite")
        self.fav_btn.clicked.connect(self._on_fav_clicked)
        header_layout.addWidget(self.fav_btn)

        main_layout.addLayout(header_layout)

        # Body: Snippet preview (up to 2 lines)
        self.preview_label = QLabel(self.note.preview, self)
        self.preview_label.setProperty("class", "cardPreview")
        self.preview_label.setWordWrap(True)
        self.preview_label.setMaximumHeight(42)
        self.preview_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        main_layout.addWidget(self.preview_label, 1)

        # Footer: Category Pill + Date
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(8)

        if self.note.category_name:
            color = self.note.category_color or ThemeManager.instance().get_color("accent")
            qc = QColor(color)
            r, g, b = qc.red(), qc.green(), qc.blue()
            self.category_pill = QLabel(f" {self.note.category_name} ", self)
            self.category_pill.setStyleSheet(f"""
                QLabel {{
                    background-color: rgba({r}, {g}, {b}, 0.15);
                    color: {color};
                    border: 1px solid rgba({r}, {g}, {b}, 0.35);
                    border-radius: 8px;
                    padding: 1px 6px;
                    font-size: 10px;
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
        try:
            theme = ThemeManager.instance()
            gold_color = theme.get_color("icon_gold")
            muted_color = theme.get_color("icon")

            if self.note.is_pinned and hasattr(self, "pin_label"):
                accent_color = theme.get_color("accent")
                self.pin_label.setPixmap(
                    render_svg_pixmap("pin", color=accent_color, fill=accent_color, size=13)
                )

            if self.note.is_favorite:
                self.fav_btn.setIcon(get_icon("favorites", color=gold_color, fill=gold_color, size=14))
            else:
                self.fav_btn.setIcon(get_icon("favorites", color=muted_color, fill="none", size=14))
        except RuntimeError:
            pass

    def _on_fav_clicked(self):
        if self.note.id:
            self.favorite_toggled.emit(self.note.id)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            child = self.childAt(event.pos())
            if child != self.fav_btn and not self.fav_btn.isAncestorOf(child):
                if self.note.id:
                    self.clicked.emit(self.note.id)
        super().mousePressEvent(event)

    def contextMenuEvent(self, event):
        if not self.note or not self.note.id:
            return
        menu = QMenu(self)
        pin_act = menu.addAction("Unpin Note" if self.note.is_pinned else "Pin Note")
        fav_act = menu.addAction("Remove from Favorites" if self.note.is_favorite else "Add to Favorites")
        arch_act = menu.addAction("Restore Note" if self.note.is_archived else "Archive Note")
        menu.addSeparator()
        del_act = menu.addAction("Delete Note")

        action = menu.exec(event.globalPos())
        if action == pin_act:
            self.pin_toggled.emit(self.note.id)
        elif action == fav_act:
            self.favorite_toggled.emit(self.note.id)
        elif action == arch_act:
            self.archive_requested.emit(self.note.id)
        elif action == del_act:
            self.delete_requested.emit(self.note.id)
