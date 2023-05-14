import configparser
import struct
import time

import rtmidi

CONFIG_FILENAME = 'config.cfg'


class Midi:

    def __init__(self):
        cfg = configparser.ConfigParser()
        cfg.read(CONFIG_FILENAME)
        self.input_name = cfg.get('Midi', 'InPort', fallback="")
        self.output_name = cfg.get('Midi', 'OutPort', fallback="")
        self.channel = int(cfg.get('Midi Real-Time', 'Channel', fallback="0"))

        self.midi_in = rtmidi.MidiIn()
        self.midi_out = rtmidi.MidiOut()
        self.open_midi_ports()

    def open_midi_ports(self):
        for i in range(self.midi_out.get_port_count()):
            if self.output_name == self.midi_out.get_port_name(i):
                self.midi_out.open_port(port=i)
        for i in range(self.midi_in.get_port_count()):
            if self.input_name == self.midi_in.get_port_name(i):
                self.midi_in.open_port(port=i)

    def close_midi_ports(self):
        self.midi_in.close_port()
        self.midi_out.close_port()
        self.midi_in.delete()
        self.midi_out.delete()

    def send_sysex(self, packet):
        print("SysEx: " + packet.hex(" ").upper())

        if not self.midi_out.is_port_open() or not self.midi_in.is_port_open():
            raise Exception("Could not find the named port. Please check MIDI settings.")

        self.midi_in.ignore_types(sysex=False)
        self.flush_input_queue()
        self.midi_out.send_message(bytearray(packet))
        self.flush_input_queue()

    def flush_input_queue(self):
        time.sleep(0.01)
        self.midi_in.get_message()

    def set_parameter(self, parameter, data, block0=0):
        sysex = self.make_simple_sys_ex(parameter, data, block0)
        self.send_sysex(sysex)

    def set_dsp_parameters(self, dsp_params):
        # Array size is always 14 bytes: length is "0D"
        msg_start = bytes.fromhex("F0 44 19 01 7F 01 03 03 00 00 00 00 00 00 00 00 00 00 57 00 00 00 0D 00")
        msg_end = bytes.fromhex("F7")
        self.send_sysex(msg_start + dsp_params + msg_end)

    def make_simple_sys_ex(self, parameter, data, block0=0):
        return bytes.fromhex("F0 44 19 01 7F 01 03 03 00 00 00 00 00 00 00 00") + self.decimal_to_two_bytes(block0) \
            + self.decimal_to_two_bytes(parameter) + bytes.fromhex("00 00 00 00") \
            + self.decimal_to_two_bytes(data) + bytes.fromhex("F7")

    @staticmethod
    def make_sys_ex(parameter, data, category=3, memory=3, parameter_set=0, block0=0):
        return bytes.fromhex("F0 44 19 01 7F 01") \
            + struct.pack("<BBHHHHHHHH", category, memory, parameter_set, 0, 0, 0, block0, parameter, 0, 0) \
            + data + bytes.fromhex("F7")

    @staticmethod
    def make_program_change(prgm, bankMSB, bankLSB=0, channel=0):
        return struct.pack("<BBBBBBBB", 0xB0 + channel, 0x00, bankMSB, 0xB0 + channel, 0x20, bankLSB, 0xC0 + channel,
                           prgm)

    @staticmethod
    def decimal_to_hex(decimal_num):
        return '{:02x}'.format(decimal_num)

    @staticmethod
    def decimal_to_two_bytes(decimal_num):
        if decimal_num > 32267:
            raise ValueError("Number is too big: {}".format(decimal_num))

        return struct.pack("<BB", decimal_num % 128, decimal_num // 128)
