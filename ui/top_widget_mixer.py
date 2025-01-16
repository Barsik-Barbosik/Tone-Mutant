from PySide2.QtCore import Slot, Signal, Qt
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QFrame, QGridLayout, QComboBox, QSizePolicy, QSpacerItem, \
    QLineEdit

from ui.gui_helper import GuiHelper


class TopWidgetMixer(QWidget):
    redraw_upper_volume_knob_signal = Signal()

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.core = parent.core

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.tone_name_input = QLineEdit("StagePno")
        self.tone_name_input.setFixedWidth(130)
        self.tone_name_input.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.tone_name_input.setFont(font)

        self.create_block("UPPER 1", self.core.tone.upper_volume, self.on_volume_change, self.on_pan_change)
        self.create_block("UPPER 2", self.core.tone.upper_volume, self.on_volume_change, self.on_pan_change)
        self.create_block("LOWER 1", self.core.tone.upper_volume, self.on_volume_change, self.on_pan_change)
        self.create_block("LOWER 2", self.core.tone.upper_volume, self.on_volume_change, self.on_pan_change)

        self.redraw_upper_volume_knob_signal.connect(self.redraw_upper_volume_knob)

    def create_block(self, title, volume_value, volume_callback, pan_callback):
        frame = QFrame()
        frame.setObjectName("upper-frame")
        frame_layout = QGridLayout(frame)
        frame_layout.setVerticalSpacing(2)
        frame_layout.setContentsMargins(10, 10, 10, 5)

        frame_layout.addWidget(QLabel(f"<b>{title}</b>"), 0, 0, alignment=Qt.AlignLeft)
        spacer = QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)
        frame_layout.addItem(spacer, 0, 0)

        if title == "UPPER 1":
            frame_layout.addWidget(self.tone_name_input, 0, 1, 1, 2, alignment=Qt.AlignLeft)

        else:
            tone_combo = QComboBox()
            tone_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            tone_combo.addItems(["001 - StagePno", "002 - GrandPno", "003 - BrtPiano"])
            tone_combo.setFixedWidth(130)
            frame_layout.addWidget(tone_combo, 0, 1, 1, 2, alignment=Qt.AlignLeft)

        frame_layout.addWidget(QLabel("Vol:"), 1, 1)
        inner_volume_knob_layout = GuiHelper.create_knob_input(volume_value, volume_callback)
        frame_layout.addLayout(inner_volume_knob_layout, 1, 2)

        frame_layout.addWidget(QLabel("Pan:"), 2, 1)
        inner_pan_knob_layout = GuiHelper.create_knob_input(volume_value, pan_callback)
        frame_layout.addLayout(inner_pan_knob_layout, 2, 2)

        self.layout.addWidget(frame)

    def on_volume_change(self, parameter):
        self.core.send_parameter_change_sysex(parameter)

    def on_pan_change(self, parameter):
        pass

    @Slot()
    def redraw_upper_volume_knob(self):
        # GuiHelper.clear_layout(self.inner_upper_volume_knob_layout)
        # self.inner_upper_volume_knob_layout = GuiHelper.create_knob_input(self.core.tone.upper_volume,
        #                                                                   self.on_volume_change)
        # self.outer_upper_volume_knob_layout.addLayout(self.inner_upper_volume_knob_layout)
        pass
