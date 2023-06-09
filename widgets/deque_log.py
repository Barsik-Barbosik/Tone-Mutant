from collections import deque

from PySide2.QtCore import QThreadPool, Signal
from PySide2.QtWidgets import QTextBrowser

from external.sysex_highlighter import SysexHighlighter


class DequeLog(QTextBrowser):
    update_log_signal = Signal()

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.log_queue = deque()
        self.threadpool = QThreadPool()

        self.setObjectName("log-textbox")
        SysexHighlighter(self.document())

        self.update_log_signal.connect(self._update_log)

    def log(self, message: str):
        self.log_queue.append(message)
        self.update_log_signal.emit()

    def _update_log(self):
        while True:
            message = self._get_message()
            if message is not None:
                self.append(message)
            else:
                break

    def _get_message(self):
        try:
            return self.log_queue.popleft()
        except IndexError:
            return None
