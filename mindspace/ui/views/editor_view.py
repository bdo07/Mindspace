"""Markdown note editor view with live split preview, toolbar, and auto-save."""

from typing import List, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QKeySequence, QResizeEvent, QShortcut
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from mindspace.models.category import Category
from mindspace.models.note import Note
from mindspace.services.category_service import CategoryService
from mindspace.services.note_service import NoteService
from mindspace.ui.assets.icons import get_icon, render_svg_pixmap
from mindspace.ui.components.toolbar import EditorToolbar
from mindspace.ui.dialogs.confirm_dialog import ConfirmDialog
from mindspace.ui.themes.theme_manager import ThemeManager
from mindspace.utils.debounce import Debouncer
from mindspace.utils.markdown_utils import markdown_to_html


class EditorView(QWidget):
    """Note editor view with live markdown preview, formatting tools, and auto-save."""

    back_requested = Signal()
    note_saved = Signal(int)
    note_deleted = Signal(int)

    def __init__(
        self,
        note_service: NoteService,
        category_service: CategoryService,
        parent=None,
    ):
        super().__init__(parent)
        self.note_service = note_service
        self.category_service = category_service
        self.current_note: Optional[Note] = None

        self._is_loading = False
        self._mode = "write"  # 'write', 'split', 'preview'

        self._setup_ui()
        self._setup_shortcuts()
        self._setup_debouncer()
        self._update_icons()
        ThemeManager.instance().theme_changed.connect(self._on_theme_changed)

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 18, 24, 20)
        main_layout.setSpacing(12)

        # 1. Top Action Bar
        top_bar = QHBoxLayout()
        top_bar.setSpacing(8)

        self.back_btn = QPushButton("All Notes", self)
        self.back_btn.setProperty("class", "secondaryBtn")
        self.back_btn.setFixedHeight(32)
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.clicked.connect(self._on_back_clicked)
        top_bar.addWidget(self.back_btn)

        # Category dropdown
        self.cat_combo = QComboBox(self)
        self.cat_combo.setProperty("class", "standardInput")
        self.cat_combo.setFixedHeight(32)
        self.cat_combo.setMinimumWidth(130)
        self.cat_combo.currentIndexChanged.connect(self._on_category_changed)
        top_bar.addWidget(self.cat_combo)

        # Save status indicator
        self.status_container = QWidget(self)
        status_layout = QHBoxLayout(self.status_container)
        status_layout.setContentsMargins(6, 0, 6, 0)
        status_layout.setSpacing(6)

        self.status_dot = QLabel(self.status_container)
        self.status_dot.setFixedSize(7, 7)
        self.status_dot.setStyleSheet("background-color: #34C759; border-radius: 3px;")
        status_layout.addWidget(self.status_dot)

        self.save_status = QLabel("Saved", self.status_container)
        self.save_status.setStyleSheet("font-size: 11px; font-weight: 500; color: #8E8E93;")
        status_layout.addWidget(self.save_status)

        top_bar.addWidget(self.status_container)
        top_bar.addStretch()

        # View mode selector (Write / Split / Preview)
        mode_box = QFrame(self)
        mode_box.setStyleSheet("background: transparent;")
        mode_layout = QHBoxLayout(mode_box)
        mode_layout.setContentsMargins(0, 0, 0, 0)
        mode_layout.setSpacing(2)

        self.btn_mode_write = QPushButton("Write", mode_box)
        self.btn_mode_write.setProperty("class", "segmentedTab")
        self.btn_mode_write.setFixedHeight(28)
        self.btn_mode_write.setCursor(Qt.PointingHandCursor)
        self.btn_mode_write.clicked.connect(lambda: self.set_view_mode("write"))
        mode_layout.addWidget(self.btn_mode_write)

        self.btn_mode_split = QPushButton("Split", mode_box)
        self.btn_mode_split.setProperty("class", "segmentedTab")
        self.btn_mode_split.setFixedHeight(28)
        self.btn_mode_split.setCursor(Qt.PointingHandCursor)
        self.btn_mode_split.clicked.connect(lambda: self.set_view_mode("split"))
        mode_layout.addWidget(self.btn_mode_split)

        self.btn_mode_preview = QPushButton("Preview", mode_box)
        self.btn_mode_preview.setProperty("class", "segmentedTab")
        self.btn_mode_preview.setFixedHeight(28)
        self.btn_mode_preview.setCursor(Qt.PointingHandCursor)
        self.btn_mode_preview.clicked.connect(lambda: self.set_view_mode("preview"))
        mode_layout.addWidget(self.btn_mode_preview)

        top_bar.addWidget(mode_box)

        # Pin toggle button
        self.pin_btn = QPushButton(self)
        self.pin_btn.setProperty("class", "iconBtn")
        self.pin_btn.setFixedSize(30, 30)
        self.pin_btn.setToolTip("Pin Note")
        self.pin_btn.setCursor(Qt.PointingHandCursor)
        self.pin_btn.clicked.connect(self._toggle_pin)
        top_bar.addWidget(self.pin_btn)

        # Favorite toggle button
        self.fav_btn = QPushButton(self)
        self.fav_btn.setProperty("class", "iconBtn")
        self.fav_btn.setFixedSize(30, 30)
        self.fav_btn.setToolTip("Favorite Note")
        self.fav_btn.setCursor(Qt.PointingHandCursor)
        self.fav_btn.clicked.connect(self._toggle_favorite)
        top_bar.addWidget(self.fav_btn)

        # Archive button
        self.archive_btn = QPushButton(self)
        self.archive_btn.setProperty("class", "iconBtn")
        self.archive_btn.setFixedSize(30, 30)
        self.archive_btn.setToolTip("Archive Note")
        self.archive_btn.setCursor(Qt.PointingHandCursor)
        self.archive_btn.clicked.connect(self._toggle_archive)
        top_bar.addWidget(self.archive_btn)

        # Delete button
        self.delete_btn = QPushButton(self)
        self.delete_btn.setProperty("class", "iconBtn")
        self.delete_btn.setFixedSize(30, 30)
        self.delete_btn.setToolTip("Delete Note")
        self.delete_btn.setCursor(Qt.PointingHandCursor)
        self.delete_btn.clicked.connect(self._delete_note)
        top_bar.addWidget(self.delete_btn)

        main_layout.addLayout(top_bar)

        # 2. Note Title Input
        self.title_input = QLineEdit(self)
        self.title_input.setObjectName("editorTitleInput")
        self.title_input.setPlaceholderText("Untitled Note")
        self.title_input.textChanged.connect(self._on_content_changed)
        main_layout.addWidget(self.title_input)

        # 3. Formatting Toolbar
        self.toolbar = EditorToolbar(parent=self)
        self.toolbar.preview_toggled.connect(self._on_toolbar_preview_toggle)
        main_layout.addWidget(self.toolbar)

        # 4. Content Area: Splitter hosting Editor and Preview Browser
        self.splitter = QSplitter(Qt.Horizontal, self)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: transparent;
                width: 6px;
            }
        """)

        self.editor_content = QPlainTextEdit(self.splitter)
        self.editor_content.setObjectName("editorContentInput")
        self.editor_content.setPlaceholderText("Start typing note content here... (Markdown supported)")
        self.editor_content.textChanged.connect(self._on_content_changed)
        self.toolbar.set_editor(self.editor_content)
        self.splitter.addWidget(self.editor_content)

        self.preview_browser = QTextBrowser(self.splitter)
        self.preview_browser.setObjectName("markdownPreview")
        self.preview_browser.setOpenExternalLinks(True)
        self.splitter.addWidget(self.preview_browser)

        main_layout.addWidget(self.splitter, 1)

        self.set_view_mode("write")

    def _setup_shortcuts(self):
        save_sc = QShortcut(QKeySequence.Save, self)
        save_sc.activated.connect(self.save_immediately)

        bold_sc = QShortcut(QKeySequence("Ctrl+B"), self)
        bold_sc.activated.connect(lambda: self.toolbar._wrap_selection("**", "**"))

        italic_sc = QShortcut(QKeySequence("Ctrl+I"), self)
        italic_sc.activated.connect(lambda: self.toolbar._wrap_selection("*", "*"))

    def _setup_debouncer(self):
        self.save_debouncer = Debouncer(delay_ms=600, callback=self._perform_save, parent=self)

    def set_view_mode(self, mode: str):
        """Switches between 'write', 'split', and 'preview' modes."""
        self._mode = mode
        self.btn_mode_write.setProperty("active", "true" if mode == "write" else "false")
        self.btn_mode_split.setProperty("active", "true" if mode == "split" else "false")
        self.btn_mode_preview.setProperty("active", "true" if mode == "preview" else "false")
        self.btn_mode_write.style().polish(self.btn_mode_write)
        self.btn_mode_split.style().polish(self.btn_mode_split)
        self.btn_mode_preview.style().polish(self.btn_mode_preview)

        if mode == "write":
            self.editor_content.setVisible(True)
            self.preview_browser.setVisible(False)
            self.editor_content.setFocus()
        elif mode == "preview":
            self._render_markdown()
            self.editor_content.setVisible(False)
            self.preview_browser.setVisible(True)
        elif mode == "split":
            self._render_markdown()
            self.editor_content.setVisible(True)
            self.preview_browser.setVisible(True)
            # Give equal halves
            half = self.splitter.width() // 2 if self.splitter.width() > 0 else 400
            self.splitter.setSizes([half, half])
            self.editor_content.setFocus()

    def _on_toolbar_preview_toggle(self, is_preview: bool):
        self.set_view_mode("preview" if is_preview else "write")

    def _render_markdown(self):
        content = self.editor_content.toPlainText()
        theme = ThemeManager.instance().current_theme
        html_content = markdown_to_html(content, theme=theme)
        self.preview_browser.setHtml(html_content)

    def load_note(self, note_id: int):
        """Loads a note into the editor."""
        self._is_loading = True
        self.current_note = self.note_service.get_note(note_id)

        self._populate_categories()

        if self.current_note:
            self.title_input.setText(self.current_note.title)
            self.editor_content.setPlainText(self.current_note.content)

            for i in range(self.cat_combo.count()):
                if self.cat_combo.itemData(i) == self.current_note.category_id:
                    self.cat_combo.setCurrentIndex(i)
                    break

            if self.current_note.is_archived:
                self.archive_btn.setToolTip("Restore Note")
            else:
                self.archive_btn.setToolTip("Archive Note")

        self._set_save_status(saved=True)
        self._update_icons()
        self._is_loading = False

        # Default to write mode
        self.set_view_mode("write")

    def _populate_categories(self):
        self.cat_combo.blockSignals(True)
        self.cat_combo.clear()
        self.cat_combo.addItem("No Category", userData=None)
        for cat in self.category_service.list_categories():
            self.cat_combo.addItem(cat.name, userData=cat.id)
        self.cat_combo.blockSignals(False)

    def _set_save_status(self, saved: bool):
        if saved:
            self.status_dot.setStyleSheet("background-color: #34C759; border-radius: 3px;")
            self.save_status.setText("Saved")
        else:
            self.status_dot.setStyleSheet("background-color: #E67700; border-radius: 3px;")
            self.save_status.setText("Saving...")

    def _on_content_changed(self):
        if self._is_loading or not self.current_note:
            return
        self._set_save_status(saved=False)
        self.save_debouncer.call()
        if self._mode in ("split", "preview"):
            self._render_markdown()

    def _on_category_changed(self, idx: int):
        if self._is_loading or not self.current_note:
            return
        cat_id = self.cat_combo.currentData()
        self.note_service.update_note(self.current_note.id, category_id=cat_id)
        self.current_note.category_id = cat_id
        self.note_saved.emit(self.current_note.id)

    def _perform_save(self):
        if not self.current_note or not self.current_note.id:
            return

        title = self.title_input.text().strip() or "Untitled Note"
        content = self.editor_content.toPlainText()
        cat_id = self.cat_combo.currentData()

        self.note_service.update_note(
            note_id=self.current_note.id,
            title=title,
            content=content,
            category_id=cat_id,
        )
        self.current_note.title = title
        self.current_note.content = content
        self.current_note.category_id = cat_id

        self._set_save_status(saved=True)
        self.note_saved.emit(self.current_note.id)

    def save_immediately(self):
        """Immediately triggers save."""
        self.save_debouncer.trigger_now()

    def _on_back_clicked(self):
        self.save_immediately()
        self.back_requested.emit()

    def _toggle_pin(self):
        if not self.current_note:
            return
        updated = self.note_service.toggle_pin(self.current_note.id)
        if updated:
            self.current_note = updated
            self._update_icons()
            self.note_saved.emit(self.current_note.id)

    def _toggle_favorite(self):
        if not self.current_note:
            return
        updated = self.note_service.toggle_favorite(self.current_note.id)
        if updated:
            self.current_note = updated
            self._update_icons()
            self.note_saved.emit(self.current_note.id)

    def _toggle_archive(self):
        if not self.current_note:
            return
        if self.current_note.is_archived:
            updated = self.note_service.restore_note(self.current_note.id)
        else:
            updated = self.note_service.archive_note(self.current_note.id)

        if updated:
            self.current_note = updated
            self.note_saved.emit(self.current_note.id)
            self.back_requested.emit()

    def _delete_note(self):
        if not self.current_note:
            return

        confirmed = ConfirmDialog.ask(
            self,
            title="Delete Note",
            message=f"Are you sure you want to delete '{self.current_note.title}'? This action cannot be undone.",
            confirm_label="Delete",
            is_danger=True,
        )
        if confirmed:
            note_id = self.current_note.id
            self.note_service.delete_note(note_id)
            self.note_deleted.emit(note_id)
            self.back_requested.emit()

    def _on_theme_changed(self, theme_name: str = ""):
        try:
            self._update_icons()
            if self._mode in ("split", "preview"):
                self._render_markdown()
        except RuntimeError:
            pass

    def _update_icons(self):
        try:
            theme = ThemeManager.instance()
            icon_color = theme.get_color("icon")
            gold_color = theme.get_color("icon_gold")
            accent_color = theme.get_color("accent")

            self.back_btn.setIcon(get_icon("arrow-left", color=icon_color, size=14))

            if self.current_note:
                if self.current_note.is_pinned:
                    self.pin_btn.setIcon(get_icon("pin", color=accent_color, fill=accent_color, size=15))
                    self.pin_btn.setProperty("active", "true")
                else:
                    self.pin_btn.setIcon(get_icon("pin", color=icon_color, fill="none", size=15))
                    self.pin_btn.setProperty("active", "false")

                if self.current_note.is_favorite:
                    self.fav_btn.setIcon(get_icon("favorites", color=gold_color, fill=gold_color, size=15))
                    self.fav_btn.setProperty("active", "true")
                else:
                    self.fav_btn.setIcon(get_icon("favorites", color=icon_color, fill="none", size=15))
                    self.fav_btn.setProperty("active", "false")

                self.archive_btn.setIcon(get_icon("archived", color=icon_color, size=15))
                self.delete_btn.setIcon(get_icon("trash", color=theme.get_color("danger"), size=15))

                self.pin_btn.style().polish(self.pin_btn)
                self.fav_btn.style().polish(self.fav_btn)
        except RuntimeError:
            pass

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        # If window gets narrower than 950px, disable split view automatically to prevent text clipping
        if self.width() < 950 and self._mode == "split":
            self.set_view_mode("write")
