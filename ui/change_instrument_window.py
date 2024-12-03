from PySide2 import QtCore
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

from utils.utils import resource_path


class ChangeInstrumentWindow(QDialog):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pause: parent tone selection")
        self.setWindowIcon(QIcon(resource_path("resources/note.png")))

        layout = QVBoxLayout()
        label = QLabel(text)
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setTextFormat(QtCore.Qt.RichText)
        layout.addWidget(label)

        ok_button = QPushButton(" Continue")
        ok_button.setIcon(QIcon(resource_path("resources/apply.png")))
        ok_button.setObjectName("random-button")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

        self.setLayout(layout)
