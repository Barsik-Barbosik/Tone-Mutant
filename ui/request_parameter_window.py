from PySide2 import QtCore
from PySide2.QtGui import QIcon, QIntValidator
from PySide2.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QFormLayout, QMessageBox

from utils.utils import resource_path


class RequestParameterWindow(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.setWindowTitle("Request Parameter")
        self.setWindowIcon(QIcon(resource_path("resources/request.png")))

        self.core = parent.core

        layout = QVBoxLayout()
        label = QLabel("Request a parameter from the synthesizer.\nThe result will appear in the 'Log' tab.")
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)

        form_layout = QFormLayout()

        self.number_input = QLineEdit()
        self.number_input.setPlaceholderText("Parameter Number...")
        self.number_input.setValidator(QIntValidator(0, 255, self))
        form_layout.addRow("Number:", self.number_input)

        self.block_input = QLineEdit()
        self.block_input.setPlaceholderText("Block...")
        self.block_input.setText("0")
        self.block_input.setValidator(QIntValidator(0, 7, self))
        form_layout.addRow("Block:", self.block_input)

        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Category... (0-65)")
        self.category_input.setValidator(QIntValidator(0, 65, self))
        self.category_input.setText("3")
        form_layout.addRow("Category:", self.category_input)

        self.memory_input = QLineEdit()
        self.memory_input.setPlaceholderText("Memory... (0-4)")
        self.memory_input.setValidator(QIntValidator(0, 4, self))
        self.memory_input.setText("3")
        form_layout.addRow("Memory Area ID:", self.memory_input)

        self.parameter_set_input = QLineEdit()
        self.parameter_set_input.setPlaceholderText("Parameter Set...")
        self.parameter_set_input.setValidator(QIntValidator(0, 1499, self))
        self.parameter_set_input.setText("0")
        form_layout.addRow("Parameter Set:", self.parameter_set_input)

        layout.addLayout(form_layout)

        self.submit_button = QPushButton("Get!")
        self.submit_button.setIcon(QIcon(resource_path("resources/apply.png")))
        self.submit_button.clicked.connect(self.on_submit)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)
        self.show()

    def on_submit(self):
        try:
            self.core.main_window.right_tab_widget.setCurrentIndex(1)  # open Log tab
            number = int(self.number_input.text())
            block = int(self.block_input.text())
            category = int(self.category_input.text())
            memory = int(self.memory_input.text())
            parameter_set = int(self.parameter_set_input.text())
            self.core.request_custom_parameter(number, block, category, memory, parameter_set)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "All fields must contain valid integers.")
            return
