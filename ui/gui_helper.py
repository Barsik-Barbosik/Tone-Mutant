from ui.i18n import tr, parameter_help
import configparser
from typing import Callable

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDial, \
    QHBoxLayout, QSpinBox, QComboBox, QWidget, QSizePolicy, QGridLayout, QMainWindow, \
    QDockWidget, QFrame, QTabWidget, QVBoxLayout, QTextEdit, QPushButton, QApplication
from PySide6.QtWidgets import QLabel

from constants import constants
from constants.constants import DEFAULT_SYNTH_MODEL, CTX_700_800
from constants.enums import ParameterType
from models.parameter import Parameter, MainParameter
from utils.syntax_highlighters.sysex_highlighter import SysexHighlighter
from utils.utils import resource_path


class GuiHelper:

    @staticmethod
    def init_top_dock(main_window: QMainWindow):
        top_dock = QDockWidget(tr("Layer Mixer"), main_window)
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
        right_dock = QDockWidget(tr("Right Dock"), main_window)
        right_dock.setTitleBarWidget(QWidget())
        right_dock.setFloating(False)

        # Create tabs (Help and Log)
        help_tab = GuiHelper.create_help_tab(main_window)
        log_tab = GuiHelper.create_log_tab(main_window)

        # Set up the tab widget
        tab_widget = QTabWidget(main_window)
        tab_widget.setMinimumHeight(500)
        tab_widget.setMinimumWidth(300)
        tab_widget.addTab(help_tab, tr("Info / Help"))
        tab_widget.addTab(log_tab, tr("Log"))

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

        if GuiHelper.is_expert_mode_enabled():
            GuiHelper.add_midi_msg_input(log_tab_layout, main_window)

        log_tab.setLayout(log_tab_layout)
        return log_tab

    @staticmethod
    def is_expert_mode_enabled() -> bool:
        """Checks if expert mode is enabled."""
        cfg = configparser.ConfigParser()
        cfg.read(constants.CONFIG_FILENAME)
        return cfg.get("Expert", "is_expert_mode_enabled", fallback="false").lower() == "true"

    @staticmethod
    def has_user_memory() -> bool:
        """Checks if synthesizer model has user memory."""
        cfg = configparser.ConfigParser()
        cfg.read(constants.CONFIG_FILENAME)
        return not cfg.get("Synthesizer", "model", fallback=DEFAULT_SYNTH_MODEL) == CTX_700_800

    @staticmethod
    def add_midi_msg_input(log_tab_layout: QVBoxLayout, main_window: QMainWindow):
        """Adds the MIDI message input section to the log tab."""
        midi_msg_input = QTextEdit(main_window)
        midi_msg_input.setAccessibleName(tr("Custom MIDI message"))
        midi_msg_input.setAccessibleDescription(tr("Hexadecimal bytes. Tab moves to Send MIDI Message."))
        midi_msg_input.setTabChangesFocus(True)
        midi_msg_input.setPlaceholderText(tr("MIDI message..."))
        midi_msg_input.setMaximumHeight(80)
        SysexHighlighter(midi_msg_input.document())
        log_tab_layout.addWidget(midi_msg_input)

        submit_button = QPushButton(tr(" Send MIDI Message"))
        submit_button.setIcon(QIcon(resource_path("resources/send.png")))
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

            label = QLabel(tr(dsp_param.name + ":"))
            label.setObjectName(label_class)
            qgrid_layout.addWidget(label, row, column)
            if dsp_param.type == ParameterType.COMBO:
                control = GuiHelper.create_combo_input(dsp_param, function_to_run)
                label.setBuddy(control)
                qgrid_layout.addWidget(control, row, column + 1)
            elif dsp_param.type in [ParameterType.KNOB, ParameterType.KNOB_X2, ParameterType.SPECIAL_ATK_REL_KNOB,
                                    ParameterType.SPECIAL_DELAY_KNOB]:
                controls = GuiHelper.create_knob_input(dsp_param, function_to_run)
                label.setBuddy(controls.itemAt(0).widget())
                qgrid_layout.addLayout(controls, row, column + 1)
        return right_side_items_count

    @staticmethod
    def create_combo_input(parameter: Parameter, function_to_run: Callable) -> QComboBox:
        combo_box = QComboBox()
        combo_box.setAccessibleName(tr(parameter.name))
        combo_box.setAccessibleDescription(parameter_help(parameter))
        if len(parameter.choices) > 1 and parameter.choices[1] is not None and len(parameter.choices[1]) > 30:
            # amp cabinet types
            combo_box.setObjectName("fat-combo-box")
            combo_box.setMaximumWidth(150)
        combo_box.addItems([tr(choice) for choice in parameter.choices])
        combo_box.setCurrentIndex(parameter.value)
        combo_box.currentIndexChanged.connect(
            lambda new_value: GuiHelper.on_combo_changed(combo_box, parameter, function_to_run))
        return combo_box

    @staticmethod
    def create_knob_input(parameter: Parameter, function_to_run: Callable) -> QHBoxLayout:
        knob_spinbox = QSpinBox()
        knob_spinbox.setAccessibleName(tr(parameter.name))
        knob_spinbox.setAccessibleDescription(
            "{} Rango de {} a {}. Escriba un valor o use las flechas arriba y abajo.".format(
                parameter_help(parameter), parameter.choices[0], parameter.choices[1]))
        # Commit typed numbers on Enter or focus loss, avoiding partial MIDI values.
        knob_spinbox.setKeyboardTracking(False)
        knob_spinbox.setMaximumWidth(60)
        knob_spinbox.setMinimum(parameter.choices[0])
        knob_spinbox.setMaximum(parameter.choices[1])
        knob_spinbox.setValue(parameter.value)

        knob = QDial()
        knob.setAccessibleName(tr(parameter.name + " dial"))
        knob.setAccessibleDescription(parameter_help(parameter))
        # The linked native spin box offers the same value without a duplicate Tab stop.
        knob.setFocusPolicy(Qt.NoFocus)
        knob.setMinimum(knob_spinbox.minimum())
        knob.setMaximum(knob_spinbox.maximum())
        knob.setValue(parameter.value)
        knob.setFixedSize(constants.KNOB_SIZE, constants.KNOB_SIZE)
        knob.valueChanged.connect(
            lambda new_value: GuiHelper.on_knob_changed(knob, knob_spinbox, parameter, function_to_run))
        knob_spinbox.valueChanged.connect(
            lambda new_value: GuiHelper.on_knob_spinbox_changed(knob_spinbox, knob, parameter, function_to_run))

        if isinstance(parameter, MainParameter):
            if parameter.param_number is None:
                knob_spinbox.setEnabled(False)
                knob.setEnabled(False)

        hbox = QHBoxLayout()
        hbox.addWidget(knob_spinbox)
        hbox.addWidget(knob)
        return hbox

    @staticmethod
    def on_combo_changed(combo: QComboBox, parameter: Parameter, function_to_run: Callable):
        parameter.value = combo.currentIndex()
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
            focused = QApplication.focusWidget()
            for widget in GuiHelper.layout_widgets(layout):
                if widget == focused or widget.isAncestorOf(focused):
                    name = widget.accessibleName()
                    if name:
                        kind = type(widget)

                        def restore_focus(layout=layout, name=name, kind=kind):
                            try:
                                for replacement in GuiHelper.layout_widgets(layout):
                                    if type(replacement) == kind and replacement.accessibleName() == name:
                                        replacement.setFocus(Qt.OtherFocusReason)
                                        break
                            except RuntimeError:
                                pass  # The whole window may have closed meanwhile.

                        QTimer.singleShot(0, restore_focus)
                    break
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    GuiHelper.clear_layout(child.layout())

    @staticmethod
    def layout_widgets(layout):
        for index in range(layout.count()):
            item = layout.itemAt(index)
            if item.widget() is not None:
                yield item.widget()
            elif item.layout() is not None:
                yield from GuiHelper.layout_widgets(item.layout())

    @staticmethod
    def get_spacer() -> QWidget:
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        return spacer

    @staticmethod
    def get_green_icon():
        return QIcon(resource_path("resources/green.png"))

    @staticmethod
    def get_white_icon():
        return QIcon(resource_path("resources/white.png"))
