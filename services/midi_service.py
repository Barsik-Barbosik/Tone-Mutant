import configparser
import threading
import time
from collections import deque

import rtmidi
from PySide2.QtCore import QReadWriteLock

from constants import constants
from constants.constants import DEFAULT_MIDI_IN_PORT, DEFAULT_MIDI_OUT_PORT, DEFAULT_MIDI_CHANNEL
from constants.enums import SysexType, SysexId, Size
from external.worker import Worker
from model.instrument import Instrument
from utils.utils import int_to_hex, int_to_lsb_msb, format_as_nice_hex, list_to_hex_str, \
    int_to_lsb_msb_8bit, size_to_lsb_msb, lsb_msb_to_int

# TODO: group all params into enums; use for different log highlighting colors
SYSEX_FIRST_BYTE = 0xF0
CC_FIRST_BYTE = 0xB0  # for channel 0
CC_BANK_SELECT_MSB = 0x00
CC_BANK_SELECT_LSB = 0x20  # transmit: 0x00, receive: ignored
INSTRUMENT_SELECT_FIRST_BYTE = 0xC0

BLOCK_INDEX = 16
SYSEX_TYPE_INDEX = 18

MAIN_PARAMETER_NUMBERS = [20, 14, 15]  # TODO: get numbers automatically from main list
MAIN_SHORT_PARAMETER_NUMBERS = [59, 63, 60, 61, 43, 45, 5, 57, 56, 58, 200]


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
            self.lock = QReadWriteLock()
            self.bank_select_msg_queue = deque()
            self.active_sync_job_count = 0

            self.midi_in = None
            self.midi_out = None
            self.input_name = None
            self.output_name = None
            self.channel = None

            self.open_midi_ports()

    def open_midi_ports(self):
        self.midi_in = rtmidi.MidiIn()
        self.midi_out = rtmidi.MidiOut()

        cfg = configparser.ConfigParser()
        cfg.read(constants.CONFIG_FILENAME)
        self.input_name = cfg.get("Midi", "InPort", fallback=DEFAULT_MIDI_IN_PORT)
        self.output_name = cfg.get("Midi", "OutPort", fallback=DEFAULT_MIDI_OUT_PORT)
        self.channel = DEFAULT_MIDI_CHANNEL

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

    def check_and_reopen_midi_ports(self):
        if not self.midi_out.is_port_open() or not self.midi_in.is_port_open():
            self.open_midi_ports()
        if not self.midi_out.is_port_open() or not self.midi_in.is_port_open():
            raise Exception("Unable to open MIDI port. Please check the MIDI settings.")

    def send_sysex(self, sysex_hex_str: str):
        self.check_and_reopen_midi_ports()
        self.core.main_window.log_texbox.log("[MIDI OUT]\n" + format_as_nice_hex(sysex_hex_str))
        self.lock.lockForWrite()
        self.active_sync_job_count = self.active_sync_job_count + 1
        self.midi_out.send_message(bytearray(bytes.fromhex(sysex_hex_str)))
        self.lock.unlock()
        time.sleep(0.01)

    def send_midi_msg(self, msg_str: str):
        self.check_and_reopen_midi_ports()
        self.core.main_window.log_texbox.log("[MIDI OUT] " + format_as_nice_hex(msg_str))
        self.lock.lockForWrite()

        try:
            self.active_sync_job_count = self.active_sync_job_count + 1
            self.midi_out.send_message(bytearray(bytes.fromhex(msg_str)))
        except Exception as e:
            self.core.main_window.show_error_msg(str(e))

        self.lock.unlock()
        time.sleep(0.01)

    def request_tone_name(self):
        size = size_to_lsb_msb(Size.TONE_NAME)
        msg = "F0 44 19 01 7F 00 03 03 00 00 00 00 00 00 00 00 00 00 00 00 00 00" + size + "F7"
        self.send_sysex(msg)

    def request_parameter_value(self, block_id: int, parameter: int):
        msg = "F0 44 19 01 7F 00 03 03 00 00 00 00 00 00 00 00" \
              + int_to_lsb_msb(block_id) + int_to_lsb_msb(parameter) + "00 00 00 00 F7"
        self.send_sysex(msg)
        # time.sleep(0.1)

    def request_dsp_module(self, block_id: int):
        msg_start = "F0 44 19 01 7F 00 03 03 00 00 00 00 00 00 00 00"
        msg_block_id = int_to_lsb_msb(block_id)
        msg_end = "55 00 00 00 00 00 F7"
        self.send_sysex(msg_start + msg_block_id + msg_end)

    def request_dsp_params(self, block_id: int):
        size = size_to_lsb_msb(Size.DSP_PARAMS)
        msg_start = "F0 44 19 01 7F 00 03 03 00 00 00 00 00 00 00 00"
        msg_block_id = int_to_lsb_msb(block_id)
        msg_end = "57 00 00 00" + size + "F7"
        self.send_sysex(msg_start + msg_block_id + msg_end)

    def process_message(self, message, _):
        message, deltatime = message

        self.lock.lockForWrite()
        self.active_sync_job_count = max(0, self.active_sync_job_count - 1)  # count-- until 0
        self.lock.unlock()

        if message[0] == SYSEX_FIRST_BYTE and message[1] == SysexId.CASIO:
            block_id = lsb_msb_to_int(message[BLOCK_INDEX], message[BLOCK_INDEX + 1])
            sysex_type = lsb_msb_to_int(message[SYSEX_TYPE_INDEX], message[SYSEX_TYPE_INDEX + 1])
            if sysex_type == SysexType.TONE_NAME.value:
                self.log("[MIDI IN] Tone Name\n", message)
                response = message[-1 - Size.TONE_NAME:-1]
                self.core.process_tone_name_response(response)
            elif sysex_type in MAIN_PARAMETER_NUMBERS:
                self.log("[MIDI IN] Parameter\n", message)
                response = message[-1 - Size.MAIN_PARAMETER:-1]
                self.core.process_main_parameter_response(sysex_type, block_id, response)  # 2 bytes
            elif sysex_type in MAIN_SHORT_PARAMETER_NUMBERS:
                self.log("[MIDI IN] Parameter\n", message)
                response = message[-1 - Size.MAIN_PARAMETER_SHORT:-1]
                self.core.process_main_parameter_response(sysex_type, block_id, response[:1])  # 1 byte
            elif sysex_type == SysexType.DSP_MODULE.value:
                self.log("[MIDI IN] DSP module\n", message)
                response = message[-1 - Size.DSP_MODULE:-1]
                self.core.process_dsp_module_response(block_id, response[0])
            elif sysex_type == SysexType.DSP_PARAMS.value:
                self.log("[MIDI IN] DSP parameters\n", message)
                response = message[-1 - Size.DSP_PARAMS:-1]
                self.core.process_dsp_module_parameters_response(block_id, response)
            else:
                self.log("[MIDI IN]\n", message)
        elif message[0] == SYSEX_FIRST_BYTE and message[1] == SysexId.REAL_TIME:
            self.log("[MIDI IN] Real Time SysEx\n", message)
        elif message[0] == CC_FIRST_BYTE and message[1] == CC_BANK_SELECT_MSB:
            self.log("[MIDI IN] Bank change MSB\n", message)
            self.bank_select_msg_queue.append(message)
            time.sleep(0.01)
        elif message[0] == CC_FIRST_BYTE and message[1] == CC_BANK_SELECT_LSB:
            self.log("[MIDI IN] Bank change LSB\n", message)
        # elif message[0] == CC_FIRST_BYTE:
        #     self.log("[MIDI IN] CC: ", message)
        elif message[0] == INSTRUMENT_SELECT_FIRST_BYTE:
            self.log("[MIDI IN] Program change\n", message)
            bank_select_msg = self.get_last_bank_select_message()
            if bank_select_msg is not None:
                self.core.process_instrument_select_response(bank_select_msg[2], message[1])

                worker = Worker(self.core.countdown_and_autosynchronize, 2)
                worker.signals.error.connect(lambda error: print(f"Error: {error}"))
                worker.start()

        else:
            self.log("[MIDI IN] ", message)

    def log(self, title, message):
        self.core.main_window.log_texbox.log(title + format_as_nice_hex(list_to_hex_str(message)))

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

    def send_dsp_bypass_sysex(self, block_id: int, bypass: bool):
        value = 1 if bypass else 0
        self.send_parameter_change_short_sysex(block_id, SysexType.DSP_BYPASS.value, value)

    def send_dsp_params_change_sysex(self, block_id: int, params_list: list):
        # Array size is always 14 bytes: length is "0D" TODO: use size
        msg_start = "F0 44 19 01 7F 01 03 03 00 00 00 00 00 00 00 00"
        msg_block_param_and_size = int_to_lsb_msb(block_id) + "57 00 00 00 0D 00"
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
        self.midi_out.send_message([CC_FIRST_BYTE, CC_BANK_SELECT_MSB, instrument.bank])
        time.sleep(0.01)
        self.midi_out.send_message([CC_FIRST_BYTE, CC_BANK_SELECT_LSB, 0x00])
        time.sleep(0.01)
        self.midi_out.send_message([INSTRUMENT_SELECT_FIRST_BYTE, instrument.program])

    @staticmethod
    def make_sysex(block_id: int, parameter: int, value: int) -> str:
        return "F0 44 19 01 7F 01 03 03 00 00 00 00 00 00 00 00" \
            + int_to_lsb_msb(block_id) \
            + int_to_lsb_msb(parameter) \
            + "00 00 00 00" \
            + int_to_lsb_msb(value) \
            + "F7"

    # Special case for "SHORT_PARAMS" list parameters
    @staticmethod
    def make_sysex_short_value(block_id: int, parameter: int, value: int) -> str:
        return "F0 44 19 01 7F 01 03 03 00 00 00 00 00 00 00 00" \
            + int_to_lsb_msb(block_id) \
            + int_to_lsb_msb(parameter) \
            + "00 00 00 00" \
            + int_to_hex(value) \
            + "F7"

    # Special case for "Attack time" and "Release time" parameters
    @staticmethod
    def make_sysex_8bit_value(block_id: int, parameter: int, value: int) -> str:
        return "F0 44 19 01 7F 01 03 03 00 00 00 00 00 00 00 00" \
            + int_to_lsb_msb(block_id) \
            + int_to_lsb_msb(parameter) \
            + "00 00 00 00" \
            + int_to_lsb_msb_8bit(value) \
            + "F7"
