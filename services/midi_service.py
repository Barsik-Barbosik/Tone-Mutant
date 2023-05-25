import configparser
import threading
import time

import rtmidi
from PySide2.QtCore import QThreadPool

from constants import constants
from constants.enums import SysexType
from external.worker import Worker
from model.instrument import Instrument

SYSEX_FIRST_BYTE = 0xF0
BLOCK_INDEX = 16
SYSEX_TYPE_INDEX = 18
TONE_NAME_RESPONSE_SIZE = 16  # TODO: replace 0F in sysex
DSP_MODULE_RESPONSE_SIZE = 2


class MidiService:
    __instance = None
    __lock = threading.Lock()

    @staticmethod
    def get_instance():
        if MidiService.__instance is None:
            with MidiService.__lock:
                if MidiService.__instance is None:
                    MidiService()
        return MidiService.__instance

    def __init__(self):
        if MidiService.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            MidiService.__instance = self
            self.core = None

            cfg = configparser.ConfigParser()
            cfg.read(constants.CONFIG_FILENAME)
            self.input_name = cfg.get("Midi", "InPort", fallback="")
            self.output_name = cfg.get("Midi", "OutPort", fallback="")
            self.channel = int(cfg.get("Midi Real-Time", "Channel", fallback="0"))

            self.threadpool = QThreadPool()
            self.midi_in = rtmidi.MidiIn()
            self.midi_out = rtmidi.MidiOut()
            self.open_midi_ports()

    def start_midi_worker(self, incoming_message, _):
        self.threadpool.start(Worker(self.process_message, incoming_message))

    def open_midi_ports(self):
        for i in range(self.midi_out.get_port_count()):
            if self.output_name == self.midi_out.get_port_name(i):
                self.midi_out.open_port(port=i)
        for i in range(self.midi_in.get_port_count()):
            if self.input_name == self.midi_in.get_port_name(i):
                self.midi_in.ignore_types(sysex=False, timing=True, active_sense=True)
                self.midi_in.open_port(port=i)
                self.midi_in.set_callback(self.start_midi_worker)

    def close_midi_ports(self):
        self.midi_in.close_port()
        self.midi_out.close_port()
        self.midi_in.delete()
        self.midi_out.delete()

    def verify_midi_ports(self):
        if not self.midi_out.is_port_open() or not self.midi_in.is_port_open():
            self.open_midi_ports()
        if not self.midi_out.is_port_open() or not self.midi_in.is_port_open():
            raise Exception("Unable to open MIDI port. Please verify MIDI settings.")

    def send_sysex(self, sysex_hex_str: str):
        self.verify_midi_ports()
        print("SysEx: " + self.format_as_nice_hex(sysex_hex_str))
        self.midi_out.send_message(bytearray(bytes.fromhex(sysex_hex_str)))
        time.sleep(0.01)

    def request_tone_name(self):
        msg = "F0 44 19 01 7F 00 03 03 00 00 00 00 00 00 00 00 00 00 00 00 00 00 0F 00 F7"
        self.send_sysex(msg)

    def request_dsp_module(self, block_id: int):
        if self.is_block_id_valid(block_id):
            # Array size is always 14 bytes: length is "0D"
            msg_start = "F0 44 19 01 7F 00 03 03 00 00 00 00 00 00 00 00"
            msg_block_id = self.decimal_to_hex(block_id)
            msg_end = "00 55 00 00 00 00 00 F7"

            self.send_sysex(msg_start + msg_block_id + msg_end)

    def request_dsp_params(self, block_id: int):
        if self.is_block_id_valid(block_id):
            # Array size is always 14 bytes: length is "0D"
            msg_start = "F0 44 19 01 7F 00 03 03 00 00 00 00 00 00 00 00"
            msg_block_id = self.decimal_to_hex(block_id)
            msg_end = "00 57 00 00 00 0D 00 F7"

            return self.send_sysex(msg_start + msg_block_id + msg_end)

    def process_message(self, message):
        message, deltatime = message
        print("incoming midi: " + self.format_as_nice_hex(self.list_to_hex_str(message)))
        if len(message) > 3 and message[0] == SYSEX_FIRST_BYTE:
            print("SysEx response type (in hex): " + self.decimal_to_hex(message[SYSEX_TYPE_INDEX]))
            if message[SYSEX_TYPE_INDEX] == SysexType.TONE_NAME.value:
                print("Set tone name callback!")
                response = message[len(message) - 1 - TONE_NAME_RESPONSE_SIZE:len(message) - 1]
                print("Response:\t" + self.format_as_nice_hex(self.list_to_hex_str(response)))
                self.core.process_tone_name_response(response)
            elif message[SYSEX_TYPE_INDEX] == SysexType.DSP_MODULE.value:
                print("Set DSP module callback!")
                block_id = message[BLOCK_INDEX]
                response = message[len(message) - 1 - DSP_MODULE_RESPONSE_SIZE:len(message) - 1]
                print("Response (first byte):\t" + self.format_as_nice_hex(self.list_to_hex_str(response[0])))
                self.core.process_dsp_module_by_block_id_response(block_id, response[0])
            elif message[SYSEX_TYPE_INDEX] == SysexType.DSP_PARAMS.value:
                print("Set DSP params callback!")
                self.core.process_dsp_module_parameters_response(message)

    def send_dsp_module_change_sysex(self, block_id: int, new_dsp_id: int):
        self.send_parameter_change_sysex(block_id, SysexType.DSP_MODULE.value, new_dsp_id)

    def send_dsp_params_change_sysex(self, block_id: int, params_list: list):
        # Array size is always 14 bytes: length is "0D"
        msg_start = "F0 44 19 01 7F 01 03 03 00 00 00 00 00 00 00 00"
        msg_block_param_and_size = self.decimal_to_hex(block_id) + "00 57 00 00 00 0D 00"
        msg_params = self.list_to_hex_str(params_list)
        msg_end = "F7"

        print("Setting DSP Params:\t" + self.format_as_nice_hex(msg_params))
        self.send_sysex(msg_start + msg_block_param_and_size + msg_params + msg_end)

    def send_parameter_change_sysex(self, block_id: int, parameter: int, value: int):
        sysex = self.make_sysex(block_id, parameter, value)
        self.send_sysex(sysex)

    def send_change_tone_msg(self, instrument: Instrument):
        self.midi_out.send_message([0xB0, 0x00, instrument.bank])
        time.sleep(0.01)
        self.midi_out.send_message([0xB0, 0x20, 0x00])
        time.sleep(0.01)
        self.midi_out.send_message([0xC0, instrument.program_change])

        # self.midi_out.send_message(bytearray(bytes.fromhex("B0 00 04")))
        # time.sleep(0.01)
        # self.midi_out.send_message(bytearray(bytes.fromhex("B0 20 00")))
        # time.sleep(0.01)
        # self.midi_out.send_message(bytearray(bytes.fromhex("C0 04")))

    @staticmethod
    def is_block_id_valid(block_id: int):
        return isinstance(int(block_id), int) and 0 <= int(block_id) <= 3

    @staticmethod
    def make_sysex(block_id: int, parameter: int, value: int) -> str:
        return "F0 44 19 01 7F 01 03 03 00 00 00 00 00 00 00 00" \
            + MidiService.decimal_to_hex_hex(block_id) \
            + MidiService.decimal_to_hex_hex(parameter) \
            + "00 00 00 00" \
            + MidiService.decimal_to_hex_hex(value) \
            + "F7"

    @staticmethod
    def decimal_to_hex(decimal_num: int) -> str:
        return "{:02X}".format(decimal_num)

    @staticmethod
    def decimal_to_hex_hex(decimal_num: int) -> str:
        if decimal_num > 32267:
            raise ValueError("Number is too big: {}".format(decimal_num))

        return "{:02X}".format(decimal_num % 128) + " {:02X}".format(decimal_num // 128)

    @staticmethod
    def list_to_hex_str(int_list: list) -> str:
        hex_str = ""
        for int_value in int_list:
            hex_str = hex_str + " " + MidiService.decimal_to_hex(int_value)
        return hex_str

    @staticmethod
    def format_as_nice_hex(input_str: str) -> str:
        string_without_spaces = input_str.replace(" ", "")
        return " ".join(string_without_spaces[i:i + 2] for i in range(0, len(string_without_spaces), 2))
