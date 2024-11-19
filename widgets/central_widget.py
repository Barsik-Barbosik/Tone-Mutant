import json
import random

from PySide2.QtCore import Qt, Slot, Signal
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QWidget, QGridLayout, QTabWidget, QHBoxLayout, QListWidgetItem, QTextBrowser, QPushButton

from constants import constants
from constants.enums import TabName, ParameterType
from external.object_encoder import ObjectEncoder
from syntax_highlighters.json_highlighter import JsonHighlighter
from utils.utils import resource_path
from widgets.dsp_page import DspPage
from widgets.gui_helper import GuiHelper
from widgets.inactive_list_widget import InactiveListWidget


class CentralWidget(QWidget):
    update_help_text_panel_signal = Signal()
    redraw_main_params_panel_signal = Signal()

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.core = parent.core
        self.main_window = self.core.main_window

        self.json_view_tab_textbox = QTextBrowser()
        JsonHighlighter(self.json_view_tab_textbox.document())

        self.dsp_page_1 = DspPage(self, 0)
        self.dsp_page_2 = DspPage(self, 1)
        self.dsp_page_3 = DspPage(self, 2)
        self.dsp_page_4 = DspPage(self, 3)
        self.current_dsp_page: DspPage = None

        main_layout = QGridLayout(self)
        self.setLayout(main_layout)

        self.instrument_list = InactiveListWidget(self)
        self.instrument_list.setObjectName("inactive-list")

        self.qgrid_layout = QGridLayout()
        self.tab_widget = QTabWidget(self)
        self.tab_widget.setMinimumHeight(500)
        self.tab_widget.addTab(self.create_main_params_page(), TabName.MAIN_PARAMETERS.value)
        self.tab_widget.addTab(self.dsp_page_1, TabName.DSP_1.value)
        self.tab_widget.addTab(self.dsp_page_2, TabName.DSP_2.value)
        self.tab_widget.addTab(self.dsp_page_3, TabName.DSP_3.value)
        self.tab_widget.addTab(self.dsp_page_4, TabName.DSP_4.value)
        self.tab_widget.addTab(self.create_json_view_page(), TabName.JSON.value)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        main_layout.addWidget(self.tab_widget, 0, 0, 2, 1)

        self.update_help_text_panel_signal.connect(self.update_help_text_panel)
        self.redraw_main_params_panel_signal.connect(self.redraw_main_params_panel)

    def create_main_params_page(self) -> QWidget:
        self.qgrid_layout.setColumnStretch(0, 1)
        self.qgrid_layout.setColumnStretch(1, 2)
        self.qgrid_layout.setColumnStretch(2, 1)
        self.qgrid_layout.setColumnStretch(3, 2)
        main_params_page = QWidget(self)
        hbox_layout = QHBoxLayout()
        main_params_page.setLayout(hbox_layout)

        self.instrument_list.setFixedWidth(180)
        # self.instrument_list.setEnabled(False)
        for idx, instrument in enumerate(constants.ALL_INSTRUMENTS_3000_5000):
            item = QListWidgetItem()
            item.setText("{:03}".format(instrument.id) + "  -  " + instrument.name)
            item.setData(Qt.UserRole, instrument.id)
            self.instrument_list.insertItem(idx, item)
        # self.instrument_list.setCurrentRow(0)
        self.instrument_list.itemSelectionChanged.connect(self.on_instrument_list_changed)
        hbox_layout.addWidget(self.instrument_list)  # left side

        GuiHelper.fill_qgrid_with_params(self.qgrid_layout,
                                         self.core.tone.main_parameter_list,
                                         constants.RIGHT_SIDE_MAIN_PARAMS,
                                         self.set_synth_parameter)

        hbox_layout.addLayout(self.qgrid_layout)  # right side
        return main_params_page

    @Slot()
    def redraw_main_params_panel(self):
        GuiHelper.clear_layout(self.qgrid_layout)
        right_side_items_count = GuiHelper.fill_qgrid_with_params(self.qgrid_layout,
                                                                  self.core.tone.main_parameter_list,
                                                                  constants.RIGHT_SIDE_MAIN_PARAMS,
                                                                  self.set_synth_parameter)

        largest_items_count = max(right_side_items_count,
                                  len(self.core.tone.main_parameter_list) - right_side_items_count)

        random_button = QPushButton(" Randomize Parameters", self)
        random_button.setIcon(QIcon(resource_path("resources/random.png")))
        random_button.setObjectName("random-button")
        random_button.clicked.connect(self.on_random_button_pressed)
        button_row = largest_items_count + 1
        self.qgrid_layout.addWidget(random_button, button_row, 0, 1, 4)

    def on_random_button_pressed(self):
        for main_param in self.core.tone.main_parameter_list:
            if main_param.name != "Volume":
                if main_param.type == ParameterType.COMBO:
                    main_param.value = random.randint(0, len(main_param.choices) - 1)
                if main_param.type in [ParameterType.KNOB, ParameterType.KNOB_X2, ParameterType.SPECIAL_ATK_REL_KNOB]:
                    main_param.value = random.randint(main_param.choices[0], main_param.choices[1])
                self.core.send_parameter_change_sysex(main_param)
        self.redraw_main_params_panel()
        self.main_window.show_status_msg(
            "It may be necessary to correct volume level and octave shift after setting random values.",
            3000)

    def get_current_tab_name(self):
        return TabName(self.tab_widget.tabText(self.tab_widget.currentIndex()))

    def on_tab_changed(self, _):
        self.current_dsp_page = None
        current_tab_name = self.get_current_tab_name()

        if current_tab_name == TabName.MAIN_PARAMETERS:
            self.main_window.show_status_msg("Main parameters for editing tone", 3000)
        elif current_tab_name in [TabName.DSP_1, TabName.DSP_2, TabName.DSP_3, TabName.DSP_4]:
            self.main_window.show_status_msg("Parameters for " + current_tab_name.value + " module", 3000)
            if current_tab_name == TabName.DSP_1:
                self.current_dsp_page = self.dsp_page_1
            elif current_tab_name == TabName.DSP_2:
                self.current_dsp_page = self.dsp_page_2
            elif current_tab_name == TabName.DSP_3:
                self.current_dsp_page = self.dsp_page_3
            elif current_tab_name == TabName.DSP_4:
                self.current_dsp_page = self.dsp_page_4
            self.current_dsp_page.redraw_dsp_params_panel()
        elif current_tab_name == TabName.JSON:
            self.main_window.show_status_msg("Tone information in JSON-format", 3000)
            self.json_view_tab_textbox.setPlainText(self.get_json())

        self.update_help_text_panel()

    def get_json(self):
        return json.dumps(self.core.tone, cls=ObjectEncoder, indent=4)

    def on_instrument_list_changed(self):
        instrument_id: int = self.instrument_list.currentItem().data(Qt.UserRole)
        self.core.change_instrument_by_id_from_list(instrument_id)

    def create_json_view_page(self) -> QWidget:
        json_view_page = QWidget(self)
        hbox_layout = QHBoxLayout()
        hbox_layout.addWidget(self.json_view_tab_textbox)
        json_view_page.setLayout(hbox_layout)
        return json_view_page

    @Slot()
    def update_help_text_panel(self):
        text = ""
        if self.get_current_tab_name() == TabName.MAIN_PARAMETERS:
            text = "<h2>Main Parameters</h2>List of parameters for editing tone.<br/>"
            for param in self.core.tone.main_parameter_list:
                text = text + "<br/><b>" + param.name + "</b><br/>" + param.description + "<br/>"
        elif self.get_current_tab_name() == TabName.JSON:
            text = "<h2>JSON</h2>Main tone data in JSON format. Many parameter values can be seen here. Currently, this view is read-only. Perhaps in the future, it will become editable."
        elif self.current_dsp_page is not None and self.current_dsp_page.block_id is not None:
            if self.current_dsp_page.dsp_module is None:
                text = "DSP module is not selected."
            else:
                text = "<h2>" + self.current_dsp_page.get_module_name() + "</h2>" \
                       + self.current_dsp_page.dsp_module.description + "<br/>"
                for param in self.current_dsp_page.dsp_module.dsp_parameter_list:
                    text = text + "<br/><b>" + param.name + "</b><br/>" + param.description + "<br/>"

        self.main_window.show_help_text(text)

    # Send message to update synth's main parameter
    def set_synth_parameter(self, parameter):
        self.core.send_parameter_change_sysex(parameter)
