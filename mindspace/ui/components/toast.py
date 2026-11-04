"""Toast notification overlay for Mindspace."""

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRect, QTimer, Qt
from PySide6.QtWidgets import QGraphicsOpacityEffect, QHBoxLayout, QLabel, QWidget


class Toast(QWidget):
    """Subtle floating notification toast for feedback messages."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.SubWindow | Qt.FramelessWindowHint | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(16, 10, 16, 10)

        self.label = QLabel("", self)
        self.label.setStyleSheet("""
            color: #FFFFFF;
            font-size: 13px;
            font-weight: 500;
        """)
        self._layout.addWidget(self.label)

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_anim = QPropertyAnimation(self.opacity_effect, b"opacity")

        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self._fade_out)

    def show_message(self, message: str, is_error: bool = False, duration_ms: int = 2600):
        self.label.setText(message)
        bg_color = "rgba(224, 49, 49, 0.95)" if is_error else "rgba(32, 32, 36, 0.92)"
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                border-radius: 8px;
            }}
        """)
        self.adjustSize()

        if self.parentWidget():
            parent_rect = self.parentWidget().rect()
            x = (parent_rect.width() - self.width()) // 2
            y = parent_rect.height() - self.height() - 32
            self.move(x, y)

        self.show()
        self.raise_()

         
        self.opacity_anim.stop()
        self.opacity_anim.setDuration(180)
        self.opacity_anim.setStartValue(0.0)
        self.opacity_anim.setEndValue(1.0)
        self.opacity_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.opacity_anim.start()

        self.hide_timer.start(duration_ms)

    def _fade_out(self):
        self.opacity_anim.stop()
        self.opacity_anim.setDuration(220)
        self.opacity_anim.setStartValue(1.0)
        self.opacity_anim.setEndValue(0.0)
        self.opacity_anim.setEasingCurve(QEasingCurve.InCubic)
        self.opacity_anim.finished.connect(self.hide)
        self.opacity_anim.start()

