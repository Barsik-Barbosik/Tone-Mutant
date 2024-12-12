from PySide2 import QtCore
from PySide2.QtGui import QIcon, QIntValidator
from PySide2.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QFormLayout, QMessageBox

from utils.utils import resource_path


class DeleteToneWindow(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.setWindowTitle("Delete Tone")
        self.setWindowIcon(QIcon(resource_path("resources/piano_minus.png")))

        self.core = parent.core

        layout = QVBoxLayout()
        label = QLabel("Delete a tone from the synthesizer's memory")
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)

        form_layout = QFormLayout()

        tone_number = None
        if self.core.tone.parent_tone and 800 < self.core.tone.parent_tone.id <= 900:
            tone_number = self.core.tone.parent_tone.id

        self.number_input = QLineEdit()
        self.number_input.setPlaceholderText("Tone Number... (801-900)")
        self.number_input.setValidator(QIntValidator(801, 900, self))

        if tone_number:
            self.number_input.setText(str(tone_number))

        form_layout.addRow("Tone Number:", self.number_input)

        layout.addLayout(form_layout)

        self.submit_button = QPushButton("DELETE")
        self.submit_button.setIcon(QIcon(resource_path("resources/exclamation.png")))
        self.submit_button.clicked.connect(self.on_submit)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)
        self.show()

    def on_submit(self):
        try:
            self.core.log(f"[INFO] Deleting tone number: {self.number_input.text()}")

            if self.number_input.text() and 800 < int(self.number_input.text()) <= 900:
                self.core.delete_tone(int(self.number_input.text()))
                self.core.synchronize_tone_with_synth()
                self.core.status_msg_signal.emit("Tone successfully deleted!", 3000)
                self.close()
                self.deleteLater()
            else:
                QMessageBox.warning(self, "Input Error", "The 'Tone Number' must be in the range of 801 to 900.")

        except ValueError:
            QMessageBox.warning(self, "Input Error", "The 'Tone Number' field must contain a valid integer.")
