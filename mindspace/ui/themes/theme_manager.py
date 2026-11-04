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
            "background": "#11170F" if dark else "#F7F8F4",
            "surface": "#202B1D" if dark else "#FFFFFF",
            "sidebar": "#182116" if dark else "#F0F2EB",
            "elevated": "#293725" if dark else "#FFFFFF",
            "text": "#F2F5ED" if dark else "#20251E",
            "text_secondary": "#A7B29F" if dark else "#777E73",
            "text_muted": "#6C7865" if dark else "#9AA295",
            "accent": "#97D7FF" if dark else "#15370D",
            "accent_hover": "#B5E3FF" if dark else "#1D4D13",
            "accent_light": "#1E3545" if dark else "#E8F0E4",
            "secondary_accent": "#F1A344",
            "secondary_accent_hover": "#FFB862" if dark else "#E09230",
            "secondary_accent_light": "#382713" if dark else "#FEF3E2",
            "soft_accent": "#97D7FF",
            "green_accent": "#6C9B59" if dark else "#15370D",
            "green_accent_hover": "#7EAF6B" if dark else "#1D4D13",
            "border": "#354331" if dark else "#E4E8DF",
            "border_hover": "#4D6047" if dark else "#C8CEC1",
            "icon": "#A7B29F" if dark else "#777E73",
            "icon_active": "#97D7FF" if dark else "#15370D",
            "icon_gold": "#F1A344",  # Warm Amber for favorites/stars
            "danger": "#FF6B6B" if dark else "#D63031",
            "success": "#6C9B59" if dark else "#15370D",
            "primary_btn_bg": "#97D7FF" if dark else "#15370D",
            "primary_btn_text": "#11170F" if dark else "#FFFFFF",
            "swatch_border": "#FFFFFF" if dark else "#15370D",
        }
        return colors.get(token, "#777E73")
