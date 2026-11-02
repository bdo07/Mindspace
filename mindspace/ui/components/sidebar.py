"""Sidebar navigation component for MINDSPACE with responsive collapse support."""

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
    """Left sidebar for primary navigation, categories, and settings with responsive collapse support."""

    nav_changed = Signal(str)  # 'notes', 'quick', 'tasks', 'favorites', 'archived', 'settings', 'category:<id>'
    add_category_clicked = Signal()
    theme_toggle_clicked = Signal()
    collapse_toggled = Signal(bool)

    EXPANDED_WIDTH = 220
    COLLAPSED_WIDTH = 60

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebarContainer")
        self.setFixedWidth(self.EXPANDED_WIDTH)

        self.is_collapsed = False
        self._active_key = "notes"
        self._nav_buttons: Dict[str, QPushButton] = {}
        self._nav_labels: Dict[str, QLabel] = {}
        self._badge_labels: Dict[str, QLabel] = {}
        self._category_buttons: Dict[int, QPushButton] = {}
        self._category_labels: Dict[int, QLabel] = {}
        self._category_badges: Dict[int, QLabel] = {}

        self._setup_ui()
        self._update_theme_elements()
        ThemeManager.instance().theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self, theme_name: str = ""):
        try:
            self._update_theme_elements()
        except RuntimeError:
            pass

    def _setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 14, 10, 14)
        self.main_layout.setSpacing(4)

        # 1. Header (Logo + Brand + Collapse Toggle)
        self.brand_container = QWidget(self)
        self.brand_container.setStyleSheet("background: transparent;")
        brand_layout = QHBoxLayout(self.brand_container)
        brand_layout.setContentsMargins(4, 2, 4, 10)
        brand_layout.setSpacing(8)

        self.logo_label = QLabel(self.brand_container)
        self.logo_label.setFixedSize(26, 26)
        self.logo_label.setCursor(Qt.PointingHandCursor)
        brand_layout.addWidget(self.logo_label)

        self.brand_text_widget = QWidget(self.brand_container)
        self.brand_text_widget.setStyleSheet("background: transparent;")
        brand_text_layout = QVBoxLayout(self.brand_text_widget)
        brand_text_layout.setContentsMargins(0, 0, 0, 0)
        brand_text_layout.setSpacing(0)

        self.app_title = QLabel("MINDSPACE", self.brand_text_widget)
        self.app_title.setObjectName("appTitle")
        brand_text_layout.addWidget(self.app_title)

        self.app_subtitle = QLabel("Personal Space", self.brand_text_widget)
        self.app_subtitle.setObjectName("appSubtitle")
        brand_text_layout.addWidget(self.app_subtitle)

        brand_layout.addWidget(self.brand_text_widget, 1)

        self.toggle_btn = QPushButton(self.brand_container)
        self.toggle_btn.setProperty("class", "iconBtn")
        self.toggle_btn.setFixedSize(26, 26)
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.setToolTip("Collapse / Expand Sidebar")
        self.toggle_btn.clicked.connect(self.toggle_collapse)
        brand_layout.addWidget(self.toggle_btn)

        self.main_layout.addWidget(self.brand_container)

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
            self.main_layout.addWidget(btn)

        # 3. Categories section
        self.cat_header_widget = QWidget(self)
        self.cat_header_widget.setStyleSheet("background: transparent;")
        cat_header_layout = QHBoxLayout(self.cat_header_widget)
        cat_header_layout.setContentsMargins(4, 10, 4, 2)

        self.cat_title = QLabel("CATEGORIES", self.cat_header_widget)
        self.cat_title.setObjectName("sidebarSectionTitle")
        cat_header_layout.addWidget(self.cat_title)
        cat_header_layout.addStretch()

        self.add_cat_btn = QPushButton(self.cat_header_widget)
        self.add_cat_btn.setProperty("class", "iconBtn")
        self.add_cat_btn.setFixedSize(22, 22)
        self.add_cat_btn.setToolTip("Add Category")
        self.add_cat_btn.setCursor(Qt.PointingHandCursor)
        self.add_cat_btn.clicked.connect(self.add_category_clicked.emit)
        cat_header_layout.addWidget(self.add_cat_btn)

        self.main_layout.addWidget(self.cat_header_widget)

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
        self.main_layout.addWidget(self.cat_scroll, 1)

        # 4. Footer: Theme Toggle & Settings
        self.footer_widget = QWidget(self)
        self.footer_widget.setStyleSheet("background: transparent;")
        footer_layout = QVBoxLayout(self.footer_widget)
        footer_layout.setContentsMargins(0, 4, 0, 0)
        footer_layout.setSpacing(3)

        self.theme_btn = QPushButton(self.footer_widget)
        self.theme_btn.setProperty("class", "sidebarNavBtn")
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.setFixedHeight(34)
        self.theme_btn_layout = QHBoxLayout(self.theme_btn)
        self.theme_btn_layout.setContentsMargins(8, 0, 8, 0)
        self.theme_btn_layout.setSpacing(8)

        self.theme_icon_lbl = QLabel(self.theme_btn)
        self.theme_icon_lbl.setFixedSize(16, 16)
        self.theme_icon_lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.theme_btn_layout.addWidget(self.theme_icon_lbl)

        self.theme_text_lbl = QLabel("Theme", self.theme_btn)
        self.theme_text_lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.theme_text_lbl.setStyleSheet("background: transparent; font-weight: inherit; color: inherit;")
        self.theme_btn_layout.addWidget(self.theme_text_lbl, 1)

        self.theme_btn.clicked.connect(self.theme_toggle_clicked.emit)
        footer_layout.addWidget(self.theme_btn)

        self.settings_btn = self._create_nav_button("settings", "Settings", "settings", has_badge=False)
        footer_layout.addWidget(self.settings_btn)

        self.main_layout.addWidget(self.footer_widget)

    def _create_nav_button(self, key: str, label: str, icon_name: str, has_badge: bool = True) -> QPushButton:
        btn = QPushButton(self)
        btn.setProperty("class", "sidebarNavBtn")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setProperty("nav_key", key)
        btn.setProperty("icon_name", icon_name)
        btn.setFixedHeight(34)
        btn.setToolTip(label)

        btn_layout = QHBoxLayout(btn)
        btn_layout.setContentsMargins(8, 0, 8, 0)
        btn_layout.setSpacing(8)

        icon_lbl = QLabel(btn)
        icon_lbl.setFixedSize(16, 16)
        icon_lbl.setAttribute(Qt.WA_TransparentForMouseEvents)
        btn.setProperty("icon_label", icon_lbl)
        btn_layout.addWidget(icon_lbl)

        text_label = QLabel(label, btn)
        text_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        text_label.setStyleSheet("background: transparent; font-weight: inherit; color: inherit;")
        btn_layout.addWidget(text_label, 1)
        self._nav_labels[key] = text_label

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
        for btn in self._category_buttons.values():
            self.cat_layout.removeWidget(btn)
            btn.deleteLater()
        self._category_buttons.clear()
        self._category_labels.clear()
        self._category_badges.clear()

        while self.cat_layout.count():
            item = self.cat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        note_counts = note_counts or {}

        for cat in categories:
            btn = QPushButton(self.cat_container)
            btn.setProperty("class", "sidebarNavBtn")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(30)
            btn.setToolTip(f"{cat.name} ({note_counts.get(cat.id, 0)} notes)")

            layout = QHBoxLayout(btn)
            layout.setContentsMargins(8, 0, 8, 0)
            layout.setSpacing(8)

            # Colored category dot
            dot = QLabel(btn)
            dot.setFixedSize(8, 8)
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
            name_lbl.setVisible(not self.is_collapsed)
            self._category_labels[cat.id] = name_lbl

            # Count badge
            cnt = note_counts.get(cat.id, 0)
            cnt_badge = QLabel(str(cnt), btn)
            cnt_badge.setProperty("class", "badge")
            cnt_badge.setFixedHeight(18)
            cnt_badge.setAttribute(Qt.WA_TransparentForMouseEvents)
            layout.addWidget(cnt_badge)
            cnt_badge.setVisible(not self.is_collapsed)
            self._category_badges[cat.id] = cnt_badge

            cat_key = f"category:{cat.id}"
            btn.clicked.connect(lambda checked=False, k=cat_key: self._on_btn_clicked(k))
            self.cat_layout.addWidget(btn)
            self._category_buttons[cat.id] = btn

        self.cat_layout.addStretch()

    def toggle_collapse(self):
        self.set_collapsed(not self.is_collapsed)

    def set_collapsed(self, collapsed: bool):
        self.is_collapsed = collapsed
        self.setFixedWidth(self.COLLAPSED_WIDTH if collapsed else self.EXPANDED_WIDTH)

        # Show/Hide brand texts
        self.brand_text_widget.setVisible(not collapsed)
        self.cat_header_widget.setVisible(not collapsed)
        self.theme_text_lbl.setVisible(not collapsed)

        # Show/Hide nav labels and badges
        for lbl in self._nav_labels.values():
            lbl.setVisible(not collapsed)
        for badge in self._badge_labels.values():
            badge.setVisible(not collapsed)

        # Show/Hide category labels and badges
        for lbl in self._category_labels.values():
            lbl.setVisible(not collapsed)
        for badge in self._category_badges.values():
            badge.setVisible(not collapsed)

        self._update_theme_elements()
        self.collapse_toggled.emit(self.is_collapsed)

    def _update_theme_elements(self):
        try:
            theme = ThemeManager.instance()
            accent = theme.get_color("accent")
            icon_color = theme.get_color("icon")

            # Logo
            self.logo_label.setPixmap(render_svg_pixmap("logo", color=accent, size=22))

            # Collapse button icon
            toggle_icon = "sidebar-expand" if self.is_collapsed else "sidebar-toggle"
            self.toggle_btn.setIcon(get_icon(toggle_icon, color=icon_color, size=15))

            # Add category plus icon
            self.add_cat_btn.setIcon(get_icon("plus", color=icon_color, size=14))

            # Nav icons
            for key, btn in self._nav_buttons.items():
                icon_name = btn.property("icon_name")
                icon_lbl = btn.property("icon_label")
                if icon_name and icon_lbl:
                    icon_lbl.setPixmap(render_svg_pixmap(icon_name, color=icon_color, size=16))

            # Theme button icon & label
            if theme.is_dark:
                self.theme_text_lbl.setText("Light Mode")
                self.theme_icon_lbl.setPixmap(render_svg_pixmap("sun", color=icon_color, size=16))
                self.theme_btn.setToolTip("Switch to Light Mode")
            else:
                self.theme_text_lbl.setText("Dark Mode")
                self.theme_icon_lbl.setPixmap(render_svg_pixmap("moon", color=icon_color, size=16))
                self.theme_btn.setToolTip("Switch to Dark Mode")
        except RuntimeError:
            pass
