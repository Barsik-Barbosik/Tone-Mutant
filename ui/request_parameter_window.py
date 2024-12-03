from PySide2 import QtCore
from PySide2.QtGui import QIcon, QIntValidator
from PySide2.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QFormLayout, QMessageBox

from utils.utils import resource_path


class RequestParameterWindow(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.setWindowTitle("Request Parameter")
        self.setWindowIcon(QIcon(resource_path("resources/get.png")))

        self.core = parent.core

        layout = QVBoxLayout()
        label = QLabel("Request a parameter from the synthesizer.\nThe result will appear in the \"Log\" tab.")
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)

        form_layout = QFormLayout()

        self.number_input = QLineEdit()
        self.number_input.setPlaceholderText("Number... (0-255?)")
        self.number_input.setValidator(QIntValidator(0, 255, self))
        form_layout.addRow("Number:", self.number_input)

        self.block_input = QLineEdit()
        self.block_input.setPlaceholderText("Block... (0-7?)")
        self.block_input.setValidator(QIntValidator(0, 7, self))
        form_layout.addRow("Block:", self.block_input)

        layout.addLayout(form_layout)

        self.submit_button = QPushButton("Get!")
        self.submit_button.setIcon(QIcon(resource_path("resources/apply.png")))
        self.submit_button.clicked.connect(self.on_submit)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)
        self.show()

    def on_submit(self):
        try:
            number = int(self.number_input.text())
            block = int(self.block_input.text())
            self.core.request_custom_parameter(number, block)
        except ValueError:
            QMessageBox.warning(self, "Input Error",
                                "The \"Number\" and \"Block\" fields must contain a valid integers.")
            return
