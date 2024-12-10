"""
This code is a modified version of the MIDI communication methods originally written
by michgz, taken from the ToneTyrant and ac7maker projects available at:
https://github.com/michgz/tonetyrant/blob/master/python/midi_comms.py
https://github.com/michgz/ac7maker/blob/master/internal/tone_rw.py
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
    TONE_CATEGORY = 3
    PARAM_LIST = list(range(0, 123)) + [200, 201, 202]  # Correct for CT-X3000/5000
    IS_DEBUG_MODE = False

    class SysexTimeoutError(Exception):
        pass

    def read_current_tone(self):
        """
        Original name: tone_read

        Read current tone directly from the keyboard.
        Bulk uploads & downloads for some reason don't work, so it needs to be done parameter-by-parameter.

        Function reads a tone from the "currently selected" memory segment (memory 3), and returns it HBR form.
        This particular memory segment doesn't permit true HBR reads, so under the hood this is multiple single parameter reads.
        """
        parameter_set = 0
        memory = 3

        if self.IS_DEBUG_MODE:
            t1 = time.time()

        # Get MIDI ports and replace callback (callback is used instead of MidiIn.get_message())
        midi_in, midi_out = MidiService.get_instance().provide_midi_ports()
        midi_in.set_callback(self.process_message)

        y = []

        for p in self.PARAM_LIST:
            z = []
            if p != 0 and p != 84:  # Name or DSP name. They will be filled with default values only, so don't need to read
                for b in range(self.block_count_for_parameter(p)):
                    length = 0
                    if p == 87:
                        length = 15
                    single_parameter = self.get_single_parameter(midi_out, p, length=length, memory=memory,
                                                                 category=self.TONE_CATEGORY,
                                                                 parameter_set=parameter_set, block0=b)
                    z.append(single_parameter)

            y.append(z)

            if self.IS_DEBUG_MODE:
                print("-----")

        if self.IS_DEBUG_MODE:
            t2 = time.time()
            print("tone_read() function: time elapsed {0:.3f} seconds".format(t2 - t1))

        x = bytearray(b'\x00' * 0x1C8)

        # Name
        # x[0x1A6:0x1B6] = b'                '
        x[0x1A6:0x1B6] = b'TheNameOfTheTone'

        for (a, b) in [(0, 0x00), (20, 0x88)]:
            x[b + 0x00:b + 0x02] = self.to_2b(y[a + 7][0])
            x[b + 0x02:b + 0x04] = self.to_2b(y[a + 6][0])
            x[b + 0x04:b + 0x06] = self.to_2b(y[a + 7][1])
            x[b + 0x06:b + 0x08] = self.to_2b(y[a + 6][1])
            x[b + 0x08:b + 0x0A] = self.to_2b(y[a + 7][2])
            x[b + 0x0A:b + 0x0C] = self.to_2b(y[a + 6][2])

            x[b + 0x0C:b + 0x0E] = self.to_2b(y[a + 11][0])
            x[b + 0x0E:b + 0x10] = self.to_2b(y[a + 10][0])
            x[b + 0x10:b + 0x12] = self.to_2b(y[a + 11][1])
            x[b + 0x12:b + 0x14] = self.to_2b(y[a + 10][1])
            x[b + 0x14:b + 0x16] = self.to_2b(y[a + 11][2])
            x[b + 0x16:b + 0x18] = self.to_2b(y[a + 10][2])
            x[b + 0x18:b + 0x1A] = self.to_2b(y[a + 11][3])

            x[b + 0x1A:b + 0x1C] = self.to_2b(y[a + 10][3])
            x[b + 0x1C:b + 0x1E] = self.to_2b(y[a + 11][4])
            x[b + 0x1E:b + 0x20] = self.to_2b(y[a + 10][4])
            x[b + 0x20:b + 0x22] = self.to_2b(y[a + 11][5])
            x[b + 0x22:b + 0x24] = self.to_2b(y[a + 10][5])
            x[b + 0x24:b + 0x26] = self.to_2b(y[a + 11][6])
            x[b + 0x26:b + 0x28] = self.to_2b(y[a + 10][6])

            x[b + 0x7C] = y[a + 8][0]
            x[b + 0x7D] = y[a + 9][0]
            x[b + 0x7E:b + 0x7F] = self.to_1b(y[a + 14][0])
            x[b + 0x7F:b + 0x80] = self.to_1b(y[a + 15][0])
            x[b + 0x80:b + 0x81] = self.to_1b(y[a + 16][0])

            x[b + 0x28:b + 0x2A] = self.to_2b(y[a + 13][0])
            x[b + 0x2A:b + 0x2C] = self.to_2b(y[a + 12][0])
            x[b + 0x2C:b + 0x2E] = self.to_2b(y[a + 13][1])
            x[b + 0x2E:b + 0x30] = self.to_2b(y[a + 12][1])
            x[b + 0x30:b + 0x32] = self.to_2b(y[a + 13][2])
            x[b + 0x32:b + 0x34] = self.to_2b(y[a + 12][2])
            x[b + 0x34:b + 0x36] = self.to_2b(y[a + 13][3])
            x[b + 0x36:b + 0x38] = self.to_2b(y[a + 12][3])
            x[b + 0x38:b + 0x3A] = self.to_2b(y[a + 13][4])
            x[b + 0x3A:b + 0x3C] = self.to_2b(y[a + 12][4])
            x[b + 0x3C:b + 0x3E] = self.to_2b(y[a + 13][5])
            x[b + 0x3E:b + 0x40] = self.to_2b(y[a + 12][5])
            x[b + 0x40:b + 0x42] = self.to_2b(y[a + 13][6])
            x[b + 0x42:b + 0x44] = self.to_2b(y[a + 12][6])

            x[b + 0x44:b + 0x46] = self.to_2b(y[a + 18][0])
            x[b + 0x46:b + 0x48] = self.to_2b(y[a + 17][0])
            x[b + 0x48:b + 0x4A] = self.to_2b(y[a + 18][1])
            x[b + 0x4A:b + 0x4C] = self.to_2b(y[a + 17][1])
            x[b + 0x4C:b + 0x4E] = self.to_2b(y[a + 18][2])
            x[b + 0x4E:b + 0x50] = self.to_2b(y[a + 17][2])
            x[b + 0x50:b + 0x52] = self.to_2b(y[a + 18][3])
            x[b + 0x52:b + 0x54] = self.to_2b(y[a + 17][3])
            x[b + 0x54:b + 0x56] = self.to_2b(y[a + 18][4])
            x[b + 0x56:b + 0x58] = self.to_2b(y[a + 17][4])
            x[b + 0x58:b + 0x5A] = self.to_2b(y[a + 18][5])
            x[b + 0x5A:b + 0x5C] = self.to_2b(y[a + 17][5])
            x[b + 0x5C:b + 0x5E] = self.to_2b(y[a + 18][6])
            x[b + 0x5E:b + 0x60] = self.to_2b(y[a + 17][6])

            x[b + 0x60:b + 0x62] = self.to_2b(y[a + 20][0])
            x[b + 0x62:b + 0x64] = self.to_2b(y[a + 19][0])
            x[b + 0x64:b + 0x66] = self.to_2b(y[a + 20][1])
            x[b + 0x66:b + 0x68] = self.to_2b(y[a + 19][1])
            x[b + 0x68:b + 0x6A] = self.to_2b(y[a + 20][2])
            x[b + 0x6A:b + 0x6C] = self.to_2b(y[a + 19][2])
            x[b + 0x6C:b + 0x6E] = self.to_2b(y[a + 20][3])
            x[b + 0x6E:b + 0x70] = self.to_2b(y[a + 19][3])
            x[b + 0x70:b + 0x72] = self.to_2b(y[a + 20][4])
            x[b + 0x72:b + 0x74] = self.to_2b(y[a + 19][4])
            x[b + 0x74:b + 0x76] = self.to_2b(y[a + 20][5])
            x[b + 0x76:b + 0x78] = self.to_2b(y[a + 19][5])
            x[b + 0x78:b + 0x7A] = self.to_2b(y[a + 20][6])
            x[b + 0x7A:b + 0x7C] = self.to_2b(y[a + 19][6])

            x[b + 0x82:b + 0x84] = self.to_2b(y[a + 2][0])
            x[b + 0x84:b + 0x85] = self.to_1b(y[a + 3][0])
            x[b + 0x85:b + 0x86] = self.to_1b(y[a + 4][0])
            x[b + 0x86:b + 0x87] = self.to_1b(y[a + 5][0])
            x[b + 0x87] = y[a + 1][0]

        x[0x110] = y[56][0]
        x[0x111] = y[57][0]
        x[0x112] = y[58][0]
        x[0x113] = y[60][0]
        x[0x114] = y[61][0]
        x[0x115] = y[62][0]
        x[0x116] = y[63][0]
        x[0x117] = y[64][0]
        x[0x118] = y[65][0]

        x[0x119] = y[67][0]
        x[0x11A] = y[68][0]
        x[0x11B] = y[69][0]
        x[0x11C] = y[70][0]

        x[0x11D] = y[71][0]
        x[0x11E] = y[72][0]
        x[0x11F] = y[73][0]
        x[0x120] = y[74][0]

        x[0x121:0x122] = self.to_1b(y[75][0])
        x[0x122:0x123] = self.to_1b(y[76][0])
        x[0x123:0x124] = self.to_1b(y[77][0])

        x[0x180:0x181] = self.to_1b(y[93][0])
        x[0x181:0x182] = self.to_1b(y[97][0])
        x[0x182:0x183] = self.to_1b(y[98][0])

        x[0x184:0x188] = struct.pack('<I', y[100][0])
        x[0x188:0x18C] = struct.pack('<I', y[101][0])
        x[0x18C] = y[102][0]
        x[0x18D:0x18E] = self.to_1b(y[103][0])
        x[0x18E:0x18F] = self.to_1b(y[104][0])
        x[0x18F:0x190] = self.to_1b(y[105][0])
        x[0x190:0x194] = struct.pack('<I', y[106][0])
        x[0x194:0x195] = self.to_1b(y[107][0])
        x[0x195:0x196] = self.to_1b(y[108][0])

        x[0x1B6:0x1B7] = self.to_1b(y[45][0])
        x[0x1B7:0x1B8] = self.to_1b(y[46][0])
        x[0x1B8:0x1B9] = self.to_1b(y[47][0])
        x[0x1B9:0x1BA] = self.to_1b(y[48][0])
        x[0x1BA:0x1BB] = self.to_1b(y[49][0])
        x[0x1BB:0x1BC] = self.to_1b(y[50][0])
        x[0x1BC:0x1BD] = self.to_1b(y[51][0])
        x[0x1BD:0x1BE] = self.to_1b(y[52][0])
        x[0x1BE:0x1BF] = self.to_1b(y[53][0])
        x[0x1BF:0x1C0] = self.to_1b(y[54][0])

        x[0x1C0:0x1C1] = self.to_1b(y[78][0])
        x[0x1C1:0x1C2] = self.to_1b(y[79][0])

        x[0x124] = 0xFF  # ?? Always 0xFF but no parameters

        x[0x1C2] = y[123][0]  # parameter 200
        x[0x1C3] = y[124][0]  # parameter 201
        x[0x1C4] = y[125][0]  # parameter 202
        x[0x1C5:0x1C8] = b'\x00\x00\x00'

        # DSP parameters
        x[0x126:0x136] = b'                '  # Name
        for j in range(4):
            dsp = y[85][j]
            self.check_less(y[86][j], 2)
            if y[86][j] != 0:
                dsp += 0x4000
            x[0x136 + j * 0x12:0x138 + j * 0x12] = struct.pack('<H', dsp)
            if len(y[87][j]) > 0 and len(y[87][j]) < 16:
                x[0x138 + j * 0x12:0x138 + len(y[87][j]) + j * 0x12] = y[87][j]

        # Bit field parameters
        self.check_less(y[109][0], 2)

        if y[109][0]:
            x[0x196] = 1
        x[0x197] = y[110][0]
        x[0x198] = y[111][0]
        x[0x199] = y[112][0]

        v = 0
        self.check_less(y[113][0], 16)
        self.check_less(y[114][0], 2)
        self.check_less(y[115][0], 2)
        self.check_less(y[116][0], 4)
        if y[113][0]:
            v += (y[113][0] % 16)
        if y[114][0]:
            v += 0x10
        if y[115][0]:
            v += 0x20
        v += 0x40 * (y[116][0] % 4)
        x[0x19A] = v

        v = 0
        self.check_less(y[92][0], 8)
        self.check_less(y[94][0], 4)
        self.check_less(y[95][0], 2)
        self.check_less(y[96][0], 2)
        self.check_less(y[99][0], 2)
        if y[99][0]:
            v += 1
        if y[96][0]:
            v += 0x02
        if y[95][0]:
            v += 0x04
        v += 0x08 * (y[94][0] % 4)
        v += 0x20 * (y[92][0] % 8)
        x[0x17E] = v

        v = 0
        self.check_less(y[88][0], 2)
        self.check_less(y[89][0], 4)
        self.check_less(y[90][0], 2)
        self.check_less(y[91][0], 2)
        if y[91][0]:
            v += 0x02
        if y[90][0]:
            v += 0x04
        v += 0x08 * (y[89][0] % 4)
        if y[88][0]:
            v += 0x80
        x[0x17F] = v

        v = 0
        self.check_less(y[55][0], 2)
        self.check_less(y[80][0], 16)
        self.check_less(y[81][0], 2)
        self.check_less(y[82][0], 2)
        self.check_less(y[83][0], 2)
        if y[83][0]:
            v += 0x01
        if y[82][0]:
            v += 0x02
        if y[81][0]:
            v += 0x04
        v += 0x08 * (y[80][0] % 16)
        if y[55][0]:
            v += 0x80
        x[0x1A4] = v

        v = 0
        self.check_less(y[41][0], 2)
        self.check_less(y[42][0], 4)
        self.check_less(y[43][0], 8)
        self.check_less(y[44][0], 2)
        if y[44][0]:
            v += 0x01
        v += 2 * (y[43][0] % 8)
        v += 0x20 * (y[42][0] % 4)
        if y[41][0]:
            v += 0x80
        x[0x1A5] = v

        v = 0
        self.check_less(y[59][0], 16)
        self.check_less(y[66][0], 16)
        v += 16 * (y[59][0] % 16)
        v += (y[66][0] % 16)
        x[0x124] = v

        # Filters
        self.check_less(y[117][0], 16)
        self.check_less(y[118][0], 64)
        self.check_less(y[119][0], 64)
        self.check_less(y[120][0], 16)
        self.check_less(y[121][0], 2)
        self.check_less(y[122][0], 8)
        self.check_less(y[117][1], 16)
        self.check_less(y[118][1], 64)
        self.check_less(y[119][1], 64)
        self.check_less(y[120][1], 16)
        self.check_less(y[121][1], 2)
        self.check_less(y[122][1], 8)

        x[0x19C] = (y[117][0] % 16) + 16 * (y[118][0] % 16)
        x[0x1A0] = (y[117][1] % 16) + 16 * (y[118][1] % 16)

        x[0x19D] = ((y[118][0] // 16) % 4) + 4 * (y[119][0] % 64)
        x[0x1A1] = ((y[118][1] // 16) % 4) + 4 * (y[119][1] % 64)

        x[0x19E] = (y[122][0] % 8) + 8 * (y[121][0] % 2) + 16 * (y[120][0] % 16)
        x[0x1A2] = (y[122][1] % 8) + 8 * (y[121][1] % 2) + 16 * (y[120][1] % 16)

        return x

    def get_single_parameter(self, midi_out, parameter, category=3, memory=3, parameter_set=0, block0=0, block1=0,
                             length=0):
        global type_1_rxed
        type_1_rxed = b''

        if length > 0:
            l = length
        else:
            l = 1

        # Read the parameter
        packet = self.make_packet(parameter_set=parameter_set, category=category, memory=memory, parameter=parameter,
                                  block=[0, 0, block1, block0], length=l)
        if self.IS_DEBUG_MODE:
            print("Parameter {0} ([{1},{2}])".format(parameter, block1, block0))
            print(f"packet: {packet.hex()}")
        midi_out.send_message(bytearray(packet))
        time.sleep(0.01)

        # Decode the response. Value of "length" determines whether to regard it as a string or a number.
        if length > 0:
            # Regard the response as a string
            if len(type_1_rxed) > 0:  # should maybe check this is equal to length??
                return type_1_rxed
            else:
                return b''  # Error! Nothing read
        else:
            # Regard the response as a number
            f = -1
            if len(type_1_rxed) > 0:
                # A number has been received. Decode it.
                if len(type_1_rxed) == 1:
                    f = struct.unpack('<B', type_1_rxed)[0]
                elif len(type_1_rxed) == 2:
                    g = struct.unpack('<2B', type_1_rxed)
                    if g[0] >= 128 or g[1] >= 128:
                        raise Exception("Invalid packed value")
                    f = g[0] + 128 * g[1]
                elif len(type_1_rxed) == 3:
                    g = struct.unpack('<3B', type_1_rxed)
                    if g[0] >= 128 or g[1] >= 128 or g[2] >= 128:
                        raise Exception("Invalid packed value")
                    f = g[0] + 128 * g[1] + 128 * 128 * g[2]
                elif len(type_1_rxed) == 4:
                    g = struct.unpack('<4B', type_1_rxed)
                    if g[0] >= 128 or g[1] >= 128 or g[2] >= 128 or g[3] >= 128:
                        raise Exception("Invalid packed value")
                    f = g[0] + 128 * g[1] + 128 * 128 * g[2] + 128 * 128 * 128 * g[3]
                elif len(type_1_rxed) == 5:
                    g = struct.unpack('<5B', type_1_rxed)
                    if g[0] >= 128 or g[1] >= 128 or g[2] >= 128 or g[3] >= 128 or g[4] >= 16:
                        raise Exception("Invalid packed value")
                    f = g[0] + 128 * g[1] + 128 * 128 * g[2] + 128 * 128 * 128 * g[3] + 128 * 128 * 128 * 128 * g[4]
                else:
                    # raise Exception("Too long to be a number")
                    pass
            return f

    def bulk_download(self, param_set, memory=1, category=30):
        """
        Original name: download_ac7_internal
        Request and receive a complete parameter set from the keyboard.
        """
        global have_got_ack, have_got_ess, total_rxed
        total_rxed = b''

        # Get MIDI ports and replace callback
        midi_in, midi_out = MidiService.get_instance().provide_midi_ports()
        midi_in.set_callback(self.process_message)

        # Send SBS (Start Bulk Send) command and wait for ACK
        sbs_packet = self.make_packet(command=8, sub_command=2)
        if self.IS_DEBUG_MODE:
            print(f"SBS packet: {sbs_packet.hex()}")
        have_got_ack = False
        midi_out.send_message(bytearray(sbs_packet))
        self.wait_for_ack()

        # Send HBR command
        hbr_packet = self.make_packet(command=4, parameter_set=param_set, category=category, memory=memory)
        if self.IS_DEBUG_MODE:
            print(f"HBR packet: {hbr_packet.hex()}")
        midi_out.send_message(bytearray(hbr_packet))

        have_got_ess = False

        while not have_got_ess:
            have_got_ack = False
            self.wait_for_ack()
            pkt = self.make_packet(parameter_set=param_set, category=category, memory=memory, command=0x0A)
            if self.IS_DEBUG_MODE:
                print(f"packet: {pkt.hex()}")
            midi_out.send_message(bytearray(pkt))

        # Send EBS (End Bulk Send) - No ACK expected
        esb_packet = self.make_packet(parameter_set=param_set, category=category, memory=memory, command=0x0E)
        if self.IS_DEBUG_MODE:
            print(f"ESB packet: {esb_packet.hex()}")
        midi_out.send_message(bytearray(esb_packet))
        time.sleep(0.3)
        return total_rxed

    def bulk_upload(self, param_set, data, memory=1, category=30):
        """
        Original name: upload_ac7_internal
        Upload a complete parameter set to the keyboard.
        The meaning of the data and required length depend on "memory" and "category".

        Args:
            param_set: Parameter set number (0-99 for User Tone numbers 801-900).
            data: The data to be uploaded, length varies based on memory/category.
            memory: Memory location (default=1 for user memory).
            category: Data category (default=30 for rhythms).

        Raises:
            Exception: If MIDI ports cannot be opened or communication fails.
        """
        global have_got_ack

        # Get MIDI ports and replace callback
        midi_in, midi_out = MidiService.get_instance().provide_midi_ports()
        midi_in.set_callback(self.process_message)

        # Send SBS (Start Bulk Send) command and wait for ACK
        sbs_packet = self.make_packet(command=8, sub_command=3)
        if self.IS_DEBUG_MODE:
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
            if self.IS_DEBUG_MODE:
                print(f"> Data Packet (offset {i}): {data_packet.hex(' ').upper()}")
            have_got_ack = False
            midi_out.send_message(bytearray(data_packet))
            self.wait_for_ack()

            i += len_remaining

        # Send ESS (End Send Session) - No ACK expected
        ess_packet = self.make_packet(parameter_set=param_set, category=category, memory=memory, command=0xD)
        if self.IS_DEBUG_MODE:
            print(f"> ESS Packet: {ess_packet.hex(' ').upper()}")
        midi_out.send_message(bytearray(ess_packet))
        time.sleep(0.3)

        # Send EBS (End Bulk Send) - No ACK expected
        ebs_packet = self.make_packet(parameter_set=param_set, category=category, memory=memory, command=0xE)
        if self.IS_DEBUG_MODE:
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
                if self.IS_DEBUG_MODE:
                    print("have_got_ack: timeout...")
                raise self.SysexTimeoutError("SYSEX communication timed out.")
            time.sleep(0.02)

    def process_message(self, message, _):
        message, deltatime = message
        if self.IS_DEBUG_MODE:
            print(f"MIDI IN message: {message}")
        self.parse_response(bytes(message))

    def parse_response(self, data):
        """
        Parse bytes received from the MIDI port, collating them into SYSEX packets.

        Parameters:
            data (bytes): The incoming MIDI data.
        """
        global so_far

        in_packet = bool(so_far)  # Determine if already in a packet

        for byte in data:
            if in_packet:
                if byte == 0xF7:  # End of SYSEX packet
                    so_far += b'\xF7'
                    if self.IS_DEBUG_MODE:
                        print("so_far: " + so_far.hex(" ").upper())
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

        if self.IS_DEBUG_MODE:
            print(f"packet received: {packet.hex()}")

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
    def to_1b(v):
        """
        Number to single-byte parameter
        """
        return struct.pack('B', v)

    @staticmethod
    def to_2b(v):
        """
        Number to dual-byte parameter
        """
        # return struct.pack('2B', v//128, v%128)
        return struct.pack('<H', v)

    @staticmethod
    def check_less(v, mx):
        if v >= mx:
            # print(v)
            raise Exception

    @staticmethod
    def _extract_crc(packet):
        """
        Extract the CRC from a packet.
        """
        crc_bytes = struct.unpack('<5B', packet[-6:-1])
        return sum(crc_bytes[i] << (7 * i) for i in range(5))

    @staticmethod
    def block_count_for_parameter(p):
        """
        Return the number of blocks for a specific parameter
        """
        if p >= 117 and p <= 122:
            return 2
        if p >= 85 and p <= 87:
            return 4
        if p >= 17 and p <= 20:
            return 7
        if p >= 10 and p <= 11:
            return 7
        if p >= 12 and p <= 13:
            return 7
        if p >= 6 and p <= 7:
            return 3
        if p >= 37 and p <= 40:
            return 7
        if p >= 30 and p <= 31:
            return 7
        if p >= 32 and p <= 33:
            return 7
        if p >= 26 and p <= 27:
            return 3
        return 1

    @staticmethod
    def wrap_tone_file(x):
        y = b'CT-X3000'
        y += struct.pack('<2I', 0, 0)
        y += b'TONH'
        y += struct.pack('<3I', 0, binascii.crc32(x), len(x))
        y += x
        y += b'EODA'
        return y
