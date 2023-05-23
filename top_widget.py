from PySide2.QtWidgets import QWidget, QLabel, QComboBox, QGridLayout

CHANNELS = ["Upper keyboard 1", "MIDI In 1"]


class TopWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # inner_layout.addWidget(QLabel(
        #     "Channel: [UPPER 1]            Tone name: [StagePno]            Mute: [OFF]            [SYNCHRONIZE UPPER TONE]            [RANDOMIZE UPPER TONE]"))

        self.channel = 0
        self.layout = QGridLayout(self)

        selection = CHANNELS[1] if self.channel == 32 else CHANNELS[0]
        self.channel_combo = self.create_combo_box("Channel:", CHANNELS, selection)
        self.channel_combo.currentIndexChanged.connect(lambda: self.dummy())

    def dummy(self):
        if self.channel_combo.currentIndex() != -1:
            self.channel = 32 if self.channel_combo.currentIndex() == 1 else 0
            print("Channel: " + str(self.channel))

    def create_combo_box(self, label, items, selection):
        self.layout.addWidget(QLabel(label), self.layout.rowCount(), 0)
        combo_box = QComboBox(self)
        combo_box.addItems(items)
        combo_box.setCurrentText(selection)
        self.layout.addWidget(combo_box, self.layout.rowCount() - 1, 1)
        return combo_box
