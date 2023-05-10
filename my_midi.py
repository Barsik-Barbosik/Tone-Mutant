import configparser
import queue
import struct
import time

import rtmidi

import external.toneTyrant.midi_comms as midi_comms

CONFIG_FILENAME = 'config.cfg'


class Midi(midi_comms.MidiComms):

    def __init__(self):
        cfg = configparser.ConfigParser()
        cfg.read(CONFIG_FILENAME)
        self._input_name = cfg.get('Midi', 'InPort', fallback="")
        self._output_name = cfg.get('Midi', 'OutPort', fallback="")
        self._realtime_enable = True
        self._realtime_channel = int(cfg.get('Midi Real-Time', 'Channel', fallback="0"))
        self._logging_level = 0
        self._queue = queue.Queue()
        self._thread = midi_comms.MidiComms.MidiThread(self)
        self._thread.start()

    def send_sysex(self, packet):
        """
        Send SysEx to the keyboard
        """
        print("SysEx: " + packet.hex(" ").upper())

        # Open the device (if needed)
        midiin = rtmidi.MidiIn()
        midiout = rtmidi.MidiOut()
        for i in range(midiout.get_port_count()):
            if self._output_name == midiout.get_port_name(i):
                midiout.open_port(port=i)
        for i in range(midiin.get_port_count()):
            if self._input_name == midiin.get_port_name(i):
                midiin.open_port(port=i)
        if not midiout.is_port_open() or not midiin.is_port_open():
            raise Exception("Could not find the named port. Please check MIDI settings.")

        midiin.ignore_types(sysex=False)

        # Flush the input queue
        time.sleep(0.01)
        midiin.get_message()

        # Send the packet
        midiout.send_message(bytearray(packet))
        print(" Sent: " + packet.hex(" ").upper())
        time.sleep(0.1)
        # Handle any response -- don't expect one
        midiin.get_message()
        time.sleep(0.01)

        # Close the device
        midiin.close_port()
        midiout.close_port()

        # Also delete the instances. See notes in rtmidi-python documentation. This is
        # needed to get around delays in the python garbage-collector. A better
        # solution might be to keep the ports open and close only when exiting the
        # program.
        midiin.delete()
        midiout.delete()

    def set_parameter(self, parameter, data, block0=0):
        sysex = self.make_simple_sys_ex(parameter, data, block0)
        self.send_sysex(sysex)

    def set_dsp_parameters(self, dsp_params):
        # Array size is always 14 bytes: length is "0D"
        msg_start = bytes.fromhex("F0 44 19 01 7F 01 03 03 21 00 00 00 00 00 00 00 00 00 57 00 00 00 0D 00")
        msg_end = bytes.fromhex("F7")
        self.send_sysex(msg_start + dsp_params + msg_end)

    def two_bytes(self, X):
        # Expect X to be between 0 and 32267
        return struct.pack("<BB", X % 128, X // 128)

    def make_simple_sys_ex(self, parameter, data, block0=0):
        return bytes.fromhex("F0 44 19 01 7F 01 03 03 00 00 00 00 00 00 00 00") + self.two_bytes(block0) \
            + self.two_bytes(parameter) + bytes.fromhex("00 00 00 00") \
            + self.two_bytes(data) + bytes.fromhex("F7")

    def make_sys_ex(self, parameter, data, category=3, memory=3, parameter_set=0, block0=0):
        return bytes.fromhex("F0 44 19 01 7F 01") \
            + struct.pack("<BBHHHHHHHH", category, memory, parameter_set, 0, 0, 0, block0, parameter, 0, 0) \
            + data + bytes.fromhex("F7")

    def make_program_change(self, prgm, bankMSB, bankLSB=0, channel=0):
        return struct.pack("<BBBBBBBB", 0xB0 + channel, 0x00, bankMSB, 0xB0 + channel, 0x20, bankLSB, 0xC0 + channel,
                           prgm)
