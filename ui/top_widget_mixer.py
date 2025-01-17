from PySide2.QtCore import Slot, Signal, Qt
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QFrame, QGridLayout, QComboBox, QSizePolicy, QSpacerItem, \
    QLineEdit

from constants.enums import ParameterType
from models.parameter import AdvancedParameter
from ui.gui_helper import GuiHelper


class TopWidgetMixer(QWidget):
    redraw_volume_knob_signal = Signal(int, int)

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.core = parent.core

        self.upper1_volume = AdvancedParameter(200, 200, 0, "UPPER 1 Volume",
                                               "Volume of the note. Only notes played on the keyboard are affected by this (not MIDI IN or rhythms).",
                                               ParameterType.KNOB, [0, 127])
        self.upper2_volume = AdvancedParameter(200, 200, 0, "UPPER 2 Volume", "Volume of the note.",
                                               ParameterType.KNOB, [0, 127])
        self.lower1_volume = AdvancedParameter(200, 200, 0, "LOWER 1 Volume", "Volume of the note. ",
                                               ParameterType.KNOB, [0, 127])
        self.lower2_volume = AdvancedParameter(200, 200, 0, "LOWER 2 Volume", "Volume of the note.",
                                               ParameterType.KNOB, [0, 127])

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.tone_name_input = QLineEdit("StagePno")
        self.tone_name_input.setFixedWidth(130)
        self.tone_name_input.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.tone_name_input.setFont(font)

        # Block for UPPER 1
        frame_upper1 = QFrame()
        frame_upper1.setObjectName("upper-frame")
        self.frame_layout_upper1 = QGridLayout(frame_upper1)
        self.frame_layout_upper1.setVerticalSpacing(2)
        self.frame_layout_upper1.setContentsMargins(10, 10, 10, 5)

        self.frame_layout_upper1.addWidget(QLabel("<b>UPPER 1</b>"), 0, 0, alignment=Qt.AlignLeft)
        spacer = QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.frame_layout_upper1.addItem(spacer, 0, 0)
        self.frame_layout_upper1.addWidget(self.tone_name_input, 0, 1, 1, 2, alignment=Qt.AlignLeft)
        self.frame_layout_upper1.addWidget(QLabel("Vol:"), 1, 1)
        self.volume_knob_layout_upper1 = GuiHelper.create_knob_input(self.upper1_volume, self.on_volume_change)
        self.frame_layout_upper1.addLayout(self.volume_knob_layout_upper1, 1, 2)
        self.frame_layout_upper1.addWidget(QLabel("Pan:"), 2, 1)
        pan_knob_layout_upper1 = GuiHelper.create_knob_input(self.upper1_volume, self.on_pan_change)
        self.frame_layout_upper1.addLayout(pan_knob_layout_upper1, 2, 2)
        self.layout.addWidget(frame_upper1)

        # Block for UPPER 2
        frame_upper2 = QFrame()
        frame_upper2.setObjectName("upper-frame")
        self.frame_layout_upper2 = QGridLayout(frame_upper2)
        self.frame_layout_upper2.setVerticalSpacing(2)
        self.frame_layout_upper2.setContentsMargins(10, 10, 10, 5)

        self.frame_layout_upper2.addWidget(QLabel("<b>UPPER 2</b>"), 0, 0, alignment=Qt.AlignLeft)
        spacer = QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.frame_layout_upper2.addItem(spacer, 0, 0)
        tone_combo_upper2 = QComboBox()
        tone_combo_upper2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        tone_combo_upper2.addItems(["001 - StagePno", "002 - GrandPno", "003 - BrtPiano"])
        tone_combo_upper2.setFixedWidth(130)
        self.frame_layout_upper2.addWidget(tone_combo_upper2, 0, 1, 1, 2, alignment=Qt.AlignLeft)
        self.frame_layout_upper2.addWidget(QLabel("Vol:"), 1, 1)
        self.volume_knob_layout_upper2 = GuiHelper.create_knob_input(self.upper2_volume, self.on_volume_change)
        self.frame_layout_upper2.addLayout(self.volume_knob_layout_upper2, 1, 2)
        self.frame_layout_upper2.addWidget(QLabel("Pan:"), 2, 1)
        pan_knob_layout_upper2 = GuiHelper.create_knob_input(self.upper2_volume, self.on_pan_change)
        self.frame_layout_upper2.addLayout(pan_knob_layout_upper2, 2, 2)
        self.layout.addWidget(frame_upper2)

        # Block for LOWER 1
        frame_lower1 = QFrame()
        frame_lower1.setObjectName("upper-frame")
        self.frame_layout_lower1 = QGridLayout(frame_lower1)
        self.frame_layout_lower1.setVerticalSpacing(2)
        self.frame_layout_lower1.setContentsMargins(10, 10, 10, 5)

        self.frame_layout_lower1.addWidget(QLabel("<b>LOWER 1</b>"), 0, 0, alignment=Qt.AlignLeft)
        spacer = QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.frame_layout_lower1.addItem(spacer, 0, 0)
        tone_combo_lower1 = QComboBox()
        tone_combo_lower1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        tone_combo_lower1.addItems(["001 - StagePno", "002 - GrandPno", "003 - BrtPiano"])
        tone_combo_lower1.setFixedWidth(130)
        self.frame_layout_lower1.addWidget(tone_combo_lower1, 0, 1, 1, 2, alignment=Qt.AlignLeft)
        self.frame_layout_lower1.addWidget(QLabel("Vol:"), 1, 1)
        self.volume_knob_layout_lower1 = GuiHelper.create_knob_input(self.lower1_volume, self.on_volume_change)
        self.frame_layout_lower1.addLayout(self.volume_knob_layout_lower1, 1, 2)
        self.frame_layout_lower1.addWidget(QLabel("Pan:"), 2, 1)
        pan_knob_layout_lower1 = GuiHelper.create_knob_input(self.lower1_volume, self.on_pan_change)
        self.frame_layout_lower1.addLayout(pan_knob_layout_lower1, 2, 2)
        self.layout.addWidget(frame_lower1)

        # Block for LOWER 2
        frame_lower2 = QFrame()
        frame_lower2.setObjectName("upper-frame")
        self.frame_layout_lower2 = QGridLayout(frame_lower2)
        self.frame_layout_lower2.setVerticalSpacing(2)
        self.frame_layout_lower2.setContentsMargins(10, 10, 10, 5)

        self.frame_layout_lower2.addWidget(QLabel("<b>LOWER 2</b>"), 0, 0, alignment=Qt.AlignLeft)
        spacer = QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.frame_layout_lower2.addItem(spacer, 0, 0)
        tone_combo_lower2 = QComboBox()
        tone_combo_lower2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        tone_combo_lower2.addItems(["001 - StagePno", "002 - GrandPno", "003 - BrtPiano"])
        tone_combo_lower2.setFixedWidth(130)
        self.frame_layout_lower2.addWidget(tone_combo_lower2, 0, 1, 1, 2, alignment=Qt.AlignLeft)
        self.frame_layout_lower2.addWidget(QLabel("Vol:"), 1, 1)
        self.volume_knob_layout_lower2 = GuiHelper.create_knob_input(self.lower2_volume, self.on_volume_change)
        self.frame_layout_lower2.addLayout(self.volume_knob_layout_lower2, 1, 2)
        self.frame_layout_lower2.addWidget(QLabel("Pan:"), 2, 1)
        pan_knob_layout_lower2 = GuiHelper.create_knob_input(self.lower2_volume, self.on_pan_change)
        self.frame_layout_lower2.addLayout(pan_knob_layout_lower2, 2, 2)
        self.layout.addWidget(frame_lower2)

        self.redraw_volume_knob_signal.connect(self.redraw_volume_knob)

    def on_volume_change(self, parameter):
        self.core.send_volume_change_sysex(parameter)

    def on_pan_change(self, parameter):
        pass

    @Slot()
    def redraw_volume_knob(self, param_set: int, volume):
        print(f"redraw_volume_knob... param_set: {param_set}, volume: {volume}")

        if param_set == 0:
            self.upper1_volume.value = volume
            GuiHelper.clear_layout(self.volume_knob_layout_upper1)
            self.volume_knob_layout_upper1 = GuiHelper.create_knob_input(self.upper1_volume, self.on_volume_change)
            self.frame_layout_upper1.addLayout(self.volume_knob_layout_upper1, 1, 2)
        elif param_set == 1:
            self.upper2_volume.value = volume
            GuiHelper.clear_layout(self.volume_knob_layout_upper2)
            self.volume_knob_layout_upper2 = GuiHelper.create_knob_input(self.upper2_volume, self.on_volume_change)
            self.frame_layout_upper2.addLayout(self.volume_knob_layout_upper2, 1, 2)
        elif param_set == 2:
            self.lower1_volume.value = volume
            GuiHelper.clear_layout(self.volume_knob_layout_lower1)
            self.volume_knob_layout_lower1 = GuiHelper.create_knob_input(self.lower1_volume, self.on_volume_change)
            self.frame_layout_lower1.addLayout(self.volume_knob_layout_lower1, 1, 2)
        elif param_set == 3:
            self.lower2_volume.value = volume
            GuiHelper.clear_layout(self.volume_knob_layout_lower2)
            self.volume_knob_layout_lower2 = GuiHelper.create_knob_input(self.lower2_volume, self.on_volume_change)
            self.frame_layout_lower2.addLayout(self.volume_knob_layout_lower2, 1, 2)
