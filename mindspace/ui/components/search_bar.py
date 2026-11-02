"""Search input component with debounce and clear button."""

from PySide6.QtCore import QPoint, QSize, Qt, Signal
from PySide6.QtGui import QIcon, QPainter
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QWidget

from mindspace.ui.assets.icons import get_icon, render_svg_pixmap
from mindspace.ui.themes.theme_manager import ThemeManager
from mindspace.utils.debounce import Debouncer


class SearchBar(QWidget):
    """Clean minimalist search bar with icon, debounce, and clear action."""

    search_changed = Signal(str)

    def __init__(self, placeholder: str = "Search notes, tags, content...", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.input = QLineEdit(self)
        self.input.setProperty("class", "searchInput")
        self.input.setPlaceholderText(placeholder)
        self.input.setFixedHeight(38)

        # Clear button
        self.clear_btn = QPushButton(self)
        self.clear_btn.setFixedSize(24, 24)
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.setStyleSheet("border: none; background: transparent;")
        self.clear_btn.setVisible(False)
        self.clear_btn.clicked.connect(self.clear_search)

        layout.addWidget(self.input)

        # Connect debouncer
        self.debouncer = Debouncer(delay_ms=250, callback=self._emit_search, parent=self)
        self.input.textChanged.connect(self._on_text_changed)

        self._update_icons()
        ThemeManager.instance().theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self, theme_name: str = ""):
        try:
            self._update_icons()
        except RuntimeError:
            pass

    def _update_icons(self):
        try:
            theme = ThemeManager.instance()
            icon_color = theme.get_color("icon")
            self.clear_btn.setIcon(get_icon("close", color=icon_color, size=14))
            search_icon = get_icon("search", color=icon_color, size=16)
            self.input.addAction(search_icon, QLineEdit.LeadingPosition)
        except RuntimeError:
            pass

    def _on_text_changed(self, text: str):
        self.clear_btn.setVisible(bool(text.strip()))
        self.debouncer.call(text.strip())

    def _emit_search(self, query: str):
        self.search_changed.emit(query)

    def clear_search(self):
        self.input.clear()
        self.search_changed.emit("")

    def set_focus(self):
        self.input.setFocus()
        self.input.selectAll()

    def text(self) -> str:
        return self.input.text().strip()
