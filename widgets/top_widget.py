from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton

from constants import constants
from constants.enums import ParameterType
from model.parameter import AdvancedParameter
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

        volume_parameter = AdvancedParameter(200, 200, 0, "UPPER 1 Volume",
                                             "Volume of the note. Only notes played on the keyboard are affected by this (not MIDI IN or rhythms).",
                                             ParameterType.KNOB, [0, 127])
        self.layout.addLayout(GuiHelper.create_knob_input(volume_parameter, self.on_volume_change))

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

    def on_volume_change(self, parameter):
        self.core.send_parameter_change_sysex(parameter)
