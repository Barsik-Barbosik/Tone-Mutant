"""Native Qt keyboard helpers shared by nonmodal editor windows."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction


def enable_escape_to_close(window):
    action = QAction(window)
    action.setShortcut("Escape")
    action.setShortcutContext(Qt.WindowShortcut)
    action.triggered.connect(window.close)
    window.addAction(action)
