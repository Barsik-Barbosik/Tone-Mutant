from tests.qt_helpers import synchronize_tone_with_synth
"""Exhaustive conversion, malformed input and captured CT-X800 regression tests."""
import binascii
import copy
from collections import deque
import json
from pathlib import Path
import random
import unittest
from unittest.mock import Mock, patch
from types import SimpleNamespace

from PySide6.QtCore import QReadWriteLock
from constants import constants
from constants.enums import ParameterType
from models.tone import Tone
from services.midi_service import MidiService
from services.tyrant_midi_service import TyrantMidiService
from tools.probe_ctx800 import request_packet, parse_reply, plan
from utils.utils import encode_value_by_type, decode_param_value, int_to_lsb_msb, lsb_msb_to_int


def fake_service():
    service = object.__new__(MidiService)
    service.core = Mock()
    service.lock = QReadWriteLock()
    service.active_sync_job_count = 0
    service.bank_select_msg_queue = deque()
    tone = Tone()
    service.short_params = [234, 237] + [p.param_number for p in tone.main_parameter_list + tone.advanced_parameter_list
                                        if p.name in constants.SHORT_PARAMS]
    service.long_params = [p.param_number for p in tone.main_parameter_list + tone.advanced_parameter_list
                           if p.name not in constants.SHORT_PARAMS]
    return service


