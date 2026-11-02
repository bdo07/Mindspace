"""Settings data models and defaults."""

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class AppSettings:
    """Application user preferences."""

    theme: str = "light"  # 'light' or 'dark'
    auto_save_delay_ms: int = 600
    default_view: str = "notes"  # 'notes', 'quick', 'tasks', 'favorites'
    editor_font_size: int = 14
    editor_font_family: str = "Inter"
    show_markdown_preview: bool = False
    window_width: int = 1180
    window_height: int = 760

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AppSettings":
        instance = cls()
        if "theme" in data:
            instance.theme = data["theme"]
        if "auto_save_delay_ms" in data:
            instance.auto_save_delay_ms = int(data["auto_save_delay_ms"])
        if "default_view" in data:
            instance.default_view = data["default_view"]
        if "editor_font_size" in data:
            instance.editor_font_size = int(data["editor_font_size"])
        if "editor_font_family" in data:
            instance.editor_font_family = data["editor_font_family"]
        if "show_markdown_preview" in data:
            val = data["show_markdown_preview"]
            instance.show_markdown_preview = val in (True, 1, "1", "true", "True")
        if "window_width" in data:
            instance.window_width = int(data["window_width"])
        if "window_height" in data:
            instance.window_height = int(data["window_height"])
        return instance

    def to_dict(self) -> Dict[str, str]:
        return {
            "theme": self.theme,
            "auto_save_delay_ms": str(self.auto_save_delay_ms),
            "default_view": self.default_view,
            "editor_font_size": str(self.editor_font_size),
            "editor_font_family": self.editor_font_family,
            "show_markdown_preview": "1" if self.show_markdown_preview else "0",
            "window_width": str(self.window_width),
            "window_height": str(self.window_height),
        }

