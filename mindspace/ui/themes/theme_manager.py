"""Theme manager handles switching between Light and Dark styles dynamically."""

from pathlib import Path
from typing import Dict
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

THEMES_DIR = Path(__file__).parent


class ThemeManager(QObject):
    """Manages application stylesheets, active theme, and theme change notifications."""

    theme_changed = Signal(str)

    _instance = None

    @classmethod
    def instance(cls) -> "ThemeManager":
        if cls._instance is None:
            cls._instance = ThemeManager()
        return cls._instance

    def __init__(self):
        super().__init__()
        self._current_theme = "light"
        self._cache: Dict[str, str] = {}
        self._load_stylesheets()

    def _load_stylesheets(self):
        for theme_name in ("light", "dark"):
            file_path = THEMES_DIR / f"{theme_name}.qss"
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    self._cache[theme_name] = f.read()

    @property
    def current_theme(self) -> str:
        return self._current_theme

    @property
    def is_dark(self) -> bool:
        return self._current_theme == "dark"

    def apply_theme(self, theme_name: str, app: QApplication = None):
        """Applies stylesheet for the specified theme to the application."""
        if theme_name not in ("light", "dark"):
            theme_name = "light"

        self._current_theme = theme_name
        stylesheet = self._cache.get(theme_name, "")

        target_app = app or QApplication.instance()
        if target_app:
            target_app.setStyleSheet(stylesheet)

        self.theme_changed.emit(theme_name)

    def toggle_theme(self, app: QApplication = None) -> str:
        new_theme = "dark" if self._current_theme == "light" else "light"
        self.apply_theme(new_theme, app)
        return new_theme

    def get_color(self, token: str) -> str:
        """Returns hex color code for the token in the current theme."""
        dark = self.is_dark
        colors = {
            "background": "#18181B" if dark else "#F7F6F2",
            "surface": "#212126" if dark else "#FFFFFF",
            "sidebar": "#131316" if dark else "#F0EFEA",
            "text": "#F3F3F5" if dark else "#202020",
            "text_secondary": "#9E9EA8" if dark else "#858585",
            "text_muted": "#72727D" if dark else "#9C9A94",
            "accent": "#9D8DE6" if dark else "#8B79D9",
            "accent_hover": "#B1A3F0" if dark else "#7967C7",
            "accent_light": "#322E47" if dark else "#F0EEFA",
            "border": "#2E2E38" if dark else "#EAE8E2",
            "border_hover": "#424250" if dark else "#CDC9BD",
            "icon": "#9E9EA8" if dark else "#7A7A80",
            "icon_active": "#9D8DE6" if dark else "#8B79D9",
            "icon_gold": "#FFD43B" if dark else "#E59900",
            "danger": "#FF6B6B" if dark else "#E03131",
            "success": "#51CF66" if dark else "#2B8A3E",
        }
        return colors.get(token, "#858585")

