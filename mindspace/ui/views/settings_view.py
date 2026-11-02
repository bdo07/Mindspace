"""Settings view for theme, auto-save delay, database backup & restore."""

from pathlib import Path
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from mindspace import __version__
from mindspace.services.backup_service import BackupService
from mindspace.services.settings_service import SettingsService
from mindspace.ui.assets.icons import get_icon, render_svg_pixmap
from mindspace.ui.dialogs.about_dialog import AboutDialog
from mindspace.ui.dialogs.confirm_dialog import ConfirmDialog
from mindspace.ui.themes.theme_manager import ThemeManager


class SettingsView(QWidget):
    """Application preferences and database management."""

    theme_changed_signal = Signal(str)
    database_restored = Signal()

    def __init__(
        self,
        settings_service: SettingsService,
        backup_service: BackupService,
        parent=None,
    ):
        super().__init__(parent)
        self.settings_service = settings_service
        self.backup_service = backup_service

        self._setup_ui()
        self._update_icons()
        ThemeManager.instance().theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self, theme_name: str = ""):
        try:
            self._update_icons()
            self.refresh()
            if hasattr(self, "theme_combo") and theme_name:
                self.theme_combo.blockSignals(True)
                self.theme_combo.setCurrentIndex(1 if theme_name == "dark" else 0)
                self.theme_combo.blockSignals(False)
        except RuntimeError:
            pass

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(14)

        # Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(2)

        title = QLabel("Settings", self)
        title.setObjectName("pageTitle")
        header_layout.addWidget(title)

        subtitle = QLabel("Personalize your workspace, preferences, and local data.", self)
        subtitle.setObjectName("pageSubtitle")
        header_layout.addWidget(subtitle)

        main_layout.addLayout(header_layout)

        # Scroll area for settings sections
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(0, 4, 0, 16)
        c_layout.setSpacing(18)

        # 1. Appearance Section
        c_layout.addWidget(self._create_section_title("APPEARANCE"))
        theme_card = self._create_card()
        tc_layout = QGridLayout(theme_card)
        tc_layout.setContentsMargins(16, 14, 16, 14)
        tc_layout.setSpacing(12)

        t_lbl = QLabel("Color Theme", theme_card)
        t_lbl.setProperty("class", "settingTitle")
        t_desc = QLabel("Choose between a warm light canvas and an eye-friendly dark mode.", theme_card)
        t_desc.setProperty("class", "settingDesc")

        t_text_box = QVBoxLayout()
        t_text_box.addWidget(t_lbl)
        t_text_box.addWidget(t_desc)
        tc_layout.addLayout(t_text_box, 0, 0)

        self.theme_combo = QComboBox(theme_card)
        self.theme_combo.setProperty("class", "standardInput")
        self.theme_combo.setFixedHeight(34)
        self.theme_combo.setMinimumWidth(150)
        self.theme_combo.addItem("Light Canvas", userData="light")
        self.theme_combo.addItem("Dark Charcoal", userData="dark")

        current_theme = self.settings_service.get_settings().theme
        self.theme_combo.setCurrentIndex(1 if current_theme == "dark" else 0)
        self.theme_combo.currentIndexChanged.connect(self._on_theme_select)
        tc_layout.addWidget(self.theme_combo, 0, 1, Qt.AlignRight)

        # Startup View
        v_lbl = QLabel("Default Startup View", theme_card)
        v_lbl.setProperty("class", "settingTitle")
        v_desc = QLabel("Select which view opens automatically when starting Mindspace.", theme_card)
        v_desc.setProperty("class", "settingDesc")

        v_text_box = QVBoxLayout()
        v_text_box.addWidget(v_lbl)
        v_text_box.addWidget(v_desc)
        tc_layout.addLayout(v_text_box, 1, 0)

        self.startup_combo = QComboBox(theme_card)
        self.startup_combo.setProperty("class", "standardInput")
        self.startup_combo.setFixedHeight(34)
        self.startup_combo.setMinimumWidth(150)
        self.startup_combo.addItem("All Notes", userData="notes")
        self.startup_combo.addItem("Quick Notes", userData="quick")
        self.startup_combo.addItem("Tasks", userData="tasks")
        self.startup_combo.addItem("Favorites", userData="favorites")

        default_v = self.settings_service.get_settings().default_view
        for i in range(self.startup_combo.count()):
            if self.startup_combo.itemData(i) == default_v:
                self.startup_combo.setCurrentIndex(i)
                break
        self.startup_combo.currentIndexChanged.connect(self._on_startup_view_select)
        tc_layout.addWidget(self.startup_combo, 1, 1, Qt.AlignRight)

        c_layout.addWidget(theme_card)

        # 2. Editor & Auto-Save Section
        c_layout.addWidget(self._create_section_title("EDITOR & AUTO-SAVE"))
        editor_card = self._create_card()
        ec_layout = QGridLayout(editor_card)
        ec_layout.setContentsMargins(16, 14, 16, 14)
        ec_layout.setSpacing(12)

        as_lbl = QLabel("Auto-Save Frequency", editor_card)
        as_lbl.setProperty("class", "settingTitle")
        as_desc = QLabel("Notes are automatically saved locally as you write without losing focus.", editor_card)
        as_desc.setProperty("class", "settingDesc")

        as_box = QVBoxLayout()
        as_box.addWidget(as_lbl)
        as_box.addWidget(as_desc)
        ec_layout.addLayout(as_box, 0, 0)

        self.autosave_combo = QComboBox(editor_card)
        self.autosave_combo.setProperty("class", "standardInput")
        self.autosave_combo.setFixedHeight(34)
        self.autosave_combo.setMinimumWidth(150)
        self.autosave_combo.addItem("Fast (400 ms)", userData=400)
        self.autosave_combo.addItem("Normal (600 ms)", userData=600)
        self.autosave_combo.addItem("Relaxed (1200 ms)", userData=1200)

        current_delay = self.settings_service.get_settings().auto_save_delay_ms
        for i in range(self.autosave_combo.count()):
            if self.autosave_combo.itemData(i) == current_delay:
                self.autosave_combo.setCurrentIndex(i)
                break
        self.autosave_combo.currentIndexChanged.connect(self._on_autosave_select)
        ec_layout.addWidget(self.autosave_combo, 0, 1, Qt.AlignRight)

        c_layout.addWidget(editor_card)

        # 3. Database & Backup Section
        c_layout.addWidget(self._create_section_title("LOCAL DATA & BACKUP"))
        backup_card = self._create_card()
        bc_layout = QVBoxLayout(backup_card)
        bc_layout.setContentsMargins(16, 14, 16, 14)
        bc_layout.setSpacing(12)

        self.stats_lbl = QLabel(backup_card)
        self.stats_lbl.setProperty("class", "statsText")
        bc_layout.addWidget(self.stats_lbl)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.export_btn = QPushButton("Export Backup...", backup_card)
        self.export_btn.setProperty("class", "secondaryBtn")
        self.export_btn.setFixedHeight(32)
        self.export_btn.setCursor(Qt.PointingHandCursor)
        self.export_btn.clicked.connect(self._on_export_backup)
        btn_row.addWidget(self.export_btn)

        self.restore_btn = QPushButton("Restore Backup...", backup_card)
        self.restore_btn.setProperty("class", "secondaryBtn")
        self.restore_btn.setFixedHeight(32)
        self.restore_btn.setCursor(Qt.PointingHandCursor)
        self.restore_btn.clicked.connect(self._on_restore_backup)
        btn_row.addWidget(self.restore_btn)

        btn_row.addStretch()
        bc_layout.addLayout(btn_row)
        c_layout.addWidget(backup_card)

        # 4. About Section
        c_layout.addWidget(self._create_section_title("ABOUT"))
        about_card = self._create_card()
        ac_layout = QHBoxLayout(about_card)
        ac_layout.setContentsMargins(16, 14, 16, 14)

        info_box = QVBoxLayout()
        info_box.setSpacing(2)
        app_name_lbl = QLabel(f"MINDSPACE v{__version__}", about_card)
        app_name_lbl.setProperty("class", "settingTitle")
        tech_lbl = QLabel("Modern desktop productivity sanctuary built with Python 3, PySide6 & SQLite.", about_card)
        tech_lbl.setProperty("class", "settingDesc")
        info_box.addWidget(app_name_lbl)
        info_box.addWidget(tech_lbl)
        ac_layout.addLayout(info_box, 1)

        self.shortcuts_btn = QPushButton("Shortcuts Guide", about_card)
        self.shortcuts_btn.setProperty("class", "secondaryBtn")
        self.shortcuts_btn.setFixedHeight(32)
        self.shortcuts_btn.setCursor(Qt.PointingHandCursor)
        self.shortcuts_btn.clicked.connect(self._show_about_dialog)
        ac_layout.addWidget(self.shortcuts_btn)

        c_layout.addWidget(about_card)
        c_layout.addStretch()

        scroll.setWidget(container)
        main_layout.addWidget(scroll, 1)

    def _create_section_title(self, text: str) -> QLabel:
        lbl = QLabel(text, self)
        lbl.setProperty("class", "sectionHeader")
        return lbl

    def _create_card(self) -> QFrame:
        card = QFrame(self)
        card.setProperty("class", "noteCard")
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        return card

    def refresh(self):
        """Refreshes database statistics."""
        stats = self.backup_service.get_stats()
        kb_size = max(1, stats["file_size"] // 1024)
        self.stats_lbl.setText(
            f"<b>Database location:</b> {self.backup_service.db.db_path}<br>"
            f"<b>Notes:</b> {stats['active_notes']} active, {stats['archived_notes']} archived &nbsp;•&nbsp; "
            f"<b>Tasks:</b> {stats['total_tasks']} &nbsp;•&nbsp; "
            f"<b>Categories:</b> {stats['total_categories']} &nbsp;•&nbsp; "
            f"<b>Storage:</b> {kb_size} KB"
        )

    def _on_theme_select(self, idx: int):
        theme_val = self.theme_combo.currentData()
        self.settings_service.set_theme(theme_val)
        ThemeManager.instance().apply_theme(theme_val)
        self.theme_changed_signal.emit(theme_val)

    def _on_startup_view_select(self, idx: int):
        view_val = self.startup_combo.currentData()
        self.settings_service.set_default_view(view_val)

    def _on_autosave_select(self, idx: int):
        delay = self.autosave_combo.currentData()
        self.settings_service.set_auto_save_delay(delay)

    def _on_export_backup(self):
        default_name = f"mindspace_backup_{Path(self.backup_service.db.db_path).stem}.db"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Mindspace Backup",
            str(Path.home() / default_name),
            "SQLite Database (*.db);;All Files (*)",
        )
        if file_path:
            success, msg = self.backup_service.export_backup(file_path)
            self.refresh()

    def _on_restore_backup(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Backup to Restore",
            str(Path.home()),
            "SQLite Database (*.db);;All Files (*)",
        )
        if not file_path:
            return

        is_valid, msg = self.backup_service.validate_backup(file_path)
        if not is_valid:
            ConfirmDialog.ask(
                self,
                title="Invalid Backup",
                message=msg,
                confirm_label="OK",
                is_danger=True,
            )
            return

        confirmed = ConfirmDialog.ask(
            self,
            title="Confirm Database Restore",
            message="Restoring from this backup will overwrite current notes, tasks, and categories. Proceed?",
            confirm_label="Restore",
            is_danger=True,
        )
        if confirmed:
            ok, res_msg = self.backup_service.restore_backup(file_path)
            if ok:
                self.refresh()
                self.database_restored.emit()

    def _show_about_dialog(self):
        dlg = AboutDialog(parent=self)
        dlg.exec()

    def _update_icons(self):
        try:
            theme = ThemeManager.instance()
            icon_color = theme.get_color("icon")
            self.export_btn.setIcon(get_icon("backup", color=icon_color, size=14))
            self.restore_btn.setIcon(get_icon("restore", color=icon_color, size=14))
            self.shortcuts_btn.setIcon(get_icon("info", color=icon_color, size=14))
        except RuntimeError:
            pass
