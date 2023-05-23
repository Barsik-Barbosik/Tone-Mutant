from PySide2.QtWidgets import QWidget, QLabel, QComboBox, QHBoxLayout, QPushButton

from gui_helper import GuiHelper

ALL_CHANNELS = ["Upper keyboard", "MIDI Channel 1"]
CHANNEL_ENABLE_DISABLE_ITEMS = ["ENABLED", "DISABLED"]


class TopWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.channel = 0
        self.layout = QHBoxLayout(self)

        selection = ALL_CHANNELS[1] if self.channel == 32 else ALL_CHANNELS[0]
        self.layout.addWidget(QLabel("Channel:"))

        self.channel_combo = QComboBox(self)
        self.channel_combo.addItems(ALL_CHANNELS)
        self.channel_combo.setCurrentText(selection)
        self.channel_combo.currentIndexChanged.connect(lambda: self.on_channel_change())
        self.layout.addWidget(self.channel_combo)

        mute_combo = QComboBox(self)
        mute_combo.addItems(CHANNEL_ENABLE_DISABLE_ITEMS)
        mute_combo.setCurrentIndex(0)
        self.layout.addWidget(mute_combo)

        self.layout.addWidget(GuiHelper.get_spacer())

        self.tone_name_label = QLabel("001 StagePno")
        self.tone_name_label.setObjectName("tone-name-label")
        self.layout.addWidget(self.tone_name_label)

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
