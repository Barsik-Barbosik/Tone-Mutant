import configparser

import rtmidi
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QWidget, QLabel, QComboBox, QGridLayout, QHBoxLayout, QPushButton, QSizePolicy, \
    QSpacerItem, QMessageBox

from constants import constants
from constants.constants import DEFAULT_MIDI_IN_PORT, DEFAULT_MIDI_OUT_PORT, DEFAULT_SYNTH_MODEL, CTX_3000_5000, \
    CTX_700_800, CTX_8000IN_9000IN
from utils.utils import resource_path


class SettingsWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setWindowIcon(QIcon(resource_path("resources/settings.png")))

        self.core = parent.core
        self.cfg = self._load_config()

        self.synthesizer_model = self.cfg.get('Synthesizer', 'Model', fallback=DEFAULT_SYNTH_MODEL)
        self.input_name = self.cfg.get('Midi', 'InPort', fallback=DEFAULT_MIDI_IN_PORT)
        self.output_name = self.cfg.get('Midi', 'OutPort', fallback=DEFAULT_MIDI_OUT_PORT)
        self.is_expert_mode_enabled = self.cfg.get('Expert', 'is_expert_mode_enabled', fallback="false")

        self.synth_models = [CTX_3000_5000, CTX_8000IN_9000IN, CTX_700_800]
        self.input_ports = rtmidi.MidiIn().get_ports()
        self.output_ports = rtmidi.MidiOut().get_ports()
        self.expert_mode_values = ["OFF", "ON"]
        self.expert_mode_mapping = {"OFF": "false", "ON": "true"}
        self.inverse_expert_mode_mapping = {v: k for k, v in self.expert_mode_mapping.items()}

        self.layout = QGridLayout(self)
        self._initialize_ui()
        self.show()

    def _load_config(self):
        """Load the application configuration."""
        cfg = configparser.ConfigParser()
        cfg.read(constants.CONFIG_FILENAME)
        return cfg

    def _initialize_ui(self):
        """Set up the user interface."""
        self._add_combo_box("Synthesizer Model:", self.synth_models, self.synthesizer_model, 0)
        self._add_spacer(1)
        self._add_combo_box("MIDI Input Port:", self.input_ports, self.input_name, 2)
        self._add_combo_box("MIDI Output Port:", self.output_ports, self.output_name, 3)
        self._add_spacer(4)
        self._add_combo_box("Expert Mode:", self.expert_mode_values,
                            self.inverse_expert_mode_mapping.get(self.is_expert_mode_enabled, "OFF"), 5)
        self._add_spacer(6)
        self._add_action_buttons(7)

    def _add_combo_box(self, label_text, items, selection, row):
        """Helper method to add a labeled combo box."""
        label = QLabel(label_text)
        label.setObjectName("midi-settings-label")
        self.layout.addWidget(label, row, 0)

        combo_box = QComboBox(self)
        combo_box.setObjectName("midi-settings-combo")
        combo_box.addItems(items)
        combo_box.setCurrentText(selection)
        self.layout.addWidget(combo_box, row, 1)

        attribute_name = self._format_attribute_name(label_text)
        setattr(self, attribute_name, combo_box)

    def _add_spacer(self, row):
        """Helper method to add a vertical spacer."""
        spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout.addItem(spacer, row, 0, 1, 2)

    def _add_action_buttons(self, row):
        """Helper method to add OK and Cancel buttons."""
        button_layout = QHBoxLayout()

        ok_button = QPushButton(" OK", self)
        ok_button.setIcon(QIcon(resource_path("resources/apply.png")))
        ok_button.clicked.connect(self._apply_settings)
        button_layout.addWidget(ok_button)

        cancel_button = QPushButton(" CANCEL", self)
        cancel_button.setIcon(QIcon(resource_path("resources/cancel.png")))
        cancel_button.clicked.connect(self._close_window)
        button_layout.addWidget(cancel_button)

        self.layout.addLayout(button_layout, row, 0, 1, 2)

    def _apply_settings(self):
        """Apply the settings and update the configuration file."""
        expert_mode_changed = (
                self.is_expert_mode_enabled != self.expert_mode_mapping[self.expert_mode_combo.currentText()]
        )

        self._update_config('Synthesizer', 'Model', self.synthesizer_model_combo.currentText())
        self._update_config('Midi', 'InPort', self.midi_input_port_combo.currentText())
        self._update_config('Midi', 'OutPort', self.midi_output_port_combo.currentText())
        self._update_config('Expert', 'is_expert_mode_enabled',
                            self.expert_mode_mapping[self.expert_mode_combo.currentText()])

        with open(constants.CONFIG_FILENAME, 'w') as cfg_file:
            self.cfg.write(cfg_file)

        if expert_mode_changed:
            self._show_restart_required_message()

        self._refresh_core()
        self._close_window()

    def _refresh_core(self):
        """Refresh the core settings after applying changes."""
        self.core.tone.synthesizer_model = self.synthesizer_model_combo.currentText()

        try:
            self.core.close_midi_ports()
            self.core.open_midi_ports()
        except Exception as e:
            self.core.log(f"[ERROR] Unable to open MIDI port: {e}")

        self.core.main_window.central_widget.populate_instrument_list()

    def _show_restart_required_message(self):
        """Show a message box indicating restart is required."""
        message_box = QMessageBox(self)
        message_box.setIcon(QMessageBox.Information)
        message_box.setWindowTitle("Restart Required")
        message_box.setText("Changes to Expert Mode will take effect after restarting the application.")
        message_box.setStandardButtons(QMessageBox.Ok)
        message_box.exec_()

    def _close_window(self):
        """Close and clean up the settings window."""
        self.close()
        self.deleteLater()

    def _update_config(self, section, option, value):
        """Update the configuration file."""
        if not self.cfg.has_section(section):
            self.cfg.add_section(section)
        self.cfg.set(section, option, value)

    @staticmethod
    def _format_attribute_name(label_text):
        """Format a label text into a valid attribute name."""
        return label_text.lower().replace(" ", "_").replace(":", "") + "_combo"
