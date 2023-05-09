import configparser

import rtmidi
from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QGridLayout, QHBoxLayout, QPushButton, QSizePolicy

CONFIG_FILENAME = 'config.cfg'


class MidiSettingsWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("MIDI settings")

        cfg = configparser.ConfigParser()
        cfg.read(CONFIG_FILENAME)
        input_name = cfg.get('Midi', 'InPort', fallback="")
        output_name = cfg.get('Midi', 'OutPort', fallback="")
        realtime_channel = int(cfg.get('Midi Real-Time', 'Channel', fallback="0"))

        input_ports = rtmidi.MidiIn().get_ports()
        output_ports = rtmidi.MidiOut().get_ports()
        channels = ["0  Upper keyboard 1", "32  MIDI In 1"]

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.layout = QGridLayout(self)
        self.create_combo_box("Input port:", input_ports, input_name)
        self.create_combo_box("Output port:", output_ports, output_name)
        self.create_combo_box("Channel:", channels, "32" if realtime_channel == 32 else "16")
        self.layout.addWidget(spacer, 4, 0, 1, 2)
        self.layout.setRowMinimumHeight(4, 20)
        self.layout.setRowStretch(4, 20)

        button_layout = QHBoxLayout()
        button_layout.addWidget(spacer)
        ok_button = QPushButton("OK", self)
        cancel_button = QPushButton("CANCEL", self)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(spacer)
        self.layout.addLayout(button_layout, 5, 0, 1, 2)

        self.setLayout(self.layout)

    def create_combo_box(self, label, items, default_selection):
        self.layout.addWidget(QLabel(label), self.layout.rowCount(), 0)
        combo_box = QComboBox(self)
        combo_box.addItems(items)
        combo_box.setCurrentText(default_selection)
        self.layout.addWidget(combo_box, self.layout.rowCount() - 1, 1)
        return combo_box
