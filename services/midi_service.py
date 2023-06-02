import configparser
import threading
import time
from collections import deque

import rtmidi
from PySide2.QtCore import QThreadPool

from constants import constants
from constants.enums import SysexType
from external.worker import Worker
from model.instrument import Instrument
from utils.utils import decimal_to_hex, decimal_to_hex_hex, format_as_nice_hex, list_to_hex_str, decimal_to_hex_hex_8bit

# TODO: group all params into enums
SYSEX_FIRST_BYTE = 0xF0
BANK_SELECT_PART1_FIRST_BYTE = 0xB0
BANK_SELECT_PART2 = [0xB0, 0x20, 0x00]
INSTRUMENT_SELECT_FIRST_BYTE = 0xC0

BLOCK_INDEX = 16
SYSEX_TYPE_INDEX = 18

TONE_NAME_RESPONSE_SIZE = 16  # TODO: replace 0F in sysex
MAIN_PARAMETER_RESPONSE_SIZE = 2
MAIN_SHORT_PARAMETER_RESPONSE_SIZE = 1
DSP_MODULE_RESPONSE_SIZE = 2
DSP_PARAMS_RESPONSE_SIZE = 14  # TODO: replace 0D in sysex

MAIN_PARAMETER_NUMBERS = [20, 14, 15]  # TODO: get numbers automatically from main list
MAIN_SHORT_PARAMETER_NUMBERS = [59, 63, 60, 61, 43, 45, 5, 57, 56, 58]


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

            self.bank_select_msg_queue = deque()

            self.threadpool = QThreadPool()
            self.midi_in = rtmidi.MidiIn()
            self.midi_out = rtmidi.MidiOut()
            self.open_midi_ports()

    # def start_midi_worker(self, incoming_message, _):
    #     self.threadpool.start(Worker(self.process_message, incoming_message))

    def open_midi_ports(self):
        for i in range(self.midi_out.get_port_count()):
            if self.output_name == self.midi_out.get_port_name(i):
                self.midi_out.open_port(port=i)
        for i in range(self.midi_in.get_port_count()):
            if self.input_name == self.midi_in.get_port_name(i):
                self.midi_in.ignore_types(sysex=False, timing=True, active_sense=True)
                self.midi_in.open_port(port=i)
                self.midi_in.set_callback(self.process_message)

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
        print("Outgoing SysEx:\t\t" + format_as_nice_hex(sysex_hex_str))
        self.midi_out.send_message(bytearray(bytes.fromhex(sysex_hex_str)))
        time.sleep(0.01)

    def request_tone_name(self):
        msg = "F0 44 19 01 7F 00 03 03 00 00 00 00 00 00 00 00 00 00 00 00 00 00 0F 00 F7"
        self.send_sysex(msg)

    def request_parameter_value(self, block_id: int, parameter: int):
        msg = "F0 44 19 01 7F 00 03 03 00 00 00 00 00 00 00 00" \
              + decimal_to_hex(block_id) + "00" + decimal_to_hex_hex(parameter) + "00 00 00 00 F7"
        self.send_sysex(msg)
        time.sleep(0.1)

    def request_dsp_module(self, block_id: int):
        if self.is_block_id_valid(block_id):
            # Array size is always 14 bytes: length is "0D"
            msg_start = "F0 44 19 01 7F 00 03 03 00 00 00 00 00 00 00 00"
            msg_block_id = decimal_to_hex(block_id)
            msg_end = "00 55 00 00 00 00 00 F7"
            self.send_sysex(msg_start + msg_block_id + msg_end)

    def request_dsp_params(self, block_id: int):
        if self.is_block_id_valid(block_id):
            # Array size is always 14 bytes: length is "0D"
            msg_start = "F0 44 19 01 7F 00 03 03 00 00 00 00 00 00 00 00"
            msg_block_id = decimal_to_hex(block_id)
            msg_end = "00 57 00 00 00 0D 00 F7"
            self.send_sysex(msg_start + msg_block_id + msg_end)

    def process_message(self, message, _):
        message, deltatime = message
        print("Incoming midi msg:\t" + format_as_nice_hex(list_to_hex_str(message)))
        if len(message) > 3 and message[0] == SYSEX_FIRST_BYTE:
            print("\tSysEx response type (as hex): " + decimal_to_hex(message[SYSEX_TYPE_INDEX]))
            if message[SYSEX_TYPE_INDEX] == SysexType.TONE_NAME.value:
                response = message[len(message) - 1 - TONE_NAME_RESPONSE_SIZE:len(message) - 1]
                print("\tTone name response: " + format_as_nice_hex(list_to_hex_str(response)))
                self.core.process_tone_name_response(response)
            elif message[SYSEX_TYPE_INDEX] in MAIN_PARAMETER_NUMBERS:
                block_id = message[BLOCK_INDEX]
                response = message[len(message) - 1 - MAIN_PARAMETER_RESPONSE_SIZE:len(message) - 1]
                print("\tMain parameter response: " + format_as_nice_hex(list_to_hex_str(response)))
                self.core.process_main_parameter_response(message[SYSEX_TYPE_INDEX], block_id, response)
            elif message[SYSEX_TYPE_INDEX] in MAIN_SHORT_PARAMETER_NUMBERS:
                block_id = message[BLOCK_INDEX]
                response = message[len(message) - 1 - MAIN_SHORT_PARAMETER_RESPONSE_SIZE:len(message) - 1]
                print("\tMain parameter response: " + format_as_nice_hex(list_to_hex_str(response)))
                self.core.process_main_parameter_response(message[SYSEX_TYPE_INDEX], block_id, response)
            elif message[SYSEX_TYPE_INDEX] == SysexType.DSP_MODULE.value:
                block_id = message[BLOCK_INDEX]
                response = message[len(message) - 1 - DSP_MODULE_RESPONSE_SIZE:len(message) - 1]
                print("\tDSP module response (first byte as hex): " + decimal_to_hex(response[0]))
                self.core.process_dsp_module_response(block_id, response[0])
            elif message[SYSEX_TYPE_INDEX] == SysexType.DSP_PARAMS.value:
                block_id = message[BLOCK_INDEX]
                response = message[len(message) - 1 - DSP_PARAMS_RESPONSE_SIZE:len(message) - 1]
                print("\tDSP params response: " + format_as_nice_hex(list_to_hex_str(response)))
                self.core.process_dsp_module_parameters_response(block_id, response)
        elif message[0] == BANK_SELECT_PART1_FIRST_BYTE and message != BANK_SELECT_PART2:
            self.bank_select_msg_queue.append(message)
            time.sleep(0.01)
        elif message[0] == INSTRUMENT_SELECT_FIRST_BYTE:
            bank_select_msg = self.get_last_bank_select_message()
            if bank_select_msg is not None:
                print("\tBank select msg: " + format_as_nice_hex(list_to_hex_str(bank_select_msg)))
                print("\tInstrument select msg: " + format_as_nice_hex(list_to_hex_str(message)))
                self.core.process_instrument_select_response(bank_select_msg[2], message[1])
                self.threadpool.start(Worker(self.core.countdown_and_autosynchronize, 2))

    def get_last_bank_select_message(self):
        last_message = None
        while True:
            try:
                last_message = self.bank_select_msg_queue.popleft()
            except IndexError:
                return last_message

    def get_message(self):
        try:
            return self.bank_select_msg_queue.popleft()
        except IndexError:
            return None

    def send_dsp_module_change_sysex(self, block_id: int, new_dsp_id: int):
        self.send_parameter_change_sysex(block_id, SysexType.DSP_MODULE.value, new_dsp_id)

    def send_dsp_params_change_sysex(self, block_id: int, params_list: list):
        # Array size is always 14 bytes: length is "0D"
        msg_start = "F0 44 19 01 7F 01 03 03 00 00 00 00 00 00 00 00"
        msg_block_param_and_size = decimal_to_hex(block_id) + "00 57 00 00 00 0D 00"
        msg_params = list_to_hex_str(params_list)
        msg_end = "F7"
        self.send_sysex(msg_start + msg_block_param_and_size + msg_params + msg_end)

    def send_parameter_change_sysex(self, block_id: int, parameter: int, value: int):
        sysex = self.make_sysex(block_id, parameter, value)
        self.send_sysex(sysex)

    def send_parameter_change_short_sysex(self, block_id: int, parameter: int, value: int):
        sysex = self.make_sysex_short_value(block_id, parameter, value)
        self.send_sysex(sysex)

    def send_atk_rel_parameter_change_sysex(self, block_id: int, parameter: int, value: int):
        sysex = self.make_sysex_8bit_value(block_id, parameter, value)
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

    # TODO: more validations
    @staticmethod
    def is_block_id_valid(block_id: int):
        return isinstance(int(block_id), int) and 0 <= int(block_id) <= 3

    @staticmethod
    def make_sysex(block_id: int, parameter: int, value: int) -> str:
        return "F0 44 19 01 7F 01 03 03 00 00 00 00 00 00 00 00" \
            + decimal_to_hex_hex(block_id) \
            + decimal_to_hex_hex(parameter) \
            + "00 00 00 00" \
            + decimal_to_hex_hex(value) \
            + "F7"

    # Special case for "SHORT_PARAMS" list parameters
    @staticmethod
    def make_sysex_short_value(block_id: int, parameter: int, value: int) -> str:
        return "F0 44 19 01 7F 01 03 03 00 00 00 00 00 00 00 00" \
            + decimal_to_hex_hex(block_id) \
            + decimal_to_hex_hex(parameter) \
            + "00 00 00 00" \
            + decimal_to_hex(value) \
            + "F7"

    # Special case for "Attack time" and "Release time" parameters
    @staticmethod
    def make_sysex_8bit_value(block_id: int, parameter: int, value: int) -> str:
        return "F0 44 19 01 7F 01 03 03 00 00 00 00 00 00 00 00" \
            + decimal_to_hex_hex(block_id) \
            + decimal_to_hex_hex(parameter) \
            + "00 00 00 00" \
            + decimal_to_hex_hex_8bit(value) \
            + "F7"
