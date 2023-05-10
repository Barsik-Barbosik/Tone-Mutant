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
        self.input_name = cfg.get('Midi', 'InPort', fallback="")
        self.output_name = cfg.get('Midi', 'OutPort', fallback="")
        self.channel = int(cfg.get('Midi Real-Time', 'Channel', fallback="0"))

        input_ports = rtmidi.MidiIn().get_ports()
        output_ports = rtmidi.MidiOut().get_ports()
        channels = ["0 - Upper keyboard 1", "32 - MIDI In 1"]

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.layout = QGridLayout(self)
        self.input_port_combo = self.create_combo_box("Input port:", input_ports, self.input_name)
        self.output_port_combo = self.create_combo_box("Output port:", output_ports, self.output_name)
        self.channel_combo = self.create_combo_box("Channel:", channels,
                                                   channels[1] if self.channel == 32 else channels[0])
        self.layout.addWidget(spacer, 4, 0, 1, 2)
        self.layout.setRowMinimumHeight(4, 20)
        self.layout.setRowStretch(4, 20)

        button_layout = QHBoxLayout()
        button_layout.addWidget(spacer)
        ok_button = QPushButton("OK", self)
        ok_button.clicked.connect(self.ok_button_action)
        cancel_button = QPushButton("CANCEL", self)
        cancel_button.clicked.connect(self.cancel_button_action)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(spacer)
        self.layout.addLayout(button_layout, 5, 0, 1, 2)

        self.setLayout(self.layout)

        self.show()

    def create_combo_box(self, label, items, selection):
        self.layout.addWidget(QLabel(label), self.layout.rowCount(), 0)
        combo_box = QComboBox(self)
        combo_box.addItems(items)
        combo_box.setCurrentText(selection)
        self.layout.addWidget(combo_box, self.layout.rowCount() - 1, 1)
        return combo_box

    def ok_button_action(self):
        cfg = configparser.ConfigParser()
        cfg.read(CONFIG_FILENAME)

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

        if self.channel_combo.currentIndex() != -1:
            self.channel = 32 if self.channel_combo.currentIndex() == 1 else 0
            if not cfg.has_section("Midi Real-Time"):
                cfg.add_section("Midi Real-Time")
            cfg.set("Midi Real-Time", "Channel", str(self.channel))

        with open(CONFIG_FILENAME, 'w') as cfg_file:
            cfg.write(cfg_file)

        self.close()

    def cancel_button_action(self):
        self.close()
