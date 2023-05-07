"""
A class for performing MIDI communications
"""

import binascii
import configparser
import logging
import queue
import struct
import threading
import time

# Install with pip install python-rtmidi
import rtmidi

import parameters

# Some global variables used by the communications
#
is_busy = False
must_send_ack = False
have_got_ack = False
have_got_ess = False

so_far = b''
total_rxed = b''
type_1_rxed = b''


# The main class:
#
class MidiComms:
    class MidiThread(threading.Thread):
        def __init__(self, _parent):
            threading.Thread.__init__(self)
            self._parent = _parent

        def run(self):
            # Loops forever, until a stop signal is received
            while True:
                obj = self._parent._queue.get(True)
                if len(obj) < 5:
                    # A stop signal
                    break
                self._parent.set_single_parameter(obj[0], obj[4], midi_bytes=obj[2], category=3, memory=3,
                                                  parameter_set=obj[3], block0=obj[1])

        @classmethod
        def StopSignal(cls):
            return (0,)

    def __init__(self):
        cfg = configparser.ConfigParser()
        cfg.read('config.cfg')
        self._input_name = cfg.get('Midi', 'InPort', fallback="")
        self._output_name = cfg.get('Midi', 'OutPort', fallback="")
        self._realtime_channel = int(cfg.get('Midi Real-Time', 'Channel', fallback="0"))
        self._realtime_enable = cfg.get('Midi Real-Time', 'Enable', fallback="False").lower() in ['true', '1', 't', 'y',
                                                                                                  'yes']
        self._logging_level = 0
        if cfg.get("Logging", "Level", fallback="").lower() in ['on', '1']:
            self._logging_level = 1
        elif cfg.get("Logging", "Level", fallback="").lower() in ['2']:
            self._logging_level = 2
        # Translate the logging levels to Python logging levels as follows:
        #   0 = no logging of interest to user. (WARNING)
        #   1 = logging of each SysEx message, for use by user. (INFO)
        #   2 = logging of each SysEx message, as well as other extraneous stuff. (DEBUG)
        if self._logging_level == 1:
            logging.getLogger().setLevel(logging.INFO)
        elif self._logging_level == 2:
            logging.getLogger().setLevel(logging.DEBUG)

        self._queue = queue.Queue()
        self._thread = MidiComms.MidiThread(self)
        self._thread.start()

    def QueueParamVal(self, P: parameters.Param, p_val):
        if self._realtime_enable:
            self._queue.put((P.number, P.block0, P.midiBytes, self._realtime_channel, p_val), block=False)

    def Close(self):
        self._queue.put(MidiComms.MidiThread.StopSignal(), block=False)
        self._thread.join(1.0)  # Time out after 1 second

    def SetParamTo(self, P: parameters.Param, p_val):
        self.set_single_parameter(P.number, p_val, midi_bytes=P.midiBytes, category=3, memory=3,
                                  parameter_set=self._realtime_channel, block0=P.block0)
        return True

    def AllowMidi(self):
        """
        Return True if MIDI operations are possible
        """
        return True

    # Define the device ID. Constructed as follows:
    #    0x44       Manufacturer ID ( = Casio)
    #    0x19 0x01  Model ID ( = CT-X3000, CT-X5000, CT-X700)
    #    0x7F       Device. This is a "don't care" value
    #
    DEVICE_ID = b"\x44\x19\x01\x7F"

    def midi_7bit_to_8bit(self, b):
        """
        Decode from MIDI "7-bit format", which requires the MSb of each byte to be
        zero.
        """

        r = 0  # remainder
        n = 0  # position of split
        i = 0  # pointer to input
        c = b''  # output

        while i < len(b):

            x = b[i]

            if x >= 128:
                raise Exception("Not valid 7-bit data at position {0} : {1:02X}!".format(i, x))

            if n == 0 or n == 8:
                r = x
                n = 0
            elif n == 1:
                c += struct.pack('<B', ((x & 0x01) << 7) + r)
                r = x // 2
            elif n == 2:
                c += struct.pack('<B', ((x & 0x03) << 6) + r)
                r = x // 4
            elif n == 3:
                c += struct.pack('<B', ((x & 0x07) << 5) + r)
                r = x // 8
            elif n == 4:
                c += struct.pack('<B', ((x & 0x0f) << 4) + r)
                r = x // 16
            elif n == 5:
                c += struct.pack('<B', ((x & 0x1f) << 3) + r)
                r = x // 32
            elif n == 6:
                c += struct.pack('<B', ((x & 0x3f) << 2) + r)
                r = x // 64
            elif n == 7:
                c += struct.pack('<B', ((x & 0x7f) << 1) + r)
                r = 0
            i += 1
            n += 1
        if r != 0:
            raise Exception("Left over data! Probably an error")

        return c

    def midi_8bit_to_7bit(self, b):
        """
        Encode to MIDI "7-bit format", which requires the MSb of each byte to be
        zero.
        """

        r = 0  # remainder
        n = 0  # position of split
        i = 0  # pointer to input
        c = b''  # output

        while i < len(b):
            if n == 0 or n == 7:
                n = 0
                c += struct.pack('<B', 0x1 * (b[i] & 0x7f))
                r = (b[i] & 0x80) // 0x80
            elif n == 1:
                c += struct.pack('<B', r + 0x2 * (b[i] & 0x3f))
                r = (b[i] & 0xc0) // 0x40
            elif n == 2:
                c += struct.pack('<B', r + 0x4 * (b[i] & 0x1f))
                r = (b[i] & 0xe0) // 0x20
            elif n == 3:
                c += struct.pack('<B', r + 0x8 * (b[i] & 0x0f))
                r = (b[i] & 0xf0) // 0x10
            elif n == 4:
                c += struct.pack('<B', r + 0x10 * (b[i] & 0x07))
                r = (b[i] & 0xf8) // 0x8
            elif n == 5:
                c += struct.pack('<B', r + 0x20 * (b[i] & 0x03))
                r = (b[i] & 0xfc) // 0x4
            elif n == 6:
                c += struct.pack('<B', r + 0x40 * (b[i] & 0x01))
                c += struct.pack('<B', (b[i] & 0xfe) // 0x2)
                r = 0
            n += 1
            i += 1
        if n < 7:
            c += struct.pack('<B', r)
        return c

    def handle_pkt(self, p):
        """
        Handle a complete packet as received from the MIDI port. It is assumed that
        each packet will be in Casio SYSEX format.
        """
        global is_busy
        global must_send_ack
        global have_got_ack
        global have_got_ess
        global total_rxed
        global type_1_rxed
        # print(p.hex(" "))
        if len(p) < 7:
            print("BAD PACKET!!")
            return
        if p[0] != 0xF0 or p[1] != 0x44 or p[4] != 0x7F or p[-1] != 0xF7:
            print("BAD PACKET!!")
            return
        type_of_pkt = p[5]
        if type_of_pkt == 0xB:
            is_busy = True
        else:
            is_busy = False
            if type_of_pkt == 0xA:
                have_got_ack = True
            if type_of_pkt == 0xD:
                have_got_ack = True
                have_got_ess = True

        if type_of_pkt == 3 or type_of_pkt == 5:  # This takes a CRC
            c = struct.unpack('<5B', p[-6:-1])
            crc_compare = c[0] + (1 << 7) * c[1] + (1 << 14) * c[2] + (1 << 21) * c[3] + (1 << 28) * c[4]
            if binascii.crc32(p[1:-6]) == crc_compare:
                must_send_ack = True
                if type_of_pkt == 5:
                    have_got_ack = True  # This one must look like an ACK
                    mm = self.midi_7bit_to_8bit(p[12:-6])
                    total_rxed += mm
            else:
                print("BAD CRC!!!")

        if type_of_pkt == 1:
            v = p[24:-1]
            type_1_rxed = v

    def parse_response(self, b, *, _debug=False):
        """
        Parse bytes received from the MIDI port, collating them into SYSEX packets.
        """
        global so_far

        in_pkt = True
        if len(so_far) == 0:
            in_pkt = False

        for i in range(len(b)):
            x = b[i]
            if in_pkt:
                if x == 0xF7:
                    so_far += b'\xf7'
                    # Have completed. Do something!
                    if _debug:
                        print(so_far.hex(" ").upper())
                    self.handle_pkt(so_far)
                    in_pkt = False
                    so_far = b''
                elif x == 0xF0:
                    # Error! but start a new packet
                    so_far = b'\xf0'
                elif x >= 0x80:
                    # Error!
                    in_pkt = False
                    so_far = b''
                else:
                    so_far += b[i:i + 1]
            else:
                if x == 0xF0:
                    so_far = b'\xf0'
                    in_pkt = True

    class SysexTimeoutError(Exception):
        """
        An exception specific to the SYSEX communications. The most likely reason
        for this exception to be raised is that the keyboard has become unplugged,
        powered off, etc.
        """
        pass

    def wait_for_ack(self, f):
        """
        Receive bytes from the MIDI port and parse them until an ACK packet has
        been seen. If more than 4 seconds passes then an exception will be raised.
        """
        global have_got_ack
        have_got_ack = False
        st = time.monotonic()
        while True:
            msg = f.get_message()
            if msg is not None:
                # print("<    " + bytes(msg[0]).hex(" "))
                self.parse_response(bytes(msg[0]))
            if have_got_ack:
                # Success!
                return
            time.sleep(0.02)
            if time.monotonic() > st + 4.0:
                # Clean up. We're exiting with an exception, but just in case a higher-
                # level process catches the exception we should have the port closed.
                # os.close(f)
                # Timed out. Completely exit the program
                raise self.SysexTimeoutError("SYSEX communication timed out. Exiting ...")

    def make_packet(self, tx=False,
                    category=30,
                    memory=1,
                    parameter_set=0,
                    block=[0, 0, 0, 0],
                    parameter=0,
                    index=0,
                    length=1,
                    command=-1,
                    sub_command=3,
                    data=b''):
        """
        Construct a packet in Casio SYSEX format, for sending over the MIDI port
        """

        w = b'\xf0' + self.DEVICE_ID
        if command < 0:
            if (tx):
                command = 1
            else:
                command = 0
        w += struct.pack('<B', command)

        if command == 0x8:
            return w + struct.pack('<B', sub_command) + b'\xf7'

        w += struct.pack('<2B', category, memory)
        w += struct.pack('<2B', parameter_set % 128, parameter_set // 128)

        if command == 0xA:
            return w + b'\xf7'

        elif command == 5:
            w += struct.pack('<2B', length % 128, length // 128)
            w += self.midi_8bit_to_7bit(data)
            crc_val = binascii.crc32(w[1:])
            w += self.midi_8bit_to_7bit(struct.pack('<I', crc_val))
            w += b'\xf7'
            return w

        elif (command >= 2 and command < 8) or command == 0xD or command == 0xE:
            # OBR/HBR doesn't have the following stuff
            pass

        else:
            if len(block) != 4:
                print("Length of block should be 4, was {0}; setting to all zeros".format(len(block)))
                block = [0, 0, 0, 0]
            for blk_x in block:
                w += struct.pack('<BB', blk_x % 128, blk_x // 128)
            w += struct.pack('<BBHH', parameter % 128, parameter // 128, index, length - 1)
        if (tx):
            w += data
        w += b'\xf7'
        return w

    def set_single_parameter(self, parameter, data, midi_bytes=1, category=3, memory=3, parameter_set=0, block0=0,
                             block1=0, *, _debug=False):
        """
        Send a single parameter value to the keyboard
        """

        _logger = logging.getLogger()
        _logger.info(f" parameter {parameter}, block {block0} <- {str(data)}:")

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
            raise Exception("Could not find the named port")

        midiin.ignore_types(sysex=False)

        # Flush the input queue
        time.sleep(0.01)
        midiin.get_message()

        # Prepare the input
        d = b''
        l = 1

        if isinstance(data, type(0)):
            # The input is an integer. The "length" parameter passed to make_packet must be
            # 1, but we don't know how many bytes of bit-stuffed data the keyboard is actually
            # expecting. Use the "midi_bytes" parameter for that.

            key_len = midi_bytes

            # Now do the bit-stuffing
            for i in range(key_len):
                d = d + struct.pack('B', data & 0x7F)
                data = data // 0x80
            l = 1  # length is always 1 for numeric inputs

        else:
            # Assume the input is a byte array
            d = data
            l = len(d)

        # Write the parameter
        pkt = self.make_packet(tx=True, parameter_set=parameter_set, category=category, memory=memory,
                               parameter=parameter, block=[0, 0, block1, block0], length=l, data=d)
        midiout.send_message(bytearray(pkt))
        _logger.info("    " + pkt.hex(" ").upper())
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

    def upload_ac7_internal(self, param_set, data, memory=1, category=30, *, _debug=False):
        """
        Send a complete parameter set to the keyboard. The meaning of the data, and
        the required data length, depend on the values of "memory" and "category".
        For upload to Tone data in User Memory, the values should be:
            - memory=1
            - category=3
        In that case, the value of "param_set" can be any number from 0 to 99,
        corresponding to User Tone numbers 801-900, and the data is required to be
        of length 0x1C8.
        """

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
            raise Exception("Could not find the named port")

        midiin.ignore_types(sysex=False)

        # Flush the input queue
        midiin.get_message()
        time.sleep(0.2)

        # Send the SBS command
        pkt = self.make_packet(command=8, sub_command=3)
        # print("> " + pkt.hex(" "))
        midiout.send_message(bytearray(pkt))  # SBS(HBS)
        self.wait_for_ack(midiin)

        i = 0
        while i < len(data):
            # Send a HBS packet:
            # Category 30 = Rhythms
            # Parameter set: indicates the specific rhythm
            # Memory 1 = user rhythm space

            len_remaining = len(data) - i
            if len_remaining > 0x80:
                len_remaining = 0x80

            pkt = self.make_packet(parameter_set=param_set, category=category, memory=memory, command=5,
                                   length=len_remaining, data=data[i:i + len_remaining])
            # print("> " + pkt.hex(" "))
            midiout.send_message(bytearray(pkt))
            self.wait_for_ack(midiin)
            i += len_remaining

        # Send ESS (no ACK expected)
        # print("Sending ESS")
        midiout.send_message(
            bytearray(self.make_packet(parameter_set=param_set, category=category, memory=memory, command=0xd)))
        time.sleep(0.3)

        # Send EBS (no ACK expected)
        # print("Sending EBS")
        midiout.send_message(
            bytearray(self.make_packet(parameter_set=param_set, category=category, memory=memory, command=0xe)))
        time.sleep(0.3)

        midiin.close_port()
        midiout.close_port()

    def download_ac7_internal(self, param_set, memory=1, category=30, *, _debug=False):
        """
        Request and receive a complete parameter set from the keyboard. The meaning
        of the data depends on the values of "memory" and "category". For download
        from Tone data in User Memory, the values should be:
            - memory=1
            - category=3
        In that case, the value of "param_set" can be any number from 0 to 99,
        corresponding to User Tone numbers 801-900.
        """

        global have_got_ess
        global total_rxed

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
            raise Exception("Could not find the named port")

        midiin.ignore_types(sysex=False)

        # Flush the input queue
        midiin.get_message()
        time.sleep(0.2)

        total_rxed = b''

        # Send the SBS command

        pkt = self.make_packet(command=8, sub_command=2)
        # print(pkt)
        midiout.send_message(bytearray(pkt))  # SBS(HBR)
        self.wait_for_ack(midiin)

        pkt = self.make_packet(command=4, parameter_set=param_set, category=category, memory=memory)
        # print(pkt)
        midiout.send_message(bytearray(pkt))  # HBR

        have_got_ess = False

        while True:
            self.wait_for_ack(midiin)

            if have_got_ess:
                break

            pkt = self.make_packet(parameter_set=param_set, category=category, memory=memory, command=0xa)
            midiout.send_message(bytearray(pkt))

        # Send EBS (no ACK expected)
        midiout.send_message(
            bytearray(self.make_packet(parameter_set=param_set, category=category, memory=memory, command=0xe)))
        time.sleep(0.3)

        midiin.close_port()
        midiout.close_port()

        return total_rxed
