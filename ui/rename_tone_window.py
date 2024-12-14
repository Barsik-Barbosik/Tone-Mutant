from PySide2 import QtCore
from PySide2.QtGui import QIcon, QIntValidator
from PySide2.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QFormLayout, QMessageBox

from constants.constants import DEFAULT_TONE_NAME
from utils.utils import resource_path


class RenameToneWindow(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.core = parent.core

        self.number_input = None
        self.name_input = None
        self.submit_button = None
        self.setWindowTitle("Rename Tone")
        self.setWindowIcon(QIcon(resource_path("resources/piano_pencil.png")))

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.add_title(layout)
        self.add_form(layout)
        self.add_submit_button(layout)

        self.setLayout(layout)
        self.show()

    @staticmethod
    def add_title(layout):
        label = QLabel("Rename tone in the synthesizer's memory")
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)

    def add_form(self, layout):
        form_layout = QFormLayout()

        # Tone Number input
        tone_number = self.get_tone_number()
        self.number_input = self.create_line_edit("Tone Number... (801-900)", QIntValidator(801, 900), tone_number)
        form_layout.addRow("Tone Number:", self.number_input)

        # Tone Name input
        tone_name = self.get_tone_name()
        self.name_input = self.create_line_edit("New Name...", None, tone_name)
        self.name_input.setMaxLength(8)
        form_layout.addRow("New Name:", self.name_input)

        layout.addLayout(form_layout)

    def add_submit_button(self, layout):
        self.submit_button = QPushButton("RENAME")
        self.submit_button.setIcon(QIcon(resource_path("resources/apply.png")))
        self.submit_button.clicked.connect(self.on_submit)
        layout.addWidget(self.submit_button)

    @staticmethod
    def create_line_edit(placeholder, validator, default_value):
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        if validator:
            line_edit.setValidator(validator)
        if default_value:
            line_edit.setText(str(default_value))
        return line_edit

    def get_tone_number(self):
        if self.core.tone.parent_tone and 800 < self.core.tone.parent_tone.id <= 900:
            return self.core.tone.parent_tone.id
        return None

    def get_tone_name(self):
        return self.core.tone.name if self.core.tone.name else None

    def on_submit(self):
        try:
            tone_number = int(self.number_input.text())

            if 800 < tone_number <= 900:
                self.close()

                new_name = DEFAULT_TONE_NAME
                if self.name_input.text():
                    new_name = self.name_input.text()

                self.core.start_tone_rename_worker(tone_number, new_name)
                self.deleteLater()
            else:
                QMessageBox.warning(self, "Input Error", "The 'Tone Number' must be in the range of 801 to 900.")

        except ValueError:
            QMessageBox.warning(self, "Input Error", "The 'Tone Number' field must contain a valid integer.")
