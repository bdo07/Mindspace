"""About dialog displaying app information, philosophy, and keyboard shortcuts."""

import sys
from pathlib import Path

 
_project_root = str(Path(__file__).resolve().parent.parent.parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from mindspace import __version__
from mindspace.ui.assets.icons import render_svg_pixmap
from mindspace.ui.themes.theme_manager import ThemeManager


class AboutDialog(QDialog):
    """About Mindspace window."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About MINDSPACE")
        self.setFixedSize(480, 430)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)
 
        header_layout = QHBoxLayout()
        header_layout.setSpacing(14)

        logo_lbl = QLabel(self)
        accent_color = ThemeManager.instance().get_color("accent")
        logo_lbl.setPixmap(render_svg_pixmap("logo", color=accent_color, size=42))
        header_layout.addWidget(logo_lbl)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        app_title = QLabel("MINDSPACE", self)
        app_title.setProperty("class", "aboutTitle")
        title_col.addWidget(app_title)

        version_lbl = QLabel(f"Version {__version__} — Your Personal Space", self)
        version_lbl.setProperty("class", "aboutVersion")
        title_col.addWidget(version_lbl)

        header_layout.addLayout(title_col)
        header_layout.addStretch()
        layout.addLayout(header_layout)
 
        desc_lbl = QLabel(
            "A minimalist personal productivity sanctuary combining notes, tasks, "
            "quick thoughts, favorites, and organization. Built with Python 3, PySide6, "
            "and local SQLite for complete offline privacy.",
            self,
        )
        desc_lbl.setProperty("class", "dialogDesc")
        desc_lbl.setWordWrap(True)
        layout.addWidget(desc_lbl)

        
        sc_card = QFrame(self)
        sc_card.setProperty("class", "shortcutCard")
        sc_layout = QGridLayout(sc_card)
        sc_layout.setContentsMargins(12, 10, 12, 10)
        sc_layout.setSpacing(6)

        shortcuts = [
            ("Ctrl / Cmd + N", "New Note"),
            ("Ctrl / Cmd + F", "Quick Search"),
            ("Ctrl / Cmd + S", "Save Note Immediately"),
            ("Ctrl / Cmd + Q", "Quit Application"),
        ]

        for idx, (key, desc) in enumerate(shortcuts):
            k_lbl = QLabel(key, sc_card)
            k_lbl.setProperty("class", "shortcutKey")
            d_lbl = QLabel(desc, sc_card)
            d_lbl.setProperty("class", "shortcutDesc")
            sc_layout.addWidget(k_lbl, idx, 0)
            sc_layout.addWidget(d_lbl, idx, 1)

        layout.addWidget(sc_card)
        layout.addStretch()

         
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("Done", self)
        close_btn.setProperty("class", "primaryBtn")
        close_btn.setFixedHeight(34)
        close_btn.setFixedWidth(80)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)


if __name__ == "__main__":
    app = QApplication.instance() or QApplication(sys.argv)
    ThemeManager.instance().apply_theme("light")
    dialog = AboutDialog()
    dialog.show()
    sys.exit(app.exec())
