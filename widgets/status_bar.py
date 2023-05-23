import threading

from PySide2.QtWidgets import QStatusBar


class StatusBar(QStatusBar):
    __instance = None
    __lock = threading.Lock()

    @staticmethod
    def get_instance():
        if StatusBar.__instance is None:
            with StatusBar.__lock:
                if StatusBar.__instance is None:
                    StatusBar()
        return StatusBar.__instance

    def __init__(self):
        if StatusBar.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            super().__init__()
            StatusBar.__instance = self

    def show_status_msg(self, text: str, msecs: int):
        self.setStyleSheet("background-color: white; color: black")
        self.showMessage(text, msecs)

    def show_error_msg(self, text: str):
        self.setStyleSheet("background-color: white; color: red")
        self.showMessage(text, 5000)
