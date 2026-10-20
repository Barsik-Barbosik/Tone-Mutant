"""Packaged startup verification with simulated devices; no MIDI ports are opened."""
import json
import os
from pathlib import Path
import traceback


def run_selftest(output):
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    import rtmidi
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    from ui.i18n import install_qt_spanish
    from ui.main_window import MainWindow
    from utils.utils import resource_path

    class NoMidi:
        sent = []
        def get_ports(self): return []
        def get_port_count(self): return 0
        def is_port_open(self): return False
        def close_port(self): pass
        def delete(self): pass
        def send_message(self, message): self.sent.append(message)

    report = {"ok": False, "hardware": "simulated; no actual MIDI ports"}
    original_in, original_out = rtmidi.MidiIn, rtmidi.MidiOut
    rtmidi.MidiIn = rtmidi.MidiOut = NoMidi
    try:
        app = QApplication.instance() or QApplication([])
        report["qt_spanish"] = install_qt_spanish(app)
        app.setStyleSheet(Path(resource_path("resources/style.qss")).read_text(encoding="utf-8"))
        window = MainWindow()
        window.resize(1280, 800)
        window.show()

        def finish():
            try:
                panel = window.central_widget
                tabs = [panel.tab_widget.tabText(i) for i in range(panel.tab_widget.count())]
                assert tabs[0] == "Principales" and tabs[-1] == "Experimental", tabs
                assert Path(resource_path("captures/ctx800-survey-20261019.json")).is_file()
                assert not NoMidi.sent
                assert report["qt_spanish"]
                report.update(ok=True, tabs=tabs, midi_messages_sent=len(NoMidi.sent),
                              experimental_rows=panel.experimental_page.table.rowCount())
            except Exception:
                report["error"] = traceback.format_exc()
            finally:
                window.exit_call()
                app.quit()

        QTimer.singleShot(350, finish)
        app.exec()
    except Exception:
        report["error"] = traceback.format_exc()
    finally:
        rtmidi.MidiIn, rtmidi.MidiOut = original_in, original_out
        Path(output).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if report["ok"] else 1
