from collections import deque

from PySide2.QtCore import QThreadPool, Signal, Qt
from PySide2.QtWidgets import QTextBrowser, QAction, QMenu

from constants.constants import LOG_MAX_LEN
from syntax_highlighters.sysex_highlighter import SysexHighlighter


class DequeLog(QTextBrowser):
    update_log_signal = Signal()

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.log_queue = deque(maxlen=LOG_MAX_LEN)
        self.threadpool = QThreadPool()

        self.setObjectName("log-textbox")
        SysexHighlighter(self.document())

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

        self.clear_action = QAction("Clear", self)
        self.clear_action.triggered.connect(self._clear_content)

        self.context_menu = QMenu(self)
        self.context_menu.addAction(self.clear_action)

        self.update_log_signal.connect(self._update_log)

    def log(self, message: str):
        self.log_queue.append(message)
        self.update_log_signal.emit()

    def _update_log(self):
        while True:
            message = self._get_message()
            if message is not None:
                self.append(message)
                self._apply_log_limit()
            else:
                break
        # self.moveCursor(self.textCursor().End)

    def _get_message(self):
        try:
            return self.log_queue.popleft()
        except IndexError:
            return None

    def _apply_log_limit(self):
        while self.document().blockCount() > LOG_MAX_LEN:
            cursor = self.textCursor()
            cursor.movePosition(cursor.Start)
            cursor.select(cursor.BlockUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar()

    def _show_context_menu(self, pos):
        self.context_menu.clear()

        default_menu = self.createStandardContextMenu()
        actions = default_menu.actions()
        for action in actions:
            self.context_menu.addAction(action)

        self.context_menu.addSeparator()
        self.context_menu.addAction(self.clear_action)

        self.context_menu.exec_(self.mapToGlobal(pos))

    def _clear_content(self):
        self.clear()
