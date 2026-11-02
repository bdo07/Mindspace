"""Application entry point for MINDSPACE."""

import sys
from pathlib import Path

# Ensure project root is on sys.path even when executed directly as a script
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication

from mindspace import __app_name__, __version__
from mindspace.ui.assets.icons import get_icon
from mindspace.ui.main_window import MainWindow


def main():
    """Main routine initializing and executing MINDSPACE."""
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName(__app_name__)
    app.setApplicationDisplayName("MINDSPACE — Your Personal Space")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("Mindspace")
    app.setOrganizationDomain("mindspace.app")

    # Set default clean system font
    font_family = ".AppleSystemUIFont" if sys.platform == "darwin" else "Segoe UI"
    default_font = QFont(font_family, 10)
    default_font.setStyleHint(QFont.SansSerif)
    app.setFont(default_font)

    # Set Window Icon
    app_icon = get_icon("logo", color="#8B79D9", size=64)
    app.setWindowIcon(app_icon)

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
