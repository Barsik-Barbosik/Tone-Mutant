import sys

from PySide2.QtCore import Qt, QCoreApplication
from PySide2.QtWidgets import QApplication, QMainWindow, QTextBrowser, \
    QStatusBar

from model.tone import Tone
from services.midi_service import MidiService
from widgets.central_widget import CentralWidget
from widgets.gui_helper import GuiHelper
from widgets.midi_settings_window import MidiSettingsWindow
from widgets.top_widget import TopWidget


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CT-X Controller")

        self.tone: Tone = Tone()
        self.midi_service = MidiService.get_instance()
        self.midi_service.main = self

        self.menu_bar = GuiHelper.init_menu_bar(self)
        self.setMenuBar(self.menu_bar)

        self.central_widget = CentralWidget(self)
        self.setCentralWidget(self.central_widget)
        self.central_widget.layout().setContentsMargins(10, 10, 0, 10)  # remove right margin

        self.top_widget = TopWidget(self)
        self.top_dock = GuiHelper.init_top_dock(self)
        self.addDockWidget(Qt.TopDockWidgetArea, self.top_dock)

        self.help_texbox = QTextBrowser()
        self.right_dock = GuiHelper.init_right_dock(self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.right_dock)

        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        self.midi_settings_window = None

        self.synchronize_tone_with_synth()

    def synchronize_tone_with_synth(self):
        print("Synchronizing tone!")
        self.tone = Tone()  # TODO: fix -> tone is initialized twice during the application startup

        try:
            self.midi_service.request_tone_name()
        except Exception as e:
            self.show_error_msg(str(e))

        self.reload_dsp_page(self.central_widget.dsp_page_1)
        self.reload_dsp_page(self.central_widget.dsp_page_2)
        self.reload_dsp_page(self.central_widget.dsp_page_3)
        self.reload_dsp_page(self.central_widget.dsp_page_4)
        self.central_widget.on_tab_changed(0)

    def update_tone_name(self, message):
        tone_name = ''.join(chr(i) for i in message if chr(i).isprintable())
        print("Synth tone name: " + tone_name)
        if tone_name is not None and len(tone_name.strip()) > 0:
            self.tone.name = tone_name
        else:
            self.tone.name = "Unknown Tone"
        self.top_widget.tone_name_label.setText(self.tone.name)

    @staticmethod
    def reload_dsp_page(dsp_page):
        dsp_page.update_tone_dsp_module_by_dsp_id(None)
        if dsp_page.dsp_module is not None:
            dsp_page.list_widget.setCurrentItem(dsp_page.get_list_item_by_dsp_id(dsp_page.dsp_module.id))

    def show_help_text(self, text: str):
        self.help_texbox.setHtml(text)

    def show_status_msg(self, text: str, msecs: int):
        self.status_bar.setStyleSheet("background-color: white; color: black")
        self.status_bar.showMessage(text, msecs)

    def show_error_msg(self, text: str):
        self.status_bar.setStyleSheet("background-color: white; color: red")
        self.status_bar.showMessage(text, 5000)

    def show_midi_settings(self):
        self.midi_settings_window = MidiSettingsWindow()

    @staticmethod
    def menu_exit_action():
        QCoreApplication.instance().quit()

    def exit_call(self):
        self.central_widget.midi_service.close_midi_ports()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    with open("style.qss", "r") as style_file:
        style = style_file.read()
        app.setStyleSheet(style)

    window = MainWindow()
    window.resize(1000, 600)
    window.show()
    app.aboutToQuit.connect(window.exit_call)
    sys.exit(app.exec_())
