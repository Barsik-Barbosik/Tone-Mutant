from PySide2.QtCore import Slot, Signal, Qt
from PySide2.QtGui import QFont
from PySide2.QtWidgets import QWidget, QLabel, QHBoxLayout, QFrame, QGridLayout, QComboBox, QSizePolicy, QSpacerItem, \
    QLineEdit

from constants.constants import DEFAULT_TONE_NAME
from constants.enums import ParameterType
from models.parameter import AdvancedParameter
from ui.gui_helper import GuiHelper
from utils.utils import get_all_instruments


class TopWidgetMixer(QWidget):
    redraw_volume_knob_signal = Signal(int, int)
    redraw_pan_knob_signal = Signal(int, int)

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.core = parent.core

        self.upper1_volume = AdvancedParameter(234, 234, 0, "UPPER 1 Volume",
                                               "Volume of the note. Only notes played on the keyboard are affected by this (not MIDI IN or rhythms).",
                                               ParameterType.KNOB, [0, 127])
        self.upper2_volume = AdvancedParameter(234, 234, 1, "UPPER 2 Volume", "Volume of the note.",
                                               ParameterType.KNOB, [0, 127])
        self.lower1_volume = AdvancedParameter(234, 234, 2, "LOWER 1 Volume", "Volume of the note. ",
                                               ParameterType.KNOB, [0, 127])
        self.lower2_volume = AdvancedParameter(234, 234, 3, "LOWER 2 Volume", "Volume of the note.",
                                               ParameterType.KNOB, [0, 127])

        # Param number 237 works with category 2 & memory 3
        self.upper1_pan = AdvancedParameter(237, 237, 0, "UPPER 1 Pan", "UPPER 1 Pan", ParameterType.KNOB, [-64, 63])
        self.upper2_pan = AdvancedParameter(237, 237, 1, "UPPER 2 Pan", "UPPER 2 Pan", ParameterType.KNOB, [-64, 63])
        self.lower1_pan = AdvancedParameter(237, 237, 2, "LOWER 1 Pan", "LOWER 1 Pan", ParameterType.KNOB, [-64, 63])
        self.lower2_pan = AdvancedParameter(237, 237, 3, "LOWER 2 Pan", "LOWER 2 Pan", ParameterType.KNOB, [-64, 63])

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # Tone Name Input
        self.tone_name_input = self.create_tone_name_input(DEFAULT_TONE_NAME)

        # Add Blocks for UPPER 1, UPPER 2, LOWER 1, LOWER 2
        self.layout.addWidget(self.create_tone_block("UPPER 1", self.tone_name_input,
                                                     self.upper1_volume, self.upper1_pan,
                                                     volume_knob_name="volume_knob_layout_upper1",
                                                     pan_knob_name="pan_knob_layout_upper1",
                                                     frame_layout_name="frame_layout_upper1"))
        self.layout.addWidget(self.create_tone_block("UPPER 2", None, self.upper2_volume, self.upper2_pan,
                                                     self.on_upper2_selected, "tone_combo_upper2",
                                                     volume_knob_name="volume_knob_layout_upper2",
                                                     pan_knob_name="pan_knob_layout_upper2",
                                                     frame_layout_name="frame_layout_upper2"))
        self.layout.addWidget(self.create_tone_block("LOWER 1", None, self.lower1_volume, self.lower1_pan,
                                                     self.on_lower1_selected, "tone_combo_lower1",
                                                     volume_knob_name="volume_knob_layout_lower1",
                                                     pan_knob_name="pan_knob_layout_lower1",
                                                     frame_layout_name="frame_layout_lower1"))
        self.layout.addWidget(self.create_tone_block("LOWER 2", None, self.lower2_volume, self.lower2_pan,
                                                     self.on_lower2_selected, "tone_combo_lower2",
                                                     volume_knob_name="volume_knob_layout_lower2",
                                                     pan_knob_name="pan_knob_layout_lower2",
                                                     frame_layout_name="frame_layout_lower2"))

        # Signals
        self.redraw_volume_knob_signal.connect(self.redraw_volume_knob)
        self.redraw_pan_knob_signal.connect(self.redraw_pan_knob)

    @staticmethod
    def create_tone_name_input(default_name):
        tone_name_input = QLineEdit(default_name)
        tone_name_input.setFixedWidth(130)
        tone_name_input.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        tone_name_input.setFont(font)
        return tone_name_input

    def create_tone_block(self, label, tone_widget, volume_var, pan_var, tone_change_handler=None,
                          tone_combo_name=None, volume_knob_name=None, pan_knob_name=None, frame_layout_name=None):
        frame = QFrame()
        frame.setObjectName("upper-frame")
        frame_layout = QGridLayout(frame)
        frame_layout.setVerticalSpacing(2)
        frame_layout.setContentsMargins(10, 10, 10, 5)

        # Assign the frame layout to an instance attribute if a name is provided
        if frame_layout_name:
            setattr(self, frame_layout_name, frame_layout)

        # Title
        frame_layout.addWidget(QLabel(f"<b>{label}</b>"), 0, 0, alignment=Qt.AlignLeft)

        # Spacer
        spacer = QSpacerItem(20, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)
        frame_layout.addItem(spacer, 0, 0)

        # Tone Widget or Combo Box
        if tone_widget:
            frame_layout.addWidget(tone_widget, 0, 1, 1, 2, alignment=Qt.AlignLeft)
        else:
            tone_combo = QComboBox()
            tone_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            tone_combo.setFixedWidth(130)
            self.populate_tone_combo(tone_combo)
            if tone_change_handler:
                tone_combo.currentIndexChanged.connect(tone_change_handler)

            # Assign the combo box to an instance attribute if a name is provided
            if tone_combo_name:
                setattr(self, tone_combo_name, tone_combo)

            frame_layout.addWidget(tone_combo, 0, 1, 1, 2, alignment=Qt.AlignLeft)

        # Volume
        frame_layout.addWidget(QLabel("Vol:"), 1, 1)
        volume_knob_layout = GuiHelper.create_knob_input(volume_var, self.on_knob_change)
        if volume_knob_name:
            setattr(self, volume_knob_name, volume_knob_layout)
        frame_layout.addLayout(volume_knob_layout, 1, 2)

        # Pan
        frame_layout.addWidget(QLabel("Pan:"), 2, 1)
        pan_knob_layout = GuiHelper.create_knob_input(pan_var, self.on_knob_change)
        if pan_knob_name:
            setattr(self, pan_knob_name, pan_knob_layout)
        frame_layout.addLayout(pan_knob_layout, 2, 2)

        return frame

    def on_knob_change(self, parameter):
        self.core.send_performance_param_change_sysex(parameter)

    @Slot()
    def redraw_volume_knob(self, block0: int, volume: int):
        volume_knob_layouts = [
            (self.upper1_volume, self.volume_knob_layout_upper1),
            (self.upper2_volume, self.volume_knob_layout_upper2),
            (self.lower1_volume, self.volume_knob_layout_lower1),
            (self.lower2_volume, self.volume_knob_layout_lower2)
        ]

        if 0 <= block0 < len(volume_knob_layouts):
            volume_param, layout = volume_knob_layouts[block0]
            volume_param.value = volume
            knob = layout.itemAt(0).widget()
            knob.setValue(volume)

    @Slot()
    def redraw_pan_knob(self, block0: int, pan: int):
        pan_knob_layouts = [
            (self.upper1_pan, self.pan_knob_layout_upper1),
            (self.upper2_pan, self.pan_knob_layout_upper2),
            (self.lower1_pan, self.pan_knob_layout_lower1),
            (self.lower2_pan, self.pan_knob_layout_lower2)
        ]

        if 0 <= block0 < len(pan_knob_layouts):
            pan_param, layout = pan_knob_layouts[block0]
            pan_param.value = pan
            knob = layout.itemAt(0).widget()
            knob.setValue(pan)

    @staticmethod
    def populate_tone_combo(combo):
        combo.clear()

        for instrument in get_all_instruments():
            display_text = "{:03} - {}".format(instrument.id, instrument.name)
            combo.addItem(display_text, instrument.id)

    def populate_all_tone_combos(self):
        self.populate_tone_combo(self.tone_combo_upper2)
        self.populate_tone_combo(self.tone_combo_lower1)
        self.populate_tone_combo(self.tone_combo_lower2)

    def select_item_by_id(self, block0, id_to_select):
        tone_combos = {
            1: self.tone_combo_upper2,
            2: self.tone_combo_lower1,
            3: self.tone_combo_lower2
        }

        combo = tone_combos.get(block0)
        if combo:
            for index in range(combo.count()):
                item_data = combo.itemData(index, Qt.UserRole)
                if item_data == id_to_select:
                    combo.setCurrentIndex(index)
                    return

    def on_upper2_selected(self, index):
        self._on_tone_selected(index, self.tone_combo_upper2, 1, "UPPER 2 Tone")

    def on_lower1_selected(self, index):
        self._on_tone_selected(index, self.tone_combo_upper2, 2, "LOWER 1 Tone")

    def on_lower2_selected(self, index):
        self._on_tone_selected(index, self.tone_combo_upper2, 3, "LOWER 2 Tone")

    def _on_tone_selected(self, index, combo_box, block, log_prefix):
        if index >= 0:
            selected_text = combo_box.itemText(index)
            selected_id = combo_box.itemData(index, Qt.UserRole)
            self.core.log(f"[INFO] {log_prefix}: {selected_text}")
            self.core.send_instrument_change_sysex(block, selected_id)
