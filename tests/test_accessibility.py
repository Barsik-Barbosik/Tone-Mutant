from tests.qt_helpers import synchronize_tone_with_synth
from ui.i18n import tr
"""Native Qt regression checks. MIDI services are replaced; no hardware is used."""
import os
import configparser
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QWidget, QSpinBox, QComboBox, QLineEdit, QAbstractItemView, QTableWidgetItem

from constants import constants
from constants.enums import ParameterType
from models.parameter import Parameter
from ui.gui_helper import GuiHelper
from ui.main_window import MainWindow
from ui.settings_window import SettingsWindow
from ui.upload_tone_window import UploadToneWindow
from ui.rename_tone_window import RenameToneWindow
from ui.delete_tone_window import DeleteToneWindow
from ui.request_parameter_window import RequestParameterWindow
from ui.user_tone_manager_window import UserToneManagerWindow
from ui.drag_and_drop_table import DragAndDropTable


class AccessibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.patches = [patch("core.MidiService"), patch("core.TyrantMidiService"),
                       patch("core.Core.synchronize_tone_with_synth", new=synchronize_tone_with_synth)]
        for item in cls.patches:
            item.start()
        cls.window = MainWindow()
        cls.window.show()
        cls.app.processEvents()

    @classmethod
    def tearDownClass(cls):
        cls.window.close()
        for item in reversed(cls.patches):
            item.stop()

    def test_all_parameter_variants_expose_names_descriptions_and_bounds(self):
        params = list(self.window.core.tone.main_parameter_list)
        params += self.window.core.tone.advanced_parameter_list
        for module in constants.ALL_DSP_MODULES:
            params += module.dsp_parameter_list + [module.bypass]
        self.assertGreater(len(params), 100)
        for parameter in params:
            with self.subTest(parameter=parameter.name):
                if parameter.type == ParameterType.COMBO:
                    control = GuiHelper.create_combo_input(parameter, Mock())
                    self.assertEqual(control.count(), len(parameter.choices))
                    self.assertEqual(control.accessibleName(), tr(parameter.name))
                    control.deleteLater()
                else:
                    layout = GuiHelper.create_knob_input(parameter, Mock())
                    spin, dial = layout.itemAt(0).widget(), layout.itemAt(1).widget()
                    self.assertEqual(spin.accessibleName(), tr(parameter.name))
                    self.assertTrue(spin.accessibleDescription())
                    self.assertEqual((spin.minimum(), spin.maximum()), tuple(parameter.choices))
                    self.assertEqual(dial.focusPolicy(), Qt.NoFocus)
                    spin.deleteLater()
                    dial.deleteLater()

    def test_typed_number_commits_once_on_enter(self):
        parameter = Parameter(1, "Test volume", "Volume", ParameterType.KNOB, [0, 127])
        callback = Mock()
        host = QWidget()
        layout = GuiHelper.create_knob_input(parameter, callback)
        host.setLayout(layout)
        host.show()
        spin = layout.itemAt(0).widget()
        spin.setFocus()
        spin.selectAll()
        QTest.keyClicks(spin, "42")
        callback.assert_not_called()
        QTest.keyClick(spin, Qt.Key_Return)
        callback.assert_called_once_with(parameter)
        self.assertEqual(parameter.value, 42)
        self.assertEqual(layout.itemAt(1).widget().value(), 42)
        host.close()

    def test_dial_and_spin_updates_send_one_change_each(self):
        parameter = Parameter(1, "Test", "", ParameterType.KNOB, [0, 127])
        callback = Mock()
        layout = GuiHelper.create_knob_input(parameter, callback)
        spin, dial = layout.itemAt(0).widget(), layout.itemAt(1).widget()
        spin.setValue(30)
        self.assertEqual(callback.call_count, 1)
        dial.setValue(40)
        self.assertEqual(callback.call_count, 2)
        self.assertEqual(spin.value(), 40)

    def test_duplicate_combo_choices_preserve_selected_index(self):
        parameter = Parameter(1, "Choice", "", ParameterType.COMBO, ["Same", "Same"])
        callback = Mock()
        combo = GuiHelper.create_combo_input(parameter, callback)
        combo.setCurrentIndex(1)
        self.assertEqual(parameter.value, 1)
        callback.assert_called_once()

    def test_single_choice_combo_can_be_created(self):
        parameter = Parameter(1, "Choice", "", ParameterType.COMBO, ["Only"])
        self.assertEqual(GuiHelper.create_combo_input(parameter, Mock()).count(), 1)

    def test_all_dialog_inputs_have_explicit_names(self):
        windows = []
        with patch("ui.settings_window.rtmidi.MidiIn") as midi_in, \
             patch("ui.settings_window.rtmidi.MidiOut") as midi_out:
            midi_in.return_value.get_ports.return_value = []
            midi_out.return_value.get_ports.return_value = []
            for constructor in (SettingsWindow, UploadToneWindow, RenameToneWindow,
                                DeleteToneWindow, RequestParameterWindow):
                dialog = constructor(self.window)
                windows.append(dialog)
                for control in dialog.findChildren(QWidget):
                    if isinstance(control, (QLineEdit, QComboBox)):
                        self.assertTrue(control.accessibleName(), constructor.__name__)
                self.assertIn("Esc", [action.shortcut().toString() for action in dialog.actions()])
        for dialog in windows:
            dialog.close()

    def test_parameter_request_rejects_out_of_range_before_midi(self):
        dialog = RequestParameterWindow(self.window)
        dialog.number_input.setText("256")
        with patch.object(dialog.core, "request_custom_parameter") as request, \
             patch("ui.request_parameter_window.QMessageBox.warning") as warning:
            dialog.on_submit()
            request.assert_not_called()
            warning.assert_called_once()
        dialog.close()

    def test_sysex_two_byte_values_stay_within_seven_bits(self):
        from utils.utils import int_to_lsb_msb
        self.assertEqual(int_to_lsb_msb(0), "00 00")
        self.assertEqual(int_to_lsb_msb(16383), "7F 7F")
        for invalid in (-1, 16384, 32267):
            with self.assertRaises(ValueError):
                int_to_lsb_msb(invalid)

    def test_mixer_layer_handlers_use_their_own_choices(self):
        mixer = self.window.top_widget
        for combo, handler, layer in [(mixer.tone_combo_lower1, mixer.on_lower1_selected, 2),
                                      (mixer.tone_combo_lower2, mixer.on_lower2_selected, 3)]:
            combo.setItemData(0, 123 + layer, Qt.UserRole)
            with patch.object(mixer.core, "send_instrument_change_sysex") as send:
                handler(0)
                send.assert_called_once_with(layer, 123 + layer)

    def test_received_mixer_values_do_not_echo_midi(self):
        mixer = self.window.top_widget
        with patch.object(mixer.core, "send_performance_param_change_sysex") as send:
            mixer.redraw_volume_knob(0, 76)
            mixer.redraw_pan_knob(0, -20)
            send.assert_not_called()
        for layout, value in [(mixer.volume_knob_layout_upper1, 76), (mixer.pan_knob_layout_upper1, -20)]:
            self.assertEqual(layout.itemAt(0).widget().value(), value)
            self.assertEqual(layout.itemAt(1).widget().value(), value)

    def test_received_tone_selection_and_refresh_do_not_echo_midi(self):
        mixer = self.window.top_widget
        with patch.object(mixer.core, "send_instrument_change_sysex") as send:
            mixer.select_item_by_id(2, mixer.tone_combo_lower1.itemData(1))
            mixer.populate_all_tone_combos()
            send.assert_not_called()

    def test_status_survives_timeout_and_focus_returns(self):
        window = self.window
        window.activateWindow()
        window.top_widget.tone_name_input.setFocus()
        self.app.processEvents()
        window.status_bar.showMessage("Test complete")
        window.status_bar.clearMessage()
        self.assertEqual(window.status_history.text(), "Test complete")
        window._focus_status()
        self.assertTrue(window.status_history.hasFocus())
        window._leave_status()
        self.assertTrue(window.top_widget.tone_name_input.hasFocus())

    def test_action_menu_survives_settings_reload(self):
        self.window.reload_menu_bar()
        menus = [action.menu() for action in self.window.menu_bar.actions()]
        menu = next(menu for menu in menus if menu.title() == tr("&Actions"))
        self.assertEqual([action.text() for action in menu.actions()], [tr(x) for x in ["Refresh", "Generate Tone", "Random Name"]])

    def test_ctx800_disables_user_memory_and_uses_its_tone_list(self):
        from utils.utils import get_all_instruments
        cfg = configparser.ConfigParser()
        cfg.read_dict({"Synthesizer": {"Model": constants.CTX_700_800}})
        try:
            with patch("configparser.ConfigParser", return_value=cfg):
                self.window.reload_menu_bar()
                self.assertFalse(GuiHelper.has_user_memory())
                self.assertIs(get_all_instruments(), constants.ALL_INSTRUMENTS_700_800)
                tools = next(action.menu() for action in self.window.menu_bar.actions()
                             if action.text() == tr("&Synthesizer Tools"))
                memory_actions = [action for action in tools.actions() if action.text() in tuple(tr(x) for x in (
                    "User Tone Manager", "Save Tone to Synthesizer's Memory", "Rename Tone", "Delete Tone"))]
                self.assertEqual(len(memory_actions), 4)
                self.assertTrue(all(not action.isEnabled() for action in memory_actions))
        finally:
            self.window.reload_menu_bar()

    def test_f6_shortcuts_move_between_regions(self):
        window = self.window
        window.activateWindow()
        window.top_widget.tone_name_input.setFocus()
        self.app.processEvents()
        QTest.keyClick(window.top_widget.tone_name_input, Qt.Key_F6)
        self.assertTrue(window.central_widget.tab_widget.tabBar().hasFocus())
        QTest.keyClick(window.central_widget.tab_widget.tabBar(), Qt.Key_F6)
        self.assertTrue(window.right_tab_widget.tabBar().hasFocus())
        QTest.keyClick(window.right_tab_widget.tabBar(), Qt.Key_F6, Qt.ShiftModifier)
        self.assertTrue(window.central_widget.tab_widget.tabBar().hasFocus())

    def test_parameter_focus_survives_panel_redraw(self):
        panel = self.window.central_widget
        panel.tab_widget.setCurrentIndex(0)
        self.window.activateWindow()
        original = next(widget for widget in GuiHelper.layout_widgets(panel.qgrid_layout)
                        if isinstance(widget, QSpinBox) and widget.accessibleName() == "Volumen")
        original.setFocus()
        self.app.processEvents()
        panel.redraw_main_params_panel()
        self.app.processEvents()
        focused = self.app.focusWidget()
        self.assertIsInstance(focused, QSpinBox)
        self.assertEqual(focused.accessibleName(), "Volumen")
        self.assertIsNot(focused, original)

    def test_dsp_state_has_text_accessible_to_screen_readers(self):
        module = constants.ALL_DSP_MODULES[0]
        self.window.core.update_tone_dsp_module_and_refresh_gui(0, module.id)
        name = self.window.central_widget.tab_widget.tabBar().accessibleTabName(1)
        self.assertIn(tr(module.name), name)

    def test_table_enter_opens_native_name_editor(self):
        table = DragAndDropTable()
        table.addItem("Tone")
        table.setCurrentCell(0, 0)
        table.show()
        QTest.keyClick(table, Qt.Key_Return)
        self.assertEqual(table.state(), QAbstractItemView.EditingState)
        table.close()

    def test_upload_allows_keyboard_destination_and_cancel(self):
        manager = UserToneManagerWindow(self.window)
        manager.file_table_widget.setRowCount(1)
        manager.file_table_widget.setItem(0, 0, QTableWidgetItem("test.ton"))
        manager.file_table_widget.setCurrentCell(0, 0)
        with patch("ui.user_tone_manager_window.QInputDialog.getInt", return_value=(805, True)), \
             patch.object(manager, "on_load_tone_file") as upload:
            manager.on_move_from_pc()
            upload.assert_called_once_with("test.ton", 4)
        with patch("ui.user_tone_manager_window.QInputDialog.getInt", return_value=(805, False)), \
             patch.object(manager, "on_load_tone_file") as upload:
            manager.on_move_from_pc()
            upload.assert_not_called()
        manager.close()


if __name__ == "__main__":
    unittest.main()
