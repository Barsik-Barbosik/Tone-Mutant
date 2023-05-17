import random

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QWidget, QGridLayout, QTabWidget, QFormLayout, QDial, \
    QLabel, QListWidget, QHBoxLayout, QSpinBox, QSizePolicy, QComboBox, QListWidgetItem, QTextBrowser, QPushButton

from enums.enums import ParameterType, TabName
from midi_service import MidiService
from model.DspEffect import DspEffect
from model.DspParameter import DspParameter
from model.MainEffect import MainEffect
from model.MainModel import MainModel

KNOB_SIZE = 40
RIGHT_SIDE_KNOBS = (
    "Overdrive Gain", "Overdrive Level", "Dist Gain", "Dist Level", "Delay Level L", "Delay Level R", "Input Level",
    "Wet Level", "Dry Level")


class CentralWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.midi_service = MidiService()
        self.main_model = MainModel()
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
        self.tab_widget.addTab(self.create_output_page(), TabName.OUTPUT.value)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        main_layout.addWidget(self.tab_widget, 0, 0, 2, 1)

    def on_tab_changed(self, i):
        self.main_model.currentTabName = TabName(self.tab_widget.tabText(self.tab_widget.currentIndex()))
        self.parent().show_status_msg(
            self.main_model.currentTabName.value + ": " + self.main_model.get_current_dsp_name(), 1000)
        if self.main_model.currentTabName == TabName.OUTPUT:
            self.output_tab_textbox.setPlainText(self.main_model.get_output_text())
        self.redraw_help_msg()

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
        for idx, dsp_effect in enumerate(DspEffect.get_dsp_effects_tuple()):
            item = QListWidgetItem()
            item.setText(dsp_effect.name)
            item.setData(Qt.UserRole, dsp_effect.id)
            list_widget.insertItem(idx + 1, item)
        list_widget.setCurrentRow(0)
        list_widget.itemSelectionChanged.connect(lambda: self.on_list_widget_changed(list_widget, qgrid_layout))
        hbox_layout.addWidget(list_widget)  # left side

        self.redraw_dsp_params_panel(qgrid_layout)
        hbox_layout.addLayout(qgrid_layout)  # right side

        return dsp_page

    def redraw_dsp_params_panel(self, qgrid_layout: QGridLayout):
        self.clear_layout(qgrid_layout)

        if self.main_model.get_current_dsp() is not None:

            right_side_items_count = 0

            for idx, dsp_param in enumerate(self.main_model.get_current_dsp().dsp_parameter_list):
                if dsp_param.name not in RIGHT_SIDE_KNOBS:
                    row = idx - right_side_items_count
                    column = 0
                    label_padding = "padding-left: 10px;"
                else:
                    row = right_side_items_count
                    column = 2
                    label_padding = "padding-left: 30px;"
                    right_side_items_count += 1

                label = QLabel(dsp_param.name + ":")
                label.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
                label.setStyleSheet(label_padding)
                qgrid_layout.addWidget(label, row, column)
                if dsp_param.type == ParameterType.COMBO:
                    qgrid_layout.addWidget(self.create_combo_input(dsp_param), row, column + 1)
                elif dsp_param.type in [ParameterType.KNOB, ParameterType.KNOB_2BYTES]:
                    qgrid_layout.addLayout(self.create_knob_input(dsp_param), row, column + 1)

            random_button = QPushButton("Set random values", self)
            random_button.setStyleSheet("margin: 20px 50px 10px 50px; padding: 5px;")
            random_button.clicked.connect(lambda: self.on_random_button_pressed(qgrid_layout))
            button_row = len(self.main_model.get_current_dsp().dsp_parameter_list) - right_side_items_count + 1
            qgrid_layout.addWidget(random_button, button_row, 0, 1, 4)
        else:
            qgrid_layout.addWidget(self.get_spacer(), 0, 0, 1, 4)

        spacer = self.get_spacer()
        qgrid_layout.addWidget(spacer)

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
        dsp_effect_id: int = list_widget.currentItem().data(Qt.UserRole)
        self.main_model.set_current_dsp(dsp_effect_id)
        self.change_dsp_module()
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
        for dsp_param in self.main_model.get_current_dsp().dsp_parameter_list:
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
        main_params_page = QWidget(self)
        hbox_layout = QHBoxLayout(self)
        left_layout = QFormLayout()
        right_layout = QFormLayout()

        list_widget = QListWidget(self)
        list_widget.setFixedWidth(180)
        list_widget.insertItem(0, "001 Piano 1")
        list_widget.insertItem(1, "002 Piano 2")
        list_widget.setCurrentRow(0)
        left_layout.addWidget(list_widget)

        for idx, main_param in enumerate(MainEffect.get_main_effects_tuple()):
            if idx < 3:
                if main_param.type == ParameterType.COMBO:
                    left_layout.addRow(main_param.name + ":", self.create_combo_input(main_param))
                elif main_param.type in [ParameterType.KNOB, ParameterType.KNOB_2BYTES]:
                    left_layout.addRow(main_param.name + ":", self.create_knob_input(main_param))
            else:
                if main_param.type == ParameterType.COMBO:
                    right_layout.addRow(main_param.name + ":", self.create_combo_input(main_param))
                elif main_param.type in [ParameterType.KNOB, ParameterType.KNOB_2BYTES]:
                    right_layout.addRow(main_param.name + ":", self.create_knob_input(main_param))

        hbox_layout.addLayout(left_layout)
        hbox_layout.addLayout(right_layout)
        main_params_page.setLayout(hbox_layout)
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
        dsp_effect = self.main_model.get_current_dsp()
        msg = ""
        if self.main_model.get_current_block_id() is not None:
            if dsp_effect is None:
                msg = "DSP module is not selected."
            else:
                msg = "<h3>" + self.main_model.get_current_dsp_name() + "</h3>" + dsp_effect.description + "<br/>"
                for param in dsp_effect.dsp_parameter_list:
                    msg = msg + "<br/><b>" + param.name + "</b><br/>" + param.description + "<br/>"

        self.parent().show_help_msg(msg)

    def change_dsp_module(self):
        if self.main_model.get_current_dsp() is None:
            print("Current DSP effect id: OFF")
            # TODO: turn DSP off
            self.parent().show_status_msg("Not implemented!!", 1000)
        else:
            print("Current DSP effect id: " + str(self.main_model.get_current_dsp().id))
            print("Current DSP effect name: " + self.main_model.get_current_dsp().name)

            try:
                self.midi_service.send_dsp_module_change_sysex(self.main_model.get_current_dsp().id,
                                                               self.main_model.get_current_block_id())
                synth_dsp_params = self.midi_service.request_dsp_params(self.main_model.get_current_block_id())
                for idx, dsp_param in enumerate(self.main_model.get_current_dsp().dsp_parameter_list):
                    dsp_param.value = synth_dsp_params[idx]
                self.send_dsp_params_change_sysex()
            except Exception as e:
                self.parent().show_error_msg(str(e))

    def send_dsp_params_change_sysex(self):
        try:
            self.midi_service.send_dsp_params_change_sysex(self.main_model.get_current_dsp_params_as_list(),
                                                           self.main_model.get_current_block_id())
        except Exception as e:
            self.parent().show_error_msg(str(e))
