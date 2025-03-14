import configparser
import threading
import time
from collections import deque

import rtmidi
from PySide2.QtCore import QReadWriteLock

from constants import constants
from constants.constants import DEFAULT_MIDI_IN_PORT, DEFAULT_MIDI_OUT_PORT, DEFAULT_MIDI_CHANNEL
from constants.enums import SysexType, SysexId, Size
from models.instrument import Instrument
from utils.utils import int_to_hex, int_to_lsb_msb, format_as_nice_hex, list_to_hex_str, \
    int_to_lsb_msb_8bit, size_to_lsb_msb, lsb_msb_to_int
from utils.worker import Worker

# TODO: group all params into enums; use for different log highlighting colors
SYSEX_FIRST_BYTE = 0xF0
CC_FIRST_BYTE = 0xB0  # for channel 0
CC_BANK_SELECT_MSB = 0x00
CC_BANK_SELECT_LSB = 0x20  # transmit: 0x00, receive: ignored
INSTRUMENT_SELECT_FIRST_BYTE_CH0 = 0xC0
INSTRUMENT_SELECT_FIRST_BYTE_CH1 = 0xC1
INSTRUMENT_SELECT_FIRST_BYTE_CH2 = 0xC2
INSTRUMENT_SELECT_FIRST_BYTE_CH3 = 0xC3

MEMORY_1 = 1  # Synthesizer's user memory area
MEMORY_3 = 3  # 3 is real-time, current tone

BLOCK_0_INDEX = 16
SYSEX_TYPE_INDEX = 18
PARAM_SET_INDEX = 8


