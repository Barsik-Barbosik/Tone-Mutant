from PySide2.QtCore import Slot, Signal
from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton

from constants import constants
from widgets.gui_helper import GuiHelper

ALL_CHANNELS = ["Upper keyboard", "MIDI Channel 1"]
CHANNEL_ENABLE_DISABLE_ITEMS = ["ENABLED", "DISABLED"]


class TopWidget(QWidget):
    redraw_upper_volume_knob_signal = Signal()

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.core = parent.core
        self.main_window = self.core.main_window

        self.channel = 0
        self.layout = QHBoxLayout(self)

        label = QLabel("UPPER 1 Volume:")
        self.layout.addWidget(label)
        self.outer_upper_volume_knob_layout = QHBoxLayout()
        self.inner_upper_volume_knob_layout = GuiHelper.create_knob_input(self.core.tone.upper_volume,
                                                                          self.on_volume_change)
        self.outer_upper_volume_knob_layout.addLayout(self.inner_upper_volume_knob_layout)
        self.layout.addLayout(self.outer_upper_volume_knob_layout)

        self.layout.addWidget(GuiHelper.get_spacer())  # --------------------------

        self.tone_name_label = QLabel(constants.DEFAULT_TONE_NAME)
        self.tone_name_label.setObjectName("tone-name-label")
        self.layout.addWidget(self.tone_name_label)

        self.layout.addWidget(GuiHelper.get_spacer())  # --------------------------

        synchronize_tone_button = QPushButton("Synchronize tone", self)
        synchronize_tone_button.setObjectName("top-widget-button")
        synchronize_tone_button.clicked.connect(self.core.synchronize_tone_with_synth)
        self.layout.addWidget(synchronize_tone_button)

        randomize_tone_button = QPushButton("Randomize tone", self)
        randomize_tone_button.setObjectName("top-widget-button")
        randomize_tone_button.clicked.connect(self.on_random_button_pressed)
        self.layout.addWidget(randomize_tone_button)

        self.redraw_upper_volume_knob_signal.connect(self.redraw_upper_volume_knob)

    def on_volume_change(self, parameter):
        self.core.send_parameter_change_sysex(parameter)

    def on_random_button_pressed(self):
        self.main_window.show_status_msg(
            "Random main params and 2 DSP!",
            3000)

    @Slot()
    def redraw_upper_volume_knob(self):
        GuiHelper.clear_layout(self.inner_upper_volume_knob_layout)
        self.inner_upper_volume_knob_layout = GuiHelper.create_knob_input(self.core.tone.upper_volume,
                                                                          self.on_volume_change)
        self.outer_upper_volume_knob_layout.addLayout(self.inner_upper_volume_knob_layout)
