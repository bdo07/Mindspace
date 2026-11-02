"""Debounce utility for PySide6 using QTimer."""

from typing import Callable
from PySide6.QtCore import QObject, QTimer


class Debouncer(QObject):
    """Executes a callback only after a delay has elapsed since the last invocation."""

    def __init__(self, delay_ms: int = 500, callback: Callable = None, parent: QObject = None):
        super().__init__(parent)
        self.delay_ms = delay_ms
        self.callback = callback
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._handle_timeout)
        self._args = ()
        self._kwargs = {}

    def call(self, *args, **kwargs):
        """Reset the timer and store latest arguments."""
        self._args = args
        self._kwargs = kwargs
        self._timer.start(self.delay_ms)

    def trigger_now(self):
        """Immediately triggers callback if timer is pending."""
        if self._timer.isActive():
            self._timer.stop()
            self._handle_timeout()

    def cancel(self):
        """Cancels any pending callback."""
        self._timer.stop()

    def set_delay(self, delay_ms: int):
        self.delay_ms = delay_ms

    def _handle_timeout(self):
        if self.callback:
            self.callback(*self._args, **self._kwargs)

