import random
import time

from PySide2.QtCore import Slot, Signal, Qt
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QFrame, QGridLayout, QComboBox, QSizePolicy, QSpacerItem, \
    QLineEdit

from ui.gui_helper import GuiHelper
from utils.worker import Worker


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

    def on_pan_change(self, paramter):
        pass

    def on_randomize_tone_button_pressed(self):
        msg = "Setting random main parameters and selecting 1–2 random DSP modules"
        self.core.log(f"[INFO] {msg}...")
        self.core.main_window.loading_animation.start()

        self.core.main_window.central_widget.on_random_button_pressed()

        # Random DSP modules
        random_dsp_1 = random.randint(0, self.core.main_window.central_widget.dsp_page_1.list_widget.count() - 1)
        random_dsp_2 = random.randint(0, self.core.main_window.central_widget.dsp_page_2.list_widget.count() - 1)

        if random_dsp_1 == 0 and random_dsp_2 > 0:  # swap
            random_dsp_1, random_dsp_2 = random_dsp_2, random_dsp_1

        self.core.main_window.central_widget.dsp_page_1.list_widget.setCurrentRow(random_dsp_1)
        self.core.main_window.central_widget.dsp_page_2.list_widget.setCurrentRow(random_dsp_2)

        if random_dsp_1 > 0 or random_dsp_2 > 0:
            msg += ": " + ", ".join(filter(None, [
                self.core.tone.dsp_module_1.name if random_dsp_1 > 0 else None,
                self.core.tone.dsp_module_2.name if random_dsp_2 > 0 else None
            ]))

        self.core.show_status_msg(msg, 3000)
        self.core.pause_status_bar_updates(True)

        # Random DSP params
        worker = Worker(self.randomize_dsp_params, random_dsp_1, random_dsp_2)
        worker.signals.error.connect(lambda error: self.show_error_msg(str(error[1])))
        worker.start()

    def randomize_dsp_params(self, random_dsp_1, random_dsp_2):
        if random_dsp_1 > 0:
            time.sleep(0.3)
            self.core.main_window.central_widget.dsp_page_1.on_random_button_pressed(
                self.core.main_window.central_widget.dsp_page_1.block_id)

        if random_dsp_2 > 0:
            time.sleep(0.3)
            self.core.main_window.central_widget.dsp_page_2.on_random_button_pressed(
                self.core.main_window.central_widget.dsp_page_2.block_id)

        self.core.pause_status_bar_updates(False)
        self.core.main_window.loading_animation.stop()

    @Slot()
    def redraw_upper_volume_knob(self):
        # GuiHelper.clear_layout(self.inner_upper_volume_knob_layout)
        # self.inner_upper_volume_knob_layout = GuiHelper.create_knob_input(self.core.tone.upper_volume,
        #                                                                   self.on_volume_change)
        # self.outer_upper_volume_knob_layout.addLayout(self.inner_upper_volume_knob_layout)
        pass
