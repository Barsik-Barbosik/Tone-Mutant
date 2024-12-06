"""
This code is a refactored version of the MIDI communication methods originally written
by michgz, taken from the ToneTyrant project available at:
https://github.com/michgz/tonetyrant/blob/master/python/midi_comms.py

The original implementation has been modified for improved readability, modularity,
and adherence to Python's PEP 8 style guide.
"""

import binascii
import struct
import time

from services.midi_service import MidiService  # RtMidi has been replaced with the existing MidiService

have_got_ack = False
have_got_ess = False
is_busy = False
must_send_ack = False
so_far = b''
total_rxed = b''
type_1_rxed = b''


class TyrantMidiService:
    # Define the device ID. Constructed as follows:
    #    0x44       Manufacturer ID ( = Casio)
    #    0x19 0x01  Model ID ( = CT-X3000, CT-X5000, CT-X700)
    #    0x7F       Device. This is a "don't care" value
    DEVICE_ID = b'\x44\x19\x01\x7F'

    class SysexTimeoutError(Exception):
        pass

    def download_tone(self, param_set, memory=1, category=30, *, _debug=False):
        """
        Old name: download_ac7_internal
        Request and receive a complete parameter set from the keyboard.
        """
        global have_got_ack, have_got_ess, total_rxed
        total_rxed = b''

        # Get MIDI ports and replace callback
        midi_in, midi_out = MidiService.get_instance().provide_midi_ports()
        midi_in.set_callback(self.process_message)

        # Send SBS (Start Bulk Send) command and wait for ACK
        sbs_packet = self.make_packet(command=8, sub_command=2)
        # print(sbs_packet.hex())
        have_got_ack = False
        midi_out.send_message(bytearray(sbs_packet))
        self.wait_for_ack()

        # Send HBR command
        hbr_packet = self.make_packet(command=4, parameter_set=param_set, category=category, memory=memory)
        # print(hbr_packet.hex())
        midi_out.send_message(bytearray(hbr_packet))

        have_got_ess = False

        while not have_got_ess:
            have_got_ack = False
            self.wait_for_ack()
            pkt = self.make_packet(parameter_set=param_set, category=category, memory=memory, command=0x0A)
            midi_out.send_message(bytearray(pkt))

        # Send EBS (End Bulk Send) - No ACK expected
        esb_packet = self.make_packet(parameter_set=param_set, category=category, memory=memory, command=0x0E)
        # print(esb_packet.hex())
        midi_out.send_message(bytearray(esb_packet))
        time.sleep(0.3)
        return total_rxed

    def upload_tone(self, param_set, data, memory=1, category=30, *, _debug=True):
        """
        Old name: upload_ac7_internal
        Upload a complete parameter set to the keyboard.
        The meaning of the data and required length depend on "memory" and "category".

        Args:
            param_set: Parameter set number (0-99 for User Tone numbers 801-900).
            data: The data to be uploaded, length varies based on memory/category.
            memory: Memory location (default=1 for user memory).
            category: Data category (default=30 for rhythms).
            _debug: Enables debug logs if True.

        Raises:
            Exception: If MIDI ports cannot be opened or communication fails.
        """
        global have_got_ack

        # Get MIDI ports and replace callback
        midi_in, midi_out = MidiService.get_instance().provide_midi_ports()
        midi_in.set_callback(self.process_message)

        # Send SBS (Start Bulk Send) command and wait for ACK
        sbs_packet = self.make_packet(command=8, sub_command=3)
        if _debug:
            print(f"> SBS Packet: {sbs_packet.hex(' ').upper()}")
        have_got_ack = False
        midi_out.send_message(bytearray(sbs_packet))
        self.wait_for_ack()

        # Send data in chunks of up to 0x80 bytes
        i = 0
        while i < len(data):
            len_remaining = min(0x80, len(data) - i)
            data_packet = self.make_packet(
                parameter_set=param_set,
                category=category,
                memory=memory,
                command=5,
                length=len_remaining,
                data=data[i:i + len_remaining]
            )
            if _debug:
                print(f"> Data Packet (offset {i}): {data_packet.hex(' ').upper()}")
            have_got_ack = False
            midi_out.send_message(bytearray(data_packet))
            self.wait_for_ack()

            i += len_remaining

        # Send ESS (End Send Session) - No ACK expected
        ess_packet = self.make_packet(parameter_set=param_set, category=category, memory=memory, command=0xD)
        if _debug:
            print(f"> ESS Packet: {ess_packet.hex(' ').upper()}")
        midi_out.send_message(bytearray(ess_packet))
        time.sleep(0.3)

        # Send EBS (End Bulk Send) - No ACK expected
        ebs_packet = self.make_packet(parameter_set=param_set, category=category, memory=memory, command=0xE)
        if _debug:
            print(f"> EBS Packet: {ebs_packet.hex(' ').upper()}")
        midi_out.send_message(bytearray(ebs_packet))
        time.sleep(0.3)

    def make_packet(self, tx=False, category=30, memory=1, parameter_set=0,
                    block=None, parameter=0, index=0, length=1, command=-1,
                    sub_command=3, data=b''):
        """
        Construct a packet in Casio SYSEX format for sending over the MIDI port.
        """
        block = block or [0, 0, 0, 0]
        packet = b'\xf0' + self.DEVICE_ID

        if command < 0:
            command = 1 if tx else 0
        packet += struct.pack('<B', command)

        if command == 0x08:
            return packet + struct.pack('<B', sub_command) + b'\xf7'

        packet += struct.pack('<2B', category, memory)
        packet += struct.pack('<2B', parameter_set % 128, parameter_set // 128)

        if command == 0x0A:
            return packet + b'\xf7'

        if command == 5:
            packet += struct.pack('<2B', length % 128, length // 128)
            packet += self.midi_8bit_to_7bit(data)
            crc_val = binascii.crc32(packet[1:])
            packet += self.midi_8bit_to_7bit(struct.pack('<I', crc_val))
            return packet + b'\xf7'

        if command in (2, 3, 4, 6, 7, 0x0D, 0x0E):
            # Commands without additional processing
            pass
        else:
            if len(block) != 4:
                print(f"Invalid block length {len(block)}, resetting to zeros.")
                block = [0, 0, 0, 0]
            for blk in block:
                packet += struct.pack('<BB', blk % 128, blk // 128)
            packet += struct.pack('<BBHH', parameter % 128, parameter // 128, index, length - 1)

        if tx:
            packet += data

        return packet + b'\xf7'

    def wait_for_ack(self):
        """
        Wait for an ACK packet from the MIDI port.
        Raises a SysexTimeoutError if no ACK is received within 4 seconds.
        """
        global have_got_ack
        start_time = time.monotonic()

        while have_got_ack is False:
            if time.monotonic() > start_time + 4.0:
                print("timeout...")
                raise self.SysexTimeoutError("SYSEX communication timed out.")
            time.sleep(0.02)

    def process_message(self, message, _):
        message, deltatime = message
        # print(message)
        self.parse_response(bytes(message))

    def parse_response(self, data, *, _debug=False):
        """
        Parse bytes received from the MIDI port, collating them into SYSEX packets.

        Parameters:
            data (bytes): The incoming MIDI data.
            _debug (bool): If True, print debug information about parsed packets.
        """
        global so_far

        in_packet = bool(so_far)  # Determine if already in a packet

        for byte in data:
            if in_packet:
                if byte == 0xF7:  # End of SYSEX packet
                    so_far += b'\xF7'
                    if _debug:
                        print(so_far.hex(" ").upper())
                    self.handle_pkt(so_far)
                    so_far = b''  # Reset packet buffer
                    in_packet = False
                elif byte == 0xF0:  # Unexpected start of a new SYSEX packet
                    # Reset and start a new packet
                    so_far = b'\xF0'
                elif byte >= 0x80:  # Invalid MIDI data in a packet
                    # Error: Reset state
                    so_far = b''
                    in_packet = False
                else:
                    # Append valid data to the packet
                    so_far += bytes([byte])
            else:
                if byte == 0xF0:  # Start of a new SYSEX packet
                    so_far = b'\xF0'
                    in_packet = True

    def handle_pkt(self, packet):
        """
        Handle a complete packet as received from the MIDI port.
        It is assumed that each packet is in Casio SYSEX format.
        """
        global is_busy, must_send_ack, have_got_ack, have_got_ess, total_rxed, type_1_rxed

        # Validate packet length
        if len(packet) < 7:
            print("BAD PACKET!!")
            return

        # Validate packet structure
        if not (packet[0] == 0xF0 and packet[1] == 0x44 and packet[4] == 0x7F and packet[-1] == 0xF7):
            print("BAD PACKET!!")
            return

        # Extract packet type
        packet_type = packet[5]
        # print(packet_type)

        # Handle different packet types
        if packet_type == 0x0B:  # Busy signal
            is_busy = True
            return
        else:
            is_busy = False
            if packet_type == 0x0A:  # ACK
                have_got_ack = True
            elif packet_type == 0x0D:  # ESS
                have_got_ack = True
                have_got_ess = True

        # Handle CRC-validated packets
        if packet_type in (0x03, 0x05):  # Packets requiring CRC
            crc_received = self._extract_crc(packet)
            crc_calculated = binascii.crc32(packet[1:-6])

            if crc_calculated == crc_received:
                must_send_ack = True
                if packet_type == 0x05:  # Packet with data
                    have_got_ack = True
                    data = self.midi_7bit_to_8bit(packet[12:-6])
                    total_rxed += data
            else:
                print("BAD CRC!!!")

        # Handle type 1 packets
        if packet_type == 0x01:
            type_1_rxed = packet[24:-1]

    @staticmethod
    def midi_8bit_to_7bit(b):
        """
        Encode to MIDI "7-bit format", which requires the MSb of each byte to be zero.
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

    @staticmethod
    def midi_7bit_to_8bit(b):
        """
        Decode from MIDI "7-bit format", which requires the MSb of each byte to be zero.
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

    @staticmethod
    def _extract_crc(packet):
        """
        Extract the CRC from a packet.
        """
        crc_bytes = struct.unpack('<5B', packet[-6:-1])
        return sum(crc_bytes[i] << (7 * i) for i in range(5))
