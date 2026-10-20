from ui.i18n import tr
from PySide6 import QtCore
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

from utils.utils import resource_path


class ChangeInstrumentWindow(QDialog):
    def __init__(self, parent, message, button_text):
        super().__init__()
        self.core = parent
        self.setWindowTitle(tr("Open Tone (JSON)"))
        self.setWindowIcon(QIcon(resource_path("resources/note.png")))

        layout = QVBoxLayout()

        self.add_title(layout)

        label = QLabel(tr(message))
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setTextFormat(QtCore.Qt.RichText)
        layout.addWidget(label)

        ok_button = QPushButton(tr(button_text))
        ok_button.setIcon(QIcon(resource_path("resources/apply.png")))
        ok_button.setObjectName("random-button")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

        self.setLayout(layout)

    @staticmethod
    def add_title(layout):
        label = QLabel()
        label.setText(tr("<h2>Open Tone (JSON)</h2>"))
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)
