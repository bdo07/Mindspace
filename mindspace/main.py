"""Application entry point for MINDSPACE."""

import sys
from pathlib import Path
from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication

from mindspace import __app_name__, __version__
from mindspace.ui.assets.icons import get_icon
from mindspace.ui.main_window import MainWindow


def main():
    """Main routine initializing and executing MINDSPACE."""
    # Enable High DPI pixmaps and scaling
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName(__app_name__)
    app.setApplicationDisplayName("MINDSPACE — Your Personal Space")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("Mindspace")
    app.setOrganizationDomain("mindspace.app")

    # Set default clean system font
    default_font = QFont("-apple-system", 10)
    default_font.setStyleHint(QFont.SansSerif)
    app.setFont(default_font)

    # Set Window Icon
    app_icon = get_icon("logo", color="#8B79D9", size=64)
    app.setWindowIcon(app_icon)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

