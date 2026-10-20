from tests.qt_helpers import synchronize_tone_with_synth
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QComboBox, QSpinBox
from constants.enums import TabName
from constants import constants
from ui.main_window import MainWindow
from ui.i18n import tr, install_qt_spanish
from ui.gui_helper import GuiHelper


class SpanishExperimentalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.patches = [patch("core.MidiService"), patch("core.TyrantMidiService"),
                        patch("core.Core.synchronize_tone_with_synth", new=synchronize_tone_with_synth)]
        for item in self.patches: item.start()
        self.window = MainWindow()
        self.page = self.window.central_widget.experimental_page

    def tearDown(self):
        self.window.close()
        for item in reversed(self.patches): item.stop()

    def test_translated_tabs_keep_stable_identifiers(self):
        tabs = self.window.central_widget.tab_widget
        self.assertEqual(tabs.tabText(0), "Principales")
        self.assertEqual(tabs.tabText(5), "Avanzados")
        for index in range(tabs.count()):
            tabs.setCurrentIndex(index)
            self.assertIsInstance(self.window.central_widget.get_current_tab_name(), TabName)
        self.assertEqual(self.window.central_widget.get_current_tab_name(), TabName.EXPERIMENTAL)

    def test_output_route_is_accessible_and_sends_the_correct_short_parameter(self):
        controls = list(GuiHelper.layout_widgets(self.window.central_widget.advanced_qgrid_layout))
        route = next(widget for widget in controls if widget.accessibleName() == "Ruta de salida")
        self.assertEqual([route.itemText(i) for i in range(route.count())], ["Directa", "DSP"])
        route.setCurrentIndex(1)
        self.window.core.midi_service.send_parameter_change_short_sysex.assert_called_once_with(0, 44, 1)

    def test_experimental_controls_do_not_send_unless_enabled(self):
        self.assertFalse(self.page.editors.isEnabled())
        parameter = self.window.core.tone.advanced_parameter_list[0]
        with patch.object(self.window.core, "send_parameter_change_sysex") as send:
            self.page._change_parameter(parameter)
            send.assert_not_called()
            self.page.enable_editing.setChecked(True)
            self.page._change_parameter(parameter)
            send.assert_called_once_with(parameter)

    def test_read_query_and_response_do_not_write_parameter_values(self):
        row = self.page.row_for[(100, 0)]
        self.page.table.setCurrentCell(row, 0)
        self.page.read_selected()
        self.window.core.midi_service.request_parameter_value_full.assert_called_once_with(0, 100, 3, 3, 0, 0)
        self.window.core.raw_parameter_signal.emit(100, 0, [1, 0, 0, 0, 0])
        self.assertEqual(self.page.table.item(row, 2).text(), "01 00 00 00 00")
        self.assertIsNone(self.page.pending)
        self.assertTrue(self.page.read_button.isEnabled())
        self.window.core.midi_service.send_parameter_change_sysex.assert_not_called()
        self.window.core.midi_service.send_parameter_change_short_sysex.assert_not_called()

    def test_read_timeout_preserves_last_observed_value(self):
        row = self.page.row_for[(200, 0)]
        self.page.table.setCurrentCell(row, 0)
        self.page.read_selected()
        self.page._read_timeout()
        self.assertIsNone(self.page.pending)
        self.assertIsNone(self.page.observations[(200, 0)]["data"])
        self.assertIn("no respondió", self.page.result.toPlainText())

    def test_other_reply_cannot_satisfy_pending_query(self):
        self.page.table.setCurrentCell(self.page.row_for[(100, 0)], 0)
        self.page.read_selected()
        self.window.core.raw_parameter_signal.emit(101, 0, [42])
        self.assertEqual(self.page.pending, (100, 0))

    def test_hidden_effects_are_selected_in_experimental(self):
        hidden = {module.id for module in constants.ALL_DSP_MODULES if "(hidden)" in module.name}
        normal_list = self.window.central_widget.dsp_page_1.list_widget
        ordinary = {normal_list.item(i).data(Qt.UserRole) for i in range(normal_list.count())}
        self.assertFalse(hidden & ordinary)
        self.assertEqual({self.page.effect_combo.itemData(i) for i in range(self.page.effect_combo.count())}, hidden)
        with patch.object(self.window.core, "update_dsp_module_from_list") as apply:
            self.page._apply_effect()
            apply.assert_not_called()
            self.page.enable_editing.setChecked(True)
            self.page._apply_effect()
            apply.assert_called_once_with(0, self.page.effect_combo.currentData())

    def test_snapshot_save_and_comparison_are_readable(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "captura.json")
            with patch("ui.experimental_page.QFileDialog.getSaveFileName", return_value=(path, "")):
                self.page.save_snapshot()
            saved = json.loads(Path(path).read_text(encoding="utf-8"))
            self.assertEqual(saved["format"], "ToneMutant experimental v1")
            self.page.observations[(100, 0)]["data"] = [42]
            with patch("ui.experimental_page.QFileDialog.getOpenFileName", return_value=(path, "")):
                self.page.compare_snapshot()
            self.assertIn("Parámetro 100", self.page.result.toPlainText())
            self.assertIn("2A", self.page.result.toPlainText())

    def test_translation_preserves_user_names_and_json_keys(self):
        self.window.core.tone.name = "Volume"
        self.window.top_widget.update_tone_name_input_and_parent_info()
        self.assertEqual(self.window.top_widget.tone_name_input.text(), "Volume")
        data = json.loads(self.window.central_widget.get_json())
        self.assertEqual(data["parameters"][0]["name"], "Attack Time")
        self.assertEqual(tr("Attack Time"), "Tiempo de ataque")

    def test_native_qt_buttons_have_spanish_translation(self):
        from PySide6.QtCore import QCoreApplication
        self.assertTrue(install_qt_spanish(self.app))
        self.assertIn("ancelar", QCoreApplication.translate("QPlatformTheme", "Cancel"))

    def test_cancel_json_import_with_no_current_parent_sends_nothing(self):
        self.window.core.tone.parent_tone = None
        with patch("core.ChangeInstrumentWindow") as dialog:
            dialog.return_value.Accepted = 1
            dialog.return_value.exec.return_value = 0
            self.window.core.load_tone_from_json({"parameters": [{"name": "Volume", "value": 90}]})
        self.window.core.midi_service.send_parameter_change_short_sysex.assert_not_called()

    def test_qt_exposes_spanish_names_roles_focus_and_numeric_bounds(self):
        from PySide6.QtGui import QAccessible
        panel = self.window.central_widget
        route = next(widget for widget in GuiHelper.layout_widgets(panel.advanced_qgrid_layout)
                     if widget.accessibleName() == "Ruta de salida")
        spin = next(widget for widget in GuiHelper.layout_widgets(panel.qgrid_layout)
                    if widget.accessibleName() == "Volumen")
        for control, role, name in ((route, QAccessible.Role.ComboBox, "Ruta de salida"),
                                    (spin, QAccessible.Role.SpinBox, "Volumen")):
            interface = QAccessible.queryAccessibleInterface(control)
            self.assertEqual(interface.role(), role)
            self.assertEqual(interface.text(QAccessible.Text.Name), name)
            self.assertTrue(interface.state().focusable)
        value_interface = QAccessible.queryAccessibleInterface(spin).valueInterface()
        self.assertEqual(value_interface.minimumValue(), 0)
        self.assertEqual(value_interface.maximumValue(), 127)


if __name__ == "__main__":
    unittest.main()
