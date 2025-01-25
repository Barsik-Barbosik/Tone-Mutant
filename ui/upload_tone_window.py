from PySide2 import QtCore
from PySide2.QtGui import QIcon, QIntValidator
from PySide2.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QFormLayout, QMessageBox, \
    QHBoxLayout

from constants.constants import DEFAULT_TONE_NAME
from utils.utils import resource_path


class UploadToneWindow(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.core = parent.core

        self.number_input = None
        self.name_input = None
        self.submit_button = None
        self.setWindowTitle("Save a tone to the synth's memory")
        self.setWindowIcon(QIcon(resource_path("resources/piano_plus.png")))

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.add_title(layout)
        self.add_form(layout)
        self.add_submit_button(layout)

        self.resize(330, 160)
        self.setLayout(layout)
        self.show()

    @staticmethod
    def add_title(layout):
        label = QLabel()
        label.setText("<h2>Save Current Tone</h2>")
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)

    def add_form(self, layout):
        form_layout = QFormLayout()

        # Tone Number input
        tone_number = self.get_tone_number()
        self.number_input = self.create_line_edit("User Memory... (801-900)", QIntValidator(801, 900), tone_number)
        form_layout.addRow("Tone Number:", self.number_input)

        # Tone Name input
        tone_name = self.get_tone_name()
        self.name_input = self.create_line_edit("Tone Name... (8 symbols)", None, tone_name)
        self.name_input.setMaxLength(8)
        form_layout.addRow("Tone Name:", self.name_input)

        layout.addLayout(form_layout)

    def add_submit_button(self, layout):
        self.submit_button = QPushButton(" SAVE")
        self.submit_button.setIcon(QIcon(resource_path("resources/apply.png")))
        self.submit_button.clicked.connect(self.on_submit)
        self.submit_button.setFixedWidth(150)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.submit_button)
        button_layout.addStretch()
        button_layout.setContentsMargins(10, 10, 10, 5)  # (left, top, right, bottom) margins

        layout.addLayout(button_layout)

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

                if self.name_input.text():
                    self.core.tone.name = self.name_input.text()
                else:
                    self.core.tone.name = DEFAULT_TONE_NAME

                self.core.start_tone_upload_worker(tone_number)
                self.core.main_window.top_widget.update_tone_name_input_and_parent_info()
                self.deleteLater()
            else:
                QMessageBox.warning(self, "Input Error", "The 'Tone Number' must be in the range of 801 to 900.")

        except ValueError:
            QMessageBox.warning(self, "Input Error", "The 'Tone Number' field must contain a valid integer.")
