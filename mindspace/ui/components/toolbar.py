"""Markdown formatting toolbar for the Note Editor."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QPushButton,
    QPlainTextEdit,
    QTextEdit,
    QWidget,
)

from mindspace.ui.assets.icons import get_icon
from mindspace.ui.themes.theme_manager import ThemeManager


class EditorToolbar(QFrame):
    """Toolbar providing one-click markdown formatting actions."""

    preview_toggled = Signal(bool)

    def __init__(self, editor: QPlainTextEdit = None, parent=None):
        super().__init__(parent)
        self.setObjectName("editorToolbar")
        self.editor = editor
        self.is_preview_mode = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(4)

        self.btn_bold = self._create_btn("bold", "Bold (Ctrl+B)", lambda: self._wrap_selection("**", "**"))
        self.btn_italic = self._create_btn("italic", "Italic (Ctrl+I)", lambda: self._wrap_selection("*", "*"))
        self.btn_h1 = self._create_btn("heading", "Heading 1", lambda: self._prefix_line("# "))
        self.btn_list = self._create_btn("list", "Bullet List", lambda: self._prefix_line("- "))
        self.btn_todo = self._create_btn("tasks", "Checklist", lambda: self._prefix_line("- [ ] "))
        self.btn_quote = self._create_btn("quote", "Quote", lambda: self._prefix_line("> "))
        self.btn_code = self._create_btn("code", "Code Block", self._insert_code)
        self.btn_link = self._create_btn("link", "Insert Link", self._insert_link)

        layout.addWidget(self.btn_bold)
        layout.addWidget(self.btn_italic)
        layout.addWidget(self.btn_h1)
        layout.addWidget(self.btn_list)
        layout.addWidget(self.btn_todo)
        layout.addWidget(self.btn_quote)
        layout.addWidget(self.btn_code)
        layout.addWidget(self.btn_link)

        layout.addStretch()

        self.btn_preview = QPushButton(self)
        self.btn_preview.setProperty("class", "secondaryBtn")
        self.btn_preview.setText("Preview")
        self.btn_preview.setFixedHeight(30)
        self.btn_preview.setCursor(Qt.PointingHandCursor)
        self.btn_preview.clicked.connect(self._toggle_preview)
        layout.addWidget(self.btn_preview)

        self._update_icons()
        ThemeManager.instance().theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self, theme_name: str = ""):
        try:
            self._update_icons()
        except RuntimeError:
            pass

    def _create_btn(self, icon_name: str, tooltip: str, callback) -> QPushButton:
        btn = QPushButton(self)
        btn.setProperty("class", "iconBtn")
        btn.setToolTip(tooltip)
        btn.setFixedSize(30, 30)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(callback)
        btn.setProperty("icon_name", icon_name)
        return btn

    def _update_icons(self):
        try:
            theme = ThemeManager.instance()
            icon_color = theme.get_color("icon")
            for btn in self.findChildren(QPushButton):
                icon_name = btn.property("icon_name")
                if icon_name:
                    btn.setIcon(get_icon(icon_name, color=icon_color, size=15))

            preview_icon = get_icon("eye", color=icon_color, size=15)
            self.btn_preview.setIcon(preview_icon)
        except RuntimeError:
            pass

    def set_editor(self, editor: QPlainTextEdit):
        self.editor = editor

    def _wrap_selection(self, prefix: str, suffix: str):
        if not self.editor:
            return
        cursor = self.editor.textCursor()
        selected_text = cursor.selectedText()
        if selected_text:
            cursor.insertText(f"{prefix}{selected_text}{suffix}")
        else:
            cursor.insertText(f"{prefix}text{suffix}")
        self.editor.setFocus()

    def _prefix_line(self, prefix: str):
        if not self.editor:
            return
        cursor = self.editor.textCursor()
        cursor.movePosition(cursor.StartOfLine)
        cursor.insertText(prefix)
        self.editor.setFocus()

    def _insert_code(self):
        if not self.editor:
            return
        cursor = self.editor.textCursor()
        selected_text = cursor.selectedText()
        if "\n" in selected_text or not selected_text:
            cursor.insertText(f"```\n{selected_text or 'code'}\n```\n")
        else:
            cursor.insertText(f"`{selected_text}`")
        self.editor.setFocus()

    def _insert_link(self):
        if not self.editor:
            return
        cursor = self.editor.textCursor()
        selected_text = cursor.selectedText() or "link title"
        cursor.insertText(f"[{selected_text}](https://...)")
        self.editor.setFocus()

    def _toggle_preview(self):
        self.is_preview_mode = not self.is_preview_mode
        if self.is_preview_mode:
            self.btn_preview.setText("Edit")
            self.btn_preview.setProperty("active", "true")
        else:
            self.btn_preview.setText("Preview")
            self.btn_preview.setProperty("active", "false")
        self.btn_preview.style().polish(self.btn_preview)
        self.preview_toggled.emit(self.is_preview_mode)