class ProtocolTests(unittest.TestCase):
    def test_ctx800_uses_documented_octave_and_note_off_limits(self):
        tone = Tone()
        tone.configure_model(constants.CTX_700_800)
        octave = next(p for p in tone.main_parameter_list if p.param_number == 43)
        note_off = next(p for p in tone.advanced_parameter_list if p.param_number == 42)
        self.assertEqual(octave.choices, [-2, 2])
        for ui, raw in ((-2, 2), (0, 4), (2, 6)):
            octave.value = ui
            self.assertEqual(encode_value_by_type(octave), raw)
            self.assertEqual(decode_param_value(raw, octave), ui)
        self.assertEqual(note_off.choices, ["Note-off Velocity", "Note-on Velocity", "Both"])
        tone.configure_model(constants.CTX_3000_5000)
        self.assertEqual(octave.choices, [-3, 3])
        self.assertEqual(len(note_off.choices), 4)

    def test_all_14_bit_integers_roundtrip(self):
        for value in range(16384):
            raw = bytes.fromhex(int_to_lsb_msb(value))
            self.assertTrue(all(byte < 128 for byte in raw))
            self.assertEqual(lsb_msb_to_int(*raw), value)

    def test_all_descriptor_values_roundtrip(self):
        tone = Tone()
        parameters = tone.main_parameter_list + tone.advanced_parameter_list
        for module in constants.ALL_DSP_MODULES:
            parameters += copy.deepcopy(module.dsp_parameter_list + [module.bypass])
        checked = 0
        for parameter in parameters:
            if parameter.type == ParameterType.SPECIAL_DELAY_KNOB:
                continue
            values = range(len(parameter.choices)) if parameter.type == ParameterType.COMBO else range(
                parameter.choices[0], parameter.choices[1] + 1)
            for value in values:
                parameter.value = value
                self.assertEqual(decode_param_value(encode_value_by_type(parameter), parameter), value,
                                 "{} value {}".format(parameter.name, value))
                checked += 1
        self.assertGreater(checked, 20000)

    def test_attack_release_off_grid_values_stay_in_ui_range(self):
        parameter = Tone().main_parameter_list[0]
        for raw in range(16384):
            decoded = decode_param_value(raw, parameter)
            self.assertTrue(0 <= decoded <= 127, "raw {} decoded {}".format(raw, decoded))
        self.assertEqual(decode_param_value(0, parameter), 127)
        self.assertEqual(decode_param_value(16383, parameter), 0)

    def test_packed_bytes_match_independent_bitstream_encoder(self):
        rng = random.Random(20261019)
        service = TyrantMidiService()
        for size in list(range(40)) + [127, 128, 129, 255, 256, 456, 512, 4096]:
            raw = bytes(rng.randrange(256) for _ in range(size))
            number = int.from_bytes(raw, "little")
            expected = bytes((number >> shift) & 127 for shift in range(0, size * 8, 7))
            packed = service.midi_8bit_to_7bit(raw)
            self.assertEqual(packed, expected, "payload length {}".format(size))
            self.assertEqual(service.midi_7bit_to_8bit(packed), raw)

    def test_tone_file_roundtrip_and_integrity(self):
        service = TyrantMidiService()
        raw = bytes((i * 17) % 256 for i in range(456))
        wrapped = service.wrap_tone_file(raw)
        self.assertEqual(service.unwrap_tone_file(wrapped), raw)
        for offset in (16, 24, 28, 100, len(wrapped) - 5):
            damaged = bytearray(wrapped)
            damaged[offset] ^= 1
            with self.subTest(offset=offset), self.assertRaises(ValueError):
                service.unwrap_tone_file(bytes(damaged))
        with self.assertRaises(ValueError):
            service.unwrap_tone_file(wrapped[:-5] + wrapped[-4:])

    def test_malformed_midi_never_crashes_or_updates_tone(self):
        service = fake_service()
        rng = random.Random(20261019)
        messages = [[], [0xF0], [0xF0, 0x44], [0xB0], [0xB0, 0], [0xC0], [0xC1]]
        messages += [[rng.randrange(256) for _ in range(rng.randrange(65))] for _ in range(4000)]
        with patch("services.midi_service.time.sleep"):
            for message in messages:
                service.process_message((message, 0), None)
        service.core.process_parameter_response.assert_not_called()
        service.core.process_tone_name_response.assert_not_called()

    def test_foreign_model_and_request_echo_do_not_update_tone(self):
        service = fake_service()
        request = request_packet(45)
        reply = request[:-1] + [90, 0xF7]
        reply[5] = 1
        foreign = reply[:]
        foreign[2] = 0x20
        for message in (request, foreign, reply[:-2] + [0xF7]):
            service.process_message((message, 0), None)
        service.core.process_parameter_response.assert_not_called()

    def test_bulk_sysex_roundtrip_and_crc(self):
        import services.tyrant_midi_service as state
        service = TyrantMidiService()
        raw = bytes(range(128))
        packet = service.make_packet(command=5, category=3, data=raw, length=len(raw))
        self.assertTrue(all(byte < 128 for byte in packet[1:-1]))
        self.assertEqual(service._extract_crc(packet), binascii.crc32(packet[1:-6]))
        state.total_rxed = b''
        state.have_got_ack = False
        service.handle_pkt(packet)
        self.assertEqual(state.total_rxed, raw)
        self.assertTrue(state.have_got_ack)

    def test_realtime_byte_does_not_destroy_partial_sysex(self):
        import services.tyrant_midi_service as state
        state.so_far = b''
        service = TyrantMidiService()
        packet = service.make_packet(command=0x0A, category=3)
        with patch.object(service, "handle_pkt") as handle:
            service.parse_response(packet[:4] + b'\xf8' + packet[4:])
            handle.assert_called_once_with(packet)

    def test_probe_can_only_generate_read_requests(self):
        for _, parameter, block, length in plan():
            packet = request_packet(parameter, block, length)
            self.assertEqual(packet[5], 0)
            self.assertEqual(len(packet), 25)
            self.assertTrue(all(0 <= byte < 128 for byte in packet[1:-1]))
            self.assertEqual(packet[6:10], [3, 3, 0, 0])

    def test_delay_values_roundtrip_including_leading_zeroes(self):
        from core import Core
        from ui.dsp_page import DspPage
        tone = Tone()
        module = copy.deepcopy(next(module for module in constants.ALL_DSP_MODULES if module.name == "Delay"))
        tone.dsp_module_1 = module
        target = SimpleNamespace(tone=tone, main_window=Mock())
        page = SimpleNamespace(dsp_module=module)
        for value in range(1, 1100):
            module.dsp_parameter_list[0].value = value
            packet = DspPage.get_dsp_params_as_list(page)
            Core.process_dsp_module_parameters_response(target, 0, packet)
            self.assertEqual(module.dsp_parameter_list[0].value, value, "Delay time {}".format(value))

    def test_tyrant_packet_index_and_array_length_use_7_bit_pairs(self):
        service = TyrantMidiService()
        for value in (0, 127, 128, 255, 16383):
            packet = service.make_packet(category=3, memory=3, index=value, length=value + 1)
            self.assertEqual(packet[20:22], bytes.fromhex(int_to_lsb_msb(value)))
            self.assertEqual(packet[22:24], bytes.fromhex(int_to_lsb_msb(value)))
            self.assertTrue(all(byte < 128 for byte in packet[1:-1]))

    def test_captured_survey_is_readable_beyond_the_visible_controls(self):
        path = Path(__file__).resolve().parents[1] / "captures" / "ctx800-survey-20261019.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        replies = {entry["parameter"]: entry["reply"] for entry in data["requests"]}
        self.assertEqual(len(replies), 126)
        self.assertTrue(all(replies[parameter] is not None for parameter in range(123)))
        self.assertTrue(all(replies[parameter] is None for parameter in (200, 201, 202)))
        for parameter in (100, 101, 106):
            self.assertEqual(len(replies[parameter]["data"]), 5)

    def test_real_capture_can_be_replayed_without_hardware(self):
        capture = Path(__file__).resolve().parents[1] / "captures" / "ctx800-readonly-20261019.json"
        self.assertTrue(capture.is_file(), "Keep the anonymized fixture with the tests")
        data = json.loads(capture.read_text(encoding="utf-8"))
        self.assertEqual(len(data["requests"]), 40)
        self.assertTrue(all(item["reply"] is not None for item in data["requests"]))
        service = fake_service()
        for received in data["received"]:
            message = list(bytes.fromhex(received["hex"]))
            self.assertEqual(parse_reply(message), received["reply"])
            service.process_message((message, 0), None)
        service.core.process_tone_name_response.assert_called_once()
        self.assertGreater(service.core.process_parameter_response.call_count, 20)

    def test_real_capture_populates_native_window_with_valid_values(self):
        from PySide6.QtWidgets import QApplication
        from ui.main_window import MainWindow
        app = QApplication.instance() or QApplication([])
        path = Path(__file__).resolve().parents[1] / "captures" / "ctx800-readonly-20261019.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        with patch("core.MidiService"), patch("core.TyrantMidiService"), \
             patch("core.Core.synchronize_tone_with_synth", new=synchronize_tone_with_synth):
            window = MainWindow()
            service = fake_service()
            service.core = window.core
            for received in data["received"]:
                service.process_message((list(bytes.fromhex(received["hex"])), 0), None)
            app.processEvents()
            tone = window.core.tone
            parameters = tone.main_parameter_list + tone.advanced_parameter_list
            for module in (tone.dsp_module_1, tone.dsp_module_2, tone.dsp_module_3, tone.dsp_module_4):
                if module:
                    parameters += module.dsp_parameter_list
            for parameter in parameters:
                with self.subTest(parameter=parameter.name):
                    if parameter.type == ParameterType.COMBO:
                        self.assertIn(parameter.value, range(len(parameter.choices)))
                    else:
                        self.assertTrue(parameter.choices[0] <= parameter.value <= parameter.choices[1])
            window.core.midi_service.send_parameter_change_sysex.assert_not_called()
            window.core.midi_service.send_atk_rel_parameter_change_sysex.assert_not_called()
            window.close()


if __name__ == "__main__":
    unittest.main()
