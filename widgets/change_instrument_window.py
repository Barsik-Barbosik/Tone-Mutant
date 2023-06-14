from PySide2 import QtCore
from PySide2.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton


class ChangeInstrumentWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Pause: parent tone selection")

        layout = QVBoxLayout()
        label = QLabel(
            "Please, use your CT-X3000/5000 synthesizer controls to manually select the parent tone:\n\n001 GrandPno\n\nThen press \"Continue\" button to apply parameter changes!")
        label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(label)

        ok_button = QPushButton("Continue")
        ok_button.setObjectName("random-button")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button)

        self.setLayout(layout)
