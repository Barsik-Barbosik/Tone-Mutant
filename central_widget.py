import random

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QGridLayout, QTabWidget, QDial, \
    QLabel, QListWidget, QHBoxLayout, QSpinBox, QSizePolicy, QComboBox, QListWidgetItem, QTextBrowser, QPushButton

from enums.enums import ParameterType, TabName
from midi_service import MidiService
from model.current_model import CurrentModel
from model.dsp_module import DspModule
from model.dsp_parameter import DspParameter
from model.instrument import Instrument

KNOB_SIZE = 40
RIGHT_SIDE_MAIN_PARAMS = (
    "Vibrato Type", "Vibrato Depth", "Vibrato Rate", "Vibrato Delay", "Octave Shift", "Volume")
RIGHT_SIDE_DSP_PARAMS = (
    "Overdrive Gain", "Overdrive Level", "Dist Gain", "Dist Level", "Delay Level L", "Delay Level R", "Input Level",
    "Wet Level", "Dry Level")


class CentralWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.midi_service = MidiService()
        self.main_model = CurrentModel()
        self.output_tab_textbox = QTextBrowser()

        main_layout = QGridLayout(self)
        self.setLayout(main_layout)

        self.tab_widget = QTabWidget(self)
        self.tab_widget.setMinimumHeight(400)
        self.tab_widget.addTab(self.create_main_params_page(), TabName.MAIN_PARAMETERS.value)
        self.tab_widget.addTab(self.create_dsp_page(), TabName.DSP_1.value)
        self.tab_widget.addTab(self.create_dsp_page(), TabName.DSP_2.value)
        self.tab_widget.addTab(self.create_dsp_page(), TabName.DSP_3.value)
        self.tab_widget.addTab(self.create_dsp_page(), TabName.DSP_4.value)
        self.tab_widget.addTab(self.create_output_page(), TabName.JSON.value)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        main_layout.addWidget(self.tab_widget, 0, 0, 2, 1)

    def on_tab_changed(self, i):
        current_tab_name = self.get_current_tab_name()
        self.main_model.update_current_block_id(current_tab_name)

        try:
            synth_dsp_module = self.midi_service.request_dsp_module(self.main_model.current_block_id)
            self.main_model.update_current_dsp_module(synth_dsp_module[0])
        except Exception as e:
            self.parent().show_error_msg(str(e))

        if current_tab_name in [TabName.DSP_1, TabName.DSP_2, TabName.DSP_3, TabName.DSP_4]:
            self.parent().show_status_msg(current_tab_name.value + ": " + self.main_model.current_dsp_name, 1000)
            # TODO
            print("update list item!")
        elif current_tab_name == TabName.MAIN_PARAMETERS:
            self.parent().show_status_msg("Main parameters for editing tone", 1000)
        elif current_tab_name == TabName.JSON:
            self.parent().show_status_msg("Tone information in JSON-format", 1000)
            self.output_tab_textbox.setPlainText(self.main_model.get_current_tone_as_json())
        self.redraw_help_msg()

    def get_current_tab_name(self):
        return TabName(self.tab_widget.tabText(self.tab_widget.currentIndex()))

    def create_dsp_page(self) -> QWidget:
        qgrid_layout = QGridLayout(self)
        qgrid_layout.setColumnStretch(0, 1)
        qgrid_layout.setColumnStretch(1, 2)
        qgrid_layout.setColumnStretch(2, 1)
        qgrid_layout.setColumnStretch(3, 2)
        dsp_page = QWidget(self)
        hbox_layout = QHBoxLayout(self)
        dsp_page.setLayout(hbox_layout)

        list_widget = QListWidget(self)
        list_widget.setFixedWidth(180)
        list_widget.insertItem(0, "OFF")
        for idx, dsp_module in enumerate(DspModule.get_all_dsp_modules()):
            item = QListWidgetItem()
            item.setText(dsp_module.name)
            item.setData(Qt.UserRole, dsp_module.id)
            list_widget.insertItem(idx + 1, item)
        list_widget.setCurrentRow(0)
        list_widget.itemSelectionChanged.connect(lambda: self.on_list_widget_changed(list_widget, qgrid_layout))
        hbox_layout.addWidget(list_widget)  # left side

        self.redraw_dsp_params_panel(qgrid_layout)
        hbox_layout.addLayout(qgrid_layout)  # right side

        return dsp_page

    def redraw_dsp_params_panel(self, qgrid_layout: QGridLayout):
        self.clear_layout(qgrid_layout)

        if self.main_model.current_dsp_module is not None:
            right_side_items_count = self.fill_qgrid_with_params(
                qgrid_layout, self.main_model.current_dsp_module.dsp_parameter_list, RIGHT_SIDE_DSP_PARAMS)

            random_button = QPushButton("Set random values", self)
            random_button.setObjectName("random-button")
            random_button.clicked.connect(lambda: self.on_random_button_pressed(qgrid_layout))
            button_row = len(self.main_model.current_dsp_module.dsp_parameter_list) - right_side_items_count + 1
            qgrid_layout.addWidget(random_button, button_row, 0, 1, 4)
        else:
            qgrid_layout.addWidget(self.get_spacer(), 0, 0, 1, 4)

        spacer = self.get_spacer()
        qgrid_layout.addWidget(spacer)

    def fill_qgrid_with_params(self, qgrid_layout, param_list, right_side_items) -> int:
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
                qgrid_layout.addWidget(self.create_combo_input(dsp_param), row, column + 1)
            elif dsp_param.type in [ParameterType.KNOB, ParameterType.KNOB_2BYTES]:
                qgrid_layout.addLayout(self.create_knob_input(dsp_param), row, column + 1)
        return right_side_items_count

    def create_combo_input(self, dsp_parameter: DspParameter) -> QComboBox:
        combo_box = QComboBox(self)
        combo_box.addItems(dsp_parameter.choices)
        combo_box.setCurrentIndex(dsp_parameter.value)
        combo_box.currentIndexChanged.connect(lambda: self.on_combo_changed(combo_box, dsp_parameter))
        return combo_box

    def create_knob_input(self, dsp_parameter: DspParameter) -> QHBoxLayout:
        knob_spinbox = QSpinBox(self)
        knob_spinbox.setMinimum(dsp_parameter.choices[0])
        knob_spinbox.setMaximum(dsp_parameter.choices[1])
        knob_spinbox.setValue(dsp_parameter.value)
        knob = QDial(self)
        knob.setMinimum(knob_spinbox.minimum())
        knob.setMaximum(knob_spinbox.maximum())
        knob.setValue(dsp_parameter.value)
        knob.setFixedSize(KNOB_SIZE, KNOB_SIZE)
        knob.valueChanged.connect(lambda: self.on_knob_changed(knob, knob_spinbox, dsp_parameter))
        knob_spinbox.valueChanged.connect(lambda: self.on_knob_spinbox_changed(knob_spinbox, knob, dsp_parameter))
        hbox = QHBoxLayout(self)
        hbox.addWidget(knob_spinbox)
        hbox.addWidget(knob)
        return hbox

    def on_list_widget_changed(self, list_widget: QListWidget, qgrid_layout: QGridLayout):
        dsp_module_id: int = list_widget.currentItem().data(Qt.UserRole)
        self.main_model.update_current_dsp_module(dsp_module_id)
        self.on_dsp_module_changed()
        self.redraw_dsp_params_panel(qgrid_layout)
        self.redraw_help_msg()

    def on_combo_changed(self, combo: QComboBox, dsp_parameter: DspParameter):
        dsp_parameter.value = dsp_parameter.choices.index(combo.currentText())
        self.send_dsp_params_change_sysex()

    def on_knob_changed(self, knob: QDial, linked_knob_spinbox: QSpinBox, dsp_parameter: DspParameter):
        if knob.value() != linked_knob_spinbox.value():
            linked_knob_spinbox.setValue(knob.value())
            dsp_parameter.value = knob.value()
            self.send_dsp_params_change_sysex()

    def on_knob_spinbox_changed(self, knob_spinbox: QSpinBox, linked_knob: QDial, dsp_parameter: DspParameter):
        if knob_spinbox.value() != linked_knob.value():
            linked_knob.setValue(knob_spinbox.value())
            dsp_parameter.value = knob_spinbox.value()
            self.send_dsp_params_change_sysex()

    def on_random_button_pressed(self, qgrid_layout):
        for dsp_param in self.main_model.current_dsp_module.dsp_parameter_list:
            if dsp_param.type == ParameterType.COMBO:
                dsp_param.value = random.randint(0, len(dsp_param.choices) - 1)
            if dsp_param.type in [ParameterType.KNOB, ParameterType.KNOB_2BYTES]:
                dsp_param.value = random.randint(dsp_param.choices[0], dsp_param.choices[1])
        self.send_dsp_params_change_sysex()
        self.redraw_dsp_params_panel(qgrid_layout)
        self.parent().show_status_msg("It may be necessary to correct volume levels after setting random values.", 3000)

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    self.clear_layout(child.layout())

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

        self.fill_qgrid_with_params(qgrid_layout, self.main_model.tone.main_parameter_list, RIGHT_SIDE_MAIN_PARAMS)

        hbox_layout.addLayout(qgrid_layout)  # right side
        return main_params_page

    def create_output_page(self) -> QWidget:
        output_page = QWidget(self)
        hbox_layout = QHBoxLayout(self)
        hbox_layout.addWidget(self.output_tab_textbox)
        output_page.setLayout(hbox_layout)
        return output_page

    def get_spacer(self):
        spacer = QWidget(self)
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        return spacer

    def redraw_help_msg(self):
        dsp_module = self.main_model.current_dsp_module
        msg = ""
        if self.main_model.current_block_id is not None:
            if dsp_module is None:
                msg = "DSP module is not selected."
            else:
                msg = "<h2>" + self.main_model.current_dsp_name + "</h2>" + dsp_module.description + "<br/>"
                for param in dsp_module.dsp_parameter_list:
                    msg = msg + "<br/><b>" + param.name + "</b><br/>" + param.description + "<br/>"
        elif self.get_current_tab_name() == TabName.MAIN_PARAMETERS:
            msg = "<h2>Main Parameters</h2>List of parameters for editing tone.<br/>"
            for param in self.main_model.tone.main_parameter_list:
                msg = msg + "<br/><b>" + param.name + "</b><br/>" + param.description + "<br/>"

        self.parent().show_help_msg(msg)

    def on_dsp_module_changed(self):
        if self.main_model.current_dsp_module is None:
            print("Current DSP module id: OFF")
            # TODO: turn DSP off
            self.parent().show_status_msg("Not implemented!!", 1000)
        else:
            print("Current DSP module id: " + str(self.main_model.current_dsp_module.id))
            print("Current DSP module name: " + self.main_model.current_dsp_module.name)

            try:
                self.midi_service.send_dsp_module_change_sysex(self.main_model.current_dsp_module.id,
                                                               self.main_model.current_block_id)
                synth_dsp_params = self.midi_service.request_dsp_params(self.main_model.current_block_id)
                for idx, dsp_param in enumerate(self.main_model.current_dsp_module.dsp_parameter_list):
                    dsp_param.value = synth_dsp_params[idx]
                self.send_dsp_params_change_sysex()
            except Exception as e:
                self.parent().show_error_msg(str(e))

    def send_dsp_params_change_sysex(self):
        try:
            self.midi_service.send_dsp_params_change_sysex(self.main_model.get_current_dsp_params_as_list(),
                                                           self.main_model.current_block_id)
        except Exception as e:
            self.parent().show_error_msg(str(e))
