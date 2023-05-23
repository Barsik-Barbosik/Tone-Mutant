import configparser
import struct
import threading
import time

import rtmidi

from constants.enums import SysexType
from model.instrument import Instrument

CONFIG_FILENAME = "../config.cfg"
RESPONSE_TIMEOUT = 5  # in seconds


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

            cfg = configparser.ConfigParser()
            cfg.read(CONFIG_FILENAME)
            self.input_name = cfg.get("Midi", "InPort", fallback="")
            self.output_name = cfg.get("Midi", "OutPort", fallback="")
            self.channel = int(cfg.get("Midi Real-Time", "Channel", fallback="0"))

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

    def verify_midi_ports(self):
        if not self.midi_out.is_port_open() or not self.midi_in.is_port_open():
            self.open_midi_ports()
        if not self.midi_out.is_port_open() or not self.midi_in.is_port_open():
            raise Exception("Unable to open MIDI port. Please verify MIDI settings.")

    def send_sysex(self, sysex_hex_str: str):
        self.verify_midi_ports()
        print("SysEx: " + self.format_as_nice_hex(sysex_hex_str))
        self.midi_in.ignore_types(sysex=False, timing=True, active_sense=True)
        self.flush_input_queue()
        self.midi_out.send_message(bytearray(bytes.fromhex(sysex_hex_str)))
        self.flush_input_queue()
        self.midi_in.ignore_types(sysex=True, timing=True, active_sense=True)

    def send_sysex_and_get_response(self, sysex_hex_str: str, required_size: int) -> list:
        self.verify_midi_ports()
        print("SysEx:\t\t" + self.format_as_nice_hex(sysex_hex_str))
        self.midi_in.ignore_types(sysex=False, timing=True, active_sense=True)
        self.flush_input_queue()
        self.midi_out.send_message(bytearray(bytes.fromhex(sysex_hex_str)))

        # Wait for a correct response
        message = None
        start_time = time.time()
        while (message is None or len(message[0]) < 4) and time.time() - start_time < RESPONSE_TIMEOUT:
            message = self.midi_in.get_message()
            time.sleep(0.01)

        if message is None:
            return None

        self.midi_in.ignore_types(sysex=True, timing=True, active_sense=True)
        response, delta_time = message
        params_list = response[len(response) - 1 - required_size:len(response) - 1]
        print("Response:\t" + self.format_as_nice_hex(self.list_to_hex_str(response)))
        print("Response params list:\t" + self.format_as_nice_hex(self.list_to_hex_str(params_list)))

        return params_list

    def flush_input_queue(self):
        time.sleep(0.01)
        self.midi_in.get_message()

    def send_change_tone_msg(self, instrument: Instrument):
        print("...")
        # note_on = [0x90, 60, 112]  # channel 1, middle C, velocity 112
        # note_off = [0x80, 60, 0]
        # self.midi_out.send_message(note_on)
        # time.sleep(0.5)
        # self.midi_out.send_message(note_off)
        # time.sleep(0.1)
        #
        # cc_01 = [0xB0, 0x00,instrument.bank]
        # cc_02 = [0xB0, 0x20, 0x00]
        # pc = [0xC0, instrument.program_change]
        # self.midi_out.send_message(cc_01)
        # time.sleep(0.1)
        # self.midi_out.send_message(cc_02)
        # time.sleep(0.1)
        # self.midi_out.send_message(pc)
        # time.sleep(0.1)
        #
        # aaa = self.make_program_change(19, 35, bankLSB=0, channel=0)
        # bbb = aaa.hex(' ').upper()
        # self.send_sysex(bbb)
        # s1 = "B0 00 04"
        # s2 = "B0 20 00"
        # s3 = "C0 04"
        # self.flush_input_queue()
        # self.midi_out.send_message(bytearray(bytes.fromhex(s2)))
        # time.sleep(0.5)
        # self.midi_out.send_message(bytearray(bytes.fromhex(s1)))
        # time.sleep(0.5)
        # self.midi_out.send_message(bytearray(bytes.fromhex(s3)))
        # time.sleep(0.5)
        #
        # s1 = "B1 00 04"
        # s2 = "B1 20 00"
        # s3 = "C1 04"
        # self.flush_input_queue()
        # self.midi_out.send_message(bytearray(bytes.fromhex(s2)))
        # time.sleep(0.5)
        # self.midi_out.send_message(bytearray(bytes.fromhex(s1)))
        # time.sleep(0.5)
        # self.midi_out.send_message(bytearray(bytes.fromhex(s3)))
        # time.sleep(0.5)
        #
        # s1 = "B2 00 04"
        # s2 = "B2 20 00"
        # s3 = "C2 04"
        # self.flush_input_queue()
        # self.midi_out.send_message(bytearray(bytes.fromhex(s1)))
        # time.sleep(0.5)
        # self.midi_out.send_message(bytearray(bytes.fromhex(s2)))
        # time.sleep(0.5)
        # self.midi_out.send_message(bytearray(bytes.fromhex(s3)))
        # time.sleep(0.5)


    def send_dsp_params_change_sysex(self, params_list: list, block_id: int):
        # Array size is always 14 bytes: length is "0D"
        msg_start = "F0 44 19 01 7F 01 03 03 00 00 00 00 00 00 00 00"
        msg_block_param_and_size = self.decimal_to_hex(block_id) + "00 57 00 00 00 0D 00"
        msg_params = self.list_to_hex_str(params_list)
        msg_end = "F7"

        print("Setting DSP Params:\t" + self.format_as_nice_hex(msg_params))
        self.send_sysex(msg_start + msg_block_param_and_size + msg_params + msg_end)

    def request_dsp_module(self, block_id: int):
        if self.is_block_id_valid(block_id):
            # Array size is always 14 bytes: length is "0D"
            msg_start = "F0 44 19 01 7F 00 03 03 00 00 00 00 00 00 00 00"
            msg_block_id = self.decimal_to_hex(block_id)
            msg_end = "00 55 00 00 00 00 00 F7"

            return self.send_sysex_and_get_response(msg_start + msg_block_id + msg_end, 2)

    def request_dsp_params(self, block_id: int):
        if self.is_block_id_valid(block_id):
            # Array size is always 14 bytes: length is "0D"
            msg_start = "F0 44 19 01 7F 00 03 03 00 00 00 00 00 00 00 00"
            msg_block_id = self.decimal_to_hex(block_id)
            msg_end = "00 57 00 00 00 0D 00 F7"

            return self.send_sysex_and_get_response(msg_start + msg_block_id + msg_end, 14)

    @staticmethod
    def is_block_id_valid(block_id: int):
        return isinstance(int(block_id), int) and 0 <= int(block_id) <= 3

    def send_dsp_module_change_sysex(self, new_dsp_id: int, block_id: int):
        self.send_parameter_change_sysex(SysexType.SET_DSP_MODULE.value, new_dsp_id, block_id)

    def send_parameter_change_sysex(self, parameter: int, value: int, block_id: int):
        sysex = self.make_sysex(parameter, value, block_id)
        self.send_sysex(sysex)

    def make_sysex(self, parameter: int, data: int, block0: int) -> str:
        return "F0 44 19 01 7F 01 03 03 00 00 00 00 00 00 00 00" \
            + self.decimal_to_hex_hex(block0) \
            + self.decimal_to_hex_hex(parameter) \
            + "00 00 00 00" \
            + self.decimal_to_hex_hex(data) \
            + "F7"

    @staticmethod
    def decimal_to_hex(decimal_num: int) -> str:
        return "{:02X}".format(decimal_num)

    @staticmethod
    def decimal_to_hex_hex(decimal_num: int) -> str:
        if decimal_num > 32267:
            raise ValueError("Number is too big: {}".format(decimal_num))

        return "{:02X}".format(decimal_num % 128) + " {:02X}".format(decimal_num // 128)

    def list_to_hex_str(self, int_list: list) -> str:
        hex_str = ""
        for int_value in int_list:
            hex_str = hex_str + " " + self.decimal_to_hex(int_value)
        return hex_str

    @staticmethod
    def format_as_nice_hex(input_str: str) -> str:
        string_without_spaces = input_str.replace(" ", "")
        return " ".join(string_without_spaces[i:i + 2] for i in range(0, len(string_without_spaces), 2))

    # @staticmethod
    # def decimal_to_two_bytes(decimal_num):
    #     if decimal_num > 32267:
    #         raise ValueError("Number is too big: {}".format(decimal_num))
    #
    #     return struct.pack("<BB", decimal_num % 128, decimal_num // 128)
    #
    # @staticmethod
    # def make_sys_ex(parameter, data, category=3, memory=3, parameter_set=0, block0=0):
    #     return bytes.fromhex("F0 44 19 01 7F 01") \
    #         + struct.pack("<BBHHHHHHHH", category, memory, parameter_set, 0, 0, 0, block0, parameter, 0, 0) \
    #         + data + bytes.fromhex("F7")

    @staticmethod
    def make_program_change(prgm, bankMSB, bankLSB=0, channel=0):
        return struct.pack("<BBBBBBBB", 0xB0 + channel, 0x00, bankMSB, 0xB0 + channel, 0x20, bankLSB, 0xC0 + channel,
                           prgm)
