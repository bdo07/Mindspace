"""Sidebar navigation component for MINDSPACE."""

from typing import Dict, List, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from mindspace.models.category import Category
from mindspace.ui.assets.icons import get_icon, render_svg_pixmap
from mindspace.ui.themes.theme_manager import ThemeManager


class Sidebar(QWidget):
    """Left sidebar for primary navigation, categories, and settings."""

    nav_changed = Signal(str)  # 'notes', 'quick', 'tasks', 'favorites', 'archived', 'settings', 'category:<id>'
    add_category_clicked = Signal()
    theme_toggle_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebarContainer")
        self.setFixedWidth(230)

        self._active_key = "notes"
        self._nav_buttons: Dict[str, QPushButton] = {}
        self._badge_labels: Dict[str, QLabel] = {}
        self._category_buttons: Dict[int, QPushButton] = {}

        self._setup_ui()
        self._update_theme_elements()
        ThemeManager.instance().theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self, theme_name: str = ""):
        try:
            self._update_theme_elements()
        except RuntimeError:
            pass

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 16, 12, 16)
        main_layout.setSpacing(6)

        # 1. Header (Logo + Brand)
        brand_layout = QHBoxLayout()
        brand_layout.setContentsMargins(8, 4, 8, 12)
        brand_layout.setSpacing(10)

        self.logo_label = QLabel(self)
        self.logo_label.setFixedSize(28, 28)
        brand_layout.addWidget(self.logo_label)

        brand_text_layout = QVBoxLayout()
        brand_text_layout.setSpacing(1)

        app_title = QLabel("MINDSPACE", self)
        app_title.setObjectName("appTitle")
        brand_text_layout.addWidget(app_title)

        app_subtitle = QLabel("Your Personal Space", self)
        app_subtitle.setObjectName("appSubtitle")
        brand_text_layout.addWidget(app_subtitle)

        brand_layout.addLayout(brand_text_layout)
        brand_layout.addStretch()
        main_layout.addLayout(brand_layout)

        # 2. Main Navigation items
        nav_items = [
            ("notes", "All Notes", "notes"),
            ("quick", "Quick Notes", "quick"),
            ("tasks", "Tasks", "tasks"),
            ("favorites", "Favorites", "favorites"),
            ("archived", "Archived", "archived"),
        ]

        for key, label, icon_name in nav_items:
            btn = self._create_nav_button(key, label, icon_name)
            main_layout.addWidget(btn)

        # 3. Categories section with scroll area
        cat_header_layout = QHBoxLayout()
        cat_header_layout.setContentsMargins(4, 10, 4, 2)

        cat_title = QLabel("CATEGORIES", self)
        cat_title.setObjectName("sidebarSectionTitle")
        cat_header_layout.addWidget(cat_title)
        cat_header_layout.addStretch()

        self.add_cat_btn = QPushButton(self)
        self.add_cat_btn.setProperty("class", "iconBtn")
        self.add_cat_btn.setFixedSize(22, 22)
        self.add_cat_btn.setToolTip("Add Category")
        self.add_cat_btn.setCursor(Qt.PointingHandCursor)
        self.add_cat_btn.clicked.connect(self.add_category_clicked.emit)
        cat_header_layout.addWidget(self.add_cat_btn)

        main_layout.addLayout(cat_header_layout)

        # Scrollable categories container
        self.cat_scroll = QScrollArea(self)
        self.cat_scroll.setWidgetResizable(True)
        self.cat_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.cat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.cat_container = QWidget()
        self.cat_container.setStyleSheet("background: transparent;")
        self.cat_layout = QVBoxLayout(self.cat_container)
        self.cat_layout.setContentsMargins(0, 0, 0, 0)
        self.cat_layout.setSpacing(2)
        self.cat_layout.addStretch()

        self.cat_scroll.setWidget(self.cat_container)
        main_layout.addWidget(self.cat_scroll, 1)

        # 4. Footer: Theme Toggle & Settings
        footer_layout = QVBoxLayout()
        footer_layout.setSpacing(4)

        self.theme_btn = QPushButton("Theme", self)
        self.theme_btn.setProperty("class", "sidebarNavBtn")
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.clicked.connect(self.theme_toggle_clicked.emit)
        footer_layout.addWidget(self.theme_btn)

        self.settings_btn = self._create_nav_button("settings", "Settings", "settings", has_badge=False)
        footer_layout.addWidget(self.settings_btn)

        main_layout.addLayout(footer_layout)

    def _create_nav_button(self, key: str, label: str, icon_name: str, has_badge: bool = True) -> QPushButton:
        btn = QPushButton(self)
        btn.setProperty("class", "sidebarNavBtn")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setProperty("nav_key", key)
        btn.setProperty("icon_name", icon_name)

        btn_layout = QHBoxLayout(btn)
        btn_layout.setContentsMargins(10, 6, 10, 6)
        btn_layout.setSpacing(8)

        text_label = QLabel(label, btn)
        text_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        text_label.setStyleSheet("background: transparent; font-weight: inherit; color: inherit;")
        btn_layout.addWidget(text_label, 1)

        if has_badge:
            badge = QLabel("0", btn)
            badge.setProperty("class", "badge")
            badge.setAlignment(Qt.AlignCenter)
            badge.setAttribute(Qt.WA_TransparentForMouseEvents)
            badge.setFixedHeight(18)
            btn_layout.addWidget(badge)
            self._badge_labels[key] = badge

        btn.clicked.connect(lambda: self._on_btn_clicked(key))
        self._nav_buttons[key] = btn
        return btn

    def _on_btn_clicked(self, key: str):
        self.set_active(key)
        self.nav_changed.emit(key)

    def set_active(self, key: str):
        """Updates visually active button."""
        self._active_key = key
        for k, btn in self._nav_buttons.items():
            is_active = (k == key)
            btn.setProperty("active", "true" if is_active else "false")
            btn.style().polish(btn)
            if k in self._badge_labels:
                badge = self._badge_labels[k]
                badge.setProperty("class", "badgeActive" if is_active else "badge")
                badge.style().polish(badge)

        # Clear category highlights if a main tab is active
        for cat_id, btn in self._category_buttons.items():
            is_active = (f"category:{cat_id}" == key)
            btn.setProperty("active", "true" if is_active else "false")
            btn.style().polish(btn)

    def update_counts(self, counts: Dict[str, int]):
        """Updates badge counts."""
        for key, count in counts.items():
            if key in self._badge_labels:
                self._badge_labels[key].setText(str(count))

    def set_categories(self, categories: List[Category], note_counts: Optional[Dict[int, int]] = None):
        """Rebuilds category button list."""
        # Clear existing category buttons
        for btn in self._category_buttons.values():
            self.cat_layout.removeWidget(btn)
            btn.deleteLater()
        self._category_buttons.clear()

        # Remove stretch item
        while self.cat_layout.count():
            item = self.cat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        note_counts = note_counts or {}
        theme = ThemeManager.instance()

        for cat in categories:
            btn = QPushButton(self.cat_container)
            btn.setProperty("class", "sidebarNavBtn")
            btn.setCursor(Qt.PointingHandCursor)

            layout = QHBoxLayout(btn)
            layout.setContentsMargins(10, 5, 10, 5)
            layout.setSpacing(8)

            # Colored category dot
            dot = QLabel(btn)
            dot.setFixedSize(9, 9)
            dot.setStyleSheet(f"""
                QLabel {{
                    background-color: {cat.color};
                    border-radius: 4px;
                }}
            """)
            layout.addWidget(dot)

            # Category name
            name_lbl = QLabel(cat.name, btn)
            name_lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
            name_lbl.setStyleSheet("background: transparent; font-weight: inherit; color: inherit;")
            layout.addWidget(name_lbl, 1)

            # Count badge
            cnt = note_counts.get(cat.id, 0)
            cnt_badge = QLabel(str(cnt), btn)
            cnt_badge.setProperty("class", "badge")
            cnt_badge.setFixedHeight(18)
            cnt_badge.setAttribute(Qt.WA_TransparentForMouseEvents)
            layout.addWidget(cnt_badge)

            cat_key = f"category:{cat.id}"
            btn.clicked.connect(lambda checked=False, k=cat_key: self._on_btn_clicked(k))
            self.cat_layout.addWidget(btn)
            self._category_buttons[cat.id] = btn

        self.cat_layout.addStretch()

    def _update_theme_elements(self):
        try:
            theme = ThemeManager.instance()
            accent = theme.get_color("accent")
            icon_color = theme.get_color("icon")

            # Logo
            self.logo_label.setPixmap(render_svg_pixmap("logo", color=accent, size=24))

            # Add category plus icon
            self.add_cat_btn.setIcon(get_icon("plus", color=icon_color, size=14))

            # Nav icons
            for key, btn in self._nav_buttons.items():
                icon_name = btn.property("icon_name")
                if icon_name:
                    btn.setIcon(get_icon(icon_name, color=icon_color, size=16))

            # Theme button icon & label
            if theme.is_dark:
                self.theme_btn.setText("Light Mode")
                self.theme_btn.setIcon(get_icon("sun", color=icon_color, size=16))
            else:
                self.theme_btn.setText("Dark Mode")
                self.theme_btn.setIcon(get_icon("moon", color=icon_color, size=16))
        except RuntimeError:
            pass
