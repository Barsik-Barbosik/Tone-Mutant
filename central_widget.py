import json

from PySide2.QtCore import Qt, QThreadPool
from PySide2.QtWidgets import QWidget, QGridLayout, QTabWidget, QListWidget, QHBoxLayout, QListWidgetItem, QTextBrowser

from dsp_page import DspPage
from enums.enums import TabName
from external.object_encoder import ObjectEncoder
from gui_helper import GuiHelper
from midi_service import MidiService
from model.instrument import Instrument
from model.tone import Tone

RIGHT_SIDE_MAIN_PARAMS = (
    "Vibrato Type", "Vibrato Depth", "Vibrato Rate", "Vibrato Delay", "Octave Shift", "Volume")


class CentralWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.threadpool = QThreadPool.globalInstance()
        self.json_view_tab_textbox = QTextBrowser()
        self.midi_service = MidiService.get_instance()
        self.gui_factory = GuiHelper()

        self.tone: Tone = Tone()
        self.dsp_page_1 = DspPage(self.tone, 0)
        self.dsp_page_2 = DspPage(self.tone, 1)
        self.dsp_page_3 = DspPage(self.tone, 2)
        self.dsp_page_4 = DspPage(self.tone, 3)
        self.current_dsp_page: DspPage = None

        main_layout = QGridLayout(self)
        self.setLayout(main_layout)

        self.tab_widget = QTabWidget(self)
        self.tab_widget.setMinimumHeight(400)
        self.tab_widget.addTab(self.create_main_params_page(), TabName.MAIN_PARAMETERS.value)
        self.tab_widget.addTab(self.dsp_page_1, TabName.DSP_1.value)
        self.tab_widget.addTab(self.dsp_page_2, TabName.DSP_2.value)
        self.tab_widget.addTab(self.dsp_page_3, TabName.DSP_3.value)
        self.tab_widget.addTab(self.dsp_page_4, TabName.DSP_4.value)
        self.tab_widget.addTab(self.create_json_view_page(), TabName.JSON.value)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        main_layout.addWidget(self.tab_widget, 0, 0, 2, 1)

    def on_tab_changed(self, _unused_idx):
        current_tab_name = self.get_current_tab_name()

        if current_tab_name == TabName.MAIN_PARAMETERS:
            self.parent().show_status_msg("Main parameters for editing tone", 3000)
        elif current_tab_name in [TabName.DSP_1, TabName.DSP_2, TabName.DSP_3, TabName.DSP_4]:
            self.parent().show_status_msg("Parameters for " + current_tab_name.value + " module", 3000)

            if current_tab_name == TabName.DSP_1:
                self.current_dsp_page = self.dsp_page_1
            elif current_tab_name == TabName.DSP_2:
                self.current_dsp_page = self.dsp_page_2
            elif current_tab_name == TabName.DSP_3:
                self.current_dsp_page = self.dsp_page_3
            elif current_tab_name == TabName.DSP_4:
                self.current_dsp_page = self.dsp_page_4
            else:
                self.current_dsp_page = None

            self.current_dsp_page.update_tone_dsp_module_by_dsp_id(None)
        elif current_tab_name == TabName.JSON:
            self.parent().show_status_msg("Tone information in JSON-format", 3000)
            self.json_view_tab_textbox.setPlainText(json.dumps(self.tone, cls=ObjectEncoder, indent=4))

        self.redraw_help_msg()

    def get_current_tab_name(self):
        return TabName(self.tab_widget.tabText(self.tab_widget.currentIndex()))

    def create_main_params_page(self) -> QWidget:
        qgrid_layout = QGridLayout(self)
        qgrid_layout.setColumnStretch(0, 1)
        qgrid_layout.setColumnStretch(1, 2)
        qgrid_layout.setColumnStretch(2, 1)
        qgrid_layout.setColumnStretch(3, 2)
        main_params_page = QWidget(self)
        hbox_layout = QHBoxLayout(self)
        main_params_page.setLayout(hbox_layout)

        list_widget = QListWidget(self)
        list_widget.setFixedWidth(180)
        for idx, instrument in enumerate(Instrument.get_all_instruments()):
            item = QListWidgetItem()
            item.setText("{:03}".format(instrument.id) + "  -  " + instrument.name)
            item.setData(Qt.UserRole, instrument.id)
            list_widget.insertItem(idx, item)
        list_widget.setCurrentRow(0)
        hbox_layout.addWidget(list_widget)  # left side

        self.gui_factory.fill_qgrid_with_params(qgrid_layout,
                                                self.tone.main_parameter_list,
                                                RIGHT_SIDE_MAIN_PARAMS,
                                                self.do_nothing)

        hbox_layout.addLayout(qgrid_layout)  # right side
        return main_params_page

    def create_json_view_page(self) -> QWidget:
        json_view_page = QWidget(self)
        hbox_layout = QHBoxLayout(self)
        hbox_layout.addWidget(self.json_view_tab_textbox)
        json_view_page.setLayout(hbox_layout)
        return json_view_page

    def redraw_help_msg(self):
        msg = ""
        if self.get_current_tab_name() == TabName.MAIN_PARAMETERS:
            msg = "<h2>Main Parameters</h2>List of parameters for editing tone.<br/>"
            for param in self.tone.main_parameter_list:
                msg = msg + "<br/><b>" + param.name + "</b><br/>" + param.description + "<br/>"
        elif self.current_dsp_page is not None and self.current_dsp_page.block_id is not None:
            if self.current_dsp_page.dsp_module is None:
                msg = "DSP module is not selected."
            else:
                msg = "<h2>" + self.current_dsp_page.get_module_name() + "</h2>" \
                      + self.current_dsp_page.dsp_module.description + "<br/>"
                for param in self.current_dsp_page.dsp_module.dsp_parameter_list:
                    msg = msg + "<br/><b>" + param.name + "</b><br/>" + param.description + "<br/>"

        self.parent().show_help_msg(msg)

    # def aaa(self):
    #     worker = Worker(self.send_dsp_params_change_sysex)
    #     worker.signals.result.connect(self.print_output)
    #     worker.signals.finished.connect(self.thread_complete)
    #     self.threadpool.start(worker)
    #
    # def print_output(self, s):
    #     print(s)

    @staticmethod
    def do_nothing():
        print("...")
