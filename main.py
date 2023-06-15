import json
import sys

from PySide2.QtCore import Qt, QCoreApplication, Signal, Slot
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication, QMainWindow, QTextBrowser, \
    QStatusBar, QFileDialog, QSplitter

from core import Core
from widgets.central_widget import CentralWidget
from widgets.deque_log import DequeLog
from widgets.gui_helper import GuiHelper
from widgets.settings_window import SettingsWindow
from widgets.top_widget import TopWidget


class MainWindow(QMainWindow):
    status_msg_signal = Signal(str, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CT-X Tone MUTANT 1.00")
        self.setWindowIcon(QIcon("resources/note.png"))

        self.core: Core = Core(self)

        self.menu_bar = GuiHelper.init_menu_bar(self)
        self.setMenuBar(self.menu_bar)

        self.help_texbox = QTextBrowser(self)
        self.log_texbox = DequeLog(self)

        self.central_widget = CentralWidget(self)
        # self.setCentralWidget(self.central_widget)
        self.central_widget.layout().setContentsMargins(10, 10, 0, 10)  # remove right margin

        self.top_widget = TopWidget(self)
        self.top_dock = GuiHelper.init_top_dock(self)
        self.addDockWidget(Qt.TopDockWidgetArea, self.top_dock)

        self.right_dock = GuiHelper.init_right_dock(self)
        # self.addDockWidget(Qt.RightDockWidgetArea, self.right_dock)

        splitter = QSplitter(self)
        splitter.addWidget(self.central_widget)
        splitter.addWidget(self.right_dock)
        splitter.setStretchFactor(0, 1)  # central_widget
        splitter.setStretchFactor(1, 2)  # right_dock
        self.setCentralWidget(splitter)

        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        self.settings_window = None

        self.status_msg_signal.connect(self.show_status_msg)

        self.core.synchronize_tone_with_synth()

    def show_help_text(self, text: str):
        self.help_texbox.setHtml(text)

    @Slot(str, int)
    def show_status_msg(self, text: str, msecs: int):
        self.status_bar.setStyleSheet("background-color: white; color: black")
        self.status_bar.showMessage(text, msecs)

    def show_error_msg(self, text: str):
        self.status_bar.setStyleSheet("background-color: white; color: red")
        self.status_bar.showMessage(text, 5000)

    def show_settings(self):
        self.settings_window = SettingsWindow()

    def show_open_json_dialog(self):
        options = QFileDialog.Options()
        file_dialog = QFileDialog()
        file_dialog.setOptions(options)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_name, _ = file_dialog.getOpenFileName(self, "Open File", "", "JSON Files (*.json);;All Files (*)",
                                                   options=options)

        if file_name:
            with open(file_name, 'r') as file:
                self.core.load_tone_from_json(json.load(file))

    def show_save_json_dialog(self):
        options = QFileDialog.Options()
        file_dialog = QFileDialog()
        file_dialog.setOptions(options)
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setDefaultSuffix("json")
        file_name, _ = file_dialog.getSaveFileName(self, "Save File", "", "JSON Files (*.json);;All Files (*)",
                                                   options=options)
        if file_name:
            print("Saving file:", file_name)
            with open(file_name, 'w') as file:
                file.write(self.central_widget.get_json())

    @staticmethod
    def menu_exit_action():
        QCoreApplication.instance().quit()

    def exit_call(self):
        self.core.close_midi_ports()
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
