import configparser
from typing import Callable

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QDial, \
    QHBoxLayout, QSpinBox, QComboBox, QWidget, QSizePolicy, QGridLayout, QMenuBar, QMenu, QAction, QMainWindow, \
    QDockWidget, QFrame, QTabWidget, QVBoxLayout, QTextEdit, QPushButton
from PySide2.QtWidgets import QLabel

from constants import constants
from constants.enums import ParameterType
from models.parameter import Parameter, MainParameter
from utils.utils import resource_path


class GuiHelper:

    @staticmethod
    def init_menu_bar(main_window: QMainWindow, exit_callback, open_json_callback, save_json_callback,
                      settings_callback, how_to_save_callback, request_parameter_callback):
        menu_bar = QMenuBar(main_window)

        file_menu = QMenu("&File", main_window)
        menu_bar.addMenu(file_menu)

        open_json_action = QAction(QIcon(resource_path('resources/open.png')), "&Open Tone (JSON)", main_window)
        open_json_action.setStatusTip("Read tone information from a JSON-formatted file")
        open_json_action.triggered.connect(open_json_callback)

        save_json_action = QAction(QIcon(resource_path('resources/save.png')), "&Save Tone (JSON)", main_window)
        save_json_action.setStatusTip("Save tone information as a JSON-formatted file")
        save_json_action.triggered.connect(save_json_callback)

        open_action = QAction(QIcon(resource_path('resources/open.png')), "Open Tone (TON)", main_window)
        open_action.setStatusTip(
            "Open TON file (Not implemented. Please use the \"Synchronize Tone\" button to load the required tone from the synthesizer.)")
        open_action.setEnabled(False)

        save_action = QAction(QIcon(resource_path('resources/save.png')), "Save Tone (TON)", main_window)
        save_action.setStatusTip(
            "Save tone as a TON file (Not implemented. Please use the synthesizer to save and export the tone. See \"How to Save a TON File\" for instructions.)")
        save_action.setEnabled(False)

        how_to_save_action = QAction(QIcon(resource_path('resources/help.png')), "&How to Save a TON File", main_window)
        how_to_save_action.setStatusTip("Instructions on how to use the synthesizer to save and export the tone")
        how_to_save_action.triggered.connect(how_to_save_callback)

        midi_settings_action = QAction(QIcon(resource_path('resources/settings.png')), "&Settings", main_window)
        midi_settings_action.setStatusTip("Open settings")
        midi_settings_action.triggered.connect(settings_callback)

        exit_action = QAction(QIcon(resource_path('resources/exit.png')), "&Exit", main_window)
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(exit_callback)

        file_menu.addAction(open_json_action)
        file_menu.addAction(save_json_action)
        file_menu.addSeparator()
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(how_to_save_action)
        file_menu.addSeparator()
        file_menu.addAction(midi_settings_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        if GuiHelper.is_custom_midi_msg_enabled():
            requests_menu = QMenu("&Request", main_window)
            menu_bar.addMenu(requests_menu)

            request_parameter_action = QAction(QIcon(resource_path('resources/get.png')), "&Request Parameter", main_window)
            request_parameter_action.setStatusTip("Request a parameter from synthesizer")
            request_parameter_action.triggered.connect(request_parameter_callback)

            requests_menu.addAction(request_parameter_action)

        return menu_bar

    @staticmethod
    def init_top_dock(main_window: QMainWindow):
        top_dock = QDockWidget("Top Dock", main_window)
        top_dock.setTitleBarWidget(QWidget())
        top_dock.setFloating(False)

        qframe = QFrame(main_window)
        qframe.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        qframe.setObjectName("top-widget")
        inner_layout = QHBoxLayout()
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.addWidget(main_window.top_widget)
        qframe.setLayout(inner_layout)

        outer_widget = QWidget(main_window)
        outer_layout = QHBoxLayout()
        outer_layout.setContentsMargins(10, 10, 10, 0)  # remove bottom margin
        outer_layout.addWidget(qframe)
        outer_widget.setLayout(outer_layout)

        top_dock.setWidget(outer_widget)

        return top_dock

    @staticmethod
    def init_right_dock(main_window: QMainWindow):
        # Create the dock widget
        right_dock = QDockWidget("Right Dock", main_window)
        right_dock.setTitleBarWidget(QWidget())
        right_dock.setFloating(False)

        # Create tabs (Help and Log)
        help_tab = GuiHelper.create_help_tab(main_window)
        log_tab = GuiHelper.create_log_tab(main_window)

        # Set up the tab widget
        tab_widget = QTabWidget(main_window)
        tab_widget.setMinimumHeight(500)
        tab_widget.setMinimumWidth(300)
        tab_widget.addTab(help_tab, "Info / Help")
        tab_widget.addTab(log_tab, "Log")

        # Save a reference to the tab widget in the main window
        main_window.right_tab_widget = tab_widget

        # Wrap tab widget in a container and set it as the dock widget's content
        outer_widget = QWidget(main_window)
        outer_layout = QHBoxLayout()
        outer_layout.setContentsMargins(0, 10, 10, 10)  # remove left margin
        outer_layout.addWidget(tab_widget)
        outer_widget.setLayout(outer_layout)

        right_dock.setWidget(outer_widget)
        return right_dock

    @staticmethod
    def create_help_tab(main_window: QMainWindow) -> QWidget:
        """Creates the Help/Info tab."""
        help_tab = QWidget(main_window)
        help_tab_layout = QHBoxLayout()
        help_tab_layout.addWidget(main_window.help_texbox)
        help_tab.setLayout(help_tab_layout)
        return help_tab

    @staticmethod
    def create_log_tab(main_window: QMainWindow) -> QWidget:
        """Creates the Log tab."""
        log_tab = QWidget(main_window)
        log_tab_layout = QVBoxLayout()
        log_tab_layout.addWidget(main_window.log_texbox)

        if GuiHelper.is_custom_midi_msg_enabled():
            GuiHelper.add_midi_msg_input(log_tab_layout, main_window)

        log_tab.setLayout(log_tab_layout)
        return log_tab

    @staticmethod
    def is_custom_midi_msg_enabled() -> bool:
        """Checks if custom MIDI message sending is enabled."""
        cfg = configparser.ConfigParser()
        cfg.read(constants.CONFIG_FILENAME)
        return cfg.get("Expert", "is_custom_midi_msg_sending_enabled", fallback="false").lower() == "true"

    @staticmethod
    def add_midi_msg_input(log_tab_layout: QVBoxLayout, main_window: QMainWindow):
        """Adds the MIDI message input section to the log tab."""
        midi_msg_input = QTextEdit(main_window)
        midi_msg_input.setPlaceholderText("MIDI message...")
        midi_msg_input.setMaximumHeight(80)
        log_tab_layout.addWidget(midi_msg_input)

        submit_button = QPushButton(" Send MIDI Message")
        submit_button.setIcon(QIcon(resource_path("resources/apply.png")))
        submit_button.clicked.connect(lambda: main_window.core.send_custom_midi_msg(midi_msg_input.toPlainText()))
        log_tab_layout.addWidget(submit_button)

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
            elif dsp_param.type in [ParameterType.KNOB, ParameterType.KNOB_X2, ParameterType.SPECIAL_ATK_REL_KNOB,
                                    ParameterType.SPECIAL_DELAY_KNOB]:
                qgrid_layout.addLayout(GuiHelper.create_knob_input(dsp_param, function_to_run), row, column + 1)
        return right_side_items_count

    @staticmethod
    def create_combo_input(parameter: Parameter, function_to_run: Callable) -> QComboBox:
        combo_box = QComboBox()
        if parameter.choices[1] is not None and len(parameter.choices[1]) > 30:
            # amp cabinet types
            combo_box.setObjectName("fat-combo-box")
            combo_box.setMaximumWidth(150)
        combo_box.addItems(parameter.choices)
        combo_box.setCurrentIndex(parameter.value)
        combo_box.currentIndexChanged.connect(
            lambda new_value: GuiHelper.on_combo_changed(combo_box, parameter, function_to_run))
        return combo_box

    @staticmethod
    def create_knob_input(parameter: Parameter, function_to_run: Callable) -> QHBoxLayout:
        knob_spinbox = QSpinBox()
        knob_spinbox.setMaximumWidth(60)
        knob_spinbox.setMinimum(parameter.choices[0])
        knob_spinbox.setMaximum(parameter.choices[1])
        knob_spinbox.setValue(parameter.value)

        knob = QDial()
        knob.setMinimum(knob_spinbox.minimum())
        knob.setMaximum(knob_spinbox.maximum())
        knob.setValue(parameter.value)
        knob.setFixedSize(constants.KNOB_SIZE, constants.KNOB_SIZE)
        knob.valueChanged.connect(
            lambda new_value: GuiHelper.on_knob_changed(knob, knob_spinbox, parameter, function_to_run))
        knob_spinbox.valueChanged.connect(
            lambda new_value: GuiHelper.on_knob_spinbox_changed(knob_spinbox, knob, parameter, function_to_run))

        if isinstance(parameter, MainParameter):
            if parameter.action_number is None:
                knob_spinbox.setEnabled(False)
                knob.setEnabled(False)

        hbox = QHBoxLayout()
        hbox.addWidget(knob_spinbox)
        hbox.addWidget(knob)
        return hbox

    @staticmethod
    def on_combo_changed(combo: QComboBox, parameter: Parameter, function_to_run: Callable):
        parameter.value = parameter.choices.index(combo.currentText())
        function_to_run(parameter)

    @staticmethod
    def on_knob_changed(knob: QDial, linked_knob_spinbox: QSpinBox, parameter: Parameter, function_to_run: Callable):
        if knob.value() != linked_knob_spinbox.value():
            linked_knob_spinbox.setValue(knob.value())
            parameter.value = knob.value()
            function_to_run(parameter)

    @staticmethod
    def on_knob_spinbox_changed(knob_spinbox: QSpinBox, linked_knob: QDial, parameter: Parameter,
                                function_to_run: Callable):
        if knob_spinbox.value() != linked_knob.value():
            linked_knob.setValue(knob_spinbox.value())
            parameter.value = knob_spinbox.value()
            function_to_run(parameter)

    @staticmethod
    def clear_layout(layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    GuiHelper.clear_layout(child.layout())

    @staticmethod
    def get_spacer() -> QWidget:
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        return spacer