class MidiService:
    __instance = None
    __lock = threading.Lock()
    IS_DEBUG_MODE = False

    @staticmethod
    def get_instance():
        if MidiService.__instance is None:
            with MidiService.__lock:
                if MidiService.__instance is None:
                    MidiService()
        return MidiService.__instance

    def __init__(self, parent):
        if MidiService.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            MidiService.__instance = self
            self.core = parent
            self.lock = QReadWriteLock()
            self.bank_select_msg_queue = deque()
            self.active_sync_job_count = 0

            self.midi_in = None
            self.midi_out = None
            self.input_name = None
            self.output_name = None
            self.channel = None
            self.short_params = [234, 237]  # volume, pan
            self.long_params = []

            for param in self.core.tone.main_parameter_list:
                if param.name in constants.SHORT_PARAMS:
                    self.short_params.append(param.param_number)
                else:
                    self.long_params.append(param.param_number)

            for param in self.core.tone.advanced_parameter_list:
                if param.name in constants.SHORT_PARAMS:
                    self.short_params.append(param.param_number)
                else:
                    self.long_params.append(param.param_number)

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

    def provide_midi_ports(self):
        self.check_and_reopen_midi_ports()
        return self.midi_in, self.midi_out

    def send_sysex(self, sysex_hex_str: str):
        self.lock.lockForWrite()
        try:
            self.check_and_reopen_midi_ports()
            self.core.log("[MIDI OUT]\n" + format_as_nice_hex(sysex_hex_str))
            self.active_sync_job_count = self.active_sync_job_count + 1
            self.midi_out.send_message(bytearray(bytes.fromhex(sysex_hex_str)))
        except Exception as e:
            self.core.show_error_msg(str(e))
        finally:
            self.lock.unlock()
        time.sleep(0.01)

    def send_custom_midi_msg(self, msg_str: str):
        self.lock.lockForWrite()
        try:
            self.check_and_reopen_midi_ports()
            msg_hex: str = format_as_nice_hex(msg_str)
            line_break = "\n" if msg_hex is not None and msg_hex.startswith("F0") else ""
            self.core.log("[MIDI OUT]" + line_break + msg_hex)
            self.active_sync_job_count = self.active_sync_job_count + 1
            self.midi_out.send_message(bytearray(bytes.fromhex(msg_str)))
        except Exception as e:
            self.core.show_error_msg(str(e))
        finally:
            self.lock.unlock()
        time.sleep(0.01)

    def request_tone_name(self):
        size = size_to_lsb_msb(Size.TONE_NAME)
        msg = "F0 44 19 01 7F 00 03 03 00 00 00 00 00 00 00 00 00 00 00 00 00 00" + size + "F7"
        self.send_sysex(msg)

    def request_parameter_value(self, block0: int, parameter: int):
        msg = "F0 44 19 01 7F 00 03 03 00 00 00 00 00 00 00 00" \
              + int_to_lsb_msb(block0) + int_to_lsb_msb(parameter) + "00 00 00 00 F7"
        self.send_sysex(msg)
        # time.sleep(0.1)

    def request_parameter_value_full(self,
                                     block0: int,
                                     parameter: int,
                                     category: int,
                                     memory: int,
                                     parameter_set: int,
                                     size: int):
        msg = "F0 44 19 01 7F 00" + int_to_hex(category) + int_to_hex(memory) \
              + int_to_lsb_msb(parameter_set) + "00 00 00 00 00 00" + int_to_lsb_msb(block0) \
              + int_to_lsb_msb(parameter) + "00 00" + int_to_lsb_msb(size) + "F7"
        self.send_sysex(msg)

    def send_parameter_value_full(self,
                                  block0: int,
                                  param_number: int,
                                  category: int,
                                  memory: int,
                                  parameter_set: int,
                                  value: int,
                                  size: int):
        msg_value = int_to_hex(value) if param_number in self.short_params else int_to_lsb_msb(value)
        msg = "F0 44 19 01 7F 01" + int_to_hex(category) + int_to_hex(memory) \
              + int_to_lsb_msb(parameter_set) + "00 00 00 00 00 00" + int_to_lsb_msb(block0) \
              + int_to_lsb_msb(param_number) + "00 00" + int_to_lsb_msb(size) + msg_value + "F7"
        if self.IS_DEBUG_MODE:
            print(">> " + format_as_nice_hex(msg))
        self.send_sysex(msg)

    def request_dsp_module(self, block0: int):
        msg_start = "F0 44 19 01 7F 00 03 03 00 00 00 00 00 00 00 00"
        msg_block0 = int_to_lsb_msb(block0)
        msg_end = "55 00 00 00 00 00 F7"
        self.send_sysex(msg_start + msg_block0 + msg_end)

    def request_dsp_params(self, block0: int):
        size = size_to_lsb_msb(Size.DSP_PARAMS)
        msg_start = "F0 44 19 01 7F 00 03 03 00 00 00 00 00 00 00 00"
        msg_block0 = int_to_lsb_msb(block0)
        msg_end = "57 00 00 00" + size + "F7"
        self.send_sysex(msg_start + msg_block0 + msg_end)

    def process_message(self, message, _):
        message, deltatime = message

        self.lock.lockForWrite()
        try:
            self.active_sync_job_count = max(0, self.active_sync_job_count - 1)  # count-- until 0
        finally:
            self.lock.unlock()

        if self.IS_DEBUG_MODE:
            print(format_as_nice_hex(list_to_hex_str(message)))

        if message[0] == SYSEX_FIRST_BYTE and message[1] == SysexId.CASIO and len(message) > (SYSEX_TYPE_INDEX + 1):
            block0 = lsb_msb_to_int(message[BLOCK_0_INDEX], message[BLOCK_0_INDEX + 1])
            sysex_type = lsb_msb_to_int(message[SYSEX_TYPE_INDEX], message[SYSEX_TYPE_INDEX + 1])
            param_set = lsb_msb_to_int(message[PARAM_SET_INDEX], message[PARAM_SET_INDEX + 1])

            if message[7] == MEMORY_1:
                self._process_memory_1_message(sysex_type, message)
            elif message[7] == MEMORY_3:
                self._process_memory_3_message(sysex_type, block0, param_set, message)
            else:
                self.log("[MIDI IN] SysEx", message)
        elif message[0] == SYSEX_FIRST_BYTE and message[1] == SysexId.REAL_TIME:
            self.log("[MIDI IN] Real Time SysEx", message)
        elif message[0] == CC_FIRST_BYTE and message[1] == CC_BANK_SELECT_MSB:
            self.log("[MIDI IN] Bank change MSB ", message)
            self.bank_select_msg_queue.append(message)
            time.sleep(0.01)
        elif message[0] == CC_FIRST_BYTE and message[1] == CC_BANK_SELECT_LSB:
            self.log("[MIDI IN] Bank change LSB ", message)
        # elif message[0] == CC_FIRST_BYTE:
        #     self.log("[MIDI IN] CC: ", message)
        elif message[0] == INSTRUMENT_SELECT_FIRST_BYTE_CH0:
            self.log("[MIDI IN] Program change ", message)
            bank_select_msg = self.get_last_bank_select_message()
            if bank_select_msg is not None:
                self.core.process_instrument_select_response(bank_select_msg[2], message[1])

                worker = Worker(self.core.countdown_and_autosynchronize, 2)
                worker.signals.error.connect(lambda error: self.core.show_error_msg(str(error[1])))
                worker.start()
        elif message[0] in [INSTRUMENT_SELECT_FIRST_BYTE_CH1, INSTRUMENT_SELECT_FIRST_BYTE_CH2, INSTRUMENT_SELECT_FIRST_BYTE_CH3]:
            self.log("[MIDI IN] Upper/Lower program change ", message)
            self.core.request_custom_parameter(SysexType.TONE_NUMBER.value, 1, 2, 3, 0, 0)
            self.core.request_custom_parameter(SysexType.TONE_NUMBER.value, 2, 2, 3, 0, 0)
            self.core.request_custom_parameter(SysexType.TONE_NUMBER.value, 3, 2, 3, 0, 0)
        else:
            self.log("[MIDI IN] ", message)

    def _process_memory_1_message(self, sysex_type, message):
        if sysex_type == SysexType.TONE_NAME.value:
            self.log("[MIDI IN] Tone Name (Memory 1)", message)
            tone_number_response = message[8:10]  # "parameter set" value
            tone_name_response = message[-1 - Size.TONE_NAME:-1]
            self.core.process_user_memory_tone_name_response(tone_number_response, tone_name_response)
        else:
            self.log("[MIDI IN] SysEx (Memory 1)", message)

    def _process_memory_3_message(self, sysex_type, block0, param_set, message):
        if sysex_type == SysexType.TONE_NAME.value:
            self.log("[MIDI IN] Tone Name", message)
            response = message[-1 - Size.TONE_NAME:-1]
            self.core.process_tone_name_response(response)
        elif sysex_type in self.long_params:
            self.log(f"[MIDI IN] Parameter {sysex_type}", message)
            response = message[-1 - Size.MAIN_PARAMETER:-1]
            self.core.process_parameter_response(sysex_type, block0, param_set, response)  # 2 bytes
        elif sysex_type in self.short_params:
            self.log(f"[MIDI IN] Parameter {sysex_type}", message)
            response = message[-1 - Size.MAIN_PARAMETER_SHORT:-1]
            self.core.process_parameter_response(sysex_type, block0, param_set, response[:1])  # 1 byte
        elif sysex_type == SysexType.DSP_MODULE.value:
            self.log("[MIDI IN] DSP module", message)
            response = message[-1 - Size.DSP_MODULE:-1]
            self.core.process_dsp_module_response(block0, response[0])
        elif sysex_type == SysexType.DSP_PARAMS.value:
            self.log("[MIDI IN] DSP parameters", message)
            response = message[-1 - Size.DSP_PARAMS:-1]
            self.core.process_dsp_module_parameters_response(block0, response)
        elif sysex_type == SysexType.TONE_NUMBER.value:
            self.log(f"[MIDI IN] Parameter {sysex_type}", message)
            tone_number = 0
            response = message[-1 - Size.MAIN_PARAMETER:-1]
            tone_tumber_response = lsb_msb_to_int(response[0], response[1])

            if tone_tumber_response in range(0, 800):
                tone_number = tone_tumber_response + 1
            elif tone_tumber_response in range(820, 920):
                tone_number = tone_tumber_response - 19

            self.core.process_tone_number_from_performance_params_response(tone_number, block0)
        else:
            self.log("[MIDI IN] SysEx", message)

    def log(self, title, message):
        msg_hex: str = format_as_nice_hex(list_to_hex_str(message))
        line_break = "\n" if msg_hex is not None and msg_hex.startswith("F0") else ""
        self.core.log(title + line_break + msg_hex)

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

    def send_dsp_module_change_sysex(self, block0: int, new_dsp_id: int):
        self.send_parameter_change_sysex(block0, SysexType.DSP_MODULE.value, new_dsp_id)

    def send_dsp_bypass_sysex(self, block0: int, bypass: bool):
        value = 1 if bypass else 0
        self.send_parameter_change_short_sysex(block0, SysexType.DSP_BYPASS.value, value)

    def send_dsp_params_change_sysex(self, block0: int, params_list: list):
        # Array size is always 14 bytes: length is "0D" TODO: use size
        msg_start = "F0 44 19 01 7F 01 03 03 00 00 00 00 00 00 00 00"
        msg_block0_param_and_size = int_to_lsb_msb(block0) + "57 00 00 00 0D 00"
        msg_params = list_to_hex_str(params_list)
        msg_end = "F7"
        self.send_sysex(msg_start + msg_block0_param_and_size + msg_params + msg_end)

    def send_parameter_change_sysex(self, block0: int, parameter: int, value: int):
        sysex = self.make_sysex(block0, parameter, value)
        self.send_sysex(sysex)

    def send_parameter_change_short_sysex(self, block0: int, parameter: int, value: int):
        sysex = self.make_sysex_short_value(block0, parameter, value)
        self.send_sysex(sysex)

    # # Same as send_parameter_change_short_sysex, but with parameter_set
    # def send_parameter_change_short_sysex_2(self, block0: int, parameter: int, parameter_set: int, value: int):
    #     sysex = self.make_sysex_short_value_2(block0, parameter, parameter_set, value)
    #     self.send_sysex(sysex)

    def send_atk_rel_parameter_change_sysex(self, block0: int, parameter: int, value: int):
        sysex = self.make_sysex_8bit_value(block0, parameter, value)
        self.send_sysex(sysex)

    def send_change_tone_msg(self, tone_number, block0):
        internal_number = tone_number - 1
        if tone_number > 800:
            internal_number = tone_number + 19
        msg = "F0 44 19 01 7F 01 02 03 00 00 00 00 00 00 00 00 " + int_to_lsb_msb(block0) + " 64 01 00 00 00 00" \
              + int_to_lsb_msb(internal_number) + "F7"
        self.send_sysex(msg)

    # for calibration tones
    def send_change_tone_msg_2(self, tone_number):
        msg = "F0 44 19 01 7F 01 02 03 00 00 00 00 00 00 00 00 00 00 64 01 00 00 00 00" \
              + int_to_lsb_msb(tone_number) + "F7"
        self.send_sysex(msg)

    def send_change_tone_cc_msg(self, instrument: Instrument):
        self.midi_out.send_message([CC_FIRST_BYTE, CC_BANK_SELECT_MSB, instrument.bank])
        time.sleep(0.01)
        self.midi_out.send_message([CC_FIRST_BYTE, CC_BANK_SELECT_LSB, 0x00])
        time.sleep(0.01)
        self.midi_out.send_message([INSTRUMENT_SELECT_FIRST_BYTE_CH0, instrument.program])

    @staticmethod
    def make_sysex(block0: int, parameter: int, value: int) -> str:
        return "F0 44 19 01 7F 01 03 03 00 00 00 00 00 00 00 00" \
            + int_to_lsb_msb(block0) \
            + int_to_lsb_msb(parameter) \
            + "00 00 00 00" \
            + int_to_lsb_msb(value) \
            + "F7"

    # Special case for "SHORT_PARAMS" list parameters
    @staticmethod
    def make_sysex_short_value(block0: int, parameter: int, value: int) -> str:
        return "F0 44 19 01 7F 01 03 03 00 00 00 00 00 00 00 00" \
            + int_to_lsb_msb(block0) \
            + int_to_lsb_msb(parameter) \
            + "00 00 00 00" \
            + int_to_hex(value) \
            + "F7"

    # # Same as make_sysex_short_value, but with parameter_set
    # @staticmethod
    # def make_sysex_short_value_2(block0: int, parameter: int, parameter_set: int, value: int) -> str:
    #     return "F0 44 19 01 7F 01 03 03 " + int_to_lsb_msb(parameter_set) + " 00 00 00 00 00 00" \
    #         + int_to_lsb_msb(block0) \
    #         + int_to_lsb_msb(parameter) \
    #         + "00 00 00 00" \
    #         + int_to_hex(value) \
    #         + "F7"

    # Special case for "Attack time" and "Release time" parameters
    @staticmethod
    def make_sysex_8bit_value(block0: int, parameter: int, value: int) -> str:
        return "F0 44 19 01 7F 01 03 03 00 00 00 00 00 00 00 00" \
            + int_to_lsb_msb(block0) \
            + int_to_lsb_msb(parameter) \
            + "00 00 00 00" \
            + int_to_lsb_msb_8bit(value) \
            + "F7"
