import copy
import random

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QGridLayout, QListWidget, QHBoxLayout, QListWidgetItem, QPushButton

from constants import constants
from constants.enums import ParameterType
from model.dsp_module import DspModule
from model.dsp_parameter import DspParameter
from model.tone import Tone
from services.midi_service import MidiService
from widgets.gui_helper import GuiHelper


class DspPage(QWidget):
    def __init__(self, main_window, block_id: int):
        super().__init__()
        self.main = main_window
        self.tone: Tone = self.main.tone
        self.block_id: int = block_id
        self.dsp_module: DspModule = None
        self.midi_service = MidiService.get_instance()

        hbox_layout = QHBoxLayout(self)
        self.setLayout(hbox_layout)

        self.qgrid_layout = QGridLayout(self)
        self.qgrid_layout.setColumnStretch(0, 1)
        self.qgrid_layout.setColumnStretch(1, 2)
        self.qgrid_layout.setColumnStretch(2, 1)
        self.qgrid_layout.setColumnStretch(3, 2)

        self.list_widget = QListWidget(self)
        self.list_widget.setFixedWidth(180)
        self.list_widget.insertItem(0, constants.EMPTY_DSP_NAME)
        for idx, dsp_module in enumerate(constants.ALL_DSP_MODULES):
            item = QListWidgetItem()
            item.setText(dsp_module.name)
            item.setData(Qt.UserRole, dsp_module.id)
            self.list_widget.insertItem(idx + 1, item)
        self.list_widget.setCurrentRow(0)
        self.list_widget.itemSelectionChanged.connect(lambda: self.on_list_widget_changed(self.list_widget))
        hbox_layout.addWidget(self.list_widget)  # left side

        self.redraw_dsp_params_panel()
        hbox_layout.addLayout(self.qgrid_layout)  # right side

    def redraw_dsp_params_panel(self):
        self.clear_layout(self.qgrid_layout)

        if self.dsp_module is not None:
            right_side_items_count = GuiHelper.fill_qgrid_with_params(self.qgrid_layout,
                                                                      self.dsp_module.dsp_parameter_list,
                                                                      constants.RIGHT_SIDE_DSP_PARAMS,
                                                                      self.midi_set_synth_dsp_params)

            random_button = QPushButton("Randomize DSP values", self)
            random_button.setObjectName("random-button")
            random_button.clicked.connect(lambda: self.on_random_button_pressed())
            button_row = len(self.dsp_module.dsp_parameter_list) - right_side_items_count + 1
            self.qgrid_layout.addWidget(random_button, button_row, 0, 1, 4)
        else:
            self.qgrid_layout.addWidget(GuiHelper.get_spacer(), 0, 0, 1, 4)

        self.qgrid_layout.addWidget(GuiHelper.get_spacer())

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    self.clear_layout(child.layout())

    def on_list_widget_changed(self, list_widget: QListWidget):
        dsp_module_id: int = list_widget.currentItem().data(Qt.UserRole)

        self.update_tone_dsp_module_by_dsp_id(dsp_module_id)

    def on_random_button_pressed(self):
        for dsp_param in self.dsp_module.dsp_parameter_list:
            if dsp_param.type == ParameterType.COMBO:
                dsp_param.value = random.randint(0, len(dsp_param.choices) - 1)
            if dsp_param.type in [ParameterType.KNOB, ParameterType.KNOB_2BYTES]:
                dsp_param.value = random.randint(dsp_param.choices[0], dsp_param.choices[1])
        self.midi_set_synth_dsp_params()
        self.redraw_dsp_params_panel()
        self.main.show_status_msg(
            "It may be necessary to correct volume levels after setting random values.", 3000)

    def get_module_name(self):
        return self.dsp_module.name if self.dsp_module is not None else constants.EMPTY_DSP_NAME

    def update_tone_dsp_module_by_dsp_id(self, dsp_module_id):
        synth_dsp_module_id = None
        if dsp_module_id is None:
            try:
                synth_dsp_module = self.midi_service.request_dsp_module(self.block_id)
                synth_dsp_module_id = synth_dsp_module[0]
                if synth_dsp_module is not None and len(synth_dsp_module) > 0:
                    dsp_module_id = synth_dsp_module_id
            except Exception as e:
                self.main.show_error_msg(str(e))

        if self.dsp_module is None or self.dsp_module.id != dsp_module_id:
            if self.block_id == 0:
                self.tone.dsp_module_1 = copy.deepcopy(Tone.get_dsp_module_by_id(dsp_module_id))
                self.dsp_module = self.tone.dsp_module_1
            elif self.block_id == 1:
                self.tone.dsp_module_2 = copy.deepcopy(Tone.get_dsp_module_by_id(dsp_module_id))
                self.dsp_module = self.tone.dsp_module_2
            elif self.block_id == 2:
                self.tone.dsp_module_3 = copy.deepcopy(Tone.get_dsp_module_by_id(dsp_module_id))
                self.dsp_module = self.tone.dsp_module_3
            elif self.block_id == 3:
                self.tone.dsp_module_4 = copy.deepcopy(Tone.get_dsp_module_by_id(dsp_module_id))
                self.dsp_module = self.tone.dsp_module_4

            if synth_dsp_module_id is None or synth_dsp_module_id != dsp_module_id:
                self.midi_set_synth_dsp_module()

            self.midi_get_synth_dsp_params()
            self.redraw_dsp_params_panel()
            self.main.central_widget.redraw_help_msg()

    def get_dsp_params_as_list(self) -> list:
        output = [0] * 14
        if self.dsp_module is not None:
            for idx, parameter in enumerate(self.dsp_module.dsp_parameter_list):
                if parameter.type == ParameterType.COMBO:
                    output[idx] = parameter.value
                elif parameter.type == ParameterType.KNOB:
                    output[idx] = parameter.value if parameter.choices[0] == 0 else parameter.value + 64
                elif parameter.type == ParameterType.KNOB_2BYTES:
                    # special case, only for the "delay" DSP module
                    output[12] = int(str(parameter.value).zfill(4)[:2])  # first 2 digits
                    output[13] = int(str(parameter.value).zfill(4)[2:])  # last 2 digits
        return output

    @staticmethod
    def decode_param_value(value: int, dsp_param: DspParameter):
        if dsp_param.type == ParameterType.KNOB:
            if dsp_param.choices[0] == 0:
                return value
            elif dsp_param.choices[0] == -64:
                return value - 64
        # TODO
        # elif parameter.type == ParameterType.KNOB_2BYTES:
        #     return value
        return value

    def midi_set_synth_dsp_module(self):
        if self.dsp_module is None:
            # TODO: turn DSP off
            self.main.show_status_msg("Not implemented!!", 1000)
        else:
            try:
                self.midi_service.send_dsp_module_change_sysex(self.dsp_module.id, self.block_id)
            except Exception as e:
                self.main.show_error_msg(str(e))

    def midi_get_synth_dsp_params(self):
        if self.dsp_module is not None:
            try:
                synth_dsp_params = self.midi_service.request_dsp_params(self.block_id)
                for idx, dsp_param in enumerate(self.dsp_module.dsp_parameter_list):
                    print("Param before: " + str(synth_dsp_params[idx]) + ", after: " + str(
                        self.decode_param_value(synth_dsp_params[idx], dsp_param)))
                    dsp_param.value = self.decode_param_value(synth_dsp_params[idx], dsp_param)
            except Exception as e:
                self.main.show_error_msg(str(e))

            current_row = self.get_list_item_by_dsp_id(self.dsp_module.id)
            self.list_widget.setCurrentItem(current_row)
            print("midi_get_synth_dsp_params - finished")

    def midi_set_synth_dsp_params(self):
        try:
            self.midi_service.send_dsp_params_change_sysex(self.get_dsp_params_as_list(), self.block_id)
        except Exception as e:
            self.main.show_error_msg(str(e))
        print("midi_set_synth_dsp_params - finished")

    def get_list_item_by_dsp_id(self, dsp_module_id):
        for idx in range(self.list_widget.count()):
            item = self.list_widget.item(idx)
            if item.data(Qt.UserRole) == dsp_module_id:
                return item
