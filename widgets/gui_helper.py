from typing import Callable

from PySide2.QtWidgets import QDial, \
    QHBoxLayout, QSpinBox, QComboBox, QWidget, QSizePolicy, QGridLayout, QMenuBar, QMenu, QAction, QMainWindow, \
    QDockWidget, QFrame, QTabWidget
from PySide2.QtWidgets import QLabel

from constants import constants
from constants.enums import ParameterType
from model.dsp_parameter import DspParameter


class GuiHelper:

    @staticmethod
    def init_menu_bar(main_window: QMainWindow):
        menu_bar = QMenuBar(main_window)

        file_menu = QMenu("&File", main_window)
        menu_bar.addMenu(file_menu)

        open_action = QAction("&Open Tone (TON)", main_window)
        open_action.setStatusTip("Open TON-file")
        open_action.setEnabled(False)
        save_action = QAction("&Save Tone (TON)", main_window)
        save_action.setStatusTip("Save tone as TON-file")
        save_action.setEnabled(False)
        open_json_action = QAction("Open Tone (JSON)", main_window)
        open_json_action.setStatusTip("Read tone information from JSON-formatted file")
        save_json_action = QAction("Save Tone (JSON)", main_window)
        save_json_action.setStatusTip("Save tone information as JSON-formatted file")
        midi_settings_action = QAction("&MIDI settings", main_window)
        midi_settings_action.setStatusTip("Open MIDI settings")
        midi_settings_action.triggered.connect(main_window.show_midi_settings)
        exit_action = QAction("&Exit", main_window)
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(main_window.menu_exit_action)

        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(open_json_action)
        file_menu.addAction(save_json_action)
        file_menu.addSeparator()
        file_menu.addAction(midi_settings_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        return menu_bar

    @staticmethod
    def init_top_dock(main_window: QMainWindow):
        top_dock = QDockWidget("Top Dock", main_window)
        top_dock.setTitleBarWidget(QWidget())
        top_dock.setFloating(False)

        qframe = QFrame(main_window)
        qframe.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        qframe.setObjectName("top-widget")
        inner_layout = QHBoxLayout(main_window)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.addWidget(main_window.top_widget)
        qframe.setLayout(inner_layout)

        outer_widget = QWidget(main_window)
        outer_layout = QHBoxLayout(main_window)
        outer_layout.setContentsMargins(10, 10, 10, 0)  # remove bottom margin
        outer_layout.addWidget(qframe)
        outer_widget.setLayout(outer_layout)

        top_dock.setWidget(outer_widget)

        return top_dock

    @staticmethod
    def init_right_dock(main_window: QMainWindow):
        right_dock = QDockWidget("Right Dock", main_window)
        right_dock.setTitleBarWidget(QWidget())
        right_dock.setFloating(False)

        inner_widget = QWidget(main_window)
        inner_layout = QHBoxLayout(main_window)
        inner_layout.addWidget(main_window.help_texbox)
        inner_widget.setLayout(inner_layout)

        tab_widget = QTabWidget(main_window)
        tab_widget.setMinimumHeight(500)
        tab_widget.setMinimumWidth(300)
        tab_widget.addTab(inner_widget, "Info / Help")

        outer_widget = QWidget(main_window)
        outer_layout = QHBoxLayout(main_window)
        outer_layout.setContentsMargins(0, 10, 10, 10)  # remove left margin
        outer_layout.addWidget(tab_widget)
        outer_widget.setLayout(outer_layout)

        right_dock.setWidget(outer_widget)

        return right_dock

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
        knob.setFixedSize(constants.KNOB_SIZE, constants.KNOB_SIZE)
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
        function_to_run()  # send dsp params change sysex

    @staticmethod
    def on_knob_changed(knob: QDial, linked_knob_spinbox: QSpinBox, dsp_parameter: DspParameter,
                        function_to_run: Callable):
        if knob.value() != linked_knob_spinbox.value():
            linked_knob_spinbox.setValue(knob.value())
            dsp_parameter.value = knob.value()
            function_to_run()  # send dsp params change sysex

    @staticmethod
    def on_knob_spinbox_changed(knob_spinbox: QSpinBox, linked_knob: QDial, dsp_parameter: DspParameter,
                                function_to_run: Callable):
        if knob_spinbox.value() != linked_knob.value():
            linked_knob.setValue(knob_spinbox.value())
            dsp_parameter.value = knob_spinbox.value()
            function_to_run()  # send dsp params change sysex

    @staticmethod
    def get_spacer() -> QWidget:
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        return spacer
