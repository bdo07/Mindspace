"""Quick Notes scratchpad view for frictionless, rapid capture."""

from typing import List
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence, QShortcut, QGuiApplication
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from mindspace.models.note import Note
from mindspace.services.note_service import NoteService
from mindspace.ui.assets.icons import get_icon, render_svg_pixmap
from mindspace.ui.dialogs.confirm_dialog import ConfirmDialog
from mindspace.ui.themes.theme_manager import ThemeManager
from mindspace.utils.date_utils import format_relative_date


class QuickNotesView(QWidget):
    """Frictionless scratchpad view for instant thought capture."""

    open_in_editor_requested = Signal(int)
    counts_changed = Signal()

    def __init__(self, note_service: NoteService, parent=None):
        super().__init__(parent)
        self.note_service = note_service
        self._cards: List[QWidget] = []

        self._setup_ui()
        self._setup_shortcuts()
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

        # 1. Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(2)

        title = QLabel("Quick Notes", self)
        title.setObjectName("pageTitle")
        header_layout.addWidget(title)

        subtitle = QLabel("Instantly capture fleeting thoughts and raw ideas without friction.", self)
        subtitle.setObjectName("pageSubtitle")
        header_layout.addWidget(subtitle)

        main_layout.addLayout(header_layout)

        # 2. Quick Capture Box
        capture_frame = QFrame(self)
        capture_frame.setObjectName("quickCaptureBox")
        capture_frame.setProperty("class", "noteCard")

        capture_layout = QVBoxLayout(capture_frame)
        capture_layout.setContentsMargins(14, 12, 14, 12)
        capture_layout.setSpacing(8)

        self.input_box = QPlainTextEdit(capture_frame)
        self.input_box.setObjectName("quickCaptureInput")
        self.input_box.setPlaceholderText("What's on your mind? Jot down an idea, link, or fragment...")
        self.input_box.setMaximumHeight(80)
        capture_layout.addWidget(self.input_box)

        action_row = QHBoxLayout()
        hint_lbl = QLabel("Press Ctrl/Cmd + Enter to capture", capture_frame)
        hint_lbl.setProperty("class", "hintText")
        action_row.addWidget(hint_lbl)
        action_row.addStretch()

        self.add_btn = QPushButton("Capture Thought", capture_frame)
        self.add_btn.setProperty("class", "primaryBtn")
        self.add_btn.setFixedHeight(32)
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.clicked.connect(self._on_capture)
        action_row.addWidget(self.add_btn)

        capture_layout.addLayout(action_row)
        main_layout.addWidget(capture_frame)

        # 3. Scroll Area for thoughts
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.thoughts_container = QWidget()
        self.thoughts_container.setStyleSheet("background: transparent;")
        self.thoughts_layout = QVBoxLayout(self.thoughts_container)
        self.thoughts_layout.setContentsMargins(0, 4, 0, 16)
        self.thoughts_layout.setSpacing(10)
        self.thoughts_layout.addStretch()

        self.scroll_area.setWidget(self.thoughts_container)
        main_layout.addWidget(self.scroll_area, 1)

        # 4. Empty State
        self.empty_state = QWidget(self)
        empty_layout = QVBoxLayout(self.empty_state)
        empty_layout.setAlignment(Qt.AlignCenter)
        empty_layout.setSpacing(8)

        self.empty_icon = QLabel(self.empty_state)
        self.empty_icon.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(self.empty_icon)

        empty_title = QLabel("No quick notes yet", self.empty_state)
        empty_title.setProperty("class", "emptyStateTitle")
        empty_title.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(empty_title)

        empty_desc = QLabel("Type in the box above to capture your first thought.", self.empty_state)
        empty_desc.setProperty("class", "emptyStateText")
        empty_desc.setAlignment(Qt.AlignCenter)
        empty_layout.addWidget(empty_desc)

        self.empty_state.setVisible(False)
        main_layout.addWidget(self.empty_state, 1)

    def _setup_shortcuts(self):
        shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        shortcut.activated.connect(self._on_capture)

    def _on_capture(self):
        text = self.input_box.toPlainText().strip()
        if not text:
            return
        self.note_service.create_quick_note(content=text)
        self.input_box.clear()
        self.refresh()
        self.counts_changed.emit()

    def refresh(self):
        for card in self._cards:
            self.thoughts_layout.removeWidget(card)
            card.deleteLater()
        self._cards.clear()

        while self.thoughts_layout.count():
            item = self.thoughts_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        quick_notes = self.note_service.list_notes(is_archived=False, is_quick=True, sort_by="created_at", sort_desc=True)

        if not quick_notes:
            self.scroll_area.setVisible(False)
            self.empty_state.setVisible(True)
            return

        self.scroll_area.setVisible(True)
        self.empty_state.setVisible(False)

        theme = ThemeManager.instance()
        card_bg = theme.get_color("surface")
        border_color = theme.get_color("border")

        for note in quick_notes:
            card = QFrame(self.thoughts_container)
            card.setProperty("class", "noteCard")
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(14, 12, 14, 12)
            card_layout.setSpacing(8)

            # Thought Text
            content_lbl = QLabel(note.content, card)
            content_lbl.setProperty("class", "quickThoughtContent")
            content_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
            content_lbl.setWordWrap(True)
            card_layout.addWidget(content_lbl)

            # Footer
            footer = QHBoxLayout()
            footer.setSpacing(8)

            date_lbl = QLabel(format_relative_date(note.created_at), card)
            date_lbl.setProperty("class", "cardDate")
            footer.addWidget(date_lbl)
            footer.addStretch()

            # Copy button
            copy_btn = QPushButton("Copy", card)
            copy_btn.setProperty("class", "secondaryBtn")
            copy_btn.setFixedHeight(26)
            copy_btn.setCursor(Qt.PointingHandCursor)
            copy_btn.clicked.connect(lambda checked=False, txt=note.content: self._copy_to_clipboard(txt))
            footer.addWidget(copy_btn)

            # Convert to full note button
            convert_btn = QPushButton("Full Note", card)
            convert_btn.setProperty("class", "secondaryBtn")
            convert_btn.setFixedHeight(26)
            convert_btn.setCursor(Qt.PointingHandCursor)
            convert_btn.clicked.connect(lambda checked=False, nid=note.id: self._convert_to_full(nid))
            footer.addWidget(convert_btn)

            # Delete button
            del_btn = QPushButton(card)
            del_btn.setProperty("class", "iconBtn")
            del_btn.setFixedSize(26, 26)
            del_btn.setIcon(get_icon("trash", color=theme.get_color("danger"), size=13))
            del_btn.setCursor(Qt.PointingHandCursor)
            del_btn.setToolTip("Delete Quick Note")
            del_btn.clicked.connect(lambda checked=False, nid=note.id: self._delete_thought(nid))
            footer.addWidget(del_btn)

            card_layout.addLayout(footer)
            self.thoughts_layout.addWidget(card)
            self._cards.append(card)

        self.thoughts_layout.addStretch()

    def _copy_to_clipboard(self, text: str):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(text)

    def _convert_to_full(self, note_id: int):
        self.note_service.convert_quick_to_regular(note_id)
        self.counts_changed.emit()
        self.open_in_editor_requested.emit(note_id)

    def _delete_thought(self, note_id: int):
        confirmed = ConfirmDialog.ask(
            self,
            title="Delete Quick Note",
            message="Are you sure you want to delete this thought? This action cannot be undone.",
            confirm_label="Delete",
            is_danger=True,
        )
        if confirmed:
            self.note_service.delete_note(note_id)
            self.refresh()
            self.counts_changed.emit()

    def _update_icons(self):
        try:
            theme = ThemeManager.instance()
            self.add_btn.setIcon(get_icon("plus", color="#FFFFFF", size=13))
            self.empty_icon.setPixmap(render_svg_pixmap("quick", color=theme.get_color("accent"), size=44))
        except RuntimeError:
            pass
