import random

from PySide2.QtCore import Qt, Slot, Signal
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QWidget, QGridLayout, QListWidget, QHBoxLayout, QListWidgetItem, QPushButton, QLabel

from constants import constants
from constants.enums import ParameterType
from models.dsp_module import DspModule
from ui.gui_helper import GuiHelper
from utils import utils
from utils.utils import resource_path


class DspPage(QWidget):
    redraw_dsp_params_panel_signal = Signal()

    def __init__(self, parent, block_id: int):
        super().__init__(parent)
        self.core = parent.core
        self.block_id: int = block_id
        self.dsp_module: DspModule = None

        hbox_layout = QHBoxLayout(self)
        self.setLayout(hbox_layout)

        self.qgrid_layout = QGridLayout()
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
        self.list_widget.itemSelectionChanged.connect(lambda: self.on_list_widget_changed(block_id))

        hbox_layout.addWidget(self.list_widget)  # left side
        hbox_layout.addLayout(self.qgrid_layout)  # right side

        self.redraw_dsp_params_panel_signal.connect(lambda: self.redraw_dsp_params_panel(block_id))

    @Slot()
    def redraw_dsp_params_panel(self, _):
        # print(f"redraw_dsp_params_panel, block: {self.block_id}")
        GuiHelper.clear_layout(self.qgrid_layout)

        if self.dsp_module is not None:
            right_side_items_count = GuiHelper.fill_qgrid_with_params(self.qgrid_layout,
                                                                      self.dsp_module.dsp_parameter_list,
                                                                      constants.RIGHT_SIDE_DSP_PARAMS,
                                                                      self.core.set_synth_dsp_params)

            label = QLabel("Bypass:")
            label.setObjectName("label-right-side")
            self.qgrid_layout.addWidget(label, right_side_items_count, 2)
            self.qgrid_layout.addWidget(GuiHelper.create_combo_input(self.dsp_module.bypass, self.send_dsp_bypass),
                                        right_side_items_count, 3)
            right_side_items_count = right_side_items_count + 1

            largest_items_count = max(right_side_items_count,
                                      len(self.dsp_module.dsp_parameter_list) - right_side_items_count)

            random_button = QPushButton(" Randomize DSP Values", self)
            random_button.setIcon(QIcon(resource_path("resources/random_star.png")))
            random_button.setObjectName("random-button")
            random_button.clicked.connect(lambda: self.on_random_button_pressed(self.block_id))
            button_row = largest_items_count + 1
            self.qgrid_layout.addWidget(random_button, button_row, 0, 1, 4)
        else:
            self.qgrid_layout.addWidget(GuiHelper.get_spacer(), 0, 0, 1, 4)

        self.qgrid_layout.addWidget(GuiHelper.get_spacer())

    def send_dsp_bypass(self, bypass_parameter):
        bypass = True if bypass_parameter.value == 1 else False
        self.core.send_dsp_bypass(self.block_id, bypass)

    def on_list_widget_changed(self, _):
        if self.list_widget.currentItem() is None:
            self.list_widget.blockSignals(True)
            self.list_widget.setCurrentRow(0)
            self.list_widget.blockSignals(False)
        else:
            dsp_module_id: int = self.list_widget.currentItem().data(Qt.UserRole)
            # print(f"block_id: {self.block_id}, dsp_module_id: {dsp_module_id}")
            if self.dsp_module is None or self.dsp_module.id != dsp_module_id:
                self.core.update_dsp_module_from_list(self.block_id, dsp_module_id)

    def on_random_button_pressed(self, _):
        for dsp_param in self.dsp_module.dsp_parameter_list:
            if dsp_param.type == ParameterType.COMBO:
                dsp_param.value = random.randint(0, len(dsp_param.choices) - 1)
            if dsp_param.type in [ParameterType.KNOB, ParameterType.SPECIAL_DELAY_KNOB]:
                dsp_param.value = random.randint(dsp_param.choices[0], dsp_param.choices[1])
        self.core.set_synth_dsp_params(None)
        self.redraw_dsp_params_panel_signal.emit()
        msg = "It might be necessary to adjust the volume levels after setting random values."
        self.core.show_status_msg(msg, 3000)
        self.core.log("[INFO] " + msg)

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
                if parameter.type == ParameterType.SPECIAL_DELAY_KNOB:
                    # special case, only for the "delay" DSP module
                    output[12] = int(str(parameter.value).zfill(4)[:2])  # first 2 digits
                    output[13] = int(str(parameter.value).zfill(4)[2:])  # last 2 digits
                else:
                    output[idx] = utils.encode_value_by_type(parameter)

        return output
