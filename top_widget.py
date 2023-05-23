from PySide2.QtWidgets import QWidget, QLabel, QComboBox, QHBoxLayout, QSizePolicy, QPushButton

from gui_helper import GuiHelper

CHANNELS = ["Upper keyboard 1", "MIDI In 1"]


class TopWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.channel = 0
        self.layout = QHBoxLayout(self)

        self.layout.addWidget(QLabel("Tone name: [StagePno]"))
        self.layout.addWidget(GuiHelper.get_spacer())

        selection = CHANNELS[1] if self.channel == 32 else CHANNELS[0]
        self.channel_combo = self.create_combo_box("Channel:", CHANNELS, selection)
        self.channel_combo.currentIndexChanged.connect(lambda: self.on_channel_change())
        self.layout.addWidget(GuiHelper.get_spacer())

        self.layout.addWidget(QLabel("Mute: [OFF]"))
        self.layout.addWidget(GuiHelper.get_spacer())

        synchronize_tone_button = QPushButton("SYNCHRONIZE", self)
        # synchronize_tone_button.setObjectName("random-button")
        self.layout.addWidget(synchronize_tone_button)

        randomize_tone_button = QPushButton("RANDOMIZE", self)
        # randomize_tone_button.setObjectName("random-button")
        self.layout.addWidget(randomize_tone_button)

    def on_channel_change(self):
        if self.channel_combo.currentIndex() != -1:
            self.channel = 32 if self.channel_combo.currentIndex() == 1 else 0
            print("Channel: " + str(self.channel))

    def create_combo_box(self, label, items, selection):
        self.layout.addWidget(QLabel(label))
        combo_box = QComboBox(self)
        combo_box.addItems(items)
        combo_box.setCurrentText(selection)
        self.layout.addWidget(combo_box)
        return combo_box
