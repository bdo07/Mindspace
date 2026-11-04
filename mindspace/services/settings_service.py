"""Service layer for Application Settings."""

from mindspace.database.repository import MindspaceRepository
from mindspace.models.settings import AppSettings


class SettingsService:
    """Manages reading and writing application settings."""

    def __init__(self, repo: MindspaceRepository):
        self.repo = repo
        self._cached_settings: AppSettings = self.get_settings()

    def get_settings(self) -> AppSettings:
        raw_dict = self.repo.get_settings()
        self._cached_settings = AppSettings.from_dict(raw_dict)
        return self._cached_settings


    def set_theme(self, theme: str) -> None:
        if theme not in ("light", "dark"):
            theme = "light"
        self.repo.update_setting("theme", theme)
        self._cached_settings.theme = theme

    def set_auto_save_delay(self, ms: int) -> None:
        ms = max(200, min(5000, ms))
        self.repo.update_setting("auto_save_delay_ms", str(ms))
        self._cached_settings.auto_save_delay_ms = ms

    def set_editor_font_size(self, size: int) -> None:
        size = max(10, min(32, size))
        self.repo.update_setting("editor_font_size", str(size))
        self._cached_settings.editor_font_size = size

    def set_default_view(self, view_name: str) -> None:
        self.repo.update_setting("default_view", view_name)
        self._cached_settings.default_view = view_name

    def set_window_geometry(self, width: int, height: int) -> None:
        self.repo.update_setting("window_width", str(width))
        self.repo.update_setting("window_height", str(height))
        self._cached_settings.window_width = width
        self._cached_settings.window_height = height

    def save_settings(self, settings: AppSettings) -> None:
        self.repo.update_settings(settings.to_dict())
        self._cached_settings = settings

