from tests.qt_helpers import synchronize_tone_with_synth
"""Regression coverage for program changes arriving on RtMidi's native thread."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import threading
import unittest
from unittest.mock import Mock, patch

from PySide6.QtCore import QThread
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from test_protocol import fake_service
from core import Core


class MidiThreadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.patches = [patch("core.MidiService"), patch("core.TyrantMidiService"),
                        patch("core.Core.synchronize_tone_with_synth", new=synchronize_tone_with_synth)]
        for item in self.patches: item.start()
        self.window = MainWindow()
        self.core = self.window.core
        self.service = fake_service()
        self.service.core = self.core
        self.service.midi_in = Mock()
        self.service.midi_out = Mock()
        self.core.midi_service = self.service
        self.core._test_synchronizations = 0

    def tearDown(self):
        self.window.close()
        for item in reversed(self.patches): item.stop()

    def test_1000_native_program_changes_run_on_gui_thread_and_debounce(self):
        observed_threads = []
        original = self.core.process_instrument_select_response

        def observe(bank, program):
            observed_threads.append(QThread.currentThread())
            original(bank, program)

        with patch.object(self.core, "process_instrument_select_response", side_effect=observe), \
             patch("sys.excepthook") as unhandled:
            def produce():
                self.service.process_message(([0xB0, 0, 1], 0), None)
                for number in range(1000):
                    self.service.process_message(([0xC0, number % 32], 0), None)
            worker = threading.Thread(target=produce)
            worker.start()
            worker.join(timeout=5)
            self.assertFalse(worker.is_alive(), "The MIDI callback must return without waiting for the GUI")
            self.assertEqual(observed_threads, [], "No widget should be modified by the native callback")
            self.app.processEvents()
            self.assertEqual(len(observed_threads), 1000)
            self.assertTrue(all(thread == self.app.thread() for thread in observed_threads))
            self.service.midi_out.send_message.assert_not_called()
            QTest.qWait(450)
            self.assertEqual(self.core._test_synchronizations, 1)
            unhandled.assert_not_called()

    def test_callback_copies_the_native_message_buffer(self):
        original_buffer = [0xC0, 0]
        with patch.object(self.core, "process_instrument_select_response") as update:
            def produce():
                self.service.process_message(([0xB0, 0, 1], 0), None)
                self.service.process_message((original_buffer, 0), None)
                original_buffer[1] = 127
            worker = threading.Thread(target=produce)
            worker.start(); worker.join(timeout=5)
            self.app.processEvents()
            update.assert_called_once_with(1, 0)

    def test_sync_preserves_open_ports_and_callback(self):
        with patch.object(self.service, "close_midi_ports") as close, \
             patch.object(self.service, "open_midi_ports") as reopen, \
             patch("services.midi_service.time.sleep"):
            Core.synchronize_tone_with_synth(self.core)
            close.assert_not_called()
            reopen.assert_not_called()
            self.service.midi_in.set_callback.assert_not_called()

    def test_messages_after_shutdown_are_ignored(self):
        self.core.shutdown()
        with patch.object(self.core, "process_instrument_select_response") as update:
            worker = threading.Thread(target=lambda: self.service.process_message(([0xC0, 1], 0), None))
            worker.start(); worker.join(timeout=5)
            self.app.processEvents()
            update.assert_not_called()
        self.assertFalse(self.core.autosync_timer.isActive())

    def test_missing_bank_still_schedules_a_read(self):
        self.service.process_message(([0xC0, 1], 0), None)
        self.assertTrue(self.core.autosync_timer.isActive())


if __name__ == "__main__":
    unittest.main()
