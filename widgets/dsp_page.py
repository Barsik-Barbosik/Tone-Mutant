import random

from PySide2.QtCore import Qt, Slot, Signal
from PySide2.QtWidgets import QWidget, QGridLayout, QListWidget, QHBoxLayout, QListWidgetItem, QPushButton

from constants import constants
from constants.enums import ParameterType
from model.dsp_module import DspModule
from widgets.gui_helper import GuiHelper


class DspPage(QWidget):
    redraw_dsp_params_panel_signal = Signal()

    def __init__(self, parent, block_id: int):
        super().__init__(parent)
        self.core = parent.core
        self.main_window = self.core.main_window

        self.block_id: int = block_id
        self.dsp_module: DspModule = None

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
        self.list_widget.itemSelectionChanged.connect(self.on_list_widget_changed)
        hbox_layout.addWidget(self.list_widget)  # left side
        hbox_layout.addLayout(self.qgrid_layout)  # right side

        self.redraw_dsp_params_panel_signal.connect(self.redraw_dsp_params_panel)

    @Slot()
    def redraw_dsp_params_panel(self):
        self.clear_layout(self.qgrid_layout)

        if self.dsp_module is not None:
            right_side_items_count = GuiHelper.fill_qgrid_with_params(self.qgrid_layout,
                                                                      self.dsp_module.dsp_parameter_list,
                                                                      constants.RIGHT_SIDE_DSP_PARAMS,
                                                                      self.core.set_synth_dsp_params)

            random_button = QPushButton("Randomize DSP values", self)
            random_button.setObjectName("random-button")
            random_button.clicked.connect(self.on_random_button_pressed)
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

    def on_list_widget_changed(self):
        if self.list_widget.currentItem() is None:
            self.list_widget.blockSignals(True)
            self.list_widget.setCurrentRow(0)
            self.list_widget.blockSignals(False)
        else:
            dsp_module_id: int = self.list_widget.currentItem().data(Qt.UserRole)
            if self.dsp_module is None or self.dsp_module.id != dsp_module_id:
                self.core.update_dsp_module_from_list(self.block_id, dsp_module_id)

    def on_random_button_pressed(self):
        for dsp_param in self.dsp_module.dsp_parameter_list:
            if dsp_param.type == ParameterType.COMBO:
                dsp_param.value = random.randint(0, len(dsp_param.choices) - 1)
            if dsp_param.type in [ParameterType.KNOB, ParameterType.SPECIAL_DELAY_KNOB]:
                dsp_param.value = random.randint(dsp_param.choices[0], dsp_param.choices[1])
        self.core.set_synth_dsp_params(None)
        self.redraw_dsp_params_panel()
        self.main_window.show_status_msg("It may be necessary to correct volume levels after setting random values.",
                                         3000)

    def get_module_name(self):
        return self.dsp_module.name if self.dsp_module is not None else constants.EMPTY_DSP_NAME

    def get_list_item_by_dsp_id(self, dsp_module_id):
        for idx in range(self.list_widget.count()):
            item = self.list_widget.item(idx)
            if item.data(Qt.UserRole) == dsp_module_id:
                return item

    def get_dsp_params_as_list(self) -> list:
        output = [0] * 14
        if self.dsp_module is not None:
            for idx, parameter in enumerate(self.dsp_module.dsp_parameter_list):
                if parameter.type == ParameterType.COMBO:
                    output[idx] = parameter.value
                elif parameter.type == ParameterType.KNOB:
                    output[idx] = parameter.value if parameter.choices[0] == 0 else parameter.value + 64
                elif parameter.type == ParameterType.SPECIAL_DELAY_KNOB:
                    # special case, only for the "delay" DSP module
                    output[12] = int(str(parameter.value).zfill(4)[:2])  # first 2 digits
                    output[13] = int(str(parameter.value).zfill(4)[2:])  # last 2 digits
        return output
