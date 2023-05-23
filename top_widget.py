from PySide2.QtWidgets import QWidget, QLabel, QComboBox, QHBoxLayout, QPushButton, QFrame

from gui_helper import GuiHelper

CHANNELS = ["Upper keyboard 1", "MIDI 1"]
MUTE = ["OFF", "ON"]


class TopWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.channel = 0
        self.layout = QHBoxLayout(self)

        self.layout.addWidget(QLabel("Tone name:"))
        self.name_label = QLabel("StagePno")
        self.name_label.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(GuiHelper.get_spacer())

        selection = CHANNELS[1] if self.channel == 32 else CHANNELS[0]
        self.channel_combo = self.create_combo_box("Channel:", CHANNELS, selection)
        self.channel_combo.currentIndexChanged.connect(lambda: self.on_channel_change())
        self.layout.addWidget(GuiHelper.get_spacer())

        self.channel_combo = self.create_combo_box("Mute:", MUTE, MUTE[0])
        self.layout.addWidget(GuiHelper.get_spacer())

        synchronize_tone_button = QPushButton("Synchronize tone", self)
        synchronize_tone_button.setObjectName("top-widget-button")
        self.layout.addWidget(synchronize_tone_button)

        randomize_tone_button = QPushButton("Randomize tone", self)
        randomize_tone_button.setObjectName("top-widget-button")
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
