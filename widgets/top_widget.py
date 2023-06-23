from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton, QDial, QSpinBox

from constants import constants
from widgets.gui_helper import GuiHelper

ALL_CHANNELS = ["Upper keyboard", "MIDI Channel 1"]
CHANNEL_ENABLE_DISABLE_ITEMS = ["ENABLED", "DISABLED"]


class TopWidget(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.core = parent.core
        self.main_window = self.core.main_window

        self.channel = 0
        self.layout = QHBoxLayout(self)

        label = QLabel("UPPER 1 Volume:")
        self.layout.addWidget(label)

        knob_spinbox = QSpinBox()
        knob_spinbox.setMinimum(0)
        knob_spinbox.setMaximum(127)
        knob_spinbox.setValue(100)
        self.layout.addWidget(knob_spinbox)

        knob = QDial()
        knob.setMinimum(0)
        knob.setMaximum(127)
        knob.setValue(100)
        knob.setFixedSize(constants.KNOB_SIZE, constants.KNOB_SIZE)
        knob.valueChanged.connect(self.on_volume_change)
        self.layout.addWidget(knob)

        self.layout.addWidget(GuiHelper.get_spacer())

        self.tone_name_label = QLabel(constants.DEFAULT_TONE_NAME)
        self.tone_name_label.setObjectName("tone-name-label")
        self.layout.addWidget(self.tone_name_label)

        self.layout.addWidget(GuiHelper.get_spacer())

        synchronize_tone_button = QPushButton("Synchronize tone", self)
        synchronize_tone_button.setObjectName("top-widget-button")
        synchronize_tone_button.clicked.connect(self.core.synchronize_tone_with_synth)
        self.layout.addWidget(synchronize_tone_button)

        randomize_tone_button = QPushButton("Randomize tone", self)
        randomize_tone_button.setObjectName("top-widget-button")
        self.layout.addWidget(randomize_tone_button)

    def on_volume_change(self):
        # self.core.midi_service.send_sysex("F0 44 19 01 7F 01 03 03 00 00 00 00 00 00 00 00 00 00 48 01 00 00 00 00 00 F7")  # TODO: remove!~
        # self.core.midi_service.send_sysex("B0 01 7F")  # TODO: remove!~
        # self.core.midi_service.send_sysex("B4 01 7F")  # TODO: remove!~
        # self.core.midi_service.send_sysex("B1 01 7F")  # TODO: remove!~
        # self.core.midi_service.send_sysex("B2 01 7F")  # TODO: remove!~
        # self.core.midi_service.send_sysex("B3 01 7F")  # TODO: remove!~
        pass
