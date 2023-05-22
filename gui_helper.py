from typing import Callable

from PySide2.QtWidgets import QDial, \
    QHBoxLayout, QSpinBox, QComboBox, QWidget, QSizePolicy, QGridLayout
from PySide2.QtWidgets import QLabel

from enums.enums import ParameterType
from model.dsp_parameter import DspParameter

KNOB_SIZE = 40


class GuiHelper:

    @staticmethod
    def fill_qgrid_with_params(qgrid_layout: QGridLayout, param_list: list, right_side_items: tuple,
                               function_to_run: Callable) -> int:
        right_side_items_count = 0
        for idx, dsp_param in enumerate(param_list):
            if dsp_param.name not in right_side_items:
                row = idx - right_side_items_count
                column = 0
                label_class = "label-left-side"
            else:
                row = right_side_items_count
                column = 2
                label_class = "label-right-side"
                right_side_items_count += 1

            label = QLabel(dsp_param.name + ":")
            label.setObjectName(label_class)
            qgrid_layout.addWidget(label, row, column)
            if dsp_param.type == ParameterType.COMBO:
                qgrid_layout.addWidget(GuiHelper.create_combo_input(dsp_param, function_to_run), row, column + 1)
            elif dsp_param.type in [ParameterType.KNOB, ParameterType.KNOB_2BYTES]:
                qgrid_layout.addLayout(GuiHelper.create_knob_input(dsp_param, function_to_run), row, column + 1)
        return right_side_items_count

    @staticmethod
    def create_combo_input(dsp_parameter: DspParameter, function_to_run: Callable) -> QComboBox:
        combo_box = QComboBox()
        combo_box.addItems(dsp_parameter.choices)
        combo_box.setCurrentIndex(dsp_parameter.value)
        combo_box.currentIndexChanged.connect(
            lambda: GuiHelper.on_combo_changed(combo_box, dsp_parameter, function_to_run))
        return combo_box

    @staticmethod
    def create_knob_input(dsp_parameter: DspParameter, function_to_run: Callable) -> QHBoxLayout:
        knob_spinbox = QSpinBox()
        knob_spinbox.setMinimum(dsp_parameter.choices[0])
        knob_spinbox.setMaximum(dsp_parameter.choices[1])
        knob_spinbox.setValue(dsp_parameter.value)
        knob = QDial()
        knob.setMinimum(knob_spinbox.minimum())
        knob.setMaximum(knob_spinbox.maximum())
        knob.setValue(dsp_parameter.value)
        knob.setFixedSize(KNOB_SIZE, KNOB_SIZE)
        knob.valueChanged.connect(lambda: GuiHelper.on_knob_changed(knob, knob_spinbox, dsp_parameter, function_to_run))
        knob_spinbox.valueChanged.connect(
            lambda: GuiHelper.on_knob_spinbox_changed(knob_spinbox, knob, dsp_parameter, function_to_run))
        hbox = QHBoxLayout()
        hbox.addWidget(knob_spinbox)
        hbox.addWidget(knob)
        return hbox

    @staticmethod
    def on_combo_changed(combo: QComboBox, dsp_parameter: DspParameter, function_to_run: Callable):
        dsp_parameter.value = dsp_parameter.choices.index(combo.currentText())
        function_to_run()  # send_dsp_params_change_sysex()

    @staticmethod
    def on_knob_changed(knob: QDial, linked_knob_spinbox: QSpinBox, dsp_parameter: DspParameter,
                        function_to_run: Callable):
        if knob.value() != linked_knob_spinbox.value():
            linked_knob_spinbox.setValue(knob.value())
            dsp_parameter.value = knob.value()
            function_to_run()  # send_dsp_params_change_sysex()

    @staticmethod
    def on_knob_spinbox_changed(knob_spinbox: QSpinBox, linked_knob: QDial, dsp_parameter: DspParameter,
                                function_to_run: Callable):
        if knob_spinbox.value() != linked_knob.value():
            linked_knob.setValue(knob_spinbox.value())
            dsp_parameter.value = knob_spinbox.value()
            function_to_run()  # send_dsp_params_change_sysex()

    @staticmethod
    def get_spacer() -> QWidget:
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        return spacer
