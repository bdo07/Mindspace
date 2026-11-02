"""Notes view displaying searchable, sortable, responsive grid of note cards."""

from typing import List, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from mindspace.models.category import Category
from mindspace.models.note import Note
from mindspace.services.category_service import CategoryService
from mindspace.services.note_service import NoteService
from mindspace.ui.assets.icons import get_icon, render_svg_pixmap
from mindspace.ui.components.note_card import NoteCard
from mindspace.ui.components.search_bar import SearchBar
from mindspace.ui.dialogs.confirm_dialog import ConfirmDialog
from mindspace.ui.themes.theme_manager import ThemeManager


class NotesView(QWidget):
    """View showing notes in an adaptive, responsive grid with filters, search, and sorting."""

    note_selected = Signal(int)
    new_note_requested = Signal()
    note_updated = Signal()

    def __init__(
        self,
        note_service: NoteService,
        category_service: CategoryService,
        view_mode: str = "notes",  # 'notes', 'favorites', 'archived', 'category'
        category_id: Optional[int] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.note_service = note_service
        self.category_service = category_service
        self.view_mode = view_mode
        self.category_id = category_id

        self.current_search = ""
        self.current_sort = "updated_at"
        self.current_sort_desc = True
        self.selected_filter_category_id: Optional[int] = category_id
        self._current_cols = 2

        self._cards: List[NoteCard] = []

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

        # 1. Header Row (Title, Subtitle, New Note Button)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        self.title_lbl = QLabel(self._get_title_text(), self)
        self.title_lbl.setObjectName("pageTitle")
        title_col.addWidget(self.title_lbl)

        self.subtitle_lbl = QLabel("0 notes", self)
        self.subtitle_lbl.setObjectName("pageSubtitle")
        title_col.addWidget(self.subtitle_lbl)

        header_layout.addLayout(title_col, 1)

        if self.view_mode != "archived":
            self.new_note_btn = QPushButton("New Note", self)
            self.new_note_btn.setProperty("class", "primaryBtn")
            self.new_note_btn.setFixedHeight(34)
            self.new_note_btn.setCursor(Qt.PointingHandCursor)
            self.new_note_btn.clicked.connect(self.new_note_requested.emit)
            header_layout.addWidget(self.new_note_btn)

        main_layout.addLayout(header_layout)

        # 2. Controls Row (Search, Category Filter, Sort)
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)

        self.search_bar = SearchBar(placeholder="Search notes, tags, content...", parent=self)
        self.search_bar.search_changed.connect(self._on_search)
        controls_layout.addWidget(self.search_bar, 1)

        # Category Filter Dropdown
        if self.view_mode in ("notes", "favorites"):
            self.cat_filter = QComboBox(self)
            self.cat_filter.setProperty("class", "standardInput")
            self.cat_filter.setFixedHeight(36)
            self.cat_filter.setMinimumWidth(130)
            self.cat_filter.addItem("All Categories", userData=None)
            self.cat_filter.currentIndexChanged.connect(self._on_cat_filter_changed)
            controls_layout.addWidget(self.cat_filter)

        # Sort dropdown
        self.sort_combo = QComboBox(self)
        self.sort_combo.setProperty("class", "standardInput")
        self.sort_combo.setFixedHeight(36)
        self.sort_combo.setMinimumWidth(140)
        self.sort_combo.addItem("Recently Updated", userData=("updated_at", True))
        self.sort_combo.addItem("Recently Created", userData=("created_at", True))
        self.sort_combo.addItem("Title (A-Z)", userData=("title", False))
        self.sort_combo.currentIndexChanged.connect(self._on_sort_changed)
        controls_layout.addWidget(self.sort_combo)

        main_layout.addLayout(controls_layout)

        # 3. Scrollable Grid Area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.grid_container = QWidget()
        self.grid_container.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(0, 4, 0, 16)
        self.grid_layout.setSpacing(12)

        self.scroll_area.setWidget(self.grid_container)
        main_layout.addWidget(self.scroll_area, 1)

        # 4. Empty State Container
        self.empty_state = QWidget(self)
        empty_layout = QVBoxLayout(self.empty_state)
        empty_layout.setAlignment(Qt.AlignCenter)
        empty_layout.setSpacing(8)

        self.empty_icon = QLabel(self.empty_state)
        self.empty_icon.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(self.empty_icon)

        self.empty_title = QLabel("No notes found", self.empty_state)
        self.empty_title.setProperty("class", "emptyStateTitle")
        self.empty_title.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(self.empty_title)

        self.empty_text = QLabel("Start capturing your thoughts, plans, and ideas.", self.empty_state)
        self.empty_text.setProperty("class", "emptyStateText")
        self.empty_text.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(self.empty_text)

        if self.view_mode != "archived":
            self.empty_btn = QPushButton("Create Note", self.empty_state)
            self.empty_btn.setProperty("class", "primaryBtn")
            self.empty_btn.setFixedHeight(34)
            self.empty_btn.setCursor(Qt.PointingHandCursor)
            self.empty_btn.clicked.connect(self.new_note_requested.emit)
            empty_layout.addWidget(self.empty_btn, 0, Qt.AlignCenter)

        self.empty_state.setVisible(False)
        main_layout.addWidget(self.empty_state, 1)

    def _get_title_text(self) -> str:
        if self.view_mode == "favorites":
            return "Favorites"
        elif self.view_mode == "archived":
            return "Archived Notes"
        elif self.view_mode == "category" and self.category_id:
            cat = self.category_service.get_category(self.category_id)
            return cat.name if cat else "Category Notes"
        return "All Notes"

    def _calculate_columns(self) -> int:
        """Dynamically computes number of columns based on available width."""
        viewport_w = self.scroll_area.viewport().width()
        if viewport_w <= 100:
            viewport_w = max(300, self.width() - 48)

        if viewport_w < 560:
            return 1
        elif viewport_w < 860:
            return 2
        elif viewport_w < 1220:
            return 3
        else:
            return 4

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        new_cols = self._calculate_columns()
        if new_cols != self._current_cols and self._cards:
            self._current_cols = new_cols
            self._reposition_cards()

    def _reposition_cards(self):
        """Relayouts existing cards into current column count without re-instantiating."""
        for card in self._cards:
            self.grid_layout.removeWidget(card)

        for idx, card in enumerate(self._cards):
            row = idx // self._current_cols
            col = idx % self._current_cols
            self.grid_layout.addWidget(card, row, col)

    def refresh(self):
        """Reloads notes from database and refreshes grid."""
        # Update category dropdown
        if hasattr(self, "cat_filter"):
            current_selected = self.cat_filter.currentData()
            self.cat_filter.blockSignals(True)
            self.cat_filter.clear()
            self.cat_filter.addItem("All Categories", userData=None)
            for c in self.category_service.list_categories():
                self.cat_filter.addItem(c.name, userData=c.id)
            for i in range(self.cat_filter.count()):
                if self.cat_filter.itemData(i) == current_selected:
                    self.cat_filter.setCurrentIndex(i)
                    break
            self.cat_filter.blockSignals(False)

        # Clear existing cards
        for card in self._cards:
            self.grid_layout.removeWidget(card)
            card.deleteLater()
        self._cards.clear()

        # Fetch notes
        is_archived = (self.view_mode == "archived")
        is_fav = True if self.view_mode == "favorites" else None
        cat_id = self.category_id if self.view_mode == "category" else self.selected_filter_category_id

        notes = self.note_service.list_notes(
            category_id=cat_id,
            is_favorite=is_fav,
            is_archived=is_archived,
            is_quick=False,
            search_query=self.current_search,
            sort_by=self.current_sort,
            sort_desc=self.current_sort_desc,
        )

        # Update labels
        self.title_lbl.setText(self._get_title_text())
        count_text = f"{len(notes)} note" if len(notes) == 1 else f"{len(notes)} notes"
        if self.current_search:
            count_text += f" matching '{self.current_search}'"
        self.subtitle_lbl.setText(count_text)

        # Show empty state or populate cards
        if not notes:
            self.scroll_area.setVisible(False)
            self.empty_state.setVisible(True)
            return

        self.scroll_area.setVisible(True)
        self.empty_state.setVisible(False)

        self._current_cols = self._calculate_columns()
        for idx, note in enumerate(notes):
            card = NoteCard(note, self.grid_container)
            card.clicked.connect(self.note_selected.emit)
            card.favorite_toggled.connect(self._on_toggle_fav)

            row = idx // self._current_cols
            col = idx % self._current_cols
            self.grid_layout.addWidget(card, row, col)
            self._cards.append(card)

    def _on_toggle_fav(self, note_id: int):
        self.note_service.toggle_favorite(note_id)
        self.note_updated.emit()
        self.refresh()

    def _on_search(self, query: str):
        self.current_search = query
        self.refresh()

    def _on_cat_filter_changed(self, idx: int):
        self.selected_filter_category_id = self.cat_filter.currentData()
        self.refresh()

    def _on_sort_changed(self, idx: int):
        sort_by, sort_desc = self.sort_combo.currentData()
        self.current_sort = sort_by
        self.current_sort_desc = sort_desc
        self.refresh()

    def _update_icons(self):
        try:
            theme = ThemeManager.instance()
            accent_color = theme.get_color("accent")

            if hasattr(self, "new_note_btn"):
                self.new_note_btn.setIcon(get_icon("plus", color="#FFFFFF", size=14))

            self.empty_icon.setPixmap(render_svg_pixmap("notes", color=accent_color, size=44))
        except RuntimeError:
            pass
