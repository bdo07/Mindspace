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
            "background": "#161618" if dark else "#F7F6F2",
            "surface": "#1E1E22" if dark else "#FFFFFF",
            "sidebar": "#121214" if dark else "#EFECE6",
            "text": "#F2F2F5" if dark else "#1C1C1E",
            "text_secondary": "#9A9AA4" if dark else "#6E6E73",
            "text_muted": "#6C6C77" if dark else "#8E8E93",
            "accent": "#9887E8" if dark else "#7059C8",
            "accent_hover": "#AA9BF0" if dark else "#634DB8",
            "accent_light": "#2C2744" if dark else "#ECE8F9",
            "border": "#2C2C32" if dark else "#E5E2D9",
            "border_hover": "#3E3E48" if dark else "#C9C4B7",
            "icon": "#9A9AA4" if dark else "#6E6E73",
            "icon_active": "#9887E8" if dark else "#7059C8",
            "icon_gold": "#FFD43B" if dark else "#F59F00",
            "danger": "#FF6B6B" if dark else "#D63031",
            "success": "#51CF66" if dark else "#2B8A3E",
            "primary_btn_bg": "#7E69D6" if dark else "#7059C8",
            "primary_btn_text": "#FFFFFF",
            "swatch_border": "#FFFFFF" if dark else "#1C1C1E",
        }
        return colors.get(token, "#858585")

