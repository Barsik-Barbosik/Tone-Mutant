from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel


class MidiSettingsWindow(QWidget):

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel("Another Window")
        layout.addWidget(self.label)
        self.setLayout(layout)
