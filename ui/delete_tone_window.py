from PySide2 import QtCore
from PySide2.QtGui import QIcon, QIntValidator
from PySide2.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QFormLayout, QMessageBox, \
    QHBoxLayout

from utils.utils import resource_path


class DeleteToneWindow(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.setWindowTitle("Delete a tone in memory")
        self.setWindowIcon(QIcon(resource_path("resources/piano_minus.png")))

        self.core = parent.core

        layout = QVBoxLayout()
        label = QLabel()
        label.setText("<h2>Delete a Tone</h2>")
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)

        form_layout = QFormLayout()

        tone_number = None
        if self.core.tone.parent_tone and 800 < self.core.tone.parent_tone.id <= 900:
            tone_number = self.core.tone.parent_tone.id

        self.number_input = QLineEdit()
        self.number_input.setPlaceholderText("User Memory... (801-900)")
        self.number_input.setValidator(QIntValidator(801, 900, self))

        if tone_number:
            self.number_input.setText(str(tone_number))

        form_layout.addRow("Tone Number:", self.number_input)

        layout.addLayout(form_layout)

        self.submit_button = QPushButton(" DELETE")
        self.submit_button.setIcon(QIcon(resource_path("resources/exclamation.png")))
        self.submit_button.clicked.connect(self.on_submit)
        self.submit_button.setFixedWidth(150)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.submit_button)
        button_layout.addStretch()
        button_layout.setContentsMargins(10, 10, 10, 5)  # (left, top, right, bottom) margins

        layout.addLayout(button_layout)

        self.resize(330, 160)
        self.setLayout(layout)
        self.show()

    def on_submit(self):
        try:
            if self.number_input.text() and 800 < int(self.number_input.text()) <= 900:
                self.close()
                self.core.start_tone_delete_worker(int(self.number_input.text()))
                self.deleteLater()
            else:
                QMessageBox.warning(self, "Input Error", "The 'Tone Number' must be in the range of 801 to 900.")

        except ValueError:
            QMessageBox.warning(self, "Input Error", "The 'Tone Number' field must contain a valid integer.")
