import configparser

import rtmidi
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QWidget, QLabel, QComboBox, QGridLayout, QHBoxLayout, QPushButton, QSizePolicy

from constants import constants
from constants.constants import DEFAULT_MIDI_IN_PORT, DEFAULT_MIDI_OUT_PORT, DEFAULT_SYNTH_MODEL
from utils.utils import resource_path


class SettingsWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.setWindowTitle("Settings")

        self.core = parent.core

        cfg = configparser.ConfigParser()
        cfg.read(constants.CONFIG_FILENAME)
        self.synthesizer_model = cfg.get('Synthesizer', 'Model', fallback=DEFAULT_SYNTH_MODEL)
        self.input_name = cfg.get('Midi', 'InPort', fallback=DEFAULT_MIDI_IN_PORT)
        self.output_name = cfg.get('Midi', 'OutPort', fallback=DEFAULT_MIDI_OUT_PORT)

        synth_models = ["CT-X3000/5000", "CT-X8000IN/9000IN", "CT-X700/800"]
        input_ports = rtmidi.MidiIn().get_ports()
        output_ports = rtmidi.MidiOut().get_ports()

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.layout = QGridLayout(self)
        self.synthesizer_model_combo = self.create_combo_box("Synthesizer model:", synth_models, self.synthesizer_model)
        self.input_port_combo = self.create_combo_box("MIDI Input port:", input_ports, self.input_name)
        self.output_port_combo = self.create_combo_box("MIDI Output port:", output_ports, self.output_name)
        self.layout.addWidget(spacer, 4, 0, 1, 2)
        self.layout.setRowMinimumHeight(4, 20)
        self.layout.setRowStretch(4, 20)

        button_layout = QHBoxLayout()
        button_layout.addWidget(spacer)
        ok_button = QPushButton(" OK", self)
        ok_button.setIcon(QIcon(resource_path("resources/apply.png")))
        ok_button.clicked.connect(self.ok_button_action)
        cancel_button = QPushButton(" CANCEL", self)
        cancel_button.setIcon(QIcon(resource_path("resources/cancel.png")))
        cancel_button.clicked.connect(self.cancel_button_action)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(spacer)
        self.layout.addLayout(button_layout, 5, 0, 1, 2)

        self.setLayout(self.layout)

        self.show()

    def create_combo_box(self, label_text, items, selection):
        label = QLabel(label_text)
        label.setObjectName("midi-settings-label")
        self.layout.addWidget(label, self.layout.rowCount(), 0)
        combo_box = QComboBox(self)
        combo_box.setObjectName("midi-settings-combo")
        combo_box.addItems(items)
        combo_box.setCurrentText(selection)
        self.layout.addWidget(combo_box, self.layout.rowCount() - 1, 1)
        return combo_box

    def ok_button_action(self):
        cfg = configparser.ConfigParser()
        cfg.read(constants.CONFIG_FILENAME)

        if self.synthesizer_model_combo.currentIndex() != -1:
            self.synthesizer_model = self.synthesizer_model_combo.currentText()
            if not cfg.has_section("Synthesizer"):
                cfg.add_section("Synthesizer")
            cfg.set('Synthesizer', 'Model', self.synthesizer_model)

        if self.input_port_combo.currentIndex() != -1:
            self.input_name = self.input_port_combo.currentText()
            if not cfg.has_section("Midi"):
                cfg.add_section("Midi")
            cfg.set('Midi', 'InPort', self.input_name)

        if self.output_port_combo.currentIndex() != -1:
            self.output_name = self.output_port_combo.currentText()
            if not cfg.has_section("Midi"):
                cfg.add_section("Midi")
            cfg.set('Midi', 'OutPort', self.output_name)

        with open(constants.CONFIG_FILENAME, 'w') as cfg_file:
            cfg.write(cfg_file)

        self.core.tone.synthesizer_model = self.synthesizer_model
        self.core.close_midi_ports()
        self.core.midi_service.open_midi_ports()

        self.close()

    def cancel_button_action(self):
        self.close()
